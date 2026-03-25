#!/usr/bin/env python3
"""
Extract 50-second clips from downloaded songs starting at 30 seconds.
Saves clips as separate files for embedding/extraction.
"""

import csv
import subprocess
import os
from pathlib import Path

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
SONGS_DIR = BASE_DIR / "songs"
CLIPS_DIR = BASE_DIR / "clips_50s"
PROGRESS_FILE = BASE_DIR / ".clip_progress.json"

CLIP_START = 30  # seconds
CLIP_DURATION = 50  # seconds

def get_audio_file(song_path_pattern):
    """Find the actual audio file matching the song path pattern."""
    # Pattern is like: songs/{id}_{title}.%(ext)s
    # Need to find the actual file with extension
    base = str(song_path_pattern).replace('%(ext)s', '*')
    base = base.replace('.%(ext)s', '*')
    # Find files matching
    songs_path = Path(SONGS_DIR)
    # The actual pattern would be the base without wildcards and with actual extension
    # Let's just list the songs dir and find matches
    return None  # Will use the path directly

def extract_clip(youtube_id, song_title, download_path):
    """Extract a 50-second clip from the song."""
    if not download_path:
        return False, "No download path"

    # Find the actual file - download_path has %(ext)s placeholder
    base = download_path.replace('%(ext)s', '*')
    base = base.replace('.', '_*.')

    # Search in songs directory
    actual_files = list(SONGS_DIR.glob(f"{youtube_id}_*"))
    if not actual_files:
        return False, f"No file found for {youtube_id}"

    input_file = actual_files[0]
    if not input_file.exists():
        return False, f"File not found: {input_file}"

    # Output file
    output_file = CLIPS_DIR / f"{youtube_id}_clip.mp3"

    # Skip if already exists
    if output_file.exists():
        return True, "Already exists"

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite
        "-ss", str(CLIP_START),  # Start time
        "-i", str(input_file),   # Input file
        "-t", str(CLIP_DURATION),  # Duration
        "-acodec", "libmp3lame",
        "-q:a", "2",  # Quality
        str(output_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and output_file.exists():
            size = output_file.stat().st_size
            return True, f"Created: {size:,} bytes"
        else:
            return False, result.stderr[:200] if result.stderr else "Unknown error"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:100]

def main():
    print("Tamil Song Clip Extractor")
    print(f"Clip: {CLIP_DURATION}s starting at {CLIP_START}s")
    print("=" * 60)

    CLIPS_DIR.mkdir(exist_ok=True)

    # Read CSV
    rows = []
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id') and row.get('downloaded') == 'Y':
                rows.append(row)

    total = len(rows)
    print(f"Total downloaded songs: {total}")
    print()

    # Count existing clips
    existing_clips = len(list(CLIPS_DIR.glob("*.mp3")))
    print(f"Existing clips: {existing_clips}")
    print()

    success_count = 0
    skip_count = 0
    fail_count = 0

    for idx, row in enumerate(rows):
        youtube_id = row.get('youtube_id', '')
        song_title = row.get('song_title', 'unknown')
        download_path = row.get('download_path', '')

        # Check if clip already exists
        output_file = CLIPS_DIR / f"{youtube_id}_clip.mp3"
        if output_file.exists():
            skip_count += 1
            continue

        print(f"[{idx+1}/{total}] Extracting: {song_title[:40]}...")

        success, msg = extract_clip(youtube_id, song_title, download_path)

        if success:
            print(f"  ✓ {msg}")
            success_count += 1
        else:
            print(f"  ✗ {msg}")
            fail_count += 1

    print()
    print("=" * 60)
    print(f"Done: {success_count} created, {skip_count} skipped, {fail_count} failed")
    print(f"Clips saved to: {CLIPS_DIR}")

if __name__ == "__main__":
    main()