#!/usr/bin/env python3
"""
Tamil Song Fetcher - Recent Decades (1990-2026)
Simple append-based approach.
"""

import csv
import json
import subprocess
import time
from pathlib import Path
import re

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
FIELDNAMES = ['year', 'date', 'song_title', 'movie', 'composer', 'singer', 'lyricist',
              'youtube_id', 'youtube_title', 'duration', 'official', 'verified',
              'downloaded', 'download_path', 'view_count', 'error']

OFFICIAL_CHANNELS = {
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya", "Old Tamil Songs",
    "Maestro", "Isaignani", "Sony Music India", "Sony Music South",
}


def is_official(channel):
    if not channel:
        return False
    c = channel.lower()
    return any(oc.lower() in c for oc in OFFICIAL_CHANNELS)


def is_tamil_song(title):
    title_lower = title.lower()
    # Has Tamil script
    if any('\u0b80' <= c <= '\u0fff' for c in title):
        return True
    # Looks like Tamil film song
    neg = ['hindi', 'telugu', 'malayalam', 'kannada', 'bollywood', 'bgm', 'ringtone', 'remix only']
    if not any(n in title_lower for n in neg):
        if any(k in title_lower for k in ['tamil', 'song', 'video', 'movie', 'film', 'audio', 'official']):
            return True
    return False


def parse_title(title):
    title_clean = re.sub(r'[\|/\-\–\—•*]', ' ', title)
    title_clean = re.sub(r'\s+', ' ', title_clean).strip()[:80]
    return title_clean


def search_songs(query, limit=15):
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
           f"ytsearch{limit}:{query}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return []
        songs = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line.strip())
                duration = data.get('duration') or 0
                if 30 < duration < 900:
                    songs.append(data)
            except json.JSONDecodeError:
                continue
        return songs
    except:
        return []


def main():
    print("Tamil Song Fetcher - Recent Decades")
    print("=" * 50)

    # Load existing IDs
    existing_ids = set()
    if SONGS_CSV.exists():
        with open(SONGS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('youtube_id'):
                    existing_ids.add(row['youtube_id'])

    print(f"Existing songs: {len(existing_ids)}")

    # Build queries for 1990-2026
    queries = []
    for year in range(1990, 2027):
        queries.append((year, f"Tamil hit songs {year}"))
        queries.append((year, f"Tamil popular songs {year}"))
    queries.append((None, "Tamil hit songs 1990s"))
    queries.append((None, "Tamil hit songs 2000s"))
    queries.append((None, "Tamil viral songs 2010s"))
    queries.append((None, "Tamil trending songs 2020s"))
    queries.append((None, "Tamil love song"))
    queries.append((None, "Tamil melody song"))
    queries.append((None, "Anirudh Tamil hits"))
    queries.append((None, "AR Rahman Tamil hits"))
    queries.append((None, "Vijay Tamil hit songs"))
    queries.append((None, "Rajinikanth Tamil hit songs"))
    queries.append((None, "Dhanush Tamil hit songs"))

    print(f"Queries: {len(queries)}")
    print()

    new_songs = []
    seen = set(existing_ids)

    for i, (default_year, query) in enumerate(queries):
        if (i + 1) % 30 == 0:
            print(f"[{i+1}/{len(queries)}] {query}... (found {len(new_songs)} so far)")

        songs = search_songs(query, limit=15)

        for song in songs:
            vid = song.get('id', '')
            if vid in seen:
                continue

            title = song.get('title', '')
            if not is_tamil_song(title):
                continue

            # Extract year
            year = default_year
            m = re.search(r'(19[9][0-9]|20[0-2][0-9])', title)
            if m:
                year = int(m.group())

            new_songs.append({
                'year': year,
                'date': f"{year}-01-01",
                'song_title': parse_title(title),
                'movie': '',
                'composer': '',
                'singer': '',
                'lyricist': '',
                'youtube_id': vid,
                'youtube_title': title,
                'duration': song.get('duration', 0),
                'official': 'Y' if is_official(song.get('channel', '')) else 'N',
                'verified': 'N',
                'downloaded': 'N',
                'download_path': '',
                'view_count': song.get('view_count', 0) or 0,
                'error': ''
            })
            seen.add(vid)

        time.sleep(0.2)

        # Save every 50 queries
        if (i + 1) % 50 == 0:
            # Append new songs to CSV
            with open(SONGS_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writerows(new_songs)
            print(f"  Saved {len(new_songs)} new songs")
            new_songs = []

    # Save remaining
    if new_songs:
        with open(SONGS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerows(new_songs)

    print()
    print("=" * 50)

    # Stats
    total = 0
    by_year = {}
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            y = row.get('year', '?')
            by_year[y] = by_year.get(y, 0) + 1

    print(f"✓ Total songs: {total}")
    print(f"Years covered: {len(by_year)}")
    for y in sorted(by_year.keys(), reverse=True)[:15]:
        print(f"  {y}: {by_year[y]}")


if __name__ == "__main__":
    main()
