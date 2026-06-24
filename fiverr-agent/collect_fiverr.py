import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

QUERIES = [
    "data entry",
    "python automation",
    "excel automation",
    "google sheets automation",
    "powerpoint presentation",
    "data cleaning",
    "pdf to excel",
    "lead generation",
    "market research",
    "wordpress bug fix",
    "shopify product upload",
    "resume writing",
]

BADGES = {
    "Ad",
    "Level 1",
    "Level 2",
    "Top Rated",
    "Fiverr’s Choice",
    "Vetted Pro",
    "Offers video consultations",
}


@dataclass
class Listing:
    query: str
    title: str
    seller: str
    seller_meta: str
    rating: str
    reviews: str
    listed_price: str
    search_url: str


def search_url(query: str) -> str:
    q = quote(query)
    return (
        f"https://www.fiverr.com/search/gigs?query={q}"
        f"&source=main_banner&search_in=everywhere&search-autocomplete-original-term={q}"
    )


def clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def looks_like_seller(line: str) -> bool:
    if len(line) > 70 or line in BADGES:
        return False
    if re.match(r"^[A-Z](?:\s|$)", line):
        return True
    return bool(re.match(r"^[A-Z][A-Za-z0-9 ._-]{1,45}$", line))


def parse_listings(query: str, url: str, text: str) -> list[Listing]:
    lines = clean_lines(text)
    listings = []
    for index, line in enumerate(lines):
        if not line.lower().startswith("i will "):
            continue
        seller = ""
        meta = []
        for prev in reversed(lines[max(0, index - 6) : index]):
            if prev in BADGES:
                meta.append(prev)
            elif not seller and looks_like_seller(prev):
                seller = prev
                break
        tail = lines[index + 1 : index + 8]
        joined_tail = " ".join(tail)
        rating_match = re.search(r"\b([0-5]\.\d)\s+\(([^)]+)\)", joined_tail)
        price_match = re.search(r"From\s+₹[\d,]+", joined_tail)
        listings.append(
            Listing(
                query=query,
                title=line,
                seller=seller,
                seller_meta=", ".join(reversed(meta)),
                rating=rating_match.group(1) if rating_match else "",
                reviews=rating_match.group(2) if rating_match else "",
                listed_price=price_match.group(0) if price_match else "",
                search_url=url,
            )
        )
    return listings


def main() -> None:
    all_results = []
    page_records = []
    start_index = int(os.environ.get("START_INDEX", "0"))
    end_index = int(os.environ.get("END_INDEX", str(len(QUERIES))))
    selected_queries = QUERIES[start_index:end_index]
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = next((candidate for candidate in context.pages if "fiverr.com" in candidate.url), context.pages[0])
        for query in selected_queries:
            url = search_url(query)
            page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            page.wait_for_timeout(5_500)
            title = page.title()
            body = page.locator("body").inner_text(timeout=8_000)
            is_blocked = "It needs a human touch" in body or "PXCR" in body
            listings = [] if is_blocked else parse_listings(query, url, body)
            all_results.extend(listings)
            page_records.append(
                {
                    "query": query,
                    "url": url,
                    "page_title": title,
                    "blocked": is_blocked,
                    "listing_count": len(listings),
                    "sample": body[:2000],
                }
            )
            Path("fiverr_collection_pages.json").write_text(
                json.dumps(page_records, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            Path("fiverr_listings.json").write_text(
                json.dumps([asdict(item) for item in all_results], indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(json.dumps(page_records[-1], ensure_ascii=False), flush=True)
            if is_blocked:
                break
            time.sleep(6)
        browser.close()
    Path("fiverr_collection_pages.json").write_text(
        json.dumps(page_records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    Path("fiverr_listings.json").write_text(
        json.dumps([asdict(item) for item in all_results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {len(all_results)} listings from {len(page_records)} pages")


if __name__ == "__main__":
    main()
