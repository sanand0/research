# Extending the LinkedIn CLI

The unit of extension is a **read operation that returns records plus a continuation**, not a separate browser script with its own cache and error format. A small explicit dispatch is preferable to a plugin framework until more than one independent extension needs one.

## Why these capabilities

The browsing-history snapshot (February–November 2026) contained 3,296 exact-host LinkedIn history records and 150 shortcuts. Profile pages and member activity dominated, followed by people search, own-post analytics, network and post detail. Jobs appeared only four times across the matching sources. [Aggregate evidence](evidence/history-summary.json) excludes individual profile/post URLs and query text.

The existing scripts add use cases that URL frequency alone misses:

- `linkedin.py`: profile/experience/education, Markdown, refresh/TTL and authenticated browsing without a pre-opened LinkedIn tab.
- `backuplinkedin.py`: incremental post/comment backups, stable reply parents, media, engagement counts, analytics by time period, demographics and public reposts.
- Existing JSONL/JSON archives: useful data should be searchable immediately, without repeating the entire crawl.

Accordingly, native API reads handle frequent small requests; importers reuse existing data; native background CDP handles detailed backups, preserving the existing JSONL as a stable public format for the blog. The Python implementation is archived.

## One standalone script and one test file

`~/code/scripts/linkedin` is the installed source; `linkedin` here is an identical copy. `~/code/scripts/tests/test_linkedin.mjs` is the single combined test, run by `just test-linkedin-api` and included in the scripts repo’s `just test` / `just verify`. No runtime bundler or local-module imports are needed. Backup regressions are consolidated into this test file, including a separately owned headless Chromium fixture profile. Archived Python tests are excluded from the active suite.

The script keeps logical sections and named functions/classes for CDP, pure validation/decoders, DOM fallbacks, the operation manifest, SQLite `Cache`, bounded `sync`, archive/history import, native backup/archive persistence, `Client`, and CLI/rendering. These boundaries remain testable without splitting deployment into multiple files. Node’s standard library supplies the dependencies. No Python subprocess or archived code is loaded. A lossless `backupRow` accompanies normalized post/comment records and is excluded from the FTS index to avoid indexing duplicate raw content. Compatible exports include only saved backup rows.

People-search inputs are validated by `searchFacets`, resolved through allowlisted SDUI typeahead reads by `resolveSearchFacets`, and normalized to the exact IDs passed to Voyager/cache keys. All returned matches are OR within a facet; facets are AND. `resolveProfileTarget` chooses the first personalized people result. Account-scoped lookup rows preserve these bindings offline and across resume; a per-invocation memo avoids repeated requests for the same term. Own-post `syncAnalytics` uses the shared page/checkpoint engine while `saveAnalytics` durably updates both the analytics record and canonical post after each successful fetch. A failed later post does not discard completed metric updates.

## Record and page contracts

Every persisted record has `id`, `kind` and a `source`. Records can also carry `name`, `text`, `url`, `author`, `observedAt`, `sections`, media, metrics or relationship fields. Complete URNs keep namespaces distinct. Profiles, posts, comments, activity observations, companies, invitations, analytics snapshots and history links have distinct kinds.

A page adapter returns:

```js
{ records: [/* normalized records */], next: { start, token } /* or null */,
  source: 'voyager', warnings: [] }
```

An API decoder starts at the operation's root collection and resolves its references through `included`. It must not scan all included profiles/posts and assume they are requested results. Search view models may contain display fields while included Profile objects are merely references. Activity observations preserve both the selected actor and the target post's actual author.

The sync engine saves the whole page and continuation atomically, then applies the output limit. Root IDs, next tokens and termination are validated. It never treats `paging.total == 0` as proof that a token-bearing activity collection is empty.

SDUI home-feed streams have been captured/replayed by the research probes, but a complete semantic stream decoder is not implemented. The shipped client reports `dom-feed` and bounded visible coverage. A future stream adapter can replace the feed method while keeping the record/page/cache contracts.

## Storage and freshness

One SQLite file contains account-scoped records, FTS5 indexes, collection memberships, continuation checkpoints, run summaries and short collection leases. WAL mode and a busy timeout allow local readers while imports/syncs commit pages. Indexes support account/kind, URL, post/comment relationships and FTS lookup. A future incompatible schema version is rejected rather than overwritten.

Records merge sparsely: a reduced API response cannot erase media, analytics or reply data already obtained from an archive. Older timestamped archive rows can enrich missing fields without overwriting a newer observation. Missing values are not interpreted as deletions. An observation timestamp does not claim simultaneous freshness for every retained field; archive analytics retain their own scrape metadata.

Collection membership records ordering/seen time independently of the canonical record. Thus importing another dataset does not change which records a query returns. Current membership is a union of observed records, not a deletion-aware replica. Repeated ranked-feed appearances are collapsed by post ID within a collection; recording every placement/recommending actor separately is future work.

`--resume` reads a checkpoint for that account/query. A new head refresh ignores it. Tokens remain in SQLite; stdout only indicates whether continuation is resumable. Feed continuations are process-local and explicitly cannot resume across invocations. Dead-process leases are reclaimed immediately; live leases prevent simultaneous traversal of the same collection. Different operations can run independently.

The database and output files use mode 0600; newly created cache directories use 0700. No HTTP cookies, session headers, passwords or raw API response bodies are stored. The imported public/private data remains sensitive user data and is ignored by Git.

## Add a capability

1. Capture a small current UI/API sample in a background tab; verify identity, permissions, response shape and semantics. Record the capture date.
2. Add operation metadata/query ID in the operation manifest.
3. Add a pure decoder and synthetic fixture tests in the pure decoder section and combined test file. Include unrelated entities, missing references, empty results and next-page behavior.
4. Add a small method in `Client` returning the page contract, or an explicitly named DOM/legacy adapter when a stable API read is unavailable.
5. Register dispatch/argument rules in the CLI dispatch section. Reuse `sync` and `Cache.commit`; do not add per-command credential or caching code.
6. Run a bounded live semantic comparison and verify offline output with the browser unavailable. Add sanitized counts to evidence and document the capability's limits.

A different backend (direct HTTP, official portability API or a future SDUI decoder) should implement the same operation/page contract. Endpoint acceptance, decoding and completeness are separate facts and should stay separate in output and tests.

For future account-changing operations, create a separate explicit command family with destination validation, previews, dry-run and deliberate execution. The current generic transport only permits Voyager GET reads; it does not expose an unrestricted API request command.

## Current boundaries

- Detailed comment/reply, demographic and public repost collection uses bounded native CDP. Completeness is reported per observation; LinkedIn can withhold private or filtered data.
- Comments/reactions activity preserves owner/target context but does not claim full detail/UI parity.
- Profile sections currently support experience, education and skills. The old script's suggested certifications/projects/languages/etc. are candidates for additional section adapters after capture.
- Home feed is a ranked, partial snapshot, not a complete following stream or historical archive. Unidentified cards remain explicit warnings.
- People-search location, current/past organization and degree facets accept real IDs/URNs. Name/typeahead resolution, outgoing invitations, messaging, jobs, notifications, scheduling and write commands are future capabilities. They are not silently approximated by keyword concatenation or DOM heuristics.
- Unknown/null values preserve prior known cache values; deletion tracking and per-field freshness are not implemented.

## Markdown presentation

Markdown is a pure document view over the normalized record contract. The CLI passes command context to the renderer for useful titles and query summaries; it does not change JSON envelopes or cache records. Typed layouts cover people/company/network tables, profiles, posts, analytics, comment threads, member activity, cache status, imports, backups, previews and empty results. Explicit field selections retain every requested value, using lists for single records and tables for collections. Titles include range/count summaries, simple metrics use lists, and raw URLs occupy the final table columns.

Shared helpers format human labels, dates with their original precision, counts, safe links and balanced content headings/fences. Unknown metrics remain an em dash; zero remains zero. Markdown source may be saved directly with --output. JSON, JSONL and text formats retain their existing contracts.

## Scheduled reads, local paths and terminal presentation

Scheduled reads use only the `scheduledPostsList` and `scheduledPostFullRow` components, with actor `Self`. `readRscRows` reads JSON/data and length-prefixed UTF-8 text rows; decoders follow data references while skipping callbacks, tracking and action execution. Replacement membership snapshots remove cancelled items from the active list. Partial snapshot metadata prevents a small earlier request from hiding larger requested results. `appPaths` is pure and runs before SQLite/browser initialization.

`presentMarkdown` runs only for interactive Markdown: `glow -p`, then the user-configured PAGER, then raw output. Post dates precede author/headline metadata; activity-ID publication-time inference is tagged in machine records. Pipes, files and structured formats retain direct output.

## Activity/post corrections — 2026-11-10

Activity resolves explicit profile/company URLs and URNs without switching types. Bare usernames prefer a profile; missing/inaccessible usernames try an exact company slug before personalized people search. The exact-company step avoids treating a person who merely mentions OpenAI as that company. Native multi-actor Posts search uses `fromMember`, `fromOrganization`, and `date_posted`, omitting keywords entirely; a single member keeps its timeline endpoint. Output is sorted before limiting; offline collection reads order by publication. Actor identity deduplication and canonical ordering share cache keys across equivalent lists.

Voyager originals can be referenced by `*resharedUpdate`, supplied directly, or wrapped by `*update`. Decode all three with cycle protection; legacy original IDs come from `updateMetadata.urn`. Feed cards containing embedded commentary are hydrated through a post read. Do not infer missing text from an `aria-hidden` decorative more button: SDUI can keep the full text in the DOM while retaining that control. Visible expansion controls remain a truncation signal and trigger a bounded post hydration. Full API observations clear stale truncation flags. Media-only updates do not require commentary.

A new sync replaces collection membership in its first committed page, retaining canonical records and resumable page transactions. Fresh cached pages with continuations must satisfy the requested output count. These changes prevent stale members and undersized cached results from overriding a refreshed/larger list.
