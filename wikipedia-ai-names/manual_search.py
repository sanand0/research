#!/usr/bin/env python3
"""
Manually search for specific people and patterns.
"""

import requests
import json

headers = {
    "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)"
}

# List of potential matches to check
names_to_check = [
    "Aishwarya Rai",
    "Ai Ai",
    "Ahilyabai",
    "Ahilya Bai",
    "Aishwarya Dhanush",
]

# Also search for people with single name "Ai"
single_names = ["Ai (artist)", "Ai (singer)", "Ai (rapper)"]

matching_names = []

print("Checking specific names...")
print("="*70)

for name in names_to_check + single_names:
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
                print(f"✓ Found: {title}")

                # Check if it matches pattern
                if title.lower().startswith("ai") and title.lower().endswith("ai"):
                    matching_names.append(title)
                    print(f"  → MATCHES PATTERN!")
            else:
                print(f"✗ Not found: {name}")
    except Exception as e:
        print(f"Error checking '{name}': {e}")

print("\n" + "="*70)
print("Searching for people on 'Ai (given name)' Wikipedia page...")
print("="*70)

# Get the content of the "Ai (given name)" page
url = "https://en.wikipedia.org/w/api.php"
params = {
    "action": "parse",
    "format": "json",
    "page": "Ai (given name)",
    "prop": "wikitext"
}

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    data = response.json()

    wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")

    # Look for names in the wikitext
    lines = wikitext.split("\n")
    for line in lines:
        # Look for wiki links  [[Name]]
        if "[[" in line and "]]" in line:
            # Extract linked names
            import re
            links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', line)
            for link in links:
                # Check if it's a person's name (simple heuristic)
                if link.lower().startswith("ai") and link.lower().endswith("ai"):
                    if link not in matching_names:
                        matching_names.append(link)
                        print(f"  • {link}")

except Exception as e:
    print(f"Error fetching 'Ai (given name)' page: {e}")

print("\n" + "="*70)
print("Searching for people on 'Ai (surname)' Wikipedia page...")
print("="*70)

# Get the content of the "Ai (surname)" page
params["page"] = "Ai (surname)"

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    data = response.json()

    wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")

    # Look for names in the wikitext
    lines = wikitext.split("\n")
    for line in lines:
        if "[[" in line and "]]" in line:
            import re
            links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', line)
            for link in links:
                if link.lower().startswith("ai") and link.lower().endswith("ai"):
                    if link not in matching_names:
                        matching_names.append(link)
                        print(f"  • {link}")

except Exception as e:
    print(f"Error fetching 'Ai (surname)' page: {e}")

print("\n" + "="*70)
print(f"Total matches found: {len(matching_names)}")
print("="*70)

for name in sorted(matching_names, key=lambda x: len(x)):
    print(f"  • {name} (length: {len(name)})")

# Save results
with open("manual_matches.json", "w") as f:
    json.dump({
        "count": len(matching_names),
        "names": sorted(matching_names, key=lambda x: len(x))
    }, f, indent=2)

print(f"\nResults saved to manual_matches.json")
