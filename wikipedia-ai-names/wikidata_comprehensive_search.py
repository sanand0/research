#!/usr/bin/env python3
"""
Comprehensive search using Wikidata SPARQL to find ALL people whose names
begin and end with "AI" (case-insensitive).
"""

import requests
import json
import time

def query_wikidata_sparql(query):
    """Execute a SPARQL query against Wikidata."""
    url = "https://query.wikidata.org/sparql"

    headers = {
        "User-Agent": "WikipediaResearchBot/1.0 (Educational Research Project; python-requests)",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, params={"query": query, "format": "json"}, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error querying Wikidata: {e}")
        return None

def matches_pattern(name):
    """Check if name starts and ends with 'AI' (case-insensitive)."""
    if not name:
        return False
    name_clean = name.strip()
    return name_clean.lower().startswith("ai") and name_clean.lower().endswith("ai")

# Query 1: Search for people with labels starting with "Ai"
print("="*70)
print("COMPREHENSIVE WIKIDATA SEARCH")
print("="*70)
print("\nQuery 1: Searching Wikidata for all humans with names starting with 'Ai'...")
print("This may take a while as we're querying millions of records...")

sparql_query = """
SELECT DISTINCT ?person ?personLabel ?article WHERE {
  ?person wdt:P31 wd:Q5 .  # instance of human
  ?article schema:about ?person .
  ?article schema:isPartOf <https://en.wikipedia.org/> .
  ?person rdfs:label ?personLabel .
  FILTER(LANG(?personLabel) = "en")
  FILTER(REGEX(?personLabel, "^[Aa][Ii]", "i"))
}
LIMIT 10000
"""

results_data = query_wikidata_sparql(sparql_query)

matching_names = set()

if results_data:
    bindings = results_data.get("results", {}).get("bindings", [])
    print(f"Found {len(bindings)} people with names starting with 'Ai'")
    print("Filtering for names that also end with 'ai'...\n")

    for binding in bindings:
        person_label = binding.get("personLabel", {}).get("value", "")
        article_url = binding.get("article", {}).get("value", "")

        if matches_pattern(person_label):
            # Extract Wikipedia article title from URL
            if "/wiki/" in article_url:
                wiki_title = article_url.split("/wiki/")[-1].replace("_", " ")
                matching_names.add(wiki_title)
                print(f"  ✓ {wiki_title}")

print(f"\nQuery 1 found {len(matching_names)} matches")

# Query 2: Search by given names and family names separately
print("\n" + "="*70)
print("Query 2: Searching by given name + family name combinations...")
print("="*70)

# Common given names starting with Ai
given_names_starting_ai = [
    "Ai", "Aishwarya", "Aisling", "Aisha", "Aishah", "Aislinn",
    "Ainsley", "Aidan", "Aiden", "Aiko", "Aina", "Ainhoa"
]

# Common family names ending with ai
family_names_ending_ai = [
    "Rai", "Bai", "Sai", "Tai", "Wai", "Kai", "Lai", "Mai",
    "Desai", "Lokhande", "Nagai", "Futai", "Santai"
]

for given_name in given_names_starting_ai:
    for family_name in family_names_ending_ai:
        full_pattern = f"{given_name} {family_name}"

        if not matches_pattern(full_pattern):
            continue

        sparql_query_name = f"""
        SELECT DISTINCT ?person ?personLabel ?article WHERE {{
          ?person wdt:P31 wd:Q5 .
          ?article schema:about ?person .
          ?article schema:isPartOf <https://en.wikipedia.org/> .
          ?person rdfs:label ?personLabel .
          FILTER(LANG(?personLabel) = "en")
          FILTER(REGEX(?personLabel, "^{given_name}.*{family_name}$", "i"))
        }}
        LIMIT 100
        """

        results_data = query_wikidata_sparql(sparql_query_name)

        if results_data:
            bindings = results_data.get("results", {}).get("bindings", [])

            for binding in bindings:
                person_label = binding.get("personLabel", {}).get("value", "")
                article_url = binding.get("article", {}).get("value", "")

                if matches_pattern(person_label):
                    if "/wiki/" in article_url:
                        wiki_title = article_url.split("/wiki/")[-1].replace("_", " ")
                        if wiki_title not in matching_names:
                            matching_names.add(wiki_title)
                            print(f"  ✓ {wiki_title}")

        time.sleep(0.5)  # Be respectful to Wikidata servers

print(f"\nQuery 2 found {len(matching_names)} total unique matches")

# Query 3: Japanese names with single given name "Ai"
print("\n" + "="*70)
print("Query 3: Searching for people with mononym 'Ai'...")
print("="*70)

sparql_query_ai = """
SELECT DISTINCT ?person ?personLabel ?article WHERE {
  ?person wdt:P31 wd:Q5 .
  ?article schema:about ?person .
  ?article schema:isPartOf <https://en.wikipedia.org/> .
  ?person rdfs:label ?personLabel .
  FILTER(LANG(?personLabel) = "en")
  FILTER(REGEX(?personLabel, "^Ai \\\\(", "i") || REGEX(?personLabel, "^Ai$", "i"))
}
LIMIT 1000
"""

results_data = query_wikidata_sparql(sparql_query_ai)

if results_data:
    bindings = results_data.get("results", {}).get("bindings", [])

    for binding in bindings:
        person_label = binding.get("personLabel", {}).get("value", "")
        article_url = binding.get("article", {}).get("value", "")

        if matches_pattern(person_label):
            if "/wiki/" in article_url:
                wiki_title = article_url.split("/wiki/")[-1].replace("_", " ")
                if wiki_title not in matching_names:
                    matching_names.add(wiki_title)
                    print(f"  ✓ {wiki_title}")

# Final results
print("\n" + "="*70)
print("FINAL COMPREHENSIVE RESULTS")
print("="*70)
print(f"Found {len(matching_names)} people whose names begin and end with 'AI':\n")

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
with open("wikidata_comprehensive_results.json", "w") as f:
    json.dump({
        "count": len(matching_names),
        "names": sorted_names,
        "methodology": "Wikidata SPARQL queries searching all humans with English Wikipedia articles"
    }, f, indent=2)

print(f"\nResults saved to wikidata_comprehensive_results.json")
