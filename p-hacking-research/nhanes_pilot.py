#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "lifelines>=0.30",
#   "pandas>=2.2",
# ]
# ///

"""Small NHANES 2005-06 mortality headline-factory pilot.

This intentionally freezes one cohort and one demographic adjustment model, then
changes only the focal exposure. It is a screening/demo analysis, not a full
complex-survey reproduction of any publication.
"""

from __future__ import annotations

import argparse
import math
import shutil
import urllib.request
from pathlib import Path

import pandas as pd
from lifelines import CoxPHFitter


CDC_XPT = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles"
CDC_MORT = (
    "https://ftp.cdc.gov/pub/health_statistics/NCHS/datalinkage/"
    "linked_mortality/NHANES_2005_2006_MORT_2019_PUBLIC.dat"
)
MORTALITY_FILE = "NHANES_2005_2006_MORT_2019_PUBLIC.dat"

TABLE_FILES = {
    "demo": "DEMO_D.xpt",
    "sleep": "SLQ_D.xpt",
    "activity": "PAQ_D.xpt",
    "support": "SSQ_D.xpt",
    "alcohol": "ALQ_D.xpt",
    "oral": "OHQ_D.xpt",
    "smoking": "SMQ_D.xpt",
    "health": "HSQ_D.xpt",
}

EXPOSURES = [
    {
        "id": "sleep_hours",
        "table": "sleep",
        "variable": "SLD010H",
        "label": "Hours of sleep",
        "kind": "range_sd",
        "lo": 1,
        "hi": 12,
        "unit": "per 1 SD more",
    },
    {
        "id": "walk_bike",
        "table": "activity",
        "variable": "PAD020",
        "label": "Walked/bicycled for transport",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "home_yard",
        "table": "activity",
        "variable": "PAQ100",
        "label": "Moderate home/yard work",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "vigorous_activity",
        "table": "activity",
        "variable": "PAD200",
        "label": "Vigorous activity",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "moderate_activity",
        "table": "activity",
        "variable": "PAD320",
        "label": "Moderate activity",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "strength",
        "table": "activity",
        "variable": "PAD440",
        "label": "Muscle-strengthening activity",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "tv_3plus",
        "table": "activity",
        "variable": "PAD590",
        "label": "TV/video ≥3 hours/day",
        "kind": "sets",
        "yes_values": {3, 4, 5},
        "no_values": {0, 1, 2, 6},
        "unit": "yes vs no",
    },
    {
        "id": "computer_2plus",
        "table": "activity",
        "variable": "PAD600",
        "label": "Computer ≥2 hours/day",
        "kind": "sets",
        "yes_values": {2, 3, 4, 5},
        "no_values": {0, 1, 6},
        "unit": "yes vs no",
    },
    {
        "id": "emotional_support",
        "table": "support",
        "variable": "SSQ011",
        "label": "Can count on emotional support",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "financial_support",
        "table": "support",
        "variable": "SSQ051",
        "label": "Can count on financial support",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "close_friends",
        "table": "support",
        "variable": "SSQ061",
        "label": "Number of close friends",
        "kind": "range_sd",
        "lo": 0,
        "hi": 50,
        "unit": "per 1 SD more",
    },
    {
        "id": "weekly_religion",
        "table": "support",
        "variable": "SSD044",
        "label": "Religious services ≥weekly",
        "kind": "threshold",
        "lo": 0,
        "hi": 2557,
        "threshold": 52,
        "unit": "yes vs no",
    },
    {
        "id": "alcohol_12",
        "table": "alcohol",
        "variable": "ALQ101",
        "label": "Had ≥12 alcoholic drinks in a year",
        "kind": "binary",
        "yes": 1,
        "no": 2,
        "unit": "yes vs no",
    },
    {
        "id": "good_teeth",
        "table": "oral",
        "variable": "OHQ011",
        "label": "Teeth rated good/very good/excellent",
        "kind": "sets",
        "yes_values": {11, 12, 13},
        "no_values": {14, 15},
        "unit": "yes vs fair/poor",
    },
    {
        "id": "no_mouth_ache",
        "table": "oral",
        "variable": "OHQ620",
        "label": "No mouth/tooth aching in past year",
        "kind": "sets",
        "yes_values": {5},
        "no_values": {1, 2, 3, 4},
        "unit": "never vs any",
    },
]


def local_tables(data_dir: Path | str = "data") -> dict[str, Path]:
    root = Path(data_dir)
    return {name: root / filename for name, filename in TABLE_FILES.items()}


def clean_binary(series: pd.Series, *, yes: int, no: int) -> pd.Series:
    return series.map({yes: 1.0, no: 0.0})


def clean_range(series: pd.Series, *, lo: float, hi: float) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.where(numeric.between(lo, hi))


def clean_sets(
    series: pd.Series, *, yes_values: set[int], no_values: set[int]
) -> pd.Series:
    def recode(value: float) -> float:
        if value in yes_values:
            return 1.0
        if value in no_values:
            return 0.0
        return math.nan

    return series.map(recode)


def recode_smoking(table: pd.DataFrame) -> pd.Series:
    """0=never, 1=former, 2=current; invalid responses become missing."""
    ever = table["SMQ020"]
    now = table["SMQ040"]
    result = pd.Series(math.nan, index=table.index, dtype=float)
    result[ever == 2] = 0
    result[(ever == 1) & (now == 3)] = 1
    result[(ever == 1) & now.isin([1, 2])] = 2
    return result


def bh_adjust(pvalues: pd.Series) -> list[float]:
    """Benjamini-Hochberg adjusted p-values, preserving input order."""
    p = pd.Series(pvalues, dtype=float)
    order = p.sort_values().index
    ranked = p.loc[order]
    m = len(ranked)
    adjusted = ranked * m / pd.Series(range(1, m + 1), index=order)
    adjusted = adjusted.iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return adjusted.reindex(p.index).tolist()


def prepare_exposure(series: pd.Series, spec: dict) -> pd.Series:
    kind = spec["kind"]
    if kind == "binary":
        return clean_binary(series, yes=spec["yes"], no=spec["no"])
    if kind == "sets":
        return clean_sets(
            series,
            yes_values=spec["yes_values"],
            no_values=spec["no_values"],
        )
    if kind == "threshold":
        value = clean_range(series, lo=spec["lo"], hi=spec["hi"])
        return (value >= spec["threshold"]).astype(float).where(value.notna())
    if kind == "range_sd":
        value = clean_range(series, lo=spec["lo"], hi=spec["hi"])
        sd = value.std()
        return (value - value.mean()) / sd if sd and not math.isnan(sd) else value * math.nan
    raise ValueError(f"Unknown exposure kind: {kind}")


def parse_int(text: str) -> int | None:
    value = text.strip()
    return None if not value or value == "." else int(value)


def parse_mortality_line(line: str) -> dict:
    """Parse official 2019 public-use NHANES LMF fixed-width positions."""
    return {
        "SEQN": parse_int(line[0:6]),
        "ELIGSTAT": parse_int(line[14:15]),
        "MORTSTAT": parse_int(line[15:16]),
        "UCOD_LEADING": line[16:19].strip() or None,
        "DIABETES": parse_int(line[19:20]),
        "HYPERTEN": parse_int(line[20:21]),
        "PERMTH_INT": parse_int(line[42:45]),
        "PERMTH_EXM": parse_int(line[45:48]),
    }


def read_mortality(path: Path) -> pd.DataFrame:
    with path.open(encoding="ascii") as handle:
        rows = [parse_mortality_line(line) for line in handle if line.strip()]
    return pd.DataFrame(rows)


def download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as response, path.open("wb") as output:
        shutil.copyfileobj(response, output)


def download_sources(data_dir: Path, *, skip_mortality: bool = False) -> None:
    for filename in TABLE_FILES.values():
        path = data_dir / filename
        print(f"download {filename}", flush=True)
        download(f"{CDC_XPT}/{filename}", path)
    if not skip_mortality:
        print(f"download {MORTALITY_FILE}", flush=True)
        try:
            download(CDC_MORT, data_dir / MORTALITY_FILE)
        except Exception as exc:
            raise RuntimeError(
                "CDC's ftp.cdc.gov mortality endpoint could not be reached. "
                f"Download {CDC_MORT} manually into {data_dir / MORTALITY_FILE} "
                "and rerun. Questionnaire files are already usable."
            ) from exc


def read_xpt(path: Path) -> pd.DataFrame:
    return pd.read_sas(path, format="xport", encoding="latin1")


def inventory(data_dir: Path) -> pd.DataFrame:
    tables = {
        name: read_xpt(path)
        for name, path in local_tables(data_dir).items()
        if path.exists()
    }
    rows = []
    for spec in EXPOSURES:
        table = tables.get(spec["table"])
        if table is None:
            rows.append({**spec, "n_valid": 0, "status": "missing table"})
            continue
        exposure = prepare_exposure(table[spec["variable"]], spec)
        rows.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "table": spec["table"],
                "variable": spec["variable"],
                "unit": spec["unit"],
                "n_valid": int(exposure.notna().sum()),
                "status": "ok",
            }
        )
    return pd.DataFrame(rows)


def clean_demo(demo: pd.DataFrame) -> pd.DataFrame:
    out = demo[
        [
            "SEQN",
            "RIDAGEYR",
            "RIAGENDR",
            "RIDRETH1",
            "DMDEDUC2",
            "INDFMPIR",
            "DMDMARTL",
            "WTINT2YR",
            "WTMEC2YR",
            "SDMVPSU",
            "SDMVSTRA",
        ]
    ].copy()
    out = out[out["RIDAGEYR"] >= 40]
    out["DMDEDUC2"] = out["DMDEDUC2"].where(out["DMDEDUC2"].between(1, 5))
    out["DMDMARTL"] = out["DMDMARTL"].where(out["DMDMARTL"].between(1, 6))
    out["RIDRETH1"] = out["RIDRETH1"].where(out["RIDRETH1"].between(1, 5))
    out["RIAGENDR"] = out["RIAGENDR"].where(out["RIAGENDR"].between(1, 2))
    out["cluster"] = out["SDMVSTRA"] * 10 + out["SDMVPSU"]
    return out


def model_frame(
    demo: pd.DataFrame,
    mortality: pd.DataFrame,
    exposure_table: pd.DataFrame,
    spec: dict,
    *,
    adjustment: str,
    smoking: pd.DataFrame,
    health: pd.DataFrame,
) -> pd.DataFrame:
    exposure = exposure_table[["SEQN", spec["variable"]]].copy()
    exposure["EXPOSURE"] = prepare_exposure(exposure[spec["variable"]], spec)
    merged = (
        clean_demo(demo)
        .merge(mortality, on="SEQN", how="inner")
        .merge(exposure[["SEQN", "EXPOSURE"]], on="SEQN", how="inner")
    )

    columns = [
        "PERMTH_INT",
        "MORTSTAT",
        "cluster",
        "EXPOSURE",
        "RIDAGEYR",
        "INDFMPIR",
        "RIAGENDR",
        "RIDRETH1",
        "DMDEDUC2",
        "DMDMARTL",
    ]
    categorical = ["RIAGENDR", "RIDRETH1", "DMDEDUC2", "DMDMARTL"]
    weight = "WTINT2YR"

    common_health_sample = adjustment in {
        "health_sample_demographic",
        "health_sample_smoking",
        "health",
    }
    smoke = smoking[["SEQN", "SMQ020", "SMQ040"]].copy()
    smoke["SMOKING"] = recode_smoking(smoke)

    if common_health_sample:
        health_status = health[["SEQN", "HSD010"]].copy()
        health_status["HSD010"] = health_status["HSD010"].where(
            health_status["HSD010"].between(1, 5)
        )
        merged = (
            merged.merge(smoke[["SEQN", "SMOKING"]], on="SEQN", how="left")
            .merge(health_status, on="SEQN", how="left")
        )
        merged = merged[merged["SMOKING"].notna() & merged["HSD010"].notna()]
        weight = "WTMEC2YR"
    elif adjustment == "smoking":
        merged = merged.merge(smoke[["SEQN", "SMOKING"]], on="SEQN", how="left")

    if adjustment in {"smoking", "health_sample_smoking", "health"}:
        columns.append("SMOKING")
        categorical.append("SMOKING")

    if adjustment == "health":
        columns.append("HSD010")
        categorical.append("HSD010")

    merged = merged[
        (merged["ELIGSTAT"] == 1)
        & merged["MORTSTAT"].isin([0, 1])
        & merged["PERMTH_INT"].gt(0)
        & merged[weight].gt(0)
    ]
    merged["WEIGHT"] = merged[weight]
    columns.insert(2, "WEIGHT")
    frame = merged[columns].dropna().copy()
    return pd.get_dummies(frame, columns=categorical, drop_first=True, dtype=float)


def fit_exposure(frame: pd.DataFrame, spec: dict, adjustment: str) -> dict:
    if len(frame) < 100 or frame["MORTSTAT"].sum() < 20:
        return {
            "adjustment": adjustment,
            "id": spec["id"],
            "label": spec["label"],
            "unit": spec["unit"],
            "n": len(frame),
            "deaths": int(frame["MORTSTAT"].sum()),
            "status": "too few observations/events",
        }
    model = CoxPHFitter()
    model.fit(
        frame,
        duration_col="PERMTH_INT",
        event_col="MORTSTAT",
        weights_col="WEIGHT",
        cluster_col="cluster",
        robust=True,
    )
    row = model.summary.loc["EXPOSURE"]
    return {
        "adjustment": adjustment,
        "id": spec["id"],
        "label": spec["label"],
        "unit": spec["unit"],
        "n": len(frame),
        "deaths": int(frame["MORTSTAT"].sum()),
        "hr": float(math.exp(row["coef"])),
        "ci_low": float(math.exp(row["coef lower 95%"])),
        "ci_high": float(math.exp(row["coef upper 95%"])),
        "p": float(row["p"]),
        "status": "ok",
    }


def analyze(data_dir: Path, adjustments: list[str]) -> pd.DataFrame:
    paths = local_tables(data_dir)
    missing = [str(path) for path in paths.values() if not path.exists()]
    mortality_path = data_dir / MORTALITY_FILE
    if not mortality_path.exists():
        missing.append(str(mortality_path))
    if missing:
        raise FileNotFoundError("Missing required data: " + ", ".join(missing))

    tables = {name: read_xpt(path) for name, path in paths.items()}
    mortality = read_mortality(mortality_path)
    results = []
    for adjustment in adjustments:
        for spec in EXPOSURES:
            frame = model_frame(
                tables["demo"],
                mortality,
                tables[spec["table"]],
                spec,
                adjustment=adjustment,
                smoking=tables["smoking"],
                health=tables["health"],
            )
            results.append(fit_exposure(frame, spec, adjustment))

    output = pd.DataFrame(results)
    output["q_bh"] = math.nan
    for adjustment, rows in output.groupby("adjustment"):
        valid = rows["p"].notna()
        index = rows.index[valid]
        output.loc[index, "q_bh"] = bh_adjust(output.loc[index, "p"])
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["download", "inventory", "analyze"],
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--skip-mortality", action="store_true")
    parser.add_argument(
        "--adjustment",
        choices=[
            "demographic",
            "smoking",
            "health_sample_demographic",
            "health_sample_smoking",
            "health",
            "all",
        ],
        default="all",
        help="Covariate set for analyze; all runs primary and same-sample sensitivities.",
    )
    args = parser.parse_args()

    if args.command == "download":
        download_sources(args.data_dir, skip_mortality=args.skip_mortality)
        return
    if args.command == "inventory":
        print(inventory(args.data_dir).to_csv(index=False))
        return

    adjustments = (
        [
            "demographic",
            "smoking",
            "health_sample_demographic",
            "health_sample_smoking",
            "health",
        ]
        if args.adjustment == "all"
        else [args.adjustment]
    )
    results = analyze(args.data_dir, adjustments)
    out = Path("results")
    out.mkdir(exist_ok=True)
    results.to_csv(out / "nhanes_2005_2006_headline_factory.csv", index=False)
    print(
        results.sort_values(["adjustment", "p"], na_position="last").to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
