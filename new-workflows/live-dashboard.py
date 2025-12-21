#!/usr/bin/env python3
"""
Real-Time API Dashboard Generator
Fetches live data from APIs and creates multi-format visualizations

Demonstrates: curl + jq + Python + SVG + Audio in a real-world workflow
"""

import json
import subprocess
import sys
import time
from datetime import datetime


def fetch_github_stats(username):
    """Fetch GitHub repository stats using curl + jq"""
    print(f"  Fetching GitHub stats for: {username}...")

    # Use curl to fetch repos and jq to process
    cmd = f'''curl -s "https://api.github.com/users/{username}/repos?per_page=10&sort=updated" | \
jq -r '[.[] | {{name: .name, stars: .stargazers_count, forks: .forks_count, size: .size}}] | \
sort_by(-.stars) | .[:8]' '''

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  Error fetching data: {result.stderr}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  Error parsing JSON response")
        return None


def create_github_visualization(repos, username):
    """Create multi-format visualization of GitHub data"""

    # Create data structure for visualization
    data = {
        "title": f"GitHub Stats: @{username} (Top Repos by Stars)",
        "unit": " ★",
        "data": [
            {"month": repo['name'][:8], "avg_response": repo['stars'], "requests": repo['forks']}
            for repo in repos
        ]
    }

    # Save to temp file
    temp_file = "/tmp/github_stats.json"
    with open(temp_file, 'w') as f:
        json.dump(data, f, indent=2)

    return temp_file


def display_live_ascii_dashboard(repos, username):
    """Create a beautiful live ASCII dashboard"""

    # Header
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + f" GitHub Repository Stats: @{username}".ljust(78) + "║")
    print("║" + f" Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(78) + "║")
    print("╚" + "═" * 78 + "╝\n")

    max_stars = max(repo['stars'] for repo in repos) if repos else 1

    # Repository bars
    for repo in repos:
        name = repo['name'][:25].ljust(25)
        stars = repo['stars']
        forks = repo['forks']

        # Normalize to 40 char width
        bar_length = int((stars / max_stars) * 40) if max_stars > 0 else 0

        # Color based on stars
        if stars > 100:
            color = '\033[93m'  # Yellow (popular)
        elif stars > 20:
            color = '\033[92m'  # Green (good)
        else:
            color = '\033[94m'  # Blue (new)

        reset = '\033[0m'

        bar = '█' * bar_length
        print(f"{name} │ {color}{bar}{reset} {stars:>5} ★  ({forks} forks)")

    # Statistics
    total_stars = sum(repo['stars'] for repo in repos)
    total_forks = sum(repo['forks'] for repo in repos)

    print("\n" + "─" * 80)
    print(f"  Total Stars: {total_stars:,} | Total Forks: {total_forks:,} | Repos Shown: {len(repos)}")
    print("═" * 80 + "\n")


def create_ascii_sparkline(values):
    """Create a sparkline from values"""
    if not values or len(values) < 2:
        return ""

    chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    max_val = max(values)
    min_val = min(values)

    if max_val == min_val:
        return chars[3] * len(values)

    sparkline = ""
    for val in values:
        normalized = (val - min_val) / (max_val - min_val)
        idx = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
        sparkline += chars[idx]

    return sparkline


def main():
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "LIVE API DASHBOARD GENERATOR" + " " * 30 + "║")
    print("║" + " " * 15 + "Showcasing Real-World Creative Workflows" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝\n")

    # Get username
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "torvalds"  # Default to Linus Torvalds
        print(f"  No username provided, using default: {username}")

    print(f"\n[1/3] Fetching Live Data from GitHub API...")
    print("  " + "─" * 76)

    repos = fetch_github_stats(username)

    if not repos or len(repos) == 0:
        print("\n  ✗ No repositories found or API error")
        sys.exit(1)

    print(f"  ✓ Fetched {len(repos)} repositories\n")

    # Display live ASCII dashboard
    print("[2/3] Generating ASCII Dashboard...")
    print("  " + "─" * 76)
    display_live_ascii_dashboard(repos, username)

    # Create comprehensive visualizations
    print("[3/3] Generating Multi-Format Visualizations...")
    print("  " + "─" * 76)

    temp_file = create_github_visualization(repos, username)

    # Run the visualizer
    subprocess.run([
        'python3', '/home/user/research/new-workflows/visualize.py', temp_file
    ])

    # Show jq one-liner for quick stats
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + "  Quick jq One-Liners for API Analysis".ljust(79) + "║")
    print("╚" + "═" + "═" * 76 + "╝\n")

    print("  Get total stars:")
    print(f'''    curl -s "https://api.github.com/users/{username}/repos" | jq '[.[].stargazers_count] | add' ''')

    print("\n  Top 3 repos by stars:")
    print(f'''    curl -s "https://api.github.com/users/{username}/repos" | jq 'sort_by(-.stargazers_count) | .[:3] | .[] | "\\(.name): \\(.stargazers_count)★"' ''')

    print("\n  ASCII visualization of all repos:")
    print(f'''    curl -s "https://api.github.com/users/{username}/repos" | jq -r '.[] | "\\(.name): " + ("★" * (.stargazers_count / 100 | floor))' ''')

    print("\n" + "═" * 80)
    print("  ✓ Dashboard Complete!")
    print("  ")
    print("  This demonstrates:")
    print("    • Live API data fetching with curl")
    print("    • JSON processing with jq")
    print("    • Real-time ASCII visualization")
    print("    • SVG generation for sharing")
    print("    • Audio sonification of metrics")
    print("    • All using standard tools!")
    print("═" * 80 + "\n")


if __name__ == '__main__':
    main()
