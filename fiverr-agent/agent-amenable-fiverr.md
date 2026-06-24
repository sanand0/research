# Agent-amenable Fiverr opportunities

Scanned on 2026-06-24 via the logged-in Fiverr tab exposed on CDP at `localhost:9222`.

## Method

- Tried direct `curl` first against Fiverr search. It returned HTTP 403 from Fiverr/Cloudflare/PerimeterX, so direct scraping was not a reliable route.
- Used the live browser session through CDP and collected rendered search-result text. This avoided extracting or storing login cookies.
- Sampled 12 search areas, saved 610 parsed listings from 12 pages, and hit no block pages in the saved run.
- Raw evidence files: `fiverr_collection_pages_all.json`, `fiverr_listings_all.json`, plus batch files.

Search coverage:

| Query | Parsed listings | Fiverr page title |
|---|---:|---|
| data entry | 48 | Data Entry Services Online |
| python automation | 52 | Desktop Applications Development Services Online |
| excel automation | 52 | Data Processing Services Online |
| google sheets automation | 52 | Excel Macros & Formula Services |
| powerpoint presentation | 50 | Presentation Design Services |
| data cleaning | 48 | Data Cleaning Services |
| pdf to excel | 48 | Convert to an Editable File Services |
| lead generation | 52 | Fiverr Marketplace for The Lean Entrepreneur |
| market research | 52 | Market Research Reports & Analysis Services |
| wordpress bug fix | 52 | Fix Bugs with Web Programming Experts |
| shopify product upload | 52 | E-Commerce Product Uploading Services |
| resume writing | 52 | Resume Writing Services |

## Ranked opportunities

| Rank | Opportunity | Agent fit | Fiverr evidence | Price I would solve it at |
|---:|---|---|---|---|
| 1 | Python automation, web scraping, API scripts | Very high: code agents can implement, test, document, and deliver reproducible scripts. Best when the site/API is accessible and output schema is clear. | Examples from `python automation`: "create a python program or python script" from ₹1,494; "custom python web scraping, data mining, and web automation" from ₹2,987; "python web scraping, data extraction and automation" from ₹2,987 with 950 reviews. | ₹6,000 for a small script; ₹12,000-₹25,000 for scraping/API automation with retries, config, and tests. |
| 2 | Google Sheets / Excel automation | Very high: formulas, Apps Script, VBA-like logic, dashboards, and validation rules are structured and testable. | Examples: "automate google sheets using apps script" from ₹4,978; "automate google sheets, form, gmail, drive, calendar via apps script" from ₹5,974; "build dashboard, automate and fix excel or google sheets with advanced formula" from ₹2,987. | ₹5,000-₹8,000 for formulas/fixes; ₹10,000-₹18,000 for Apps Script workflows or dashboards. |
| 3 | Data cleaning, deduplication, formatting, CSV/Excel cleanup | Very high: agents can profile data, transform with scripts, emit before/after counts, and run deterministic checks. | Examples from `data cleaning`: "clean your excel contact database" from ₹1,494; "clean, format, merge and deduplicate excel or CSV data" from ₹1,494; "data entry, data management and cleaning, excel data clean" from ₹1,992. | ₹2,500-₹6,000 for one dataset; ₹8,000-₹15,000 for messy multi-file normalization with audit logs. |
| 4 | PDF/image to Excel/CSV/Word conversion | Very high if the source is digital or OCR quality is decent; easy to verify row counts and sample accuracy. | Examples from `pdf to excel`: "convert PDF, image, scanned documents into CSV file, excel, google sheets" from ₹996; "convert PDF to excel" from ₹996; "professionally convert PDF to excel with accuracy" from ₹1,992. | ₹1,500-₹3,000 for simple PDFs; ₹4,000-₹10,000 for scanned/OCR-heavy or table-reconstruction jobs. |
| 5 | Shopify / WooCommerce product uploads and CSV imports | High: agents can clean source catalogs, map fields, generate import CSVs, and spot-check products. Risk rises if manual admin access is required. | Examples from `shopify product upload`: "upload or add 400 products to your woocommerce and shopify store" from ₹996; "scrape product from website upload or import csv to shopify woocommerce listing" from ₹1,494; "product upload on woocommerce shopify etsy ebay amazon walmart from excel or CSV" from ₹996. | ₹2,000 for a clean 50-100 SKU import file; ₹5,000-₹12,000 for scraping, image handling, variants, and QA. |
| 6 | Scoped WordPress bug fixes | High for reproducible HTML/CSS/PHP/plugin errors with staging access; not ideal for vague performance, malware, hosting, or payment issues. | Examples from `wordpress bug fix`: "fix wordpress issues, fix wordpress errors, bugs" from ₹498; "quickly fix wordpress errors, fix wordpress bugs, fix wordpress issues, HTML CSS" from ₹996; "fix website bugs, wordpress, PHP, laravel, and javascript errors" from ₹2,987. | ₹2,500-₹5,000 for one reproducible bug; ₹8,000-₹15,000 for multi-issue cleanup with backups and regression checks. |
| 7 | B2B lead list building and validation | Medium-high: search, extraction, enrichment, and validation can be agent-run, but compliance, source quality, and bounce risk need explicit constraints. | Examples from `lead generation`: "verified b2b prospect email list" from ₹3,485; "targeted b2b linkedin leads and verified email list" from ₹2,489; "b2b leads, google map scraping, lead generation" from ₹996. | ₹4,000-₹8,000 per focused 100-250 verified leads; ₹12,000+ for enrichment, dedupe, and validation evidence. |
| 8 | Data entry / web research / copy-paste workflows | Medium-high: often agent-solvable, but many listings are commodity-priced and ambiguous. Best when output fields and sources are specified. | Examples from `data entry`: "data entry and typing with fast delivery" from ₹1,992; "accurate data entry, web research, copy paste and excel data entry jobs" from ₹1,992; "web scraping data mining data collection and data entry" from ₹498. | ₹2,000-₹5,000 for a bounded form/spreadsheet task; avoid open-ended "virtual assistant" scopes unless converted into a checklist. |
| 9 | PowerPoint / Google Slides redesign from provided content | Medium: agents are strong at structure, rewriting, charts, and templates; visual taste and brand nuance require review. | Examples from `powerpoint presentation`: "design powerpoint presentation and pitch deck" from ₹4,978; "create powerpoint presentation design, canva and google slides" from ₹6,969; "research and create powerpoint presentation on any topic" from ₹9,956. | ₹4,000-₹8,000 for cleanup/redesign under 15 slides; ₹12,000-₹25,000 for research-backed pitch/story decks. |
| 10 | Narrow market / competitor research | Medium: source collection, tables, citations, SWOT/TAM drafts are agent-friendly; strategy recommendations need human review. | Examples from `market research`: "market research, swot analysis and competitor analysis" from ₹7,467; "startup market research and competitor analysis with TAM insights" from ₹4,480; "deep internet research" from ₹3,485. | ₹8,000-₹15,000 for a cited competitor scan; ₹20,000-₹35,000 for TAM/SAM/SOM or investor-grade report with source pack. |
| 11 | Resume, cover letter, LinkedIn optimization | Medium-low: agents can rewrite and ATS-match, but positioning, truthfulness, and career judgment need client input. | Examples from `resume writing`: "professional resume writing service for IT, cybersecurity, tech sales" from ₹8,463; "resume, cover letter, linkedin in 1 day" from ₹6,969; "fully optimized resume, CV, cover letter and linkedin" from ₹3,983. | ₹3,000-₹6,000 for formatting/ATS rewrite; ₹8,000-₹15,000 only with interview notes and human review. |

## Best targets to actually pursue

1. **Python automation / scraping scripts**: best blend of high value, objective acceptance criteria, and clear agent leverage.
2. **Sheets/Excel automation**: very agent-solvable and less likely to depend on blocked external sites.
3. **Data cleaning and PDF-to-Excel conversion**: lower price ceiling, but highly repeatable and easy to verify.
4. **Shopify product import cleanup**: good if sold as CSV/import preparation rather than manual admin labor.
5. **Scoped WordPress fixes**: profitable when the bug is reproducible and access is available, but reject broad "fix my site" tasks.

## Constraints and caveats

- Direct `curl` without the browser session was blocked with HTTP 403. Browser-CDP collection was the practical method.
- I did not open individual gig detail pages; prices are search-result "From" prices and may only reflect entry packages.
- Fiverr showed prices in INR for this session, so proposed prices are also in INR.
- Some search-result duplicates remain because Fiverr repeats promoted or high-ranking gigs.
- I treated tasks as agent-amenable only when the deliverable can be checked: code runs, rows match, formulas work, links validate, pages render, or slides match a brief.
