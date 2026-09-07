#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Resumable downloader for official source files for Platform Promise.

Non-empty files are skipped. New files are streamed to a .part sibling and
atomically renamed only after a successful HTTP 200 response, so interruption
is safe to retry. Use --force when deliberately refreshing a snapshot.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
HEADERS = {
    "User-Agent": "PlatformPromise/1.0 (Singapore train reliability research)",
    "Referer": "https://datamall.lta.gov.sg/content/datamall/en/search_datasets.html",
}
SOURCES = (
    ("rail-reliability-2025-08-to-2026-07.pdf", "https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/Rail_Service_Reliability_Performance_Aug_2025_to_Jul_2026.pdf"),
    ("rail-reliability-historical-2020-2025.pdf", "https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/Annex%E2%80%93Historical_Rail_Service_Reliability_Performance.pdf"),
    ("ridership-annual.json", "https://data.gov.sg/api/action/datastore_search?resource_id=d_ba615ec4cc5d9f5b7800ad82057f36f1&limit=100"),
    ("gtfs-schedule-descriptor.zip", "https://datamall.lta.gov.sg/content/dam/datamall/datasets/PublicTransportRelated/GTFSScheduleTrain.zip"),
)


def download_if_missing(filename: str, url: str, force: bool) -> bool:
    destination = RAW / filename
    if destination.exists() and destination.stat().st_size > 0 and not force:
        print(f"skip {destination.relative_to(ROOT)} (already present)")
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    partial.unlink(missing_ok=True)
    print(f"download {url}")
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=120) as response, partial.open("wb") as output:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} while downloading {url}")
        shutil.copyfileobj(response, output)
    if partial.stat().st_size == 0:
        partial.unlink()
        raise RuntimeError(f"empty response from {url}")
    os.replace(partial, destination)
    print(f"saved {destination.relative_to(ROOT)} ({destination.stat().st_size:,} bytes)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="redownload every source")
    parser.add_argument("--skip-validation", action="store_true", help="do not run the source/analysis checks")
    args = parser.parse_args()
    for filename, url in SOURCES:
        download_if_missing(filename, url, args.force)
    if not args.skip_validation:
        subprocess.run(["uv", "run", "scripts/validate_sources.py"], cwd=ROOT, check=True)
    print("download pipeline complete; data/app-data.json remains the checked-in browser-ready analysis")


if __name__ == "__main__":
    main()
