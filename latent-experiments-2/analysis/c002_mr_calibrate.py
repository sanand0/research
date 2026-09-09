#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mrestimator==0.2.0", "numpy>=2", "scipy>=1.10"]
# ///
"""Calibrate subsampling-invariant MR estimation before Allen spike analysis."""

from __future__ import annotations

import json
from pathlib import Path

import mrestimator as mre
import numpy as np

DT_MS = 4
R2_GATE = 0.90


def simulate_matched(m: float, mean_activity: float, length: int, seed: int) -> np.ndarray:
    """Stationary branching process with fixed mean population activity."""
    if not 0 <= m < 1:
        raise ValueError("stationary calibration requires 0 <= m < 1")
    h = mean_activity * (1 - m)
    return np.asarray(mre.simulate_branching(m=m, h=h, length=length, seed=seed)).reshape(-1)


def subsample(data: np.ndarray, probability: float, seed: int) -> np.ndarray:
    """Binomial event subsampling used by the reference MR implementation."""
    if not 0 < probability <= 1:
        raise ValueError("probability must be in (0, 1]")
    return np.random.default_rng(seed).binomial(np.asarray(data, dtype=int), probability)


def estimate_m(data: np.ndarray, kmax: int = 200) -> dict[str, float | bool]:
    """Estimate m and require the exponential-regression applicability fit to work."""
    coeff = mre.coefficients(data, steps=(1, kmax), dt=DT_MS, dtunit="ms", numboot=0)
    fit = mre.fit(coeff)
    m = float(fit.mre)
    tau = float(fit.tau)
    r2 = float(fit.rsquared)
    applicable = bool(np.isfinite([m, tau, r2]).all() and 0 < m < 1 and tau > 0 and r2 >= R2_GATE)
    return {"m": m, "tau_ms": tau, "r2": r2, "applicable": applicable}


def run_calibration() -> dict:
    mean_activity = 2.0  # ~64 Allen units * 7.8 Hz * 4 ms from the feasibility probe
    length = 225_000  # 900 s, half of the standardized 30-min Allen spontaneous block
    true_ms = [0.0, 0.8, 0.98, 0.99]
    probabilities = [1.0, 0.5, 0.25]
    seeds = [11, 23, 37, 53, 71]
    rows = []

    for m in true_ms:
        for seed in seeds:
            x = simulate_matched(m, mean_activity, length, seed)
            for p in probabilities:
                y = x if p == 1 else subsample(x, p, seed + 10_000 + int(p * 100))
                out = estimate_m(y)
                rows.append({"true_m": m, "sampling_probability": p, "seed": seed, **out})

    # Independent Poisson is a known non-PAR propagation null: fitting should fail applicability.
    for seed in seeds:
        x = np.random.default_rng(seed).poisson(mean_activity, length)
        rows.append({"true_m": None, "label": "independent_poisson", "sampling_probability": 1.0, "seed": seed, **estimate_m(x)})

    summary = {}
    for m in true_ms:
        key = str(m)
        summary[key] = {}
        for p in probabilities:
            vals = [r for r in rows if r.get("true_m") == m and r["sampling_probability"] == p]
            est = np.array([r["m"] for r in vals])
            summary[key][str(p)] = {
                "n": len(vals),
                "applicable": sum(bool(r["applicable"]) for r in vals),
                "mean_estimate": float(est.mean()),
                "sd_estimate": float(est.std(ddof=1)),
                "mean_abs_error": float(np.mean(np.abs(est - m))),
            }
    nulls = [r for r in rows if r.get("label") == "independent_poisson"]

    return {
        "method": "mrestimator 0.2.0 multistep regression",
        "dt_ms": DT_MS,
        "kmax": 200,
        "r2_applicability_gate": R2_GATE,
        "mean_activity_per_bin": mean_activity,
        "length_bins": length,
        "duration_s": length * DT_MS / 1000,
        "synthetic_subsampling_note": "Reference binomial event subsampling; real Allen validation must also use fixed unit subsets.",
        "summary": summary,
        "poisson_null": {
            "n": len(nulls),
            "applicable": sum(bool(r["applicable"]) for r in nulls),
            "r2_range": [float(min(r["r2"] for r in nulls)), float(max(r["r2"] for r in nulls))],
            "note": "Poisson is a known non-propagating null; m is uninterpretable when applicability fails.",
        },
        "rows": rows,
    }


if __name__ == "__main__":
    result = run_calibration()
    out = Path(__file__).parents[1] / "results" / "c002_mr_calibration.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"summary": result["summary"], "poisson_null": result["poisson_null"]}, indent=2))
