# Phase 2: Extended Evaluation Summary

## Overview

Extended the original 6-extractor evaluation with 5 additional modern tools, bringing the total to **11 extractors** tested on 20 diverse web pages.

## New Tools Tested

1. **justext** (Python) - Heuristic boilerplate removal
2. **resiliparse** (Python) - Fast text extraction for web archives
3. **inscriptis** (Python) - Layout-aware HTML→text
4. **boilerpy3** (Python) - Python port of Boilerpipe
5. **node-html-markdown** (Node.js) - Fast HTML→Markdown converter

## Results

### Overall Rankings (All 11 Extractors)

| Rank | Extractor | Score | Category |
|------|-----------|-------|----------|
| 1-4 | mozilla-readability, readabilipy, trafilatura, readability-lxml | 79.0/100 | Article Extractors ✓ |
| 5-7 | markdownify, node-html-markdown, html2text | 72.3/100 | HTML Converters |
| 8 | boilerpy3 | 50.0/100 | Text Extractor |
| 9 | resiliparse | 49.8/100 | Text Extractor |
| 10 | justext | 48.5/100 | Text Extractor |
| 11 | inscriptis | 43.5/100 | Text Extractor |

### Heading ID Preservation (Critical Metric)

**Tools that preserve heading IDs:**
- Mozilla Readability: 14 IDs (clean) ✓
- ReadabiliPy: 14 IDs (clean) ✓
- markdownify: 16 IDs (but includes navigation/ads)

**Tools that preserve ZERO heading IDs:**
- All other 8 tools including the 5 new ones

### Key Findings

1. **No new tool beats Mozilla Readability** for article extraction with heading IDs
2. **Three distinct categories emerged:**
   - **Article Extractors:** Intelligently extract main content (4 tools)
   - **HTML Converters:** Convert entire page including chrome (3 tools)
   - **Text Extractors:** Extract plain text, lose structure (4 tools)

3. **Speed vs. Quality confirmed:**
   - resiliparse: 0.01s, no structure
   - trafilatura: 0.08s, structure but no IDs
   - Mozilla Readability: 3.32s, structure + IDs ✓

4. **New tool highlights:**
   - **resiliparse**: Fastest (0.01s) but loses all heading structure
   - **inscriptis**: Good for preserving table layout as text
   - **node-html-markdown**: Fast but includes all navigation (like html2text)
   - **justext/boilerpy3**: Aggressive boilerplate removal, sometimes too aggressive

## Updated Recommendation

**PRIMARY (unchanged):** Mozilla Readability + Turndown
- Best for: Article extraction with stable heading IDs
- Platform: Node.js
- Trade-off: Slower (3.3s avg) but highest quality

**PYTHON ALTERNATIVE (unchanged):** ReadabiliPy
- Same quality as Mozilla Readability
- Python API but requires Node.js

**SPEED ALTERNATIVE (unchanged):** trafilatura
- Best for: Fast extraction without heading IDs (0.08s avg)
- Pure Python

**NEW: TEXT-ONLY USE CASES:**
- **resiliparse**: Fastest text extraction (0.01s) for NLP/corpus building
- **inscriptis**: Best for preserving table layout in plain text

## What We Learned

1. **Heading ID preservation is rare:** Only Mozilla Readability algorithm does it well
2. **Modern ≠ Better:** Newer tools (2024-2025) don't outperform Mozilla Readability (2017)
3. **Different tools, different purposes:** Choose based on use case (extraction vs. conversion vs. text)
4. **Structure matters:** Text-only extractors score low because they lose document hierarchy

## Recommendation Stands

After testing 11 total extractors, the original recommendation is **confirmed**:

**Use Mozilla Readability + Turndown for article extraction with stable heading IDs.**

No alternative tested (old or new) provides better heading ID preservation while maintaining clean content extraction.
