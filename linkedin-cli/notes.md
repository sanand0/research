# LinkedIn CLI investigation notes

## 2026-11-08

- Scope: investigate read-only API access for people/content searches, profiles, member activity and the home feed; recommend an agent-friendly CLI and resumable local sync.
- Done: primary-source comparison, live background CDP capture and replay, explicit capability/evidence matrix, reproducible credential-free probe, RESEARCH.md, README.md and root research-index entry.
- The pre-created `linkedin-cli/` directory is the new research folder. Preserve `prompts.md` and unrelated work elsewhere in the monorepo.
- Preflight: local shell and write access to this directory work; `localhost:9222/json/list` responds and includes an authenticated-looking LinkedIn feed tab. Authentication still needs API validation.
- Read devtools, agent-friendly-cli, laptop-location and code skills. No relevant LinkedIn memory-registry hits.
- Root README.md already contains an unrelated mobile-features edit; any index change must preserve it. Parent directory is outside this task's writable root.
- No credentials, raw browser cookies, session headers, personal feed/profile payloads or third-party source checkouts will be committed.
- Authentication verified: same-origin browser fetch of `/voyager/api/me` returned 200 with normalized `{data,included}` and a MiniProfile.
- Key discovery: the existing home feed uses `/flagship-web/rsc-action/actions/pagination` and `server-request` (SDUI), rather than exposing only classic Voyager requests.
- Tool environment: mise shim needs an explicit installed agent-browser path; its socket path must be set to `/tmp`. With that override, `agent-browser connect 9222` succeeds. Node REPL connector cannot reach this shell's localhost; use local Node/CDP instead.
- Live Voyager probes: full-profile REST decoration `FullProfile-76`, persisted people search `voyagerSearchDashClusters.e438ab99259203e9c1cd3f358e217282`, and member-posts query `voyagerFeedDashProfileUpdates.be2623b61657a92a693eb8d9c67aeec0` all return 200 with real entities.
- People-search first page: 5 entities, all 5 names present in the rendered search page. Second page (`start=5,count=5`): 5 entities, zero entity-URN overlap.
- Content search (`resultType=CONTENT`) using the same persisted search query returns 200 with feed Update records. Semantic/UI comparison still pending.
- Member-posts pagination: page one and page two each return 5 root references with zero overlap; metadata has a paginationToken even though paging.total is 0. Never use total=0 as an end-of-history signal.
- Legacy home feed `/feed/updatesV2?q=feedByType&feedType=HOMEPAGE` returns 400. This is a deliberate compatibility probe, not proof that the current home feed is inaccessible.
- GitHub live API returns 404 for tomquirk/linkedin-api and mguttmann/linkedin-internal-api. Search indexes still contain their references; do not recommend them as currently installable foundations.
- Member comments/reactions: category-specific GraphQL requests each returned 200 and five root references. Their detailed activity attribution is not yet normalized or compared with UI.
- Another searched member's full profile and five posts returned 200. Search Profile entities are deliberately partial; derive the navigable identifier from the result view model, then resolve the full profile.
- Content search semantic check: five Update text prefixes matched all five in the rendered content-search page.
- Home-feed discovery succeeded after enabling CDP focus emulation and dispatching wheel events to the background tab; no target activation was used. The pagination action is `com.linkedin.sdui.pagers.feed.mainFeed` and the body carries token/state/template context.
- Home replay: 200, seven activity IDs identical to capture; five substantial text passages matched rendered DOM. Captured response was 4,437,729 JavaScript characters, not a measured compressed transfer size. A fresh standalone `probe.mjs --surface home` run returned 200 with five matching activity IDs.
- Direct Node HTTP `/voyager/api/me` returned 200 with two session cookies kept only in memory. Other direct HTTP operations were not tested; background browser fetch has the broader live validation.
- Evidence saved only as structural summaries. All temporary research tabs were closed; the original LinkedIn tab ID and feed URL were preserved.
- Validation: Node syntax checks; two automated summary tests passed (private values omitted and total=0 with continuation retained); independent identity and home-feed probes succeeded.
- Research artifacts: RESEARCH.md, README.md, probes/tests and sanitized evidence. No finished CLI, SDUI entity decoder, production sync or full backfill is claimed.

## CLI implementation — 2026-11-08

- Done means: usable read commands chosen from browsing history, automatic SQLite/FTS caching, resumable bounded sync, explicit offline reads, and common-scenario tests plus live service checks.
- Browser/history preflight passed: read-only SQLite snapshot available (184 MB), authenticated identity API 200, Node has built-in SQLite and FTS5.
- History reference: 3,296 history records plus 150 shortcuts matched LinkedIn's exact host. Profiles, member activity, people search, own post analytics, network and post details dominate; only four jobs records across matching sources. Counts are stored as aggregate evidence; user URLs/titles are not research fixtures.
- Implementation choice: reuse Node/CDP and native SQLite instead of adding a Python-to-JavaScript bridge. No runtime npm dependencies. New live reads cache normalized records; cache search/import work without CDP.
- Inspected ~/code/scripts/linkedin.py, backuplinkedin.py, their prompts/tests and archive structures. Added profile-section/Markdown parity, JSONL/invitation/history imports, cached comment/repost queries and an optional adapter for detailed backup/analytics. Existing scripts and source archives are unchanged.
- Implemented modular Node CLI with native SQLite/FTS5, automatic cache-first reads, per-account isolation, field masks/NDJSON/schema/JSON params, page-atomic sync/checkpoints and dead-process lease recovery.
- Imported 3,403 post/comment rows (326 posts + 3,077 comments), 1,575 invitation rows (deduplicated) and 925 canonical browsed LinkedIn links. Cache is private and Git-ignored.
- Native live checks succeeded: profile with experience/education, people/content/company search, two-page member posts, comments/reactions activity, single-post lookup, connections and received invitations.
- Feed fallback initially skipped most cards because reaction-state keys include a `reactionState-` prefix. Corrected stable-ID matching; three extracted posts matched independent API reads for ID/text/author. Missing stable IDs remain explicit warnings.
- Analytics regression: Discovery puts values before labels, Engagement after labels. Added failing synthetic test, fixed offsets and rechecked live metrics. Unknown/withheld values are not zero.
- Existing backup adapter live test: one post analytics refresh in a dedicated background tab, working on a temporary archive copy, then importing saved rows. Original archive untouched. Detailed live comment expansion was not rerun.
- Tests now cover atomic rollback, network interruption, actual killed-process recovery, account mismatch, FTS updates/Unicode/punctuation, imports, reply parents, schema/encoding/auth/rate errors, output contracts, offline cache hits and backup source preservation.
- Cache benchmark on 5,920 seeded records: 100 FTS queries, median 3.3 ms / p95 6.1 ms inside the process; integrity_check=ok and EXPLAIN confirms FTS index use. CLI startup is additional.

## Single-file migration — 2026-11-09

- User requested Markdown by default (`md` alias), documented search filters, own-post analytics fetch/sync/update, and deployment as one script plus one test file in ~/code/scripts/.
- Read the destination repo AGENTS.md and justfile. Existing Python linkedin.py/tests remain separate; add a Node-specific test recipe to the canonical just test dependency list and run just verify before shipping.
- Consolidated runtime modules into one dependency-free linkedin.mjs, preserving named pure functions/classes and cache schema. Combined the tests into tests/test_linkedin.mjs. No runtime bundler or local imports are needed.
- Added real people-search geoUrn/currentCompany/pastCompany/network facets with numeric IDs/URNs and strict validation; filters are part of cache identity. Help explains how to obtain IDs instead of silently turning filter names into keywords.
- Added analytics me / sync analytics me for the logged-in account, relative/ISO date selection, ownership checks, per-post durable updates and resumable batch discovery. Single-post refresh updates both the analytics snapshot and canonical cached counters; likes aliases total reactions.
- Live native checks on 2026-11-09 passed: geo + second-degree search, current-organization search, own analytics batch, resumed batch and a 7-day range. Cached post counters matched fetched analytics; zero-valued counters were retained.
- Copied standalone linkedin.mjs and tests/test_linkedin.mjs into ~/code/scripts/. Added test-linkedin-api to the scripts just test/verify graph, documented daily/weekly usage, and repointed the installed linkedin symlink to the scripts copy. Existing Python CLI, backup script and their tests were preserved.
- Removed obsolete research lib/ runtime modules and split CLI test files. Research probes remain separate historical tools; the shipped CLI has only node: builtin imports and runs from an isolated directory.
- Added regression for stdin imports and moved analytics checkpoint initialization under the shared collection lease to prevent a competing sync from resetting another process's checkpoint.
- Validation: 30 standalone tests passed through scripts/just test-linkedin-api; 32 tests including the two historical research-probe tests passed in the research folder. Full scripts just verify passed its LinkedIn recipes but stopped at two unrelated tests/test_transcribe.py prompt assertions (18 tests in that module passed). The remaining timestamp recipe passed 13 tests separately.
- An earlier full-suite run stopped at an uncached anyascii dependency in offline Rofi tests. Prewarmed that exact dependency; all 47 Rofi tests then passed without source changes.

## Readable Markdown documents — 2026-11-09

- Done means every Markdown-producing command has a useful document layout, JSON/JSONL/text contracts remain intact, and saved-file output is checked across real cached records and synthetic fixtures.
- Replaced generic record headings, camelCase metric names, raw analytics page text and JSON status/import fallbacks with typed document layouts: profiles/sections, people/company/network tables, full posts/media links, analytics tables/audiences, comment threads, distinct actor/author activity, history/reposts, cache status, imports/backup and dry-run previews.
- Added output regression cases for one document title, links/Markdown escaping, dates, zero/unknown metrics, source/pagination notes, field masks and structured-format preservation. Kept the single runtime/test file deployment.
- Final validation: 41 installed standalone tests and 43 research tests passed. Compared all eight cached record kinds across JSON/JSONL/text (24 byte-identical comparisons), parsed 16 Markdown documents, and reviewed headless analytics/comment previews with working reply anchors. Verified an actual installed offline status export and private file permissions (600).
- Research and scripts runtime/test copies match byte-for-byte; the scripts README documents saved Markdown reports. Full scripts `just verify` again stopped on the two pre-existing transcription prompt assertions; the remaining timestamp recipe passed 13 tests. No transcription/setup files were changed.

## Direct executable and compact terminal Markdown — 2026-11-09

- Done means `linkedin` resolves directly to the executable in ~/code/scripts with no ~/.local/bin shim or .mjs runtime, headings include ranges/counts, row links come last, scalar metrics use lists, existing structured output remains intact, and installed/offline/tests are checked.
- Verified Node 26 is active, ~/code/scripts is on PATH, and the old ~/.local/bin/linkedin is a symlink to the script we installed. Changes outside research require the filesystem approval tool; no browser or live network reads are needed.
- Renamed both standalone sources to `linkedin`, updated test imports/docs/just commands, installed the real executable in ~/code/scripts, and removed only the old .mjs source plus its ~/.local/bin symlink. Confirmed PATH resolves directly to the scripts command and isolated execution/import needs no package metadata.
- Compacted all document headings with ranges/counts, consolidated metadata, replaced scalar metric/audience/import/cache-count tables with lists, moved plain URLs to the final table columns (including explicit field selections), and preserved full text, zero/unknown values, reply anchors and JSON/JSONL/text contracts.
- Validation: 44 installed tests and 46 research tests pass; 24 structured/text comparisons across eight cached record kinds are unchanged. Parsed 16 Markdown documents and rendered three headless layouts; analytics shrank 43→31 lines, batch analytics 66→46. Actual installed offline cache and analytics exports passed with private output permissions. Full scripts verify still stops at the same two unrelated transcription prompt assertions.

## Native backup and compatible archive — 2026-11-09

- Done means one active linkedin script performs detailed post/comment/reply and analytics/repost backups, retains all existing JSONL fields/history for the unchanged blog consumer, exposes a compatible offline export, and replaces the old Python entry point with an archived copy plus fish abbreviation.
- Confirmed localhost:9222 is reachable, fish is available, and the scripts/blog working trees have unrelated edits to preserve. The JSONL contains 326 posts and 3,077 comments, including raw text and details absent from the previous normalized import.
- Reusing the existing, tested legacy/SDUI DOM extractors as native JavaScript; replacing Python orchestration rather than invoking archived code. Native backup writes each completed post atomically and keeps a lossless archive row alongside searchable normalized fields.
- Replaced the subprocess adapter with native CDP orchestration reusing both legacy and SDUI extractors. Added lossless backupRow storage, compatible raw-JSONL export, conservative rich-field/snapshot merging, file locks with dead-process recovery, per-post atomic archive replacement and searchable cache updates. Raw duplicate backup rows are excluded from FTS indexing.
- Live testing found two independent hydration hazards: element tags were invalidated by React replacement, and visible SSR controls could precede their event handlers. Rooted identity locators and verified closed-panel retries fixed both. Demographics is a separate async module, so native detail collection waits for its section and verifies tab activation.
- Archived the Python implementation byte-for-byte, repointed its historical tests to archive, and added `abbr --add backuplinkedin.py 'linkedin backup me'` without disturbing existing setup changes. No Python subprocess remains in the active CLI.
- Verified all 3,403 original rows round-trip losslessly and the unchanged blog loader produces identical normalized documents/dates/links for all 326 original posts. All 10 blog tests passed. Installed native backup updated the real default archive from 3,403 to 3,405 rows while every original row stayed byte-equivalent as parsed JSON. The newly fetched comment thread reported complete.
- Final native checks: 57 installed tests / 59 research tests, 43 historical Python tests after relocation, 10 blog tests and 13 timestamp tests passed. Detailed live analytics saved all six demographic tabs plus one visible public repost with complete public-list statistics. Fish syntax and exact abbreviation expansion passed. Full verification still stops on the same two unrelated transcription prompt assertions. Aggregate evidence is in evidence/native-backup-validation.json; private snapshots remain ignored under .cache or /tmp.
- Retained generic legacy see-more controls and role=button previous-comment loaders; the native headless CDP fixture exercises the latter. The final full scripts suite passed the LinkedIn recipes and stopped only at the two pre-existing transcription failures. Final focused tests were rerun after the two selector additions.

## Consolidated tests and human lookup inputs — 2026-11-09

- Done means active backup regressions run entirely in tests/test_linkedin.mjs, the older Python tests are archived, textual geo/current/past-company filters resolve through LinkedIn and combine all returned matching suggestions with OR, profile-name inputs pick the first personalized people result, posts show publication timestamps near the top, and interactive Markdown uses glow -p then PAGER then raw output. Pipes/files and structured formats bypass pagers.
- User initially chose first ranked filter suggestions, then explicitly revised that choice to all matching suggestions with OR. Profile resolution remains first-match. Existing numeric/URN filters and profile URLs/identifiers must keep working, and offline runs must reuse cached resolutions without opening a browser.
- Added read-only scheduled-post list/full-content SDUI decoding and effective paths reporting. Confirmed the live connections error was a valid connection with no resolved profile; preserve its identity/date and show unavailable instead of aborting all rows.
- Live research-source checks passed: Chennai/Singapore/Boston and IBM/Tata (current/past) resolve through authenticated typeahead, activity accepts a personalized name, connections returns 20 entries including one unavailable member, and scheduled returns three exact timestamps with full content. Credentials and private captures stay outside committed evidence.
- Native behavioral ports cover the historical Python backup cases in the single JS test file, including isolated headless CDP/DOM fixtures, loading/zero analytics, repost completion and cleanup. Research tests: 93 passed (91 native plus two historical probes).
- Installed byte-identical runtime/tests in ~/code/scripts. Archived the previous Python tests unchanged at archive/test_backuplinkedin.py, removed their active recipe, and made the native recipe install the existing Chromium fixture dependency. Preserved concurrent justfile changes and user-owned fish edits.
- Installed validation: 91/91 native tests passed; full just verify passed its LinkedIn recipe and stopped only at the same two pre-existing transcription prompt assertions. The final timestamp recipe passed 13 tests separately. Node syntax and diff whitespace checks passed; no private captures are tracked.
- Installed live defaults returned 20 connections (one unavailable), three scheduled posts with complete text/times and effective paths. The legacy backup archive hash stayed unchanged. Name/filter lookups also passed offline; an actual interactive glow -p session opened and exited cleanly, and tests cover PAGER/raw fallback and non-TTY bypass.

## Profile/company activity and post corrections — 2026-11-10

- Investigation and live evidence: [activity-posts-update](activity-posts-update/README.md). Implemented three-line post headers; corrected hidden expansion controls and normalized original-post references; native multi-member/company post filters; profile-first actor lookup and company URLs/URNs; explicit actor selections; sorted live/offline lists.
- Cleanup found and fixed a nonexistent package bin, undersized fresh paginated caches, stale refresh membership and a tab-close/discovery race between successive invocations. No dependencies added; retained the independently executable copies and legacy tools pending caller review.
- Name search still follows the established first-personalized-result policy: exact usernames/URLs are preferable where names are ambiguous. Documented other review items in the report.

## Local post times and showcase targets — 2026-11-10

- [Follow-up investigation](showcase-local-time/README.md): local-time Markdown post dates without the activity-ID suffix; explicit showcase URLs and `showcase:SLUG` reuse organization lookup/native post search.
- Live Claude showcase actor 106863934 and three post IDs match the rendered page. User confirmed preserving profile-first semantics because bare claude is a real member handle. Research tests: 105 passed.
