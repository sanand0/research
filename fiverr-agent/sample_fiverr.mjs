import { chromium } from "playwright";
import fs from "node:fs/promises";

const cdp = "http://localhost:9222";
const queries = [
  "data entry",
  "web scraping",
  "python automation",
  "excel automation",
  "powerpoint presentation",
];

function textOf(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function extractCards() {
  const anchors = [...document.querySelectorAll("a[href*='/services/'], a[href*='/gig/']")];
  const seen = new Set();
  const cards = [];
  for (const a of anchors) {
    const href = a.href;
    if (seen.has(href)) continue;
    seen.add(href);
    const root = a.closest("article, li, div[class*='gig'], div[class*='card']") ?? a.parentElement;
    const text = textOf(root?.innerText ?? a.innerText);
    if (text.length < 20) continue;
    const price = text.match(/(?:From|Starting at|US\$|\$)\s*[\d,]+(?:\.\d{2})?/i)?.[0] ?? "";
    cards.push({ title: textOf(a.innerText).slice(0, 180), href, price, text: text.slice(0, 700) });
  }
  return cards.slice(0, 80);
}

async function main() {
  const browser = await chromium.connectOverCDP(cdp);
  const context = browser.contexts()[0];
  const existing = context.pages().find((p) => p.url().includes("fiverr.com")) ?? context.pages()[0];
  const results = [];
  for (const query of queries) {
    const url = `https://www.fiverr.com/search/gigs?query=${encodeURIComponent(query)}&source=main_banner&ref_ctx_id=&search_in=everywhere&search-autocomplete-original-term=${encodeURIComponent(query)}`;
    const page = await context.newPage();
    const responses = [];
    page.on("response", async (response) => {
      const u = response.url();
      if (!u.includes("fiverr.com")) return;
      const ct = response.headers()["content-type"] ?? "";
      if (!ct.includes("json") && !u.includes("/api/")) return;
      responses.push({ url: u, status: response.status(), contentType: ct });
    });
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForTimeout(5000);
    const cards = await page.evaluate(extractCards);
    const title = await page.title();
    const bodyText = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
    results.push({ query, url, title, cards, responses: responses.slice(0, 80), bodySample: textOf(bodyText).slice(0, 1200) });
    await page.close();
  }
  await fs.writeFile("sample_fiverr_results.json", JSON.stringify(results, null, 2));
  await existing.bringToFront().catch(() => {});
  await browser.close();
  console.log(JSON.stringify(results.map((r) => ({ query: r.query, title: r.title, cards: r.cards.length, responses: r.responses.length, first: r.cards[0] })), null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
