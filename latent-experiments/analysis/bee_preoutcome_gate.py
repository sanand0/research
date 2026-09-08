#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13"]
# ///
"""Outcome-blind feasibility/stability checks for honey-bee level-vs-history H004."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SRC = Path("candidates/honey-bee-peirson/predictors_2014_alberta.csv")
OUT = Path("analysis/bee_preoutcome_gate.json")

df = pd.read_csv(SRC, parse_dates=["Inspection Date"])
meta = df.drop_duplicates("Colony Number").set_index("Colony Number")[["Region", "Apiary", "Patties", "Fumagillin", "ColonyGroup"]]

rows = []
for colony, g in df.dropna(subset=["Adults"]).groupby("Colony Number"):
    g = g.sort_values("Inspection Date")
    if set(g["Date"]) != {"May 2014", "June 2014", "August 2014"}:
        continue
    days = (g["Inspection Date"] - g["Inspection Date"].min()).dt.days.to_numpy(dtype=float)
    y = np.log1p(g["Adults"].to_numpy(dtype=float))
    slope_per30 = np.polyfit(days, y, 1)[0] * 30
    vals = g.set_index("Date")
    recent = (
        np.log1p(vals.at["August 2014", "Adults"]) - np.log1p(vals.at["June 2014", "Adults"])
    ) / ((vals.at["August 2014", "Inspection Date"] - vals.at["June 2014", "Inspection Date"]).days / 30)
    may_aug = (
        np.log1p(vals.at["August 2014", "Adults"]) - np.log1p(vals.at["May 2014", "Adults"])
    ) / ((vals.at["August 2014", "Inspection Date"] - vals.at["May 2014", "Inspection Date"]).days / 30)
    rows.append(
        {
            "Colony Number": colony,
            "aug_log_adults": float(np.log1p(vals.at["August 2014", "Adults"])),
            "may_log_adults": float(np.log1p(vals.at["May 2014", "Adults"])),
            "slope_3pt_log_per30d": float(slope_per30),
            "slope_recent_log_per30d": float(recent),
            "slope_may_aug_log_per30d": float(may_aug),
        }
    )
feat = pd.DataFrame(rows).set_index("Colony Number").join(meta)

# Secondary brood history, not used to choose primary unless the adult phenotype fails.
brood_rows = []
for colony, g in df.dropna(subset=["Worker Cells"]).groupby("Colony Number"):
    g = g.sort_values("Inspection Date")
    if set(g["Date"]) != {"May 2014", "June 2014", "August 2014"}:
        continue
    days = (g["Inspection Date"] - g["Inspection Date"].min()).dt.days.to_numpy(dtype=float)
    y = np.log1p(g["Worker Cells"].to_numpy(dtype=float))
    brood_rows.append((colony, np.polyfit(days, y, 1)[0] * 30))
brood = pd.Series(dict(brood_rows), name="brood_slope")

corr = lambda x, y: float(spearmanr(x, y).statistic)
r_defs = {
    "three_point_vs_recent": corr(feat["slope_3pt_log_per30d"], feat["slope_recent_log_per30d"]),
    "three_point_vs_may_aug": corr(feat["slope_3pt_log_per30d"], feat["slope_may_aug_log_per30d"]),
    "three_point_vs_aug_size": corr(feat["slope_3pt_log_per30d"], feat["aug_log_adults"]),
    "three_point_vs_may_size": corr(feat["slope_3pt_log_per30d"], feat["may_log_adults"]),
}
common = feat.index.intersection(brood.index)
r_defs["adult_vs_brood_three_point"] = corr(feat.loc[common, "slope_3pt_log_per30d"], brood.loc[common])

# Residual trajectory variation conditional on current size + region + randomized treatments.
X = pd.get_dummies(
    feat[["aug_log_adults", "Region", "Patties", "Fumagillin"]],
    columns=["Region", "Patties", "Fumagillin"],
    drop_first=True,
    dtype=float,
)
X.insert(0, "intercept", 1.0)
y = feat["slope_3pt_log_per30d"].to_numpy()
beta, *_ = np.linalg.lstsq(X.to_numpy(), y, rcond=None)
resid = y - X.to_numpy() @ beta

summary = {
    "n_complete_adult": int(len(feat)),
    "n_complete_brood": int(len(brood)),
    "regions": {str(k): int(v) for k, v in feat["Region"].value_counts().items()},
    "apiaries": int(feat["Apiary"].nunique()),
    "correlations_spearman": r_defs,
    "slope_sd": float(feat["slope_3pt_log_per30d"].std()),
    "slope_resid_after_aug_region_treatments_sd": float(np.std(resid, ddof=1)),
    "residual_fraction_sd": float(np.std(resid, ddof=1) / feat["slope_3pt_log_per30d"].std()),
    "slope_quantiles": {
        str(q): float(v)
        for q, v in feat["slope_3pt_log_per30d"].quantile([0.05, 0.25, 0.5, 0.75, 0.95]).items()
    },
}
OUT.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
