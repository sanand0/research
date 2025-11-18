#!/usr/bin/env python3
"""
Exhaustive search of ALL Wikipedia pages starting with "Ai" using pagination.
This will iterate through ALL pages, not just the first 500.
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

def is_person_page(title, categories):
    """Check if the page is about a person based on categories."""
    if not categories:
        return False

    person_keywords = [
        "births", "deaths", "living people", "people from",
        "actors", "actresses", "politicians", "writers", "artists",
        "musicians", "singers", "athletes", "scientists", "engineers",
        "businesspeople", "entrepreneurs", "military", "religious"
    ]

    categories_text = " ".join(categories).lower()

    for keyword in person_keywords:
        if keyword in categories_text:
            return True

    return False

def get_page_categories(title):
    """Get categories for a Wikipedia page."""
    url = "https://en.wikipedia.org/w/api.php"

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
            if page_id == "-1":
                return []
            categories = page_data.get("categories", [])
            return [cat["title"] for cat in categories]

        return []
    except Exception as e:
        return []

print("="*70)
print("EXHAUSTIVE WIKIPEDIA SEARCH")
print("="*70)
print("\nSearching ALL Wikipedia pages starting with 'Ai'...")
print("Using pagination to get complete results...\n")

url = "https://en.wikipedia.org/w/api.php"

matching_names = set()
all_pages_checked = 0
pages_matching_pattern = 0
person_pages_found = 0

# Start from "Ai"
ap_from = "Ai"
ap_continue = None

batch_num = 0

while True:
    batch_num += 1
    print(f"Batch {batch_num}: Fetching pages starting from '{ap_from}'...")

    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apfrom": ap_from,
        "aplimit": 500,  # Maximum allowed
        "apnamespace": 0  # Main namespace (articles)
    }

    if ap_continue:
        params["apcontinue"] = ap_continue

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("allpages", [])

        if not pages:
            print("  No more pages found.")
            break

        # Check if we've moved past "Ai" prefix
        first_title = pages[0]["title"]
        if not first_title.lower().startswith("ai"):
            print(f"  Moved past 'Ai' prefix (reached '{first_title}'), stopping.")
            break

        for page in pages:
            title = page["title"]
            all_pages_checked += 1

            # Stop if we've moved past "Ai" prefix
            if not title.lower().startswith("ai"):
                print(f"  Reached '{title}', stopping (past 'Ai' prefix).")
                break

            # Check if title matches pattern
            if matches_pattern(title):
                pages_matching_pattern += 1

                # Get categories to check if it's a person
                categories = get_page_categories(title)

                if is_person_page(title, categories):
                    matching_names.add(title)
                    person_pages_found += 1
                    print(f"  ✓ Match #{person_pages_found}: {title}")

                time.sleep(0.05)  # Small delay to be respectful

        # Check for continuation
        if "continue" in data and "apcontinue" in data["continue"]:
            ap_continue = data["continue"]["apcontinue"]
            ap_from = pages[-1]["title"]  # Update starting point
            print(f"  Processed {len(pages)} pages. Continuing...")
            time.sleep(0.5)  # Delay between batches
        else:
            print("  No more pages to fetch.")
            break

    except Exception as e:
        print(f"  Error: {e}")
        break

# Final results
print("\n" + "="*70)
print("EXHAUSTIVE SEARCH RESULTS")
print("="*70)
print(f"Total pages checked: {all_pages_checked}")
print(f"Pages matching name pattern (start+end with 'ai'): {pages_matching_pattern}")
print(f"Person pages found: {person_pages_found}")
print(f"\nFinal matches: {len(matching_names)} people\n")

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
with open("exhaustive_results.json", "w") as f:
    json.dump({
        "count": len(matching_names),
        "names": sorted_names,
        "methodology": "Exhaustive Wikipedia API search using pagination through ALL pages starting with 'Ai'",
        "statistics": {
            "total_pages_checked": all_pages_checked,
            "pages_matching_pattern": pages_matching_pattern,
            "person_pages_found": person_pages_found
        }
    }, f, indent=2)

print(f"\nResults saved to exhaustive_results.json")
print("\n" + "="*70)
print("This search is exhaustive for English Wikipedia pages")
print("starting with 'Ai' as of the time of this query.")
print("="*70)
