# Processing errors audit v1

Audit date: 2026-06-01

Scope:

- `rules.csv`
- `scripts/build_rules_csv.py`
- `data/processed/manual_links.yaml`
- `scripts/build_analysis_tables.py`
- derived processed tables under `data/processed/`

## Executive summary

I found and fixed multiple extraction, classification, and curation errors. The most important issues were:

1. Non-NFL / pre-1920 football history was leaking into an NFL rule-change dataset.
2. Hall of Fame chronology rows were noisy: some rows were franchise/team-history events, not rule changes.
3. NFL Ops historical seed rows copied the page intro into `effect`, rather than the specific rule-change summary.
4. The classifier matched `onside` inside the word `considering`, causing 2026 officiating/disqualification proposals to be misclassified as kickoff/special-teams rows.
5. Kickoff rows that mentioned replay were being classified as officiating rather than special teams.
6. 2026 proposal PDF parsing leaked the following bylaw-summary text into proposal 5's `reason` field.
7. K-Ball / kicking-football rows were not consistently classified as kickoff / special-teams rows.
8. Detroit's 2024 approved third-challenge rule was not linked to the Detroit challenge-system canonical group.
9. Manual proposal-link output included selector matches that were not actually applied because earlier, more specific canonical links had precedence.
10. `pypdf` emitted noisy malformed-object warnings while parsing the 2022 rulebook PDF.
11. Substitution history rows were classified as generic gameplay instead of roster/substitution lineage.
12. 2026 approved proposal `(A)` was parsed as `(A)` instead of `4-A`.

After fixes:

- `rules.csv`: 102 rows
- `rule_events.csv`: 102 rows
- `rule_changes.csv`: 61 rows
- `rule_lineages.csv`: 22 rows
- `rule_proposal_links.csv`: 53 rows
- validation script passes

## Error 1: Pre-NFL / non-NFL historical rows leaked into `rules.csv`

### Symptom

The earlier `hof_chronology` parser included years before the NFL existed, including 1869, 1876, 1898, 1904, and 1906.

Examples included:

- Rutgers-Princeton using modified London Football Association rules
- first American football rules at the Massasoit convention
- scoring changes before NFL formation

### Why it was wrong

These rows may be relevant to American football history, but they are not NFL rule changes. They polluted year-based analysis and made the dataset look broader than it really was.

### Fix

Changed `parse_hof()` to skip years before 1920.

### Validation

`validate_processing.py` checks `no_pre_1920_rows`. Current result: pass.

## Error 2: Hall of Fame chronology extraction was too broad

### Symptom

The keyword-based parser captured rows that mentioned “rules” or “moved” but were not rule changes, such as franchise relocations, league naming, and generic organizational history.

Examples seen before fixing:

- league name changed to APFA / NFL
- teams moved or renamed
- Championship Game moved to another city

### Why it was wrong

The source is a chronology, not a rule-change dataset. Keyword extraction must be conservative.

### Fix

Rewrote `parse_hof()` to:

- keep only NFL-era years
- split chronology text into sentences
- keep only specific rule-change phrases, such as waiver rule, annual draft, forward pass legalized from anywhere, hashmarks, goal posts, roughing-the-passer penalty, and college-class signing rule
- split multi-rule years into separate rows
- classify league/player-acquisition rules as `league_rule` instead of `playing_rule`

### Validation

Current `hof_chronology` rows are now 7 rows:

- 1926 college-class signing rule
- 1933 hashmarks / goal posts
- 1933 forward pass from anywhere behind line of scrimmage
- 1934 waiver rule
- 1935 annual draft
- 1935 hashmarks moved
- 1938 roughing-the-passer penalty

`validate_processing.py` checks for pre-NFL rows and franchise-move noise. Current result: pass.

## Error 3: NFL Ops historical seed rows had bad `effect` values

### Symptom

Rows from `nflops_evolution` had useful summaries but the `effect` field contained the first 500 characters of the entire page intro. Every historical row had the same irrelevant text beginning “Imagine the NFL if the rules of play had never changed…”

### Why it was wrong

It made row-level analysis misleading and could pollute embeddings or text classification.

### Fix

For curated historical seed rows, set `effect = summary`.

### Validation

Spot-checked `nflops_evolution` rows. Each `effect` now matches its specific summary.

## Error 4: `onside` false-positive inside `considering`

### Symptom

The 2026 proposal allowing League personnel to consult with on-field officials when considering disqualification was misclassified as kickoff because `onside` was found inside `considering`.

### Why it was wrong

The classifier used substring matching rather than word-boundary matching.

### Fix

Changed kickoff/special-teams detection in both scripts to use regex word boundaries:

```python
r"\b(free kick|kickoff|kicking off|onside|k-balls?|touchback|fair catch|setup zone|landing zone|kicking footballs?|wedge)\b"
```

### Validation

`validate_processing.py` checks that 2026 PDF proposal 4 is not classified as kickoff. Current result: pass.

## Error 5: Kickoff rows that mentioned replay were classified as officiating

### Symptom

The 2024 dynamic kickoff rule mentioned that the Replay Official could automatically review whether a free kick legally touched the ground or a receiving team player in the landing zone. Because “Replay Official” appeared in the text, it was classified as officiating instead of special teams.

### Why it was wrong

For phase analysis, kickoff/free-kick rules should remain special-teams rows even when they include officiating subclauses.

### Fix

In `classify()`, special-teams/kickoff detection now has priority over replay/officiating detection.

### Validation

The 2024 dynamic kickoff rule is now `category=special_teams`, `affected_phase=kickoff`, and belongs to canonical group `kickoff_dynamic_trial_to_permanent_2024_2026`.

## Error 6: 2026 full proposal PDF parser leaked bylaw text into proposal 5

### Symptom

The 2026 PDF proposal 5 row had `reason` containing the following `2026 Bylaw Proposals Summary` text and even later bylaw references.

### Why it was wrong

The regex block boundary did not stop at the “2026 Bylaw Proposals Summary” heading.

### Fix

Updated the 2026 PDF block parser to stop at:

- next playing-rule proposal
- `2026 Bylaw Proposals Summary`
- bylaw proposal heading
- `2026 Resolution Proposals Summary`
- resolution proposal heading

Also constrained `Reason:` extraction to stop before those headings.

### Validation

`validate_processing.py` checks that proposal 5's reason does not contain `Bylaw Proposals Summary`, and that proposal 5 is classified as officiating. Current result: pass.

## Error 7: K-Ball / kicking-football rows were not recognized as special teams

### Symptom

The 2025 K-Ball resolution rows were classified under general gameplay/administration in processed lineages.

### Why it was wrong

The regex matched `k-ball`, but the source text uses `K-Balls`; it also says “kicking footballs.”

### Fix

Expanded special-teams regex to include:

- `k-balls?`
- `kicking footballs?`

### Validation

Both 2025 K-Ball rows now have:

- `category=special_teams`
- `auto_lineage=kickoff`
- `auto_sublineage=k_ball_preparation`

`validate_processing.py` checks this. Current result: pass.

## Error 8: Detroit 2024 approved third-challenge rule was not linked to its canonical group

### Symptom

The canonical group `challenge_system_expansion_detroit_2023_2024` included Detroit’s 2023 proposals but missed Detroit’s 2024 approved rule protecting a club’s ability to challenge a third ruling after one successful challenge.

### Why it was wrong

The selector matched “third challenge” but not “challenge a third ruling.”

### Fix

Added `challenge a third` to the manual selector.

### Validation

`validate_processing.py` checks that the Detroit challenge canonical group contains a 2024 approved row. Current result: pass.

## Error 9: Manual link table included non-applied selector matches

### Symptom

`rule_proposal_links.csv` included broad matches even when those rows had already been assigned to earlier, more specific canonical groups. This made the link table look like it contained real assignments when some were merely candidate overlaps.

### Why it was wrong

`apply_manual_links()` added link rows before checking whether an event was still unassigned.

### Fix

Changed `apply_manual_links()` so link rows are emitted only when the manual selector is actually applied to an unassigned event.

### Validation

`validate_processing.py` checks `link_type == manual_selector_applied` for all link rows. Current result: pass.

## Error 10: Noisy `pypdf` malformed-object warnings

### Symptom

Parsing the 2022 rulebook PDF produced hundreds of `Ignoring wrong pointing object` warnings on stderr.

### Why it was wrong

The output looked like a failed run even though extraction succeeded.

### Fix

Wrapped the 2022 PDF reader creation with `contextlib.redirect_stderr(io.StringIO())`.

### Validation

A rebuild now has zero stderr bytes for `build_rules_csv.py` under normal cached execution.

## Error 11: Substitution history rows were classified as generic gameplay

### Symptom

The 1943 substitution-relaxation row and 1949 free-substitution row appeared under general gameplay.

### Why it was wrong

They are better modeled as roster/substitution-lineage changes because they affected substitution and specialization.

### Fix

Added `substitution` and `substitute` to roster-management classification and lineage rules.

### Validation

Both rows now have:

- `category=roster_management`
- `affected_phase=roster`
- `auto_lineage=roster_management`
- `auto_sublineage=roster_flexibility`

`validate_processing.py` checks this. Current result: pass.

## Error 12: 2026 approved proposal `(A)` was parsed as `(A)` instead of `4-A`

### Symptom

The 2026 approved page had a nested label `(A)` for a playing-rule proposal. It was stored as proposal number `(A)`, losing its parent ordinal context.

### Why it was wrong

The generic list parser did not normalize lettered list items.

### Fix

When a list item number is `(A)`, it is converted to `{list_index}-A`, producing `4-A` in the 2026 approved page.

### Validation

`nflops_approved_2026` now has proposal number `4-A` for the disqualification-consultation rule.

## Current validation

Created:

```bash
scripts/validate_processing.py
```

Run:

```bash
uv run scripts/validate_processing.py
```

Current output:

```text
rules_rows=102
events_rows=102 changes_rows=61 lineages_rows=22 links_rows=53
PASS
```

## Current files after fixes

Updated scripts:

- `scripts/build_rules_csv.py`
- `scripts/build_analysis_tables.py`
- `scripts/validate_processing.py`

Updated data:

- `rules.csv`
- `data/processed/manual_links.yaml`
- `data/processed/rule_events.csv`
- `data/processed/rule_changes.csv`
- `data/processed/rule_lineages.csv`
- `data/processed/rule_proposal_links.csv`
- parquet equivalents

## Known limitations, not treated as processing errors

These are not fixed in this pass because they require new sources or human editorial decisions:

1. 2024 detailed rulebook PDF/list is still not located.
2. 2021 and earlier annual rulebook PDFs are still missing except for seed historical rows.
3. Historical rows remain seed-quality, not a complete official chronology.
4. Some canonical grouping choices are interpretive, especially broad `replay_officiating_authority_expansion_2023_2026`.
5. Some summary-level and rulebook-section rows intentionally coexist; downstream analysis should decide whether to use event-level or canonical-change-level tables.
