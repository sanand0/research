#!/usr/bin/env python3
"""Test search with corrected songs."""

import json
import subprocess
import time
import csv
from pathlib import Path

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"

# Test with known 2011 hits and corrected data
TEST_SONGS = [
    (2011, "Why This Kolaveri Di", "3", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2011, "Naan Muthu", "3", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2011, " Kannanda", "Muthu", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2012, "Mandalay", "Biriyani", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2013, "Mundasupatti", "Mundasupatti", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2013, "Happy", "Dingy", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2014, "Selfie", "Mundasupatti", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
]

def check_official(channel):
    official = ["SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking", "Ayngaran", "T-Series", "Music", "VEVO"]
    return any(ch in str(channel) for ch in official)

def search_song(year, song, movie, composer, singer, lyricist):
    query = f"{song} {movie} Tamil song {year}"
    print(f"\nSearching: {query}")

    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--", f"ytsearch5:{query}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            if not lines:
                return None

            best = None
            best_views = 0

            for line in lines:
                try:
                    data = json.loads(line.strip())
                    is_official = check_official(data.get('channel', ''))
                    views = data.get('view_count', 0) or 0

                    # Skip very long videos (likely jukeboxes > 10 min)
                    duration = data.get('duration', 0) or 0
                    if duration > 600:
                        continue

                    # Skip non-Tamil language indicators in title
                    title = data.get('title', '').lower()
                    if any(x in title for x in ['hindi', 'telugu', 'malayalam', 'kannada']):
                        if 'tamil' not in title:
                            continue

                    # Prefer official channels
                    if is_official and views > best_views:
                        best = data
                        best_views = views

                    # Fallback to highest views
                    if not best and views > best_views:
                        best = data
                        best_views = views

                except json.JSONDecodeError:
                    continue

            if best:
                is_official = check_official(best.get('channel', ''))
                print(f"  ✓ {best.get('title', '')[:70]}")
                print(f"    Channel: {best.get('channel', 'N/A')} (Official: {'Y' if is_official else 'N'})")
                print(f"    Duration: {best.get('duration', 0):.0f}s, Views: {best.get('view_count', 0):,}")
                print(f"    ID: {best.get('id', '')}")
                return best

            print(f"  ✗ No suitable result found")
            return None

    except Exception as e:
        print(f"  Error: {e}")
        return None

    return None

# Run test searches
rows = []
for year, song, movie, composer, singer, lyricist in TEST_SONGS:
    result = search_song(year, song, movie, composer, singer, lyricist)
    if result:
        rows.append({
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
            'official': 'Y' if check_official(result.get('channel', '')) else 'N',
            'verified': 'Y',
            'downloaded': 'N',
            'download_path': '',
            'view_count': result.get('view_count', 0),
            'error': ''
        })
    else:
        rows.append({
            'year': year,
            'date': f"{year}-01-01",
            'song_title': song,
            'movie': movie,
            'composer': composer,
            'singer': singer,
            'lyricist': lyricist,
            'youtube_id': '',
            'youtube_title': '',
            'duration': 0,
            'official': 'N',
            'verified': 'N',
            'downloaded': 'N',
            'download_path': '',
            'view_count': 0,
            'error': 'Not found'
        })
    time.sleep(1)

# Write test CSV
if rows:
    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Test catalog written: {len(rows)} songs")
    for row in rows:
        status = "✓" if row['youtube_id'] else "✗"
        print(f"  {status} {row['year']} - {row['song_title']} ({row['movie']}) [{row['youtube_id']}]")
