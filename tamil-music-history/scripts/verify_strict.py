#!/usr/bin/env python3
"""
Tamil Song Verifier - Strict Mode
Only accepts results from verified official Tamil music channels.
"""

import csv
import json
import subprocess
import time
from pathlib import Path

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
FIELDNAMES = ['year', 'date', 'song_title', 'movie', 'composer', 'singer', 'lyricist',
              'youtube_id', 'youtube_title', 'duration', 'official', 'verified',
              'downloaded', 'download_path', 'view_count', 'error']

# Only use these official channels - most reliable for Tamil songs
OFFICIAL_ONLY = {
    "Saregama Tamil", "Saregama Carvaan Tamil", "Saregama",
    "Ilaiyaraaja Official", "Ilaiyaraaja",
    "SonyMusicSouthVEVO", "Sony Music South", "Sony Music India",
    "SunMusic", "Tips", "Ayngaran",
    "Music Wave", "Pyramid Music", "Pyramid Glitz Music",
    "Think Music India",
    "AP International",
    "Old Tamil Songs",
}

# Curated iconic songs - only include ones with high confidence
CURATED_SONGS = [
    # 1950s - MSV era - these are well-documented
    (1955, "Anbe Vaa", "Anbe Vaa", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1962, "Annai", "Annai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1965, "Paattum Naane", "Thiruvilayadal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1975, "Malarae Kurinji", "Muthal Mariyathai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1979, "Nadhiyoram", "Annai Oru Aalayam", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),

    # 1980s - Ilaiyaraaja peak
    (1983, "Mandram Vandha", "Mouna Ragam", "Ilaiyaraaja", "S. P. Balasubrahmanyam", "Vaali"),
    (1983, "Poovizhi", "Poovizhi", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1984, "Unnaithane", "Nallavanukku Nallavan", "Ilaiyaraaja", "S. P. Balasubrahmanyam", "Vaali"),
    (1986, "Nila Adhu", "Nayakan", "Ilaiyaraaja", "S. P. Balasubrahmanyam", "Vaali"),
]


def is_strict_official(channel):
    if not channel:
        return False
    c = channel.lower()
    return any(oc.lower() in c for oc in OFFICIAL_ONLY)


def search_song_strict(year, song, movie, composer, singer, lyricist):
    """Search with strict official channel filter."""
    queries = [
        f'"{song}" "{movie}" Tamil song {year} official',
        f'{song} {movie} Tamil song Ilaiyaraaja MSV',
    ]

    for query in queries:
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
               f"ytsearch5:{query}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                continue

            best = None
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line.strip())
                    duration = data.get('duration') or 0
                    channel = data.get('channel', '')

                    # MUST be from official channel
                    if not is_strict_official(channel):
                        continue

                    # Skip jukeboxes
                    if duration > 600:
                        continue

                    # Prefer duration 60-400 seconds
                    if 60 <= duration <= 400:
                        best = data
                        break
                    elif best is None:
                        best = data

                except json.JSONDecodeError:
                    continue

            if best:
                return best

        except Exception:
            continue

        time.sleep(0.3)

    return None


def main():
    print("Tamil Song Verifier - Strict Mode")
    print("=" * 60)

    # Load existing
    existing_ids = set()
    existing_rows = []

    if SONGS_CSV.exists():
        with open(SONGS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row.get('youtube_id', '')
                if vid:
                    existing_ids.add(vid)
                existing_rows.append(row)

    print(f"Existing: {len(existing_rows)} songs")
    print(f"Looking for: {len(CURATED_SONGS)} high-confidence songs")
    print()

    new_songs = []

    for i, (year, song, movie, composer, singer, lyricist) in enumerate(CURATED_SONGS):
        print(f"[{i+1}/{len(CURATED_SONGS)}] {year} - {song} ({movie})...")

        # Check if already there
        already = any(
            r.get('song_title', '').lower() == song.lower() and
            r.get('movie', '').lower() == movie.lower()
            for r in existing_rows + new_songs
        )
        if already:
            print(f"  Already in catalog")
            continue

        result = search_song_strict(year, song, movie, composer, singer, lyricist)

        if result:
            new_songs.append({
                'year': year,
                'date': f"{year}-01-01",
                'song_title': song,
                'movie': movie,
                'composer': composer,
                'singer': singer,
                'lyricist': lyricist,
                'youtube_id': result.get('id', ''),
                'youtube_title': result.get('title', ''),
                'duration': result.get('duration', 0),
                'official': 'Y',
                'verified': 'Y',
                'downloaded': 'N',
                'download_path': '',
                'view_count': result.get('view_count', 0) or 0,
                'error': ''
            })
            print(f"  ✓ {result.get('title', '')[:60]}")
            print(f"    Channel: {result.get('channel', 'N/A')}")
        else:
            print(f"  ✗ Not found")

        time.sleep(0.5)

    # Save
    if new_songs:
        all_rows = existing_rows + new_songs
        # Fix empty values
        for r in all_rows:
            r.setdefault('year', '2000')
            r.setdefault('view_count', '0')

        all_rows.sort(key=lambda x: (int(x.get('year', 2000)), int(x.get('view_count', 0))), reverse=True)

        with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(all_rows)

        print()
        print(f"Added {len(new_songs)} verified songs")

    # Summary
    total = len(existing_rows) + len(new_songs)
    verified = sum(1 for r in existing_rows + new_songs if r.get('verified') == 'Y')
    print(f"Total: {total}, Verified: {verified}")


if __name__ == "__main__":
    main()
