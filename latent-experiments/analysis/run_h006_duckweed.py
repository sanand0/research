#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["lifelines>=0.30", "numpy>=2", "pandas>=2", "scipy>=1.13"]
# ///
"""Run frozen H006 landmark Cox analyses on the two public duckweed experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test
from scipy.stats import ttest_ind

DATE_COLUMN = re.compile(r"^[A-Z][a-z]{2}\.\d{2}\.\d{4}$")
EXP1_TREATMENTS = {"L01": "1", "L02": "1/2", "L04": "1/4", "L08": "1/8", "L16": "1/16"}
EXP2_TREATMENTS = {"1": "1", "4": "1/4", "1.0": "1", "4.0": "1/4"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def daily_columns(df: pd.DataFrame) -> dict[str, pd.Timestamp]:
    cols = {c: pd.to_datetime(c, format="%b.%d.%Y") for c in df.columns if DATE_COLUMN.match(str(c))}
    if not cols:
        raise ValueError("No daily reproduction columns found")
    return cols


def normalize_treatment(value: object, experiment: int) -> str | None:
    text = str(value).strip()
    if experiment == 1:
        return EXP1_TREATMENTS.get(text)
    return EXP2_TREATMENTS.get(text)


def prepare(path: Path, experiment: int, landmark: int) -> tuple[pd.DataFrame, dict[str, object]]:
    raw = pd.read_csv(path)
    if experiment == 2:
        if "exclude" not in raw:
            raise ValueError("Experiment 2 is missing source exclusion column")
        raw = raw.loc[raw["exclude"].astype(str).str.strip().str.casefold().eq("no")].copy()

    raw["treatment"] = [normalize_treatment(v, experiment) for v in raw["light.treatment"]]
    raw = raw.loc[raw["treatment"].notna()].copy()

    raw["birth"] = pd.to_datetime(raw["date.birth"], format="%b.%d.%Y", errors="raise")
    raw["last"] = pd.to_datetime(raw["date.last.repro"], format="%b.%d.%Y", errors="raise")
    raw["lifespan"] = (raw["last"] - raw["birth"]).dt.days + 1
    if (raw["lifespan"] <= 0).any():
        raise ValueError("Non-positive reproductive lifespan detected")

    # Landmarking removes plants whose reproductive death occurs before the full predictor window.
    eligible = raw.loc[raw["lifespan"] >= landmark + 1].copy()
    dates = daily_columns(eligible)

    early = np.zeros(len(eligible), dtype=float)
    for col, date in dates.items():
        age = (date - eligible["birth"]).dt.days + 1
        in_window = age.between(1, landmark)
        values = pd.to_numeric(eligible[col], errors="coerce").fillna(0).to_numpy(dtype=float)
        early += np.where(in_window.to_numpy(), values, 0.0)
    eligible["early"] = early
    eligible["remaining"] = eligible["lifespan"] - landmark
    eligible["event"] = 1

    means = eligible.groupby("treatment", observed=True)["early"].transform("mean")
    sds = eligible.groupby("treatment", observed=True)["early"].transform(lambda x: x.std(ddof=1))
    if sds.isna().any() or (sds <= 0).any():
        bad = sorted(eligible.loc[sds.isna() | (sds <= 0), "treatment"].unique())
        raise ValueError(f"Zero/undefined early-reproduction SD in treatments: {bad}")
    eligible["early_z"] = (eligible["early"] - means) / sds

    meta = {
        "source_rows": int(len(pd.read_csv(path, usecols=["id"]))),
        "analytic_source_rows": int(len(raw)),
        "landmark": landmark,
        "eligible_n": int(len(eligible)),
        "treatment_n": {str(k): int(v) for k, v in eligible["treatment"].value_counts().sort_index().items()},
        "early_zero_n": int((eligible["early"] == 0).sum()),
        "early_mean": float(eligible["early"].mean()),
        "early_sd": float(eligible["early"].std(ddof=1)),
        "remaining_median": float(eligible["remaining"].median()),
    }
    return eligible, meta


def fit_landmark(path: Path, experiment: int, landmark: int) -> dict[str, object]:
    df, meta = prepare(path, experiment, landmark)
    model_df = df[["remaining", "event", "early_z", "treatment"]].copy()
    cph = CoxPHFitter()
    cph.fit(model_df, duration_col="remaining", event_col="event", strata=["treatment"], robust=True)
    row = cph.summary.loc["early_z"]
    beta = float(row["coef"])
    se = float(row["se(coef)"])
    ci_low = float(row["coef lower 95%"])
    ci_high = float(row["coef upper 95%"])
    hr = math.exp(beta)
    hr_low = math.exp(ci_low)
    hr_high = math.exp(ci_high)
    p = float(row["p"])

    ph = proportional_hazard_test(cph, model_df, time_transform="rank")
    ph_p = float(ph.summary.loc["early_z", "p"])

    return {
        **meta,
        "beta": beta,
        "se": se,
        "hr": hr,
        "ci95": [hr_low, hr_high],
        "p": p,
        "ph_test_p": ph_p,
    }


def support_class(result: dict[str, object]) -> str:
    lo, hi = result["ci95"]
    if lo > 1:
        return "SUPPORTED_TRADEOFF"
    if hi < 1:
        return "CONTRADICTED"
    return "NOT_SUPPORTED"


def known_signal(exp2: Path) -> dict[str, object]:
    df = pd.read_csv(exp2)
    df = df.loc[df["exclude"].astype(str).str.strip().str.casefold().eq("no")].copy()
    df["treatment"] = [normalize_treatment(v, 2) for v in df["light.treatment"]]
    df["birth"] = pd.to_datetime(df["date.birth"], format="%b.%d.%Y", errors="raise")
    df["last"] = pd.to_datetime(df["date.last.repro"], format="%b.%d.%Y", errors="raise")
    df["lifespan"] = (df["last"] - df["birth"]).dt.days + 1
    df["log10_lifespan"] = np.log10(df["lifespan"])
    full = df.loc[df["treatment"] == "1", "log10_lifespan"].to_numpy()
    low = df.loc[df["treatment"] == "1/4", "log10_lifespan"].to_numpy()
    test = ttest_ind(full, low, equal_var=True)
    return {
        "n": int(len(df)),
        "mean_log10_lifespan_full": float(full.mean()),
        "mean_log10_lifespan_quarter": float(low.mean()),
        "t": float(test.statistic),
        "p": float(test.pvalue),
        "direction_matches_source": bool(low.mean() > full.mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp2", type=Path, required=True)
    parser.add_argument("--exp1", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/h006_duckweed.json"))
    args = parser.parse_args()

    primary = fit_landmark(args.exp2, experiment=2, landmark=7)
    day5 = fit_landmark(args.exp2, experiment=2, landmark=5)
    replication = fit_landmark(args.exp1, experiment=1, landmark=7)

    primary_class = support_class(primary)
    day5_class = support_class(day5)
    primary_sign = int(np.sign(primary["beta"]))
    day5_sign = int(np.sign(day5["beta"]))
    rep_sign = int(np.sign(replication["beta"]))
    stability = "STABLE" if primary_sign == day5_sign and primary_class == day5_class else "SENSITIVE"
    rep_ci = replication["ci95"]
    if rep_sign == primary_sign and ((rep_ci[0] > 1 and primary_sign > 0) or (rep_ci[1] < 1 and primary_sign < 0)):
        rep_class = "STRONG_DIRECTIONAL_REPLICATION"
    elif rep_sign == primary_sign:
        rep_class = "DIRECTIONALLY_CONSISTENT"
    elif (rep_ci[0] > 1 and primary_sign < 0) or (rep_ci[1] < 1 and primary_sign > 0):
        rep_class = "CONTRADICTORY"
    else:
        rep_class = "INCONCLUSIVE"

    result = {
        "hypothesis": "H006",
        "source_sha256": {"experiment_2": sha256(args.exp2), "experiment_1": sha256(args.exp1)},
        "known_signal": known_signal(args.exp2),
        "experiment_2_day7_primary": primary,
        "experiment_2_day5_sensitivity": day5,
        "experiment_1_day7_replication": replication,
        "decision": primary_class,
        "stability": stability,
        "replication": rep_class,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"decision": primary_class, "stability": stability, "replication": rep_class}))


if __name__ == "__main__":
    main()
