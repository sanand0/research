#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["fastapi>=0.115.0", "uvicorn>=0.30.0", "python-multipart>=0.0.9"]
# ///

"""FastAPI app serving PDF fuzzy search demo."""

from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Body, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "uploads"
WEB_DIR = BASE_DIR / "web"

DATA_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.mount("/files", StaticFiles(directory=DATA_DIR), name="files")


HOME_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PDF Fuzzy Linker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
    <link href="https://cdn.jsdelivr.net/npm/pdfjs-dist@4.4.168/web/pdf_viewer.min.css" rel="stylesheet" />
  </head>
  <body class="bg-light">
    <main class="container py-5">
      <h1 class="mb-4">Upload a PDF</h1>
      <form id="upload-form" class="card p-4 bg-white shadow-sm">
        <div class="mb-3">
          <label for="file" class="form-label">Choose a PDF file</label>
          <input class="form-control" type="file" name="file" id="file" accept="application/pdf" required />
        </div>
        <div class="d-flex align-items-center gap-3">
          <button class="btn btn-primary" type="submit">Upload and open</button>
          <span id="upload-status" class="text-muted small"></span>
        </div>
      </form>
    </main>
    <script type="module">
      const form = document.getElementById('upload-form')
      const fileInput = document.getElementById('file')
      const status = document.getElementById('upload-status')
      form.addEventListener('submit', async (event) => {
        event.preventDefault()
        const file = fileInput.files?.[0]
        if (!file) {
          status.textContent = 'Please pick a PDF first.'
          status.className = 'text-danger small'
          return
        }
        status.textContent = 'Uploading…'
        status.className = 'text-muted small'
        try {
          const response = await fetch('/upload', {
            method: 'POST',
            headers: {
              'x-filename': file.name,
              'content-type': file.type || 'application/pdf',
            },
            body: await file.arrayBuffer(),
          })
          if (response.redirected) {
            window.location.href = response.url
            return
          }
          if (response.ok && response.headers.get('location')) {
            window.location.href = response.headers.get('location')
            return
          }
          status.textContent = 'Upload failed. Please try again.'
          status.className = 'text-danger small'
        } catch (error) {
          status.textContent = 'Upload failed. Please try again.'
          status.className = 'text-danger small'
        }
      })
    </script>
  </body>
</html>
"""


DOC_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PDF Fuzzy Linker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
    <style>
      .pdf-container { position: relative; }
      .highlight { background: rgba(255, 235, 59, 0.6); }
      #loading-banner { position: fixed; top: 0; width: 100%; z-index: 100; }
    </style>
  </head>
  <body class="bg-light">
    <div id="loading-banner" class="alert alert-info text-center mb-0">Loading PDF…</div>
    <header class="bg-white shadow-sm">
      <div class="container py-3 d-flex flex-wrap align-items-center gap-3">
        <a class="navbar-brand" href="/">PDF Fuzzy Linker</a>
        <form class="d-flex flex-grow-1" role="search" onsubmit="return false">
          <input id="search-input" class="form-control me-2" type="search" placeholder="Search text" aria-label="Search" />
        </form>
      </div>
    </header>
    <main class="container py-3">
      <div class="row">
        <div class="col-md-9">
          <div id="pdf-root" class="d-flex flex-column gap-3"></div>
        </div>
        <div class="col-md-3">
          <h5>Matches</h5>
          <div id="matches"></div>
        </div>
      </div>
    </main>
    <script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@4.4.168/build/pdf.min.js"></script>
    <script>pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.4.168/build/pdf.worker.min.js";</script>
    <script>window.PDF_FILE_URL = "/files/{pdf_name}";</script>
    <script type="module" src="/static/viewer.js"></script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Serve upload form."""
    return HTMLResponse(content=HOME_HTML)


@app.post("/upload")
async def upload(
    content: Annotated[bytes, Body(...)],
    x_filename: Annotated[str | None, Header(alias="x-filename")] = None,
    content_type: Annotated[str | None, Header(alias="content-type")] = None,
) -> RedirectResponse:
    """Store uploaded PDF and redirect to viewer."""
    if content_type not in {None, "application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    pdf_id = uuid4().hex
    dest = DATA_DIR / f"{pdf_id}.pdf"
    dest.write_bytes(content)
    return RedirectResponse(url=f"/docs/{pdf_id}", status_code=303)


@app.get("/docs/{pdf_id}", response_class=HTMLResponse)
def view_pdf(pdf_id: str) -> HTMLResponse:
    """Render the viewer page."""
    pdf_path = DATA_DIR / f"{pdf_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    html = DOC_TEMPLATE.replace("{pdf_name}", pdf_path.name)
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
