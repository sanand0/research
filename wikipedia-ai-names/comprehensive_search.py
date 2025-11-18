#!/usr/bin/env python3
"""
Comprehensive search for all people whose names start and end with 'AI'.
"""

import requests
import json
import time

headers = {
    "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)"
}

def matches_pattern(name):
    """Check if name starts and ends with 'AI' (case-insensitive)."""
    # Remove parenthetical disambiguations for checking
    name_clean = name.split("(")[0].strip()
    return name_clean.lower().startswith("ai") and name_clean.lower().endswith("ai")

def search_wikipedia_category(category, max_members=500):
    """Search a Wikipedia category for members."""
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": max_members,
        "cmnamespace": 0  # Main namespace (articles)
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        return data.get("query", {}).get("categorymembers", [])
    except Exception as e:
        print(f"Error searching category '{category}': {e}")
        return []

matching_names = set()

# Known matches
known_matches = ["Aishwarya Rai", "Ai Ai", "Ai Nagai"]

print("Adding known matches...")
for name in known_matches:
    if matches_pattern(name):
        matching_names.add(name)
        print(f"  ✓ {name}")

# Search for Japanese names starting with Ai
print("\nSearching for Japanese people with names starting with Ai...")

japanese_first_names_ai = [
    "Ai Fukuhara", "Ai Miyazato", "Ai Kago", "Ai Otsuka",
    "Ai Tominaga", "Ai Maeda", "Ai Hashimoto", "Ai Kayano",
    "Ai Nonaka", "Ai Shimizu", "Ai Takahashi", "Ai Sugiyama"
]

for name in japanese_first_names_ai:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "prop": "info"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":  # Page exists
                title = page_data.get("title", "")
                if matches_pattern(title):
                    matching_names.add(title)
                    print(f"  ✓ {title}")

        time.sleep(0.1)  # Be nice to Wikipedia
    except Exception as e:
        print(f"  Error checking '{name}': {e}")

# Search for Indian names with Aishwarya/Aisling + last names ending in 'ai'
print("\nSearching for Indian/Irish names with pattern...")

first_names = ["Aishwarya", "Aisling", "Aisha", "Aishath", "Aishah"]
last_names_ending_ai = [
    "Rai", "Bai", "Desai", "Lokhande", "Deol", "Kapoor", "Sharma",
    "Verma", "Chopra", "Singh", "Kaur", "Dhanush", "Arjun",
    "Shetty", "Menon", "Nair", "Iyer"
]

for first in first_names:
    for last in last_names_ending_ai:
        full_name = f"{first} {last}"

        # Only check if it matches the pattern
        if not matches_pattern(full_name):
            continue

        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": full_name,
            "prop": "info|categories",
            "cllimit": 10
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":  # Page exists
                    title = page_data.get("title", "")

                    # Check if it's about a person (not a redirect)
                    categories = page_data.get("categories", [])
                    if categories:  # Has categories, likely a real article
                        matching_names.add(title)
                        print(f"  ✓ {title}")

            time.sleep(0.1)
        except Exception as e:
            pass  # Skip errors

# Search for Chinese/Japanese single name "Ai"
print("\nSearching for people with single name 'Ai'...")

single_name_variants = [
    "Ai (singer)",
    "Ai (musician)",
    "Ai (Japanese singer)",
    "Ai Carina Uemura"
]

for name in single_name_variants:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "prop": "info"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":  # Page exists
                title = page_data.get("title", "")
                if matches_pattern(title):
                    matching_names.add(title)
                    print(f"  ✓ {title}")

        time.sleep(0.1)
    except Exception as e:
        pass

# Search for historical Indian figures
print("\nSearching for historical Indian figures...")

historical_names = [
    "Ahilyabai Holkar",
    "Ahilya Bai",
    "Ahalya Bai",
    "Tarabai",
    "Jijabai",
    "Putalabai"
]

for name in historical_names:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "prop": "info"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":  # Page exists
                title = page_data.get("title", "")
                if matches_pattern(title):
                    matching_names.add(title)
                    print(f"  ✓ {title}")

        time.sleep(0.1)
    except Exception as e:
        pass

# Results
print("\n" + "="*70)
print(f"Found {len(matching_names)} people whose names begin and end with 'AI':")
print("="*70)

sorted_names = sorted(matching_names, key=lambda x: len(x))

for name in sorted_names:
    print(f"  • {name} (length: {len(name)})")

if matching_names:
    print("\n" + "="*70)
    print("Analysis:")
    print("="*70)
    shortest = min(sorted_names, key=lambda x: len(x))
    longest = max(sorted_names, key=lambda x: len(x))

    print(f"Shortest name: '{shortest}' ({len(shortest)} characters)")
    print(f"Longest name: '{longest}' ({len(longest)} characters)")

# Save results
with open("final_results.json", "w") as f:
    json.dump({
        "count": len(matching_names),
        "names": sorted_names
    }, f, indent=2)

print(f"\nResults saved to final_results.json")
