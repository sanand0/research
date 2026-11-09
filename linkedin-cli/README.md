# LinkedIn CLI

A single-file, read-only LinkedIn CLI with automatic SQLite caching and fast offline search. Markdown is the default output; `--format md` is an alias. Interactive terminals use `glow -p`, then `$PAGER`, then raw Markdown; pipes and saved files bypass viewers. It uses the signed-in browser through background CDP requests. No npm dependencies; requires **Node 24+** and, for live reads, a browser with CDP on `localhost:9222`.

```bash
./linkedin --help
./linkedin whoami
./linkedin profile sanand0 --sections experience,education --format markdown
./linkedin search people "data science" --limit 10
./linkedin activity "First Last" --kind posts --limit 20
./linkedin scheduled
./linkedin paths
./linkedin feed --limit 10
./linkedin find "agents" --kind post
```

The installed **`~/code/scripts/linkedin`** is an executable script, found directly on PATH. There is no `~/.local/bin/linkedin` shim. This research folder keeps an identical standalone copy. Neither copy imports local modules or requires a build step. The combined test is **`~/code/scripts/tests/test_linkedin.mjs`**, integrated as `just test-linkedin-api` in the scripts repo’s `just test` / `just verify` suite. The earlier Python `linkedin.py` and its tests remain unchanged.

## Cache and offline use

Default cache: **`~/.cache/sanand-scripts/linkedin-cli/cache.sqlite`**. Override with `--db PATH` or `LINKEDIN_DB`. It coexists with the older `linkedin.py` URL cache in that directory.

Every successful live read is cached. Repeated reads use cached results for five minutes (profiles: one day). Use `--refresh` to fetch again, `--max-age SECONDS` to change the threshold, or `--offline` to prohibit browser access. `find`, `cache`, `export`, `comments` and `reposts` always use the local cache.

```bash
./linkedin profile sanand0 --offline --format markdown
./linkedin post 'https://www.linkedin.com/feed/update/urn:li:activity:POST_ID/' --offline
./linkedin find "agent evaluation" --kind post --limit 20 --fields id,author.name,text,url
./linkedin find "Anand" --kind profile --prefix
./linkedin cache status
./linkedin cache get 'urn:li:activity:POST_ID'
./linkedin export --kind comment --limit 10000 --format ndjson > comments.jsonl
```

`find` uses SQLite FTS5 with relevance ranking: words are matched literally with AND, punctuation is safe, and `--prefix` enables prefix matching. `--since YYYY-MM-DD` (or `7d`, `2w`, `3mo`, `1y`) filters cached observations, not publication dates. Cache access is isolated by authenticated account. Use `--account USERNAME` or `LINKEDIN_ACCOUNT` to select a previously cached account offline; an online account mismatch fails before records are written under that account.

The implementation session seeded the cache with the existing post/comment archive, invitation archive and browsed LinkedIn links. It had **5,920 records** after bounded live checks, including 3,077 comments. A 100-query benchmark measured **3.3 ms median / 6.1 ms p95** inside the cache process; CLI startup is additional. See [benchmark evidence](evidence/cli-cache-benchmark.json).

## Everyday reads

| Command | Result |
|---|---|
| `whoami` | Verify the live account; `--offline` reads its cached identity. |
| `profile USER` | Profile by identifier, URL/URN, or quoted name (first personalized people result). Optional `--sections experience,education,skills`. |
| `search people QUERY` | People, names, headlines and profile links. |
| `search posts QUERY` | Matching posts and their authors/text/counts when returned. |
| `search companies QUERY` | Company search results. |
| `activity USER --kind posts` | Member posts; `me` selects the signed-in member. |
| `activity USER --kind comments` | Activity-owner context plus target posts; detailed comment attribution remains incomplete. |
| `activity USER --kind reactions` | Activity-owner context plus target posts; detailed reaction attribution remains incomplete. |
| `post URL_OR_URN_OR_ID` | One post, its author, text and accessible social counts. |
| `connections` | Your connections, most recently added first; unavailable profiles retain identity/date and are marked unavailable. |
| `invitations` | Received invitations. Does not accept, ignore or send invitations. |
| `feed` | Visible ranked home-feed snapshot in a dedicated background tab. |
| `scheduled` | Scheduled posts for the logged-in member: exact scheduled times and full text where exposed. |
| `paths` | Effective script, backup/lock/temp, SQLite/WAL/SHM, configuration and test locations; no browser/cache access. |
| `analytics POST` | Fetch/refresh your post’s visible Discovery/Engagement summary and cached counters; `analytics me` refreshes a batch. |
| `comments POST` | Cached comments and replies, preserving parent/post IDs. |
| `reposts POST` | Cached public repost details from the backup workflow. |

`people`, `posts` and `companies` also work as short aliases for `search ...`.

Profile, search, activity, post and network reads use Voyager JSON. Feed and summary analytics use explicit **DOM fallbacks** for newer SDUI pages. Feed reads expand visible post text and resolve stable IDs from card state or a read-only permalink control; the clipboard is intercepted and restored in the owned tab. Unidentified cards are skipped with warnings. The feed's IDs/text were checked against independent API post reads. Full feed SDUI stream decoding is future work.

All read output identifies its source. Missing fields remain unknown; sparse observations preserve richer cached fields rather than erase them. `observedAt` describes the record observation; it does not assert that every preserved field was refreshed together. Archive publication timestamps retain their original confidence labels.

## Profile names and people search filters

`profile`, `activity` and `backup` accept `me`, a profile URL/URN/identifier, or a quoted name. A name uses the **first accessible result from the logged-in member’s personalized people search**. Markdown and JSON identify the selected name, URL and identifier. Bare single words remain identifiers; use `name:Anand` to request a single-word name search. Use `me` when you specifically want your own profile.

```bash
linkedin profile "First Last" --sections experience,education
linkedin activity "First Last" --kind posts --limit 20
linkedin backup "First Last" --archive ./their-posts.jsonl --limit 5
linkedin profile name:Anand
```

These filters use actual LinkedIn facets, rather than adding words to the keyword query:

| Flag | Values | LinkedIn facet |
| --- | --- | --- |
| `--location` | Partial location names, numeric geo IDs or `urn:li:geo:ID` | `geoUrn` |
| `--organization` | Partial current-employer names, numeric company IDs or company/organization URNs | `currentCompany` |
| `--past-organization` | The same name/ID lookup for previous employers | `pastCompany` |
| `--degree` | `1`, `2`, `3`/`3+`, or `F`, `S`, `O`; comma-separated | `network` |

All matching suggestions returned by LinkedIn are included, including aliases such as parent-company matches. Values within one filter are **OR**; different filters are **AND**. This uses LinkedIn’s bounded typeahead suggestions, rather than claiming to enumerate its entire company/location directory. Resolved names and IDs are shown in Markdown and `meta.resolved_filters` in JSON.

```bash
linkedin search people engineer --location "Chennai,Singapore,Boston"
linkedin search people engineer --organization "IBM,Tata" --degree 1,2
linkedin search people engineer --past-organization IBM --location Singapore
linkedin search people engineer --location 102713980 --organization 1035
```

`3` means third-degree and beyond. Text resolutions are saved per account for one hour; `--refresh` repeats them, once per unique term in an invocation. Offline reads and `--resume` reuse saved resolutions and never rerank a running traversal. If a name/filter has not been resolved for the selected account, offline/resume fails with `CACHE_MISS`. Empty lookup results fail with `NOT_FOUND`, rather than silently running a broader search. Numeric IDs remain useful for choosing an exact organization/location.

## Scheduled posts and local paths

```bash
linkedin scheduled --refresh
linkedin scheduled --offline --output scheduled.md
linkedin paths
linkedin paths --format json
linkedin paths --db ./cache.sqlite --archive ./posts.jsonl
```

`scheduled` reads the logged-in member’s scheduled-post list and each returned full post through two allowlisted SDUI read components. It does not create, edit, reschedule, delete or publish posts. `scheduledAt` is an exact UTC ISO timestamp; Markdown shows the scheduled date/time near the top of each entry. Text is decoded through Flight references and UTF-8 text rows without executing components or including callback/action payloads. Missing text is reported explicitly (for example, a media-only post).

A successful refresh replaces the cached list membership, so cancelled/published posts disappear from the active list. Historical observations may still exist in offline full-text search. A limited snapshot is marked incomplete; a later larger online request fetches the remaining contents. `--offline` reports when only part of the list was cached. Results are bounded by `--limit` (20 by default).

`paths` reports effective local file locations without opening the browser or SQLite. There is **no application config file**: settings come from CLI flags and `LINKEDIN_DB`, `LINKEDIN_CDP`, `LINKEDIN_ACCOUNT`, `XDG_CACHE_HOME` and `PAGER`. Backup archives, the archive lock/temporary pattern, SQLite sidecars, the executable and its test file are listed explicitly.

## Fetch, sync and update your post analytics

```bash
# Fetch one of your own posts' metrics and update its cached counters.
linkedin analytics POST_URL --refresh
linkedin analytics POST_URL --offline --format md

# Discover your own posts and refresh a bounded recent batch.
linkedin sync analytics me --since 7d --limit 20 --max-pages 5
linkedin sync analytics me --since 7d --limit 20 --max-pages 5 --resume

# Explicit date window: since inclusive, until exclusive.
linkedin sync analytics me --since 2026-11-01 --until 2026-11-09 --limit 50 --max-pages 10
linkedin export --kind analytics --limit 10000 --format jsonl > analytics.jsonl
```

The single-post operation verifies authorship against the logged-in account before opening analytics. `analytics me` discovers posts from that account and skips posts authored by others. `--refresh`, or the `sync` prefix, bypasses the normal read TTL.

Metrics include `reactionCount`/`likes`, `commentCount`, `repostCount`, `impressionCount`, `saveCount`, `sendCount` and visible discovery/profile metrics. **`likes` aliases total reactions**, not only the LIKE reaction subtype. Missing or withheld metrics remain unknown; measured zero is preserved. Markdown renders compact metric lists; JSON/JSONL remain available for automation.

Each successful update immediately saves an analytics record and updates the canonical cached post’s counters and nested `analytics` object. A later batch failure preserves those writes; resume re-reads the unfinished discovery page. The page checkpoint advances only after that page is processed. The reused analytics tab is owned by the CLI and stays in the background.

`--since`/`--until` accept ISO dates or `Nd`, `Nw`, `Nmo`, `Ny`; months are 30-day and years 365-day periods. Relative bounds are frozen in the resumable checkpoint. Date selection uses an available publication date, or an explicitly approximate activity-ID time estimate when the API omits it. Budgets and accessible history still limit coverage. Detailed demographic tabs and public repost expansion remain available through `backup --analytics` below.

## Bounded, resumable sync

The `sync` prefix forces a fresh traversal. Ordinary paginated reads use the same page/cache engine.

```bash
./linkedin sync activity me --kind posts --page-size 10 --limit 100 --max-pages 10
./linkedin sync activity me --kind posts --page-size 10 --limit 100 --max-pages 10 --resume
./linkedin sync search people "data science" --limit 30 --max-pages 3
./linkedin sync connections --limit 100 --max-pages 10
./linkedin sync feed --limit 20 --max-pages 3
```

A whole page and its continuation are committed in one SQLite transaction. If an output limit cuts through a fetched page, the entire page is still cached; `page.fetched` and `page.returned` show the difference. Continuations stay in SQLite and are bound to the account and query. Errors include committed progress and whether resuming is possible. Repeated pages/cursors fail instead of looping. A crashed process's lease is reclaimed on the next sync, which can resume immediately from the committed page.

`--resume` continues a previous traversal. A later poll should normally omit it to refresh from the head and merge edits/new records. Expired activity continuations require a restart. Feed continuations are tied to the current background tab, so feed `--resume` is explicitly rejected; a new run creates another ranked observation. Feed/search/member activity are bounded observations, not complete historical replicas. `coverage.complete` is therefore always false.

## Native backup and compatible archives

`linkedin` subsumes the detailed backup functionality. The original Python implementation is kept at [`~/code/scripts/archive/backuplinkedin.py`](/home/sanand/code/scripts/archive/backuplinkedin.py) for historical reference; the active CLI uses Node built-ins and direct background CDP, without a Python subprocess. The older profile-oriented `linkedin.py` remains separate.

```bash
# Daily: posts, full text, media, comments and replies; update the existing archive.
linkedin backup me --limit 100
# Weekly: detailed analytics and public reposts for saved original posts.
linkedin backup me --analytics --since 7d --limit 0
# Use a separate archive or adjust the traversal bounds.
linkedin backup me --archive ./posts.jsonl --limit 5 --max-scrolls 10
linkedin backup me --no-comments --limit 5
# Offline: export all saved backup rows in the existing raw JSONL schema.
linkedin export --schema backup --output ./posts.jsonl
```

The default archive stays **`~/Documents/data/linkedin-posts.jsonl`**. `~/code/blog/scripts/linkedin_blog_map.py` continues to read it unchanged. Posts/comments retain `type`, identity, content, links, author fields, reply parents, dates/confidence, raw text, media, analytics and completeness statistics. Unknown archive fields survive import/export. `--schema backup` emits plain JSONL, without the CLI's record/summary wrappers; only previously imported or backed-up rows are included, so unrelated feed/search results do not enter the blog archive. `--kind post|comment`, `--since` (observation time) and an explicit `--limit` can narrow an export. Export defaults to all saved backup rows.

Each completed post is merged into the archive using stable type/ID identity, written through an atomic replacement, then committed to SQLite. Historical rows and richer identity/content survive partial crawls; snapshot counters may decrease or reach zero. An incomplete repost scrape keeps previously saved repost details. A failed write leaves the preceding archive intact. A process lock rejects concurrent writers to the same archive, including writers using different cache accounts, and reclaims locks left by dead processes. Reimporting the durable JSONL rebuilds the searchable cache. Rerunning a backup re-scans activity and upserts by identity; it does not claim a resumable LinkedIn DOM cursor or complete historical coverage.

Detailed analytics covers visible discovery/profile/engagement metrics, video views/watch time, profile-viewer summaries, all six available demographic tabs, and public reposts. Selection uses the logged-in author's saved original posts and stable activity dates; `--since` is inclusive and `--until` exclusive. Private reposts remain inaccessible and completeness statistics report remaining loaders/missing rows. Fast `analytics POST` remains a smaller visible-summary read; detailed collection is explicit through `backup --analytics`.

Backup options: `--archive PATH` (`--file` alias), `--no-comments`, `--analytics`, `--since`, `--until`, `--max-scrolls` (240; `--max-pages` alias), `--max-comment-rounds` (30), `--settle-ms` (800), and `--limit` (100; 0 removes only the post limit). `--output` saves the command report; `--archive` selects the durable data file. `--dry-run` previews without browser/cache/archive writes. Fish expands `backuplinkedin.py` to `linkedin backup me`; use the new backup flags rather than the old `posts --username ...` syntax. Scheduled/noninteractive invocations should be updated explicitly because fish abbreviations apply only while typing commands.

Existing data can also be imported independently after `whoami` registers the account:

```bash
linkedin import archive ~/Documents/data/linkedin-posts.jsonl
linkedin import archive ~/Documents/data/linkedin-invites.json
linkedin import history ~/Documents/data/browsing-history.db
```

Imports are local and idempotent. JSONL is streamed in batches. Browsing history is read-only and exact-host restricted; importing links does not fetch profiles.

## Readable Markdown documents

Markdown output is designed to be saved and read as a document:

- Profiles have an About section and readable experience/education headings.
- People, company, invitation and browsing-history lists use tables with plain names and raw URLs in the final Link column.
- Posts retain their full text, author, publication date, engagement counts and attachment links.
- Analytics use compact Reach, Engagement and Profile activity lists, with grouped audience data. Raw page navigation text is omitted.
- Comments form threads with local reply links; member activity distinguishes the actor from the target post's author.
- Cache status, imports, backups and previews use summaries rather than JSON dumps. Empty results, stale data and pagination use plain language.
- `--fields` preserves all selected fields: lists for one record, tables for multiple records, with link columns last.

Headings include date ranges and result counts, for example `# Post analytics (30d, 4 posts)`. Metadata shares a line and simple metric/value summaries use lists. Numbers use separators, dates state UTC where time is known, month-only dates keep their precision, and unavailable metrics use an em dash. A result has one document title; embedded source headings and unfinished code fences cannot swallow the rest of the export.

```bash
linkedin profile me --sections experience,education --output profile.md
linkedin sync analytics me --since 7d --limit 20 --max-pages 5 --output analytics.md
linkedin comments POST_URL --output discussion.md
linkedin cache status --output cache.md
```

See [examples](evidence/markdown-examples.md). JSON, JSONL and text output contracts are unchanged.

## Agent interface

```bash
./linkedin --describe
./linkedin --params '{"args":["search","people","data science"],"limit":3,"fields":"id,name,url"}'
./linkedin profile me --dry-run
./linkedin search posts "agents" --format ndjson
```

Markdown is the default, including when piped; `md` aliases `markdown`. Interactive Markdown uses `glow -p`; if unavailable it uses `$PAGER`, otherwise prints raw Markdown. Structured formats, pipes and `--output` files bypass viewers. Use `--format json` or `--format ndjson`/`jsonl` for machine-readable output. `--describe` always returns JSON. Progress goes to stderr. JSON output has `ok`, `schema_version`, `data`, source/account metadata, coverage and warnings where applicable. NDJSON emits typed record lines followed by a typed summary. `--fields` supports nested paths; `--format markdown` is useful for profiles. `--output PATH` writes a private output file. `--dry-run` previews the operation without opening a browser or changing the cache.

Errors are structured JSON with nonzero exit status: e.g. `AUTH_REQUIRED`, `BROWSER_UNAVAILABLE`, `ACCOUNT_MISMATCH`, `RATE_LIMITED`, `CURSOR_EXPIRED`, `ENDPOINT_CHANGED`, `SCHEMA_CHANGED`, `CACHE_MISS` and `SYNC_BUSY`. Authentication challenges stop the read; the user completes them in the browser. The client does not store passwords, cookies, CSRF tokens or raw response envelopes. It also works without an existing LinkedIn tab when the browser session is already authenticated: it creates an owned background tab.

No account-changing commands are implemented. The API is unofficial and can change; [RESEARCH.md](RESEARCH.md) documents access and platform limitations.

## Implementation and validation

See [DESIGN.md](DESIGN.md) for module boundaries and how to add capabilities, [notes.md](notes.md) for the investigation log, and [CLI validation](evidence/cli-validation.json) for sanitized live results.

```bash
just test
# equivalent:
node --test tests/test_linkedin.mjs test-probe.mjs  # assumes Chromium is already installed
```

91 standalone tests cover graph root selection, encoding/input validation, unknown schemas, auth/rate-limit errors, FTS updates, sparse merges, account isolation, atomic rollback, disconnect/kill recovery, imports, reply parents, analytics label order, native backup/archive recovery, offline reads, field masks and NDJSON. Live scenarios cover the command families above; API activity pagination returned six records over two pages. The scripts repository’s `just test` suite includes the standalone tests. The native test file includes isolated headless Chromium fixtures (installed by `just playwright-install`), with a fresh temporary profile and network interception; it never uses the logged-in browser or imports the archived Python module. No credentials or personal cache database are included in either repository.

The original dependency-free research probes remain available as `probe.mjs` and `http-probe.mjs`.

On 9 November 2026, the standalone script’s **30 tests passed** through `~/code/scripts/just test-linkedin-api`. Full `just verify` stopped at two unrelated prompt assertions in `tests/test_transcribe.py`; the remaining timestamp recipe passed separately. The existing Python LinkedIn CLI/backup tests passed in the full run.

Markdown document improvements are covered by 91 standalone tests. The formatter was also checked against all eight cached record kinds, with 24 unchanged JSON/JSONL/text comparisons, 16 parsed Markdown documents, and headless previews of analytics and comment anchors. The full verification run still stops on the same two unrelated transcription assertions.

Native backup migration validation: [aggregate evidence](evidence/native-backup-validation.json). All 3,403 original rows round-tripped losslessly; the unchanged blog loader produced identical documents, dates and links for 326 original posts. A one-post installed backup updated the real archive to 3,405 rows without modifying any original row. Native detailed collection captured six demographic tabs and the visible public repost. The former Python test file is archived at `~/code/scripts/archive/test_backuplinkedin.py`; its backup regressions now exercise the native implementation in `tests/test_linkedin.mjs`.

Human-input and command validation: [aggregate evidence](evidence/human-input-validation.json) and [backup-test migration coverage](evidence/backup-test-migration.md). The connections decoder now handles a valid connection whose profile details are omitted, retaining its identity/date rather than aborting the page with `SCHEMA_CHANGED`.
