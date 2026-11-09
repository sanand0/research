# A LinkedIn CLI through the underlying web APIs

The research below preceded implementation. See [README.md](README.md) for the working CLI and [DESIGN.md](DESIGN.md) for its current architecture and explicitly deferred capabilities.

**Investigated 8 November 2026.** Live tests used the existing signed-in browser at `localhost:9222`, plus temporary background tabs. No account-changing actions were intentionally issued. Normal page loads did emit LinkedIn telemetry and search-history requests. Evidence files contain response shapes and counts, without credentials or personal records.

## Recommendation

**Yes: a useful read-only LinkedIn CLI is feasible, including searches, profiles, member activity and your home feed.** This investigation retrieved real data through the underlying APIs, without extracting records by clicking through the UI.

Build a small client with **Voyager JSON as the first choice, an SDUI/React-stream adapter for the current home feed, and the existing browser as its initial authentication and request transport**. Offer direct HTTP as a separately tested backend. Put normalized records in SQLite for resumable collection and offline search.

The key scope correction is that “the LinkedIn API” is now several surfaces. A wrapper around old Voyager REST paths will cover some reads and fail on others. A maintained CLI must understand persisted queries and the newer server-driven UI protocol. Also, “sync” should mean incremental collection of accessible observations; it cannot promise a complete replica of LinkedIn or a chronological copy of the ranked home feed.

This is a feasibility study and design, with working research probes. It is not a finished general-purpose LinkedIn client.

## What worked in this session

The supporting record is [live-summary.json](evidence/live-summary.json). These are small samples from one account and browser version, not guarantees across accounts, regions or future releases.

| Capability | Live result | Strength and limit of evidence |
|---|---|---|
| Session identity | `/voyager/api/me`: 200, normalized JSON and MiniProfile | Worked through browser fetch and independently through Node HTTP with two in-memory cookies. |
| Full profile | `identity/dash/profiles`, `FullProfile-76`: 200 | Own profile and one member found through search both returned Profile, Geo and Industry entities. Full career history needs additional section reads. |
| People search | Persisted search query: 200 | Two pages of five results; zero entity-URN overlap. All five first-page names appeared in the rendered search page. |
| Content/post search | Same search query with `resultType=CONTENT`: 200 | Five Update entities; all five post-text prefixes matched the corresponding rendered content-search page. |
| Member posts | Persisted profile-updates query: 200 | Own posts: two pages of five root references, zero overlap. Another member: five root references. |
| Member comments activity | Category-specific profile-updates query: 200 | Five root references plus Comment and Update entities for the signed-in member. Detailed commenter/target attribution has not been normalized or UI-validated. |
| Member reactions activity | Category-specific profile-updates query: 200 | Five root references plus Update/social entities for the signed-in member. Detailed reaction attribution has not been normalized or UI-validated. |
| Personal home feed | SDUI main-feed pagination POST: 200; replay: 200 | Original capture contained seven distinct activity IDs; replay returned the same ID set. Five text passages matched the rendered feed. Independent probe repeated this with five IDs and matching replay. |
| Legacy home-feed REST | `/feed/updatesV2?q=feedByType&feedType=HOMEPAGE`: 400 | This older request shape is unsuitable for this session. It does not establish that all Voyager feed queries are gone. |
| Companies, jobs, connections, followers, saved posts, post details, comment threads, messaging | Not live-tested | Some are implemented by existing projects. Treat each as a separate capability requiring a current capture and semantic test. |

The member activity page itself remained on a bootstrap screen during the attempted background navigation. Consequently, activity API success and pagination are verified, but exact parity with the UI's Posts/Comments/Reactions tabs is **not** claimed. People search, content search and home-feed checks did compare representative API content with rendered results.

### Pagination findings that affect correctness

People search returned `paging.start/count/total`; the sampled total was 1,000. Do not interpret that as a complete population count or infer that every matching person is accessible.

Member activity returned five records and a `metadata.paginationToken` while **`paging.total` was zero**. Passing both the next offset and the returned token produced five new posts. Stopping on `total == 0` would silently discard valid history. Preserve token expiry metadata, detect repeated tokens/pages, and impose explicit page/item budgets.

For the home feed, replaying a captured continuation request reproduced the activity-ID set. Generating a new continuation chain, exhausting it, and recovering after token expiry were not validated. Its transport is proven; a complete feed synchronizer still needs implementation and testing.

## Which API surfaces are available?

### 1. Official developer APIs: useful, but not this full client

LinkedIn's documented open permissions include OpenID Connect identity/email and `w_member_social` for publishing and interactions. They do not provide the unrestricted people search, arbitrary-member activity and personalized home-feed access needed here. Most other products require approval. [Official access guide](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access).

Newer identity products also exist: `/rest/identityMe` provides the consenting member's profile details, with additional workplace/education fields tied to product tiers and scopes. This remains an identity integration rather than a general browsing API. [Profile Details API](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/verified-on-linkedin/api-reference/identity-me).

There is a particularly relevant official alternative for **your own archive**: Member Data Portability. The self-serve member product is documented for members in the EEA and Switzerland, with `r_dma_portability_self_serve`; the third-party product requires review and allows EEA members to consent. Snapshot and changelog endpoints support personal-data export, and the changelog covers events since consent within a 28-day query window. Eligibility was not tested on this account. These products do not replace arbitrary-user search or the home feed. [Member access](https://learn.microsoft.com/en-us/linkedin/dma/member-data-portability/member-data-portability-member/), [third-party access](https://learn.microsoft.com/en-us/linkedin/dma/member-data-portability/member-data-portability-3rd-party/).

Community Management is also not a blanket solution: its documented use restrictions include restrictions on exporting/storing member data and social-feed uses. [Product restrictions](https://learn.microsoft.com/en-us/linkedin/marketing/restricted-use-cases).

### 2. Voyager REST and persisted GraphQL: the practical structured read API

Base origin: `https://www.linkedin.com/voyager/api/`.

The live reads used:

```text
GET /voyager/api/me

GET /voyager/api/identity/dash/profiles
    ?q=memberIdentity
    &memberIdentity=<public identifier or accepted member identifier>
    &decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfile-76

GET /voyager/api/graphql
    ?variables=(<Rest.li-style variables>)
    &queryId=<operation>.<persisted hash>
```

Observed working query IDs:

| Operation | Query ID | Root collection |
|---|---|---|
| People/content search | `voyagerSearchDashClusters.e438ab99259203e9c1cd3f358e217282` | `data.data.searchDashClustersByAll` |
| Member posts | `voyagerFeedDashProfileUpdates.be2623b61657a92a693eb8d9c67aeec0` | `data.data.feedDashProfileUpdatesByMemberShareFeed` |
| Member comments | `voyagerFeedDashProfileUpdates.8f05a4e5ad12d9cb2b56eaa22afbcab9` | `data.data.feedDashProfileUpdatesByMemberComments` |
| Member reactions | `voyagerFeedDashProfileUpdates.3a42619bc23360ce8c29e737277e2ea9` | `data.data.feedDashProfileUpdatesByMemberReactions` |

These are observations, not stable API identifiers. The probes contain them to make this investigation reproducible. Capture replacements when the current web app changes; a matching operation name alone does not prove identical semantics.

People search variables were:

```text
(start:0,count:5,origin:GLOBAL_SEARCH_HEADER,
 query:(keywords:data%20science,
        flagshipSearchIntent:SEARCH_SRP,
        queryParameters:List((key:resultType,value:List(PEOPLE))),
        includeFiltersInResponse:false))
```

Content search replaced `PEOPLE` with `CONTENT`. Genuine company/geography/network filters should use the current query's facets and resolved IDs, rather than silently appending their display names to keywords. Those filter combinations were not tested here.

Member activity variables were:

```text
(count:5,start:0,profileUrn:urn%3Ali%3Afsd_profile%3A<id>)
```

The second posts page also included the returned `paginationToken`. Comments and reactions were tested with `includeWebMetadata=true`. Record that option per operation; do not assume it is universal.

Variables use Rest.li-style structure, not a JSON string: `(key:value,list:List(...))`. Encode scalar values, including URN colons and delimiter characters, without destroying the surrounding syntax. Do not interpolate untrusted search strings or URNs directly. Existing implementations expose both encoding and endpoint registries. [Toolkit implementation](https://github.com/OpenRecruiterTools/linkedin-toolkit/blob/7937c834dd068b35ace372f4f39da85ad82f7ac7/extension/src/background/voyager-core.js).

### Authentication and headers

Successful browser fetches used:

```text
credentials: include
csrf-token: <JSESSIONID cookie value, surrounding quotes removed>
x-restli-protocol-version: 2.0.0
accept: application/vnd.linkedin.normalized+json+2.1
```

The browser supplies session cookies, including HttpOnly `li_at`, automatically. Page JavaScript only needs the readable CSRF cookie; it does not need to extract `li_at`.

A separate live test read `li_at` and `JSESSIONID` through CDP into process memory, then issued `/voyager/api/me` through ordinary Node `fetch` outside the browser. With these two cookies, the CSRF header, the normalized accept header, protocol version and the browser's user-agent string, it returned 200 and a MiniProfile. [Direct HTTP evidence](evidence/probe-http.json).

That establishes direct HTTP feasibility for **identity only**. Search, member activity and SDUI were exercised through the browser's same-origin networking stack. Full HTTP-backend parity, long-lived sessions, cookie refresh and alternative network egress remain untested. Do not assume that a successful identity call establishes every endpoint's health.

### Decode an entity graph, not a flat record list

The normalized response is `{data, included}`, often with another `data` layer under GraphQL. Entities have `$type` and usually `entityUrn`; fields such as `*elements` and `*geo` reference other entities.

A correct decoder should:

1. Index entities by their complete URNs, keeping URN namespaces distinct.
2. Start from the requested operation's root collection and follow its references in order.
3. Resolve only the requested profile's experience/education/skills paths.
4. Separate post author, resharing actor, commenter, reacting actor and target post.
5. Preserve unknown/missing fields as unknown; report unresolved required references.

Scanning every included Profile or Update can mix in referenced authors, companies, related profiles and reshared posts. In the live search response, included Profile objects carried only `entityUrn`, `$recipeTypes` and `$type`; the result view models carried the display information. A profile object existing in `included` does not mean a full profile was returned. [Normalized-response reference implementation](https://github.com/OpenRecruiterTools/linkedin-toolkit/blob/7937c834dd068b35ace372f4f39da85ad82f7ac7/extension/src/background/normalized.js).

### 3. SDUI / React streams: needed for this account's home feed

Captured request:

```text
POST /flagship-web/rsc-action/actions/pagination
    ?sduiid=com.linkedin.sdui.pagers.feed.mainFeed
    &parentSpanId=<ephemeral value>
```

Observed JSON body structure:

```text
pagerId
clientArguments
  $type, requestedStateKeys, payload, requestMetadata,
  states, screenId, knownTemplateIds
paginationRequest
  $type, pagerId, trigger, retryCount,
  requestedArguments, onClientError
```

Both `clientArguments.payload` and `paginationRequest.requestedArguments.payload` contained `startIndex`, `count`, `token`, `feedSortOrder` and `requestType`. The request also carried `x-li-rsc-stream`, content type, CSRF and several browser application/tracing headers. The replay preserved captured application headers; this investigation did **not** establish the minimal required subset.

The response content type was `application/octet-stream`. It was a React-style framed stream, not a single JSON document. The first captured body had 4,437,729 JavaScript characters and approximately 1,002 hexadecimal row markers. Its replay had seven matching distinct activity IDs; five substantial text passages matched rendered feed text. A standalone repeat captured about 4.41 million characters with five IDs, again matching the replay. These are decoded text lengths, not measured compressed network transfer sizes. [Repeatable home-feed evidence](evidence/probe-home.json).

Implementation consequence: do not feed this into a Voyager JSON parser, and do not ship a regex over activity IDs as a full post decoder. IDs prove data is present; they do not reconstruct actor attribution, post boundaries, nested reshares, text references or pagination state. Implement a bounded stream decoder with row/reference resolution and root feed-item extraction. A browser DOM adapter can be an explicitly reported interim fallback while the stream decoder is incomplete.

The browser also uses `/flagship-web/rsc-action/actions/component`, `server-request`, `app-config` and a `server-stream-request` connection. Generic `server-request` actions can mutate state; an API client must allowlist known read actions rather than treat all POST requests as harmless reads.

## Existing projects and what to reuse

Repository heads were checked through GitHub's live API and recorded in [sources.json](evidence/sources.json). Source was inspected in temporary storage; no fetched repository is included here. This was source review, not an installation or end-to-end validation of those clients.

| Project | What it actually provides | Design lesson |
|---|---|---|
| [whatsmeow](https://github.com/tulir/whatsmeow) | A Go implementation of WhatsApp's web multidevice protocol, with incoming messages, receipts and app-state handling | Strong example of a protocol library separated from applications. LinkedIn's sampled reads do not supply an equivalent complete synchronization stream. |
| [twitter-cli](https://github.com/public-clis/twitter-cli) | CLI around X web GraphQL operations with session authentication; source resolves query IDs and can refresh them | The closest analogy for persisted queries, operation manifests and bounded cursor-driven commands. [Query-ID machinery](https://github.com/public-clis/twitter-cli/blob/7c634e0d396b1e7af9f63315b414925fe4f29ae7/twitter_cli/graphql.py). |
| [rdt-cli](https://github.com/public-clis/rdt-cli) | CLI using Reddit's JSON listing endpoints and authenticated OAuth endpoints | Useful command/output precedent, but a different backend: appending `.json` to Reddit routes is simpler than decoding LinkedIn SDUI. [Endpoint definitions](https://github.com/public-clis/rdt-cli/blob/5e4fb3720d5c174e976cd425ccc3b879d52cac66/rdt_cli/constants.py). |
| [OpenRecruiterTools/linkedin-toolkit](https://github.com/OpenRecruiterTools/linkedin-toolkit) | Browser-extension engine calling Voyager, with explicit endpoint registry and verified/unverified distinctions | Best starting reference for the browser-bound transport and search/profile normalization. Several query/decorations from its registry worked in this session. It is not evidence of a complete current home-feed solution. [Endpoint registry](https://github.com/OpenRecruiterTools/linkedin-toolkit/blob/7937c834dd068b35ace372f4f39da85ad82f7ac7/extension/src/background/voyager.js). |
| [bvgroup-co/lnk](https://github.com/bvgroup-co/lnk) | Existing Go CLI with profiles, searches and category-specific activity implementations | Evaluate before creating a second complete CLI. Its comments/reactions query IDs worked here. Its README warns that feed support is limited; the sampled legacy feed request failed. [Source](https://github.com/bvgroup-co/lnk/blob/9ff8a92448094a27307257d9e2e43221328392ed/internal/api/voyager.go), [limitations](https://github.com/bvgroup-co/lnk#known-limitations). |
| [vicnaum/linkedin-toolkit](https://github.com/vicnaum/linkedin-toolkit) | Detailed endpoint notes and browser-session integration | Useful reference, with an April 2026 verification date. Validate its assumptions against current traffic. |

`tomquirk/linkedin-api`, often linked as the original Python library, returned GitHub 404 during this investigation. An indexed SDUI reference at `mguttmann/linkedin-internal-api` also returned 404 from GitHub and its raw source URL. A search-index result is not proof a project remains available; neither is recommended as a currently obtainable foundation.

**Build-versus-adapt choice:** first run a bounded compatibility evaluation of `lnk` and the toolkit against the same capability matrix. If `lnk` meets normalization and maintenance needs, extend it with browser transport and local storage. If its internals need substantial replacement, build a small independent client using the endpoint knowledge, rather than carrying a large fork. Do not make a browser extension mandatory for the first prototype: CDP is already available here.

## Recommended agent-friendly CLI

These commands are a proposed interface, not commands implemented by this research folder.

```bash
linkedin auth status --verify --cdp http://localhost:9222
linkedin doctor --capability search.people
linkedin schema search.people
linkedin capabilities --output json

linkedin search people --query "data science" --limit 10 \
  --fields id,name,headline,url --output json
linkedin search posts --query "artificial intelligence" --limit 10
linkedin profile get https://www.linkedin.com/in/USERNAME/ --sections basics,experience
linkedin activity list USERNAME --kind posts --limit 20
linkedin activity list USERNAME --kind comments --limit 20
linkedin activity list USERNAME --kind reactions --limit 20
linkedin feed list --limit 20 --max-pages 2

linkedin sync feed --db linkedin.sqlite --max-pages 2
linkedin sync activity USERNAME --kind posts --db linkedin.sqlite --max-items 100
linkedin sync status --db linkedin.sqlite
linkedin local search "agents" --db linkedin.sqlite --output ndjson
linkedin export posts --db linkedin.sqlite --since 2026-11-01 --output ndjson
```

### Implementation and transport

For the user's existing `uv` workflows, Python with Typer, `httpx`, `websockets` and standard-library `sqlite3` is a reasonable small stack. The included Node probes demonstrate that Playwright is not required for CDP capture/replay. A Go implementation is attractive if extending `lnk`; language choice is less important than decoder correctness and endpoint maintenance.

Keep four separable pieces:

```text
commands / schema / output
          |
operation manifest + Voyager and SDUI decoders
          |
background CDP transport [first] | direct HTTP [optional, separately validated]
          |
normalized SQLite observations + resumable collection state
```

Use one serialized request queue per account. Default to API fetches inside a LinkedIn page: this reuses cookie renewal and the browser networking stack without handling passwords or writing session tokens. A dedicated background tab can support captures and layout-dependent fallbacks. Create it with `background: true`, never activate it, and close only tabs owned by the CLI. Focus emulation was useful for processing scroll/layout without bringing a window forward.

For unattended operation, initially run beside a persistent, manually authenticated browser reachable only on loopback. A later HTTP backend can bootstrap cookies in memory from that browser or accept an explicitly configured credential provider/keyring. Browser availability is still required by that bootstrap; calling it fully browser-free would overstate the evidence. Expired login or a challenge should produce an actionable error and require the user to complete the browser login.

Use a versioned local operation manifest containing method/path, query ID or SDUI action, variable schema, decoration, expected root, decoder version, capture date, client version and verification level. If an ID fails, recapture the exact feature from current browser traffic; JavaScript-bundle IDs are discovery candidates requiring validation. Never silently change a semantic operation to whichever older endpoint happens to return 200.

### Output contract and bounded execution

Default to JSON for non-TTY output; offer a human table on TTY and NDJSON for streams. Keep progress on stderr. Accept structured input via `--params` or stdin, expose machine-readable command schemas, reject unknown fields and invalid URN namespaces, and support field masks.

For list output, use a stable envelope such as this synthetic example:

```json
{
  "ok": true,
  "schema_version": 1,
  "data": [],
  "page": {"next_cursor": null, "has_more": false},
  "coverage": {"complete": false, "reason": "item_limit"},
  "meta": {
    "source": "voyager",
    "operation": "activity.posts",
    "observed_at": "2026-11-08T13:00:00Z",
    "decoder_version": 1
  },
  "warnings": []
}
```

`data` is empty here only to keep the example free of personal content. In the real contract, `has_more: false` means no continuation was supplied for that traversal, while coverage describes the larger collection's limits. Neither establishes a complete LinkedIn archive.

Make cursors opaque and versioned, bound to account, operation, query/filter fingerprint, transport, offset/token and expiry. Do not put session cookies in them. Keep sensitive SDUI continuation state locally and return a handle where possible. `--limit` is a total-record budget; `--page-size`, `--max-pages` and `--timeout` bound request cost. Never fetch every page by default.

For NDJSON, emit typed record lines and a final page/coverage line. On interruption or a later-page failure, return nonzero, identify the checkpoint and mark the run partial. Avoid reporting success with an empty array when decoding failed or a capability is unavailable.

Use stable errors such as `AUTH_REQUIRED`, `CHALLENGE_REQUIRED`, `FORBIDDEN`, `RATE_LIMITED`, `CURSOR_EXPIRED`, `ENDPOINT_CHANGED`, `SCHEMA_CHANGED` and `UNSUPPORTED`, with `retryable`, optional `retry_after` and a concrete next step. Distinguish an inaccessible individual profile from a failed session using a bounded identity check. For HTTP 200, validate response roots and required references too.

### Local sync model

Start with the following SQLite tables, keyed by account wherever appropriate:

| Table | Purpose |
|---|---|
| `entities(account_id, urn, kind, normalized_json, content_hash, first_seen_at, last_seen_at, changed_at)` | Latest decoded profile/post/comment/reaction representation. |
| `observations(run_id, collection_id, entity_urn, position, observed_at, relation_json)` | Ordered membership and context: ranked feed placement, repost actor, activity kind and target. |
| `sync_state(account_id, collection_id, query_hash, cursor_json, decoder_version, last_success_at)` | Resume state per query and collection; never mix filters or accounts. |
| `runs(id, started_at, finished_at, status, requests, records, stop_reason, coverage_json)` | Auditability and honest partial-coverage reporting. |
| FTS5 index over selected normalized text | Fast offline search across collected material. |

Upsert entities, observations and the next checkpoint **in one transaction per page**. Resume by re-reading the last committed cursor. Deduplicate by stable URN plus relation identity, not by display name or text. Keep repeated feed placements separate from the canonical post; do not lose a resharing actor by merging solely on the original post ID.

Record source timestamps where supplied and `observed_at` independently. Do not derive an asserted publication time from relative UI text or an inferred ID timestamp. A missing field means unknown, not deleted. Removal from a ranked feed or a search page is not evidence of deletion.

For periodic refresh, restart near the head with bounded overlap and merge changes. Use high-water marks only on collections with verified ordering; ranked feeds/search do not qualify. Resuming a feed token continues a session traversal, while a new poll starts a new observation of the ranked feed. Record the difference.

Store only what is needed, with owner-only access and account separation. Raw response capture should be opt-in, local and redacted before sharing; session headers never belong in fixtures. Snapshot/change history can be added when a demonstrated use requires it. Support `--offline` so agents can inspect existing data without triggering network requests.

### Maintenance and acceptance criteria

Before calling a capability production-ready:

- Test anonymized fixtures with multiple referenced profiles, root-order preservation, reshares, missing references and missing/empty fields.
- Test actual next-page behavior, repeated/expired cursors, duplicate observations, interruption recovery and a transaction failure before checkpoint commit.
- Validate comments/reactions against UI examples so activity actors are not confused with post authors.
- Decode SDUI text and references across chunk boundaries, escaped strings and template changes; verify an actual continuation chain and declared completeness.
- Verify browser and HTTP transports separately for every enabled operation. An explicit DOM fallback must report its source and any truncated fields.
- Perform a bounded live smoke check after manifest changes. Preserve sanitized fixtures from the same client version.

No safe request quota was established. Use one in-flight request, explicit budgets, caching and backoff respecting `Retry-After`; stop on challenges or restrictions instead of trying alternate accounts, networks or endpoint variants to evade them.

## Practical limitations

LinkedIn's current User Agreement expressly restricts automated scraping/copying, reverse engineering and bypassing access/use limits; it also reserves account-restriction rights. Successful authenticated access is technical evidence, not LinkedIn authorization. Browser-backed operation does not remove this deployment concern. [User Agreement, sections 3.4 and 8.2](https://www.linkedin.com/legal/user-agreement).

The proposed client can collect only data this account can access. Search caps, subscription features, profile visibility, deleted content and finite activity histories remain boundaries. A personal ranked feed is an observed recommendation list, not a guaranteed stream of all posts from connections. Polling can miss material between runs; neither deduplication nor a stored cursor fixes that gap.

No posting, messaging, connection requests, reactions, automated login, challenge handling, full backfill, scheduling or production sync was implemented or validated. Add account-changing commands only as a separate later phase with explicit destinations, previews, `--dry-run` and deliberate execution semantics.

## Reproduce the research probes

Requires a recent Node runtime with built-in `fetch` and `WebSocket`, and the signed-in browser exposed on loopback CDP. This session used Node 26.11.1. No npm dependencies are required.

```bash
node probe.mjs --describe
node probe.mjs --surface me
node probe.mjs --surface profile
node probe.mjs --surface people --limit 5 --start 0
node probe.mjs --surface people --limit 5 --start 5
node probe.mjs --surface content --limit 5
node probe.mjs --surface posts --limit 5
node probe.mjs --surface comments --limit 5
node probe.mjs --surface reactions --limit 5
node probe.mjs --surface home
node http-probe.mjs
node --test test-probe.mjs
```

`probe.mjs` outputs structural summaries only. Its activity offset option is a shape probe, not a complete token-aware activity paginator. `--surface home` creates one background tab, captures a main-feed pagination request and replays that read-only POST once, then closes the tab. It may cause additional requests through ordinary page behavior. `http-probe.mjs` temporarily reads two session cookies through CDP for one direct identity GET, without saving them. Keep CDP loopback-only because it grants control of the authenticated browser.

The supplied scripts validate transport and output privacy; they do not implement the proposed normalized CLI or the SDUI decoder. See [notes.md](notes.md) for the investigation log and [README.md](README.md) for the file inventory.

## 9 November 2026: human filters, scheduled posts and partial connections

- The current filter UI calls `FiltersLocationTypeaheadRequest` and `FiltersCompanyTypeaheadRequest` under `/flagship-web/rsc-action/actions/server-request`. Replaying their captured state/payload shape with synthetic component/binding keys succeeded using only the browser session, CSRF, JSON content type and `x-li-rsc-stream`. Raw headers/cookies are not persisted. All returned matching suggestions/aliases are combined with OR; different facets remain AND. Suggestion lists are bounded (the tested queries returned 2–10 items), not exhaustive catalogs.
- These are React Flight data streams. CDP response bodies can be base64-encoded. Checkbox components carry a scoped `FILTER_ITEM_<facet>_<id>_CHECKED` binding alongside the label; decoding each component avoids cross-associating unrelated labels/IDs.
- Scheduled posts are exposed by `com.linkedin.sdui.generated.sharing.dsl.impl.scheduledPostsList`, with actor Self, plus `scheduledPostFullRow` for each returned `feedUpdateUrn` / `scheduledAtEpochMillis`. The list returned three items in the live check. Exact scheduled times and full text were decoded without scheduling, editing or publishing anything. Generic component/server-request POSTs remain disallowed; only the two typeahead requests and two scheduled read components are registered.
- Full scheduled rows contain UTF-8 length-prefixed text, data references, commentary components and large callback/tracking payloads. The decoder reads commentary through references and never executes or exports action payloads. It preserves literal dollar signs and multiline Unicode text. Debug captures remain private/ignored.
- The connections failure was not a new endpoint shape: one legitimate Connection in the first ten results had `connectedMember` but omitted its resolved Profile. Other returned connections resolved normally. The decoder now retains that member identity/date with an unavailable flag and warning; malformed identities still fail. A bounded two-page live read returned 20 records successfully.
