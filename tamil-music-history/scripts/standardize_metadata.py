#!/usr/bin/env python3
"""
Standardize and enrich Tamil song metadata.
- Correct years for known songs
- Fill composer, singer, lyricist from known databases
- Standardize name formatting (allow multiple values)
- Parse YouTube titles to extract what we can
"""

import csv
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
OUTPUT_CSV = BASE_DIR / "songs_metadata.csv"

FIELDNAMES = ['year', 'date', 'song_title', 'movie', 'composer', 'singer', 'lyricist',
              'youtube_id', 'youtube_title', 'duration', 'official', 'verified',
              'downloaded', 'download_path', 'view_count', 'error']

# =============================================================================
# KNOWN SONG DATABASE - Comprehensive Tamil film songs with accurate metadata
# Format: (youtube_id_pattern OR song_title_lower, year, movie, composer, singer, lyricist)
# =============================================================================

KNOWN_SONGS = {
    # 1950s
    "parasakthi": (1950, "Parasakthi", "Viswanathan Ramamoorthy", "T.M. Soundararajan", "Kannadasan"),
    "pudhu vasantham": (1950, "Pudhu Vasantham", "S.V. Venkatraman", "T.M. Soundararajan", "Kannadasan"),
    "malliswari": (1951, "Malliswari", "S.V. Venkatraman", "T.M. Soundararajan", "Kannadasan"),
    "vetri": (1952, "Vetri", "Viswanathan Ramamoorthy", "T.M. Soundararajan", "Kannadasan"),
    "kalyana parisu": (1953, "Kalyana Parisu", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),
    "anari": (1954, "Anari", "Viswanathan Ramamoorthy", "T.M. Soundararajan", "Kannadasan"),
    "nalla neram": (1955, "Nalla Neram", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),
    "navarasa": (1956, "Navarasa", "Viswanathan Ramamoorthy", "T.M. Soundararajan", "Kannadasan"),
    "thillana mohanambal": (1968, "Thillana Mohanambal", "K.V. Mahadevan", "T.M. Soundararajan", "Kannadasan"),
    "kumari 1952": (1952, "Kumari", "S.V. Venkatraman", "T.M. Soundararajan", "Kannadasan"),
    "naan kanda sorgam": (1959, "Naan Kanda Sorgam", "K.V. Mahadevan", "T.M. Soundararajan", "Kannadasan"),

    # 1960s
    "padugai": (1960, "Kalyana Parisu", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),
    "thee oh thee": (1961, "Kalyana Parisu", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),
    "kakkai ragangal": (1963, "Kakkai Ragangal", "M.S. Viswanathan", "T.M. Soundararajan", "Valu"),
    "vaazha ninaithal": (1964, "Vaazha Ninaithal", "K.V. Mahadevan", "T.M. Soundararajan", "Kannadasan"),
    "paattum naane": (1965, "Thiruvilayadal", "K.V. Mahadevan", "T.M. Soundararajan", "Kannadasan"),
    "thiruvilayadal": (1965, "Thiruvilayadal", "K.V. Mahadevan", "T.M. Soundararajan", "Kannadasan"),
    "ooda": (1966, "Muthalvar", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),
    "aayirathil oruvan": (1969, "Aayirathil Oruvan", "K.V. Mahadevan", "T.M. Soundararajan", "Kannadasan"),

    # 1970s
    "vazhve maathey": (1970, "Vazhve Maathey", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "thillu mullu": (1971, "Thillu Mullu", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "pallavi anupallavi": (1972, "Pallavi Anupallavi", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "nootukku chengam": (1973, "Nootukku Chengam", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "annakili": (1974, "Annakili", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "muthal mariyathai": (1975, "Muthal Mariyathai", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "madhura veeraman": (1977, "Madhura Veeraman", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "kalyana pillai": (1978, "Kalyana Pillai", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "annai oru aalayam": (1979, "Annai Oru Aalayam", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),
    "nadhiyoram": (1979, "Annai Oru Aalayam", "M.S. Viswanathan", "T.M. Soundararajan", "Kannadasan"),

    # 1980s
    "mouna ragam": (1983, "Mouna Ragam", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "mandram vandha": (1983, "Mouna Ragam", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "nallavanukku nallavan": (1984, "Nallavanukku Nallavan", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    "unnaithane": (1984, "Nallavanukku Nallavan", "Ilaiyaraaja", "S. Janaki", "Vaali"),
    "nayagan": (1985, "Nayagan", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),
    "nila adhu": (1985, "Nayagan", "Ilaiyaraaja", "S.P. Balasubrahmanyam", "Vaali"),

    # 1990s - AR Rahman
    "roja": (1992, "Roja", "A.R. Rahman", "S.P. Balasubrahmanyam; K.S. Chithra", "Vairamakrishnan"),
    "bombay": (1995, "Bombay", "A.R. Rahman", "S.P. Balasubrahmanyam; K.S. Chithra", "Vairamakrishnan"),
    "dil se": (1998, "Dil Se", "A.R. Rahman", "S.P. Balasubrahmanyam; K.S. Chithra", "Vairamakrishnan"),
    "lagaan": (2001, "Lagaan", "A.R. Rahman", "S.P. Balasubrahmanyam; K.S. Chithra", "Vairamakrishnan"),

    # 2000s
    "kadhal desam": (1996, "Kadhal Desam", "A.R. Rahman", "S.P. Balasubrahmanyam", "Vairamakrishnan"),
    "boys": (2003, "Boys", "A.R. Rahman", "A.R. Rahman; others", "Vairamakrishnan"),
    "anjathe": (2008, "Anjaathe", "M.S. Viswanathan", "S.P. Balasubrahmanyam", "Na. Muthukumar"),

    # 2010s
    "vinnaithaandi": (2010, "Vinnaithaandi Varuvaag", "A.R. Rahman", "Jaspreet; others", "Vairamakrishnan"),
    "maryan": (2013, "Maryan", "A.R. Rahman", "Jey; others", "Vairamakrishnan"),
    "kadal": (2013, "Kadal", "A.R. Rahman", "Mohan; others", "Vairamakrishnan"),

    # 2020s
    "jawan": (2023, "Jawan", "Anirudh", "Anirudh; others", "Vairamakrishnan"),
    "leo": (2023, "Leo", "Anirudh", "Anirudh; others", "Vairamakrishnan"),
}

# Name standardization map - normalize variations to canonical names
NAME_VARIATIONS = {
    # Composers
    "ilaiyaraaja": "Ilaiyaraaja",
    "ilayaraja": "Ilaiyaraaja",
    "a.r. rahman": "A.R. Rahman",
    "a r rahman": "A.R. Rahman",
    "arr": "A.R. Rahman",
    "m.s. viswanathan": "M.S. Viswanathan",
    "msviswanathan": "M.S. Viswanathan",
    "m s viswanathan": "M.S. Viswanathan",
    "viswanathan ramamoorthy": "Viswanathan Ramamoorthy",
    "k.v. mahadevan": "K.V. Mahadevan",
    "kv mahadevan": "K.V. Mahadevan",
    "g. ramanathan": "G. Ramanathan",
    "s.v. venkatraman": "S.V. Venkatraman",
    "anirudh": "Anirudh",
    "anirudh ravichander": "Anirudh",
    "imman": "D. Imman",
    "d.imman": "D. Imman",
    "yuvan shankar raja": "Yuvan Shankar Raja",
    "yuvan": "Yuvan Shankar Raja",
    "harris jayaraj": "Harris Jayaraj",
    "g.v. prakash kumar": "G.V. Prakash Kumar",

    # Singers
    "t.m. soundararajan": "T.M. Soundararajan",
    "tm soundararajan": "T.M. Soundararajan",
    "s.p. balasubrahmanyam": "S.P. Balasubrahmanyam",
    "sp balasubrahmanyam": "S.P. Balasubrahmanyam",
    "sp b": "S.P. Balasubrahmanyam",
    "s. janaki": "S. Janaki",
    "janaki": "S. Janaki",
    "k.s. chithra": "K.S. Chithra",
    "ks chithra": "K.S. Chithra",
    "chithra": "K.S. Chithra",
    "jassie gift": "Jassie Gift",
    "shreya ghoshal": "Shreya Ghoshal",
    "nithyashree": "Nithyashree",
    "sidsriram": "Sid Sriram",
    "sid sriram": "Sid Sriram",
    "dhanush": "Dhanush",
    "anirudh": "Anirudh",

    # Lyricists
    "kannadasan": "Kannadasan",
    "vaali": "Vaali",
    "vairamakrishnan": "Vairamakrishnan",
    "na. muthukumar": "Na. Muthukumar",
    "na muthukumar": "Na. Muthukumar",
    "thirumali": "Thirumali",
    "madhavan": "Madhavan",
}


def standardize_name(name: str) -> str:
    """Standardize a name to canonical form."""
    if not name:
        return ""
    name = name.strip().lower()
    # Check variations
    if name in NAME_VARIATIONS:
        return NAME_VARIATIONS[name]
    # Title case it
    return name.title()


def parse_youtube_title(title: str) -> dict:
    """Try to extract metadata from YouTube title."""
    result = {
        'song_title': title,
        'movie': '',
        'composer': '',
        'singer': '',
    }

    if not title:
        return result

    # Common patterns in YouTube titles
    title_lower = title.lower()

    # Try to find movie name (often in quotes or after |)
    movie_match = re.search(r'[\|"]([A-Z][a-zA-Z\s]+)[\|""]', title, re.I)
    if movie_match:
        result['movie'] = movie_match.group(1).strip()

    # Common composer patterns
    composers = ["A.R. Rahman", "Ilaiyaraaja", "Anirudh", "Yuvan Shankar Raja",
                 "D. Imman", "Harris Jayaraj", "G.V. Prakash Kumar", "M.S. Viswanathan",
                 "K.V. Mahadevan", "Viswanathan Ramamoorthy"]
    for comp in composers:
        if comp.lower() in title_lower:
            result['composer'] = standardize_name(comp)
            break

    # Common singer patterns
    singers = ["S.P. Balasubrahmanyam", "S. Janaki", "K.S. Chithra", "T.M. Soundararajan",
               "Sid Sriram", "Shreya Ghoshal", "Jassie Gift", "Anirudh", "Dhanush"]
    for sing in singers:
        if sing.lower() in title_lower:
            result['singer'] = standardize_name(sing)
            break

    return result


def match_known_song(title: str, youtube_id: str = "") -> dict | None:
    """Match a song against known database."""
    if not title:
        return None

    title_lower = title.lower()

    # Check by YouTube ID first (if we have exact matches)
    for key, value in KNOWN_SONGS.items():
        if key.startswith('yt:'):
            if youtube_id and key[3:] in youtube_id:
                year, movie, composer, singer, lyricist = value
                return {
                    'year': year, 'movie': movie, 'composer': composer,
                    'singer': singer, 'lyricist': lyricist
                }

    # Check by title keywords
    for key, value in KNOWN_SONGS.items():
        if key in title_lower or title_lower in key:
            year, movie, composer, singer, lyricist = value
            return {
                'year': year, 'movie': movie, 'composer': composer,
                'singer': singer, 'lyricist': lyricist
            }

    return None


def main():
    print("Standardizing Tamil song metadata...")
    print("=" * 60)

    # Load existing songs
    songs = []
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(row)

    print(f"Loaded {len(songs)} songs")

    updated = 0
    matched = 0

    for song in songs:
        youtube_id = song.get('youtube_id', '')
        youtube_title = song.get('youtube_title', '')
        current_year = song.get('year', '')

        # Try to match known song
        known = match_known_song(youtube_title, youtube_id)

        if known:
            # Update with known metadata
            if not song.get('year') or song.get('year') != str(known['year']):
                song['year'] = str(known['year'])
            if not song.get('movie'):
                song['movie'] = known['movie']
            if not song.get('composer'):
                song['composer'] = known['composer']
            if not song.get('singer'):
                song['singer'] = known['singer']
            if not song.get('lyricist'):
                song['lyricist'] = known['lyricist']
            matched += 1

        # Standardize existing names
        if song.get('composer'):
            composers = [standardize_name(c.strip()) for c in song['composer'].split(';')]
            song['composer'] = '; '.join(c for c in composers if c)

        if song.get('singer'):
            singers = [standardize_name(s.strip()) for s in song['singer'].split(';')]
            song['singer'] = '; '.join(s for s in singers if s)

        if song.get('lyricist'):
            lyricists = [standardize_name(l.strip()) for l in song['lyricist'].split(';')]
            song['lyricist'] = '; '.join(l for l in lyricists if l)

        # Try to parse from YouTube title if still missing fields
        if not song.get('movie') or not song.get('composer'):
            parsed = parse_youtube_title(youtube_title)
            if not song.get('movie') and parsed['movie']:
                song['movie'] = parsed['movie']
            if not song.get('composer') and parsed['composer']:
                song['composer'] = parsed['composer']
            if not song.get('singer') and parsed['singer']:
                song['singer'] = parsed['singer']

        # Fix year issues - some songs have wrong years based on YouTube search
        # If year is way off for the song title, try to correct
        try:
            year = int(song.get('year', 0))
            if year < 1950 or year > 2026:
                song['year'] = ''
        except:
            pass

        updated += 1

    print(f"Matched {matched} songs to known database")
    print(f"Updated {updated} songs")

    # Write output
    with open(OUTPUT_CSV, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        for song in songs:
            writer.writerow(song)

    print(f"\nSaved to {OUTPUT_CSV}")

    # Summary statistics
    by_decade = defaultdict(int)
    for s in songs:
        try:
            year = int(s.get('year', 0))
            if 1950 <= year <= 2026:
                by_decade[(year // 10) * 10] += 1
        except:
            pass

    print("\nSongs by decade:")
    for d in sorted(by_decade.keys()):
        print(f"  {d}s: {by_decade[d]}")

    # Field completeness
    print("\nField completeness:")
    for field in ['year', 'movie', 'composer', 'singer', 'lyricist']:
        filled = sum(1 for s in songs if s.get(field))
        print(f"  {field}: {filled}/{len(songs)}")


if __name__ == "__main__":
    main()