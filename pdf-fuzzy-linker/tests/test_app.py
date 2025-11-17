import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from main import home, upload, view_pdf

sample_pdf = b"%PDF-1.4\n1 0 obj<<>>endobj\nxref\n0 1\n0000000000 65535 f \ntrailer<<>>\nstartxref\n0\n%%EOF"


def test_home_page_shows_upload_form():
    resp = home()
    assert resp.status_code == 200
    assert "upload" in resp.body.decode()


def test_upload_redirects_to_pdf_page(tmp_path, monkeypatch):
    monkeypatch.setattr("main.DATA_DIR", tmp_path)
    response = asyncio.run(upload(sample_pdf, x_filename="test.pdf", content_type="application/pdf"))
    assert response.status_code == 303
    assert response.headers["location"].startswith("/docs/")
    saved = next(tmp_path.glob("*.pdf"))
    page_html = view_pdf(saved.stem)
    assert "pdf-root" in page_html.body.decode()
