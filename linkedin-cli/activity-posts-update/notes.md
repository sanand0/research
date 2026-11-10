# Activity and post output update — 2026-11-10

Done: compact Markdown post headers; correct repost contents and truncation detection; profile-first activity identity resolution; multiple actors in latest order using native LinkedIn filters where supported; companies; regression and bounded live checks; cleanup findings documented.

- Existing standalone CLI and tests are maintained in this research folder and installed under `~/code/scripts`. Working tree has unrelated untracked research files; preserve them.
- CDP at localhost:9222 is reachable, including two supplied example post tabs. Live credentials will be tested through the CLI.
- Found truncation inferred from *any* button in an expandable text box, including collapse controls. Feed extracts only the first commentary and never the embedded repost.
- Found package.json points at nonexistent linkedin.mjs instead of linkedin.
- Native lists article describes Posts search with From member and Latest, rather than a merged profile timeline. Investigate native search facets.

- Live four-example comparison: API and independently rendered DOM text match exactly at 1550, 447, 468 and 1199 characters. The initial collapse-control hypothesis was incomplete: feed HTML retains decorative `aria-hidden="true"` “… more” buttons even after full text is present. Ignore these; keep genuine unexpanded controls flagged and hydrate through the API.
- A real repost (7521206725807419393) uses `*resharedUpdate`, which the old decoder ignored. Its 680-character comment now includes the 278-character original (7521186532800708609), independently fetched and matched. Also handle direct legacy and wrapped reshares with cycle guards and original activity IDs.
- Native author-only GraphQL rejects `keywords:''` (HTTP 400) but succeeds when keywords is omitted. `fromMember` accepts multiple profile IDs; `fromOrganization` accepts company IDs; mixed filters return both. Sort returned records explicitly, including cached reads.
- `openai` profile lookup is HTTP 403, while exact company slug resolves to company 11130470. People search for openai returns unrelated people who mention OpenAI. Therefore try exact company after failed profile identity and before generic people-name search; never switch the type of explicit URLs/URNs.
- Full name search can still choose the wrong person under the existing first-personalized-result contract. “Rama Ramakrishnan” selected Ramakrishnan Venkataramanan in this session; exact `ramar` resolves correctly. Document for review; do not silently change the existing name-ranking contract.
- Regression tests exposed undersized fresh cached pages and stale membership after refresh. Require enough cached records when a continuation exists, and replace membership on the first committed page of a fresh traversal. Historical records remain searchable.
- Reproduced intermittent CDP failure: Target.closeTarget acknowledgement can precede removal from /json/list. The next invocation borrowed the closing source tab and lost the websocket during whoami. Wait for disappearance during cleanup. Regression fails before the fix; two consecutive live no-tab bootstrap/identity/cleanup cycles now succeed.
- Native activity identities are deduplicated/canonically ordered for shared cache keys; actual resolved actors are exposed in output. Comments/reactions remain single-profile operations with explicit validation for unsupported combinations.

- Final validation: research `just test` passed 103/103; installed `just test-linkedin-api` passed 101/101. Installed runtime/tests are byte-identical to the research copies. The installed command returned both requested member authors and a three-line repost header with the original contents.
- Completed live verifier after the cleanup fix: four API/DOM text matches, six refreshed activity variants with offline ID parity, independently fetched repost original, and two consecutive source bootstrap/identity/cleanup cycles. Aggregate evidence is saved without raw API bodies or credentials.
- Installed only the tested executable/test file after guarding their pre-existing hashes; updated the one-line root research index. Saved the scoped scripts-repo diff as scripts.patch. Unrelated research and scripts changes remain untouched.
