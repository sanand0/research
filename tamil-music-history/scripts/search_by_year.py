#!/usr/bin/env python3
"""
Tamil Song Catalog Builder - Year-based Jukebox Search
Searches YouTube for year-specific Tamil song compilations/jukeboxes.
"""

import csv
import json
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"

OFFICIAL_CHANNELS = [
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya"
]


def check_official(channel: str) -> bool:
    return any(ch in str(channel) for ch in OFFICIAL_CHANNELS)


def search_year_jukebox(year: int) -> list[dict]:
    """Search for jukebox/compilation for a specific year."""
    query = f"Top Tamil songs {year} hit"
    print(f"  Searching: {year}")

    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
           f"ytsearch10:{query}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return []

        lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
        results = []

        for line in lines:
            try:
                data = json.loads(line.strip())
                duration = data.get('duration', 0) or 0

                # Skip very long videos (likely full compilations > 30 min)
                # but keep reasonable length jukeboxes
                if duration > 1800:  # 30 min
                    continue

                results.append(data)
            except json.JSONDecodeError:
                continue

        return results

    except Exception as e:
        print(f"  Error searching {year}: {e}")
        return []


def extract_song_from_title(title: str, year: int) -> dict:
    """Try to parse song info from title."""
    # Common patterns in Tamil song titles
    title_lower = title.lower()

    # Try to extract movie name (usually in quotes or after |)
    movie = ""
    song = title

    # Clean up common YouTube title patterns
    for sep in ['|', '-', '–', '—']:
        if sep in title:
            parts = title.split(sep)
            if len(parts) >= 2:
                # Last part is often the song name
                song = parts[-1].strip()
                # Second to last might be movie
                if len(parts) >= 3:
                    movie = parts[-2].strip()

    return {
        'song_title': song[:100],
        'movie': movie[:50],
    }


def process_year(year: int) -> list[dict]:
    """Process a single year and return song entries."""
    results = search_year_jukebox(year)
    rows = []

    for data in results:
        title = data.get('title', '')
        parsed = extract_song_from_title(title, year)

        # Determine if it's a single song or compilation
        duration = data.get('duration', 0) or 0
        is_single = 60 < duration < 400  # Between 1 and 6.5 minutes

        rows.append({
            'year': year,
            'date': f"{year}-01-01",
            'song_title': parsed['song_title'],
            'movie': parsed['movie'],
            'composer': '',
            'singer': '',
            'lyricist': '',
            'youtube_id': data.get('id', ''),
            'youtube_title': title,
            'duration': duration,
            'official': 'Y' if check_official(data.get('channel', '')) else 'N',
            'verified': 'Y',
            'downloaded': 'N',
            'download_path': '',
            'view_count': data.get('view_count', 0),
            'error': '',
            'is_single': 'Y' if is_single else 'N'
        })

    return rows


def main():
    """Build catalog by searching year by year."""
    SONGS_CSV.parent.mkdir(exist_ok=True)

    all_rows = []
    years = list(range(1950, 2027))  # 1950 to 2026

    for year in years:
        print(f"\n=== Year {year} ===")
        rows = process_year(year)
        all_rows.extend(rows)
        print(f"  Found {len(rows)} videos")

        # Save progress
        if rows:
            save_csv(all_rows)

        time.sleep(1)  # Rate limiting

    # Save final
    save_csv(all_rows)

    # Summary
    singles = sum(1 for r in all_rows if r.get('is_single') == 'Y')
    print(f"\n✓ Catalog complete: {len(all_rows)} total ({singles} single songs)")
    print(f"  CSV: {SONGS_CSV}")


def save_csv(rows):
    if not rows:
        return
    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
