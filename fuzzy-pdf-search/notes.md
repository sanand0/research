# Fuzzy PDF Search - Development Notes

## Objective
Create a minimal web app that allows fuzzy text matching and highlighting in PDFs with shareable URLs.

## Key Requirements
- Upload PDF → parse and store
- Render PDF in browser
- Fuzzy search with highlighting
- URL-based bookmarking: `/pdf-id?q=search-string`
- Show match list, highlight first match, allow clicking other matches

## Research Phase

### PDF Rendering Approaches

**Option 1: PDF.js (Mozilla)**
- Industry standard for browser-based PDF rendering
- Renders PDF as canvas elements
- Built-in text layer for selection and search
- Pros: Full control, text layer access, widely used
- Cons: Larger library, more complex setup

**Option 2: Native Browser PDF Rendering (embed/iframe)**
- Use `<embed>` or `<iframe>` with PDF URL
- Pros: Zero dependencies, native performance
- Cons: No programmatic access to text layer, can't highlight specific text

**Option 3: pdf-lib or other parsing libraries**
- Parse PDF structure but don't render
- Would need to convert to images or other format
- Not suitable for our use case

**Decision: PDF.js** is the clear winner because we need text layer access for highlighting.

### Fuzzy Matching Approaches

**Option 1: Fuse.js**
- Popular fuzzy search library
- Good for searching through arrays of items
- Configurable thresholds and scoring

**Option 2: string-similarity (Dice's coefficient)**
- Simple string similarity scoring
- Lightweight

**Option 3: Custom implementation using Levenshtein distance**
- Full control but more work

**Option 4: fuzzysort**
- Fast fuzzy searching
- Designed for autocomplete-style searching

**Decision: Fuse.js** - well-maintained, configurable, good for document search.

### Backend Approach

**Option 1: Node.js + Express**
- Lightweight, JavaScript ecosystem
- Easy PDF text extraction with pdf-parse

**Option 2: Python + Flask**
- PyPDF2 or pdfplumber for extraction
- Good PDF ecosystem

**Decision: Node.js + Express** - keeps everything in JS, simpler stack.

### Text Extraction Strategy
- Extract text page by page
- Store page numbers with text for navigation
- Create searchable text index on upload

## Architecture Design

```
Frontend:
- Upload page (index.html)
- PDF viewer page (view.html)
- Uses PDF.js for rendering
- Fuse.js for client-side fuzzy search

Backend:
- Express.js server
- pdf-parse for text extraction
- Store PDFs and extracted text
- Unique ID generation for PDFs
```

## Implementation Notes

### Backend Implementation
- Express.js server with multer for file uploads
- pdf-parse for text extraction (required proper PDF format)
- UUID for unique PDF identifiers
- In-memory storage (Map) for metadata and extracted text
- Routes: POST /api/upload, GET /api/pdf/:id, GET /api/pdf/:id/file, GET /view/:id

### Frontend Implementation
- PDF.js 3.11.174 from CDN for rendering
- Fuse.js 7.0.0 for fuzzy searching with threshold 0.4
- Text layer overlaid on canvas for highlighting
- URL query parameter support for bookmarkable searches
- Debounced search input (300ms delay)
- Match list with click-to-navigate

### Testing Results
- PDF upload and text extraction: Working
- Multi-page PDF support: Working
- Fuzzy search: Working (e.g., "fuzzi matcing" finds "fuzzy matching")
- URL bookmarking: Working (/view/pdf-id?q=search-string)
- Match highlighting: Working (yellow highlights with orange for active)
- Match list navigation: Working

### Issues Encountered
1. **pdfkit XRef error**: Initial PDFs created had "bad XRef entry" errors. Fixed by ensuring the write stream properly finishes before process exits.
2. **Text layer positioning**: Required using PDF.js viewport transforms to position text spans correctly over the canvas.
3. **Fuzzy search granularity**: Split text into sentences/chunks rather than word-by-word for meaningful matches.

### Key Decisions
- Used CDN for PDF.js and Fuse.js to keep the codebase lightweight
- Threshold of 0.4 for fuzzy matching provides good balance between tolerance and accuracy
- In-memory storage is fine for demo; production would need persistent database
- Client-side search (after text extraction) for responsive performance

