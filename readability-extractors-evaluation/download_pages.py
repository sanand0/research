#!/usr/bin/env python3
"""Download test HTML pages for readability extractor evaluation."""

import urllib.request
import time
from pathlib import Path

# Read URLs from file
urls_file = Path("test-pages/urls.txt")
urls = []

with open(urls_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)

print(f"Found {len(urls)} URLs to download")

# Create output directory
output_dir = Path("test-pages/html")
output_dir.mkdir(exist_ok=True)

# Download each URL
for i, url in enumerate(urls, 1):
    try:
        print(f"\n[{i}/{len(urls)}] Downloading: {url}")

        # Set user agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read()

        # Save to file
        output_file = output_dir / f"page_{i:02d}.html"
        with open(output_file, 'wb') as f:
            f.write(html)

        print(f"  ✓ Saved to {output_file} ({len(html):,} bytes)")

        # Be nice to servers
        time.sleep(1)

    except Exception as e:
        print(f"  ✗ Error: {e}")
        # Create empty file to maintain numbering
        output_file = output_dir / f"page_{i:02d}.html"
        output_file.write_text(f"<!-- ERROR downloading {url}: {e} -->")

print("\n✓ Download complete!")

# Create metadata file mapping numbers to URLs
metadata_file = output_dir / "metadata.txt"
with open(metadata_file, 'w') as f:
    f.write("# Mapping of page numbers to URLs\n\n")
    for i, url in enumerate(urls, 1):
        f.write(f"page_{i:02d}.html\t{url}\n")

print(f"✓ Metadata saved to {metadata_file}")
