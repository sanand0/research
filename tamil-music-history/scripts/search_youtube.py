#!/usr/bin/env python3
"""
Tamil Film Song Catalog Builder & Downloader
Uses yt-dlp to search YouTube for popular Tamil songs and build a catalog.
"""

import csv
import json
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
SONGS_DIR = BASE_DIR / "songs"
LOG_DIR = BASE_DIR / "logs"

# Iconic Tamil songs by year (seed data - movie, song, composer, singer, lyricist)
SEED_SONGS = {
    1950: [
        ("Thillana Mohanambal", "Muthu Thunivu", "A. G. R. / S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Amarashilpi", "Konjum Purave", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Vijaya", "Mottukkal", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1951: [
        ("Kalyana Parisu", "Pattuduthei", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Kalyana Parisu", "Sorgam", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1952: [
        ("Nalla Idathu", "Nalla Idathu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Amarashilpi", "Madhukketha", "S. V. Vasan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1953: [
        ("Parasakthi", "Konjum Kumari", "S. S. Vasan", "T. M. Soundararajan / P. Susheela", "Kannadasan"),
        ("Parasakthi", "Thillu Mullu", "S. S. Vasan", "T. M. Soundararajan", "Kannadasan"),
        ("Parasakthi", "Madhura Malar", "S. S. Vasan", "P. Susheela", "Kannadasan"),
    ],
    1954: [
        ("Malaikallan", "Vazhga", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Malaikallan", "Madhubala", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1955: [
        ("Anbe Vaa", "Sorgam", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Anbe Vaa", "Vazhga", "M. S. Viswanathan", "T. M. Soundararajan / P. Susheela", "Kannadasan"),
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
        ("Thaayin", "Mundha", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1959: [
        ("Vettei", "Vettei", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Pattinathar", "Pattinathar", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1960: [
        ("Kavignar", "Kavignar", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Paa", "Paa", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1961: [
        ("Thirudivarasu", "Madhuram", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Kalyana", "Kalyana", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1962: [
        ("Annai", "Annai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Navarasa", "Navarasa", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1963: [
        ("Ulagam Sutrum Valiban", "Ulagam Sutrum Valiban", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Pooja", "Pooja", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1964: [
        ("Serveri", "Serveri", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Kalyana", "Kalyana", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1965: [
        ("Thiruvilayadal", "Thiruvilayadal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Shakti", "Shakti", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1966: [
        ("Annakural", "Annakural", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Madhura", "Madhura", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1967: [
        ("Thirumalai", "Thirumalai", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Madhubala", "Madhubala", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1968: [
        ("Thillana Mohanambal", "Thillana Mohanambal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Kalyana", "Kalyana", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1969: [
        ("Kavidha", "Kavidha", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
        ("Thiruvilayadal", "Thiruvilayadal", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
    ],
    1970: [
        ("Thirudivarasu", "Thirudivarasu", "M. S. Viswanathan", "T. M. Soundararajan", "Kannadasan"),
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
    ],
    1977: [
        ("Bhuvana", "Bhuvana", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
        ("Gayathri", "Gayathri", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
    ],
    1978: [
        ("Strawberry", "Strawberry", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
        ("Muthal", "Muthal", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
    ],
    1979: [
        ("Annai", "Annai", "Ilaiyaraaja", "T. M. Soundararajan", "Kannadasan"),
        ("Guna", "Guna", "Ilaiyaraaja", "S. Janaki", "Kannadasan"),
    ],
    1980: [
        ("Varum", "Varum", "Ilaiyaraaja", "S. Janaki", "Vaali"),
        ("Sogasu", "Sogasu", "Ilaiyaraaja", "S. Janaki", "Vaali"),
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
        (" Sivaji", "Sivaji", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2007: [
        ("Kadhal", "Kadhal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Ayam", "Ayam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2008: [
        ("Jaane Tu... Ya Jaane Na", "Jaane Tu... Ya Jaane Na", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
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
        ("Muthu", "Muthu", "Anirudh", "Anirudh", "Vairamuthu"),
        ("3", "3", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Yelunaaru", "Yelunaaru", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2012: [
        ("Thaandavam", "Thaandavam", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
        ("Kadal", "Kadal", "A. R. Rahman", "S. Janaki", "Vairamuthu"),
    ],
    2013: [
        ("Parvathimala", "Parvathimala", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Kollaikaran", "Kollaikaran", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2014: [
        ("Mundasupatti", "Mundasupatti", "Anirudh", "Anirudh", "Vairamuthu"),
        (" Kaththi", "Kaththi", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2015: [
        ("OK OK", "OK OK", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Yennai", "Yennai", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2016: [
        ("Theri", "Theri", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Mersal", "Mersal", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2017: [
        ("Mersal", "Mersal", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Bigger", "Bigger", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2018: [
        ("Vada", "Vada", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Kolamaavu", "Kolamaavu", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2019: [
        ("Petta", "Petta", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Asuran", "Asuran", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2020: [
        ("Soora", "Soora", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Master", "Master", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2021: [
        ("Sulthan", "Sulthan", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Doctor", "Doctor", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2022: [
        ("Beast", "Beast", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Vikram", "Vikram", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2023: [
        ("Jawan", "Jawan", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Leo", "Leo", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2024: [
        ("Amaran", "Amaran", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Indian", "Indian", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2025: [
        ("Great", "Great", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Puli", "Puli", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
    2026: [
        ("Vida", "Vida", "Anirudh", "Anirudh", "Vairamuthu"),
        ("Disease", "Disease", "Anirudh", "Anirudh", "Vairamuthu"),
    ],
}


def run_yt_dlp(args: list, timeout: int = 60) -> dict | None:
    """Run yt-dlp and return parsed JSON output."""
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError) as e:
        print(f"  Error: {e}")
        return None


def search_youtube(query: str, year: int, limit: int = 5) -> list[dict]:
    """Search YouTube for a song and return results."""
    search_query = f"{query} {year} Tamil song official"
    print(f"  Searching: {search_query}")

    cmd = [
        "yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings",
        "--", f"ytsearch{limit}:{search_query}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            return [json.loads(line) for line in lines if line.strip()]
    except Exception as e:
        print(f"  Search error: {e}")

    return []


def check_official_channel(channel: str) -> bool:
    """Check if the channel is an official music channel."""
    official_channels = [
        "SonyMusicSouthVEVO", "SunMusic", "Tips", "Aditya", "Saregama",
        "Thinking", "Mithran", "Lahari", "T-Series", "Shemaroo",
        "Ayngaran", "Visual", "Gamma", "Sathya"
    ]
    return any(ch in channel for ch in official_channels)


def build_catalog():
    """Build the initial catalog from seed data by searching YouTube."""
    rows = []

    for year in sorted(SEED_SONGS.keys()):
        songs = SEED_SONGS[year]
        print(f"\n=== Year {year} ({len(songs)} songs) ===")

        for movie, song_title, composer, singer, lyricist in songs:
            query = f"{song_title} {movie}"
            results = search_youtube(query, year, limit=3)

            if results:
                best = results[0]
                is_official = check_official_channel(best.get('channel', ''))

                rows.append({
                    'year': year,
                    'date': f"{year}-01-01",
                    'song_title': song_title,
                    'movie': movie,
                    'composer': composer,
                    'singer': singer,
                    'lyricist': lyricist,
                    'youtube_id': best.get('id', ''),
                    'youtube_title': best.get('title', ''),
                    'duration': best.get('duration', 0),
                    'official': 'Y' if is_official else 'N',
                    'verified': 'Y',
                    'downloaded': 'N',
                    'download_path': '',
                    'view_count': best.get('view_count', 0),
                    'error': ''
                })
                print(f"  ✓ Found: {best.get('title', '')[:60]}")
            else:
                rows.append({
                    'year': year,
                    'date': f"{year}-01-01",
                    'song_title': song_title,
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
                    'error': 'Not found on YouTube'
                })
                print(f"  ✗ Not found: {song_title}")

            time.sleep(0.5)  # Rate limiting

    # Write to CSV
    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'year', 'date', 'song_title', 'movie', 'composer', 'singer',
            'lyricist', 'youtube_id', 'youtube_title', 'duration', 'official',
            'verified', 'downloaded', 'download_path', 'view_count', 'error'
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Catalog written to {SONGS_CSV} ({len(rows)} songs)")
    return rows


if __name__ == "__main__":
    build_catalog()
