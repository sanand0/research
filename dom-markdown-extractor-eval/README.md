# DOM→Markdown Extractor Library Evaluation

## Executive Summary

This research evaluates 5 popular DOM→Markdown converter libraries to determine which produces the most readable Markdown output. After testing all tools against 20 representative HTML test cases and evaluating based on both objective metrics and subjective readability, **node-html-markdown** emerges as the recommended choice for most use cases.

## Recommendation

### 🏆 Winner: node-html-markdown

**For general use, we recommend node-html-markdown** because it:
- Achieves 97.4% accuracy on objective metrics (highest score)
- Preserves code language hints (critical for technical documentation)
- Handles tables excellently
- Produces clean, readable output
- Fast and reliable

**Install:** `npm install node-html-markdown`

### Alternative Recommendations

**For Python projects with simpler content:** Use **markdownify**
- 92.3% accuracy score
- Cleanest, most readable output
- Better indentation for nested structures
- Doesn't preserve code language hints (loses `python`, `javascript` tags)

**For documents without tables:** **Turndown** is acceptable
- Popular and well-maintained
- Clean output for most content
- **WARNING:** Completely fails on table conversion

## Evaluation Methodology

### Test Cases (20 total)

We created comprehensive HTML test cases covering:
1. Headings (h1-h6)
2. Links (various types)
3. Code blocks (inline and fenced)
4. Simple tables
5. Complex tables with headers
6. Unordered lists
7. Ordered lists
8. Nested lists
9. Bold and italic text
10. Images with alt text
11. Blockquotes
12. Mixed formatting
13. Footnotes/references
14. Definition lists
15. Horizontal rules
16. Preformatted text
17. Complex nested structures
18. Code with syntax highlighting
19. Multi-column tables
20. Real-world documentation pages

### Evaluation Criteria

**Objective Metrics:**
- Heading depth preserved (ATX style `#`)
- Link text kept (inline links `[text](url)`)
- Code blocks properly fenced
- Language hints preserved (e.g., ` ```python`)
- Tables captured as pipe tables
- Lists properly formatted with correct markers
- Bold/italic emphasis preserved
- Images with alt text syntax
- Blockquotes formatted correctly
- Horizontal rules rendered

**Subjective Metrics:**
- Overall readability
- Clean output without artifacts
- Proper spacing and indentation
- Standard Markdown conventions

## Results

### Objective Scores

| Rank | Tool                  | Score  | Checks Passed | Notes                          |
|------|-----------------------|--------|---------------|--------------------------------|
| 1    | node-html-markdown    | 97.4%  | 38/39         | Only minor blockquote issue    |
| 2    | markdownify           | 92.3%  | 36/39         | Loses code language hints      |
| 3    | turndown              | 84.6%  | 33/39         | **Fails completely on tables** |
| 4    | pandoc                | 79.5%  | 31/39         | Non-standard table format      |
| 5    | html2text             | 74.4%  | 29/39         | Messy output, loses info       |

### Detailed Analysis

#### 🥇 node-html-markdown (97.4%)

**Strengths:**
- Near-perfect conversion accuracy
- Preserves code language hints (````python`, ````javascript`)
- Excellent table handling with proper pipe format
- Fast performance
- Clean, consistent output

**Weaknesses:**
- Nested blockquotes use `>>` instead of `> >` (valid but less common)
- Occasional trailing spaces after elements

**Example Output Quality:**
```markdown
### Python Example

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

| Name    | Age | City     |
| ------- | --- | -------- |
| Alice   | 30  | New York |
| Bob     | 25  | London   |
```

**Verdict:** Best overall choice for technical documentation and general use.

---

#### 🥈 markdownify (92.3%)

**Strengths:**
- Cleanest, most readable output
- Proper indentation for nested structures
- Follows standard Markdown conventions
- Excellent spacing and formatting

**Weaknesses:**
- **Does not preserve code language hints** (converts `<code class="language-python">` to plain fenced blocks)
- This is a significant loss for documentation with code examples

**Example Output Quality:**
```markdown
1. Clone the repository:

   ```
   git clone https://github.com/example/project.git
   cd project
   ```
2. Install dependencies:

   ```
   npm install
   ```
```

Note the proper indentation but missing language hints.

**Verdict:** Great for readability-focused content without heavy code examples. Not suitable for technical documentation that relies on syntax highlighting.

---

#### 🥉 turndown (84.6%)

**Strengths:**
- Popular, well-maintained library
- Works in both Node.js and browser
- Clean output for most content types
- Good handling of emphasis, links, images

**Weaknesses:**
- **CRITICAL FAILURE:** Cannot convert tables at all
  - Tables are converted to separate lines per cell (unusable)
  - This is a dealbreaker for many use cases
- Horizontal rules use `* * *` format (valid but inconsistent)

**Example Failure:**
```markdown
# Input: Simple table with 3 columns, 3 rows
# Output:
Name

Age

City

Alice

30

New York
```

**Verdict:** Only use for documents that definitely won't contain tables. Otherwise, avoid.

---

#### 4️⃣ pandoc (79.5%)

**Strengths:**
- Extremely powerful and flexible
- Supports many input/output formats
- Well-tested and maintained
- Good for complex document conversions

**Weaknesses:**
- Uses space-aligned tables instead of pipe tables (less portable)
- Loses code language hints
- Output optimized for Pandoc's Markdown variant, not GitHub/CommonMark
- Overkill for simple HTML→Markdown conversion

**Example Table Format:**
```markdown
  Name      Age   City
  --------- ----- ----------
  Alice     30    New York
  Bob       25    London
```

**Verdict:** Better suited for complex document format conversions than simple HTML→Markdown. Use when you need Pandoc's power for other reasons.

---

#### 5️⃣ html2text (74.4%)

**Strengths:**
- Classic, battle-tested tool
- Simple to use
- Works reasonably well for basic content

**Weaknesses:**
- Messy output with trailing spaces
- Uses indented code blocks instead of fenced (loses language info)
- Less readable than modern alternatives
- Cluttered formatting

**Example Issues:**
```markdown
Shopping list:

  * Apples
  * Bananas
  * Oranges
```

Note the trailing spaces and extra blank lines.

**Verdict:** Legacy tool. Better modern alternatives exist. Only use if you're already committed to it.

---

## Critical Failures Highlighted

### Turndown's Table Catastrophe

Turndown completely fails to convert tables. Here's a comparison:

**Input HTML:**
```html
<table>
  <tr><th>Name</th><th>Age</th><th>City</th></tr>
  <tr><td>Alice</td><td>30</td><td>New York</td></tr>
  <tr><td>Bob</td><td>25</td><td>London</td></tr>
</table>
```

**Expected Markdown:**
```markdown
| Name  | Age | City     |
| ----- | --- | -------- |
| Alice | 30  | New York |
| Bob   | 25  | London   |
```

**Turndown Output:**
```markdown
Name

Age

City

Alice

30

New York

Bob

25

London
```

This is completely unusable. **Do not use Turndown for any content that might contain tables.**

### html2text's Language Hint Loss

For technical documentation, preserving code language hints is critical for proper syntax highlighting.

**Input HTML:**
```html
<pre><code class="language-python">
def hello():
    print("Hello")
</code></pre>
```

**node-html-markdown Output:**
````markdown
```python
def hello():
    print("Hello")
```
````

**html2text Output:**
```markdown
    def hello():
        print("Hello")
```

html2text uses indented code blocks, losing the language information entirely.

## Performance Considerations

All tools performed reasonably fast on our test suite (20 files):
- **node-html-markdown:** ~200ms total
- **turndown:** ~150ms total
- **markdownify:** ~400ms total (Python overhead)
- **html2text:** ~350ms total
- **pandoc:** ~500ms total (process spawn overhead)

For production use cases processing thousands of documents, the JavaScript libraries (node-html-markdown, turndown) have a slight edge, but all are adequate.

## Installation & Usage

### node-html-markdown (Recommended)

```bash
npm install node-html-markdown
```

```javascript
const { NodeHtmlMarkdown } = require('node-html-markdown');

const html = '<h1>Hello World</h1><p>This is a test.</p>';
const markdown = NodeHtmlMarkdown.translate(html);
console.log(markdown);
```

### markdownify (Python Alternative)

```bash
pip install markdownify
```

```python
from markdownify import markdownify

html = '<h1>Hello World</h1><p>This is a test.</p>'
markdown = markdownify(html, heading_style="ATX")
print(markdown)
```

## Conclusion

**For most use cases, use node-html-markdown.** It provides the best balance of accuracy, feature preservation, and readability. It's particularly well-suited for:
- Technical documentation with code examples
- Content with tables
- General HTML→Markdown conversion needs

**Use markdownify** if:
- You're in a Python environment
- Your content doesn't rely heavily on syntax-highlighted code blocks
- You prioritize readability over technical accuracy

**Avoid turndown** unless you can guarantee your content will never contain tables.

**Use pandoc** only if you need its broader document conversion capabilities or are already integrated with Pandoc workflows.

**Avoid html2text** unless you're maintaining legacy systems that already use it.

## Research Artifacts

This research includes:
- 20 HTML test cases (`test-cases/`)
- Conversion scripts for all tools
- Output from all tools for all test cases (`outputs/`)
- Automated evaluation script (`evaluate.py`)
- Raw evaluation results (`evaluation-results.json`)

To reproduce this research:
```bash
node test-turndown.js
node test-node-html-markdown.js
python3 test-python-tools.py
./test-pandoc.sh
python3 evaluate.py
```

---

**Research Date:** 2025-11-10
**Tools Evaluated:** turndown, node-html-markdown, html2text, markdownify, pandoc
**Test Cases:** 20 representative HTML samples
**Evaluation Criteria:** 39 objective checks + subjective readability assessment
