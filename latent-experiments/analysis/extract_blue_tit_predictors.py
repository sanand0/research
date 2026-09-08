#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Stream the Silwood blue-tit source and persist predictor columns only.

The Figshare source also contains reproductive outcomes. This extractor never writes those
fields to disk, preserving the outcome seal for H003 candidate screening.
"""

import csv
import io
import urllib.request
from pathlib import Path

URL = "https://ndownloader.figshare.com/files/22454786"
OUT = Path("candidates/blue-tit-silwood/btoak_predictors.csv")
FIELDS = ["year", "nest.box", "female", "f.age", "LD", "BD", "mc.LD", "mc.BD"]

with urllib.request.urlopen(URL, timeout=30) as response:
    text = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(text)
    missing = set(FIELDS) - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Missing expected predictor columns: {sorted(missing)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        count = 0
        for row in reader:
            writer.writerow({field: row[field] for field in FIELDS})
            count += 1

print(f"wrote {count} predictor-only rows to {OUT}")
