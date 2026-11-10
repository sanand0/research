# LinkedIn activity and post output update

Updated the standalone `linkedin` CLI to render compact post headers, preserve originals in commented reposts, correctly identify missing text, and read profiles/companies through native actor lists. No dependencies were added.

```bash
linkedin post https://www.linkedin.com/feed/update/urn:li:activity:7525629644318879744/ --refresh
linkedin activity sanand0
linkedin activity sanand0 ramar --limit 20
linkedin activity openai
linkedin activity https://www.linkedin.com/company/openai/home
```

## What changed

- Post headings are followed immediately by the Published/Author line and the bare post URL on line three. A Markdown hard break keeps metadata and URL separate when rendered. Removed redundant `Profile:` and `Post:` labels in posts; attachment links and complete bodies remain.
- Decode normalized `*resharedUpdate`, direct legacy originals and wrapped `*update` originals, with cycle protection. Embedded originals get their correct activity ID, URL, author and contents. Feed cards containing embedded commentary receive a post API read; successful reads clear old truncation flags.
- Ignore decorative `aria-hidden` more controls and expanded/collapse controls when determining truncation. Genuine unexpanded controls still trigger hydration and retain the warning when complete text cannot be fetched. Media-only post responses no longer require commentary.
- Activity tries a bare username as a profile first, then an exact company slug, then personalized people name search. Explicit URLs/URNs retain their type. Company URLs may include `/home`, `/posts`, query strings, etc.; numeric company URLs/URNs also work. A valid profile identity wins ambiguity.
- Multiple member IDs use one native `fromMember` Posts search; companies use `fromOrganization`. Both request `date_posted` and omit keywords, because an empty keywords string causes HTTP 400. This is the API counterpart of the [native lists workflow](https://www.linkedin.com/pulse/how-take-advantage-linkedins-secret-lists-feature-mickey-mellen-munfe/). Returned posts sort before output limiting, and offline reads use publication order. Actors are deduplicated and canonically ordered for equivalent cache keys; resolved actors appear in Markdown/JSON.
- Fixed the package executable mapping (`linkedin.mjs` did not exist), undersized fresh paginated caches, stale collection membership after refresh, and a CDP cleanup race where the next invocation could borrow a tab that was still closing. Refresh removes old membership, preserving historical canonical records for search/export. Cleanup waits until owned targets disappear from browser discovery.

## Why the four complete posts were flagged

The feed decoder used `Boolean(content.querySelector('button'))`. Current SDUI retains an `aria-hidden="true"` “… more” button even when the DOM already contains the full text. A control's existence therefore did not establish missing text. Cached warnings could also survive later complete API observations because those observations never explicitly set `textTruncated:false`.

Independently fetched post API commentary and rendered post-page DOM text match exactly for all four supplied examples:

| Activity ID | API characters | DOM characters | Corrected warning |
| --- | ---: | ---: | --- |
| 7525629644318879744 | 1,550 | 1,550 | None |
| 7525540464230461440 | 447 | 447 | None |
| 7525680542780944385 | 468 | 468 | None |
| 7525498889613877249 | 1,199 | 1,199 | None |

Use `--refresh` to replace observations already saved by the old decoder; deployment does not rewrite every historical cached record.

## Verification

- `just test`: **103 passed**, including **101 native standalone tests** and two original research probe tests. Regression cases cover exact Markdown line order, all reshare representations/cycles, hidden/visible expansion controls, actual feed hydration, media-only response acceptance, input/type/error boundaries, profile precedence, company decoding, multiple actors, sorting before limiting, offline reuse, larger cache reads, membership replacement and delayed tab disappearance.
- `node activity-posts-update/verify-live.mjs`: four independent API/DOM comparisons, a real commented repost matched to a separately fetched original, six activity forms (username, member list, company slug, company URL, company URN, quoted name), latest-first output, offline/live ID parity, and consecutive source-tab cleanup checks. [Aggregate results](live-checks.json) contain no credentials or raw personal response bodies.
- The real repost checked was `7521206725807419393`: 680 characters of commentary plus its independently matched 278-character original, `7521186532800708609`.
- The native multi-member query returned posts by both Anand S and Rama Ramakrishnan. OpenAI slug, URL and company URN resolved to company `11130470` and returned OpenAI posts.
- Installed `just test-linkedin-api`: **101 passed**. Installed runtime/tests are byte-identical to the research copies; installed native list output includes both requested authors, and the installed Markdown repost includes the original. The scoped installation diff is saved as [scripts.patch](scripts.patch).
- Node syntax checks and `git diff --check` pass. Tests use an isolated headless Chromium profile; only the explicit live verifier uses the authenticated browser.

## Review items left unchanged

1. **Name matching can choose the wrong person.** The established policy uses the first personalized people result. In the live check, “Rama Ramakrishnan” selected Ramakrishnan Venkataramanan; `ramar` selected the intended Rama Ramakrishnan. Changing name ranking needs a policy choice: exact/strong name matching, interactive disambiguation, or retaining first-result behavior. Resolved actors make this visible.
2. **Native author search is a bounded indexed view.** Visibility, search indexing, and page/item budgets constrain coverage; it is not an exhaustive replica of member timelines. Mixed member/company pages were not reliably publication-sorted by the server in the probe, so returned records are explicitly sorted. This cannot prove that the newest posts globally were all indexed/returned. A single member retains its profile activity endpoint.
3. **Comments and reactions remain a single-profile view.** Detailed attribution is still incomplete, as the existing warnings state. Companies and multiple actors explicitly accept posts only rather than fabricate attribution or silently merge incompatible activity categories.
4. **Historical cache flags need a refresh.** The implementation repairs newly read observations. It does not bulk revisit private cache history or infer that every previously truncated observation was complete.
5. **Two standalone source/test copies remain.** Research and `~/code/scripts` intentionally preserve independently executable copies. A future install/check recipe could reduce synchronization drift; deleting one would change the established distribution contract.
6. **Legacy Python tools and research probes remain.** The earlier profile CLI and archived backup tools may have callers outside this folder. No usage audit justifies deleting them; current probes still have passing tests. The current runtime itself has no npm dependencies to remove.
7. **Voyager identifiers and SDUI structures remain unofficial and version-sensitive.** Automatic endpoint discovery or stream decoding would be a separate reliability project. Current failures stay explicit, and authentication/rate/schema errors do not silently broaden an actor lookup.

See [working notes](notes.md) and [live verifier](verify-live.mjs) for the investigation trail.
