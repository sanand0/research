#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "lifelines>=0.30",
#   "pandas>=2.2",
# ]
# ///

"""Frozen NHANES III food-frequency mortality screen.

Only model2 is validated and reported. model2_common/model3 are exploratory
replication diagnostics pending exact reconciliation with the 2017 paper.

The primary analysis changes only the food exposure: all 60 predefined named
times/month fields are recoded as any consumption vs none, then fitted with the
same demographic Cox model. Free-text "other food" slots are excluded.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
from pathlib import Path

import pandas as pd
from lifelines import CoxPHFitter

from nhanes_pilot import read_mortality


ADULT_DATA = Path("data/nhanes3/adult.dat")
MORTALITY_DATA = Path("data/nhanes3/mortality/NHANES_III_MORT_2019_PUBLIC.dat")
REGISTRY = Path("nhanes3-food-registry.csv")
RESULTS = Path("results/nhanes3_food_headline_factory.csv")

_ADULT: pd.DataFrame | None = None
_MORTALITY: pd.DataFrame | None = None
_ALCOHOL: pd.DataFrame | None = None
_MODEL = "model2"

EXAM_DATA = Path("data/nhanes3/exam.dat")

CORE = {
    "SEQN": (1, 5),
    "DMARACER": (13, 13),
    "DMAETHNR": (14, 14),
    "HSSEX": (15, 15),
    "HSAGEIR": (18, 19),
    "SDPPSU6": (43, 43),
    "SDPSTRA6": (44, 45),
    "WTPFQX6": (52, 60),
    "HFA8R": (1256, 1257),
    "HFA12": (1258, 1259),
    "HFF18": (1408, 1408),
    "HAS1": (2338, 2338),
    "HAR1": (2281, 2281),
    "HAR3": (2285, 2285),
    "HAT1S": (2389, 2392),
    "HAT1MET": (2393, 2395),
    "HAT3S": (2398, 2401),
    "HAT2MET": (2397, 2397),
    "HAT5S": (2404, 2407),
    "HAT4MET": (2403, 2403),
    "HAT7S": (2410, 2413),
    "HAT6MET": (2409, 2409),
    "HAT9S": (2416, 2419),
    "HAT8MET": (2415, 2415),
    "HAT11S": (2424, 2427),
    "HAT10MET": (2421, 2423),
    "HAT13S": (2432, 2435),
    "HAT12MET": (2429, 2431),
    "HAT15S": (2438, 2441),
    "HAT14MET": (2437, 2437),
    "HAT17S": (2444, 2447),
    "HAT16MET": (2443, 2443),
    "HAT20S": (2458, 2461),
    "HAT19MET": (2454, 2457),
    "HAT22S": (2470, 2473),
    "HAT21MET": (2467, 2469),
    "HAT24S": (2482, 2485),
    "HAT23MET": (2479, 2481),
    "HAT26S": (2494, 2497),
    "HAT25MET": (2491, 2493),
}

FRUIT_VARS = ["HAN3AS", "HAN3BS", "HAN3CS", "HAN3DS", "HAN3ES", "HAN3FS"]
VEGETABLE_VARS = ["HAN4AS", "HAN4BS", "HAN4CS", "HAN4GS", "HAN4HS", "HAN4IS", "HAN4LS"]
MEAT_VARS = ["HAN2CS", "HAN2DS", "HAN2ES", "HAN2FS"]
ACTIVITY_PAIRS = [
    ("HAT1S", "HAT1MET"),
    ("HAT3S", "HAT2MET"),
    ("HAT5S", "HAT4MET"),
    ("HAT7S", "HAT6MET"),
    ("HAT9S", "HAT8MET"),
    ("HAT11S", "HAT10MET"),
    ("HAT13S", "HAT12MET"),
    ("HAT15S", "HAT14MET"),
    ("HAT17S", "HAT16MET"),
    ("HAT20S", "HAT19MET"),
    ("HAT22S", "HAT21MET"),
    ("HAT24S", "HAT23MET"),
    ("HAT26S", "HAT25MET"),
]


def parse_number(text: str) -> float:
    value = text.strip()
    if not value:
        return math.nan
    try:
        return float(value)
    except ValueError:
        return math.nan


def read_registry(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def food_consumer(series: pd.Series) -> pd.Series:
    """Any reported monthly consumption vs never; 8/9 fill codes are missing."""
    numeric = pd.to_numeric(series, errors="coerce")
    invalid = numeric.isin([888, 999, 8888, 9999])
    valid = numeric.where(~invalid & numeric.ge(0))
    return (valid > 0).astype(float).where(valid.notna())


def education_group(series: pd.Series) -> pd.Series:
    """Paper-like schooling groups: none, grades 1-8, 9-11, >=12."""
    value = pd.to_numeric(series, errors="coerce")
    result = pd.Series(math.nan, index=series.index)
    result[value == 0] = 0
    result[value.between(1, 8)] = 1
    result[value.between(9, 11)] = 2
    result[value.between(12, 17)] = 3
    return result


def marital_group(series: pd.Series) -> pd.Series:
    """Married/partnered, widowed-divorced-separated, never married."""
    value = pd.to_numeric(series, errors="coerce")
    result = pd.Series(math.nan, index=series.index)
    result[value.isin([1, 2, 3])] = 1
    result[value.isin([4, 5, 6])] = 2
    result[value == 7] = 3
    return result


def bh_adjust(pvalues: pd.Series) -> list[float]:
    p = pd.Series(pvalues, dtype=float)
    order = p.sort_values().index
    ranked = p.loc[order]
    m = len(ranked)
    adjusted = ranked * m / pd.Series(range(1, m + 1), index=order)
    adjusted = adjusted.iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return adjusted.reindex(p.index).tolist()


def field(line: str, start: int, end: int) -> float:
    return parse_number(line[start - 1 : end])


def read_adult(path: Path, registry: pd.DataFrame) -> pd.DataFrame:
    foods = {
        row.variable: (int(row.start), int(row.end))
        for row in registry.itertuples(index=False)
    }
    rows = []
    with path.open(encoding="ascii") as handle:
        for line in handle:
            row = {name: field(line, *span) for name, span in CORE.items()}
            row.update({name: field(line, *span) for name, span in foods.items()})
            rows.append(row)
    return pd.DataFrame(rows)




def monthly_frequency(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.where(numeric.ge(0) & ~numeric.isin([888, 999, 8888, 9999]))


def current_smoker(adult: pd.DataFrame) -> pd.Series:
    ever = adult["HAR1"]
    now = adult["HAR3"]
    result = pd.Series(math.nan, index=adult.index)
    result[ever == 2] = 0
    result[(ever == 1) & (now == 2)] = 0
    result[(ever == 1) & (now == 1)] = 1
    return result


def activity_group(adult: pd.DataFrame) -> pd.Series:
    moderate = pd.Series(0.0, index=adult.index)
    vigorous = pd.Series(0.0, index=adult.index)
    for freq_name, met_name in ACTIVITY_PAIRS:
        freq_raw = pd.to_numeric(adult[freq_name], errors="coerce")
        invalid_freq = freq_raw.isin([8888, 9999])
        freq = freq_raw.where(~invalid_freq).fillna(0)
        met = pd.to_numeric(adult[met_name], errors="coerce")
        met = met.where(~met.isin([88, 99, 888, 999, 8888, 9999]))
        met = met.where(met <= 20, met / 100)
        active = freq > 0
        moderate += freq.where(active & met.between(3, 6), 0)
        vigorous += freq.where(active & (met > 6), 0)

    result = pd.Series(0.0, index=adult.index)
    result[moderate >= 5 * 4.3] = 1
    result[vigorous >= 3 * 4.3] = 2
    return result


def strict_frequency_sum(adult: pd.DataFrame, variables: list[str]) -> pd.Series:
    values = pd.concat(
        [monthly_frequency(adult[name]).rename(name) for name in variables],
        axis=1,
    )
    return values.sum(axis=1, min_count=len(variables))


def read_exam_alcohol(path: Path) -> pd.DataFrame:
    rows = []
    with path.open(encoding="ascii") as handle:
        for line in handle:
            seqn = field(line, 1, 5)
            phase1 = field(line, 5110, 5110)
            phase2 = field(line, 4628, 4628)
            value = phase1 if phase1 in (1, 2) else phase2
            current = 1.0 if value == 1 else 0.0 if value == 2 else math.nan
            rows.append({"SEQN": seqn, "CURRENT_DRINKER": current})
    return pd.DataFrame(rows)


def prepare_covariates(adult: pd.DataFrame) -> pd.DataFrame:
    out = adult.copy()
    out = out[out["HSAGEIR"] >= 18]
    out["RACE"] = out["DMARACER"].where(out["DMARACER"].isin([1, 2, 3]))
    out["ETHNICITY"] = out["DMAETHNR"].where(out["DMAETHNR"].isin([1, 2, 3]))
    out["SEX"] = out["HSSEX"].where(out["HSSEX"].isin([1, 2]))
    out["EDUCATION"] = education_group(out["HFA8R"])
    out["MARITAL"] = marital_group(out["HFA12"])
    out["LOW_INCOME"] = out["HFF18"].map({1.0: 1.0, 2.0: 0.0})
    out["EMPLOYED"] = out["HAS1"].map({1.0: 1.0, 2.0: 0.0})
    out["CURRENT_SMOKER"] = current_smoker(out)
    out["ACTIVITY"] = activity_group(out)
    out["FRUIT_FREQ"] = strict_frequency_sum(out, FRUIT_VARS)
    out["VEGETABLE_FREQ"] = strict_frequency_sum(out, VEGETABLE_VARS)
    out["MEAT_FREQ"] = strict_frequency_sum(out, MEAT_VARS)
    out["WEIGHT"] = out["WTPFQX6"].where(out["WTPFQX6"] > 0)
    out["CLUSTER"] = out["SDPSTRA6"] * 10 + out["SDPPSU6"]
    return out


def model_frame(
    adult: pd.DataFrame,
    mortality: pd.DataFrame,
    variable: str,
    model_name: str,
    alcohol: pd.DataFrame | None,
) -> pd.DataFrame:
    exposure = food_consumer(adult[variable])
    source = prepare_covariates(adult.assign(EXPOSURE=exposure))
    merged = source.merge(mortality, on="SEQN", how="inner")
    merged = merged[
        (merged["ELIGSTAT"] == 1)
        & merged["MORTSTAT"].isin([0, 1])
        & merged["PERMTH_INT"].gt(0)
    ]
    columns = [
        "PERMTH_INT",
        "MORTSTAT",
        "WEIGHT",
        "CLUSTER",
        "EXPOSURE",
        "HSAGEIR",
        "SEX",
        "RACE",
        "ETHNICITY",
        "EDUCATION",
        "MARITAL",
        "LOW_INCOME",
        "EMPLOYED",
    ]
    categorical = ["SEX", "RACE", "ETHNICITY", "EDUCATION", "MARITAL"]

    if model_name in {"model2_common", "model3"}:
        if alcohol is None:
            raise RuntimeError("Alcohol data required for common/model3 analysis")
        merged = merged.merge(alcohol, on="SEQN", how="left")
        lifestyle = [
            "CURRENT_SMOKER",
            "CURRENT_DRINKER",
            "ACTIVITY",
            "FRUIT_FREQ",
            "VEGETABLE_FREQ",
            "MEAT_FREQ",
        ]
        merged = merged.dropna(subset=lifestyle)
        if model_name == "model3":
            columns += lifestyle
            categorical.append("ACTIVITY")

    frame = merged[columns].dropna().copy()
    return pd.get_dummies(frame, columns=categorical, drop_first=True, dtype=float)


def fit_food(frame: pd.DataFrame, variable: str, label: str) -> dict:
    counts = frame["EXPOSURE"].value_counts()
    n0 = int(counts.get(0, 0))
    n1 = int(counts.get(1, 0))
    deaths = int(frame["MORTSTAT"].sum())
    base = {
        "variable": variable,
        "label": label,
        "n": len(frame),
        "deaths": deaths,
        "nonconsumers": n0,
        "consumers": n1,
    }
    if min(n0, n1) < 100 or deaths < 100:
        return {**base, "status": "insufficient group size"}

    model = CoxPHFitter()
    model.fit(
        frame,
        duration_col="PERMTH_INT",
        event_col="MORTSTAT",
        weights_col="WEIGHT",
        cluster_col="CLUSTER",
        robust=True,
    )
    row = model.summary.loc["EXPOSURE"]
    return {
        **base,
        "hr": float(math.exp(row["coef"])),
        "ci_low": float(math.exp(row["coef lower 95%"])),
        "ci_high": float(math.exp(row["coef upper 95%"])),
        "p": float(row["p"]),
        "status": "ok",
    }


def fit_task(task: tuple[str, str]) -> dict:
    if _ADULT is None or _MORTALITY is None:
        raise RuntimeError("Worker data not initialized")
    variable, label = task
    frame = model_frame(_ADULT, _MORTALITY, variable, _MODEL, _ALCOHOL)
    result = fit_food(frame, variable, label)
    result["model"] = _MODEL
    return result


def analyze(
    start: int = 0,
    end: int | None = None,
    workers: int = 1,
    model_name: str = "model2",
) -> pd.DataFrame:
    global _ADULT, _MORTALITY, _ALCOHOL, _MODEL

    registry = read_registry(REGISTRY)
    _ADULT = read_adult(ADULT_DATA, registry)
    _MORTALITY = read_mortality(MORTALITY_DATA)
    _MODEL = model_name
    _ALCOHOL = (
        read_exam_alcohol(EXAM_DATA)
        if model_name in {"model2_common", "model3"}
        else None
    )

    selected = registry.iloc[start:end]
    tasks = [(row.variable, row.label) for row in selected.itertuples(index=False)]
    if workers > 1 and len(tasks) > 1:
        context = mp.get_context("fork")
        with context.Pool(processes=min(workers, len(tasks))) as pool:
            results = pool.map(fit_task, tasks)
    else:
        results = [fit_task(task) for task in tasks]

    output = pd.DataFrame(results)
    if len(output):
        valid = output["p"].notna()
        output["q_bh"] = math.nan
        output.loc[valid, "q_bh"] = bh_adjust(output.loc[valid, "p"])
        output["is_chili"] = output["variable"].eq("HAN4JS")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--model",
        choices=["model2", "model2_common", "model3"],
        default="model2",
    )
    args = parser.parse_args()

    results = analyze(args.start, args.end, args.workers, args.model)
    out = args.out or (
        RESULTS
        if args.model == "model2"
        else Path(f"results/nhanes3_food_{args.model}_exploratory.csv")
    )
    out.parent.mkdir(exist_ok=True)
    results.to_csv(out, index=False)
    print(
        results.sort_values("p", na_position="last")[
            [
                "variable",
                "label",
                "n",
                "nonconsumers",
                "consumers",
                "hr",
                "ci_low",
                "ci_high",
                "p",
                "q_bh",
                "is_chili",
                "status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
