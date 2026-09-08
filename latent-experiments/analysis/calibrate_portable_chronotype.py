#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "statsmodels>=0.14"]
# ///
"""Outcome-free calibration of chronotype phenotypes that can transfer across RFID studies."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"

d = pd.read_csv(OUT / "timing_birddays_full.csv")
base = pd.read_csv(OUT / "timing_phenotypes_full.csv").set_index("TransponderHexCode")
for col in ["Temperature", "Daylength"]:
    d[f"z_{col}"] = (d[col] - d[col].mean()) / d[col].std(ddof=1)


def fit_random_effect(formula: str, sign: float = 1.0) -> tuple[pd.Series, dict]:
    model = smf.mixedlm(formula, d, groups=d["TransponderHexCode"], re_formula="1").fit(
        reml=True, method="powell", maxiter=1000
    )
    phenotype = pd.Series(
        {bird: sign * float(np.asarray(model.random_effects[bird]).reshape(-1)[0]) for bird in model.random_effects}
    )
    return phenotype, {
        "converged": bool(model.converged),
        "random_intercept_variance": float(model.cov_re.iloc[0, 0]),
        "residual_variance": float(model.scale),
    }


def compare(reference: pd.Series, candidate: pd.Series, diagnostics: dict) -> dict:
    joined = pd.concat([reference, candidate], axis=1, join="inner").dropna()
    return {
        "n": int(len(joined)),
        "pearson_r": float(joined.corr().iloc[0, 1]),
        "spearman_rho": float(spearmanr(joined.iloc[:, 0], joined.iloc[:, 1]).statistic),
        **diagnostics,
    }


early_specs = {
    "no_demographics": "first_feed_centered_m ~ z_Temperature + z_Daylength",
    "daylength_only": "first_feed_centered_m ~ z_Daylength",
    "intercept_only": "first_feed_centered_m ~ 1",
    "date_fixed_effects": "first_feed_centered_m ~ C(date)",
    "date_fixed_effects_plus_daily_total": "first_feed_centered_m ~ C(date) + np.log1p(total_feeding_events)",
}
total_specs = {
    "no_demographics": "total_feeding_events ~ z_Temperature + z_Daylength",
    "daylength_only": "total_feeding_events ~ z_Daylength",
    "intercept_only": "total_feeding_events ~ 1",
    "date_fixed_effects": "total_feeding_events ~ C(date)",
}

results = {
    "purpose": "Calibrate external-study-compatible phenotypes using Alberta predictor data only; no survival outcome is read.",
    "early_chronotype": {},
    "total_feeder_use": {},
}
for name, formula in early_specs.items():
    phenotype, diag = fit_random_effect(formula, sign=-1.0)
    results["early_chronotype"][name] = compare(base["early_chronotype"], phenotype, diag)
for name, formula in total_specs.items():
    phenotype, diag = fit_random_effect(formula)
    results["total_feeder_use"][name] = compare(base["total_blup"], phenotype, diag)

(OUT / "portable_chronotype_calibration.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
