#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=2", "scipy>=1.14"]
# ///
"""Synthetic calibration for the frozen C012 cross-lab Hue-Heat analysis.

No real Hue-Heat CSV values are read here.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.stats import t

ROOT = Path(__file__).parents[1]
SEED = 20260909
DISCOVERY_LABS = (1, 3, 5, 7)


def ols_effect(delta, red_second, hot):
    # Use an uncentered +/-1 order sign: intercept is the counterbalanced hue effect.
    # Thermal condition is centered because it is not the crossover period indicator.
    X = np.column_stack([
        np.ones(len(delta)),
        2 * red_second - 1,
        hot - np.mean(hot),
    ])
    beta, *_ = np.linalg.lstsq(X, delta, rcond=None)
    resid = delta - X @ beta
    dof = len(delta) - X.shape[1]
    s2 = np.sum(resid**2) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(beta[0]), float(np.sqrt(cov[0, 0]))


def pool_lab_effects(effects, ses):
    # The laboratory, not the participant, is the replication unit.
    effects = np.asarray(effects, dtype=float)
    mu = float(np.mean(effects))
    se = float(np.std(effects, ddof=1) / np.sqrt(len(effects)))
    stat = mu / se if se > 0 else np.inf if mu > 0 else 0.0
    p_one = float(t.sf(stat, df=len(effects) - 1))
    return mu, se, p_one


def passes_rule(effects, ses):
    effects = np.asarray(effects)
    ses = np.asarray(ses)
    mu, se, p = pool_lab_effects(effects, ses)
    sign_count = int(np.sum(effects > 0))
    loo = []
    for i in range(len(effects)):
        keep = np.arange(len(effects)) != i
        loo_mu, _, _ = pool_lab_effects(effects[keep], ses[keep])
        loo.append(loo_mu)
    passed = bool(sign_count >= 3 and p <= 0.025 and min(loo) > 0)
    return passed, {"pooled_effect": mu, "pooled_se": se, "p_one_sided": p,
                    "positive_labs": sign_count, "leave_one_lab_out_effects": loo}


def simulate_case(rng, true_effect, lab_heterogeneity_sd=0.025):
    effects, ses = [], []
    # Approximate the reported per-lab scale without using any outcome values.
    n_by_lab = {1: 55, 3: 70, 5: 80, 7: 40}
    for lab in DISCOVERY_LABS:
        n = n_by_lab[lab]
        red_second = rng.integers(0, 2, n)
        hot = rng.integers(0, 2, n)
        # A period drift contaminates red-blue differences with opposite sign
        # depending on which hue occurred second; regression adjusts for it.
        period_drift = rng.normal(0.10, 0.04)
        lab_effect = true_effect + rng.normal(0, lab_heterogeneity_sd)
        # Terminal-window averaged skin temperature still has participant-level
        # within-round noise; use a conservative 0.20 C SD.
        noise = rng.normal(0, 0.20, n)
        delta = lab_effect + period_drift * (2 * red_second - 1) + 0.03 * (hot - 0.5) + noise
        eff, se = ols_effect(delta, red_second, hot)
        effects.append(eff); ses.append(se)
    return passes_rule(effects, ses)


def calibrate(n_cases=1000):
    rng = np.random.default_rng(SEED)
    results = {}
    for effect in [0.0, 0.05, 0.10, 0.15]:
        passed = 0
        pooled = []
        for _ in range(n_cases):
            ok, d = simulate_case(rng, effect)
            passed += int(ok)
            pooled.append(d["pooled_effect"])
        results[f"effect_{effect:.2f}C"] = {
            "cases": n_cases,
            "pass_count": passed,
            "pass_rate": passed / n_cases,
            "pooled_effect_mean": float(np.mean(pooled)),
            "pooled_effect_sd": float(np.std(pooled, ddof=1)),
        }
    return {
        "claim_id": "C012",
        "real_data_accessed": False,
        "seed": SEED,
        "simulation": {
            "labs": list(DISCOVERY_LABS),
            "per_lab_rounds": {"1":55,"3":70,"5":80,"7":40},
            "within_round_delta_noise_sd_C": 0.20,
            "lab_effect_heterogeneity_sd_C": 0.025,
            "period_drift_mean_C": 0.10,
            "period_drift_sd_C": 0.04,
            "analysis": "per-lab OLS of red-minus-blue delta adjusted for order and thermal condition; equal-weight lab-level one-sample t test; >=3/4 positive; all leave-one-lab-out pooled effects positive"
        },
        "results": results,
        "calibration_acceptance": {
            "null_false_positive_rate_max": 0.03,
            "power_at_0.10C_min": 0.80,
        },
        "calibration_pass": bool(results["effect_0.00C"]["pass_rate"] <= 0.03 and results["effect_0.10C"]["pass_rate"] >= 0.80),
    }

if __name__ == "__main__":
    out = calibrate()
    path = ROOT / "results" / "c012_calibration.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
