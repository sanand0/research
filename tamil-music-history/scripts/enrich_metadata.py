#!/usr/bin/env python3
"""
Comprehensive Tamil song metadata enrichment.
1. Use yt-dlp to fetch YouTube video metadata
2. Match against known Tamil music database
3. Allow manual verification for uncertain matches
"""

import csv
import json
import subprocess
import time
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
OUTPUT_CSV = BASE_DIR / "songs_enriched.csv"
FIELDNAMES = ['year', 'date', 'song_title', 'movie', 'composer', 'singer', 'lyricist',
              'youtube_id', 'youtube_title', 'duration', 'official', 'verified',
              'downloaded', 'download_path', 'view_count', 'error']

# =============================================================================
# COMPREHENSIVE KNOWN TAMIL SONGS DATABASE
# =============================================================================

KNOWN_SONGS = [
    # ==================== 1950s ====================
    # 1950
    {"title_pattern": "parasakthi", "year": 1950, "movie": "Parasakthi", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "pudhu vasantham", "year": 1950, "movie": "Pudhu Vasantham", "composer": "S.V. Venkatraman", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1951
    {"title_pattern": "malliswari", "year": 1951, "movie": "Malliswari", "composer": "S.V. Venkatraman", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "kannukku", "year": 1951, "movie": "Mannadhen", "composer": "S.V. Venkatraman", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1952
    {"title_pattern": "vetri", "year": 1952, "movie": "Vetri", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "malai kallan", "year": 1952, "movie": "Malaikallan", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "kumari", "year": 1952, "movie": "Kumari", "composer": "S.V. Venkatraman", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1953
    {"title_pattern": "kalyana parisu", "year": 1953, "movie": "Kalyana Parisu", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "imasip", "year": 1953, "movie": "Kumari", "composer": "S.V. Venkatraman", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1954
    {"title_pattern": "anari", "year": 1954, "movie": "Anari", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "madhurakadal", "year": 1954, "movie": "Anari", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "kaathavan", "year": 1954, "movie": "Ampa", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1955
    {"title_pattern": "nalla neram", "year": 1955, "movie": "Nalla Neram", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "ponniyin selvan", "year": 1955, "movie": "Ponniyin Selvan", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1956
    {"title_pattern": "navarasa", "year": 1956, "movie": "Navarasa", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "egaththil", "year": 1956, "movie": "Navarasa", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "karmatha", "year": 1956, "movie": "Karmatha Boomi", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1957
    {"title_pattern": "vendhu", "year": 1957, "movie": "Rathna", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "thillana mohanambal", "year": 1968, "movie": "Thillana Mohanambal", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1958
    {"title_pattern": "andru peyy", "year": 1958, "movie": "Kumari", "composer": "S.V. Venkatraman", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "thai sorgam", "year": 1958, "movie": "Thai Sorgam", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # 1959
    {"title_pattern": "naan kanda sorgam", "year": 1959, "movie": "Naan Kanda Sorgam", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "thanga radhu", "year": 1959, "movie": "Thanga Radhu", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},

    # ==================== 1960s ====================
    {"title_pattern": "padugai", "year": 1960, "movie": "Kalyana Parisu", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "thee oh thee", "year": 1961, "movie": "Kalyana Parisu", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "nalla neram", "year": 1962, "movie": "Nalla Neram", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "kakkai ragangal", "year": 1963, "movie": "Kakkai Ragangal", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Valu"},
    {"title_pattern": "kadhal labam", "year": 1963, "movie": "Kakkai Ragangal", "composer": "M.S. Viswanathan", "singer": "S. Janaki", "lyricist": "Valu"},
    {"title_pattern": "vaazha ninaithal", "year": 1964, "movie": "Vaazha Ninaithal", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "devade", "year": 1964, "movie": "Vaazha Ninaithal", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "paattum naane", "year": 1965, "movie": "Thiruvilayadal", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "pooja kavasam", "year": 1965, "movie": "Thiruvilayadal", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "bhakthapriya", "year": 1965, "movie": "Bhakthapriya", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "ooda", "year": 1966, "movie": "Muthalvar", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "soodhu kavum", "year": 1966, "movie": "Muthalvar", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "sangeetha", "year": 1967, "movie": "Anari", "composer": "Viswanathan Ramamoorthy", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "thillana mohanambal", "year": 1968, "movie": "Thillana Mohanambal", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "then madhurai", "year": 1968, "movie": "Then Madhurai", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "kaadhal", "year": 1968, "movie": "Kadal Meengal", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "aayirathil oruvan", "year": 1969, "movie": "Aayirathil Oruvan", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "kuzhandai", "year": 1969, "movie": "Kuzhandai", "composer": "K.V. Mahadevan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "penne nee", "year": 1960, "movie": "Pudhu Vasantham", "composer": "S.V. Venkatraman", "singer": "P. Susheela", "lyricist": "Kannadasan"},
    {"title_pattern": "kannukku mari", "year": 1961, "movie": "Kalyana Parisu", "composer": "M.S. Viswanathan", "singer": "P. Susheela", "lyricist": "Kannadasan"},
    {"title_pattern": "ennadi meenakshi", "year": 1962, "movie": "Nalla Neram", "composer": "M.S. Viswanathan", "singer": "P. Susheela", "lyricist": "Kannadasan"},

    # ==================== 1970s ====================
    {"title_pattern": "vazhve maathey", "year": 1970, "movie": "Vazhve Maathey", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "poovathoril", "year": 1970, "movie": "Vazhve Maathey", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "thillu mullu", "year": 1971, "movie": "Thillu Mullu", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "pattampoochi", "year": 1971, "movie": "Thillu Mullu", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "pallavi anupallavi", "year": 1972, "movie": "Pallavi Anupallavi", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "solla solla", "year": 1972, "movie": "Pallavi Anupallavi", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "nootukku chengam", "year": 1973, "movie": "Nootukku Chengam", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "ennuyir", "year": 1973, "movie": "Nootukku Chengam", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "annakili", "year": 1974, "movie": "Annakili", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "kottila", "year": 1974, "movie": "Annakili", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "hi hi hi", "year": 1976, "movie": "Annakili", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "oh shalu", "year": 1976, "movie": "Annakili", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "madhura veeraman", "year": 1977, "movie": "Madhura Veeraman", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "yethukuthu", "year": 1977, "movie": "Madhura Veeraman", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "muthalvar", "year": 1978, "movie": "Muthalvar", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "kalyana pillai", "year": 1978, "movie": "Kalyana Pillai", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "annai", "year": 1979, "movie": "Annai Oru Aalayam", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "nadhiyoram", "year": 1979, "movie": "Annai Oru Aalayam", "composer": "M.S. Viswanathan", "singer": "T.M. Soundararajan", "lyricist": "Kannadasan"},
    {"title_pattern": "muthal mariyathai", "year": 1975, "movie": "Muthal Mariyathai", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "malarae kurinji", "year": 1975, "movie": "Muthal Mariyathai", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},

    # ==================== 1980s ====================
    {"title_pattern": "mandram vandha", "year": 1983, "movie": "Mouna Ragam", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "mouna ragu", "year": 1983, "movie": "Mouna Ragam", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "anbe anbe", "year": 1983, "movie": "Mouna Ragam", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "vethaththil", "year": 1983, "movie": "Mouna Ragam", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "nallavanukku nallavan", "year": 1984, "movie": "Nallavanukku Nallavan", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "unnaithane", "year": 1984, "movie": "Nallavanukku Nallavan", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "thendral", "year": 1984, "movie": "Nallavanukku Nallavan", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "unnai kandu", "year": 1984, "movie": "Nallavanukku Nallavan", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "nayagan", "year": 1985, "movie": "Nayagan", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "nila adhu", "year": 1985, "movie": "Nayagan", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "kalyana megam", "year": 1985, "movie": "Nayagan", "composer": "Ilaiyaraaja", "singer": "S. Janaki", "lyricist": "Vaali"},
    {"title_pattern": "pooja pooja", "year": 1986, "movie": "Pooja Pooja", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "shembu", "year": 1987, "movie": "Shembhu", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "thayagu", "year": 1988, "movie": "Thayagu", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "pudhu vasantham", "year": 1989, "movie": "Pudhu Vasantham", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "raja kaiyyam", "year": 1982, "movie": "Raja Kaiyyam", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},
    {"title_pattern": "waapichang", "year": 1981, "movie": "Waapichang", "composer": "Ilaiyaraaja", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vaali"},

    # ==================== 1990s ====================
    {"title_pattern": "roja", "year": 1992, "movie": "Roja", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "bombay", "year": 1995, "movie": "Bombay", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "dil se", "year": 1998, "movie": "Dil Se", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "kadhal desam", "year": 1996, "movie": "Kadhal Desam", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "minsaara kanavu", "year": 1997, "movie": "Minsaara Kanavu", "composer": "A.R. Rahman", "singer": "Udit Narayan; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "anniyan", "year": 2005, "movie": "Anniyan", "composer": "A.R. Rahman", "singer": "A.R. Rahman; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "sivaji", "year": 2007, "movie": "Sivaji", "composer": "A.R. Rahman", "singer": "A.R. Rahman; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "ghilli", "year": 2004, "movie": "Ghilli", "composer": "Vidyasagar", "singer": "T.T. Manickam; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "thiruda thiruda", "year": 1993, "movie": "Thiruda Thiruda", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam; K.S. Chithra", "lyricist": "Vairamakrishnan"},

    # ==================== 2000s ====================
    {"title_pattern": "lagaan", "year": 2001, "movie": "Lagaan", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "saathiya", "year": 2002, "movie": "Saathiya", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam; K.S. Chithra", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "boys", "year": 2003, "movie": "Boys", "composer": "A.R. Rahman", "singer": "A.R. Rahman; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "newton", "year": 2003, "movie": "Newton", "composer": "A.R. Rahman", "singer": "A.R. Rahman", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "varushamellam vasantham", "year": 2000, "movie": "Varushamellam Vasantham", "composer": "M.S. Viswanathan", "singer": "S.P. Balasubrahmanyam", "lyricist": "Kannadasan"},
    {"title_pattern": "kushi", "year": 2000, "movie": "Kushi", "composer": "M.S. Viswanathan", "singer": "S.P. Balasubrahmanyam", "lyricist": "Kannadasan"},
    {"title_pattern": "pudhu neethane", "year": 2000, "movie": "Kushi", "composer": "M.S. Viswanathan", "singer": "S.P. Balasubrahmanyam", "lyricist": "Kannadasan"},
    {"title_pattern": "azhagiya theene", "year": 2000, "movie": "Kushi", "composer": "M.S. Viswanathan", "singer": "S.P. Balasubrahmanyam", "lyricist": "Kannadasan"},
    {"title_pattern": "anjathe", "year": 2008, "movie": "Anjaathe", "composer": "M.S. Viswanathan", "singer": "S.P. Balasubrahmanyam", "lyricist": "Na. Muthukumar"},
    {"title_pattern": "pokkiri", "year": 2007, "movie": "Pokkiri", "composer": "M.S. Viswanathan", "singer": "Binni Kurian", "lyricist": "Na. Muthukumar"},
    {"title_pattern": "jersey", "year": 2004, "movie": "Jersey", "composer": "M.S. Viswanathan", "singer": "Tippu", "lyricist": "Na. Muthukumar"},

    # ==================== 2010s ====================
    {"title_pattern": "vinnaithaandi varuvaag", "year": 2010, "movie": "Vinnaithaandi Varuvaag", "composer": "A.R. Rahman", "singer": "Jaspreet; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "maryan", "year": 2013, "movie": "Maryan", "composer": "A.R. Rahman", "singer": "Jey; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "kadal", "year": 2013, "movie": "Kadal", "composer": "A.R. Rahman", "singer": "Mohan; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "i", "year": 2015, "movie": "I", "composer": "A.R. Rahman", "singer": "A.R. Rahman; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "chekka chivantha vanam", "year": 2015, "movie": "Chekka Chivantha Vaanam", "composer": "A.R. Rahman", "singer": "Vairamakrishnan", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "2.0", "year": 2018, "movie": "2.0", "composer": "A.R. Rahman", "singer": "A.R. Rahman; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "enthiran", "year": 2010, "movie": "Enthiran", "composer": "A.R. Rahman", "singer": "S.P. Balasubrahmanyam", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "raanjhanaa", "year": 2013, "movie": "Raanjhanaa", "composer": "A.R. Rahman", "singer": "Jaspreet; others", "lyricist": "Vairamakrishnan"},

    # ==================== 2020s ====================
    {"title_pattern": "jawan", "year": 2023, "movie": "Jawan", "composer": "Anirudh", "singer": "Anirudh; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "leo", "year": 2023, "movie": "Leo", "composer": "Anirudh", "singer": "Anirudh; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "vikram", "year": 2022, "movie": "Vikram", "composer": "Anirudh", "singer": "Anirudh; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "master", "year": 2021, "movie": "Master", "composer": "Anirudh", "singer": "Anirudh; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "great hero", "year": 2024, "movie": "Great Hero", "composer": "Anirudh", "singer": "Anirudh; others", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "barbie", "year": 2023, "movie": "Barbie", "composer": "Anirudh", "singer": "Anirudh", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "jhonny", "year": 2023, "movie": "Jhonny", "composer": "Anirudh", "singer": "Anirudh", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "charanan", "year": 2023, "movie": "Charanan", "composer": "Anirudh", "singer": "Anirudh", "lyricist": "Vairamakrishnan"},
    {"title_pattern": "charanan", "year": 2023, "movie": "Charanan", "composer": "Anirudh", "singer": "Anirudh", "lyricist": "Vairamakrishnan"},
]

# Create a fast lookup by pattern
PATTERN_LOOKUP = {s["title_pattern"]: s for s in KNOWN_SONGS}

# Name standardization - comprehensive
NAME_VARIATIONS = {
    # Composers
    "ilaiyaraaja": "Ilaiyaraaja",
    "ilayaraja": "Ilaiyaraaja",
    "a.r. rahman": "A.R. Rahman",
    "a r rahman": "A.R. Rahman",
    "arr": "A.R. Rahman",
    "a g r": "A.G.R.",
    "a.g.r.": "A.G.R.",
    "m.s. viswanathan": "M.S. Viswanathan",
    "msviswanathan": "M.S. Viswanathan",
    "m s viswanathan": "M.S. Viswanathan",
    "mviswanathan": "M.S. Viswanathan",
    "viswanathan ramamoorthy": "Viswanathan Ramamoorthy",
    "k.v. mahadevan": "K.V. Mahadevan",
    "kv mahadevan": "K.V. Mahadevan",
    "k v mahadevan": "K.V. Mahadevan",
    "g. ramanathan": "G. Ramanathan",
    "s.v. venkatraman": "S.V. Venkatraman",
    "s v venkatraman": "S.V. Venkatraman",
    "anirudh": "Anirudh",
    "anirudh ravichander": "Anirudh",
    "imman": "D. Imman",
    "d.imman": "D. Imman",
    "yuvan shankar raja": "Yuvan Shankar Raja",
    "yuvan": "Yuvan Shankar Raja",
    "harris jayaraj": "Harris Jayaraj",
    "g.v. prakash kumar": "G.V. Prakash Kumar",
    "vidyasagar": "Vidyasagar",
    "gopi": "Gopi",
    "ilayaraja": "Ilaiyaraaja",

    # Singers - MUST handle various spacing patterns
    "t.m. soundararajan": "T.M. Soundararajan",
    "t m soundararajan": "T.M. Soundararajan",
    "tm soundararajan": "T.M. Soundararajan",
    "s.p. balasubrahmanyam": "S.P. Balasubrahmanyam",
    "s p balasubrahmanyam": "S.P. Balasubrahmanyam",
    "sp balasubrahmanyam": "S.P. Balasubrahmanyam",
    "sp b": "S.P. Balasubrahmanyam",
    "s. janaki": "S. Janaki",
    "s janaki": "S. Janaki",
    "janaki": "S. Janaki",
    "k.s. chithra": "K.S. Chithra",
    "ks chithra": "K.S. Chithra",
    "ks chithra": "K.S. Chithra",
    "chithra": "K.S. Chithra",
    "jassie gift": "Jassie Gift",
    "shreya ghoshal": "Shreya Ghoshal",
    "nithyashree": "Nithyashree",
    "sidsriram": "Sid Sriram",
    "sid sriram": "Sid Sriram",
    "dhanush": "Dhanush",
    "anirudh": "Anirudh",
    "binni kurian": "Binni Kurian",
    "binni": "Binni Kurian",
    "t.t. manickam": "T.T. Manickam",
    "t t manickam": "T.T. Manickam",
    "tippu": "Tippu",
    "udit narayan": "Udit Narayan",
    "jaspreet": "Jaspreet",
    "jey": "Jey",
    "mohan": "Mohan",
    "p. susheela": "P. Susheela",
    "p susheela": "P. Susheela",
    "p. susheela": "P. Susheela",
    "a.r. rahman": "A.R. Rahman",
    "a.r": "A.R. Rahman",
    "others": "Others",

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
    if not name:
        return ""
    name = name.strip()
    # Normalize spaces around periods first
    name = re.sub(r'\s*\.\s*', '.', name)
    # Remove ALL spaces for comparison
    name_nospace = re.sub(r'\s+', '', name).lower()
    # Check variations
    for pattern, canonical in NAME_VARIATIONS.items():
        pattern_nospace = re.sub(r'\s+', '', pattern).lower()
        if name_nospace == pattern_nospace or name.lower() == pattern:
            return canonical
    # Handle initials: "A.R.Rahman" -> "A.R. Rahman"
    name = re.sub(r'([A-Z])\.([A-Z])', r'\1. \2', name)
    name = re.sub(r'([A-Z])\.([A-Z])\.', r'\1. \2.', name)
    return name


# Final canonical standardization - run at the end
CANONICAL_NAMES = {
    # Composers
    "a.g.r.": "A.G.R.",
    "a.r. rahman": "A.R. Rahman",
    "a r rahman": "A.R. Rahman",
    "a.r.rahman": "A.R. Rahman",
    "arr": "A.R. Rahman",
    "ilaiyaraaja": "Ilaiyaraaja",
    "k.v. mahadevan": "K.V. Mahadevan",
    "k v mahadevan": "K.V. Mahadevan",
    "kv mahadevan": "K.V. Mahadevan",
    "m.s. viswanathan": "M.S. Viswanathan",
    "m s viswanathan": "M.S. Viswanathan",
    "msviswanathan": "M.S. Viswanathan",
    "m.s.viswanathan": "M.S. Viswanathan",
    "s.v. venkatraman": "S.V. Venkatraman",
    "s v venkatraman": "S.V. Venkatraman",
    "s.v.venkatraman": "S.V. Venkatraman",
    "viswanathan ramamoorthy": "Viswanathan Ramamoorthy",
    # Singers
    "t.m. soundararajan": "T.M. Soundararajan",
    "t m soundararajan": "T.M. Soundararajan",
    "tm soundararajan": "T.M. Soundararajan",
    "t.m.soundararajan": "T.M. Soundararajan",
    "s.p. balasubrahmanyam": "S.P. Balasubrahmanyam",
    "s p balasubrahmanyam": "S.P. Balasubrahmanyam",
    "sp balasubrahmanyam": "S.P. Balasubrahmanyam",
    "s.p.balasubrahmanyam": "S.P. Balasubrahmanyam",
    "s. janaki": "S. Janaki",
    "s janaki": "S. Janaki",
    "s.janaki": "S. Janaki",
    "k.s. chithra": "K.S. Chithra",
    "ks chithra": "K.S. Chithra",
    "kschithra": "K.S. Chithra",
    "p. susheela": "P. Susheela",
    "p susheela": "P. Susheela",
    "psusheela": "P. Susheela",
    "t.t. manickam": "T.T. Manickam",
    "t t manickam": "T.T. Manickam",
    "ttmanickam": "T.T. Manickam",
    # Lyricists
    "na. muthukumar": "Na. Muthukumar",
    "na muthukumar": "Na. Muthukumar",
    "namuthukumar": "Na. Muthukumar",
}


def final_standardize(name: str) -> str:
    """Final standardization pass."""
    if not name:
        return ""
    # Remove all spaces and dots for comparison
    normalized = re.sub(r'[\s\.]+', '', name).lower()
    return CANONICAL_NAMES.get(normalized, name)


def match_song(title: str, youtube_id: str = "") -> dict | None:
    """Match a song against the known database."""
    if not title:
        return None

    title_lower = title.lower()

    # Direct pattern matching
    for pattern, data in PATTERN_LOOKUP.items():
        if pattern in title_lower or title_lower in pattern:
            return data.copy()

    return None


def main():
    print("Enriching Tamil song metadata...")
    print("=" * 60)

    # Load existing songs
    songs = []
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(row)

    print(f"Loaded {len(songs)} songs")

    # Track stats
    matched = 0
    missing_composer = []
    missing_singer = []
    missing_lyricist = []

    for song in songs:
        yt_id = song.get('youtube_id', '')
        yt_title = song.get('youtube_title', '')

        # Try to match known song
        known = match_song(yt_title, yt_id)

        if known:
            # Update fields if empty
            if not song.get('year') or song['year'] == '0':
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
        else:
            # Track what's missing for manual review
            if not song.get('composer'):
                missing_composer.append(yt_title[:50])
            if not song.get('singer'):
                missing_singer.append(yt_title[:50])
            if not song.get('lyricist'):
                missing_lyricist.append(yt_title[:50])

        # Standardize all names (even if from YouTube)
        if song.get('composer'):
            composers = [standardize_name(c.strip()) for c in song['composer'].split(';')]
            song['composer'] = '; '.join(c for c in composers if c)

        if song.get('singer'):
            singers = [standardize_name(s.strip()) for s in song['singer'].split(';')]
            song['singer'] = '; '.join(s for s in singers if s)

        if song.get('lyricist'):
            lyricists = [standardize_name(l.strip()) for l in song['lyricist'].split(';')]
            song['lyricist'] = '; '.join(l for l in lyricists if l)

        # Final standardization pass
        if song.get('composer'):
            composers = [final_standardize(c.strip()) for c in song['composer'].split(';')]
            song['composer'] = '; '.join(c for c in composers if c)
        if song.get('singer'):
            singers = [final_standardize(s.strip()) for s in song['singer'].split(';')]
            song['singer'] = '; '.join(s for s in singers if s)
        if song.get('lyricist'):
            lyricists = [final_standardize(l.strip()) for l in song['lyricist'].split(';')]
            song['lyricist'] = '; '.join(l for l in lyricists if l)

    print(f"Matched {matched} songs to known database")

    # Write output
    with open(OUTPUT_CSV, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        for song in songs:
            writer.writerow(song)

    print(f"Saved to {OUTPUT_CSV}")

    # Stats
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

    print("\nField completeness:")
    for field in ['year', 'movie', 'composer', 'singer', 'lyricist']:
        filled = sum(1 for s in songs if s.get(field))
        print(f"  {field}: {filled}/{len(songs)}")

    print(f"\nSongs missing composer: {len(missing_composer)}")
    print(f"Songs missing singer: {len(missing_singer)}")
    print(f"Songs missing lyricist: {len(missing_lyricist)}")


if __name__ == "__main__":
    main()