#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14"]
# ///
"""Reproduce Hobbs et al. bird-day timing phenotypes without reading survival outcomes.

This intentionally uses separate Gaussian random-intercept models in statsmodels because
R/MCMCglmm is unavailable in the LocalMCP environment. The exact deviation and downstream
uncertainty rule are frozen in analysis-plan-001.md before outcome access.
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
TIMING = ROOT / "candidates/chickadees-timing"
OUT = ROOT / "analysis"
RAW = TIMING / "2022-2023data.csv"
AUTHOR_R = TIMING / "analysis.R"
WEATHER = TIMING / "TempDay2023.csv"
AGES = TIMING / "Age_Sex_V2.csv"


def minutes(value: str) -> float:
    """Convert HH:MM[:SS[.fraction]] to minutes after midnight."""
    h, m, s = value.split(":")
    return int(h) * 60 + int(m) + float(s) / 60


def feeder14_exclusions() -> set[str]:
    """Extract the author's explicit feeder-14 exclusion list from their R script."""
    text = AUTHOR_R.read_text()
    block = text[text.index("# Data filtering: feeder 14 hex codes"):text.index('write.csv(feederdays_c')]
    ids = set(re.findall(r'TransponderHexCode != "([0-9A-F]+)"', block))
    assert len(ids) == 52, f"Expected 52 feeder-14 exclusions, got {len(ids)}"
    return ids


def read_weather() -> dict[str, dict[str, str]]:
    with WEATHER.open(newline="", encoding="utf-8-sig") as f:
        return {row["date"]: row for row in csv.DictReader(f)}


def read_ages() -> dict[str, dict[str, str]]:
    with AGES.open(newline="", encoding="utf-8-sig") as f:
        return {row["TransponderHexCode"]: row for row in csv.DictReader(f)}


def aggregate_bird_days() -> pd.DataFrame:
    excluded = feeder14_exclusions()
    agg: dict[tuple[str, str], list[object]] = {}
    raw_rows = winter_rows = 0
    dates: set[str] = set()

    with RAW.open(newline="") as f:
        for row in csv.DictReader(f):
            raw_rows += 1
            if row["type"] != "bird":
                continue
            date = row["Date_Time"][:10]
            if not ("2022-12-01" <= date <= "2023-02-28"):
                continue
            winter_rows += 1
            bird = row["TransponderHexCode"]
            if bird in excluded:
                continue
            dates.add(date)
            key = (bird, date)
            time = row["Time"]
            if key not in agg:
                agg[key] = [time, time, 1]
            else:
                if time < agg[key][0]:
                    agg[key][0] = time
                if time > agg[key][1]:
                    agg[key][1] = time
                agg[key][2] += 1

    weather = read_weather()
    ages = read_ages()
    unsexed = {"01103F4581", "01103F79A2", "01103F82A5", "01103FB625", "0110174F9C"}
    rows = []
    for (bird, date), (first, last, total) in agg.items():
        if total < 10 or bird in unsexed or bird not in ages or date not in weather:
            continue
        age = ages[bird]
        sex = age["SexConclusion"]
        if not sex or sex == "Unknown" or not age["MaxHatchYear"]:
            continue
        min_age = 2023 - int(float(age["MaxHatchYear"]))
        age_cat = "J" if min_age == 1 else "A"
        age_sex = f"{age_cat} {sex}"
        w = weather[date]
        rows.append(
            {
                "TransponderHexCode": bird,
                "date": date,
                "first_feeding_event": first,
                "last_feeding_event": last,
                "total_feeding_events": int(total),
                "Temperature": float(w["Temperature"]),
                "Daylength": float(w["Daylength"]),
                "Sunrise": w["Sunrise"],
                "Sunset": w["Sunset"],
                "AgeSex": age_sex,
                "first_feed_centered_m": minutes(first) - minutes(w["Sunrise"] + ":00" if w["Sunrise"].count(":") == 1 else w["Sunrise"]),
            }
        )

    df = pd.DataFrame(rows).sort_values(["TransponderHexCode", "date"]).reset_index(drop=True)
    meta = {
        "raw_rows": raw_rows,
        "winter_bird_rows_before_feeder14_exclusion": winter_rows,
        "feeder14_excluded_ids": len(excluded),
        "winter_dates_after_filter": len(dates),
        "analytic_bird_days": int(len(df)),
        "analytic_birds": int(df.TransponderHexCode.nunique()),
        "mean_days_per_bird": float(df.groupby("TransponderHexCode").size().mean()),
        "sd_days_per_bird": float(df.groupby("TransponderHexCode").size().std(ddof=1)),
    }
    print(json.dumps(meta, indent=2))
    # These are independently visible in the authors' script/output construction.
    assert meta["winter_dates_after_filter"] == 90, meta
    assert meta["analytic_birds"] == 143, meta
    assert meta["analytic_bird_days"] == 11761, meta
    return df


def fit_random_intercepts(df: pd.DataFrame, suffix: str) -> tuple[pd.DataFrame, dict]:
    data = df.copy()
    for col in ["Temperature", "Daylength"]:
        data[f"z_{col}"] = (data[col] - data[col].mean()) / data[col].std(ddof=1)

    models = {
        "first": smf.mixedlm(
            "first_feed_centered_m ~ C(AgeSex) + z_Temperature + z_Daylength",
            data,
            groups=data["TransponderHexCode"],
            re_formula="1",
        ).fit(reml=True, method="powell", maxiter=1000),
        "total": smf.mixedlm(
            "total_feeding_events ~ C(AgeSex) + z_Temperature + z_Daylength",
            data,
            groups=data["TransponderHexCode"],
            re_formula="1",
        ).fit(reml=True, method="powell", maxiter=1000),
    }

    ids = sorted(set(data.TransponderHexCode))
    out = pd.DataFrame({"TransponderHexCode": ids})
    diagnostics: dict[str, object] = {}
    for name, model in models.items():
        blup = {bird: float(np.asarray(model.random_effects[bird]).reshape(-1)[0]) for bird in ids}
        tau2 = float(model.cov_re.iloc[0, 0])
        sigma2 = float(model.scale)
        n = data.groupby("TransponderHexCode").size()
        cond_sd = {bird: math.sqrt(1 / (1 / tau2 + int(n[bird]) / sigma2)) for bird in ids}
        out[f"{name}_blup"] = out.TransponderHexCode.map(blup)
        out[f"{name}_blup_sd"] = out.TransponderHexCode.map(cond_sd)
        diagnostics[name] = {
            "converged": bool(model.converged),
            "nobs": int(model.nobs),
            "random_intercept_variance": tau2,
            "residual_variance": sigma2,
            "fixed_effects": {k: float(v) for k, v in model.fe_params.items()},
            "llf": float(model.llf),
        }

    # Hobbs coding: smaller first_feed_centered_m = earlier. Reverse sign for interpretation.
    out["early_chronotype"] = -out["first_blup"]
    out["AgeSex"] = out.TransponderHexCode.map(data.drop_duplicates("TransponderHexCode").set_index("TransponderHexCode")["AgeSex"])
    out.to_csv(OUT / f"timing_phenotypes_{suffix}.csv", index=False)
    (OUT / f"timing_fit_{suffix}.json").write_text(json.dumps(diagnostics, indent=2))
    return out, diagnostics


def residual_means(df: pd.DataFrame) -> pd.DataFrame:
    """Predeclared simpler phenotype sensitivity: bird-level means of fixed-effect residuals."""
    data = df.copy()
    for col in ["Temperature", "Daylength"]:
        data[f"z_{col}"] = (data[col] - data[col].mean()) / data[col].std(ddof=1)
    first = smf.ols("first_feed_centered_m ~ C(AgeSex) + z_Temperature + z_Daylength", data).fit()
    total = smf.ols("total_feeding_events ~ C(AgeSex) + z_Temperature + z_Daylength", data).fit()
    data["first_resid"] = first.resid
    data["total_resid"] = total.resid
    out = data.groupby("TransponderHexCode", as_index=False).agg(
        first_resid_mean=("first_resid", "mean"), total_resid_mean=("total_resid", "mean"), AgeSex=("AgeSex", "first")
    )
    out["early_resid_mean"] = -out["first_resid_mean"]
    out.to_csv(OUT / "timing_phenotypes_residual_means.csv", index=False)


def main() -> None:
    df = aggregate_bird_days()
    df.to_csv(OUT / "timing_birddays_full.csv", index=False)
    full, full_diag = fit_random_intercepts(df, "full")
    shared_df = df[(df.date >= "2023-01-09") & (df.date <= "2023-02-14")].copy()
    shared_df.to_csv(OUT / "timing_birddays_shared_window.csv", index=False)
    shared, shared_diag = fit_random_intercepts(shared_df, "shared_window")
    residual_means(df)
    summary = {
        "full": {"birds": int(full.TransponderHexCode.nunique()), "bird_days": int(len(df)), "model": full_diag},
        "shared_window": {"birds": int(shared.TransponderHexCode.nunique()), "bird_days": int(len(shared_df)), "model": shared_diag},
        "note": "No survival file is read by this script.",
    }
    (OUT / "timing_preoutcome_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"full_birds": len(full), "shared_birds": len(shared), "shared_bird_days": len(shared_df)}, indent=2))


if __name__ == "__main__":
    main()
