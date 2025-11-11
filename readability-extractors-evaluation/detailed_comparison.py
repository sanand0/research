#!/usr/bin/env python3
"""
Create a detailed comparison report of all extractors.
"""

import re
import json
from pathlib import Path
from collections import defaultdict

def analyze_heading_ids_detailed(markdown: str) -> dict:
    """
    Analyze heading ID preservation in different formats:
    - [Text](#id) - Link-style IDs (Mozilla Readability style)
    - {#id} - Pandoc style
    - <a id="..."></a> - HTML anchors
    """
    # Count link-style heading IDs (Markdown anchor pattern)
    link_style_headings = re.findall(r'^#+\s+\[(.*?)\]\(#([\w-]+)\)', markdown, re.MULTILINE)

    # Count Pandoc-style IDs
    pandoc_style = re.findall(r'\{#([\w-]+)\}', markdown)

    # Count HTML anchor IDs
    html_anchors = re.findall(r'<a.*?id="([\w-]+)".*?</a>', markdown)

    return {
        'link_style_count': len(link_style_headings),
        'link_style_ids': [id for _, id in link_style_headings][:5],  # Sample
        'pandoc_style_count': len(pandoc_style),
        'html_anchor_count': len(html_anchors),
        'total_id_count': len(link_style_headings) + len(pandoc_style) + len(html_anchors)
    }

def find_ugly_failures(extractor_name: str, page_num: str, markdown: str) -> list:
    """Detect common failure patterns."""
    failures = []

    # Empty or very short output
    if len(markdown) < 100:
        failures.append(f"Very short output ({len(markdown)} chars)")

    # No headings at all
    if not re.search(r'^#+\s', markdown, re.MULTILINE):
        failures.append("No headings found")

    # Excessive navigation/chrome artifacts
    nav_count = len(re.findall(r'(menu|navigation|sidebar|breadcrumb|skip to)', markdown, re.I))
    if nav_count > 5:
        failures.append(f"Excessive navigation artifacts ({nav_count} instances)")

    # Cookie/consent notices
    if re.search(r'(accept.*cookie|cookie consent|gdpr)', markdown, re.I):
        failures.append("Cookie/consent notices included")

    # Social media clutter
    social_count = len(re.findall(r'(share on|tweet this|facebook|linkedin|follow us)', markdown, re.I))
    if social_count > 3:
        failures.append(f"Social media clutter ({social_count} instances)")

    return failures

def compare_content_extraction(page_num: str, all_outputs: dict) -> dict:
    """Compare how different extractors handled the same page."""
    word_counts = {}
    heading_counts = {}
    image_counts = {}

    for extractor, markdown in all_outputs.items():
        word_counts[extractor] = len(re.findall(r'\w+', markdown))
        heading_counts[extractor] = len(re.findall(r'^#+\s', markdown, re.MULTILINE))
        image_counts[extractor] = len(re.findall(r'!\[.*?\]\(.*?\)', markdown))

    # Calculate variance
    word_values = list(word_counts.values())
    if word_values:
        avg_words = sum(word_values) / len(word_values)
        word_variance = sum((x - avg_words) ** 2 for x in word_values) / len(word_values)
    else:
        avg_words = 0
        word_variance = 0

    return {
        'word_counts': word_counts,
        'heading_counts': heading_counts,
        'image_counts': image_counts,
        'word_variance': word_variance,
        'avg_words': avg_words
    }

def main():
    """Create detailed comparison."""
    outputs_dir = Path('outputs')
    extractors = sorted([d.name for d in outputs_dir.iterdir() if d.is_dir()])

    print("="*70)
    print("DETAILED EXTRACTOR COMPARISON")
    print("="*70)

    # Analyze each page across all extractors
    all_page_comparisons = {}
    ugly_failures = defaultdict(list)
    heading_id_analysis = defaultdict(dict)

    for page_num in range(1, 21):
        page_name = f"page_{page_num:02d}"

        # Load all outputs for this page
        page_outputs = {}
        for extractor in extractors:
            md_file = outputs_dir / extractor / f"{page_name}.md"
            if md_file.exists():
                page_outputs[extractor] = md_file.read_text(encoding='utf-8')

        # Compare
        comparison = compare_content_extraction(page_name, page_outputs)
        all_page_comparisons[page_name] = comparison

        # Check for failures
        for extractor, markdown in page_outputs.items():
            failures = find_ugly_failures(extractor, page_name, markdown)
            if failures:
                ugly_failures[extractor].append({
                    'page': page_name,
                    'failures': failures
                })

            # Analyze heading IDs
            id_analysis = analyze_heading_ids_detailed(markdown)
            heading_id_analysis[extractor][page_name] = id_analysis

    # Print heading ID analysis
    print("\n" + "="*70)
    print("HEADING ID PRESERVATION ANALYSIS")
    print("="*70)

    for extractor in extractors:
        total_link_style = sum(
            heading_id_analysis[extractor][p]['link_style_count']
            for p in heading_id_analysis[extractor]
        )
        total_pandoc = sum(
            heading_id_analysis[extractor][p]['pandoc_style_count']
            for p in heading_id_analysis[extractor]
        )
        total_html = sum(
            heading_id_analysis[extractor][p]['html_anchor_count']
            for p in heading_id_analysis[extractor]
        )
        total_ids = total_link_style + total_pandoc + total_html

        print(f"\n{extractor}:")
        print(f"  Link-style IDs (Markdown anchors): {total_link_style}")
        print(f"  Pandoc-style IDs: {total_pandoc}")
        print(f"  HTML anchor IDs: {total_html}")
        print(f"  TOTAL IDs preserved: {total_ids}")

        # Show example if any
        for page, analysis in heading_id_analysis[extractor].items():
            if analysis['link_style_ids']:
                print(f"  Example from {page}: {analysis['link_style_ids'][:3]}")
                break

    # Print ugly failures
    print("\n" + "="*70)
    print("UGLY FAILURES BY EXTRACTOR")
    print("="*70)

    for extractor in extractors:
        failures = ugly_failures.get(extractor, [])
        print(f"\n{extractor}: {len(failures)} pages with issues")
        for failure_info in failures[:5]:  # Show first 5
            print(f"  {failure_info['page']}: {', '.join(failure_info['failures'])}")

    # Identify best performers
    print("\n" + "="*70)
    print("BEST PERFORMERS BY CATEGORY")
    print("="*70)

    # Most stable heading ID preservation
    id_counts = {
        ext: sum(
            heading_id_analysis[ext][p]['total_id_count']
            for p in heading_id_analysis[ext]
        )
        for ext in extractors
    }
    best_ids = max(id_counts.items(), key=lambda x: x[1])
    print(f"\nBest Heading ID Preservation: {best_ids[0]} ({best_ids[1]} IDs preserved)")

    # Fewest failures
    failure_counts = {ext: len(ugly_failures.get(ext, [])) for ext in extractors}
    best_clean = min(failure_counts.items(), key=lambda x: x[1])
    print(f"Cleanest Output: {best_clean[0]} ({best_clean[1]} pages with issues)")

    # Most consistent word count
    avg_variances = {}
    for extractor in extractors:
        variances = [
            all_page_comparisons[p]['word_variance']
            for p in all_page_comparisons
        ]
        avg_variances[extractor] = sum(variances) / len(variances) if variances else 0

    # Save detailed report
    report = {
        'heading_id_analysis': {
            ext: {
                'total_ids': id_counts[ext],
                'by_page': heading_id_analysis[ext]
            }
            for ext in extractors
        },
        'ugly_failures': dict(ugly_failures),
        'page_comparisons': all_page_comparisons,
        'summary': {
            'best_heading_ids': best_ids[0],
            'cleanest_output': best_clean[0],
            'total_extractors_tested': len(extractors),
            'total_pages_tested': 20
        }
    }

    report_file = outputs_dir / 'detailed_comparison.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Detailed comparison saved to: {report_file}")

if __name__ == '__main__':
    main()
