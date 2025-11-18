#!/usr/bin/env python3
"""
Filter the results to find only names that truly start with 'Ai' and end with 'ai'.
"""

import json

# Read the results
with open("results.json") as f:
    data = json.load(f)

def matches_pattern(name):
    """Check if name starts and ends with 'AI' (case-insensitive)."""
    name_clean = name.strip()
    return name_clean.lower().startswith("ai") and name_clean.lower().endswith("ai")

# Filter to find true matches
true_matches = []
for name in data["names"]:
    if matches_pattern(name):
        true_matches.append(name)
        print(f"Match: {name}")
    else:
        print(f"False positive: {name}")

print("\n" + "="*70)
print(f"Found {len(true_matches)} true matches:")
print("="*70)

for name in sorted(true_matches, key=lambda x: len(x)):
    print(f"  • {name} (length: {len(name)})")

if true_matches:
    print("\n" + "="*70)
    print("Analysis:")
    print("="*70)
    shortest = min(true_matches, key=lambda x: len(x))
    longest = max(true_matches, key=lambda x: len(x))

    print(f"Shortest name: {shortest} ({len(shortest)} characters)")
    print(f"Longest name: {longest} ({len(longest)} characters)")

# Save filtered results
with open("filtered_results.json", "w") as f:
    json.dump({
        "count": len(true_matches),
        "names": sorted(true_matches, key=lambda x: len(x))
    }, f, indent=2)

print(f"\nFiltered results saved to filtered_results.json")
