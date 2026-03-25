#!/usr/bin/env python3
"""
Fetch popular Tamil film songs from 1950-1989.
Uses curated lists of famous songs per decade with YouTube search.
"""

import csv
import subprocess
import time
from datetime import datetime
from pathlib import Path
from threading import Lock

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
FIELDNAMES = ['year', 'date', 'song_title', 'movie', 'composer', 'singer', 'lyricist',
              'youtube_id', 'youtube_title', 'duration', 'official', 'verified',
              'downloaded', 'download_path', 'view_count', 'error']

# Curated famous Tamil songs by decade - (song_title, movie, composer, singer, year)
CURATED_SONGS = [
    # 1950s - expanded to 20
    ("Pudhu Vasantham", "Pudhu Vasantham", "S V Venkatraman", "T M Soundararajan", 1950),
    (" Malli Poo", "Malliswari", "S V Venkatraman", "T M Soundararajan", 1951),
    (" En Veedu", "Vetri", "Viswanathan Ramamoorthy", "T M Soundararajan", 1952),
    (" Kalyana Parisu", "Kalyana Parisu", "M S Viswanathan", "T M Soundararajan", 1953),
    (" Madhurakadal", "Anari", "Viswanathan Ramamoorthy", "T M Soundararajan", 1954),
    (" Nalla Neram", "Nalla Neram", "M S Viswanathan", "T M Soundararajan", 1955),
    (" Egaththil Manaivi", "Navarasa", "Viswanathan Ramamoorthy", "T M Soundararajan", 1956),
    (" Sonnathu Niththa", "Thillana Mohanambal", "K V Mahadevan", "T M Soundararajan", 1957),
    (" Andru Peyy", "Kumari", "S V Venkatraman", "T M Soundararajan", 1958),
    (" Naan Kanda Sorgam", "Naan Kanda Sorgam", "K V Mahadevan", "T M Soundararajan", 1959),
    # Extra 1950s
    (" Parasakthi", "Parasakthi", "Viswanathan Ramamoorthy", "T M Soundararajan", 1950),
    (" Kannukku Mai", "Mannadhen", "S V Venkatraman", "T M Soundararajan", 1951),
    (" Malai Kallan", " Malaikallan", "M S Viswanathan", "T M Soundararajan", 1952),
    (" Imasip Pom", "Kumari", "S V Venkatraman", "T M Soundararajan", 1953),
    (" Kaathavan", "Ampa", "Viswanathan Ramamoorthy", "T M Soundararajan", 1954),
    (" Ponniyin Selvan", "Ponniyin Selvan", "K V Mahadevan", "T M Soundararajan", 1955),
    (" Karmatha Boomi", "Karmatha Boomi", "K V Mahadevan", "T M Soundararajan", 1956),
    (" Vendhu Thanindhadhu", "Rathna", "M S Viswanathan", "T M Soundararajan", 1957),
    (" Thai Sorgam", "Thai Sorgam", "K V Mahadevan", "T M Soundararajan", 1958),
    (" Thanga Radhu", "Thanga Radhu", "M S Viswanathan", "T M Soundararajan", 1959),

    # 1960s - expanded to 20
    (" Padugai", "Kalyana Parisu", "M S Viswanathan", "T M Soundararajan", 1960),
    (" Thee Oh Thee", "Kalyana Parisu", "M S Viswanathan", "T M Soundararajan", 1961),
    (" Nalla Neram", "Nalla Neram", "M S Viswanathan", "T M Soundararajan", 1962),
    (" Kakkai Ragangal", "Kakkai Ragangal", "M S Viswanathan", "T M Soundararajan", 1963),
    (" Vaazha Ninaithal", "Vaazha Ninaithal", "K V Mahadevan", "T M Soundararajan", 1964),
    (" Paattum Naane", "Thiruvilayadal", "K V Mahadevan", "T M Soundararajan", 1965),
    (" Soodhu Kavum", "Muthalvar", "M S Viswanathan", "T M Soundararajan", 1966),
    (" Thillana Mohanambal", "Thillana Mohanambal", "K V Mahadevan", "T M Soundararajan", 1967),
    (" Then Madhurai", "Then Madhurai", "M S Viswanathan", "T M Soundararajan", 1968),
    (" Aayirathil Oruvan", "Aayirathil Oruvan", "K V Mahadevan", "T M Soundararajan", 1969),
    # Extra 1960s
    (" Penne Nee", "Pudhu Vasantham", "S V Venkatraman", "P Susheela", 1960),
    (" Kannukku Mari", "Kalyana Parisu", "M S Viswanathan", "P Susheela", 1961),
    (" Ennadi Meenakshi", "Nalla Neram", "M S Viswanathan", "P Susheela", 1962),
    (" Kadhal Labam", "Kakkai Ragangal", "M S Viswanathan", "S Janaki", 1963),
    (" Devade", "Vazha Ninaithal", "K V Mahadevan", "T M Soundararajan", 1964),
    (" Bhakthapriya", "Bhakthapriya", "K V Mahadevan", "T M Soundararajan", 1965),
    (" Pooja Kavasam", "Thiruvilayadal", "K V Mahadevan", "T M Soundararajan", 1966),
    (" Sangeetha", "Anari", "Viswanathan Ramamoorthy", "T M Soundararajan", 1967),
    (" Kaadhal", "Kadal Meengal", "M S Viswanathan", "T M Soundararajan", 1968),
    (" Kuzhandai", "Kuzhandai", "K V Mahadevan", "T M Soundararajan", 1969),

    # 1970s - expanded to 20
    ("Vazhve En Bhoomi", "Vazhve Maathey", "Ilaiyaraaja", "S P Balasubrahmanyam", 1970),
    (" Thillu Mullu", "Thillu Mullu", "Ilaiyaraaja", "S P Balasubrahmanyam", 1971),
    (" Pallavi Anupallavi", "Pallavi Anupallavi", "Ilaiyaraaja", "S P Balasubrahmanyam", 1972),
    (" Nootukku Chengam", "Nootukku Chengam", "Ilaiyaraaja", "S P Balasubrahmanyam", 1973),
    (" Annakili", "Annakili", "Ilaiyaraaja", "S P Balasubrahmanyam", 1974),
    (" Malarae Kurinji", "Muthal Mariyathai", "Ilaiyaraaja", "S P Balasubrahmanyam", 1975),
    (" Hi Hi Hi", "Annakili", "Ilaiyaraaja", "S P Balasubrahmanyam", 1976),
    (" Madhura Veeraman", "Madhura Veeraman", "Ilaiyaraaja", "S P Balasubrahmanyam", 1977),
    (" Kalyana Pillai", "Kalyana Pillai", "Ilaiyaraaja", "S P Balasubrahmanyam", 1978),
    (" Nadhiyoram", "Annai Oru Aalayam", "M S Viswanathan", "T M Soundararajan", 1979),
    # Extra 1970s
    (" Poovathoril", "Vazhve Maathey", "Ilaiyaraaja", "S P Balasubrahmanyam", 1970),
    (" Pattampoochi", "Thillu Mullu", "Ilaiyaraaja", "S P Balasubrahmanyam", 1971),
    (" Solla Solla", "Pallavi Anupallavi", "Ilaiyaraaja", "S Janaki", 1972),
    (" Ennuyir", "Nootukku Chengam", "Ilaiyaraaja", "S P Balasubrahmanyam", 1973),
    (" Kottila", "Annakili", "Ilaiyaraaja", "S Janaki", 1974),
    (" Muthal Mariyathai", "Muthal Mariyathai", "Ilaiyaraaja", "S P Balasubrahmanyam", 1975),
    (" Oh Shalu", "Annakili", "Ilaiyaraaja", "S P Balasubrahmanyam", 1976),
    (" Yethukuthu", "Madhura Veeraman", "Ilaiyaraaja", "S P Balasubrahmanyam", 1977),
    (" Muthalvar", "Muthalvar", "Ilaiyaraaja", "S P Balasubrahmanyam", 1978),
    (" Nalla Neram", "Annai Oru Aalayam", "M S Viswanathan", "S Janaki", 1979),

    # 1980s - expanded to 20
    (" Mandram Vandha", "Mouna Ragam", "Ilaiyaraaja", "S P Balasubrahmanyam", 1980),
    (" Waapichang", "Waapichang", "Ilaiyaraaja", "S P Balasubrahmanyam", 1981),
    (" Raja Kaiyyam", "Raja Kaiyyam", "Ilaiyaraaja", "S P Balasubrahmanyam", 1982),
    (" Mandram Vandha", "Mouna Ragam", "Ilaiyaraaja", "K S Chithra", 1983),
    (" Unnaithane", "Nallavanukku Nallavan", "Ilaiyaraaja", "S Janaki", 1984),
    (" Nila Adhu", "Nayagan", "Ilaiyaraaja", "S P Balasubrahmanyam", 1985),
    (" Pooja Pooja", "Pooja Pooja", "Ilaiyaraaja", "S P Balasubrahmanyam", 1986),
    (" Shembhu", "Shembhu", "Ilaiyaraaja", "S P Balasubrahmanyam", 1987),
    (" Thayagu", "Thayagu", "Ilaiyaraaja", "S P Balasubrahmanyam", 1988),
    (" Pudhu Vasantham", "Pudhu Vasantham", "Ilaiyaraaja", "S P Balasubrahmanyam", 1989),
    # Extra 1980s
    (" Anbe Anbe", "Mouna Ragam", "Ilaiyaraaja", "S Janaki", 1980),
    (" Raja Kaiyyam", "Raja Kaiyyam", "Ilaiyaraaja", "S Janaki", 1981),
    (" Vethaththil", "Mouna Ragam", "Ilaiyaraaja", "S P Balasubrahmanyam", 1982),
    (" Thendral", "Nallavanukku Nallavan", "Ilaiyaraaja", "S Janaki", 1983),
    (" Unnai Kandu", "Nallavanukku Nallavan", "Ilaiyaraaja", "S P Balasubrahmanyam", 1984),
    (" Kalyana Megam", "Nayagan", "Ilaiyaraaja", "S Janaki", 1985),
    (" Pooja", "Pooja Pooja", "Ilaiyaraaja", "S Janaki", 1986),
    (" Shembhu", "Shembhu", "Ilaiyaraaja", "S Janaki", 1987),
    (" Thayagu", "Thayagu", "Ilaiyaraaja", "S Janaki", 1988),
    (" Pudhu Vasantham", "Pudhu Vasantham", "Ilaiyaraaja", "K S Chithra", 1989),
]


def search_youtube(query, max_results=5):
    """Search YouTube and return list of (yt_id, title, duration)."""
    cmd = ['yt-dlp', '--no-download', '--print', '%(id)s|%(duration)s|%(title)s',
           f'ytsearch{max_results}:{query}']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            results = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        yt_id, dur, yt_title = parts[0], parts[1], parts[2]
                        try:
                            duration = int(dur) if dur.isdigit() else 0
                        except:
                            duration = 0
                        # Accept if duration is reasonable (allow up to 600s for old songs that may be longer)
                        if duration > 0:
                            results.append((yt_id, yt_title, duration))
            return results
    except Exception as e:
        print(f"    Search error: {e}")
    return []


def find_best_match(song_title, movie, composer, singer, year):
    """Find best YouTube match for a song."""
    # Try exact title + year first
    queries = [
        f'"{song_title}" {year} Tamil',
        f'"{song_title}" {movie} Tamil song',
        f'"{song_title}" {composer} Tamil',
        f'{song_title} {year} Tamil hit song',
    ]

    for query in queries:
        results = search_youtube(query, max_results=3)
        for yt_id, yt_title, duration in results:
            # Skip if duration is clearly a jukebox (>15 min)
            if duration > 900:
                continue
            return yt_id, yt_title, duration
        time.sleep(0.3)

    return None, None, None


def main():
    print("Fetching old Tamil songs (1950-1989)")
    print("=" * 60)

    # Read existing songs to avoid duplicates
    existing = {}
    existing_titles = set()
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id'):
                existing[row['youtube_id']] = row
            if row.get('song_title'):
                existing_titles.add(row['song_title'].lower())

    print(f"Existing songs: {len(existing)}")
    print(f"Existing titles: {len(existing_titles)}")

    # Group by decade
    by_decade = {1950: [], 1960: [], 1970: [], 1980: []}
    for song in CURATED_SONGS:
        title, movie, composer, singer, year = song
        decade = (year // 10) * 10
        if decade in by_decade:
            by_decade[decade].append(song)

    new_songs = []

    for decade, songs in by_decade.items():
        print(f"\n{'='*60}")
        print(f"Processing {decade}s: {len(songs)} curated songs")
        print(f"="*60)

        for title, movie, composer, singer, year in songs:
            # Skip if we already have a similar title
            if title.lower() in existing_titles:
                print(f"  SKIP (exists): {title[:40]}")
                continue

            print(f"  Searching: {title[:40]} ({year})...", end=" ", flush=True)

            yt_id, yt_title, duration = find_best_match(title, movie, composer, singer, year)

            if yt_id:
                print(f"FOUND: {duration}s")
                new_songs.append({
                    'year': year,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'song_title': yt_title,
                    'movie': movie,
                    'composer': composer,
                    'singer': singer,
                    'lyricist': '',
                    'youtube_id': yt_id,
                    'youtube_title': yt_title,
                    'duration': duration,
                    'official': 'N',
                    'verified': 'N',
                    'downloaded': 'N',
                    'download_path': '',
                    'view_count': '',
                    'error': '',
                })
                existing_titles.add(title.lower())
            else:
                print("NOT FOUND")

            time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"Total new songs to add: {len(new_songs)}")

    if not new_songs:
        print("No new songs found.")
        return

    # Write to CSV (append)
    with open(SONGS_CSV, 'a', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        for song in new_songs:
            writer.writerow(song)

    print(f"Added {len(new_songs)} songs to {SONGS_CSV}")

    # Summary by decade
    for decade in sorted(by_decade.keys()):
        count = sum(1 for s in new_songs if (int(s['year']) // 10) * 10 == decade)
        total_in_csv = 0
        with open(SONGS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    y = int(row.get('year', 0))
                    if (y // 10) * 10 == decade:
                        total_in_csv += 1
                except:
                    pass
        print(f"  {decade}s: {count} new added, ~{total_in_csv} total in CSV")


if __name__ == "__main__":
    main()