#!/usr/bin/env python3
"""Download additional test HTML pages."""

import urllib.request
import time
from pathlib import Path

# Read URLs from file
urls_file = Path("test-pages/additional_urls.txt")
urls = []

with open(urls_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)

print(f"Found {len(urls)} additional URLs to download")

# Create output directory
output_dir = Path("test-pages/html")
output_dir.mkdir(exist_ok=True)

# Find next available number
existing = sorted(output_dir.glob("page_*.html"))
if existing:
    last_num = max(int(p.stem.split('_')[1]) for p in existing)
    start_num = last_num + 1
else:
    start_num = 1

print(f"Starting from page_{start_num:02d}")

# Download each URL
successful = []
for i, url in enumerate(urls, start_num):
    try:
        print(f"\nDownloading: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read()

        output_file = output_dir / f"page_{i:02d}.html"
        with open(output_file, 'wb') as f:
            f.write(html)

        print(f"  ✓ Saved to {output_file} ({len(html):,} bytes)")
        successful.append((i, url))

        time.sleep(1)

    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n✓ Downloaded {len(successful)} additional pages!")

# Update metadata file
metadata_file = output_dir / "metadata.txt"
with open(metadata_file, 'a') as f:
    f.write("\n# Additional pages\n")
    for num, url in successful:
        f.write(f"page_{num:02d}.html\t{url}\n")
