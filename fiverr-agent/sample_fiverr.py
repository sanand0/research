import json
import re
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

QUERIES = [
    "data entry",
    "web scraping",
    "python automation",
    "excel automation",
    "powerpoint presentation",
]


def search_url(query: str) -> str:
    q = quote(query)
    return (
        f"https://www.fiverr.com/search/gigs?query={q}"
        f"&source=main_banner&search_in=everywhere&search-autocomplete-original-term={q}"
    )


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        existing = next((page for page in context.pages if "fiverr.com" in page.url), context.pages[0])
        results = []
        for query in QUERIES:
            page = context.new_page()
            responses = []

            def on_response(response):
                url = response.url
                if "fiverr.com" not in url:
                    return
                content_type = response.headers.get("content-type", "")
                if "json" not in content_type and "/api/" not in url:
                    return
                responses.append(
                    {"url": url, "status": response.status, "content_type": content_type[:120]}
                )

            page.on("response", on_response)
            url = search_url(query)
            page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            page.wait_for_timeout(6_000)
            cards = page.evaluate(
                """
                () => {
                  const textOf = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
                  const anchors = [...document.querySelectorAll("a[href*='/categories/'], a[href*='/services/'], a[href*='/gig/']")];
                  const seen = new Set();
                  const cards = [];
                  for (const a of anchors) {
                    const href = a.href;
                    if (!href.includes('/categories/') && !href.includes('/services/')) continue;
                    if (seen.has(href)) continue;
                    seen.add(href);
                    const root = a.closest("article, li, div[class*='gig'], div[class*='card'], div") || a.parentElement;
                    const text = textOf(root?.innerText || a.innerText);
                    if (text.length < 20) continue;
                    const price = (text.match(/(?:From|Starting at|US\\$|\\$)\\s*[\\d,]+(?:\\.\\d{2})?/i) || [''])[0];
                    cards.push({ title: textOf(a.innerText).slice(0, 180), href, price, text: text.slice(0, 800) });
                  }
                  return cards.slice(0, 100);
                }
                """
            )
            body = re.sub(r"\s+", " ", page.locator("body").inner_text(timeout=5_000)).strip()
            results.append(
                {
                    "query": query,
                    "url": url,
                    "title": page.title(),
                    "cards": cards,
                    "responses": responses[:120],
                    "body_sample": body[:1500],
                }
            )
            page.close()
        existing.bring_to_front()
        browser.close()
    Path("sample_fiverr_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(
        json.dumps(
            [
                {
                    "query": item["query"],
                    "title": item["title"],
                    "cards": len(item["cards"]),
                    "responses": len(item["responses"]),
                    "first": item["cards"][0] if item["cards"] else None,
                }
                for item in results
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
