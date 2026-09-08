#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas>=2.2"]
# ///
"""Stream Peirson et al. data and persist only pre-winter 2014 predictors."""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

import pandas as pd

URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0288953.s002&type=supplementary"
OUT = Path("candidates/honey-bee-peirson/predictors_2014_alberta.csv")
KEEP = [
    "Colony Number",
    "ColonyGroup",
    "Region",
    "Apiary",
    "Patties",
    "Fumagillin",
    "Date",
    "Inspection Date",
    "Adults",
    "Worker Cells",
]
DATES = ["May 2014", "June 2014", "August 2014"]
REGIONS = ["Southern Alberta", "Northern Alberta"]

with urllib.request.urlopen(URL, timeout=30) as response:
    raw = response.read()

df = pd.read_csv(io.BytesIO(raw), usecols=KEEP)
df = df[df["Region"].isin(REGIONS) & df["Date"].isin(DATES)].copy()
assert df[["Colony Number", "Date"]].duplicated().sum() == 0
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)

print(f"rows={len(df)} colonies={df['Colony Number'].nunique()}")
print("rows/nonmissing by region/date:")
print(
    df.groupby(["Region", "Date"], observed=True)
    .agg(rows=("Colony Number", "size"), adults=("Adults", "count"), brood=("Worker Cells", "count"))
    .to_string()
)
wide = df.pivot(index="Colony Number", columns="Date", values="Adults")
for dates in (["May 2014", "June 2014", "August 2014"], ["June 2014", "August 2014"]):
    n = int(wide.reindex(columns=dates).notna().all(axis=1).sum())
    print(f"complete adults {'+'.join(dates)}={n}")
