#!/usr/bin/env python3
"""
Test additional readability extractors on all test pages.
Phase 2: Extended evaluation with 6 more tools.
"""

import json
import time
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Any

# Import new extractors
import justext
import inscriptis
from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding, bytes_to_str
from boilerpy3 import extractors as boilerpy_extractors

def run_justext(html: str) -> Dict[str, Any]:
    """Run jusText extractor."""
    start = time.time()
    try:
        paragraphs = justext.justext(html, justext.get_stoplist("English"))
        # Extract only good paragraphs
        text_parts = [p.text for p in paragraphs if not p.is_boilerplate]
        markdown = '\n\n'.join(text_parts)

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

def run_resiliparse(html: str) -> Dict[str, Any]:
    """Run Resiliparse HTML2Text extractor."""
    start = time.time()
    try:
        # Resiliparse needs HTMLTree
        from resiliparse.parse.html import HTMLTree
        tree = HTMLTree.parse(html)
        text = extract_plain_text(tree, main_content=True, preserve_formatting=True)

        duration = time.time() - start
        return {
            'success': True,
            'markdown': text,
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

def run_inscriptis(html: str) -> Dict[str, Any]:
    """Run Inscriptis HTML to text converter."""
    start = time.time()
    try:
        text = inscriptis.get_text(html)

        duration = time.time() - start
        return {
            'success': True,
            'markdown': text,
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

def run_boilerpy3(html: str) -> Dict[str, Any]:
    """Run BoilerPy3 ArticleExtractor."""
    start = time.time()
    try:
        extractor = boilerpy_extractors.ArticleExtractor()
        text = extractor.get_content(html)

        duration = time.time() - start
        return {
            'success': True,
            'markdown': text,
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

def run_node_html_markdown(html_file: Path) -> Dict[str, Any]:
    """Run node-html-markdown converter via Node.js script."""
    start = time.time()
    try:
        result = subprocess.run(
            ['node', 'node_html_markdown_extractor.js', str(html_file)],
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

def run_jina_reader(html_file: Path) -> Dict[str, Any]:
    """Run Jina Reader API on HTML file."""
    start = time.time()
    try:
        # Read HTML
        html = html_file.read_text(encoding='utf-8', errors='ignore')

        # Use Jina Reader API with HTML content
        # Note: This is a mock - real API would need URL or different approach
        # For now, we'll skip API calls and mark as not tested
        return {
            'success': False,
            'markdown': '',
            'duration': time.time() - start,
            'error': 'API not tested - requires URL, not HTML file'
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
    'justext': run_justext,
    'resiliparse': run_resiliparse,
    'inscriptis': run_inscriptis,
    'boilerpy3': run_boilerpy3,
}

def main():
    """Run all additional extractors on all test pages."""
    test_pages_dir = Path('test-pages/html/final')
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)

    # Get all test pages
    test_pages = sorted(test_pages_dir.glob('page_*.html'))

    print(f"Testing {len(EXTRACTORS)} additional extractors on {len(test_pages)} pages...")
    print(f"Extractors: {', '.join(EXTRACTORS.keys())}")
    print()

    # Load existing results if any
    results_file = output_dir / 'results_summary.json'
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
    else:
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

    # Test node-html-markdown separately
    print(f"\n{'='*60}")
    print(f"Testing: node-html-markdown")
    print(f"{'='*60}")

    extractor_dir = output_dir / 'node-html-markdown'
    extractor_dir.mkdir(exist_ok=True)
    results['node-html-markdown'] = {}

    for page_file in test_pages:
        page_num = page_file.stem
        print(f"  {page_num}...", end=' ', flush=True)

        result = run_node_html_markdown(page_file)

        # Save output
        output_file = extractor_dir / f"{page_num}.md"
        output_file.write_text(result['markdown'], encoding='utf-8')

        # Save results
        results['node-html-markdown'][page_num] = {
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

    # Save updated results summary
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✓ All additional tests complete!")
    print(f"Results saved to: {output_dir}/")
    print(f"Summary: {results_file}")
    print(f"{'='*60}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY OF NEW EXTRACTORS")
    print("="*60)
    for extractor in list(EXTRACTORS.keys()) + ['node-html-markdown']:
        if extractor in results:
            total_pages = len(results[extractor])
            successful = sum(1 for p in results[extractor].values() if p['success'])
            avg_time = sum(p['duration'] for p in results[extractor].values()) / total_pages if total_pages > 0 else 0
            print(f"{extractor:25s} {successful}/{total_pages} pages, avg {avg_time:.2f}s")

if __name__ == '__main__':
    main()
