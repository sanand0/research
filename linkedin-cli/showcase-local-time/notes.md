# Local post time and showcase activity — 2026-11-10

Done: post dates in Markdown use the process/system local timezone and omit the activity-ID suffix; showcase URLs work as explicit organizations; determine and verify bare claude resolution without breaking profile-first ambiguity handling. Preserve JSON timestamps and other output contracts. Test, install, document and save a scoped research commit.

- Starting source and research tree are clean. Existing installed runtime/tests include the previous task's uncommitted installation; compare/guard them before updating.
- Inspect existing company decoder because LinkedIn showcase pages may share the organization entity namespace and author-search filter.

- Verified live authentication and system timezone Asia/Singapore. `/in/claude/` resolves to Claude Schitter; organization universalName `claude` resolves to company 106863934 with canonical URL `/showcase/claude/`.
- User explicitly chose to keep profile-first resolution and use `showcase:claude` or the showcase URL. No bare-name exception or hardcoded brand alias.
- Reused the company decoder and native `fromOrganization` filter for showcases. Both explicit target forms returned three direct Claude posts; all three IDs occur on the independently rendered showcase page. Offline reads preserve IDs.
- Added failing regression tests before the implementation: local-time date rollover, summer/winter DST offsets, retained JSON timestamps/date-only precision; showcase URL/type/input validation; explicit organization resolution bypassing the same-name profile; native list and offline reuse.
- Changed only post publication-date formatting; other timestamp displays remain UTC. Date-only and month-only observations preserve precision. Activity-ID provenance remains in JSON without a Markdown suffix.
- Research suite: 105 tests passed. Live aggregate evidence saved in live-checks.json, with exact resolved entities, representative post IDs and local-time Markdown headers; no credentials or raw API responses.

- Installed runtime/tests match the research files byte for byte. Installed `just test-linkedin-api`: 103/103 passed. Installed `activity showcase:claude` returned three Claude-authored posts; its offline Markdown showed 10 Nov 2026, 04:45 GMT+8 with no activity-ID suffix.
- Updated help, schema, README/design and root one-line index. Saved the incremental runtime/test diff in changes.patch. Preserved unrelated changes and the previously uncommitted scripts installation.
