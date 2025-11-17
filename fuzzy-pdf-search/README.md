# Fuzzy PDF Search

A minimal web application that enables fuzzy text matching and highlighting in PDF documents with shareable, bookmarkable URLs.

## Features

- **PDF Upload**: Drag-and-drop or click to upload PDF files
- **Text Extraction**: Automatic extraction of text content on upload
- **Fuzzy Search**: Find text even with typos or spelling mistakes (e.g., "fuzzi matcing" finds "fuzzy matching")
- **Visual Highlighting**: Yellow highlights for matches, orange for active match
- **Match Navigation**: Sidebar list showing all matches with click-to-jump functionality
- **Shareable URLs**: URLs like `/view/pdf-id?q=search-string` are bookmarkable and work when shared
- **Multi-page Support**: Works with PDFs of any length

## Technology Stack

### Backend
- **Node.js + Express.js**: Lightweight web server
- **multer**: File upload handling
- **pdf-parse**: PDF text extraction (based on PDF.js)
- **uuid**: Unique identifier generation for uploaded PDFs

### Frontend
- **PDF.js 3.11.174**: Mozilla's PDF rendering library (from CDN)
- **Fuse.js 7.0.0**: Fuzzy searching with configurable thresholds (from CDN)
- **Vanilla JavaScript**: No frontend framework dependencies
- **Modern CSS**: Flexbox layout, responsive design

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Upload Page   │────>│   Express API    │────>│  In-Memory Store│
│   (index.html)  │     │   - /api/upload  │     │  - PDF files    │
└─────────────────┘     │   - /api/pdf/:id │     │  - Extracted text
                        └──────────────────┘     └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Viewer Page (viewer.html)                 │
│  ┌──────────┐  ┌─────────────────────┐  ┌─────────────────┐    │
│  │ Search   │  │   PDF Rendering     │  │   Match List    │    │
│  │ Input    │  │   (PDF.js canvas    │  │   (Clickable)   │    │
│  │          │  │   + text layer)     │  │                 │    │
│  └──────────┘  └─────────────────────┘  └─────────────────┘    │
│                         ▲                                       │
│                         │                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Fuse.js Fuzzy Search                     │      │
│  │  - Threshold: 0.4 (tolerates typos)                  │      │
│  │  - Searches extracted text chunks                     │      │
│  │  - Returns scored matches                             │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## How It Works

1. **Upload Phase**:
   - User uploads PDF via drag-and-drop or file picker
   - Server extracts text using pdf-parse
   - PDF and text are stored with a unique 8-character ID
   - User is redirected to `/view/{pdf-id}`

2. **Viewing Phase**:
   - PDF.js renders each page as a canvas element
   - A transparent text layer is overlaid for highlighting
   - Extracted text is split into searchable chunks (sentences)

3. **Searching Phase**:
   - User types in search box (debounced 300ms)
   - Fuse.js performs fuzzy search with scoring
   - Matching text elements are highlighted yellow
   - URL is updated with query parameter
   - Match list shows top 50 results with similarity scores

4. **Navigation**:
   - Click any match in sidebar to jump to it
   - Active match highlighted in orange
   - Page automatically scrolls into view

## Why These Technologies?

### PDF.js (over native browser PDF rendering)
- Provides programmatic access to text layer
- Required for custom highlighting
- Industry standard, well-maintained by Mozilla

### Fuse.js (over manual Levenshtein distance)
- Battle-tested fuzzy search algorithm
- Configurable threshold and scoring
- Optimized for performance
- Handles word boundaries and partial matches well

### Express.js (over Python/Flask)
- Keeps entire stack in JavaScript
- Fast setup and minimal boilerplate
- pdf-parse integrates seamlessly

## Setup and Running

```bash
# Install dependencies
npm install

# Start server
npm start

# Access at http://localhost:3000
```

## Usage Example

1. Open http://localhost:3000
2. Upload a PDF file
3. You'll be redirected to `/view/{pdf-id}`
4. Type in the search box (try misspelling words!)
5. Click matches in the sidebar to navigate
6. Share the URL with the query parameter

## Limitations

- **In-memory storage**: PDFs are lost on server restart (production would need database)
- **Text layer accuracy**: Depends on PDF structure; scanned PDFs won't work
- **Highlighting precision**: Highlights entire text spans, not exact character ranges
- **Search granularity**: Searches sentence/paragraph chunks, not individual words
- **No authentication**: Any user can access any uploaded PDF by ID

## Future Improvements

1. **Persistent storage**: Database for PDFs and metadata
2. **Character-level highlighting**: Precise highlight of matched characters
3. **OCR support**: Text extraction from scanned/image PDFs
4. **Search history**: Track previous searches per document
5. **PDF annotations**: Allow users to add notes to matches
6. **Export matches**: Download list of matches with context
7. **Authentication**: User accounts and access control

## Key Insights

- **Fuzzy matching threshold of 0.4** provides good tolerance for typos while avoiding false positives
- **Sentence-level chunking** gives more meaningful search results than word-by-word
- **Client-side search** after initial text extraction provides responsive UX
- **URL query parameters** enable true bookmark/share functionality
- **Text layer overlay** is essential for highlighting without modifying the PDF itself
