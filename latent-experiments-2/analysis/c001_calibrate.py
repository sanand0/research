#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy>=2", "scipy>=1.14", "scikit-learn>=1.5"]
# ///
"""Calibrate a monotone residual detector for repeated TEM-1 DMS maps."""
from __future__ import annotations

import csv, json, re
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.isotonic import IsotonicRegression

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260909
MUT = re.compile(r"^([A-Z])(\d+)([A-Z])$")


def read_cols(path: Path, *cols: str) -> dict[str, dict[str, float]]:
    out = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            out[row["mutant"]] = {c: float(row[c]) for c in cols if row.get(c, "") != ""}
    return out


def position(mutant: str) -> int:
    m = MUT.fullmatch(mutant)
    if not m:
        raise ValueError(mutant)
    return int(m.group(2))


def folds_for(mutants: list[str], rng: np.random.Generator, k: int = 5) -> np.ndarray:
    positions = np.array(sorted({position(m) for m in mutants}))
    rng.shuffle(positions)
    p2f = {int(p): i % k for i, p in enumerate(positions)}
    return np.array([p2f[position(m)] for m in mutants])


def cv_isotonic(x: np.ndarray, y: np.ndarray, folds: np.ndarray) -> np.ndarray:
    pred = np.empty_like(y)
    for fold in np.unique(folds):
        train = folds != fold
        test = ~train
        model = IsotonicRegression(increasing=True, out_of_bounds="clip")
        model.fit(x[train], y[train])
        pred[test] = model.predict(x[test])
    return pred


def eta2_position(resid: np.ndarray, positions: np.ndarray) -> float:
    grand = resid.mean()
    ss_total = np.square(resid - grand).sum()
    if ss_total == 0:
        return 0.0
    ss_between = 0.0
    for p in np.unique(positions):
        r = resid[positions == p]
        ss_between += len(r) * (r.mean() - grand) ** 2
    return float(ss_between / ss_total)


def bins10(x: np.ndarray) -> np.ndarray:
    edges = np.unique(np.quantile(x, np.linspace(0, 1, 11)))
    return np.digitize(x, edges[1:-1], right=True)


def permute_within(values: np.ndarray, bins: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = values.copy()
    for b in np.unique(bins):
        idx = np.flatnonzero(bins == b)
        out[idx] = rng.permutation(values[idx])
    return out


def pair_metrics(mutants: list[str], x: np.ndarray, y: np.ndarray, folds: np.ndarray, rng: np.random.Generator, null_n: int = 400):
    pos = np.array([position(m) for m in mutants])
    pred = cv_isotonic(x, y, folds)
    resid = y - pred
    observed = eta2_position(resid, pos)
    bins = bins10(x)
    null = np.empty(null_n)
    for i in range(null_n):
        y0 = pred + permute_within(resid, bins, rng)
        r0 = y0 - cv_isotonic(x, y0, folds)
        null[i] = eta2_position(r0, pos)
    p = (1 + np.sum(null >= observed)) / (null_n + 1)
    return {
        "n": len(y),
        "spearman": float(spearmanr(x, y).statistic),
        "rmse_after_cv_isotonic": float(np.sqrt(np.mean(resid**2))),
        "residual_sd": float(np.std(resid, ddof=1)),
        "position_eta2": observed,
        "position_null_p": float(p),
        "position_null_95": float(np.quantile(null, 0.95)),
    }, pred, resid, null


def self_test() -> None:
    rng = np.random.default_rng(1)
    mutants = [f"A{p}{aa}" for p in range(1, 31) for aa in "CDEFG"]
    x = rng.normal(size=len(mutants))
    y = 2 * x + rng.normal(scale=.2, size=len(mutants))
    folds = folds_for(mutants, rng)
    pred = cv_isotonic(x, y, folds)
    assert np.corrcoef(pred, y)[0, 1] > 0.95
    assert 0 <= eta2_position(y - pred, np.array([position(m) for m in mutants])) <= 1


def main() -> None:
    self_test()
    rng = np.random.default_rng(SEED)
    f = read_cols(ROOT / "cache/discovery/BLAT_ECOLX_Firnberg_2014.csv", "DMS_score")
    s = read_cols(ROOT / "cache/raw-discovery/BLAT_ECOLX_Stiffler_2015.csv", "39", "2500", "0_1", "0_2", "39_1", "39_2", "156_1", "156_2", "625_1", "625_2", "2500_1", "2500_2")
    common = sorted(set(f) & set(s))
    folds = folds_for(common, rng)
    x = np.array([f[m]["DMS_score"] for m in common])
    s39 = np.array([s[m]["39"] for m in common])
    s2500 = np.array([s[m]["2500"] for m in common])
    cross, pred, resid, null = pair_metrics(common, x, s2500, folds, rng)
    replicate_metrics = {}
    replicate_residual_sds = []
    for conc in ("0", "39", "156", "625", "2500"):
        rc = [m for m in common if f"{conc}_1" in s[m] and f"{conc}_2" in s[m]]
        rf = folds_for(rc, rng)
        a = np.array([s[m][f"{conc}_1"] for m in rc])
        b = np.array([s[m][f"{conc}_2"] for m in rc])
        met, _, rr, _ = pair_metrics(rc, a, b, rf, rng)
        replicate_metrics[conc] = met
        replicate_residual_sds.append(met["residual_sd"])
    selection, _, _, _ = pair_metrics(common, s39, s2500, folds, rng)

    # Power of the position-heterogeneity detector for effects anchored to same-condition replicate noise.
    positions = np.array([position(m) for m in common])
    bins = bins10(x)
    threshold = float(np.quantile(null, .95))
    replicate_noise_sd = float(np.median(replicate_residual_sds))
    power = {}
    for multiple in (0.5, 1.0, 2.0):
        hits = 0
        for _ in range(200):
            y0 = pred + permute_within(resid, bins, rng)
            effects = {int(p): rng.normal(scale=multiple * replicate_noise_sd) for p in np.unique(positions)}
            yi = y0 + np.array([effects[int(p)] for p in positions])
            ri = yi - cv_isotonic(x, yi, folds)
            hits += eta2_position(ri, positions) > threshold
        power[str(multiple)] = hits / 200

    out = {
        "seed": SEED,
        "common_mutants": len(common),
        "cross_study_firnberg_to_stiffler2500": cross,
        "known_null_same_condition_stiffler_replicates": replicate_metrics,
        "known_context_shift_stiffler39_to_stiffler2500": selection,
        "replicate_noise_sd": replicate_noise_sd,
        "injected_position_effect_power_by_replicate_noise_multiple": power,
        "calibration_valid": all(m["position_null_p"] >= 0.05 for m in replicate_metrics.values()),
        "calibration_failure_rule": "Invalid if any same-condition replicate pair is rejected by the nominal position permutation null at alpha=0.05.",
        "injected_power_interpretable": all(m["position_null_p"] >= 0.05 for m in replicate_metrics.values()),
        "injection_note": "Random position effects; SD is a multiple of the median same-condition replicate residual SD. Null preserves cross-study residual magnitude and heteroskedasticity by permuting within Firnberg score deciles. Power is not interpretable if calibration_valid is false.",
    }
    path = ROOT / "results/c001_calibration.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
