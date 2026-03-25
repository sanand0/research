#!/usr/bin/env python3
"""
Tamil Song Fetcher v2 - Targeted Search
Searches for songs from official channels and curated sources.
"""

import csv
import json
import subprocess
import time
from pathlib import Path
import re

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"

# Known working search patterns that return accurate Tamil film songs
SEARCH_QUERIES = {
    # Decade-based searches for older songs (these channels have good metadata)
    1950: ["tamil classic songs 1950s msviswanathan", "tamil old songs msv hits", "kannadasan tamil songs 1950"],
    1960: ["tamil 1960s hit songs ilaiyaraaja", "tamil romantic songs 1960", "msv songs 1960s tamil"],
    1970: ["tamil 1970s hit songs ilaiyaraaja", "ilaiyaraaja tamil hits 1970", "tamil melody songs 1970s"],
    1980: ["tamil 1980s hit songs ilaiyaraaja", "ilaiyaraaja hits tamil 1980", "tamil love songs 1980s"],
    1990: ["tamil 1990s hit songsarr", "tamil 1990s romance", "ar rahman tamil hits 1990"],
    2000: ["tamil 2000s hit songs", "ar rahman tamil songs 2000", "tamil love songs 2000s"],
    2010: ["tamil 2010s hit songs anirudh", "anirudh tamil hits", "tamil viral songs 2010s"],
    2020: ["tamil 2020s hit songs", "anirudh tamil 2020", "tamil trending songs 2020"],
}

# Additional specific searches for variety
ADDITIONAL_QUERIES = [
    "Tamil Superhits Peppy Songs",
    "Tamil melody hit songs",
    "Tamil romantic love songs",
    "Tamil Sad Songs emotional",
    "Tamil party dance hits",
    "Ilaiyaraaja Tamil hits",
    "AR Rahman Tamil songs",
    "Anirudh Tamil hits",
    "Vijay Tamil hit songs",
    "Rajinikanth Tamil hit songs",
    "Dhanush Tamil hit songs",
    "SURYA Tamil hit songs",
    "Ajith Tamil hit songs",
]


OFFICIAL_CHANNELS = {
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya", "Old Tamil Songs",
    "Maestro", "Isaignani", "Sony Music India", "Audio", "Video",
    "Hindi",  # For Tamil dubbed songs
}


def is_official(channel):
    if not channel:
        return False
    c = channel.lower()
    return any(oc.lower() in c for oc in OFFICIAL_CHANNELS)


def search_songs(query, limit=30):
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

                # Skip jukeboxes (long videos)
                if duration > 900:  # > 15 min
                    continue
                # Skip very short clips
                if duration < 30:
                    continue

                songs.append(data)
            except json.JSONDecodeError:
                continue

        return songs
    except Exception as e:
        print(f"    Error: {e}")
        return []


def extract_year_from_title(title, default_year=None):
    """Try to extract year from title, or use default."""
    title_lower = title.lower()

    # Look for year patterns
    year_match = re.search(r'19[5-9]\d|20[0-2]\d', title)
    if year_match:
        try:
            return int(year_match.group())
        except:
            pass

    return default_year


def is_likely_tamil_film_song(title):
    """Check if title looks like a Tamil film song."""
    title_lower = title.lower()

    # Positive indicators (Tamil film song characteristics)
    tamil_indicators = [
        'tamil', 'song', 'video', 'hd', '4k', 'official',
        'movie', 'film', 'audio', 'music', 'lyric',
        '唱', 'த', 'ப', 'ம', 'ந', 'சி',  # Tamil script
    ]

    # Negative indicators (not Tamil film)
    negative = [
        'hindi', 'bollywood', 'telugu', 'malayalam', 'kannada',
        'bgm', 'ringtone', 'remix', 'mix', 'cover', ' karaoke',
        'pubg', 'game', 'bgm for', 'status', 'whatsapp',
    ]

    has_tamil = any(ind in title_lower for ind in tamil_indicators)
    has_negative = any(neg in title_lower for neg in negative)

    # If it has Tamil script, likely correct
    if any(c >= '\u0b80' and c <= '\u0fff' for c in title):
        return True

    # If has positive indicators and no strong negatives
    if has_tamil and not has_negative:
        return True

    # If official channel and not obviously wrong
    return False


def parse_title(title, year):
    """Parse YouTube title to extract metadata."""
    # Clean title
    title_clean = re.sub(r'[\|/\-\–\—•*]', ' ', title)
    title_clean = re.sub(r'\s+', ' ', title_clean).strip()

    parts = [p.strip() for p in title_clean.split('|')]
    parts = [p for p in parts if p and len(p) > 2]

    song_title = title_clean[:80]
    movie = ""

    # Try to find movie name (usually in parentheses or after |)
    paren_match = re.search(r'\(([^)]+)\)', title)
    if paren_match:
        potential = paren_match.group(1)
        if len(potential) > 3 and len(potential) < 50:
            movie = potential

    # Try pipe-separated parts
    for i, p in enumerate(parts[1:4], 1):
        p_lower = p.lower()
        if any(x in p_lower for x in ['movie', 'film', 'video', 'song', 'ft', 'from', ' starring', 'preserved']):
            continue
        if 4 < len(p) < 50 and not re.search(r'\d{4}', p):
            movie = p
            break

    return song_title, movie


def main():
    print("Tamil Song Fetcher v2")
    print("=" * 50)

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

    print(f"Existing songs: {len(existing_rows)}")
    print()

    all_new_songs = {}
    seen_ids = set(existing_ids)

    # Search using targeted queries
    all_queries = []

    # Add decade-based queries
    for decade, queries in SEARCH_QUERIES.items():
        for q in queries:
            all_queries.append((decade, q))

    # Add additional queries
    for q in ADDITIONAL_QUERIES:
        all_queries.append((None, q))

    print(f"Total queries to run: {len(all_queries)}")
    print()

    for i, (decade, query) in enumerate(all_queries):
        print(f"[{i+1}/{len(all_queries)}] {query}...")

        songs = search_songs(query, limit=25)

        count = 0
        for song in songs:
            vid = song.get('id', '')
            if vid in seen_ids:
                continue

            title = song.get('title', '')
            channel = song.get('channel', '')
            duration = song.get('duration', 0)
            views = song.get('view_count', 0)

            # Skip if not likely Tamil film song
            if not is_likely_tamil_film_song(title):
                continue

            # Determine year
            year = extract_year_from_title(title, decade)
            if year is None:
                year = decade if decade else 2000

            song_title, movie = parse_title(title, year)

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
                'duration': duration,
                'official': 'Y' if is_official(channel) else 'N',
                'verified': 'N',
                'downloaded': 'N',
                'download_path': '',
                'view_count': views,
                'error': ''
            }
            seen_ids.add(vid)
            count += 1

        print(f"  Found {count} new songs (total unique: {len(all_new_songs)})")

        time.sleep(0.3)

        # Save progress periodically
        if (i + 1) % 10 == 0:
            print(f"  Saving progress...")
            combined = existing_rows + list(all_new_songs.values())
            with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=combined[0].keys())
                writer.writeheader()
                writer.writerows(combined)

    # Save final
    print()
    print("=" * 50)
    combined = existing_rows + list(all_new_songs.values())

    # Sort by year and view_count
    combined.sort(key=lambda x: (int(x.get('year', 0)), int(x.get('view_count', 0))), reverse=True)

    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=combined[0].keys())
        writer.writeheader()
        writer.writerows(combined)

    # Stats
    by_year = {}
    for row in combined:
        y = row.get('year', '?')
        by_year[y] = by_year.get(y, 0) + 1

    print(f"✓ Complete! Total songs: {len(combined)}")
    print(f"  Years covered: {len(by_year)}")
    print(f"  Songs with YouTube IDs: {sum(1 for r in combined if r.get('youtube_id'))}")


if __name__ == "__main__":
    main()
