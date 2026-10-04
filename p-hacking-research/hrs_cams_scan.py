#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "lifelines>=0.30",
#   "pandas>=2.2",
#   "pyreadstat>=1.3",
# ]
# ///

"""HRS/CAMS activity mortality headline-factory scan.

Primary estimand was frozen before looking at activity-mortality associations:
31 side-by-side CAMS activity-hour questions (A1-A31), each coded any time vs
zero time, with the same NDI mortality outcome and covariate model.

The script expects HRS/CAMS public-use files under data/hrs/. Obtain them from
the official HRS download site after registration. Raw data remain gitignored
and must not be redistributed under HRS conditions of use.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pyreadstat
from lifelines import CoxPHFitter


CAMS = Path("data/hrs/CAMS01_R.dta")
RAND_HRS = Path("data/hrs/randhrs2000_2014v2.dta")
REGISTRY = Path("hrs-cams-activity-registry.csv")
RESULTS = Path("results/hrs_cams_activity_headline_factory.csv")
BASELINE = pd.Timestamp("2001-09-01")
CUTOFF = pd.Timestamp("2012-12-31")

HRS_COLUMNS = [
    "hhidpn",
    "r5wtresp",
    "r5agey_e",
    "ragender",
    "raracem",
    "raedyrs",
    "r5shlt",
    "h5atotw",
    "r5mstat",
    "r5work",
    "r5depres",
    "r5cancre",
    "r5lunge",
    "r5hearte",
    "r5stroke",
    "r5arthre",
    "r5diabe",
    "r5hibpe",
    "r5adla",
    "r5iadla",
    "r5mobila",
    "randate",
]

CONDITIONS = [
    "r5cancre",
    "r5lunge",
    "r5hearte",
    "r5stroke",
    "r5arthre",
    "r5diabe",
    "r5hibpe",
]


def read_registry(path: Path = REGISTRY) -> pd.DataFrame:
    return pd.read_csv(path)


def make_hhidpn(hhid: object, pn: object) -> int:
    h = str(int(float(hhid))).zfill(6)
    p = str(int(float(pn))).zfill(3)
    return int(h + p)


def any_time(series: pd.Series) -> pd.Series:
    value = pd.to_numeric(series, errors="coerce")
    value = value.where(value >= 0)
    return (value > 0).astype(float).where(value.notna())


def married(series: pd.Series) -> pd.Series:
    value = pd.to_numeric(series, errors="coerce")
    result = pd.Series(math.nan, index=series.index, dtype=float)
    result[value.isin([1, 2, 3])] = 1.0
    result[value.isin([4, 5, 6, 7, 8])] = 0.0
    return result


def survival_from_ndi(
    death_date: pd.Series,
    *,
    baseline: pd.Timestamp = BASELINE,
    cutoff: pd.Timestamp = CUTOFF,
) -> tuple[pd.Series, pd.Series]:
    d = pd.to_datetime(death_date, errors="coerce")
    event = (d.notna() & (d >= baseline) & (d <= cutoff)).astype(int)
    end = d.where(event.eq(1), cutoff)
    duration = (end - baseline).dt.days / 365.25
    duration = duration.where(duration > 0)
    return duration, event


def bh_adjust(pvalues: pd.Series) -> list[float]:
    p = pd.Series(pvalues, dtype=float)
    order = p.sort_values().index
    ranked = p.loc[order]
    m = len(ranked)
    adjusted = ranked * m / pd.Series(range(1, m + 1), index=order)
    adjusted = adjusted.iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return adjusted.reindex(p.index).tolist()


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    cams = pd.read_stata(CAMS, convert_categoricals=False)
    ids = [
        make_hhidpn(hhid, pn)
        for hhid, pn in zip(cams["HHID"], cams["PN"], strict=True)
    ]
    cams = cams.copy()
    cams["hhidpn"] = ids
    hrs, _ = pyreadstat.read_dta(RAND_HRS, usecols=HRS_COLUMNS)
    return cams, hrs


def prepare_base(cams: pd.DataFrame, hrs: pd.DataFrame) -> pd.DataFrame:
    d = cams.merge(hrs, on="hhidpn", how="inner", validate="one_to_one").copy()

    ndi = pd.to_datetime(
        pd.to_numeric(d["randate"], errors="coerce"),
        unit="D",
        origin="1960-01-01",
        errors="coerce",
    )
    duration, event = survival_from_ndi(ndi)
    d["DURATION"] = duration
    d["EVENT"] = event
    d["WEIGHT"] = pd.to_numeric(d["r5wtresp"], errors="coerce").where(
        pd.to_numeric(d["r5wtresp"], errors="coerce") > 0
    )
    d["AGE"] = pd.to_numeric(d["r5agey_e"], errors="coerce")
    d["SEX"] = pd.to_numeric(d["ragender"], errors="coerce").where(
        pd.to_numeric(d["ragender"], errors="coerce").isin([1, 2])
    )
    d["RACE"] = pd.to_numeric(d["raracem"], errors="coerce").where(
        pd.to_numeric(d["raracem"], errors="coerce").isin([1, 2, 3])
    )
    d["EDUCATION"] = pd.to_numeric(d["raedyrs"], errors="coerce").where(
        pd.to_numeric(d["raedyrs"], errors="coerce").between(0, 25)
    )
    d["SELF_HEALTH"] = pd.to_numeric(d["r5shlt"], errors="coerce").where(
        pd.to_numeric(d["r5shlt"], errors="coerce").between(1, 5)
    )
    wealth = pd.to_numeric(d["h5atotw"], errors="coerce")
    d["WEALTH"] = wealth
    d["MARRIED"] = married(d["r5mstat"])
    d["EMPLOYED"] = pd.to_numeric(d["r5work"], errors="coerce").where(
        pd.to_numeric(d["r5work"], errors="coerce").isin([0, 1])
    )
    d["DEPRESSED"] = pd.to_numeric(d["r5depres"], errors="coerce").where(
        pd.to_numeric(d["r5depres"], errors="coerce").isin([0, 1])
    )
    for source in CONDITIONS:
        target = source.upper()
        d[target] = pd.to_numeric(d[source], errors="coerce").where(
            pd.to_numeric(d[source], errors="coerce").isin([0, 1])
        )
    d["ADL"] = pd.to_numeric(d["r5adla"], errors="coerce").where(
        pd.to_numeric(d["r5adla"], errors="coerce").between(0, 5)
    )
    d["IADL"] = pd.to_numeric(d["r5iadla"], errors="coerce").where(
        pd.to_numeric(d["r5iadla"], errors="coerce").between(0, 3)
    )
    d["MOBILITY"] = pd.to_numeric(d["r5mobila"], errors="coerce").where(
        pd.to_numeric(d["r5mobila"], errors="coerce").between(0, 5)
    )

    return d


PAPER_COLUMNS = [
    "DURATION",
    "EVENT",
    "WEIGHT",
    "EXPOSURE",
    "AGE",
    "SEX",
    "RACE",
    "EDUCATION",
    "SELF_HEALTH",
    "WEALTH",
    "MARRIED",
    "EMPLOYED",
    "DEPRESSED",
] + [x.upper() for x in CONDITIONS]

FUNCTIONAL_COLUMNS = PAPER_COLUMNS + ["ADL", "IADL", "MOBILITY"]


def columns_for_model(model_name: str) -> list[str]:
    if model_name == "paper_like":
        return PAPER_COLUMNS
    if model_name == "functional":
        return FUNCTIONAL_COLUMNS
    raise ValueError(f"Unknown model: {model_name}")


def common_sample_mask(
    base: pd.DataFrame,
    registry: pd.DataFrame,
    model_name: str,
) -> pd.Series:
    activities = registry["variable"].tolist()
    required = [
        c for c in columns_for_model(model_name) if c != "EXPOSURE"
    ]
    mask = base[required].notna().all(axis=1)
    mask &= base[activities].notna().all(axis=1)
    return mask


def model_frame(
    base: pd.DataFrame,
    variable: str,
    *,
    model_name: str = "paper_like",
    common_mask: pd.Series | None = None,
) -> pd.DataFrame:
    exposure = any_time(base[variable])
    frame = base.assign(EXPOSURE=exposure)
    if common_mask is not None:
        frame = frame.loc[common_mask]
    frame = frame[columns_for_model(model_name)].dropna().copy()

    # Scale wealth to avoid numerical conditioning problems; this does not
    # change the exposure coefficient.
    sd = frame["WEALTH"].std()
    if sd and not math.isnan(sd):
        frame["WEALTH"] = (frame["WEALTH"] - frame["WEALTH"].mean()) / sd

    frame = pd.get_dummies(
        frame,
        columns=["RACE"],
        drop_first=True,
        dtype=float,
    )
    return frame


def fit_activity(
    frame: pd.DataFrame,
    variable: str,
    label: str,
    period: str,
    sample: str,
    model_name: str,
) -> dict:
    counts = frame["EXPOSURE"].value_counts()
    n0 = int(counts.get(0, 0))
    n1 = int(counts.get(1, 0))
    deaths = int(frame["EVENT"].sum())
    base = {
        "variable": variable,
        "label": label,
        "period": period,
        "sample": sample,
        "model": model_name,
        "n": len(frame),
        "deaths": deaths,
        "nonparticipants": n0,
        "participants": n1,
    }
    if min(n0, n1) < 100 or deaths < 100:
        return {**base, "status": "insufficient group size"}

    model = CoxPHFitter()
    model.fit(
        frame,
        duration_col="DURATION",
        event_col="EVENT",
        weights_col="WEIGHT",
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


def analyze() -> pd.DataFrame:
    registry = read_registry()
    cams, hrs = load_data()
    base = prepare_base(cams, hrs)

    rows: list[dict] = []
    for model_name in ["paper_like", "functional"]:
        common = common_sample_mask(base, registry, model_name)
        for sample in ["exposure_specific", "common"]:
            for row in registry.itertuples(index=False):
                frame = model_frame(
                    base,
                    row.variable,
                    model_name=model_name,
                    common_mask=common if sample == "common" else None,
                )
                rows.append(
                    fit_activity(
                        frame,
                        row.variable,
                        row.label,
                        row.period,
                        sample,
                        model_name,
                    )
                )

    out = pd.DataFrame(rows)
    out["q_bh"] = math.nan
    for (_, _), group in out.groupby(["model", "sample"]):
        # Preserve the full frozen 31-activity family. Sparse, non-estimable
        # contrasts count conservatively as p=1 rather than disappearing from
        # the multiple-testing denominator.
        idx = group.index
        family_p = out.loc[idx, "p"].fillna(1.0)
        out.loc[idx, "q_bh"] = bh_adjust(family_p)
    out["is_books"] = out["variable"].eq("A3_01")
    return out


def main() -> None:
    out = analyze()
    RESULTS.parent.mkdir(exist_ok=True)
    out.to_csv(RESULTS, index=False)
    cols = [
        "model",
        "sample",
        "variable",
        "label",
        "n",
        "deaths",
        "nonparticipants",
        "participants",
        "hr",
        "ci_low",
        "ci_high",
        "p",
        "q_bh",
        "is_books",
        "status",
    ]
    print(out.sort_values(["sample", "p"], na_position="last")[cols].to_string(index=False))


if __name__ == "__main__":
    main()
