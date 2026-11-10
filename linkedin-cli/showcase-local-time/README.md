# Local post dates and Claude showcase activity

Markdown post publication dates now use the computer’s local timezone, and activity-ID-derived dates no longer display “(from activity ID)”. On this machine, `2026-11-09T20:30:00Z` displays as `10 Nov 2026, 04:30 GMT+8`. `TZ` can select another timezone. Date-only/month-only observations retain their precision; JSON timestamps and provenance remain unchanged. Other timestamp displays retain UTC.

To read Anthropic’s Claude showcase posts reliably:

```bash
linkedin activity showcase:claude
# Equivalent explicit URL:
linkedin activity https://www.linkedin.com/showcase/claude/
```

Bare `linkedin activity claude` continues to select **Claude Schitter**, the real member at `/in/claude/`, under the user-confirmed profile-first rule. Explicit showcase targets bypass the member lookup. `/home`, `/posts` and other showcase URL suffixes are accepted.

Showcase pages use LinkedIn’s company entity namespace. The existing organization decoder resolves Claude to `urn:li:fsd_company:106863934`; native Posts search uses that ID in `fromOrganization`. No brand-specific alias, extra endpoint or dependency is needed. This returns authored posts exposed by native organization search, rather than claiming to reproduce every item (including reposts) from the showcase timeline.

Verification: **105 research tests passed** (103 standalone plus two probes), including local date rollover, New York summer/winter DST offsets, date-only precision, JSON stability, explicit-target validation, profile precedence and offline behavior. Both live showcase forms returned the same three Claude post IDs; all three matched the independently rendered showcase page. See [live aggregate checks](live-checks.json), [reusable verifier](verify-live.mjs) and [notes](notes.md).

Installed verification: **103 standalone tests passed**; runtime/tests match the research copies byte for byte. The installed showcase command returned three Claude-authored posts, and its offline Markdown used `GMT+8` with no activity-ID suffix. [Incremental implementation diff](changes.patch).
