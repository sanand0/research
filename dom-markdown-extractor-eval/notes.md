# DOM→Markdown Extractor Library Evaluation

## Research Goal
Evaluate DOM→Markdown extractor libraries to identify the most readable converter.

## Methodology
1. Identify candidate libraries (JavaScript, Python, CLI tools)
2. Collect 20 representative HTML test cases
3. Run each tool on all test cases
4. Evaluate based on objective and subjective metrics
5. Score and recommend

## Progress Notes

### Initial Research - 2025-11-10

Starting research on popular DOM→Markdown converter libraries...

#### Candidate Libraries Identified

JavaScript/Node.js:
1. **Turndown** - Popular, customizable, works in browser and Node.js
2. **node-html-markdown** - Fast, clean output

Python:
3. **html2text** - Classic Python converter, Aaron Swartz's original
4. **markdownify** - BeautifulSoup-based, customizable
5. **html-to-markdown** (Rust-backed) - Very fast, 60-80x faster than Python

Go/CLI:
6. **html-to-markdown** (Go) - CLI tool, customizable
7. **Pandoc** - Universal document converter, very powerful

Selected for Testing:
- Turndown (JavaScript)
- node-html-markdown (JavaScript)
- html2text (Python)
- markdownify (Python)
- Pandoc (CLI)

#### Test Cases Created (20 total)

1. Headings (h1-h6)
2. Links (various types)
3. Code blocks (inline and fenced)
4. Simple table
5. Complex table with headers
6. Unordered list
7. Ordered list
8. Nested lists
9. Bold and italic text
10. Images with alt text
11. Blockquotes
12. Mixed formatting
13. Footnotes/references
14. Definition lists
15. Horizontal rules
16. Preformatted text
17. Complex nested structure (docs-like)
18. Code with syntax highlighting
19. Multi-column table
20. Real-world documentation page

### Evaluation Results

Ran all 5 tools against all 20 test cases. Evaluated based on objective metrics:
- Heading depth preserved (ATX style `#`)
- Link text kept (inline links `[text](url)`)
- Code blocks fenced (with language hints)
- Tables captured as pipe tables
- Lists properly formatted
- Bold/italic preserved
- Images with alt text
- Blockquotes formatted correctly
- Horizontal rules

**Objective Scores:**
1. node-html-markdown: 97.4% (38/39 checks)
2. markdownify: 92.3% (36/39 checks)
3. turndown: 84.6% (33/39 checks)
4. pandoc: 79.5% (31/39 checks)
5. html2text: 74.4% (29/39 checks)

#### Key Findings & Failures

**node-html-markdown:**
- Near-perfect performance
- Only failure: nested blockquotes use `>>` instead of `> >` (less common but valid)
- Clean output, preserves language hints
- Excellent table handling
- Minor issue: trailing spaces after some elements

**markdownify:**
- Excellent performance
- Failed on syntax highlighting (doesn't preserve language hints)
- Properly indents nested code blocks in lists
- Clean, readable output
- Good spacing

**turndown:**
- MAJOR FAILURE: Completely breaks tables (outputs cells on separate lines)
- Horizontal rules use `* * *` format (valid but detected differently)
- Otherwise solid performance
- Good for simple documents without tables

**pandoc:**
- Tables use space-aligned format instead of pipe tables
- Lost language hints on code blocks
- Very powerful but not optimized for Markdown readability
- Better for format conversion than HTML→MD specifically

**html2text:**
- Lists have extra trailing spaces (messy)
- Uses indented code blocks instead of fenced (loses language info)
- Reasonable for basic content
- Output can be cluttered

### Subjective Evaluation

**Readability Winner: markdownify**
- Cleanest, most readable output
- Proper indentation for nested structures
- Standard Markdown conventions
- Loses language hints but otherwise excellent

**Technical Winner: node-html-markdown**
- Most accurate conversion
- Preserves maximum information (language hints, etc.)
- Fast and reliable
- Slight formatting quirks but technically superior

**Best for Simple Content: turndown**
- Great for docs without tables
- Clean output
- Popular and well-maintained
- Just don't use it for tables!

**Most Powerful: pandoc**
- Swiss army knife
- Many output options
- Better for complex conversions
- Overkill for basic HTML→MD

**Legacy Option: html2text**
- Classic tool, still works
- Output can be messy
- Better alternatives exist
