# Research

- 10 Nov 2025: [`codex-fastapi-streaming`](codex-fastapi-streaming/). FastAPI + SSE wrapper lets you stream Codex CLI in a browser.
  - 11 Nov 2025: [`codex-fastapi-streaming-token`](codex-fastapi-streaming-token/). Run Codex CLI on the browser with token-by-token streaming. Not sure if Codex actually sends tokens one-by-one, so [`codex-fastapi-streaming`](codex-fastapi-streaming/) may be better.
- 10 Nov 2025: [`pyodide-pandas-breakeven`](pyodide-pandas-breakeven/). Use native JS instead of Pyodide + Pandas—the 30s load penalty means the browser never reaches a performance break-even.
- 10 Nov 2025: [`uv-cache-mount-benchmark`](uv-cache-mount-benchmark/). BuildKit cache mounts cut `uv pip install` from 11.7s to 1.7s, so ship cache mounts (or bind mounts) for any repeatable Docker build.
- 10 Nov 2025: [`gh-auth-dev-containers`](gh-auth-dev-containers/). Use the `GH_TOKEN` env var (with optional hosts.yml mount) to share GitHub CLI auth across dev containers despite keyring limitations.
- 11 Nov 2025: [`json-tools-benchmark`](json-tools-benchmark/). jaq is ~40% faster than jq, while native Node excels at heavy transforms and nearly every tool now streams results.
- 11 Nov 2025: [`dom-markdown-extractor-eval`](dom-markdown-extractor-eval/). Use `node-html-markdown` for HTML to Markdown. Has 97% accuracy. `markdownify` is a readability-focused backup, and turndown still can't handle tables.
- 11 Nov 2025: [`readability-extractors-evaluation`](readability-extractors-evaluation/). Mozilla Readability + Turndown yields the cleanest article content with stable heading IDs—trafilatura is faster but loses IDs, while html2text/markdownify include too much chrome.
- 17 Nov 2025: [`fuzzy-pdf-search`](fuzzy-pdf-search/). PDF.js + Fuse.js web app enables fuzzy text search in PDFs with shareable bookmark URLs—typos like "fuzzi matcing" still find "fuzzy matching".
- 18 Nov 2025: [`wikipedia-ai-names`](wikipedia-ai-names/). Exhaustive search of 24,086 Wikipedia pages found 11 people whose names begin and end with "AI": shortest is Ai Nagai (8 chars), longest are Aisha Yousef al-Mannai and Aishwarya Rai Bachchan (22 chars each).
- 19 Nov 2025: [`word-file-splitter-gui`](word-file-splitter-gui/). Cross-platform Python GUI app splits Word docs by delimiter and batch renames files with numeric/alphabetic/roman suffixes—44 tests pass, builds to standalone exe.
- 19 Nov 2025: [`india-data-professionals`](india-data-professionals/). GitHub API yields 790 data scientists/engineers in India (42% Bangalore-based) with best ROI—expandable to 15K-100K via additional keywords/locations/sources like Kaggle.
- 22 Nov 2025: [`jakarta-schools`](jakarta-schools/). Compiled 105 private K-12 schools in Jakarta/Greater Jakarta with contacts—15 named decision-makers (principals, heads), 85 unique schools across SPK, Christian, Islamic, and national-plus categories.
- 22 Nov 2025: [`repeated-letter-words`](repeated-letter-words/). Analyzed 370K English words to find 333 where >50% of letters are the same letter—POSSESSES (56% S) is the longest common example; includes Gardner-style and Munroe-style articles.
- 02 Jun 2026: [`nfl-rules`](nfl-rules/). Analysis of NFL rule changes.
- 12 Jun 2026: [`2026-06-test-exam`](2026-06-test-exam/). Solved and submitted the AI-Era Capability Test at 9/10; the only blocked point was an external AIPipe judge rejecting its manually entered bearer token.
- 23 Jun 2026: [`xarray-linspace`](xarray-linspace/). Fixes [Should RangeIndex.linspace handle num=1 like numpy.linspace?](https://github.com/pydata/xarray/pull/11401)
