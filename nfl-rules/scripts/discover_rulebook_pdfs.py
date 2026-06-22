#!/usr/bin/env python3
# /// script
# dependencies = ["beautifulsoup4", "lxml", "pandas", "pypdf", "requests", "pyarrow", "tabulate"]
# ///
"""Discover official NFL rulebook PDF candidates.

Resumable:
- candidate list is regenerated deterministically
- PDFs are cached in data/raw/rulebooks/
- existing cached PDFs are reused unless --refresh is passed

Outputs:
- data/interim/rulebook_pdf_candidates.csv/.parquet
- data/interim/rulebook_pdf_discovery_report.md
- cached candidate PDFs under data/raw/rulebooks/
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RULEBOOK_RAW = RAW / "rulebooks"
INTERIM = ROOT / "data" / "interim"
UA = "Mozilla/5.0 (compatible; nfl-rules-research/0.1)"

SEEDS = [
    "https://operations.nfl.com/xml-sitemap",
    "https://operations.nfl.com/sitemap.xml",
    "https://operations.nfl.com/the-rules/nfl-rulebook/",
    "https://operations.nfl.com/the-rules/",
]
YEARS = list(range(2010, 2027))

KNOWN_URLS = {
    2022: ["https://operations.nfl.com/media/5kvgzyss/2022-nfl-rulebook-final.pdf"],
}

PATTERN_URLS = [
    "https://operations.nfl.com/media/{slug}/{year}-nfl-rulebook-final.pdf",
    "https://operations.nfl.com/media/{slug}/{year}-nfl-rulebook.pdf",
    "https://operations.nfl.com/media/default/rulebook/{year}-nfl-rulebook-final.pdf",
    "https://operations.nfl.com/media/default/rulebook/{year}-nfl-rulebook.pdf",
]
# Slugs already seen in NFL Ops media links or likely from cached files. This is intentionally conservative.
KNOWN_MEDIA_SLUGS = ["5kvgzyss", "dxfj3uak", "utmx4j5y", "e4sneelu", "24emxacq", "qdbs4r4z", "gk2q0fpn", "lbr5c0k2"]


def parse_years_arg(text: str | None) -> list[int]:
    if not text:
        return YEARS
    out=[]
    for part in text.split(','):
        part=part.strip()
        if not part:
            continue
        if '-' in part:
            a,b=[int(x) for x in part.split('-',1)]
            out.extend(range(a,b+1))
        else:
            out.append(int(part))
    return sorted(set(out))


def norm_url(url: str) -> str:
    return url.strip().replace(" ", "%20")


def fetch_text(url: str) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code >= 400:
            return ""
        return r.text
    except Exception:
        return ""


def collect_urls_from_web() -> set[str]:
    urls: set[str] = set()
    for seed in SEEDS:
        text = fetch_text(seed)
        if not text:
            continue
        urls.update(re.findall(r"https?://[^\s\"'<>]+\.pdf", text, flags=re.I))
        urls.update(re.findall(r"<loc>(.*?)</loc>", text, flags=re.I))
        soup = BeautifulSoup(text, "lxml")
        for a in soup.find_all("a"):
            href = a.get("href") or ""
            if href and href.lower().split("?")[0].endswith(".pdf"):
                urls.add(urljoin(seed, href))
    return {norm_url(u) for u in urls if "operations.nfl.com" in u.lower() and ".pdf" in u.lower()}


def collect_urls_from_cached_html() -> set[str]:
    urls: set[str] = set()
    for path in RAW.glob("*.html"):
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        urls.update(re.findall(r"https?://[^\s\"'<>]+\.pdf", text, flags=re.I))
        soup = BeautifulSoup(text, "lxml")
        for a in soup.find_all("a"):
            href = a.get("href") or ""
            if href and href.lower().split("?")[0].endswith(".pdf"):
                urls.add(urljoin("https://operations.nfl.com/", href))
    return {norm_url(u) for u in urls if "operations.nfl.com" in u.lower() and ".pdf" in u.lower()}


def infer_year_from_url(url: str) -> int | None:
    m = re.search(r"\b(20\d{2})\b", url)
    return int(m.group(1)) if m else None


def candidate_urls(include_pattern_probes: bool = False, years: list[int] | None = None) -> list[dict]:
    rows: list[dict] = []
    years = years or YEARS
    found = set()
    def add(url: str, source: str, expected_year: int | None = None):
        u = norm_url(url)
        if not u or u in found:
            return
        found.add(u)
        y = expected_year or infer_year_from_url(u)
        is_rulebookish = bool(re.search(r"rulebook|rule-book|playing-rules", u, flags=re.I))
        rows.append({"url": u, "candidate_source": source, "expected_year": y, "is_rulebookish_url": is_rulebookish})

    for y, urls in KNOWN_URLS.items():
        for u in urls:
            add(u, "known_url", y)

    for u in sorted(collect_urls_from_web() | collect_urls_from_cached_html()):
        if ".pdf" in u.lower() and re.search(r"rulebook|rule-book|playing-rules|rules.*pdf|proposal", u, flags=re.I):
            add(u, "sitemap_or_cached_link")

    if include_pattern_probes:
        for y in years:
            for slug in KNOWN_MEDIA_SLUGS:
                for pat in PATTERN_URLS:
                    add(pat.format(year=y, slug=slug), "pattern_probe", y)
    return rows


def local_pdf_path(url: str, expected_year: int | None) -> Path:
    RULEBOOK_RAW.mkdir(parents=True, exist_ok=True)
    base = Path(urlparse(url).path).name or "candidate.pdf"
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base)
    prefix = str(expected_year or infer_year_from_url(url) or "unknown")
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    return RULEBOOK_RAW / f"{prefix}-{h}-{base}"


def probe(url: str, expected_year: int | None, refresh: bool = False) -> dict:
    out = {
        "status": "unknown",
        "http_status": None,
        "content_type": "",
        "content_length": None,
        "cached_path": "",
        "bytes": 0,
        "sha256": "",
        "pdf_pages": None,
        "pdf_title_text": "",
        "pdf_years_seen": "",
        "rulebook_score": 0,
        "error": "",
    }
    path = local_pdf_path(url, expected_year)
    try:
        if path.exists() and path.stat().st_size > 0 and not refresh:
            content = path.read_bytes()
            out.update({"status": "cached", "cached_path": str(path), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        else:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=18, allow_redirects=True)
            out["http_status"] = r.status_code
            out["content_type"] = r.headers.get("content-type", "")
            out["content_length"] = r.headers.get("content-length", "")
            if r.status_code != 200:
                out["status"] = f"http_{r.status_code}"
                return out
            content = r.content
            if not content.startswith(b"%PDF"):
                out["status"] = "not_pdf"
                out["bytes"] = len(content)
                return out
            path.write_bytes(content)
            out.update({"status": "found", "cached_path": str(path), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        try:
            reader = PdfReader(str(path))
            out["pdf_pages"] = len(reader.pages)
            first_text = "\n".join((p.extract_text() or "")[:2000] for p in reader.pages[:3])
            first_text_norm = re.sub(r"\s+", " ", first_text).strip()
            out["pdf_title_text"] = first_text_norm[:800]
            years = sorted(set(re.findall(r"\b20\d{2}\b", first_text_norm)))
            out["pdf_years_seen"] = ";".join(years)
            score = 0
            lt = first_text_norm.lower()
            if "rulebook" in lt: score += 4
            if "playing rules" in lt: score += 3
            if "rules changes" in lt or "rule changes" in lt: score += 2
            if str(expected_year or "") in first_text_norm: score += 2
            out["rulebook_score"] = score
            if out["status"] == "cached":
                out["status"] = "found_cached"
        except Exception as e:
            out["error"] = f"pdf_parse:{type(e).__name__}:{e}"
        return out
    except Exception as e:
        out["status"] = "error"
        out["error"] = f"{type(e).__name__}:{e}"
        return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--include-pattern-probes", action="store_true", help="Probe broad guessed media URL patterns; slower")
    parser.add_argument("--years", default=None, help="Year/range filter for pattern probes, e.g. 2019-2024")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many generated candidates")
    parser.add_argument("--limit", type=int, default=None, help="Probe at most this many candidates")
    args = parser.parse_args()
    INTERIM.mkdir(parents=True, exist_ok=True)
    years = parse_years_arg(args.years)
    candidates = candidate_urls(include_pattern_probes=args.include_pattern_probes, years=years)
    if args.offset or args.limit is not None:
        candidates = candidates[args.offset:(args.offset + args.limit) if args.limit is not None else None]
    rows = []
    for i, c in enumerate(candidates, 1):
        p = probe(c["url"], c.get("expected_year"), refresh=args.refresh)
        row = {**c, **p}
        rows.append(row)
        if p["status"].startswith("found"):
            print(f"FOUND {row.get('expected_year')} score={row['rulebook_score']} {row['url']}")
    base_cols = ["url", "candidate_source", "expected_year", "is_rulebookish_url", "status", "http_status", "content_type", "content_length", "cached_path", "bytes", "sha256", "pdf_pages", "pdf_title_text", "pdf_years_seen", "rulebook_score", "error"]
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=base_cols)
    else:
        for c in base_cols:
            if c not in df.columns:
                df[c] = ""
        df = df.sort_values(["rulebook_score", "status", "expected_year", "url"], ascending=[False, True, True, True])
    out_csv = INTERIM / "rulebook_pdf_candidates.csv"
    df.to_csv(out_csv, index=False)
    df.to_parquet(INTERIM / "rulebook_pdf_candidates.parquet", index=False)
    found = df[df["status"].astype(str).str.startswith("found", na=False)].copy()
    report = []
    report.append("# Rulebook PDF discovery report\n")
    report.append(f"Candidates probed: {len(df)}")
    report.append(f"Pattern probes: {args.include_pattern_probes}; years: {args.years or 'default'}; offset: {args.offset}; limit: {args.limit}")
    report.append(f"Found/cached PDFs: {len(found)}\n")
    if len(found):
        cols = ["expected_year", "status", "rulebook_score", "pdf_pages", "pdf_years_seen", "url", "cached_path"]
        report.append(found[cols].to_markdown(index=False))
    report.append("\n## Next action\n")
    report.append("Inspect high-scoring found PDFs, then add official annual rulebook parsers to `build_rules_csv.py` when the PDF has a clear `Rules Changes` page.")
    (INTERIM / "rulebook_pdf_discovery_report.md").write_text("\n".join(report) + "\n")
    print(f"wrote {out_csv} rows={len(df)} found={len(found)}")


if __name__ == "__main__":
    main()
