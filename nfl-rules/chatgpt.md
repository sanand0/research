---
title: "NFL Rule Change Anaysis"
date: 2026-06-02T11:22:29+08:00
source: "https://chatgpt.com/c/6a1d4cc7-1b50-83ec-8796-b1c4b0ac79ed"
---

## ChatGPT

I’ll add three script-based pipelines: a rule-funnel analysis, a kickoff case-study analysis with cached nflverse play-by-play, and a manual-review queue generator. Then I’ll update the README with the current project structure and suggested path forward.

Called tool

The nflverse parquet URLs are reachable, so the kickoff script can cache annual play-by-play files locally and rerun without refetching. I’ll now add the analysis scripts and execute them.

Called toolCalled tool

The rule-funnel script is complete and has already produced its CSV and Markdown report. I’m now adding the kickoff case-study script; it will cache nflverse annual parquet files and skip unavailable seasons rather than failing.

Called toolCalled toolCalled toolCalled toolCalled toolCalled tool

Implemented steps 1, 2, and 3 as resumable Python scripts and updated `README.md`.

Created:


```
scripts/analyze_rule_funnel.pyscripts/analyze_kickoff_case_study.pyscripts/build_manual_review_queue.py
```

Updated:


```
README.md
```

Generated analysis outputs:


```
data/analysis/rule_funnel_report.mddata/analysis/rule_funnel_summary.csvdata/analysis/rule_funnel_by_year.csvdata/analysis/rule_funnel_by_category.csvdata/analysis/rule_funnel_by_proposer_class.csvdata/analysis/rule_funnel_by_lineage.csvdata/analysis/rule_funnel_canonical_outcomes.csvdata/analysis/rule_funnel_pressure_signals.csvdata/analysis/kickoff_case_study_report.mddata/analysis/kickoff_rule_timeline.csvdata/analysis/kickoff_pbp_summary_by_season.csvdata/analysis/kickoff_pbp_summary_by_season_type.csvdata/analysis/kickoff_examples.csvdata/analysis/kickoff_return_touchback_rates.pngdata/analysis/kickoff_starting_field_position.pngdata/analysis/manual_review_queue.csvdata/analysis/manual_review_queue.md
```

The full pipeline now runs with:


```
Bashcd /home/sanand/code/research/nfl-rulesuv run scripts/build_rules_csv.pyuv run scripts/build_analysis_tables.pyuv run scripts/validate_processing.pyuv run scripts/analyze_rule_funnel.pyuv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025uv run scripts/build_manual_review_queue.py
```

Validation passes:


```
rules_rows=102events_rows=102 changes_rows=61 lineages_rows=22 links_rows=53PASS
```

Key outputs from step 1, rule funnel:


```
2023-2026 events: 85proposed events: 45approved events: 40canonical changes: 44proposed canonical changes: 29approved canonical changes: 23proposed and approved: 8approved without captured proposal: 15proposed-only pressure signals: 21
```

Key outputs from step 2, kickoff case study:


```
2021 REG return_rate=0.3914 touchback_rate=0.5752 avg_start_yardline_own=25.732022 REG return_rate=0.3706 touchback_rate=0.5969 avg_start_yardline_own=25.952023 REG return_rate=0.2139 touchback_rate=0.7302 avg_start_yardline_own=25.622024 REG return_rate=0.3261 touchback_rate=0.6419 avg_start_yardline_own=30.242025 REG return_rate=0.7403 touchback_rate=0.2064 avg_start_yardline_own=30.96
```

The kickoff story is now strong: 2023 suppressed returns, 2024 partially restored them, and 2025 appears to have dramatically shifted the return/touchback balance.

Step 3, manual-review queue:


```
Rows requiring review: 50not_linked_to_canonical_group                    49flagged_by_processing                            21historical_seed_granularity                      14historical_seed_requires_confirmation            14generic_lineage_needs_more_specific_taxonomy     11low_confidence_source_or_extraction               7non_playing_rule_classification_check             4
```

Best next steps:

1. Curate `data/analysis/manual_review_queue.csv`, starting with recent approved rows and generic-lineage rows. This will improve all downstream analysis.
2. Convert the kickoff analysis into a short publishable narrative using `kickoff_case_study_report.md` and the two PNG charts. This is the strongest current insight.
3. Add `scripts/analyze_replay_authority.py` next. Replay/officiating authority expansion is the second-best case study after kickoff.
4. Search for and add official 2024, 2021, 2020, and 2019 rulebook PDFs. This is the biggest remaining coverage gap.
5. Improve proposal-to-approval links in `manual_links.yaml`, especially for replay/challenge, 2025 roster rules, and 2026 officiating work-stoppage authority.

---

## User

Execute 1, 2, 3. Document everything so far in README.md. Think about the best way to progress on the next steps and suggest.

---

## ChatGPT

I’ll execute the three requested next steps: curate the review queue into better canonical/taxonomy links, produce a publishable kickoff narrative, and add a replay/officiating authority analysis script. Then I’ll update the README and rerun validation.

Called tool

The manual queue shows several fixable taxonomy and grouping errors, not just “review needed” rows. I’ll handle the big ones first: 2023 penalty-normalization rows, 2025 roster/club-business rows, K-Ball rows, free-agent video-call rows, and historical field/player-acquisition rows.

Called toolCalled tool

The taxonomy pass reduced the review reasons by removing the generic-lineage bucket. I’ll now add curated canonical groups for the recurring singleton families so the queue distinguishes true singletons from meaningful clusters.

Called tool


<details>
<summary>Called tool: Local MCP - Bash</summary>

Request

```
{commands: "cd /home/sanand/code/research/nfl-rules && sed -n '20,55p' scripts/build_manual_review_queue.py && uv run --with pandas python - <<'PY' import pandas as pd q=pd.read_csv('data/analysis/manual_review_queue.csv').fillna('') print(q[q.review_reasons.str.contains('non_playing', regex=False)][['year','item_type','category','auto_lineage','review_reasons']].to_string(index=False)) PY"
,
timeout_ms:
120000}
```

Response

```
{result: " if float(row.get("confidence", 1)) < 0.7: out.append("low_confidence_source_or_extraction") except Exception: pass if str(row.get("status", "")) == "historical_context": out.append("historical_seed_requires_confirmation") if str(row.get("granularity", "")) == "historical_seed": out.append("historical_seed_granularity") if str(row.get("auto_lineage", "")) == "general_gameplay": out.append("generic_lineage_needs_more_specific_taxonomy") if str(row.get("canonical_change_id", "")).startswith("event_"): out.append("not_linked_to_canonical_group") if str(row.get("item_type", "")) in {"league_rule", "resolution", "bylaw"} and str(row.get("category", "")) in {"gameplay", "administration"}: out.append("non_playing_rule_classification_check") return list(dict.fromkeys(out)) def priority(row: pd.Series) -> int: rs = str(row.get("review_reasons", "")).split(";") if row.get("review_reasons", "") else [] score = 0 if "low_confidence_source_or_extraction" in rs: score += 5 if "historical_seed_requires_confirmation" in rs: score += 4 if "generic_lineage_needs_more_specific_taxonomy" in rs: score += 3 if "not_linked_to_canonical_group" in rs: score += 2 if int(row.get("year_int", 0) or 0) >= 2023: score += 2 if str(row.get("status", "")) == "approved": score += 1 return score def suggested_action(row: pd.Series) -> str: rs = str(row.get("review_reasons", "")) year item_type category auto_lineage review_reasons 2025 bylaw administration roster_management non_playing_rule_classification_check 2025 bylaw administration roster_management non_playing_rule_classification_check "
}
1 earlier tool call hidden.
Open tool call list
```

</details>

The queue is now mostly historical seed confirmation, which is acceptable. I found two remaining actionable items: DFR bylaw classification and the 2022 free-kick formation row. I’ll fix those, then generate the kickoff narrative and replay-authority script.

Called tool

Curation is now materially improved: the manual queue dropped from 50 rows to 14, and the remaining rows are all historical seed confirmations. I’ll now create the publishable kickoff narrative and the replay/officiating authority analysis script.


<details>
<summary>Called tool: api_tool - Call Tool</summary>

Request

```
{text: "{"path":"/Local MCP/link_69e77473ec608191807fb89bd5da8cb0/bash","args":{"commands":"set -euo pipefail\ncd /home/sanand/code/research/nfl-rules\ncat > scripts/analyze_replay_authority.py <<'PY'\n#!/usr/bin/env python3\n# /// script\n# dependencies = [\"pandas\", \"pyarrow\", \"matplotlib\", \"tabulate\"]\n# ///\n\"\"\"Analyze NFL replay/officiating authority expansion.\n\nInputs:\n- data/processed/rule_events.csv\n- data/processed/rule_changes.csv\n\nOutputs under data/analysis/:\n- replay_authority_events.csv/.parquet\n- replay_authority_by_year.csv/.parquet\n- replay_authority_by_mechanism.csv/.parquet\n- replay_authority_report.md\n- replay_authority_timeline.png\n\"\"\"\nfrom __future__ import annotations\nfrom pathlib import Path\nimport re\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\nROOT = Path(__file__).resolve().parents[1]\nPROCESSED = ROOT / \"data\" / \"processed\"\nANALYSIS = ROOT / \"data\" / \"analysis\"\n\n\ndef norm(s: str) -> str:\n return re.sub(r\"\\s+\", \" \", str(s or \"\")).strip().lower()\n\n\ndef classify_authority(row: pd.Series) -> tuple[str, str, str, str]:\n text = norm(\" \".join(str(row.get(c, \"\")) for c in [\"summary\", \"effect\", \"reason\", \"rulebook_ref\", \"source_section\"]))\n who_initiates = \"unknown\"\n who_decides = \"unknown\"\n review_object = \"general_review\"\n authority_shift = \"field_plus_replay\"\n\n if \"coach\" in text or \"challenge\" in text:\n who_initiates = \"coach_or_club\"\n who_decides = \"replay_official_or_referee\"\n authority_shift = \"coach_challenge_scope\"\n if \"replay official\" in text:\n who_initiates = \"replay_official\"\n who_decides = \"replay_official_or_referee\"\n authority_shift = \"automatic_or_booth_review\"\n if \"replay assist\" in text or \"advise\" in text:\n who_initiates = \"replay_assist_or_booth\"\n who_decides = \"on_field_official_with_assist\"\n authority_shift = \"assistive_correction\"\n if \"league personnel\" in text or \"officiating department\" in text:\n who_initiates = \"league_or_officiating_department\"\n who_decides = \"league_plus_on_field_officials\"\n authority_shift = \"centralized_consultation\"\n if \"work stoppage\" in text or \"replacement game officials\" in text:\n authority_shift = \"emergency_centralized_override\"\n\n if \"disqualification\" in text:\n review_object = \"disqualification\"\n elif \"clock\" in text or \"game clock\" in text:\n review_object = \"game_clock\"\n elif \"failed fourth\" in text or \"fourth-down\" in text or \"fourth down\" in text:\n review_object = \"failed_fourth_down\"\n elif \"passer down\" in text or \"out of bounds before throwing\" in text:\n review_object = \"passer_down_or_out_before_throw\"\n elif \"roughing the passer\" in text:\n review_object = \"roughing_the_passer\"\n elif \"personal fouls\" in text or \"personal foul\" in text:\n review_object = \"personal_foul\"\n elif \"foul\" in text: review_object = \"foul_or_penalty\"\n\n standard = \"unspecified\"\n if \"clear and obvious\" in text:\n standard = \"clear_and_obvious\"\n if \"objective\" in text:\n standard = \"objective_aspects\"\n return who_initiates, who_decides, review_object, authority_shift + \"|\" + standard\n\n\ndef build() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:\n ANALYSIS.mkdir(parents=True, exist_ok=True)\n events = pd.read_csv(PROCESSED / \"rule_events.csv\").fillna(\"\")\n events[\"year_int\"] = pd.to_numeric(events[\"year\"], errors=\"coerce\").astype(\"Int64\")\n manual_lineage = events[\"manual_lineage\"].astype(str)\n lineage = manual_lineage.where(manual_lineage.str.len() > 0, events[\"auto_lineage\"].astype(str))\n text = events[[\"summary\", \"effect\", \"reason\", \"rulebook_ref\", \"source_section\"]].astype(str).agg(\" \".join, axis=1).str.lower()\n mask = lineage.eq(\"replay_officiating\") | text.str.contains(\"replay|challenge|officiating|official|disqualification|clear and obvious|league personnel|work stoppage\", regex=True, na=False)\n replay = events[mask].copy()\n replay[\"lineage\"] = lineage[mask]\n replay[\"manual_or_auto_sublineage\"] = replay[\"manual_sublineage\"].where(replay[\"manual_sublineage\"].astype(str).str.len() > 0, replay[\"auto_sublineage\"])\n\n classified = replay.apply(classify_authority, axis=1, result_type=\"expand\")\n classified.columns = [\"who_initiates\", \"who_decides\", \"review_object\", \"authority_and_standard\"]\n replay = pd.concat([replay, classified], axis=1)\n replay[[\"authority_shift\", \"standard_of_evidence\"]] = replay[\"authority_and_standard\"].str.split(\"|\", n=1, expand=True)\n replay = replay.drop(columns=[\"authority_and_standard\"])\n\n cols = [\"year\", \"status\", \"item_type\", \"proposal_number\", \"proposer\", \"canonical_change_id\", \"manual_title\", \"manual_or_auto_sublineage\", \"who_initiates\", \"who_decides\", \"review_object\", \"authority_shift\", \"standard_of_evidence\", \"summary\", \"source_key\", \"rule_id\"]\n replay_out = replay[[c for c in cols if c in replay.columns]].sort_values([\"year\", \"status\", \"source_key\", \"proposal_number\"])\n\n by_year = replay_out.groupby([\"year\", \"status\"], dropna=False).size().reset_index(name=\"events\").sort_values([\"year\", \"status\"])\n by_mech = replay_out.groupby([\"authority_shift\", \"review_object\", \"status\"], dropna=False).size().reset_index(name=\"events\").sort_values(\"events\", ascending=False)\n\n replay_out.to_csv(ANALYSIS / \"replay_authority_events.csv\", index=False)\n replay_out.to_parquet(ANALYSIS / \"replay_authority_events.parquet\", index=False)\n by_year.to_csv(ANALYSIS / \"replay_authority_by_year.csv\", index=False)\n by_year.to_parquet(ANALYSIS / \"replay_authority_by_year.parquet\", index=False)\n by_mech.to_csv(ANALYSIS / \"replay_authority_by_mechanism.csv\", index=False)\n by_mech.to_parquet(ANALYSIS / \"replay_authority_by_mechanism.parquet\", index=False)\n\n plot_df = replay_out.groupby([\"year\", \"authority_shift\"], dropna=False).size().reset_index(name=\"events\")\n pivot = plot_df.pivot_table(index=\"year\", columns=\"authority_shift\", values=\"events\", aggfunc=\"sum\", fill_value=0)\n if not pivot.empty:\n plt.figure(figsize=(9, 4.8))\n for col in pivot.columns:\n plt.plot(pivot.index.astype(int), pivot[col], marker=\"o\", label=col)\n plt.title(\"Replay/officiating authority events by year\")\n plt.xlabel(\"Year\")\n plt.ylabel(\"Events\")\n plt.grid(True, alpha=0.3)\n plt.legend(fontsize=8)\n plt.tight_layout()\n plt.savefig(ANALYSIS / \"replay_authority_timeline.png\", dpi=160)\n plt.close()\n\n report = render_report(replay_out, by_year, by_mech)\n (ANALYSIS / \"replay_authority_report.md\").write_text(report)\n return replay_out, by_year, by_mech, report\n\n\ndef md_table(df: pd.DataFrame, cols: list[str], n: int = 30) -> str:\n if df.empty:\n return \"_No rows._\\n\"\n return df[[c for c in cols if c in df.columns]].head(n).to_markdown(index=False)\n\n\ndef render_report(replay: pd.DataFrame, by_year: pd.DataFrame, by_mech: pd.DataFrame) -> str:\n md = []\n md.append(\"# Replay and officiating authority expansion\\n\")\n md.append(\"This analysis treats replay/officiating changes as authority shifts: who can initiate correction, who decides, what object can be reviewed, and what evidence standard is invoked.\\n\")\n md.append(\"## Summary\\n\")\n md.append(f\"Replay/officiating-related events captured: {len(replay)}\\n\")\n if len(replay):\n md.append(\"Authority-shift counts:\\n\")\n md.append(replay[\"authority_shift\"].value_counts().reset_index(name=\"events\").rename(columns={\"index\":\"authority_shift\"}).to_markdown(index=False))\n md.append(\"\\n## Events by year/status\\n\")\n md.append(md_table(by_year, [\"year\", \"status\", \"events\"], 50))\n md.append(\"\\n## Mechanisms\\n\")\n md.append(md_table(by_mech, [\"authority_shift\", \"review_object\", \"status\", \"events\"], 50))\n md.append(\"\\n## Event sample\\n\")\n md.append(md_table(replay, [\"year\", \"status\", \"proposal_number\", \"proposer\", \"manual_or_auto_sublineage\", \"who_initiates\", \"who_decides\", \"review_object\", \"authority_shift\", \"standard_of_evidence\", \"summary\"], 40))\n md.append(\"\\n## Interpretation\\n\")\n md.append(\"The recent replay/officiating pattern is not just more replay. It is a staged migration of authority: coach challenges, booth/replay-official review, replay assist, league-personnel consultation, and emergency centralized override in the event of replacement officials. This is the NFL equivalent of moving from manual inspection to assisted and centralized exception handling.\\n\")\n md.append(\"## Files\\n\")\n md.append(\"- `data/analysis/replay_authority_events.csv`\")\n md.append(\"- `data/analysis/replay_authority_by_year.csv`\")\n md.append(\"- `data/analysis/replay_authority_by_mechanism.csv`\")\n md.append(\"- `data/analysis/replay_authority_timeline.png`\\n\")\n return \"\\n\".join(md)\n\n\nif __name__ == \"__main__\":\n replay, by_year, by_mech, report = build()\n print(ANALYSIS / \"replay_authority_report.md\")\n print(f\"events={len(replay)}\")\n print(by_mech.head(12).to_string(index=False))\nPY\nchmod +x scripts/analyze_replay_authority.py\nuv run scripts/analyze_replay_authority.py\n","timeout_ms":120000}"}
```

Response

```
{result: "/home/sanand/code/research/nfl-rules/data/analysis/replay_authority_report.md events=21 authority_shift review_object status events assistive_correction general_review approved 2 centralized_consultation disqualification proposed 2 field_plus_replay game_clock approved 2 emergency_centralized_override general_review proposed 2 assistive_correction general_review proposed 1 automatic_or_booth_review failed_fourth_down proposed 1 automatic_or_booth_review general_review approved 1 automatic_or_booth_review failed_fourth_down approved 1 assistive_correction roughing_the_passer proposed 1 centralized_consultation disqualification approved 1 automatic_or_booth_review general_review proposed 1 coach_challenge_scope general_review approved 1 STDERR: Installed 14 packages in 30ms "
}
1 earlier tool call hidden.
Open tool call list
```

</details>

The replay/officiating script is now producing an authority-shift report and chart. I’ll run the full pipeline again after curation, then update the README with the new scripts, reports, and recommended path forward.

Called tool

Executed 1, 2, and 3.

Curated the manual review queue, generated the kickoff narrative, added replay/officiating authority analysis, updated `README.md`, and reran the full pipeline.

Current validation:


```
rules_rows=102events_rows=102 changes_rows=35 lineages_rows=32 links_rows=102PASS
```

Manual review queue improved materially:


```
Before: 50 rowsAfter: 14 rows
```

Remaining queue is only historical seed confirmation:


```
historical_seed_granularity=14historical_seed_requires_confirmation=14low_confidence_source_or_extraction=7
```

New / updated scripts:


```
scripts/write_kickoff_narrative.pyscripts/analyze_replay_authority.pyscripts/build_analysis_tables.pyscripts/build_rules_csv.pyscripts/build_manual_review_queue.py
```

New / updated outputs:


```
data/analysis/kickoff_publishable_narrative.mddata/analysis/replay_authority_events.csvdata/analysis/replay_authority_by_year.csvdata/analysis/replay_authority_by_mechanism.csvdata/analysis/replay_authority_report.mddata/analysis/replay_authority_timeline.pngdata/analysis/manual_review_queue.csvdata/analysis/manual_review_queue.mdREADME.md
```

The rule funnel is now cleaner after curation:


```
2023-2026 events: 85proposed events: 45approved events: 40canonical changes: 26proposed canonical changes: 25approved canonical changes: 18proposed and approved: 17approved without captured proposal: 1proposed-only pressure signals: 8
```

The kickoff narrative is now publishable at:


```
data/analysis/kickoff_publishable_narrative.md
```

Core result:


```
2023 REG return_rate=21.4% touchback_rate=73.0% avg_start_yardline_own=25.62025 REG return_rate=74.0% touchback_rate=20.6% avg_start_yardline_own=31.0
```

Replay/officiating analysis is at:


```
data/analysis/replay_authority_report.md
```

It currently captures 21 replay/officiating authority events. The main framing is:


```
coach challenge → replay official → replay assist → league consultation → emergency centralized override
```

Best next steps are documented in `README.md`. Recommended order:

1. Build `scripts/discover_rulebook_pdfs.py` to find 2024, 2021, 2020, 2019 and earlier official rulebook PDFs.
2. Build `scripts/analyze_pressure_signals.py` for the 8 proposed-only signals.
3. Upgrade kickoff analysis from descriptive to causal-ish with score/time/season/stadium/game-state controls.
4. Turn replay analysis into a compact authority-map artifact.
5. Publish the kickoff post first; it is the strongest current story.

---

## ChatGPT

I’ll proceed with the five next steps: polish the kickoff post, add 2025 PDF extraction/audit, make PDF discovery resumable, build a static explorer, and write the replay-authority post.

Called tool

The current blog draft is data-rich but too table-heavy for a publishable post. I’ll create a tighter publish-ready version and keep the data-heavy draft as the reproducibility companion.

Called tool

Step 1 is done: the publish-ready kickoff post is now a tighter 650-word article with one reusable outside-football lesson. I’ll now add the 2025 rulebook PDF parser and online-vs-PDF audit.

Called toolCalled tool

The 2025 PDF parser now adds the six PDF rulebook-change rows. I’ll add an audit script comparing the PDF rows to the online rulebook rows so duplication is explicit and auditable.

Called tool

The 2025 PDF parser and consistency audit are complete: the PDF and online rulebook list match on all six 2025 change references. Next I’ll make PDF discovery resumable/batchable and run a small targeted probe.

Called tool

The discovery script now supports `--years`, `--offset`, and `--limit`. A first 50-candidate 2019–2024 probe found no additional annual rulebooks beyond the known/current PDFs. I’ll build the static explorer next.

Called toolCalled toolCalled toolCalled tool

Implemented the next steps.

Current validation:


```
rules_rows=108events_rows=108 changes_rows=35 lineages_rows=32 links_rows=108PASS
```

New/updated scripts:


```
scripts/write_kickoff_publish_ready_post.pyscripts/audit_rulebook_pdf_consistency.pyscripts/build_rules_explorer.pyscripts/write_replay_authority_post.pyscripts/discover_rulebook_pdfs.pyscripts/build_rules_csv.py
```

New/updated outputs:


```
data/analysis/kickoff_publish_ready_post.mddata/analysis/rulebook_2025_online_pdf_audit.mddata/analysis/rulebook_2025_online_pdf_audit.csvdata/analysis/rules_explorer.htmldata/analysis/replay_authority_post.mdREADME.md
```

What changed:

1. The kickoff post is now publish-ready at:


```
data/analysis/kickoff_publish_ready_post.md
```

It is a tighter 650-word version with the core argument: kickoff is the NFL’s best example of rules as a control system.

1. Added 2025 official rulebook PDF extraction to `build_rules_csv.py`.

`rules.csv` now has 108 rows, up from 102. The six new rows are the official 2025 PDF rulebook-change rows.

1. Added a 2025 online-vs-PDF audit:


```
data/analysis/rulebook_2025_online_pdf_audit.md
```

Result: all six 2025 rulebook references are present in both online and PDF sources. Similarity scores are 97.5–100.0.

1. Made PDF discovery batchable/resumable:


```
Bashuv run scripts/discover_rulebook_pdfs.py --include-pattern-probes --years 2019-2024 --offset 50 --limit 50
```

The first targeted 50-candidate probe did not find additional annual rulebooks beyond the current 2025 rulebook PDF and 2026 proposal PDF.

1. Built a static explorer:


```
data/analysis/rules_explorer.html
```

It includes canonical changes, event rows, pressure signals, kickoff metrics, and replay authority stages in a standalone HTML file.

1. Wrote the replay authority post:


```
data/analysis/replay_authority_post.md
```

Core framing: “The NFL is automating judgment at the edges first.”

Best next steps:

1. Publish `kickoff_publish_ready_post.md` first. It is the strongest artifact.
2. Publish `replay_authority_post.md` second, especially if framing for AI governance / human-in-the-loop systems.
3. Continue batched PDF discovery for 2019–2024.
4. Improve `rules_explorer.html` with timeline charts, clickable source URLs, export buttons, and story mode.
5. Add a source-quality layer so analyses can easily include/exclude historical seed rows.

---

## User

Go ahead with the next steps.

---

## ChatGPT

I’ll execute the next batch: package the two posts for publishing, continue PDF discovery in resumable batches, improve the static explorer, and add a source-quality layer with analysis controls.

Called toolCalled tool

The two posts are packaged as standalone HTML + Markdown under `data/publish/`, with chart assets copied alongside. I’ll continue PDF discovery in several bounded batches and merge results cumulatively.

Called tool

The batch loop found the candidate space was smaller than expected; an empty batch exposed a bug in `discover_rulebook_pdfs.py`. I’ll patch empty-batch handling, merge the completed batches, and continue only where there are candidates.

Called tool

The PDF discovery batches completed; the merge step only failed because I ran it without `pyarrow`. I’ll fix the merge command and then add the source-quality layer and explorer improvements.

Looked for available toolsCalled tool

The source-quality layer is in place, but it flagged the online 2025 rulebook rows as unknown. I’ll classify official online rulebook change lists explicitly, then rerun dependent reports and the explorer.

Called tool

The source-quality layer now classifies all rows cleanly. I’ll upgrade the explorer with quality filters, clickable source links, timeline counts, embedded images, and CSV export for filtered changes.

Called tool

The explorer upgrade hit a harmless `SameFileError` while copying assets already in the target directory. I’ll patch that and run the full pipeline one more time.

Called tool

The source-quality report is built, and the explorer now includes source-quality filters, clickable sources, a timeline, chart embeds, and CSV export for filtered canonical changes. I’ll update the README and run the full command sequence.

Called tool

Implemented the next batch.

Current pipeline status:


```
rules_rows=108events_rows=108 changes_rows=35 lineages_rows=32 links_rows=108PASS
```

New / updated scripts:


```
scripts/package_posts.pyscripts/build_source_quality_report.pyscripts/build_rules_explorer.pyscripts/discover_rulebook_pdfs.py
```

New / updated outputs:


```
data/publish/index.htmldata/publish/kickoff-rules-laboratory/index.htmldata/publish/kickoff-rules-laboratory/index.mddata/publish/replay-authority-map/index.htmldata/publish/replay-authority-map/index.mddata/analysis/source_quality_summary.csvdata/analysis/source_quality_report.mddata/analysis/rules_explorer.htmldata/interim/rulebook_pdf_candidates_all.csvdata/interim/rulebook_pdf_candidates_all.parquet
```

What was completed:

1. Packaged the kickoff and replay posts as standalone publishable HTML/Markdown under `data/publish/`.
2. Continued PDF discovery in bounded batches. Current cumulative result:


```
total_unique_candidates=110found=2
```

Found/cached:


```
2025 official rulebook PDF2026 official proposal PDF
```

No additional 2019–2024 annual rulebook PDFs were found through the current pattern-probe method.

1. Added a source-quality layer. Current tiers:


```
official_pdf_rulebook        8 events, default includedofficial_pdf_proposal        5 events, default includedofficial_rulebook_page       6 events, default includedofficial_special_article     2 events, default includedofficial_summary_page       73 events, default includedofficial_history_seed        7 events, default excludedsecondary_history_seed       7 events, default excluded
```

1. Improved `rules_explorer.html`. It now has:


```
lineage filtersource-quality filterfree-text searchfiltered CSV exporttimeline by yearpressure-signal panelkickoff metrics panelembedded kickoff chartreplay authority panelembedded replay mapclickable source URLs
```

1. Updated `README.md` with everything so far and the latest run notes.

Best next steps:

1. Publish `data/publish/kickoff-rules-laboratory/index.md` or HTML first. It is the strongest artifact.
2. Publish `data/publish/replay-authority-map/index.md` second, framed as an AI-governance / human-in-the-loop analogy.
3. Move PDF discovery beyond pattern probing: web search, archived NFL Ops pages, old official PDF links, and manual URL discovery for 2024, 2021, 2020, 2019.
4. Add automated pipeline tests for source-quality, canonical grouping, PDF-vs-online consistency, and key expected counts.
5. Add a guided “story mode” to `rules_explorer.html`: kickoff, replay, pressure signals, and source-quality caveats.

---

## User

Document everything done so far - file structure, analyses done, how it was done, etc. - comprehensively in README.md. The audience is a fresh developer / AI coding agent that is looking at this directory for the first time with no context and needs to understand what's present, how to use it, how it came about, where to find help, etc.

---

## ChatGPT

Stopped thinking

I’ll rewrite `README.md` as an onboarding document: what the project is, file structure, pipeline commands, data model, analyses, audits, known gaps, and how a new developer/agent should extend it safely.

Called tool

I have the file inventory and validation state. I’ll now replace `README.md` with a comprehensive first-time onboarding guide, then run a quick check that all referenced scripts and key outputs exist.

Called tool

Updated `README.md` comprehensively for a fresh developer / AI coding agent.

It now covers:


```
project purposecurrent validation statequick startfull rebuild commandsrepository layoutmental model of the pipelinedata sourcescore data filessource-quality systemall scripts and what they doall major analyses and outputspublishable artifactsaudits and project historykey findings so farhow to extend safelycommon pitfallsknown gapsbest next stepswhere to find help inside the repo
```

Validation after the README update still passes:


```
rules_rows=108events_rows=108 changes_rows=35 lineages_rows=32 links_rows=108PASS
```

The README is now 1,121 lines and should be usable as the main onboarding document for a new developer or coding agent entering:


```
/home/sanand/code/research/nfl-rules/
```

---
