#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=2"]
# ///
"""Continuous fixed-support, fixed-margin null for temporal Taylor-law tests."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[1]


def balance_to_margins(weights, row_totals, col_totals, support=None, tol=1e-10, max_iter=10000):
    """RAS/IPF balance positive weights to exact row/column margins on fixed support."""
    w = np.asarray(weights, dtype=float).copy()
    r = np.asarray(row_totals, dtype=float)
    c = np.asarray(col_totals, dtype=float)
    if support is None:
        support = np.ones_like(w, dtype=bool)
    else:
        support = np.asarray(support, dtype=bool)
    if w.shape != support.shape or w.shape != (len(r), len(c)):
        raise ValueError("shape mismatch")
    if not np.isclose(r.sum(), c.sum(), rtol=1e-12, atol=1e-12):
        raise ValueError("row/column totals differ")
    if np.any(r <= 0) or np.any(c <= 0):
        raise ValueError("margins must be positive")
    if np.any(support.sum(axis=1) == 0) or np.any(support.sum(axis=0) == 0):
        raise ValueError("empty supported row/column")
    x = np.where(support, np.maximum(w, np.finfo(float).tiny), 0.0)
    for it in range(max_iter):
        x *= (r / x.sum(axis=1))[:, None]
        x *= (c / x.sum(axis=0))[None, :]
        if it % 10 == 0:
            er = np.max(np.abs(x.sum(axis=1) - r) / r)
            ec = np.max(np.abs(x.sum(axis=0) - c) / c)
            if max(er, ec) < tol:
                return x, it + 1
    raise RuntimeError("IPF did not converge")


def random_matrix(row_totals, col_totals, support, rng, family="exponential"):
    if family == "exponential":
        w = rng.exponential(1.0, size=support.shape)
    elif family == "lognormal":
        w = rng.lognormal(0.0, 1.0, size=support.shape)
    else:
        raise ValueError(f"unknown weight family {family}")
    return balance_to_margins(w, row_totals, col_totals, support)[0]


def metrics(x):
    """OLS Taylor b and dominance CV ratio across species rows."""
    x = np.asarray(x, dtype=float)
    means = x.mean(axis=1)
    variances = x.var(axis=1, ddof=1)
    valid = (means > 0) & (variances > 0)
    if valid.sum() < 4:
        raise ValueError("need >=4 nonzero-variance species")
    means = means[valid]
    variances = variances[valid]
    b = float(np.polyfit(np.log(means), np.log(variances), 1)[0])
    cv = np.sqrt(variances) / means
    cvratio = float(cv.mean() / np.average(cv, weights=means))
    return {"b": b, "cvratio": cvratio, "n_species": int(valid.sum())}


def null_metrics(row_totals, col_totals, support, n, seed, family="exponential"):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        x = random_matrix(row_totals, col_totals, support, rng, family)
        out.append(metrics(x))
    return out


def empirical_p(obs, null, direction):
    vals = np.array(null, dtype=float)
    if direction == "lower":
        return float((1 + np.sum(vals <= obs)) / (len(vals) + 1))
    if direction == "upper":
        return float((1 + np.sum(vals >= obs)) / (len(vals) + 1))
    raise ValueError(direction)


def toy_margins():
    means = np.geomspace(0.5, 30.0, 12)
    row = means * 24
    col = np.full(24, row.sum() / 24)
    support = np.ones((12, 24), dtype=bool)
    return row, col, support


def stabilized_toy(row, col, support, rng):
    """Inject lower temporal relative variability for higher-mean species."""
    means = row / len(col)
    rank = np.argsort(np.argsort(means)) / (len(means) - 1)
    sigma = 1.4 - 1.15 * rank  # subordinate species noisy, dominant species stable
    w = np.exp(rng.normal(0.0, sigma[:, None], size=support.shape))
    return balance_to_margins(w, row, col, support)[0]


def calibrate(n_cases=20, n_null=199, seed=20260909):
    row, col, support = toy_margins()
    rng = np.random.default_rng(seed)
    false_joint = 0
    positive_joint = 0
    null_ps = []
    positive_ps = []
    for case in range(n_cases):
        # Known null: pseudo-observation and reference draws use the same generator.
        obs0 = random_matrix(row, col, support, rng, "exponential")
        m0 = metrics(obs0)
        nm0 = null_metrics(row, col, support, n_null, seed + 10000 + case, "exponential")
        pb0 = empirical_p(m0["b"], [z["b"] for z in nm0], "lower")
        pc0 = empirical_p(m0["cvratio"], [z["cvratio"] for z in nm0], "upper")
        false_joint += int(pb0 <= 0.025 and pc0 <= 0.025)
        null_ps.append([pb0, pc0])

        # Known positive: same exact margins/support, but dominant species are stabilized.
        obs1 = stabilized_toy(row, col, support, rng)
        m1 = metrics(obs1)
        nm1 = null_metrics(row, col, support, n_null, seed + 20000 + case, "exponential")
        pb1 = empirical_p(m1["b"], [z["b"] for z in nm1], "lower")
        pc1 = empirical_p(m1["cvratio"], [z["cvratio"] for z in nm1], "upper")
        positive_joint += int(pb1 <= 0.025 and pc1 <= 0.025)
        positive_ps.append([pb1, pc1])
    return {
        "seed": seed,
        "n_cases": n_cases,
        "null_replicates_per_case": n_null,
        "known_null_joint_false_positives": false_joint,
        "known_positive_joint_detections": positive_joint,
        "known_positive_joint_power": positive_joint / n_cases,
        "acceptance_rule": "Calibration passes if <=2/20 joint false positives and >=16/20 joint known-positive detections.",
        "calibration_pass": bool(false_joint <= 2 and positive_joint >= 16),
        "known_null_p_pairs": null_ps,
        "known_positive_p_pairs": positive_ps,
    }


if __name__ == "__main__":
    result = calibrate()
    out = ROOT / "results" / "c003_null_calibration.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["known_null_joint_false_positives", "known_positive_joint_detections", "known_positive_joint_power", "calibration_pass"]}, indent=2))
