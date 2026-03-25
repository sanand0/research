#!/usr/bin/env python3
"""Test search with just 2011 songs first."""

import json
import subprocess
import time

# Test with well-known 2011 songs
TEST_SONGS = [
    ("Why This Kolaveri Di", "Raanjhaana", "Anirudh Ravichander", "Anirudh", "Naan Muthu"),
    ("Humpty", "Muthu", "Anirudh Ravichander", "Anirudh", "Naan Muthu"),
    ("Pooja", "Muthu", "Anirudh Ravichander", "Anirudh", "Naan Muthu"),
    ("Emforand", "3", "Anirudh Ravichander", "Anirudh", "Naan Muthu"),
    ("Otha Sollaala", "Aadukalam", "G. V. Prakash Kumar", "Velmurugan", "Vijay Sethupathi"),
]

def check_official(channel):
    official = ["SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking", "Ayngaran", "T-Series"]
    return any(ch in str(channel) for ch in official)

for movie, song, composer, singer, lyricist in TEST_SONGS:
    query = f"{song} {movie} Tamil song official"
    print(f"\nSearching: {query}")

    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--", f"ytsearch3:{query}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    data = json.loads(line)
                    is_official = check_official(data.get('channel', ''))
                    print(f"  ✓ {data.get('title', '')[:70]}")
                    print(f"    Channel: {data.get('channel', 'N/A')} (Official: {'Y' if is_official else 'N'})")
                    print(f"    Duration: {data.get('duration', 0)}s, Views: {data.get('view_count', 0):,}")
                    print(f"    ID: {data.get('id', '')}")
    except Exception as e:
        print(f"  Error: {e}")

    time.sleep(1)
