# PDF Fuzzy Linker

Minimal FastAPI + vanilla JS demo that lets users upload a PDF, render it in-browser, and highlight fuzzy-matched text snippets. The app stores each upload under a unique ID, shows search matches with clickable jumps, and keeps the query string in the URL for deep links.

## Running locally

```bash
uv run main.py  # serves at http://localhost:8000
```

## How it works
- Uploads are sent as raw bytes with an `x-filename` header to avoid multipart dependencies.
- PDFs are rendered with PDF.js in the browser; a text layer is used for in-page highlights.
- A lightweight fuzzy matcher (Levenshtein-based) ranks nearby text snippets and updates both the highlights and a match list.
- Search terms are reflected in the URL (`/docs/<id>?q=term`) so pages are bookmarkable.

## Tests
- Python API checks: `pytest`
- Front-end fuzzy logic check: `npm test`
- Lint: `npm run lint`
