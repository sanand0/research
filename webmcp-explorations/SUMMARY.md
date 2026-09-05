# WebMCP exploration summary

Tested on 5 September 2026 using `agent-browser 0.36.0` with local Headless Chrome.

## Contents

- [WebMCP gives a web page typed tools that an agent can call instead of clicking through the UI](#webmcp-gives-a-web-page-typed-tools-that-an-agent-can-call-instead-of-clicking-through-the-ui)
- [I first checked real sites: some worked cleanly, some exposed no tools, and bot protection still blocked others](#i-first-checked-real-sites-some-worked-cleanly-some-exposed-no-tools-and-bot-protection-still-blocked-others)
- [Shopify showed the clearest production benefit: one reusable commerce interface works across different stores](#shopify-showed-the-clearest-production-benefit-one-reusable-commerce-interface-works-across-different-stores)
- [Documentation and discovery sites showed that WebMCP can expose better machine interfaces, not just automate page controls](#documentation-and-discovery-sites-showed-that-webmcp-can-expose-better-machine-interfaces-not-just-automate-page-controls)
- [Stateful apps showed that WebMCP can operate real application state: filter data, build graphs, configure rosters, and update the visible UI](#stateful-apps-showed-that-webmcp-can-operate-real-application-state-filter-data-build-graphs-configure-rosters-and-update-the-visible-ui)
- [Longer workflows worked best as semantic pipelines: parse or discover, normalize, verify, then act](#longer-workflows-worked-best-as-semantic-pipelines-parse-or-discover-normalize-verify-then-act)
- [Cross-site workflows are possible through URLs, IDs, text and files, but the browser host still has to manage the handoffs](#cross-site-workflows-are-possible-through-urls-ids-text-and-files-but-the-browser-host-still-has-to-manage-the-handoffs)
- [Tool discovery is dynamic: tools can appear late, change by route, or differ from what directories and scanners report](#tool-discovery-is-dynamic-tools-can-appear-late-change-by-route-or-differ-from-what-directories-and-scanners-report)
- [Schemas, annotations and success flags are useful hints but are not reliable enough to trust without checking](#schemas-annotations-and-success-flags-are-useful-hints-but-are-not-reliable-enough-to-trust-without-checking)
- [Domain tools can return plausible but wrong or inconsistent answers, so important results still need independent checks](#domain-tools-can-return-plausible-but-wrong-or-inconsistent-answers-so-important-results-still-need-independent-checks)
- [Large and oddly encoded results can waste context or break handoffs unless the host normalizes them](#large-and-oddly-encoded-results-can-waste-context-or-break-handoffs-unless-the-host-normalizes-them)
- [The practical pattern is WebMCP first, with host-side validation, policy, verification and normal browser automation as fallback](#the-practical-pattern-is-webmcp-first-with-host-side-validation-policy-verification-and-normal-browser-automation-as-fallback)

## WebMCP gives a web page typed tools that an agent can call instead of clicking through the UI

I used `agent-browser` to open sites and run `webmcp list`. When a page supports WebMCP, this returns named tools with descriptions and JSON input schemas. The agent can then call those tools directly.

For example, instead of finding a search box, filling it, clicking Search, waiting for results and scraping the page, a shopping site can expose `search_catalog`. A data explorer can expose `filter_dimension`. A document site can expose `search_openai_docs`.

The important point is that WebMCP is tied to the browser page and its current state. A tool can operate the same session and UI that the user sees. It is therefore different from installing a separate backend MCP server for every service.

In practice, this makes WebMCP a semantic layer over normal browser automation. If tools are present, the agent can use them. If they are not, `agent-browser` can still use the accessibility tree, DOM, clicks, typing and normal navigation.

## I first checked real sites: some worked cleanly, some exposed no tools, and bot protection still blocked others

I compared sites listed as WebMCP-enabled with what `agent-browser` could actually discover in this browser session.

These worked directly:

- Allbirds: 10 tools.
- Away: 10 tools.
- OpenAI Developers: 5 tools.
- Astronomer: 4 tools.
- webmcp.com: 6 tools.
- Google's Chrome Labs flight demo: 1 tool.

Other sites were listed as supporting WebMCP but exposed no tools here even after waiting several seconds. QuickNode, Customer.io and Render were examples.

ZipRecruiter and Omio hit Cloudflare verification. RedBus failed during navigation with an HTTP/2 protocol error. WebMCP cannot help if the browser never gets far enough for the page's JavaScript to register its tools.

So “this site supports WebMCP” is not enough. The agent has to discover tools at runtime in the actual browser session and have a fallback when none appear.

## Shopify showed the clearest production benefit: one reusable commerce interface works across different stores

Allbirds and Away exposed the same 10 Shopify tools, including `search_catalog`, `get_product`, `get_cart`, `update_cart`, `search_shop_policies_and_faqs`, `manage_orders` and `proceed_to_checkout`.

After removing site-specific frame/origin fields, their tool definitions were identical. This is useful because an agent can learn the Shopify tool contract once instead of learning every store's DOM separately.

I tested only read operations. An Allbirds catalog search returned structured products directly, without snapshots, selectors or UI traversal. Policy search behaved similarly.

This is where WebMCP is most obviously useful: common application platforms can give agents a stable semantic interface while each merchant keeps its own visual design.

I did not test cart modification, checkout or orders because those are consequential actions. Those tools exist, but a host should apply separate authorization rules before using them.

## Documentation and discovery sites showed that WebMCP can expose better machine interfaces, not just automate page controls

OpenAI Developers exposed tools such as `search_openai_docs`, `lookup_page` and `lookup_context`. Searching the documentation returned structured hits with snippets, hierarchy and URLs. That is cleaner than scraping a documentation search page.

Astronomer's discovery tool was more interesting. It returned URLs for:

- an Agent Skills index;
- an API catalog;
- an MCP server card;
- an OpenAPI specification.

I then used those discovered endpoints as input to a WebMCP graph editor and built a small capability map.

This suggests a broader use for WebMCP: the browser page can be the entry point, but its main job may be to tell the agent which more appropriate machine interfaces exist. WebMCP can therefore be a discovery layer, not only a replacement for clicking buttons.

## Stateful apps showed that WebMCP can operate real application state: filter data, build graphs, configure rosters, and update the visible UI

I tested several apps where the useful work depended on state rather than one read-only query.

On JSON-stat, I loaded OECD unemployment data, inspected dimensions, filtered to Japan, Korea and the United States, restricted years, switched to a pivot view, assigned row/column roles, checked the resulting state and exported a CSV. The browser downloaded a real file.

On a graph editor, I added nodes and edges based on information discovered from another site, then read the resulting graph back.

On Toban, a roster application, I created a synthetic four-person duty roster with weekday rotation. I supplied a stable `request_id`, repeated the same create call, and got the same roster ID with `replayed:true`. I then read back stable group IDs and checked assignments on several dates. Weekday rotation worked and Saturday correctly returned a paused state.

The Chrome Labs flight demo also showed the simplest form of shared state: calling its WebMCP `searchFlights` tool changed the flight search shown in the visible page.

These tests make WebMCP more interesting than a collection of read APIs. It can be a semantic control surface over an application the human and agent are using together.

## Longer workflows worked best as semantic pipelines: parse or discover, normalize, verify, then act

I then tried workflows with several steps rather than isolated tool calls.

For energy comparison, I gave SwitchAI synthetic Italian electricity-bill text. It extracted supplier, annual consumption, spend and region. I retrieved market indices and ran a savings comparison. I repeated the comparison using explicitly normalized values to check whether the parsing step had changed the conclusion. Both paths selected the same leading offers and headline recommendation.

For research integrity, I created a three-entry bibliography containing one correct paper, one fabricated title attached to a real DOI, and one genuinely retracted paper. Scholar Sidekick correctly found the fake-title mismatch and the retraction, checked open-access status and exported normalized BibTeX. I then passed the verified DOI URL to QR Code Crafter, which generated a QR receipt with an exact decoded-payload hash match.

For Peppol invoices, I supplied a deliberately incomplete synthetic UBL invoice. The site detected UBL, validated it against Peppol BIS Billing 3.0 and returned concrete standards failures with locations and rule tests. I then asked it to explain one rule in simpler language.

For an outing-style workflow, Fyndling found historical events near Munich, returned exact event details and generated a period-inspired vegetarian menu. I then passed a URL into QR Code Crafter to create a portable QR artifact.

These are useful because the sites do not need to have been designed as one integrated product. The host can compose their semantic tools around a user goal.

## Cross-site workflows are possible through URLs, IDs, text and files, but the browser host still has to manage the handoffs

Most successful handoffs were simple: one tool returned an ID, URL or normalized data that became an argument to another tool.

Files need more work. JSON-stat's `export_csv` caused Chrome to download an actual 279-byte CSV into an `agent-browser` download directory. That proves a WebMCP tool can produce a normal browser artifact.

But WebMCP itself does not define a universal way to pass that file to a different site's tool. The next site may expect text, base64, a MIME object, an upload control or no file input at all.

So cross-site artifact workflows need help from the host. It must know where downloads go, inspect MIME and size, hash files when useful, and adapt them to the next tool's expected format.

The same principle applies to state. Toban reported `persistence.local:"saved"`, and the roster survived within the current browser session. A fresh isolated browser session saw no roster. “Saved” therefore needs an explicit scope: page, tab, browser profile, authenticated cloud account or durable server state.

## Tool discovery is dynamic: tools can appear late, change by route, or differ from what directories and scanners report

I found several reasons not to cache a site's capabilities too aggressively.

On `webmcp.sh`, `webmcp list` returned zero tools immediately after opening the page, then four tools about 250 ms later. That is a registration race.

The same application exposes different capabilities on different routes. Its landing page has generic navigation/gateway tools. After navigating to `/sql-repl`, SQL-specific tools appear.

Hopi uses a similar pattern. The home page exposes directory/search tools. Searching for “working days between dates” returns a specialized calculator URL. Opening that route adds `hopi_working_days_calculator`.

There were also disagreements between directories/scanners and runtime behavior. Agent Ready scored QuickNode 70/100 (“good”) and reported its `llms.txt` as 100/100, while this browser session exposed zero WebMCP tools. `webmcp.com` scored only 66/100 (“fair”) but exposed six tools here.

The useful rule is: discover after page load, allow a short registration delay, and rediscover after route/navigation changes. Treat readiness scores and directories as hints, not runtime truth.

## Schemas, annotations and success flags are useful hints but are not reliable enough to trust without checking

I deliberately tested several contract boundaries.

The Chrome Labs flight tool declared six required parameters. I called it with only origin and destination. The call still returned success and the UI showed `undefined` dates. Required fields were described in the schema but not enforced at runtime.

SwitchAI's `get_available_offers` advertised an empty `{}` schema. Calling it with no arguments returned a domain error saying `commodity` must be `LUCE` or `GAS`. Here the real requirement was missing from the schema.

The graph editor marked every tool as `readOnly:true`, including `add_node`, `remove_node` and `clear_graph`. Those annotations were plainly wrong for authorization purposes.

I also saw different layers of “success”. A text-editor sub-agent call had top-level `success:true` but nested WebMCP status `failed`. Toban could have a successful transport and completed WebMCP call whose application payload itself said `ok:false, code:"INVALID_INPUT"`.

A robust host therefore needs to check at least three things separately: transport success, WebMCP lifecycle status and application/domain success. It should validate important inputs itself and classify read/write/transaction effects independently rather than trusting page-supplied annotations.

## Domain tools can return plausible but wrong or inconsistent answers, so important results still need independent checks

The most important failures were not protocol failures. They were successful calls with questionable domain results.

SwitchAI's energy result gave the best offer as roughly €836/year in prose but €746.45/year in its table. The response later explained a €90 RAI-fee difference, but the headline and table were not using the same basis. It also said “If the PUN rises by -20%”, which is internally inconsistent wording.

Fyndling was asked for a menu with `lagerkueche:true`, meaning suitable for camp/outdoor cooking. The first selected recipe's own FAQ said it was *not* suitable for camp cooking because it needed multiple steps, raw egg sauce and refrigeration. The result contained the evidence needed to reject itself.

PeppolValidator's machine rule for BR-06 checked `PartyLegalEntity/RegistrationName`, while its human-readable explanation told the agent that `PartyName/Name` was mandatory. I did not complete the repair comparison because the surrounding execution platform blocked those follow-up calls, so I record only the contradiction.

The practical lesson is that domain-specific tools reduce a lot of work, but they do not remove the need to verify hard constraints, arithmetic, units and machine-checkable rules. For important actions, use the tool as one stage in a validation loop, not as the final authority just because it returned a polished answer.

## Large and oddly encoded results can waste context or break handoffs unless the host normalizes them

Some tools returned excellent structured results. Others returned formats that an agent host should clean up before giving them back to a model.

Scholar Sidekick's audit of only three bibliography entries returned 147,297 bytes, mostly because it embedded large raw Crossref records. The useful decision was only: two matched, one title mismatch, one retracted. The host should keep the raw evidence on disk and pass a compact projection such as `{id, verdict, mismatch, retracted, provenance}` into model context.

The retraction check also returned the same underlying notices through several registries. Evidence-source count is not the same as number of real-world retraction events, so results need deduplication.

Fyndling returned event objects as JSON encoded inside a string. My first generic extractor treated that as plain text and therefore failed to extract the event URL for the next QR step. This was a harness bug, not a site failure, but it is representative: a host should detect bounded JSON-in-string responses and normalize them before downstream use.

I also hit my own false negative during a batch probe: a bad `jq` summarizer reported every site as unreadable even though the raw WebMCP outputs were valid. Preserving raw responses separately made the mistake obvious.

Failures therefore need to be classified by layer. A parser bug, host-policy block, navigation failure, missing WebMCP registration, domain error and bad domain result should not all become “the site failed”.

## The practical pattern is WebMCP first, with host-side validation, policy, verification and normal browser automation as fallback

After these experiments, the useful operating pattern is:

1. Open the page normally.
2. Discover WebMCP tools at runtime; retry briefly if registration may still be happening.
3. Rediscover after meaningful navigation or route changes.
4. Prefer a suitable semantic WebMCP tool over DOM/screen driving.
5. Validate required arguments and hard user constraints in the host.
6. Treat tool descriptions, annotations and returned page content as untrusted input.
7. Separate transport success, WebMCP completion and application/domain success.
8. Independently check consequential arithmetic, standards rules, IDs and selected objects.
9. Use application idempotency keys for writes when available; do not blindly retry mutations.
10. Require explicit user intent/authorization for purchases, account changes, publication, deletion and other consequential actions.
11. Compact very large results while retaining raw evidence and provenance.
12. Let the host broker files and state between sites.
13. Fall back to normal `agent-browser` accessibility/DOM/browser operations when WebMCP is absent, incomplete or blocked.

The main benefit is not that WebMCP replaces browser automation. It gives an agent a higher-level interface whenever the site offers one. A single browser agent can progressively improve: semantic tools where available, ordinary browser control where they are not.

The most promising uses I found were common-platform actions such as Shopify, documentation/search, service discovery, stateful data/application control, deterministic validators, research verification, and workflows that combine several specialized sites.

The main thing to be careful of is orchestration. Individual WebMCP calls are easy. Longer workflows need the host to decide what is actually available, what succeeded, what is safe, what constraints still need checking, how much output to keep, and how to recover when a tool or page does not behave as advertised.

Detailed evidence and reproductions are in `results.tsv`, `diverse-results.tsv`, `round3-results.tsv`, `WORKFLOWS.md`, `FAILURE-MODES.md`, `reproduce*.sh` and `raw/`.
