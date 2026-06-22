# Missing rules audit v1

Audit date: 2026-06-01

## Summary

The first build of `rules.csv` was useful but incomplete. It had 80 rows and covered recent approved summaries plus some historical seed rows. Red-team checks against the NFL Operations sitemap, the 2025 online rulebook, special update articles, and the 2022 rulebook PDF surfaced several missing classes of rule changes.

After patching, `rules.csv` now has 107 rows. The added coverage is:

- 2022 official rulebook change list: 2 rows
- 2023 official proposal page: 17 rows
- 2023 special adopted fair-catch rule proposal: 1 row
- 2023 special Resolution G-1 for AFC playoff inequity after the cancelled Bills-Bengals game: 1 row
- 2025 online rulebook detailed change list: 6 rows

## Missing class 1: official 2023 proposed rule changes

Status before patch: missing.

Evidence: the NFL Operations sitemap includes `https://operations.nfl.com/updates/the-rules/2023-rules-change-proposals/`. The prior script had the approved 2023 page but not the proposal page.

Why this matters: proposal rows are analytically useful even when rejected. They let us study governance, proposer behavior, rejected ideas, recurrence, and eventual adoption.

Resolution: added source `nflops_proposals_2023`. The generic HTML parser now captures 17 proposed playing-rule rows.

Remaining caveat: the 2023 proposal numbering is ambiguous because the official page has two separate groups: Competition Committee proposals and club proposals. Both groups restart numbering. The current script preserves source order and proposer, but the `proposal_number` alone is not globally unique within the page. `rule_id` remains unique.

## Missing class 2: special 2023 fair-catch adoption article

Status before patch: missing.

Evidence: the NFL Operations sitemap includes `https://operations.nfl.com/updates/the-rules/adopted-playing-rules-change-proposal-putting-ball-in-play-after-fair-catch/`. This is an adopted playing-rule proposal from the Spring League Meeting, not part of the original March approved-page extraction.

Rule captured: 2023 Playing Rule Proposal No. 16A, for one year only, putting the ball in play at the receiving team's 25-yard line after a fair catch on a free kick behind the receiving team's 25-yard line. Stated reason: player safety.

Resolution: added source `nflops_adopted_2023_fair_catch` and a special article parser. Added 1 approved playing-rule row.

## Missing class 3: special 2023 Resolution G-1 after cancelled Bills-Bengals game

Status before patch: missing.

Evidence: the NFL Operations sitemap includes `https://operations.nfl.com/updates/football-ops/2023-resolution-g-1-approved-at-special-league-meeting/`.

Rule/resolution captured: 2023 Resolution G-1, approved for the 2022 season only, addressing possible AFC playoff competitive inequity after the Bills-Bengals game was suspended, postponed, then cancelled.

Resolution: added source `nflops_resolution_2023_g1_special` and a special resolution parser. Added 1 approved resolution row, with `season=2022`, `year=2022`, `status=approved`.

## Missing class 4: 2025 detailed rulebook change list

Status before patch: partially missing.

Evidence: the current NFL rulebook page contains a `2025 Rule Changes` section with rule-section-article rows. The earlier script used only the approved summary article, which collapsed multiple kickoff changes under one summary row.

Rows now captured from the rulebook change list:

- Rule 6: makes permanent the new kickoff play implemented in 2024
- 6-1-3: modifies receiving-team setup-zone alignment requirements
- 6-1-5: changes the dead-ball spot after specified touchbacks
- 6-1-6: modifies onside-kick alignment and permits declared onside kicks while trailing
- 15-9: expands Instant Replay assist
- 16-1-3: modifies regular-season overtime

Resolution: added source `nflops_rulebook_2025_changes` and a parser for the `2025 Rule Changes` section. Added 6 approved playing-rule rows.

Remaining caveat: these rows intentionally duplicate some substance from the 2025 approved summary, but at finer granularity. This is useful for downstream rulebook-ref-level analysis. Deduplication should be done analytically using `source_kind`, `source_key`, and `rulebook_ref`, not by removing these rows.

## Missing class 5: 2022 official rulebook change list

Status before patch: missing.

Evidence: the official 2022 rulebook PDF is available at `https://operations.nfl.com/media/5kvgzyss/2022-nfl-rulebook-final.pdf`. Page 3 has `2022 Rules Changes` with two rule-section rows.

Rows now captured:

- 6-1-3: makes permanent the free kick formation change implemented during the 2021 season
- 16-1-4: modifies postseason overtime to require each team to have an opportunity to possess the ball

Resolution: added source `nflops_rulebook_2022_changes` and a PDF rulebook-change parser. Added 2 approved playing-rule rows.

## Missing or still unresolved

### 1. 2024 detailed rulebook change list

I did not find an official 2024 rulebook PDF URL in the sitemap during this pass. The 2024 approved summary page is captured, but if a 2024 rulebook PDF has a finer `2024 Rules Changes` page, the current script does not yet capture it.

Likely impact: medium. The approved 2024 summary already captures six adopted playing-rule changes, but a rulebook list may split or normalize the exact rule-section-article references.

Suggested next action: discover the 2024 rulebook PDF URL via web search, archived NFL Ops pages, or link extraction from older cached rulebook pages.

### 2. 2021 and earlier official annual rulebook change lists

Only the 2022 rulebook PDF was discovered by URL probing. The script still lacks official annual change-list extraction for 2021 and earlier.

Likely impact: high for long-run analysis. The historical seed rows from NFL Ops and the Hall of Fame chronology are not complete annual rule-change records.

Suggested next action: locate PDFs for 2021, 2020, 2019, etc., then parse the early `Rules Changes` pages where available.

### 3. 2025 current-rulebook changes not explicitly listed in the change table

The 2025 rulebook text includes items like the “nose wipe” gesture under unsportsmanlike conduct, but the `2025 Rule Changes` table does not list it. I did not add it as a rule-change row because the available evidence from the official rulebook page alone proves current inclusion, not necessarily the year of change.

Suggested next action: compare 2024 vs 2025 rulebook text once the 2024 PDF is located. Add such rows only when a year-diff confirms they are new.

### 4. Operational changes that affect rules but are not playing rules

Examples include technology/measurement/officiating process changes. The script captures rulebook and proposal pages, not every operational update page. Some may be better modeled separately as `operations_change` rather than `playing_rule`.

Suggested next action: add a second dataset or item type for operational/officiating changes after defining inclusion criteria.

### 5. Historical completeness

The Pro Football Hall of Fame chronology parser is keyword-based and intentionally low-confidence. It is a seed generator, not an audited historical rule-change database.

Suggested next action: build a historical audit loop: extract all chronology candidates, manually accept/reject, add source spans, and reconcile with official NFL rulebook PDFs where available.

## Script changes made

- Added official sources for 2023 proposals, 2023 fair-catch adoption, 2023 Resolution G-1, 2025 online rulebook changes, and 2022 rulebook PDF changes.
- Added a special parser for the 2025 online rulebook `2025 Rule Changes` section.
- Added a special parser for the 2023 fair-catch adoption article.
- Added a special parser for 2023 Resolution G-1.
- Added a parser for the 2022 rulebook PDF change list.
- Fixed the `rule_ref()` regex so `Rule X, Section Y, Article Z` references are captured correctly.
- Expanded basic classification to recognize fair-catch rows as special-teams rows and violent-gesture/nose-wipe language as player-safety/conduct-adjacent rows if later added.

## Validation after patch

`uv run scripts/build_rules_csv.py --refresh` produced:

- 107 rows
- 22 columns
- 0 duplicate `rule_id`s
- 0 blank summaries

The generated outputs are:

- `rules.csv`
- `data/interim/rules.parquet`
- `data/interim/source_manifest.csv`
