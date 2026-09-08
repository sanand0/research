#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdata>=1.0", "pandas>=2.2", "numpy>=2.0", "statsmodels>=0.14"]
# ///
"""Run exploratory H005-E complete-case and outcome-availability-weighted analyses."""
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
OUTPUT = Path("results/h005e_success.json")


def parse_success(value: object) -> float:
    if pd.isna(value) or str(value).strip() == "":
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        if float(value) in (0.0, 1.0):
            return float(value)
    text = str(value).strip().lower()
    if text in {"yes", "1"}:
        return 1.0
    if text in {"no", "0"}:
        return 0.0
    raise ValueError(f"unexpected success label: {value!r}")


def zscore(series: pd.Series) -> pd.Series:
    sd = series.std(ddof=0)
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError(f"cannot standardize {series.name}: sd={sd}")
    return (series - series.mean()) / sd


def add_z(data: pd.DataFrame, contraction: str, current: str) -> pd.DataFrame:
    d = data.copy()
    d["z_contraction"] = zscore(d[contraction].astype(float))
    d["z_current"] = zscore(d[current].astype(float))
    d["z_age"] = zscore(d["age_cy"].astype(float))
    return d


def fit_gee(data: pd.DataFrame, contraction: str, current: str, weights: pd.Series | None = None) -> dict[str, float]:
    d = add_z(data, contraction, current)
    model = GEE.from_formula(
        "success ~ z_contraction + z_current + C(sex) + z_age + C(year)",
        groups="bird_id",
        data=d,
        family=sm.families.Binomial(),
        cov_struct=Exchangeable(),
        weights=None if weights is None else np.asarray(weights, dtype=float),
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
obj = rdata.conversion.convert(rdata.parser.parse_file(SOURCE))
outcomes = obj["summary"][["year_id", "success"]].copy()
data = features.merge(outcomes, on="year_id", how="left", validate="one_to_one")
data["success"] = data["success"].map(parse_success)
data["known_outcome"] = data["success"].notna().astype(int)
known = data[data["known_outcome"] == 1].copy()

primary = fit_gee(known, "contraction95", "log_mcp95_incu1")
mcp99 = fit_gee(known, "contraction99", "log_mcp99_incu1")

all_z = add_z(data, "contraction95", "log_mcp95_incu1")
selection = sm.GLM.from_formula(
    "known_outcome ~ z_contraction + z_current + C(sex) + z_age + C(year)",
    data=all_z,
    family=sm.families.Binomial(),
).fit()
p_known = float(data["known_outcome"].mean())
p_hat = np.asarray(selection.predict(all_z), dtype=float)
if np.any(p_hat <= 0):
    raise AssertionError("nonpositive outcome-availability probability")
all_z["ipw"] = p_known / p_hat
known_ipw = all_z[all_z["known_outcome"] == 1].copy()
if float(known_ipw["ipw"].max()) > 10:
    raise AssertionError(f"IPW max exceeds frozen limit: {known_ipw['ipw'].max()}")
ipw = fit_gee(known_ipw, "contraction95", "log_mcp95_incu1", weights=known_ipw["ipw"])

signs = [int(np.sign(x["beta"])) for x in [primary, mcp99, ipw]]
result = {
    "analysis": "H005-E exploratory",
    "frozen_n": int(len(data)),
    "known_n": int(len(known)),
    "birds_known": int(known["bird_id"].nunique()),
    "success": int(known["success"].sum()),
    "failure": int((1 - known["success"]).sum()),
    "primary_complete_case_mcp95": primary,
    "sensitivity_complete_case_mcp99": mcp99,
    "sensitivity_ipw_mcp95": ipw,
    "ipw_min": float(known_ipw["ipw"].min()),
    "ipw_max": float(known_ipw["ipw"].max()),
    "sign_stability": "STABLE" if len(set(signs)) == 1 else "SENSITIVE",
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
