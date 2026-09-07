#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Validate checked-in derived values against downloaded source artifacts."""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def pdf_text(path: Path) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


data = json.loads((ROOT / "data" / "app-data.json").read_text())
latest = pdf_text(RAW / "rail-reliability-2025-08-to-2026-07.pdf")
historical = pdf_text(RAW / "rail-reliability-historical-2020-2025.pdf")
ridership = json.loads((RAW / "ridership-annual.json").read_text())
ridership_rows = {row["DataSeries"]: row for row in ridership["result"]["records"]}

checks = {
    "latest punctuality row": re.search(r"99\.10%\s+99\.32%\s+99\.29%", latest) is not None,
    "latest network MKBF": "2,370,000" in latest,
    "historical network punctuality": re.search(r"99\.40%\s+99\.65%\s+99\.53%\s+99\.59%\s+99\.35%\s+99\.38%", historical) is not None,
    "historical severe delays": re.search(r"6\s+3\s+7\s+5\s+7\s+7", historical) is not None,
    "ridership API success": ridership.get("success") is True,
    "2025 MRT ridership": ridership_rows["Average Daily Ridership - MRT"]["2025"] == "3490",
    "2025 LRT ridership": ridership_rows["Average Daily Ridership - LRT"]["2025"] == "209",
    "2025 rail length": ridership_rows["Rail Length"]["2025"] == "271.3",
    "app headline": data["latest"]["punctuality"]["MRT"][-1] == 99.29,
}

failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("Source validation failed: " + ", ".join(failed))
print(f"Validated {len(checks)} source and transcription checks.")
