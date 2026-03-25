#!/usr/bin/env python3
"""
Resumable Tamil Song Downloader
Reads songs.csv and downloads songs via yt-dlp with retries and error handling.
"""

import csv
import subprocess
import time
import os
import json
from pathlib import Path
from datetime import datetime
from threading import Lock

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
SONGS_DIR = BASE_DIR / "songs"
LOG_DIR = BASE_DIR / "logs"
PROGRESS_FILE = BASE_DIR / ".download_progress.json"

MAX_RETRIES = 3
RETRY_DELAY = 5

FIELDNAMES = ['year', 'date', 'song_title', 'movie', 'composer', 'singer', 'lyricist',
              'youtube_id', 'youtube_title', 'duration', 'official', 'verified',
              'downloaded', 'download_path', 'view_count', 'error']


def load_progress():
    """Load download progress to enable resuming."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {}


def save_progress(progress: dict):
    """Save download progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def update_csv_row(youtube_id: str, downloaded: str, download_path: str, error: str):
    """Update a single row in the CSV file."""
    rows = []
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id') == youtube_id:
                row = {k: row.get(k, '') for k in FIELDNAMES}
                row['downloaded'] = downloaded
                row['download_path'] = download_path
                if error:
                    row['error'] = error[:200]
            else:
                row = {k: row.get(k, '') for k in FIELDNAMES}
            rows.append(row)

    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def get_download_path(youtube_id: str, title: str) -> Path:
    """Generate the download path for a song."""
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
    return SONGS_DIR / f"{youtube_id}_{safe_title}.%(ext)s"


def download_song(row: dict, progress: dict, lock: Lock) -> tuple[bool, str]:
    """Download a single song with retries."""
    youtube_id = row.get('youtube_id', '')
    title = row.get('youtube_title', row.get('song_title', 'unknown'))

    if not youtube_id:
        return False, "No YouTube ID"

    # Check if already downloaded
    with lock:
        if progress.get(youtube_id, {}).get('downloaded'):
            return True, "Already downloaded"

    url = f"https://www.youtube.com/watch?v={youtube_id}"
    output_path = get_download_path(youtube_id, title)
    log_file = LOG_DIR / f"{youtube_id}.log"

    for attempt in range(MAX_RETRIES):
        try:
            cmd = [
                "yt-dlp",
                "-f", "bestaudio/best",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "-o", str(output_path),
                "--write-info-json",
                "--no-playlist",
                "--no-warnings",
                "-R", "3",
                "--", url
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                with lock:
                    progress[youtube_id] = {
                        'downloaded': True,
                        'path': str(output_path),
                        'timestamp': datetime.now().isoformat()
                    }
                    save_progress(progress)

                update_csv_row(youtube_id, 'Y', str(output_path), '')

                # Move info json to logs
                info_json = Path(str(output_path).replace('%(ext)s', 'info.json'))
                if info_json.exists():
                    info_json.rename(LOG_DIR / f"{youtube_id}.info.json")

                return True, "Success"

            else:
                error_msg = result.stdout[-500:] if result.stdout else "Unknown error"
                print(f"  Attempt {attempt + 1} failed: {error_msg[:100]}")

        except subprocess.TimeoutExpired:
            error_msg = "Timeout"
        except Exception as e:
            error_msg = str(e)[:200]

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))

    with lock:
        progress[youtube_id] = {
            'downloaded': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
        save_progress(progress)

    update_csv_row(youtube_id, 'E', '', error_msg)
    return False, error_msg


def main():
    """Main download function."""
    # Ensure directories exist
    SONGS_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    # Load progress
    progress = load_progress()
    lock = Lock()

    # Read CSV
    rows = []
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id'):
                rows.append(row)

    total = len(rows)
    downloaded = sum(1 for r in rows if progress.get(r['youtube_id'], {}).get('downloaded'))
    print(f"Total songs: {total}, Downloaded: {downloaded}, Remaining: {total - downloaded}")

    if total == 0:
        print("No songs to download. Run search_youtube.py first.")
        return

    # Process all songs
    for idx, row in enumerate(rows):
        youtube_id = row.get('youtube_id', '')

        if not youtube_id:
            print(f"[{idx + 1}/{total}] Skipping - no YouTube ID")
            continue

        if progress.get(youtube_id, {}).get('downloaded'):
            print(f"[{idx + 1}/{total}] Already downloaded: {row.get('song_title', youtube_id)}")
            continue

        print(f"[{idx + 1}/{total}] Downloading: {row.get('song_title', youtube_id)}")

        success, msg = download_song(row, progress, lock)

        if success:
            print(f"  ✓ {msg}")
        else:
            print(f"  ✗ {msg}")

        time.sleep(1)


if __name__ == "__main__":
    main()
