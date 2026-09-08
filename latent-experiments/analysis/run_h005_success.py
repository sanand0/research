#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdata>=1.0", "pandas>=2.2", "numpy>=2.0", "statsmodels>=0.14"]
# ///
"""Run frozen H005 red-kite nesting-success analysis after outcome unseal."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import rdata
import statsmodels.api as sm
from statsmodels.genmod.cov_struct import Exchangeable
from statsmodels.genmod.generalized_estimating_equations import GEE

FEATURES = Path("analysis/red_kite_h005_features.csv")
SOURCE = Path("candidates/red-kite-nesttool/repo/input_data_prepared.rds")
OUTPUT = Path("results/h005_success.json")


def map_success(value: object) -> int:
    """Map only source-documented binary encodings; fail on anything else."""
    if pd.isna(value):
        raise ValueError("missing success label")
    if isinstance(value, (int, float, np.integer, np.floating)):
        if float(value) == 1:
            return 1
        if float(value) == 0:
            return 0
    text = str(value).strip().lower()
    if text in {"yes", "1"}:
        return 1
    if text in {"no", "0"}:
        return 0
    raise ValueError(f"unexpected success label: {value!r}")


def zscore(series: pd.Series) -> pd.Series:
    sd = series.std(ddof=0)
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError(f"cannot standardize {series.name}: sd={sd}")
    return (series - series.mean()) / sd


def fit_gee(data: pd.DataFrame, contraction: str, current: str) -> dict[str, float]:
    d = data.copy()
    d["z_contraction"] = zscore(d[contraction].astype(float))
    d["z_current"] = zscore(d[current].astype(float))
    d["z_age"] = zscore(d["age_cy"].astype(float))
    model = GEE.from_formula(
        "success ~ z_contraction + z_current + C(sex) + z_age + C(year)",
        groups="bird_id",
        data=d,
        family=sm.families.Binomial(),
        cov_struct=Exchangeable(),
    )
    fit = model.fit()
    beta = float(fit.params["z_contraction"])
    se = float(fit.bse["z_contraction"])
    return {
        "beta": beta,
        "se": se,
        "or": float(np.exp(beta)),
        "ci_low": float(np.exp(beta - 1.96 * se)),
        "ci_high": float(np.exp(beta + 1.96 * se)),
        "p": float(fit.pvalues["z_contraction"]),
        "working_correlation": float(np.asarray(fit.cov_struct.dep_params).reshape(-1)[0]),
    }


features = pd.read_csv(FEATURES)
if "success" in features.columns:
    raise AssertionError("outcome leaked into frozen feature file")
if features["year_id"].duplicated().any():
    raise AssertionError("frozen features must be one row per year_id")

obj = rdata.conversion.convert(rdata.parser.parse_file(SOURCE))
outcomes = obj["summary"][["year_id", "success"]].copy()
if outcomes["year_id"].duplicated().any():
    raise AssertionError("source summary must be one row per year_id")

data = features.merge(outcomes, on="year_id", how="left", validate="one_to_one")
if len(data) != len(features):
    raise AssertionError("outcome join changed frozen cohort size")
data["success"] = data["success"].map(map_success)

primary = fit_gee(data, "contraction95", "log_mcp95_incu1")
sensitivity = fit_gee(data, "contraction99", "log_mcp99_incu1")
primary_supported = primary["ci_low"] > 1 or primary["ci_high"] < 1
sensitivity_supported = sensitivity["ci_low"] > 1 or sensitivity["ci_high"] < 1
primary_sign = int(np.sign(primary["beta"]))
sensitivity_sign = int(np.sign(sensitivity["beta"]))
stability = "STABLE" if primary_sign == sensitivity_sign and primary_supported == sensitivity_supported else "SENSITIVE"

result = {
    "hypothesis": "H005",
    "n": int(len(data)),
    "birds": int(data["bird_id"].nunique()),
    "success": int(data["success"].sum()),
    "failure": int((1 - data["success"]).sum()),
    "primary_mcp95": primary,
    "sensitivity_mcp99": sensitivity,
    "decision": "SUPPORTED" if primary_supported else "NOT SUPPORTED",
    "stability": stability,
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
