#!/usr/bin/env python3
"""
Test all readability extractors on all test pages.
Saves outputs and collects metrics for evaluation.
"""

import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any
import subprocess

# Import Python extractors
import trafilatura
from readability import Document
import html2text
from markdownify import markdownify
from readabilipy import simple_json

def run_trafilatura(html: str) -> Dict[str, Any]:
    """Run trafilatura extractor."""
    start = time.time()
    try:
        result = trafilatura.extract(
            html,
            output_format='markdown',
            include_tables=True,
            include_images=True,
            include_links=True
        )
        duration = time.time() - start
        return {
            'success': True,
            'markdown': result or '',
            'duration': duration,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': str(e)
        }

def run_readability_lxml(html: str) -> Dict[str, Any]:
    """Run readability-lxml extractor with markdownify."""
    start = time.time()
    try:
        doc = Document(html)
        content_html = doc.summary()
        markdown = markdownify(content_html, heading_style="ATX")
        duration = time.time() - start
        return {
            'success': True,
            'markdown': markdown,
            'duration': duration,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': str(e)
        }

def run_html2text(html: str) -> Dict[str, Any]:
    """Run html2text converter."""
    start = time.time()
    try:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        markdown = h.handle(html)
        duration = time.time() - start
        return {
            'success': True,
            'markdown': markdown,
            'duration': duration,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': str(e)
        }

def run_markdownify(html: str) -> Dict[str, Any]:
    """Run markdownify converter."""
    start = time.time()
    try:
        markdown = markdownify(html, heading_style="ATX")
        duration = time.time() - start
        return {
            'success': True,
            'markdown': markdown,
            'duration': duration,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': str(e)
        }

def run_readabilipy(html: str) -> Dict[str, Any]:
    """Run ReadabiliPy extractor."""
    start = time.time()
    try:
        article = simple_json.simple_json_from_html_string(
            html,
            use_readability=True
        )

        # Convert to markdown
        content = article.get('content', '')
        if content:
            markdown = markdownify(content, heading_style="ATX")
        else:
            markdown = article.get('plain_text', [''])[0]

        duration = time.time() - start
        return {
            'success': True,
            'markdown': markdown,
            'duration': duration,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': str(e)
        }

def run_mozilla_readability(html_file: Path) -> Dict[str, Any]:
    """Run Mozilla Readability via Node.js script."""
    start = time.time()
    try:
        result = subprocess.run(
            ['node', 'mozilla_readability_extractor.js', str(html_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        duration = time.time() - start

        if result.returncode == 0:
            return {
                'success': True,
                'markdown': result.stdout,
                'duration': duration,
                'error': None
            }
        else:
            return {
                'success': False,
                'markdown': '',
                'duration': duration,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': str(e)
        }

# Extractor definitions
EXTRACTORS = {
    'trafilatura': run_trafilatura,
    'readability-lxml': run_readability_lxml,
    'html2text': run_html2text,
    'markdownify': run_markdownify,
    'readabilipy': run_readabilipy,
}

def main():
    """Run all extractors on all test pages."""
    test_pages_dir = Path('test-pages/html/final')
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)

    # Get all test pages
    test_pages = sorted(test_pages_dir.glob('page_*.html'))

    print(f"Testing {len(EXTRACTORS)} extractors on {len(test_pages)} pages...")
    print(f"Extractors: {', '.join(EXTRACTORS.keys())}")
    print()

    # Results tracking
    results = {}

    # Test each extractor on each page
    for extractor_name, extractor_func in EXTRACTORS.items():
        print(f"\n{'='*60}")
        print(f"Testing: {extractor_name}")
        print(f"{'='*60}")

        extractor_dir = output_dir / extractor_name
        extractor_dir.mkdir(exist_ok=True)

        results[extractor_name] = {}

        for page_file in test_pages:
            page_num = page_file.stem
            print(f"  {page_num}...", end=' ', flush=True)

            # Read HTML
            html = page_file.read_text(encoding='utf-8', errors='ignore')

            # Run extractor
            if extractor_name == 'mozilla-readability':
                result = run_mozilla_readability(page_file)
            else:
                result = extractor_func(html)

            # Save output
            output_file = extractor_dir / f"{page_num}.md"
            output_file.write_text(result['markdown'], encoding='utf-8')

            # Save results
            results[extractor_name][page_num] = {
                'success': result['success'],
                'duration': result['duration'],
                'error': result['error'],
                'output_size': len(result['markdown']),
                'output_lines': result['markdown'].count('\n')
            }

            if result['success']:
                print(f"✓ ({result['duration']:.2f}s, {len(result['markdown']):,} chars)")
            else:
                print(f"✗ Error: {result['error'][:50]}")

    # Also test Mozilla Readability
    print(f"\n{'='*60}")
    print(f"Testing: mozilla-readability")
    print(f"{'='*60}")

    extractor_dir = output_dir / 'mozilla-readability'
    extractor_dir.mkdir(exist_ok=True)
    results['mozilla-readability'] = {}

    for page_file in test_pages:
        page_num = page_file.stem
        print(f"  {page_num}...", end=' ', flush=True)

        result = run_mozilla_readability(page_file)

        # Save output
        output_file = extractor_dir / f"{page_num}.md"
        output_file.write_text(result['markdown'], encoding='utf-8')

        # Save results
        results['mozilla-readability'][page_num] = {
            'success': result['success'],
            'duration': result['duration'],
            'error': result['error'],
            'output_size': len(result['markdown']),
            'output_lines': result['markdown'].count('\n')
        }

        if result['success']:
            print(f"✓ ({result['duration']:.2f}s, {len(result['markdown']):,} chars)")
        else:
            print(f"✗ Error: {result['error'][:50]}")

    # Save results summary
    results_file = output_dir / 'results_summary.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✓ All tests complete!")
    print(f"Results saved to: {output_dir}/")
    print(f"Summary: {results_file}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
