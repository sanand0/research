# Diverse WebMCP actions and composable workflows

Tested 2026-09-05 with `agent-browser 0.36.0` and local Headless Chrome 152.

This extends the first pass beyond shopping and documentation. The main finding is that WebMCP is more interesting as an **application capability layer** than as a collection of website APIs. The useful surfaces include stateful data analysis, document workspaces, graph editing, verification, artifact generation, calculators, maps, route-scoped database access, local transforms, and domain-specific decision support.

`diverse-results.tsv` is the compact matrix. `raw/diverse/` contains discovered tool schemas. `raw/workflows/` contains invocation evidence.

## Action taxonomy observed

| Action family | Examples seen | What changes versus DOM automation |
|---|---|---|
| Retrieve/search | OpenAI docs, Shopify catalog, Scholar identifiers, CamJam spots | Query intent becomes one typed call, not search-box choreography |
| Inspect/verify | citation verification, retraction checks, QR decode verification, Core Web Vitals metrics | Site exposes domain validation logic directly |
| Transform | JSON format/minify/validate, translation, image/file utilities | Operations can happen locally in the browser without upload |
| Stateful analysis | JSON-stat load → filter → pivot → export | Agent operates the application's data model, not individual controls |
| Stateful construction | flow graph nodes/edges/layout; pizza configuration | Agent manipulates domain objects rather than coordinates/buttons |
| Navigate/discover capabilities | webmcp.sh routes, Hopi tool search, Simple Tool Stack discovery | Tools can appear only when context makes them relevant |
| Generate artifacts | verified QR, CSV export | Tool can return a receipt or download path rather than stuffing bytes into context |
| Delegate | text editor planner/researcher/writer/reviewer/skills | A web app can expose its own agent/sub-agent layer through WebMCP |
| Prepare consequential actions | Shopify cart/checkout/order tools and directory-listed booking/contact tools | WebMCP can reach real state, so host authorization matters more, not less |

The last row was deliberately not exercised against production accounts or purchases.

# Tested workflows

## 1. Browser page → machine interfaces → visual architecture map

**Sites:** Astronomer → WebMCP Flow.

Astronomer's `get_discovery_endpoints` returned four machine-facing endpoints:

- Agent Skills index
- API catalog
- MCP server card
- OpenAPI document

I then opened `webmcp-flow.vercel.app` and used WebMCP calls to create five nodes, connect Astronomer to each endpoint, run auto-layout, and read the resulting graph.

```text
Astronomer page
   ├── Agent Skills index
   ├── API catalog
   ├── MCP server card
   └── OpenAPI spec
```

Evidence: `raw/astronomer/discovery.json`, `raw/workflows/astronomer-to-flow/11-graph.json`, and `13-after.png`.

**Why this is non-obvious:** the browser page is not the end of the automation. It can be a bootstrap point that advertises better machine interfaces; another WebMCP application can then materialize or inspect those interfaces. A generic browser agent can progressively move upward in semantic level instead of scraping forever.

A practical extension is **site reconnaissance**: open any unfamiliar SaaS → discover agent/API/MCP/OpenAPI surfaces → turn them into a reviewable capability map → decide which interface the agent should use for each task.

## 2. Data URL → analytical workbench → filtered export

**Site:** JSON-stat explorer.

I ran an entirely semantic stateful analysis:

1. `fetch_dataset` — loaded the public OECD unemployment JSON-stat dataset.
2. `filter_dimension` — kept Japan, Korea, United States.
3. `filter_dimension` — kept 2012, 2013, 2014.
4. `set_view_mode` — switched to pivot.
5. `set_dimension_role` — area as rows.
6. `set_dimension_role` — year as columns.
7. `get_data_summary` — confirmed a 3-row pivot.
8. `export_csv` — exported the current filtered view.

After the initial ~1.3 s fetch, each state operation took about 10–11 ms in this run. The final summary explicitly reflected the active filters and dimension roles; export reported a three-row CSV.

Evidence: `raw/workflows/jsonstat-pivot/`.

**Why this matters:** this is closer to controlling pandas/Excel than controlling a website. The agent reasons about dimensions, filters, rows, and columns. No selector knowledge is required, and state remains visible to the human in the same app.

Possible composition: **public statistical endpoint → WebMCP pivot/filter → CSV → another agent/tool for charting or analysis**. The browser becomes a human-reviewable ETL/analysis surface.

## 3. AI-produced citation → factual identity check → retraction check → formatted bibliography

**Site:** Scholar Sidekick.

Using DOI `10.1145/3442188.3445922`:

1. `resolveIdentifier` recovered the Crossref record for *On the Dangers of Stochastic Parrots*.
2. I deliberately paired that DOI with the fake title `Large Language Models Are Perfectly Reliable`.
3. `verifyCitation` returned `verdict: mismatch`, `confidence: high`, and the actual record.
4. The real title returned `verdict: matched`.
5. `checkRetraction` reported no retraction/correction/expression of concern.
6. `formatCitation` produced the APA citation.

Evidence: `raw/workflows/scholar-chain/`.

**Useful workflow:** before an AI-generated report is published, extract cited identifiers → verify title/author/year identity → check retraction/correction status → format only citations that survive. This is stronger than merely checking that the DOI resolves: it catches a real identifier attached to an invented citation.

## 4. Need expressed in natural language → capability discovery → specialized route → calculation

**Site:** Hopi.

At the homepage, the available tools were only `hopi_directory` and `hopi_search`. Searching for `working days between dates` returned:

- the specialized tool name `hopi_working_days_calculator`
- the route `https://hopi.co.uk/working-days-calculator/`

After opening that route, `webmcp list` contained the specialized calculator. Calling it for 2026-09-01 through 2026-09-30 returned 22 working days out of 30, with 8 weekend days excluded.

Evidence: `raw/workflows/diverse-actions/hopi/`, `raw/workflows/hopi-chain/`.

**Why this is important:** a site does not need to dump hundreds of tools into every page. It can expose a small **capability router**, then register contextual tools only on the relevant route. For large enterprise applications this looks much more scalable than a giant static tool list.

## 5. App gateway → route navigation → newly scoped tools

**Site:** webmcp.sh.

The landing route exposed four generic tools:

`app_gateway`, `get_current_context`, `list_all_routes`, `navigate`.

`app_gateway` described domain routes including entities, memory blocks, graph, dashboard, and SQL REPL. After `navigate {"to":"/sql-repl"}` and re-listing, the tool surface expanded to include `get_database_info` and `sql_query`.

Evidence: `raw/workflows/webmcpsh-dynamic/`.

**Non-obvious consequence:** WebMCP can implement capability scoping by application state. The effective workflow is:

```text
open app
  → discover gateway
  → choose route semantically
  → navigate
  → re-discover tools
  → use route-specific capability
```

That is analogous to lazy-loading APIs, but controlled by the user's current browser context. It also reduces accidental authority: database tools need not exist while the user is on the landing page.

## 6. Domain computation → verifiable artifact receipt

**Site:** QR Code Crafter.

I asked `generate_verified_qr` to encode `https://example.com/webmcp-test` as a 512px SVG. Instead of dumping the SVG into the agent context, the result returned:

- output byte length and SHA-256
- exact decoded-payload hash match
- decoder identity
- contrast ratio and quiet-zone checks
- error-correction metadata
- `productionReady: true`
- explicit limitations
- endpoint/instructions for fetching the actual bytes when needed

Evidence: `raw/workflows/diverse-actions/qrcode/invoke.json`.

This is a particularly good **tool-result design pattern**: return a bounded, inspectable receipt plus a way to retrieve a large artifact only when required. It avoids filling model context with binary/base64 data while preserving verification and provenance.

A useful cross-site variant: calculator/planner produces a shareable URL → verified-QR WebMCP tool encodes it → human scans the exact state later.

## 7. Domain discovery → rich decision object

**Site:** CamJam.

`get_spots_by_region {"region":"Auckland"}` returned 13 surf spots and stable slugs. `get_surf_spot {"slug":"piha"}` then returned location, hazards, tide notes, description and a structured time series of wave height/direction/period and wind speed/direction.

Evidence: `raw/workflows/camjam-invoke.json`, `raw/workflows/camjam-chain/spot.json`.

The interesting design choice is that the detail call is **decision-rich** rather than atomized: the agent does not necessarily need four separate DOM/API traversals for location + hazards + forecast + tides. For many domains, fewer richer semantic tools may beat mechanically mirroring every backend endpoint.

## 8. Discover a local utility → move to its route → transform data

**Sites/routes:** Simple Tool Stack.

The homepage's sole WebMCP tool, `discover_tools`, advertised utilities for text, dates, images, PDF, hashes, Base64, JSON and more, each with an `href` and machine name. Opening `/dev-data/json-formatter` exposed the route-specific `json_formatter` tool. Calling it on `{"b":2,"a":1}` with formatting and key sorting returned valid formatted JSON plus byte/depth/key stats.

Evidence: `raw/workflows/simpletoolstack-invoke.json`, `raw/diverse/jsonformatter/list.json`, `raw/workflows/diverse-actions/jsonformatter/invoke.json`.

This is another progressive-disclosure architecture, but it also demonstrates **local browser compute as an agent tool**. File/image utilities can be useful precisely because sensitive bytes need not leave the browser merely to make the UI automatable.

# Other diverse surfaces discovered

- **Core Web Vitals:** `list_options`, `get_metrics`, `get_histogram`. A CMS comparison call returned ranked field-performance measurements and embedded a machine-readable attribution requirement. Evidence: `raw/workflows/corewebvitals-chain/cms.json`.
- **Chrome analytics demo:** one semantic `query` can set group-by, measure, chart type and filters together.
- **Chrome real-estate map:** `search_location` changes the map to a named location.
- **Chrome pizza demo:** seven domain-level configurator actions cover size, style, layers, toppings, reset and sharing.
- **Bandarra editor:** 26 tools span document CRUD, precise edits, workspace queries, translation, skills, planner/researcher/writer/reviewer delegation, and user-authorized mutations.

# Composable recipes worth building

These are **recipes inferred from individually working surfaces**, not all executed end-to-end here.

### A. Agent-interface reconnaissance

`page → WebMCP discovery → advertised MCP/OpenAPI/Skills endpoints → capability graph → choose cheapest/strongest interface`

Use when a coding agent lands on an unfamiliar product. The browser becomes the universal bootstrap transport; WebMCP helps the agent graduate away from browser driving when a better protocol exists.

### B. Evidence-hardening conveyor

`research/search result → identifier extraction → citation identity verification → retraction check → formatted citation → document editor`

The critical step is verification *before* formatting/polish. The Scholar workflow proves the identity/retraction portion; the editor surface provides the eventual document target, though its sub-agent calls failed in this environment.

### C. Human-reviewable data pipeline

`dataset URL → load → inspect dimensions → filter/pivot/sort → human reviews visible table → export CSV → downstream model/code`

This lets an agent perform repeatable transformations while preserving a visual checkpoint for a human rather than hiding all state in a backend script.

### D. Capability search instead of mega-tool lists

`generic site tool search → route selection → re-list capabilities → specialized tool`

Hopi, Simple Tool Stack and webmcp.sh independently exhibit variants of this mechanism. A large enterprise app could expose thousands of latent operations without presenting thousands of tool definitions to the model at once.

### E. Artifact receipt chain

`generate/transform → verify/hash/quality-check → return compact receipt → fetch bytes only if needed → share/use`

QR Code Crafter demonstrates the pattern. It is applicable to PDFs, charts, images, exports, reports and generated code bundles.

### F. Domain decision funnel

`broad list → stable entity ID/slug → rich detail/forecast/risks → rank externally → navigate human to chosen option`

CamJam demonstrates the first three steps; Shopify similarly uses search → product → variant. This is a general pattern for travel, jobs, real estate, events, equipment and other large catalogs.

# What I would encode in an `agent-browser` skill

```text
After every navigation:
1. wait briefly for tool registration, then `webmcp list`;
2. if zero tools but the page loaded, retry discovery once or twice before falling back;
3. re-list after route/state changes because capabilities may change;
4. choose domain-semantic tools over DOM actions when they satisfy the intent;
5. validate arguments locally against the advertised schema;
6. independently classify side effects — do not trust readOnly annotations alone;
7. require user intent/confirmation for writes, transactions, submissions, account actions, or sensitive disclosures;
8. evaluate completion from nested status/output, not merely top-level success;
9. bound tool-result size and preserve provenance/verification metadata;
10. fall back to accessibility/DOM when the tool is absent, incomplete, or action-only.
```

The surprising architectural implication is that **WebMCP can be the browser's service-discovery layer, not just its automation layer**. The best sites use it to expose a small semantic gateway, reveal contextual capabilities, and sometimes point the agent toward a more appropriate protocol entirely.


<!-- ROUND3_LONG_WORKFLOWS -->
# Longer workflows: round 3

These are deliberately longer than the earlier examples. I tried to make each chain answer a real user need, include at least one handoff or state transition, and independently check important intermediate results rather than trusting a single tool.

## 9. Agent-facing website launch QA: score → protocol checks → actual browser operability

**Goal:** before declaring a site “agent ready”, distinguish content readability from actual browser-agent operability.

Tested on `webmcp.com` and `quicknode.com`:

1. `agent-ready.dev/scan_site(url)` — get a high-level agent-readability score.
2. `admintoolkit.io/admintoolkit_check_ai_crawler_access` — inspect AI crawler policy.
3. `admintoolkit_validate_llms_txt` — independently parse/fetch `llms.txt`.
4. `admintoolkit_validate_webmcp_tool` — statically inspect the page for WebMCP hints where possible.
5. Open the target itself in `agent-browser` and run `webmcp list` — test what this browser session can *actually invoke*.

What happened:

- QuickNode scored **70/100 (“good”)** in Agent Ready and Agent Ready reported **llms.txt 100/100**, yet this headless `agent-browser` session exposed **0 WebMCP tools**.
- AdminToolkit independently failed to load QuickNode's `llms.txt` because its fetch helper stopped at an HTTP 301, while its robots checker followed a redirect and reported GPTBot / Google-Extended / ClaudeBot allowed.
- `webmcp.com` scored only **66/100 (“fair”)**, yet the actual browser exposed **6 callable WebMCP tools** in this run.
- `webmcp.com` blocks all three tested AI crawler tokens at `/`, while remaining fully usable through a human/browser session with WebMCP.

**Non-obvious lesson:** “agent ready” is not one scalar. At minimum keep separate axes for **content readability, crawler policy, static protocol discoverability, and runtime browser operability**. A score can be useful, but the last step should be a real browser capability probe.

Evidence: `raw/round3/agent-readiness-workflow/`.

## 10. Synthetic energy bill → live market context → offer comparison → savings decision

**Goal:** turn unstructured document text into a current market decision without a bespoke integration.

Using only synthetic bill data on SwitchAI:

1. `parse_energy_bill` extracted supplier, annual consumption, annual spend, and zone from Italian bill-like text.
2. `get_market_indices` returned current/reference PUN/PSV context and provenance timestamps.
3. `get_available_offers` was called to enumerate offers.
4. `calculate_energy_savings` was run once from the original bill text.
5. The same calculation was run again with explicit normalized values to check whether extraction changed the result.

The parsed and explicit paths agreed on the headline recommendation and the same top offers. This is a useful pattern for many domains: **document → normalized facts → live external context → decision model**, all through browser-local semantic tools.

But it also produced several serious semantic failures documented in `FAILURE-MODES.md`: an advertised empty schema hid a required argument, cost figures used inconsistent bases, and one sensitivity sentence had a nonsensical sign.

Evidence: `raw/round3/energy-workflow/`.

## 11. Private duty roster: create → replay safely → inspect IDs → project future assignments

**Goal:** test a genuinely stateful application workflow rather than a search endpoint.

Toban exposes 18 roster tools. I created a synthetic 4-person roster with two duties and weekday-only date rotation:

1. `create_schedule` with a stable `request_id`.
2. Replay the **identical** create call with the same `request_id`.
3. `list_schedules` to verify there was only one roster.
4. `get_schedule_details(section=groups)` to resolve stable task/group IDs.
5. `get_current_assignments` for 2026-09-07 and 2026-09-08.
6. Query Saturday 2026-09-12 to verify skip-weekend semantics.
7. Query Monday 2026-09-14 to confirm rotation resumes.

This worked unusually well:

- the replay returned the same schedule ID with `replayed:true`;
- only one schedule existed;
- assignments rotated deterministically on weekdays;
- Saturday returned `phase:"paused"` and zero assignments.

This is an excellent WebMCP shape: **application-level idempotency + stable IDs + readback tools**. It is much safer than an agent blindly retrying UI clicks.

A fresh isolated `agent-browser` session, however, saw zero schedules despite the creation result saying `persistence.local:"saved"`; see the persistence failure below.

Evidence: `raw/round3/roster-workflow2/` and `raw/round3/roster-workflow/`.

## 12. “Make a day of it”: nearby historical event → event details → period-inspired vegetarian menu → QR artifact

**Goal:** compose capabilities that were not designed as one product workflow.

Around Munich, Fyndling supported:

1. `find_events_near` for medieval / historical events within 200 km and a date window.
2. `get_event` for the selected event's exact venue, date, organizer and canonical Fyndling URL.
3. `compose_menu` for a three-course vegetarian menu intended for outdoor camp cooking.
4. Pass the event URL into QR Code Crafter's `generate_verified_qr` to make a portable artifact with decode/hash verification.

The event search itself worked and returned real dated events. The menu generator produced richly sourced historical recipes with manuscripts, annotations, ingredients and practical FAQs.

The interesting part was the failure: despite `lagerkueche:true`, its first selected recipe (`boc-038`) contains an FAQ explicitly saying it is **not suitable for camp cooking** because of raw egg sauce, multiple steps and lack of refrigeration. Two later courses *were* described as camp-suitable.

Also, Fyndling returned event objects as a JSON-encoded string. My first generic extraction treated it as plain text and therefore passed the site root, not the event URL, into the QR step. That is a harness bug, but exactly the kind a cross-site workflow will hit.

Evidence: `raw/round3/medieval-day-workflow/`.

## 13. Synthetic Peppol invoice → format detection → standards validation → human-readable rule explanation

**Goal:** use WebMCP as a compliance repair loop.

With a deliberately incomplete synthetic UBL invoice:

1. `detect_format` correctly identified UBL.
2. `validate_invoice` classified it as Peppol BIS Billing 3.0 and returned nine concrete rule failures, XPath-like locations, tests and a results URL.
3. `explain_rule("BR-06")` turned the first failure into a short remediation explanation plus the official docs URL.

This is a compelling enterprise workflow: an agent can take a document, run an authoritative domain validator, explain each failure and iteratively repair it.

However the explainer contradicted the actual validator for BR-06. Validation checked `AccountingSupplierParty/Party/PartyLegalEntity/RegistrationName`, while the explainer said `PartyName/Name` is mandatory. I attempted to test both repairs, but the surrounding platform blocked the follow-up calls; I therefore record the contradiction but do **not** claim which repair the service ultimately accepts.

Evidence: `raw/round3/peppol-workflow/`.

## 14. Bibliography → fabrication audit → retraction/OA checks → clean export → portable link

**Goal:** harden AI-generated research references before publication.

I constructed a three-entry BibTeX file containing:

- one correct citation (`On the Dangers of Stochastic Parrots`);
- one fabricated title attached to that **real DOI**;
- one genuinely retracted Lancet paper.

Then:

1. `auditBibliography` checked the batch.
2. It returned 2 identifier matches, **1 high-confidence title mismatch**, and **1 retracted paper**.
3. `checkOpenAccess` confirmed the valid ACM paper is gold OA / CC-BY.
4. `checkRetraction` independently returned the retraction/correction/concern notices for the Lancet DOI.
5. `exportCitation(..., format="bib")` generated normalized BibTeX and correctly prefixed the retracted paper's title with `RETRACTED:`.
6. The OA DOI URL was passed to QR Code Crafter, which returned a verified QR receipt with an exact payload-hash match.

This is probably the most immediately useful cross-site workflow I found: **LLM draft → deterministic scholarly verification → provenance/retraction check → normalized citation artifact**.

The downside is output size: the three-entry audit returned **147,297 bytes**, mostly raw registry payloads. Project the result down to verdicts/mismatches/provenance before putting it back into model context.

Evidence: `raw/round3/research-integrity/`.

## 15. Analytical state → browser download → host-mediated artifact handoff

**Goal:** test whether WebMCP composition can move beyond JSON/text into files.

Using JSON-stat:

1. load OECD unemployment data;
2. filter to Japan, Korea and the United States;
3. filter to 2012–2014;
4. `export_csv`;
5. configure `agent-browser --download-path` and inspect the result on disk.

The WebMCP call created a real **279-byte CSV** in the configured browser download directory. This proves a tool can cross the semantic/browser boundary and produce a normal artifact the host can use.

I then tried to pass that artifact into another WebMCP utility for hashing. The second tool accepted text rather than a file object, and the platform blocked the attempted bridge. That is not a WebMCP failure, but it exposes an architectural gap: **WebMCP does not itself define an inter-site artifact bus**. The browser host/agent runtime still needs to broker downloads, uploads, MIME/base64 conversions and trust boundaries.

Evidence: `raw/round3/artifact-handoff/`.

# Composition patterns that survived contact with real sites

The longer runs suggest a few reusable orchestration shapes:

- **Discover → resolve → verify → act.** Search returns candidate IDs/URLs; resolve exact object; independently validate; only then mutate or produce an artifact.
- **Parse → normalize → enrich → decide.** Especially strong for bills, invoices, reports and forms.
- **Create with idempotency key → read back → project future state.** Prefer this over retrying opaque UI writes.
- **Score → independent checker → runtime probe.** Never let a readiness/quality score replace a real capability test.
- **Produce artifact → verify receipt → host handoff.** Hashes/decoded payloads/provenance are much more useful to agents than “download succeeded”.
- **Route → re-discover tools.** Treat the capability set as page/route state, not a site-global constant.

The main design recommendation is therefore not merely “WebMCP first”. It is:

> **Use WebMCP as typed semantic stages, but put orchestration truth in the host: normalize success, enforce policy, validate constraints, re-discover after state changes, trim outputs, and independently verify consequential intermediate results.**
