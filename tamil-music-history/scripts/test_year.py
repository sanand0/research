#!/usr/bin/env python3
"""Test year-based search for a few years."""

import json
import subprocess
import time
from pathlib import Path

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")

OFFICIAL_CHANNELS = [
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya"
]


def check_official(channel):
    return any(ch in str(channel) for ch in OFFICIAL_CHANNELS)


def search_year(year):
    query = f"Top Tamil songs {year} hit"
    print(f"\n=== Year {year} ===")

    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
           f"ytsearch10:{query}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            print(f"  Found {len(lines)} results")

            for line in lines:
                try:
                    data = json.loads(line.strip())
                    title = data.get('title', '')[:70]
                    channel = data.get('channel', '')
                    duration = data.get('duration', 0) or 0
                    views = data.get('view_count', 0) or 0
                    vid = data.get('id', '')
                    official = 'Y' if check_official(channel) else 'N'

                    print(f"  [{duration:4.0f}s] {'✓' if official == 'Y' else ' '} {views:>12,} | {title}")
                    print(f"             | {channel} | {vid}")
                except json.JSONDecodeError:
                    continue
        else:
            print(f"  Error: {result.stderr}")

    except Exception as e:
        print(f"  Exception: {e}")

    time.sleep(0.5)


# Test with a few key years
for year in [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2015, 2020, 2025]:
    search_year(year)
