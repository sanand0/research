#!/usr/bin/env python3
"""
Evaluate the readability extractor outputs on objective metrics.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def count_headings(markdown: str) -> Dict[str, int]:
    """Count headings by level."""
    headings = defaultdict(int)
    for line in markdown.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            level = len(re.match(r'^#+', line).group())
            headings[f'h{level}'] = headings.get(f'h{level}', 0) + 1
    return dict(headings)

def check_heading_ids(markdown: str) -> Dict[str, any]:
    """Check for heading IDs in markdown."""
    # Common patterns for heading IDs:
    # - {#id} (Pandoc style)
    # - <a id="..."></a> (HTML anchor)
    # - ### Heading {#custom-id}

    id_patterns = [
        r'\{#[\w-]+\}',  # Pandoc style
        r'<a.*?id="[\w-]+".*?</a>',  # HTML anchor
        r'id="[\w-]+"',  # Direct ID attribute
    ]

    total_ids = 0
    for pattern in id_patterns:
        matches = re.findall(pattern, markdown)
        total_ids += len(matches)

    return {
        'has_ids': total_ids > 0,
        'id_count': total_ids
    }

def count_images(markdown: str) -> int:
    """Count images in markdown."""
    # Match ![alt](url) pattern
    return len(re.findall(r'!\[.*?\]\(.*?\)', markdown))

def count_links(markdown: str) -> int:
    """Count links in markdown."""
    # Match [text](url) pattern (not images)
    return len(re.findall(r'(?<!!)\[.*?\]\(.*?\)', markdown))

def count_code_blocks(markdown: str) -> int:
    """Count code blocks."""
    return len(re.findall(r'```', markdown)) // 2

def detect_navigation_artifacts(markdown: str) -> Dict[str, bool]:
    """Detect common navigation/chrome artifacts that shouldn't be in content."""
    artifacts = {
        'cookie_notice': bool(re.search(r'(cookie|consent|privacy policy)', markdown, re.I)),
        'navigation': bool(re.search(r'(skip to|main menu|sidebar|breadcrumb)', markdown, re.I)),
        'social_share': bool(re.search(r'(share on|tweet|facebook|linkedin)', markdown, re.I)),
        'comments_section': bool(re.search(r'(leave a comment|post comment|comments?:?\s*\d+)', markdown, re.I)),
        'ads': bool(re.search(r'(advertisement|sponsored)', markdown, re.I))
    }
    return artifacts

def calculate_content_quality_score(markdown: str) -> Dict[str, any]:
    """Calculate various content quality metrics."""
    lines = markdown.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]

    words = re.findall(r'\w+', markdown)
    sentences = re.split(r'[.!?]+', markdown)

    return {
        'total_chars': len(markdown),
        'total_lines': len(lines),
        'non_empty_lines': len(non_empty_lines),
        'word_count': len(words),
        'sentence_count': len([s for s in sentences if s.strip()]),
        'avg_words_per_sentence': len(words) / max(len([s for s in sentences if s.strip()]), 1)
    }

def analyze_extractor_output(markdown_file: Path) -> Dict:
    """Analyze a single extractor output."""
    markdown = markdown_file.read_text(encoding='utf-8')

    return {
        'file': markdown_file.name,
        'headings': count_headings(markdown),
        'heading_ids': check_heading_ids(markdown),
        'images': count_images(markdown),
        'links': count_links(markdown),
        'code_blocks': count_code_blocks(markdown),
        'artifacts': detect_navigation_artifacts(markdown),
        'quality': calculate_content_quality_score(markdown)
    }

def score_extractor(extractor_name: str, page_analyses: List[Dict]) -> Dict:
    """Calculate overall score for an extractor."""
    total_pages = len(page_analyses)

    # Aggregate metrics
    total_headings = sum(sum(a['headings'].values()) for a in page_analyses)
    total_with_ids = sum(1 for a in page_analyses if a['heading_ids']['has_ids'])
    total_images = sum(a['images'] for a in page_analyses)
    total_links = sum(a['links'] for a in page_analyses)
    total_code_blocks = sum(a['code_blocks'] for a in page_analyses)

    # Count artifacts (lower is better)
    artifact_counts = defaultdict(int)
    for analysis in page_analyses:
        for artifact, present in analysis['artifacts'].items():
            if present:
                artifact_counts[artifact] += 1

    # Calculate scores (0-100)
    scores = {}

    # Content extraction score: average word count normalized
    avg_word_count = sum(a['quality']['word_count'] for a in page_analyses) / total_pages
    scores['content_volume'] = min(100, (avg_word_count / 300) * 100)  # 300 words = 100 points

    # Structure preservation: headings, images, links
    avg_headings = total_headings / total_pages
    avg_images = total_images / total_pages
    avg_links = total_links / total_pages

    scores['structure'] = min(100, (avg_headings * 10) + (avg_images * 2) + (avg_links * 0.5))

    # ID preservation score
    scores['heading_ids'] = (total_with_ids / total_pages) * 100

    # Clean output score (fewer artifacts = higher score)
    total_artifacts = sum(artifact_counts.values())
    max_possible_artifacts = total_pages * len(artifact_counts)
    scores['cleanliness'] = 100 - ((total_artifacts / max(max_possible_artifacts, 1)) * 100)

    # Overall score (weighted average)
    scores['overall'] = (
        scores['content_volume'] * 0.3 +
        scores['structure'] * 0.3 +
        scores['heading_ids'] * 0.2 +
        scores['cleanliness'] * 0.2
    )

    return {
        'scores': scores,
        'stats': {
            'avg_word_count': avg_word_count,
            'avg_headings': avg_headings,
            'avg_images': avg_images,
            'avg_links': avg_links,
            'pages_with_ids': total_with_ids,
            'total_pages': total_pages
        },
        'artifacts': dict(artifact_counts)
    }

def main():
    """Evaluate all extractor outputs."""
    outputs_dir = Path('outputs')

    # Get all extractors
    extractors = [d.name for d in outputs_dir.iterdir() if d.is_dir()]

    print(f"Evaluating {len(extractors)} extractors...")
    print()

    all_analyses = {}
    all_scores = {}

    for extractor in extractors:
        print(f"Analyzing: {extractor}")
        extractor_dir = outputs_dir / extractor

        # Analyze each page output
        page_analyses = []
        for md_file in sorted(extractor_dir.glob('page_*.md')):
            analysis = analyze_extractor_output(md_file)
            page_analyses.append(analysis)

        all_analyses[extractor] = page_analyses

        # Calculate scores
        scores = score_extractor(extractor, page_analyses)
        all_scores[extractor] = scores

        print(f"  Overall score: {scores['scores']['overall']:.1f}/100")
        print(f"  - Content volume: {scores['scores']['content_volume']:.1f}")
        print(f"  - Structure: {scores['scores']['structure']:.1f}")
        print(f"  - Heading IDs: {scores['scores']['heading_ids']:.1f}")
        print(f"  - Cleanliness: {scores['scores']['cleanliness']:.1f}")
        print()

    # Save detailed analyses
    analyses_file = outputs_dir / 'detailed_analyses.json'
    with open(analyses_file, 'w') as f:
        json.dump(all_analyses, f, indent=2)

    scores_file = outputs_dir / 'scores.json'
    with open(scores_file, 'w') as f:
        json.dump(all_scores, f, indent=2)

    # Print rankings
    print("\n" + "="*60)
    print("RANKINGS BY OVERALL SCORE")
    print("="*60)

    ranked = sorted(all_scores.items(), key=lambda x: x[1]['scores']['overall'], reverse=True)
    for rank, (extractor, scores) in enumerate(ranked, 1):
        print(f"{rank}. {extractor:25s} {scores['scores']['overall']:5.1f}/100")

    print(f"\n✓ Evaluation complete!")
    print(f"Detailed analyses: {analyses_file}")
    print(f"Scores: {scores_file}")

if __name__ == '__main__':
    main()
