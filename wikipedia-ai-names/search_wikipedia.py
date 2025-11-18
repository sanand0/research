#!/usr/bin/env python3
"""
Search Wikipedia for people whose names begin and end with "AI" (case-insensitive).
"""

import requests
import json
import re
from collections import defaultdict

def search_wikipedia(search_term, limit=500):
    """Search Wikipedia using the MediaWiki API."""
    url = "https://en.wikipedia.org/w/api.php"

    headers = {
        "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)"
    }

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_term,
        "srlimit": limit,
        "srprop": "snippet"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        if not response.text:
            print(f"    Warning: Empty response for search term '{search_term}'")
            return []

        data = response.json()
        return data.get("query", {}).get("search", [])
    except Exception as e:
        print(f"    Error searching for '{search_term}': {e}")
        return []

def get_page_categories(title):
    """Get categories for a Wikipedia page to check if it's about a person."""
    url = "https://en.wikipedia.org/w/api.php"

    headers = {
        "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)"
    }

    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "categories",
        "cllimit": 50
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            categories = page_data.get("categories", [])
            return [cat["title"] for cat in categories]

        return []
    except Exception as e:
        return []

def is_person_article(title, categories):
    """Check if the article is about a person based on title and categories."""
    # Check categories for biographical indicators
    person_keywords = [
        "births", "deaths", "living people", "people from",
        "actors", "actresses", "politicians", "writers", "artists",
        "musicians", "singers", "athletes", "scientists", "engineers",
        "businesspeople", "entrepreneurs"
    ]

    categories_text = " ".join(categories).lower()

    for keyword in person_keywords:
        if keyword in categories_text:
            return True

    return False

def matches_pattern(name):
    """Check if name starts and ends with 'AI' (case-insensitive)."""
    name_clean = name.strip()
    return name_clean.lower().startswith("ai") and name_clean.lower().endswith("ai")

def main():
    print("Searching Wikipedia for people whose names begin and end with 'AI'...\n")

    matching_names = {}
    checked_titles = set()

    # Strategy 1: Search for known example
    print("Strategy 1: Verifying with known example...")
    results = search_wikipedia('Aishwarya Rai', limit=10)

    for result in results:
        title = result["title"]

        if title in checked_titles:
            continue
        checked_titles.add(title)

        # Check if title matches pattern
        if matches_pattern(title):
            print(f"  Checking: {title}")
            categories = get_page_categories(title)

            if is_person_article(title, categories):
                matching_names[title] = categories
                print(f"    ✓ Match found: {title}")

    # Strategy 2: Search for common patterns
    print("\nStrategy 2: Searching for specific patterns...")

    # Common first names starting with Ai
    first_names = ["Aishwarya", "Aisling", "Aisha", "Ainsley", "Aidan", "Aiden", "Aiko"]

    # Common last names ending with ai
    last_names = ["Rai", "Bai", "Kai", "Lai", "Mai", "Sai", "Tai", "Wai"]

    for first in first_names:
        for last in last_names:
            full_name = f"{first} {last}"
            if matches_pattern(full_name):
                results = search_wikipedia(full_name, limit=10)

                for result in results:
                    title = result["title"]

                    if title in checked_titles:
                        continue
                    checked_titles.add(title)

                    print(f"  Checking: {title}")
                    categories = get_page_categories(title)

                    if is_person_article(title, categories):
                        matching_names[title] = categories
                        print(f"    ✓ Match found: {title}")

    # Strategy 3: Browse names starting with Ai more broadly
    print("\nStrategy 3: Browsing all pages starting with 'Ai'...")

    url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)"
    }
    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apfrom": "Ai",
        "aplimit": 500,
        "apnamespace": 0
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("allpages", [])
    except Exception as e:
        print(f"  Error fetching allpages: {e}")
        pages = []

    for page in pages:
        title = page["title"]

        # Stop if we've moved past "Ai" prefix
        if not title.lower().startswith("ai"):
            break

        if title in checked_titles:
            continue
        checked_titles.add(title)

        # Check if title matches pattern
        if matches_pattern(title):
            print(f"  Checking: {title}")
            categories = get_page_categories(title)

            if is_person_article(title, categories):
                matching_names[title] = categories
                print(f"    ✓ Match found: {title}")

    # Results
    print("\n" + "="*70)
    print(f"Found {len(matching_names)} people whose names begin and end with 'AI':")
    print("="*70)

    sorted_names = sorted(matching_names.keys(), key=lambda x: len(x))

    for name in sorted_names:
        print(f"  • {name} (length: {len(name)})")

    if matching_names:
        print("\n" + "="*70)
        print("Analysis:")
        print("="*70)
        shortest = min(sorted_names, key=lambda x: len(x))
        longest = max(sorted_names, key=lambda x: len(x))

        print(f"Shortest name: {shortest} ({len(shortest)} characters)")
        print(f"Longest name: {longest} ({len(longest)} characters)")

    # Save results
    with open("results.json", "w") as f:
        json.dump({
            "count": len(matching_names),
            "names": sorted_names,
            "details": {name: cats[:5] for name, cats in matching_names.items()}
        }, f, indent=2)

    print(f"\nResults saved to results.json")

if __name__ == "__main__":
    main()
