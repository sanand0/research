#!/usr/bin/env python3
"""
Verify the exhaustive results and supplement with missing entries.
"""

import requests
import json

headers = {
    "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)"
}

def matches_pattern(name):
    """Check if name starts and ends with 'AI' (case-insensitive)."""
    name_clean = name.split("(")[0].strip()
    return name_clean.lower().startswith("ai") and name_clean.lower().endswith("ai")

def check_if_person(title):
    """Check if a Wikipedia page is about a person."""
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "categories|pageprops",
        "cllimit": 50
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                return False, "Page not found"

            # Check categories
            categories = page_data.get("categories", [])
            cat_text = " ".join([cat["title"] for cat in categories]).lower()

            # Exclude non-persons
            if "chimpanzee" in cat_text or "animal" in cat_text:
                return False, "Animal, not person"

            if "band" in cat_text or "musical group" in cat_text:
                return False, "Band/group, not individual person"

            # Check for person indicators
            person_keywords = [
                "births", "deaths", "living people", "people from",
                "actors", "actresses", "politicians", "writers", "artists",
                "musicians", "singers", "athletes", "scientists", "engineers",
                "businesspeople", "poets", "military"
            ]

            for keyword in person_keywords:
                if keyword in cat_text:
                    return True, "Person"

        return False, "Not classified as person"

    except Exception as e:
        return False, f"Error: {e}"

# Load exhaustive results
with open("exhaustive_results.json") as f:
    data = json.load(f)

print("="*70)
print("VERIFYING EXHAUSTIVE RESULTS")
print("="*70)

verified_people = []
non_people = []

for name in data["names"]:
    is_person, reason = check_if_person(name)
    if is_person:
        verified_people.append(name)
        print(f"✓ {name} - {reason}")
    else:
        non_people.append((name, reason))
        print(f"✗ {name} - {reason}")

# Check for missing entries that should have been found
print("\n" + "="*70)
print("CHECKING FOR MISSING ENTRIES")
print("="*70)

additional_names_to_check = [
    "Aishwarya Rai Bachchan",  # Married name
    "Aishwarya Rai",  # Maiden name (might redirect)
    "Ai Ai",  # Chinese military officer
    "Ahilyabai",  # Indian historical figure
    "Ahilya Bai Holkar",
    "Ahilyabai Holkar"
]

for name in additional_names_to_check:
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": name,
        "redirects": 1
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data_check = response.json()

        pages = data_check.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":  # Page exists
                actual_title = page_data.get("title", "")

                # Check if it matches the pattern
                if matches_pattern(name):
                    is_person, reason = check_if_person(actual_title)

                    if is_person and actual_title not in verified_people:
                        print(f"✓ FOUND MISSING: {name} (page: {actual_title}) - {reason}")
                        verified_people.append(actual_title)
                    else:
                        print(f"  Checked: {name} → {actual_title} - already included or not a person")

    except Exception as e:
        print(f"  Error checking {name}: {e}")

# Final results
print("\n" + "="*70)
print("FINAL VERIFIED RESULTS")
print("="*70)
print(f"Found {len(verified_people)} people whose names begin and end with 'AI':\n")

sorted_names = sorted(verified_people, key=lambda x: len(x))

for name in sorted_names:
    print(f"  • {name} (length: {len(name)})")

if verified_people:
    print("\n" + "="*70)
    print("Analysis:")
    print("="*70)
    shortest = min(sorted_names, key=lambda x: len(x))
    longest = max(sorted_names, key=lambda x: len(x))

    print(f"Shortest name: '{shortest}' ({len(shortest)} characters)")
    print(f"Longest name: '{longest}' ({len(longest)} characters)")

print("\n" + "="*70)
print("EXCLUDED (Not people):")
print("="*70)
for name, reason in non_people:
    print(f"  ✗ {name} - {reason}")

# Save final verified results
with open("final_verified_results.json", "w") as f:
    json.dump({
        "count": len(verified_people),
        "names": sorted_names,
        "excluded": [{"name": name, "reason": reason} for name, reason in non_people],
        "methodology": "Exhaustive Wikipedia API search (24,086 pages checked) + manual verification",
        "scope": "English Wikipedia pages with titles starting with 'Ai'"
    }, f, indent=2)

print(f"\nFinal results saved to final_verified_results.json")
