#!/usr/bin/env python3
"""
Tamil Song Fetcher - Recent Decades (1990-2026)
Focused search for modern Tamil songs where YouTube metadata is reliable.
"""

import csv
import json
import subprocess
import time
from pathlib import Path
import re

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"

# Searches that work well for modern Tamil songs
SEARCH_QUERIES = [
    # Per-year specific searches
    "Tamil hit songs {year}",
    "Tamil popular songs {year}",
    "Tamil best songs {year}",
    # Genre-based
    "Tamil love song {year}",
    "Tamil melody song {year}",
    "Tamil party song {year}",
    "Tamil sad song {year}",
    # Composer-based
    "Anirudh Tamil song {year}",
    "AR Rahman Tamil song {year}",
    "Ilaiyaraaja Tamil song {year}",
    "DSP Tamil song {year}",
    "Yuvan Tamil song {year}",
    # Actor-based
    "Vijay Tamil hit song {year}",
    "Ajith Tamil hit song {year}",
    "Rajinikanth Tamil song {year}",
    "Dhanush Tamil song {year}",
    "Suriya Tamil song {year}",
]

# Additional general searches
GENERAL_QUERIES = [
    "Tamil superhit songs 1990s",
    "Tamil hit songs 2000s",
    "Tamil viral songs 2010s",
    "Tamil trending songs 2020s",
    "Tamil best love songs",
    "Tamil melody hits",
    "Tamil party hits",
]

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


def is_likely_tamil_film_song(title, year):
    """Check if title looks like a Tamil film song."""
    title_lower = title.lower()

    # Has Tamil script - likely correct
    if any('\u0b80' <= c <= '\u0fff' for c in title):
        return True

    # Official channel with Tamil-related keywords
    neg = ['hindi', 'telugu', 'malayalam', 'kannada', 'bollywood', 'bgm', 'ringtone', 'remix only']
    if not any(n in title_lower for n in neg):
        if any(k in title_lower for k in ['tamil', 'song', 'video', 'movie', 'film', 'audio', 'official']):
            return True

    return False


def parse_title(title):
    """Parse YouTube title to extract metadata."""
    title_clean = re.sub(r'[\|/\-\–\—•*]', ' ', title)
    title_clean = re.sub(r'\s+', ' ', title_clean).strip()[:80]

    parts = [p.strip() for p in re.split(r'\|', title)]
    parts = [p for p in parts if p and len(p) > 2]

    movie = ""
    for p in parts[1:4]:
        p_lower = p.lower()
        if any(x in p_lower for x in ['movie', 'film', 'video', 'song', 'ft', 'from', ' starring', 'preserved', 'official']):
            continue
        if 4 < len(p) < 50 and not re.search(r'\d{4}', p):
            movie = p
            break

    return title_clean, movie


def search_songs(query, limit=20):
    """Search YouTube and return individual songs."""
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

                # Skip jukeboxes and clips
                if duration > 900 or duration < 30:
                    continue

                songs.append(data)
            except json.JSONDecodeError:
                continue

        return songs
    except Exception as e:
        print(f"    Error: {e}")
        return []


def main():
    print("Tamil Song Fetcher - Recent Decades (1990-2026)")
    print("=" * 55)

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

    print(f"Existing verified songs: {len(existing_rows)}")
    print()

    # Years to search
    years = list(range(1990, 2027))
    all_new_songs = {}
    seen_ids = set(existing_ids)

    # Build query list
    queries = []
    for year in years:
        for q in SEARCH_QUERIES:
            queries.append((year, q.format(year=year)))
    queries.append((None, "Tamil superhit songs 1990s"))
    queries.append((None, "Tamil hit songs 2000s"))
    queries.append((None, "Tamil viral songs 2010s"))
    queries.append((None, "Tamil trending songs 2020s"))
    queries.append((None, "Tamil best love songs"))
    queries.append((None, "Tamil melody hits"))
    queries.append((None, "Tamil party hits"))

    print(f"Total queries: {len(queries)}")
    print()

    for i, (default_year, query) in enumerate(queries):
        print(f"[{i+1}/{len(queries)}] {query}...")

        songs = search_songs(query, limit=15)

        count = 0
        for song in songs:
            vid = song.get('id', '')
            if vid in seen_ids:
                continue

            title = song.get('title', '')
            channel = song.get('channel', '')
            views = song.get('view_count', 0)

            # Filter: must look like Tamil film song
            if not is_likely_tamil_film_song(title, default_year):
                continue

            # Extract year from title
            year = default_year
            year_match = re.search(r'(19[9][0-9]|20[0-2][0-9])', title)
            if year_match:
                year = int(year_match.group())

            song_title, movie = parse_title(title)

            all_new_songs[vid] = {
                'year': year,
                'date': f"{year}-01-01",
                'song_title': song_title,
                'movie': movie,
                'composer': '',
                'singer': '',
                'lyricist': '',
                'youtube_id': vid,
                'youtube_title': title,
                'duration': song.get('duration', 0),
                'official': 'Y' if is_official(channel) else 'N',
                'verified': 'N',
                'downloaded': 'N',
                'download_path': '',
                'view_count': views,
                'error': ''
            }
            seen_ids.add(vid)
            count += 1

        print(f"  +{count} new (total unique: {len(all_new_songs)})")

        if (i + 1) % 20 == 0:
            print(f"  Saving progress...")
            combined = existing_rows + list(all_new_songs.values())
            with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=combined[0].keys())
                writer.writeheader()
                writer.writerows(combined)

        time.sleep(0.25)

    # Save final
    print()
    print("=" * 55)
    combined = existing_rows + list(all_new_songs.values())

    # Sort by year desc, views desc
    for r in combined:
        if not r.get('view_count'):
            r['view_count'] = '0'
        if not r.get('year'):
            r['year'] = '2000'

    combined.sort(key=lambda x: (int(x.get('year', 0)), int(x.get('view_count', 0))), reverse=True)

    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=combined[0].keys())
        writer.writeheader()
        writer.writerows(combined)

    # Stats
    by_year = {}
    for r in combined:
        y = r.get('year', '?')
        by_year[y] = by_year.get(y, 0) + 1

    print(f"✓ Complete!")
    print(f"  Total songs: {len(combined)}")
    print(f"  Verified (original): {sum(1 for r in combined if r.get('verified') == 'Y')}")
    print(f"  New (unverified): {len(all_new_songs)}")
    print(f"  Years: {sorted(by_year.keys())[-10:]}")
    for y in sorted(by_year.keys(), reverse=True)[-15:]:
        print(f"    {y}: {by_year[y]}")


if __name__ == "__main__":
    main()
