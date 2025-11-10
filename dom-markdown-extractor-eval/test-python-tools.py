#!/usr/bin/env python3
import os
import html2text
from markdownify import markdownify
from pathlib import Path
from bs4 import BeautifulSoup

def test_html2text():
    """Test html2text converter"""
    test_dir = Path('test-cases')
    output_dir = Path('outputs/html2text')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure html2text
    h = html2text.HTML2Text()
    h.body_width = 0  # Don't wrap lines

    test_files = sorted(test_dir.glob('*.html'))
    print(f"Testing html2text on {len(test_files)} files...\n")

    for html_file in test_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()

        # Extract body content
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body
        body_html = str(body) if body else html

        # Convert to markdown
        markdown = h.handle(body_html)

        # Save output
        output_file = output_dir / html_file.name.replace('.html', '.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✓ {html_file.name} -> {output_file.name}")

    print("\nhtml2text conversion complete!")

def test_markdownify():
    """Test markdownify converter"""
    test_dir = Path('test-cases')
    output_dir = Path('outputs/markdownify')
    output_dir.mkdir(parents=True, exist_ok=True)

    test_files = sorted(test_dir.glob('*.html'))
    print(f"\nTesting markdownify on {len(test_files)} files...\n")

    for html_file in test_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()

        # Extract body content
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body
        body_html = str(body) if body else html

        # Convert to markdown
        markdown = markdownify(body_html, heading_style="ATX")

        # Save output
        output_file = output_dir / html_file.name.replace('.html', '.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✓ {html_file.name} -> {output_file.name}")

    print("\nmarkdownify conversion complete!")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    test_html2text()
    test_markdownify()
