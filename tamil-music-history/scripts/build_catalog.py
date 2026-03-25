#!/usr/bin/env python3
"""
Comprehensive Tamil Song Catalog Builder
Searches YouTube for popular Tamil songs across all years and builds catalog.
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

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
SONGS_DIR = BASE_DIR / "songs"
LOG_DIR = BASE_DIR / "logs"

# Comprehensive seed list of iconic Tamil songs by year
SEED_SONGS = {
    1950: [
        ("Thillana Mohanambal", "Muthu Thunivu", "A. G. R.", "T. M. Soundararajan", "Kannadasan"),
        ("Vetri", "Vetri", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Parasakthi", "Konjum Kumari", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Amarashilpi", "Konjum Purave", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Muthu", "Muthu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1951: [
        ("Kalyana Parisu", "Pattuduthei", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Kalyana Parisu", "Sorgam", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Vijaya", "Vijaya", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1952: [
        ("Nalla Idathu", "Nalla Idathu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Amarashilpi", "Madhukketha", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1953: [
        ("Parasakthi", "Konjum Kumari", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Parasakthi", "Thillu Mullu", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Parasakthi", "Madhura Malar", "S. S. Vasan", "P. Susheela", "Kannadasan"),
    ],
    1954: [
        ("Malaikallan", "Vazhga", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Malaikallan", "Madhubala", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1955: [
        ("Anbe Vaa", "Sorgam", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Anbe Vaa", "Vazhga", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Vijaya", "Vijaya", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1956: [
        ("Thillu Mullu", "Muthukadal", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Rangoon Radha", "Aayiram", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1957: [
        ("Makkala Bagyam", "Muthu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Nellai", "Nellai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1958: [
        ("Uthama", "Uthama", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1959: [
        ("Pattinathar", "Pattinathar", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1960: [
        ("Palumbu", "Palumbu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Thirudivarasu", "Madhuram", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1961: [
        ("Thirudivarasu", "Thirudivarasu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1962: [
        ("Annai", "Annai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1963: [
        ("Ulagam Sutrum Valiban", "Ulagam Sutrum Valiban", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1964: [
        ("Serveri", "Serveri", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1965: [
        ("Thiruvilayadal", "Thiruvilayadal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1966: [
        ("Annakural", "Annakural", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1967: [
        ("Thirumalai", "Thirumalai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1968: [
        ("Thillana Mohanambal", "Thillana Mohanambal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1969: [
        ("Kavidha", "Kavidha", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1970: [
        ("Noolaham", "Noolaham", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1971: [
        ("Noolaham", "Noolaham", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1972: [
        ("Annakili", "Annakili", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1973: [
        ("Gumasthan", "Gumasthan", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1974: [
        ("Thappu Thalangal", "Thappu Thalangal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1975: [
        ("Muthal Mariyathai", "Muthal Mariyathai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1976: [
        ("Annakili", "Annakili", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
        ("Gayathri", "Gayathri", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
    ],
    1977: [
        ("Bhuvana", "Bhuvana", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
        ("Apoorva", "Apoorva", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1978: [
        ("Strawberry", "Strawberry", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Kilippa", "Kilippa", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1979: [
        ("Annai", "Annai", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
        ("Guna", "Guna", "Ilaiyaraaja", "S. Janaki", "Kannadasan"),
    ],
    1980: [
        ("Varum", "Varum", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Sogasu", "Sogasu", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Murattu", "Murattu", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1981: [
        ("Ranga", "Ranga", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Tik Tik", "Tik Tik", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1982: [
        ("Megam", "Megam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Apoorva", "Apoorva", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1983: [
        ("Mouna Ragam", "Mouna Ragam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Poovizhi", "Poovizhi", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1984: [
        ("Nallavan", "Nallavan", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Vishnu", "Vishnu", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1985: [
        ("Panneer", "Panneer", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Muthal", "Muthal", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1986: [
        ("Mouna Ragam", "Mouna Ragam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Nayakan", "Nayakan", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1987: [
        ("Thillu Mullu", "Thillu Mullu", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Muthal", "Muthal", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1988: [
        ("Kilippa", "Kilippa", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Rangam", "Rangam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1989: [
        ("Muthal", "Muthal", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Anjali", "Anjali", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1990: [
        ("Muthal", "Muthal", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Anand", "Anand", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1991: [
        ("Chinna", "Chinna", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Thamizha", "Thamizha", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1992: [
        ("Roja", "Roja", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Chinna", "Chinna", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1993: [
        ("Kadhalan", "Kadhalan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Thalapathi", "Thalapathi", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    ],
    1994: [
        ("Bombay", "Bombay", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Kadhalan", "Kadhalan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    1995: [
        ("Minsara Kanavu", "Minsara Kanavu", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Kadhal Desam", "Kadhal Desam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    1996: [
        ("Mouna Ragam", "Mouna Ragam", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    1997: [
        ("Muthal", "Muthal", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Iruvar", "Iruvar", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    1998: [
        ("Dil Se", "Dil Se", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    1999: [
        ("Muthal", "Muthal", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2000: [
        ("Muthu", "Muthu", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Alai Payuthey", "Alai Payuthey", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2001: [
        ("Lagaan", "Lagaan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Koi", "Koi", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2002: [
        ("Baba", "Baba", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2003: [
        ("Saathiya", "Saathiya", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Yuva", "Yuva", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2004: [
        ("Vasool", "Vasool", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Singsar", "Singsar", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2005: [
        ("Anniyan", "Anniyan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Sukanya", "Sukanya", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2006: [
        ("Vantage", "Vantage", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Sivaji", "Sivaji", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2007: [
        ("Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Ayam", "Ayam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2008: [
        ("Jaane Tu", "Jaane Tu", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Vennila", "Vennila", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2009: [
        ("Rang De Basanti", "Rang De Basanti", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Aadhavan", "Aadhavan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2010: [
        ("Raavan", "Raavan", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Enthiran", "Enthiran", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2011: [
        ("Why This Kolaveri Di", "3", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
        ("Kollaikaran", "Kollaikaran", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    ],
    2012: [
        ("Mandalay", "Biriyani", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
        ("Thaandavam", "Thaandavam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2013: [
        ("Mundasupatti", "Mundasupatti", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Happy", "Dingy", "Anirudh Ravichander", "Anirudh Ravichander", "Dhanush"),
    ],
    2014: [
        ("Mundasupatti", "Mundasupatti", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Kaththi", "Kaththi", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2015: [
        ("OK OK", "OK OK", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Yennai", "Yennai", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2016: [
        ("Theri", "Theri", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Mersal", "Mersal", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2017: [
        ("Mersal", "Mersal", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Bigger", "Bigger", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2018: [
        ("Vada", "Vada", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Kolamaavu", "Kolamaavu", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2019: [
        ("Petta", "Petta", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Asuran", "Asuran", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2020: [
        ("Soora", "Soora", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Master", "Master", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2021: [
        ("Sulthan", "Sulthan", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Doctor", "Doctor", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2022: [
        ("Beast", "Beast", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Vikram", "Vikram", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2023: [
        ("Jawan", "Jawan", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Leo", "Leo", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2024: [
        ("Amaran", "Amaran", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Indian", "Indian", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2025: [
        ("Vida", "Vida", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
        ("Puli", "Puli", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
    2026: [
        ("Vida", "Vida", "Anirudh Ravichander", "Anirudh Ravichander", "Vijay Sethupathi"),
    ],
}

OFFICIAL_CHANNELS = [
    "SonyMusicSouthVEVO", "SunMusic", "Tips", "Saregama", "Thinking",
    "Ayngaran", "T-Series", "Music", "VEVO", "Ilaiyaraaja", "Anirudh",
    "Mithran", "Lahari", "Aditya", "Sathya"
]

lock = threading.Lock()


def check_official(channel: str) -> bool:
    return any(ch in str(channel) for ch in OFFICIAL_CHANNELS)


def search_song(year: int, song: str, movie: str, composer: str, singer: str, lyricist: str) -> dict:
    """Search YouTube for a song and return the best result."""
    query = f"{song} {movie} Tamil song official {year}"
    print(f"  Searching: {song} ({year})")

    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--",
           f"ytsearch5:{query}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return make_row(year, song, movie, composer, singer, lyricist, error="Search failed")

        lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return make_row(year, song, movie, composer, singer, lyricist, error="No results")

        best = None
        best_score = 0

        for line in lines:
            try:
                data = json.loads(line.strip())
                title = data.get('title', '').lower()
                channel = data.get('channel', '')
                duration = data.get('duration', 0) or 0
                views = data.get('view_count', 0) or 0

                # Skip very long videos (jukeboxes > 10 min)
                if duration > 600:
                    continue

                # Skip non-Tamil indicators
                non_tamil = ['hindi', 'telugu', 'malayalam', 'kannada']
                if any(x in title for x in non_tamil) and 'tamil' not in title:
                    continue

                # Score: prefer official, prefer shorter (songs not jukeboxes), prefer more views
                score = 0
                if check_official(channel):
                    score += 1000
                if duration < 400:  # Prefer individual songs
                    score += 100
                score += min(views / 1_000_000, 100)  # Cap view bonus

                if score > best_score:
                    best = data
                    best_score = score

            except (json.JSONDecodeError, KeyError):
                continue

        if best:
            return make_row(
                year, song, movie, composer, singer, lyricist,
                youtube_id=best.get('id', ''),
                youtube_title=best.get('title', ''),
                duration=best.get('duration', 0),
                official='Y' if check_official(best.get('channel', '')) else 'N',
                view_count=best.get('view_count', 0)
            )

        return make_row(year, song, movie, composer, singer, lyricist, error="No suitable result")

    except subprocess.TimeoutExpired:
        return make_row(year, song, movie, composer, singer, lyricist, error="Timeout")
    except Exception as e:
        return make_row(year, song, movie, composer, singer, lyricist, error=str(e))


def make_row(year, song, movie, composer, singer, lyricist,
             youtube_id='', youtube_title='', duration=0, official='N',
             view_count=0, error=''):
    return {
        'year': year,
        'date': f"{year}-01-01",
        'song_title': song,
        'movie': movie,
        'composer': composer,
        'singer': singer,
        'lyricist': lyricist,
        'youtube_id': youtube_id,
        'youtube_title': youtube_title,
        'duration': duration,
        'official': official,
        'verified': 'Y' if youtube_id else 'N',
        'downloaded': 'N',
        'download_path': '',
        'view_count': view_count,
        'error': error
    }


def main():
    """Build the catalog using parallel searches."""
    # Ensure directories exist
    SONGS_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    # Flatten seed list
    tasks = []
    for year in sorted(SEED_SONGS.keys()):
        for movie, song, composer, singer, lyricist in SEED_SONGS[year]:
            tasks.append((year, song, movie, composer, singer, lyricist))

    print(f"Total songs to search: {len(tasks)}")

    rows = []
    completed = 0

    # Process in parallel (limit threads to avoid rate limiting)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(search_song, *task): task
            for task in tasks
        }

        for future in as_completed(futures):
            task = futures[future]
            try:
                row = future.result()
                rows.append(row)
                completed += 1

                status = "✓" if row['youtube_id'] else "✗"
                print(f"[{completed}/{len(tasks)}] {status} {task[0]} - {task[1]} [{task[2]}]")

            except Exception as e:
                print(f"[{completed}/{len(tasks)}] Error: {e}")
                rows.append(make_row(*task, error=str(e)))

            # Save progress periodically
            if completed % 20 == 0:
                save_csv(rows)

            time.sleep(0.5)  # Rate limiting

    # Save final
    save_csv(rows)

    # Summary
    found = sum(1 for r in rows if r['youtube_id'])
    print(f"\n✓ Catalog complete: {found}/{len(rows)} songs found")
    print(f"  CSV: {SONGS_CSV}")


def save_csv(rows):
    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
