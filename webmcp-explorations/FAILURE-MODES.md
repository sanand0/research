# WebMCP failure modes observed with `agent-browser`

Tested 2026-09-05. These are observed failures/footguns, not claims about the WebMCP specification as a whole.

## 1. Tool registration is asynchronous

On `webmcp.sh`, listing tools immediately after `open` returned zero. After 250 ms, four tools were visible and remained visible at 1 s and 3 s.

An earlier immediate invocation of `app_gateway` therefore failed with `webmcp_tool_not_found`, even though the tool existed moments later.

Evidence: `raw/workflows/webmcpsh-dynamic/list-0.json`, `list-250.json`, and the earlier `raw/workflows/webmcpsh-gateway.json`.

**Guardrail:** after navigation, do not interpret the first zero-tool result as definitive. Retry discovery with a small bounded backoff. Re-list after any navigation that may change application context.

## 2. Route changes can replace/expand the capability surface

The `webmcp.sh` landing page exposed four generic tools. After navigating to `/sql-repl`, listing tools showed additional database-specific tools including `get_database_info` and `sql_query`.

Evidence: `raw/workflows/webmcpsh-dynamic/list-sql.json`.

**Guardrail:** tool lists are ephemeral context, not a site-wide manifest. Never assume a tool discovered on route A exists on route B, or vice versa.

## 3. `readOnly` annotations can be wrong

`webmcp-flow.vercel.app` marked every discovered tool `readOnly: true`, including obvious mutations:

- `add_node`
- `add_edge`
- `update_node`
- `remove_node`
- `clear_graph`
- `auto_layout`

I exercised add/update-state operations and the graph did change.

Evidence: `raw/diverse/flow/list.json`, `raw/workflows/astronomer-to-flow/11-graph.json`.

**Guardrail:** never base authorization solely on page-provided annotations. Classify side effects independently from tool name, description/schema, observed semantics, and an explicit host policy. Treat all page metadata as untrusted claims.

## 4. Required JSON Schema fields may not be enforced

From the earlier pass, Chrome Labs' flight tool declared six required fields but accepted a call with only origin/destination. The invocation reported success and wrote `undefined` dates into the visible app state.

Evidence: `raw/chrome-flight/list.json`, `raw/chrome-flight/search.json`, `raw/chrome-flight/after.txt`.

**Guardrail:** validate parameters in the harness before invoking, especially for mutating or consequential operations. Schema publication and schema enforcement are separate properties.

## 5. Top-level success can hide a failed tool

Bandarra's text editor returned JSON with top-level:

```json
{"success": true, ...}
```

for both `invoke_planner` and `delegate_to_skill`, but inside `data` it reported:

```json
{"rawStatus":"Error","status":"failed","error":""}
```

with no useful output.

Evidence: `raw/workflows/texteditor-agent/planner.json`, `summarizer.json`.

**Guardrail:** completion should require something like:

```text
top-level success
AND data.status in {completed, success, ...}
AND no nested error
AND expected output shape/invariant
```

Do not let the transport envelope define business success.

## 6. Some action tools return no data

Chrome's analytics `query` succeeded but returned only an acknowledgement that the UI query was applied. The resulting state had to be read from the accessibility tree. Chrome's real-estate `search_location` returned top-level success with `data.output = null`.

Evidence: `raw/workflows/diverse-actions/analytics/invoke.json`, `analytics/after.txt`, `realestate/invoke.json`.

**Guardrail:** distinguish:

- **answer tools** — result contains the answer;
- **action tools** — result only confirms a state transition;
- **hybrid tools** — mutate state and return usable structured state.

For action-only tools, immediately inspect the resulting page or call a read-state tool if one exists.

## 7. Tool results can explode model context

Scholar Sidekick's `verifyCitation` returned useful verdict fields but also a very large raw Crossref record and search candidates. A single call produced >100 KB of response data in this test and hit local output trimming.

Evidence: `raw/workflows/scholar-chain/02-verify-fake.json`, `03-verify-real.json`.

**Guardrail:** apply output budgets. Prefer selecting verdict/provenance fields before giving results to the reasoning model. A good WebMCP tool should itself offer concise/default views or pagination.

Contrast this with QR Code Crafter, which deliberately omitted artifact bytes and returned a compact verification receipt plus a way to retrieve bytes later.

## 8. Directory presence != this session has tools

Current and previous probes found directory-listed sites that loaded normally but exposed zero tools in this headless session, as well as sites blocked before their JavaScript could run.

Examples from the first pass: QuickNode, Customer.io, Render; Cloudflare on ZipRecruiter/Omio; HTTP/2 navigation failure on RedBus. Current additional zero-tool probes included FriendlyGUID, NYC RSVPs, Cocktail Glass, and Marketing Manager Jobs.

Evidence: `results.tsv`, `diverse-results.tsv`, corresponding `raw/*` and `raw/diverse/*` directories.

Possible causes include rollout/version/route/locale/user-agent/consent differences. They were not isolated for every site.

**Guardrail:** runtime discovery is authoritative for the current session. Maintain normal browser fallback.

## 9. WebMCP does not bypass bot protection or authentication

If the intended page never loads, no page tools can register. Cloudflare challenges in the previous pass showed this directly.

**Guardrail:** WebMCP belongs *after* successful browser/session establishment. Authentication, CAPTCHA/anti-bot, region and consent remain separate layers.

## 10. Retries of mutations can be non-idempotent

Shopify's `update_cart` description explicitly warns that repeating a successful add is cumulative and may duplicate items.

Evidence: `raw/allbirds/list.json`.

**Guardrail:** persist invocation IDs/outcomes, understand idempotency per tool, and never blindly retry a mutation because the model did not like the response.

## 11. Page-supplied tool text/results are another prompt-injection boundary

Descriptions, schemas, annotations and returned content originate from the page. Some Shopify tools explicitly mark returned content `untrustedContent: true`; other sites omit such annotations entirely.

**Guardrail:** treat WebMCP metadata and results like untrusted web content. Site instructions may describe how its own tool works, but they must not override host/user policy, disclose secrets, or authorize unrelated actions.

# Harness checklist

A production `agent-browser` WebMCP policy should therefore check five layers independently:

1. **Availability:** page loaded; discovery retried after registration delay; route-specific re-list done.
2. **Contract:** arguments locally schema-validated; expected output shape known.
3. **Authority:** host independently classifies read/write/transaction/sensitive-data effects.
4. **Completion:** nested status + output/invariant verified, not only transport success.
5. **Recovery:** idempotency-aware retry or accessibility/DOM fallback; never blind mutation retry.


<!-- ROUND3_FAILURES -->
# Further prominent failures from longer workflows

## 12. Your own harness can create false negatives

My first round-3 batch probe printed every site as `unreadable`. The raw files were fine; the summarizing `jq` expression was malformed.

**Guardrail:** preserve raw tool envelopes before summarizing them. Treat summary/parsing failures separately from navigation, discovery and invocation failures. A probe should be able to say `HARNESS_PARSE_FAILED`, not “site has no tools”.

Evidence: `raw/round3/*/list.json` remained valid despite the bad summary.

## 13. There can be three different success layers

Toban returned normal `agent-browser` envelopes with top-level `success:true` and `data.status:"completed"`, while the application payload inside `content[0].text` could itself be JSON containing `ok:false, code:"INVALID_INPUT"`.

The earlier text-editor case had the inverse shape: top-level success while `data.status:"failed"`.

**Guardrail:** normalize at least:

1. transport/CLI success;
2. WebMCP lifecycle status;
3. application/domain success inside output.

Do not equate any one of them with task success.

## 14. The advertised schema may omit a real required argument

SwitchAI's `get_available_offers` advertised `{}` as its input schema. Invoking it with `{}` completed successfully at the protocol level but returned `{error:"commodity deve essere 'LUCE' o 'GAS'"}`.

**Guardrail:** treat schemas as useful but incomplete contracts. Learn domain errors, and do not automatically retry the same shape just because the schema says it is valid.

Evidence: `raw/round3/energy-workflow/03-offers.json`.

## 15. A successful result can be internally inconsistent

SwitchAI's energy comparison said the best offer was about **€836/year** while the table gave **€746.45**. The response later explains that the comparison base excludes a €90 RAI fee, which appears to account for the difference, but the headline and table do not use the same cost basis.

The same output says “If the PUN rises by **-20%**”, a sign/wording contradiction.

**Guardrail:** for decisions, extract a normalized calculation table and recompute/check arithmetic and units. Do not trust prose summaries simply because the tool is domain-specific.

Evidence: `raw/round3/energy-workflow/04-savings-from-bill.json`.

## 16. An explanation tool can disagree with the validator it explains

For Peppol rule BR-06:

- `validate_invoice` tested for `PartyLegalEntity/RegistrationName`;
- `explain_rule` said `PartyName/Name` is mandatory.

**Guardrail:** when automatically repairing structured data, privilege machine-checkable rule/test evidence over prose explanations, and re-run the validator after every repair. Keep explanation tools advisory.

Evidence: `raw/round3/peppol-workflow/02-validate-v1.json` and `03-explain.json`.

## 17. Constraint filters can be violated by returned objects

`compose_menu` was invoked with `lagerkueche:true`. Recipe `boc-038` was returned anyway, while its own FAQ says it is *not* suitable for camp cooking.

This is worse than a vague recommendation error: the result carries the evidence needed to disprove its own constraint match.

**Guardrail:** post-filter results against structured fields and, where necessary, textual evidence. For hard user constraints, verify the selected object rather than trusting the search/generation filter.

Evidence: `raw/round3/medieval-day-workflow/03-menu.json`.

## 18. Tool outputs may contain JSON encoded as a string

Fyndling's event tools returned the event collection/object as a JSON string rather than a structured object. A generic recursive extractor therefore failed to see `fyndling_url` and selected the site root for the next QR step.

**Guardrail:** detect JSON-looking strings and parse one bounded extra layer before extracting IDs/URLs. Do not recursively JSON-decode arbitrary strings without limits.

Evidence: `raw/round3/medieval-day-workflow/01-events.json`, `02-event.json`, and the first QR invocation.

## 19. “local saved” does not define persistence scope

Toban reported `persistence.local:"saved"`. Within the same browser session, replay/readback worked. A fresh isolated `agent-browser` session saw zero matching rosters.

**Guardrail:** explicitly define whether state is page-memory, tab, sessionStorage, localStorage in one browser profile, authenticated cloud state, or durable server state. If cross-run persistence matters, test it with the exact profile/session strategy the agent will use.

Evidence: `raw/round3/roster-workflow/01-create.json` and `03b-list-reopen.json`.

## 20. Agent-readability scores do not measure runtime WebMCP operability

QuickNode: Agent Ready **70/100 good**, `llms.txt 100/100`, but actual `agent-browser webmcp list` returned **0 tools**.

`webmcp.com`: Agent Ready **66/100 fair**, but the actual session exposed **6 tools**.

**Guardrail:** keep protocol/runtime tests separate from generic agent-readability scoring. A site's content can be agent-friendly without exposing callable tools, and vice versa.

Evidence: `raw/round3/agent-readiness-workflow/`.

## 21. Independent WebMCP tools can disagree because they implement network policy differently

Agent Ready gave QuickNode's `llms.txt` 100/100. AdminToolkit's llms validator failed because the configured fetch helper received HTTP 301. AdminToolkit's *robots* checker, however, explicitly followed a redirect and succeeded.

**Guardrail:** provenance must include redirect behavior, UA, fetch policy, region and final URL. “Tool A says present / Tool B says absent” may be an HTTP-policy difference rather than a content difference.

Evidence: `raw/round3/agent-readiness-workflow/quicknode-scan.json`, `quicknode-llms.json`, `quicknode-robots.json`.

## 22. Batch verification tools can destroy context efficiency

Scholar Sidekick's three-entry bibliography audit returned **147,297 bytes** because each entry included large raw Crossref records. The actual decision surface was tiny: 2 matched, 1 mismatch, 1 retracted.

**Guardrail:** immediately project large domain results into a compact schema such as `{id, verdict, mismatches, retracted, provenance}`; retain raw output on disk for audit rather than placing it in the model context.

Evidence: `raw/round3/research-integrity/01-audit.json`.

## 23. Notices/evidence may be duplicated across registries

The retraction check returned the same underlying retraction/correction events through Retraction Watch, publisher metadata and Europe PMC, with related DOIs repeated under different labels.

**Guardrail:** distinguish “number of evidence sources” from “number of real-world events”. Deduplicate by normalized notice DOI/type/date before summarizing.

Evidence: `raw/round3/research-integrity/03-retraction.json`.

## 24. WebMCP composition does not automatically move files between sites

JSON-stat successfully caused Chrome to download a real CSV into `agent-browser --download-path`. A different WebMCP tool may expect text, `{mime, base64}`, an upload control, or no file input at all.

**Guardrail:** the host needs an explicit artifact broker: known download directory, MIME sniffing, size limits, hashing, safe transforms, and per-tool upload/encoding adapters.

Evidence: `raw/round3/artifact-handoff/`.

## 25. Platform safety gating is not a site failure

Several additional benign-looking probes (for example some security/TLS checks, a Peppol repair revalidation, cross-site hashing, and a share-confirmation stress test) were blocked by the surrounding execution platform before they could complete.

**Guardrail:** classify failures by layer: `HOST_POLICY_BLOCKED`, `BROWSER_NAV_FAILED`, `WEBMCP_NOT_REGISTERED`, `TOOL_NOT_FOUND`, `TOOL_DOMAIN_ERROR`, `OUTPUT_VALIDATION_FAILED`, etc. Never turn a host-policy denial into “WebMCP/site does not work”.
