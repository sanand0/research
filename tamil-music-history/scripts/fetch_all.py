#!/usr/bin/env python3
"""
Comprehensive Tamil Song Fetcher
Searches YouTube for popular Tamil songs across all years (1950-2026).
Targets 20-50 songs per year.
"""

import csv
import json
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import re

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
PROGRESS_FILE = BASE_DIR / ".fetch_progress.json"

OFFICIAL_CHANNELS = [
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya", "Old Tamil Songs", "Old",
    "Maestro", "Isaignani", "Sony Music", "Audio", "Video"
]


def check_official(channel: str) -> bool:
    if not channel:
        return False
    channel_lower = channel.lower()
    return any(ch.lower() in channel_lower for ch in OFFICIAL_CHANNELS)


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'processed_years': [], 'songs': []}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def search_query(query: str, max_results: int = 50) -> list:
    """Search YouTube and return individual songs (not jukeboxes)."""
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
           f"ytsearch{max_results}:{query}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return []

        lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
        songs = []

        for line in lines:
            try:
                data = json.loads(line.strip())
                duration = data.get('duration') or 0
                title = data.get('title', '').lower()
                video_id = data.get('id', '')

                # Skip very long videos (jukeboxes > 15 min = 900s)
                if duration > 900:
                    continue

                # Skip non-Tamil indicators (but be lenient)
                non_tamil = ['hindi', 'telugu', 'malayalam', 'kannada', 'bollywood']
                skip = False
                for nt in non_tamil:
                    if nt in title and 'tamil' not in title:
                        skip = True
                        break
                if skip:
                    continue

                # Prefer individual songs (1-8 min) or accept reasonable length
                if 30 < duration < 600:  # 30 sec to 10 min
                    songs.append(data)
                elif duration <= 30 and len(songs) < 5:  # Short clips, only if we need more
                    songs.append(data)

            except (json.JSONDecodeError, KeyError):
                continue

        return songs

    except Exception as e:
        print(f"    Search error: {e}")
        return []


def search_year_queries(year: int) -> list:
    """Search multiple queries for a given year to maximize coverage."""
    queries = [
        f"top tamil songs {year}",
        f"tamil hit songs {year}",
        f"tamil popular songs {year}",
        f"tamil romantic songs {year}",
        f"tamil melody songs {year}",
        f"tamil devotional songs {year}",
        f"tamil sad songs {year}",
        f"tamil party songs {year}",
        f"tamil love song {year}",
        f"tamil bgm {year}",
    ]

    all_songs = {}
    seen_ids = set()

    print(f"  Searching {year} with {len(queries)} query types...")

    for query in queries:
        songs = search_query(query, max_results=20)
        for song in songs:
            vid = song.get('id', '')
            if vid and vid not in seen_ids:
                seen_ids.add(vid)
                all_songs[vid] = song
        time.sleep(0.3)  # Rate limiting

    return list(all_songs.values())


def parse_title_to_metadata(title: str, year: int) -> dict:
    """Try to extract song/movie info from YouTube title."""
    title_clean = re.sub(r'[\|/\-\–\—]', ' ', title)
    title_clean = re.sub(r'\s+', ' ', title_clean).strip()

    # Common patterns: "Song Name | Movie Name | Singer | Music"
    parts = [p.strip() for p in title_clean.split('|')]
    parts = [p for p in parts if p]

    song_title = title_clean[:80]
    movie = ""
    singer = ""
    composer = ""

    if len(parts) >= 2:
        # Try to identify movie (usually second part, often has year or director)
        for i, p in enumerate(parts[1:], 1):
            p_lower = p.lower()
            if any(x in p_lower for x in ['movie', 'film', 'video', 'song', 'ft', 'from']):
                continue
            if len(p) > 3 and len(p) < 60:
                movie = p
                if i > 0 and len(parts) > i + 1:
                    singer = parts[i + 1][:50] if len(parts) > i + 1 else ""
                break

    return {
        'song_title': song_title,
        'movie': movie,
        'composer': composer,
        'singer': singer,
    }


def process_year(year: int, existing_ids: set) -> list:
    """Process a single year and return unique songs not already in catalog."""
    songs = search_year_queries(year)

    rows = []
    for song in songs:
        vid = song.get('id', '')
        if vid in existing_ids:
            continue

        metadata = parse_title_to_metadata(song.get('title', ''), year)
        channel = song.get('channel', '')

        rows.append({
            'year': year,
            'date': f"{year}-01-01",
            'song_title': metadata['song_title'],
            'movie': metadata['movie'],
            'composer': metadata['composer'],
            'singer': metadata['singer'],
            'lyricist': '',
            'youtube_id': vid,
            'youtube_title': song.get('title', ''),
            'duration': song.get('duration', 0),
            'official': 'Y' if check_official(channel) else 'N',
            'verified': 'N',  # Needs manual verification
            'downloaded': 'N',
            'download_path': '',
            'view_count': song.get('view_count', 0),
            'error': ''
        })

    return rows


def load_existing_csv():
    """Load existing song IDs from CSV."""
    existing_ids = set()
    existing_songs = []

    if SONGS_CSV.exists():
        with open(SONGS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row.get('youtube_id', '')
                if vid:
                    existing_ids.add(vid)
                existing_songs.append(row)

    return existing_ids, existing_songs


def save_csv(rows):
    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("Tamil Song Catalog Fetcher")
    print("=" * 50)

    # Load existing data
    existing_ids, existing_songs = load_existing_csv()
    progress = load_progress()

    print(f"Existing songs in CSV: {len(existing_songs)}")
    print(f"Already processed years: {len(progress['processed_years'])}")

    # Years to process
    all_years = list(range(1950, 2027))
    years_to_process = [y for y in all_years if y not in progress['processed_years']]

    print(f"Years to process: {len(years_to_process)} ({min(years_to_process)}-{max(years_to_process) if years_to_process else 'N/A'})")
    print()

    total_new_songs = 0

    for i, year in enumerate(years_to_process):
        print(f"[{i + 1}/{len(years_to_process)}] Processing year {year}...")

        new_rows = process_year(year, existing_ids)

        # Add new songs to existing
        existing_songs.extend(new_rows)
        existing_ids.update(r['youtube_id'] for r in new_rows)

        # Mark year as processed
        progress['processed_years'].append(year)
        progress['songs'] = existing_songs

        # Save progress
        save_progress(progress)
        save_csv(existing_songs)

        print(f"  Found {len(new_rows)} new songs (total: {len(existing_songs)})")

        total_new_songs += len(new_rows)

        # Brief pause between years
        time.sleep(0.5)

    print()
    print("=" * 50)
    print(f"✓ Complete! Total songs: {len(existing_songs)}")
    print(f"  New songs found: {total_new_songs}")
    print(f"  CSV: {SONGS_CSV}")


if __name__ == "__main__":
    main()
