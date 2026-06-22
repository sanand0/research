# NFL Rules Research Dataset

This repository builds and analyzes a structured dataset of NFL rule changes, proposals, approvals, and related historical seed rows.

It was created to answer questions like:

- What NFL rules change most often?
- How does a rule idea move from proposal to approval?
- Which proposals fail but reveal recurring pressure in the game?
- How does the NFL use one-year trials and later patches?
- Can rule changes be analyzed as control systems, incentive design, and governance mechanisms?

The project has progressed beyond extraction. It now includes:

- reproducible source fetching and parsing
- processed event/change/lineage tables
- manual canonical grouping through `manual_links.yaml`
- source-quality scoring
- validation checks
- proposal-funnel analysis
- pressure-signal analysis
- kickoff case-study analysis using nflverse play-by-play
- replay/officiating authority analysis
- publishable Markdown/HTML articles
- a static HTML explorer

The strongest current coverage is 2023-2026 official NFL Operations proposal/approval data, plus official 2022 and 2025 rulebook change rows. Historical rows are seed-quality and should be treated as context or hypotheses unless independently verified.

## Current status

Run validation:

```bash
cd /home/sanand/code/research/nfl-rules
uv run scripts/validate_processing.py
```

Current validated state:

```text
rules_rows=108
events_rows=108 changes_rows=35 lineages_rows=32 links_rows=108
PASS
```

Current core table sizes:

```text
rules.csv                                      108 rows, 22 columns
data/processed/rule_events.csv                108 rows, 43 columns
data/processed/rule_changes.csv                35 rows, 21 columns
data/processed/rule_lineages.csv               32 rows, 10 columns
data/processed/rule_proposal_links.csv        108 rows, 16 columns
data/analysis/manual_review_queue.csv          14 rows, 17 columns
data/analysis/pressure_signals_ranked.csv       8 rows, 22 columns
data/interim/rulebook_pdf_candidates_all.csv  110 rows, 17 columns
```

The manual review queue is now limited to historical seed confirmation. Recent official proposal/approval rows are processed and linked.

## Quick start for a fresh developer or AI coding agent

Start here:

```bash
cd /home/sanand/code/research/nfl-rules
uv run scripts/validate_processing.py
```

Then inspect these files in order:

1. `README.md` — this guide.
2. `chatgpt.md` — ChatGPT conversation leading to this project.
3. `rules.csv` — raw structured extraction output.
4. `data/processed/rule_events.csv` — enriched event-level table.
5. `data/processed/rule_changes.csv` — canonical change-level table.
6. `data/processed/manual_links.yaml` — human-curated canonical grouping rules.
7. `data/analysis/rules_explorer.html` — static browser explorer.
8. `data/publish/kickoff-rules-laboratory/index.html` — strongest finished article.
9. `data/publish/replay-authority-map/index.html` — second finished article.

For a full deterministic rebuild from cached sources:

```bash
uv run scripts/build_rules_csv.py
uv run scripts/build_analysis_tables.py
uv run scripts/validate_processing.py
uv run scripts/audit_rulebook_pdf_consistency.py
uv run scripts/analyze_rule_funnel.py
uv run scripts/analyze_pressure_signals.py
uv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025
uv run scripts/analyze_kickoff_adjusted.py
uv run scripts/write_kickoff_publish_ready_post.py
uv run scripts/analyze_replay_authority.py
uv run scripts/build_replay_authority_map.py
uv run scripts/write_replay_authority_post.py
uv run scripts/build_rules_explorer.py
uv run scripts/build_source_quality_report.py
uv run scripts/package_posts.py
uv run scripts/build_manual_review_queue.py
```

To refetch source pages and PDFs instead of using cached files:

```bash
uv run scripts/build_rules_csv.py --refresh
uv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025 --refresh
uv run scripts/discover_rulebook_pdfs.py --refresh
```

Use refresh sparingly. Cached sources preserve reproducibility.

## Repository layout

```text
/home/sanand/code/research/nfl-rules/
├── README.md
├── rules.csv
├── missing-rules-v1.md
├── processing-errors-v1.md
├── scripts/
│   ├── build_rules_csv.py
│   ├── build_analysis_tables.py
│   ├── validate_processing.py
│   ├── discover_rulebook_pdfs.py
│   ├── audit_rulebook_pdf_consistency.py
│   ├── analyze_rule_funnel.py
│   ├── analyze_pressure_signals.py
│   ├── analyze_kickoff_case_study.py
│   ├── analyze_kickoff_adjusted.py
│   ├── write_kickoff_narrative.py
│   ├── write_kickoff_blog_post.py
│   ├── write_kickoff_publish_ready_post.py
│   ├── analyze_replay_authority.py
│   ├── build_replay_authority_map.py
│   ├── write_replay_authority_post.py
│   ├── build_rules_explorer.py
│   ├── build_source_quality_report.py
│   ├── package_posts.py
│   └── build_manual_review_queue.py
├── data/
│   ├── raw/
│   │   ├── *.html / *.pdf
│   │   ├── nflverse/
│   │   └── rulebooks/
│   ├── interim/
│   │   ├── rules.parquet
│   │   ├── source_manifest.csv
│   │   ├── rulebook_pdf_candidates.csv/.parquet
│   │   ├── rulebook_pdf_candidates_all.csv/.parquet
│   │   └── rulebook_pdf_discovery_report.md
│   ├── processed/
│   │   ├── manual_links.yaml
│   │   ├── rule_events.csv/.parquet
│   │   ├── rule_changes.csv/.parquet
│   │   ├── rule_lineages.csv/.parquet
│   │   └── rule_proposal_links.csv/.parquet
│   ├── analysis/
│   │   ├── rule_funnel_*.csv/.parquet
│   │   ├── rule_funnel_report.md
│   │   ├── pressure_signals_ranked.csv/.parquet
│   │   ├── pressure_signals_report.md
│   │   ├── kickoff_*.csv/.parquet/.md/.png
│   │   ├── replay_authority_*.csv/.parquet/.md/.png
│   │   ├── rulebook_2025_online_pdf_audit.*
│   │   ├── source_quality_summary.csv/.parquet
│   │   ├── source_quality_report.md
│   │   ├── manual_review_queue.csv/.parquet/.md
│   │   └── rules_explorer.html
│   └── publish/
│       ├── index.html
│       ├── kickoff-rules-laboratory/
│       │   ├── index.html
│       │   ├── index.md
│       │   └── chart PNGs
│       └── replay-authority-map/
│           ├── index.html
│           ├── index.md
│           └── chart PNG
```

## Mental model of the project

There are five layers:

```text
1. Sources      -> cached HTML/PDF/play-by-play files under data/raw/
2. Extraction   -> rules.csv and data/interim/rules.parquet
3. Processing   -> rule_events, rule_changes, rule_lineages, proposal links
4. Analysis     -> funnel, pressure signals, kickoff, replay, quality, manual queue
5. Artifacts    -> explorer, reports, publishable posts
```

Do not edit generated CSVs directly. Change the scripts or `manual_links.yaml`, then rerun the pipeline.

## Data sources

### Official NFL Operations sources

The extraction script currently uses official NFL Operations pages/PDFs for:

- 2023 rules-change proposals
- 2023 approved playing rules
- 2023 adopted fair-catch special article
- 2023 Resolution G-1 special article after the cancelled Bills-Bengals game
- 2024 approved playing rules
- 2025 proposed playing rules, bylaws, and resolutions
- 2025 approved playing rules, bylaws, and resolutions
- 2025 online rulebook change list
- 2025 official rulebook PDF
- 2026 proposed playing rules, bylaws, and resolutions
- 2026 approved playing rules, bylaws, and resolutions
- 2026 full proposal PDF
- 2022 official rulebook change rows, extracted earlier from a cached/known PDF URL
- NFL Operations rules-evolution narrative

### Secondary historical source

The Pro Football Hall of Fame chronology is used only for conservative seed rows. These rows are marked as lower-quality and excluded from default public-claim analysis.

### nflverse play-by-play

The kickoff analysis downloads and caches nflverse annual play-by-play parquet files under:

```text
data/raw/nflverse/
```

Currently used seasons:

```text
2021, 2022, 2023, 2024, 2025
```

## Core data files

### `rules.csv`

This is the extraction output. It has one row per source-observed rule/proposal/change/seed row.

Important columns include:

```text
rule_id
source_key
source_url
year
season
status
item_type
proposal_number
proposer
summary
effect
reason
rulebook_ref
category
mechanism
affected_phase
affected_party
temporality
source_kind
extraction_method
confidence
```

Use `rules.csv` when you need source-level auditability.

### `data/processed/rule_events.csv`

This enriches `rules.csv` with analytical fields.

Added fields include:

```text
event_id
year_int
normalized_summary
proposer_class
origin_team
granularity
outcome
proposal_group
auto_lineage
auto_sublineage
target_metric_guess
source_quality_tier
source_quality_score
source_quality_note
analysis_include_default
canonical_change_id
manual_lineage
manual_sublineage
status_lifecycle
manual_title
needs_manual_review
```

Use this for event-level analysis and auditing.

### `data/processed/rule_changes.csv`

This is the canonical change-level table. It collapses related event rows into meaningful groups using `manual_links.yaml`.

Use this for higher-level analysis: lineages, rule families, proposal-to-approval lifecycle, and public-facing summaries.

Important columns include:

```text
canonical_change_id
title
lineage
sublineage
first_year
last_year
years
status_lifecycle
target_metrics
event_count
approved_event_count
proposed_event_count
historical_event_count
source_keys
best_source_quality_score
source_quality_tiers
analysis_include_default
representative_summary
needs_manual_review
```

### `data/processed/manual_links.yaml`

This is the human curation layer.

It defines canonical groups using semantic selectors rather than hard-coded row IDs. This makes it resilient when extraction changes cause row IDs to shift.

Example conceptually:

```yaml
canonical_change_id: kickoff_dynamic_trial_to_permanent_2024_2026
lineage: kickoff
sublineage: dynamic_kickoff
status_lifecycle: trial_to_permanent_to_tuned
selectors:
  - year: 2024
    contains_all: ["new form", "free kick"]
  - year: 2025
    contains_any: ["setup zone", "touchback", "onside kick"]
```

If a new row should join an existing canonical group, edit this file and rerun:

```bash
uv run scripts/build_analysis_tables.py
uv run scripts/validate_processing.py
```

## Source-quality system

Source quality is computed in `scripts/build_analysis_tables.py` and summarized by `scripts/build_source_quality_report.py`.

Current source-quality tiers:

```text
official_pdf_rulebook        8 events, default included
official_pdf_proposal        5 events, default included
official_rulebook_page       6 events, default included
official_special_article     2 events, default included
official_summary_page       73 events, default included
official_history_seed        7 events, default excluded
secondary_history_seed       7 events, default excluded
```

Rule of thumb:

- For public claims, use rows where `analysis_include_default == True`.
- For ideation, lineage discovery, and historical hypotheses, seed rows may be included but should be labeled clearly.

Run:

```bash
uv run scripts/build_source_quality_report.py
```

Outputs:

```text
data/analysis/source_quality_summary.csv
data/analysis/source_quality_report.md
```

## Script reference

### Extraction and processing

#### `scripts/build_rules_csv.py`

Purpose: fetch/cache official sources and parse them into `rules.csv`.

Run:

```bash
uv run scripts/build_rules_csv.py
uv run scripts/build_rules_csv.py --refresh
```

Outputs:

```text
rules.csv
data/interim/rules.parquet
data/interim/source_manifest.csv
data/raw/*
```

Notes:

- Cached source files are reused unless `--refresh` is passed.
- The parser handles official summary pages, special articles, rulebook pages, rulebook PDFs, and proposal PDFs.
- It also creates lower-confidence historical seed rows.

#### `scripts/build_analysis_tables.py`

Purpose: enrich `rules.csv` into processed event/change/lineage/link tables.

Run:

```bash
uv run scripts/build_analysis_tables.py
```

Outputs:

```text
data/processed/rule_events.csv/.parquet
data/processed/rule_changes.csv/.parquet
data/processed/rule_lineages.csv/.parquet
data/processed/rule_proposal_links.csv/.parquet
```

This is where taxonomy, source quality, canonical grouping, and manual links are applied.

#### `scripts/validate_processing.py`

Purpose: validate invariants and catch known prior bugs.

Run after any extraction, taxonomy, or manual-link change:

```bash
uv run scripts/validate_processing.py
```

It checks things like:

- no duplicate rule/event IDs
- no blank summaries
- no pre-1920 non-NFL rows
- known 2026 PDF parsing bugs are fixed
- K-Ball rows classify correctly
- Detroit challenge links are present
- source event counts match

### Discovery and audit

#### `scripts/discover_rulebook_pdfs.py`

Purpose: discover and cache official NFL rulebook/proposal PDF candidates.

Run constrained discovery:

```bash
uv run scripts/discover_rulebook_pdfs.py
```

Run pattern probes in batches:

```bash
uv run scripts/discover_rulebook_pdfs.py --include-pattern-probes --years 2019-2024 --offset 0 --limit 50
uv run scripts/discover_rulebook_pdfs.py --include-pattern-probes --years 2019-2024 --offset 50 --limit 50
```

Outputs:

```text
data/interim/rulebook_pdf_candidates.csv/.parquet
data/interim/rulebook_pdf_candidates_all.csv/.parquet
data/interim/rulebook_pdf_discovery_report.md
data/raw/rulebooks/*
```

Current result:

```text
total_unique_candidates=110
found=2
```

Found/cached:

```text
2025 official rulebook PDF
2026 official proposal PDF
```

No additional 2019-2024 annual rulebook PDFs were found through the current known-slug pattern-probe approach.

#### `scripts/audit_rulebook_pdf_consistency.py`

Purpose: compare online 2025 rulebook change rows against official 2025 PDF extraction.

Run:

```bash
uv run scripts/audit_rulebook_pdf_consistency.py
```

Outputs:

```text
data/analysis/rulebook_2025_online_pdf_audit.csv/.parquet/.md
```

Current result: all six 2025 rulebook references appear in both sources with high text similarity.

### Analyses

#### `scripts/analyze_rule_funnel.py`

Purpose: analyze proposal → approval dynamics, especially for 2023-2026.

Run:

```bash
uv run scripts/analyze_rule_funnel.py
```

Outputs:

```text
data/analysis/rule_funnel_summary.csv/.parquet
data/analysis/rule_funnel_by_year.csv/.parquet
data/analysis/rule_funnel_by_category.csv/.parquet
data/analysis/rule_funnel_by_proposer_class.csv/.parquet
data/analysis/rule_funnel_by_lineage.csv/.parquet
data/analysis/rule_funnel_canonical_outcomes.csv/.parquet
data/analysis/rule_funnel_pressure_signals.csv/.parquet
data/analysis/rule_funnel_report.md
```

Current 2023-2026 summary:

```text
events=91
proposed_events=45
approved_events=46
canonical_changes=26
proposed_canonical_changes=25
approved_canonical_changes=18
proposed_and_approved=17
approved_without_captured_proposal=1
proposed_only_pressure_signal=8
```

#### `scripts/analyze_pressure_signals.py`

Purpose: rank proposed-only canonical groups as pressure signals.

Run:

```bash
uv run scripts/analyze_pressure_signals.py
```

Outputs:

```text
data/analysis/pressure_signals_ranked.csv/.parquet
data/analysis/pressure_signals_report.md
```

Current ranked signals:

```text
defensive_contact_automatic_first_down_pressure_2025
playoff_seeding_record_based_wild_card_2025
kickoff_alternative_fourth_and_twenty_2023
tush_push_assisted_sneak_pressure_2025
punt_touchback_25_yard_line_2023
future_draft_pick_trade_horizon_2026
split_flow_crackback_low_block_2023
reserve_injured_90_player_limit_2025
```

Interpretation: proposed-only rows are not failures; they are sensors for latent stress in the game or league operations.

#### `scripts/analyze_kickoff_case_study.py`

Purpose: combine kickoff rule timeline with nflverse play-by-play metrics.

Run:

```bash
uv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025
```

Outputs:

```text
data/analysis/kickoff_rule_timeline.csv/.parquet
data/analysis/kickoff_pbp_summary_by_season.csv/.parquet
data/analysis/kickoff_pbp_summary_by_season_type.csv/.parquet
data/analysis/kickoff_examples.csv/.parquet
data/analysis/kickoff_case_study_report.md
data/analysis/kickoff_return_touchback_rates.png
data/analysis/kickoff_starting_field_position.png
```

Headline regular-season metrics:

```text
2021 return_rate=39.1% touchback_rate=57.5% avg_start_own=25.7
2022 return_rate=37.1% touchback_rate=59.7% avg_start_own=26.0
2023 return_rate=21.4% touchback_rate=73.0% avg_start_own=25.6
2024 return_rate=32.6% touchback_rate=64.2% avg_start_own=30.2
2025 return_rate=74.0% touchback_rate=20.6% avg_start_own=31.0
```

#### `scripts/analyze_kickoff_adjusted.py`

Purpose: split kickoff metrics by quarter, score bucket, time bucket, and late-game onside context.

Run:

```bash
uv run scripts/analyze_kickoff_adjusted.py
```

Outputs:

```text
data/analysis/kickoff_adjusted_by_period.csv/.parquet
data/analysis/kickoff_adjusted_by_score_bucket.csv/.parquet
data/analysis/kickoff_adjusted_by_time_bucket.csv/.parquet
data/analysis/kickoff_adjusted_late_game_onside.csv/.parquet
data/analysis/kickoff_adjusted_report.md
data/analysis/kickoff_adjusted_return_rate_by_score_bucket.png
```

Interpretation: the 2025 return-rate increase is visible across ordinary score buckets, not just late-game onside situations.

#### `scripts/analyze_replay_authority.py`

Purpose: classify replay/officiating events by authority shift.

Run:

```bash
uv run scripts/analyze_replay_authority.py
```

Outputs:

```text
data/analysis/replay_authority_events.csv/.parquet
data/analysis/replay_authority_by_year.csv/.parquet
data/analysis/replay_authority_by_mechanism.csv/.parquet
data/analysis/replay_authority_report.md
data/analysis/replay_authority_timeline.png
```

#### `scripts/build_replay_authority_map.py`

Purpose: turn replay/officiating rows into a compact authority map.

Run:

```bash
uv run scripts/build_replay_authority_map.py
```

Outputs:

```text
data/analysis/replay_authority_map.csv/.parquet
data/analysis/replay_authority_map.md
data/analysis/replay_authority_map.png
```

Current authority stages:

```text
1. Coach / club challenge: 3 events
2. Replay official / booth review: 4 events
3. Replay assist: 4 events
4. League consultation: 3 events
5. Emergency centralized override: 3 events
6. Field + replay baseline: 4 events
```

### Publishing / artifacts

#### `scripts/write_kickoff_publish_ready_post.py`

Purpose: write a concise, publishable kickoff post.

Run:

```bash
uv run scripts/write_kickoff_publish_ready_post.py
```

Output:

```text
data/analysis/kickoff_publish_ready_post.md
```

Core thesis:

```text
Kickoff is the NFL’s best example of rules as a control system.
```

#### `scripts/write_replay_authority_post.py`

Purpose: write a publishable replay/officiating post.

Run:

```bash
uv run scripts/write_replay_authority_post.py
```

Output:

```text
data/analysis/replay_authority_post.md
```

Core thesis:

```text
The NFL is automating judgment at the edges first.
```

#### `scripts/package_posts.py`

Purpose: package the two publishable posts as standalone HTML + Markdown with images copied beside them.

Run:

```bash
uv run scripts/package_posts.py
```

Outputs:

```text
data/publish/index.html
data/publish/kickoff-rules-laboratory/index.html
data/publish/kickoff-rules-laboratory/index.md
data/publish/replay-authority-map/index.html
data/publish/replay-authority-map/index.md
```

#### `scripts/build_rules_explorer.py`

Purpose: build a standalone static HTML explorer.

Run:

```bash
uv run scripts/build_rules_explorer.py
```

Output:

```text
data/analysis/rules_explorer.html
```

Current explorer features:

```text
lineage filter
source-quality filter
free-text search
filtered CSV export
timeline by year
pressure-signal panel
kickoff metrics panel
embedded kickoff chart
replay authority panel
embedded replay map
clickable source URLs in event table
```

### Review queue

#### `scripts/build_manual_review_queue.py`

Purpose: create a prioritized manual review queue.

Run:

```bash
uv run scripts/build_manual_review_queue.py
```

Outputs:

```text
data/analysis/manual_review_queue.csv/.parquet/.md
```

Current queue:

```text
rows=14
historical_seed_granularity=14
historical_seed_requires_confirmation=14
low_confidence_source_or_extraction=7
```

These are not urgent for current official recent-rule analyses. They matter if you want to make stronger historical claims.

## Audits and how the project came about

Two audit documents capture the iterative build history.

### `missing-rules-v1.md`

This documents missing source coverage found after the first extraction pass.

Important fixes from that audit:

- added 2023 proposed rule changes
- added 2023 fair-catch special adoption article
- added 2023 Resolution G-1 special article
- added 2025 detailed rulebook change list
- added 2022 official rulebook change list

### `processing-errors-v1.md`

This documents extraction/classification/processing bugs found after red-teaming.

Important fixes from that audit:

- removed pre-1920 non-NFL history rows
- tightened Hall of Fame chronology extraction
- fixed bad repeated historical `effect` text
- fixed `onside` false positive inside “considering”
- fixed kickoff rows being misclassified as replay/officiating when they mention Replay Official subclauses
- fixed 2026 PDF proposal text leakage into bylaw sections
- classified K-Ball rows correctly
- linked Detroit’s 2024 third-challenge approval
- emitted only actually applied manual links
- suppressed noisy PDF warnings
- reclassified substitution rows as roster/substitution lineage
- normalized 2026 approved proposal `(A)` to `4-A`

## Key findings so far

### 1. The best current story is kickoff

Kickoff is the strongest case study because it has a visible policy sequence and measurable outcomes.

Core finding:

```text
2023 return_rate=21.4%, touchback_rate=73.0%, avg_start_own=25.6
2025 return_rate=74.0%, touchback_rate=20.6%, avg_start_own=31.0
```

Interpretation:

The NFL bought more live returns by changing incentives and spatial constraints, while giving offenses better average starting field position.

### 2. Replay/officiating is authority migration

Replay changes are best analyzed as shifts in who can initiate and decide corrections.

Authority ladder:

```text
coach challenge -> replay official / booth review -> replay assist -> league consultation -> emergency centralized override
```

This generalizes well to AI governance and human-in-the-loop workflows.

### 3. Proposed-only rows are pressure signals

The eight current pressure signals are useful future-watch items, not just failed proposals.

Most interesting:

```text
defensive contact automatic first down
playoff seeding by record
4th-and-20 onside alternative
tush push / assisted sneak
punt touchback to the 25
```

### 4. Historical analysis is not yet complete

The historical seed rows are useful for lineage framing, but this is not yet a complete century-long NFL rule-change database.

Important missing source gap:

```text
2024, 2021, 2020, 2019 official annual rulebook PDFs or detailed change lists
```

The current PDF discovery pattern-probe did not find these.

## How to extend safely

### If you add a new source

1. Add it to `SOURCES` in `scripts/build_rules_csv.py`.
2. Add or reuse a parser.
3. Run:

```bash
uv run scripts/build_rules_csv.py --refresh
uv run scripts/build_analysis_tables.py
uv run scripts/validate_processing.py
```

4. Check whether `source_quality_tier` is correct.
5. Update `data/processed/manual_links.yaml` if new rows belong to existing canonical groups.
6. Rerun affected analyses.

### If you change taxonomy

Taxonomy logic lives mostly in `scripts/build_analysis_tables.py`, especially:

```text
infer_lineage_and_sublineage()
infer_target_metric()
source_quality()
```

After changes:

```bash
uv run scripts/build_analysis_tables.py
uv run scripts/build_manual_review_queue.py
uv run scripts/validate_processing.py
```

Then inspect:

```text
data/analysis/manual_review_queue.csv
data/processed/rule_lineages.csv
data/processed/rule_changes.csv
```

### If you change canonical grouping

Edit:

```text
data/processed/manual_links.yaml
```

Then run:

```bash
uv run scripts/build_analysis_tables.py
uv run scripts/analyze_rule_funnel.py
uv run scripts/analyze_pressure_signals.py
uv run scripts/build_manual_review_queue.py
uv run scripts/validate_processing.py
```

### If you change kickoff logic

The shared extraction of kickoff plays is in:

```text
scripts/analyze_kickoff_case_study.py
```

The adjusted analysis imports that logic.

Rerun:

```bash
uv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025
uv run scripts/analyze_kickoff_adjusted.py
uv run scripts/write_kickoff_publish_ready_post.py
```

### If you change replay logic

Rerun:

```bash
uv run scripts/analyze_replay_authority.py
uv run scripts/build_replay_authority_map.py
uv run scripts/write_replay_authority_post.py
```

## Common pitfalls

### Do not treat `rules.csv` as the final analysis table

`rules.csv` is source-level. It intentionally includes duplicate perspectives, such as online rulebook rows and PDF rulebook rows for the same 2025 changes.

Use:

```text
rule_events.csv   for event/source-level analysis
rule_changes.csv  for canonical-change-level analysis
```

### Do not use historical seed rows for strong public claims

Filter:

```text
analysis_include_default == True
```

or use source quality tiers.

### Proposal numbers are not globally unique

Proposal numbers can restart by section or proposer group. Use:

```text
year + source_key + proposer + rulebook_ref + summary
```

or canonical IDs, not proposal numbers alone.

### Some rows are intentionally duplicated across source types

Example: 2025 rulebook changes appear from both the online rulebook page and the official PDF. This is good for auditability. Use canonical grouping for deduped analysis.

### The kickoff play-by-play metrics are descriptive

Caveats:

- starting field position is estimated from the next scrimmage-like play
- onside success is inferred from possession after the kick
- causal claims require controls for score, time, stadium, weather, and game context

## Known gaps

### Missing annual rulebook PDFs

Still missing:

```text
2024
2021
2020
2019
possibly earlier years
```

The current discovery script found:

```text
2025 official rulebook PDF
2026 official proposal PDF
```

but did not find the missing years through sitemap/cached links or known-slug pattern probes.

### Historical completeness

The historical rows are seed-quality only. They are not a complete annual NFL rule-change chronology.

### Unit tests

There is a validation script but not a full test suite. A good next engineering step is `scripts/test_pipeline.py` or a `tests/` directory.

## Best next steps

1. Publish `data/publish/kickoff-rules-laboratory/index.md` or `index.html`.
2. Publish `data/publish/replay-authority-map/index.md` or `index.html`.
3. Replace pattern-based PDF discovery with web/manual/archive discovery for 2024, 2021, 2020, 2019 annual rulebooks.
4. Add tests for source quality, canonical grouping, PDF-vs-online consistency, and expected counts.
5. Add story mode to `rules_explorer.html`.
6. If historical claims matter, manually validate the 14 remaining historical seed rows in `manual_review_queue.csv`.

## Where to find help inside this repository

Use these files as internal documentation:

```text
README.md                         main onboarding guide
missing-rules-v1.md               missing source audit
processing-errors-v1.md           processing bug audit and fixes
data/analysis/*_report.md         analysis-specific reports
data/analysis/manual_review_queue.md  rows still needing review
data/analysis/source_quality_report.md source-quality explanation
data/processed/manual_links.yaml  canonical grouping logic
```

For a new AI coding agent, the safest workflow is:

```bash
uv run scripts/validate_processing.py
cat README.md
cat processing-errors-v1.md
cat missing-rules-v1.md
python - <<'PY'
import pandas as pd
for p in ['rules.csv','data/processed/rule_events.csv','data/processed/rule_changes.csv']:
    df=pd.read_csv(p)
    print(p, df.shape)
    print(df.head(3).to_string())
PY
```

Then make small changes, rerun validation, and update this README if the project structure or outputs change.
