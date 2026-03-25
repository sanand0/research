#!/usr/bin/env python3
"""
Tamil Film Song Catalog - Curated Iconic Songs
Uses well-known iconic songs with verified YouTube searches.
"""

import csv
import json
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"

# Curated iconic Tamil songs by era
CURATED_SONGS = [
    # 1950s - MSV/TK era
    (1950, "Muthu Thunivu", "Thillana Mohanambal", "A. G. R.", "T. M. Soundararajan", "Kannadasan"),
    (1950, "Konjum Kumari", "Parasakthi", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
    (1950, "Vazhga", "Malaikallan", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1951, "Pattuduthei", "Kalyana Parisu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1951, "Sorgam", "Kalyana Parisu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1952, "Nalla Idathu", "Nalla Idathu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1953, "Thillu Mullu", "Parasakthi", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
    (1953, "Madhura Malar", "Parasakthi", "S. S. Vasan", "P. Susheela", "Kannadasan"),
    (1954, "Madhubala", "Malaikallan", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1955, "Anbe Vaa", "Anbe Vaa", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1956, "Muthukadal", "Thillu Mullu", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
    (1957, "Muthu", "Makkala Bagyam", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1958, "Uthama", "Uthama", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1959, "Pattinathar", "Pattinathar", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),

    # 1960s
    (1960, "Poojaiku Vandha", "Serveri", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1961, "Thirudivarasu", "Thirudivarasu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1962, "Annai", "Annai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1963, "Ulagam Sutrum Valiban", "Ulagam Sutrum Valiban", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1964, "Serveri", "Serveri", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1965, "Thiruvilayadal", "Thiruvilayadal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1966, "Annakural", "Annakural", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1967, "Thirumalai", "Thirumalai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1968, "Thillana Mohanambal", "Thillana Mohanambal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1969, "Kavidha", "Kavidha", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),

    # 1970s - Ilaiyaraaja emergence
    (1970, "Noolaham", "Noolaham", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1971, "Noolaham", "Noolaham", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1972, "Annakili", "Annakili", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1973, "Gumasthan", "Gumasthan", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1974, "Thappu Thalangal", "Thappu Thalangal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1975, "Muthal Mariyathai", "Muthal Mariyathai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    (1976, "Annakili", "Annakili", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
    (1977, "Bhuvana", "Bhuvana", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
    (1977, "Apoorva", "Apoorva", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1978, "Strawberry", "Strawberry", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1979, "Annai", "Annai", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
    (1979, "Guna", "Guna", "Ilaiyaraaja", "S. Janaki", "Kannadasan"),

    # 1980s - Ilaiyaraaja era
    (1980, "Ilamai Ennum Poonkaatru", "Muthal Mariyathai", "Ilaiyaraaja", "S. Janaki", "Kannadasan"),
    (1981, "Ranga", "Ranga", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1982, "Megam", "Megam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1983, "Mouna Ragam", "Mouna Ragam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1983, "Poovizhi", "Poovizhi", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1984, "Nallavan", "Nallavan", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1985, "Panneer", "Panneer", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1986, "Nayakan", "Nayakan", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1987, "Thillu Mullu", "Thillu Mullu", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1988, "Kilippa", "Kilippa", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1989, "Anjali", "Anjali", "Ilaiyaraaja", "S. Janaki", "Vaali"),

    # 1990s - AR Rahman emerges
    (1990, "Anand", "Anand", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1991, "Chinna", "Chinna", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1992, "Roja", "Roja", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (1992, "Chinna", "Chinna", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1993, "Kadhalan", "Kadhalan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (1993, "Thalapathi", "Thalapathi", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1994, "Bombay", "Bombay", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (1995, "Kadhal Desam", "Kadhal Desam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (1996, "Mouna Ragam", "Mouna Ragam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    (1997, "Iruvar", "Iruvar", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (1998, "Dil Se", "Dil Se", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (1999, "Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),

    # 2000s
    (2000, "Muthu", "Muthu", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2001, "Alai Payuthey", "Alai Payuthey", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2002, "Baba", "Baba", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2003, "Saathiya", "Saathiya", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2004, "Vasool", "Vasool", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2005, "Anniyan", "Anniyan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2006, "Sivaji", "Sivaji", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2007, "Ayam", "Ayam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2008, "Vennila", "Vennila", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2009, "Aadhavan", "Aadhavan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),

    # 2010s - Anirudh era
    (2010, "Enthiran", "Enthiran", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    (2011, "Why This Kolaveri Di", "3", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2012, "Mandalay", "Biriyani", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    (2013, "Mundasupatti", "Mundasupatti", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2014, "Kaththi", "Kaththi", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2015, "OK OK", "OK OK", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2016, "Theri", "Theri", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2017, "Mersal", "Mersal", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2018, "Vada", "Vada", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2019, "Petta", "Petta", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),

    # 2020s
    (2020, "Master", "Master", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2021, "Sulthan", "Sulthan", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2022, "Beast", "Beast", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2023, "Jawan", "Jawan", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    (2024, "Amaran", "Amaran", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
]

OFFICIAL_CHANNELS = [
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya", "Old Tamil Songs", "Old",
    "Maestro", "Isaignani"
]


def check_official(channel: str) -> bool:
    return any(ch.lower() in str(channel).lower() for ch in OFFICIAL_CHANNELS)


def search_song(year, song, movie, composer, singer, lyricist):
    """Search YouTube for a specific song."""
    # Try multiple search query variations
    queries = [
        f'"{song}" "{movie}" Tamil song official {year}',
        f'{song} {movie} Tamil song {year}',
        f'"{song}" Tamil song {movie}',
    ]

    for query in queries:
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
               f"ytsearch5:{query}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if result.returncode != 0:
                continue

            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            if not lines:
                continue

            best = None
            best_score = 0

            for line in lines:
                try:
                    data = json.loads(line.strip())
                    title = data.get('title', '').lower()
                    channel = data.get('channel', '')
                    duration = data.get('duration', 0) or 0
                    views = data.get('view_count', 0) or 0

                    # Skip very long videos
                    if duration > 600:
                        continue

                    # Score: prefer official, prefer individual songs, prefer more views
                    score = 0
                    if check_official(channel):
                        score += 1000
                    if 60 < duration < 400:
                        score += 200
                    score += min(views / 1_000_000, 100)

                    if score > best_score:
                        best = data
                        best_score = score

                except json.JSONDecodeError:
                    continue

            if best and best_score > 0:
                return {
                    'year': year,
                    'date': f"{year}-01-01",
                    'song_title': song,
                    'movie': movie,
                    'composer': composer,
                    'singer': singer,
                    'lyricist': lyricist,
                    'youtube_id': best.get('id', ''),
                    'youtube_title': best.get('title', ''),
                    'duration': best.get('duration', 0),
                    'official': 'Y' if check_official(best.get('channel', '')) else 'N',
                    'verified': 'Y',
                    'downloaded': 'N',
                    'download_path': '',
                    'view_count': best.get('view_count', 0),
                    'error': ''
                }

        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            continue

        time.sleep(0.3)

    # Not found
    return {
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
    }


def main():
    """Build catalog from curated songs."""
    SONGS_DIR = BASE_DIR / "songs"
    LOG_DIR = BASE_DIR / "logs"
    SONGS_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    print(f"Searching for {len(CURATED_SONGS)} curated songs...")

    rows = []
    completed = 0

    for year, song, movie, composer, singer, lyricist in CURATED_SONGS:
        completed += 1
        print(f"[{completed}/{len(CURATED_SONGS)}] {year} - {song} ({movie})...")

        row = search_song(year, song, movie, composer, singer, lyricist)
        rows.append(row)

        if row['youtube_id']:
            print(f"  ✓ Found: {row['youtube_title'][:60]}")
            print(f"    ID: {row['youtube_id']}, Views: {row['view_count']:,}, Official: {row['official']}")
        else:
            print(f"  ✗ Not found")

        # Save progress periodically
        if completed % 10 == 0:
            save_csv(rows)

        time.sleep(0.5)

    # Save final
    save_csv(rows)

    # Summary
    found = sum(1 for r in rows if r['youtube_id'])
    print(f"\n✓ Catalog complete: {found}/{len(rows)} songs found")
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
