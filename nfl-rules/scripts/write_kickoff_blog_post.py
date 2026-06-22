#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "tabulate"]
# ///
"""Write a polished blog-post style kickoff article.

Inputs:
- data/analysis/kickoff_pbp_summary_by_season_type.csv
- data/analysis/kickoff_adjusted_by_score_bucket.csv
- data/analysis/kickoff_rule_timeline.csv

Output:
- data/analysis/kickoff_blog_post.md
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/"data"/"analysis"
OUT=ANALYSIS/"kickoff_blog_post.md"

def pct(x): return f"{float(x)*100:.1f}%"
def own(x): return f"own {float(x):.1f}"

def main():
    summary=pd.read_csv(ANALYSIS/"kickoff_pbp_summary_by_season_type.csv")
    reg=summary[summary.season_type.astype(str).eq("REG")].copy().sort_values("season")
    score=pd.read_csv(ANALYSIS/"kickoff_adjusted_by_score_bucket.csv")
    scorereg=score[score.season_type.astype(str).eq("REG")].copy()
    timeline=pd.read_csv(ANALYSIS/"kickoff_rule_timeline.csv").fillna("")
    def v(year,col): return float(reg.loc[reg.season.eq(year), col].iloc[0])
    table=reg[["season","kickoffs","return_rate","touchback_rate","fair_catch_rate","onside_attempt_rate","avg_start_yardline_own","penalty_rate"]].copy()
    for c in ["return_rate","touchback_rate","fair_catch_rate","onside_attempt_rate","penalty_rate"]:
        table[c]=table[c].map(pct)
    table["avg_start_yardline_own"]=table["avg_start_yardline_own"].map(lambda x:f"{x:.1f}")
    ordinary=scorereg[scorereg.score_bucket.isin(["trailing_1_7","tied","leading_1_7"])]
    ordinary_table=ordinary[["season","score_bucket","kickoffs","return_rate","touchback_rate","avg_start_yardline_own"]].copy()
    for c in ["return_rate","touchback_rate"]: ordinary_table[c]=ordinary_table[c].map(pct)
    ordinary_table["avg_start_yardline_own"]=ordinary_table["avg_start_yardline_own"].map(lambda x:f"{x:.1f}")
    rules=timeline[timeline.year.astype(str).isin(["2022","2023","2024","2025","2026"])][["year","status","canonical_change_id","summary"]].drop_duplicates().head(25)
    md=[]
    md.append("# Kickoff is the NFL's rules laboratory\n")
    md.append("The NFL did not merely change the kickoff. It ran a live governance experiment in public.\n")
    md.append("Kickoff is where the league's rulemaking problem is easiest to see. The league wants fewer high-speed collisions, but not a dead play. It wants more returns, but not cheap field position. It wants comeback equity, but not chaos. So it keeps turning knobs: touchback incentives, alignment zones, onside-kick declarations, landing zones, K-Balls, and out-of-bounds penalties.\n")
    md.append("The result looks less like a law book and more like a control system.\n")
    md.append("## The big swing\n")
    md.append(f"In 2023, only {pct(v(2023,'return_rate'))} of regular-season kickoffs were returned. Touchbacks were {pct(v(2023,'touchback_rate'))}. By 2025, returns jumped to {pct(v(2025,'return_rate'))}, while touchbacks fell to {pct(v(2025,'touchback_rate'))}.\n")
    md.append(f"The price was field position. Estimated average starting field position after kickoffs moved from {own(v(2023,'avg_start_yardline_own'))} in 2023 to {own(v(2025,'avg_start_yardline_own'))} in 2025. The league bought live returns by giving offenses more favorable starts.\n")
    md.append("![Kickoff return and touchback rates](kickoff_return_touchback_rates.png)\n")
    md.append("![Starting field position after kickoffs](kickoff_starting_field_position.png)\n")
    md.append("## The rule sequence\n")
    md.append("The sequence matters more than any individual rule.\n")
    md.append("- 2022 made a prior free-kick formation change permanent.")
    md.append("- 2023 added a fair-catch/touchback incentive and returns collapsed.")
    md.append("- 2024 trialed the dynamic kickoff to bring returns back without recreating the old collision geometry.")
    md.append("- 2025 made the dynamic kickoff permanent and tuned touchback/setup-zone details.")
    md.append("- 2026 proposals and approvals continue tuning onside-kick and out-of-bounds incentives.\n")
    md.append("That is rulemaking as iterative mechanism design.\n")
    md.append("## Regular-season metrics\n")
    md.append(table.to_markdown(index=False))
    md.append("\n## Not just late-game noise\n")
    md.append("The 2025 return-rate jump is not only an onside-kick or comeback artifact. It is visible in ordinary score states too: tied, one-score trailing, and one-score leading.\n")
    md.append(ordinary_table.to_markdown(index=False))
    md.append("\n![Return rate by score bucket](kickoff_adjusted_return_rate_by_score_bucket.png)\n")
    md.append("## A better way to analyze rules\n")
    md.append("The usual way to read a rule change is: what changed? That misses the point. A better schema is:\n")
    md.append("1. What metric was the league trying to move?")
    md.append("2. What mechanism did it use?")
    md.append("3. What incentive did that create?")
    md.append("4. What second-order effect appeared?")
    md.append("5. What patch came next?\n")
    md.append("Kickoff has all five. The target metrics are safety, return rate, touchback rate, field position, comeback equity, and watchability. The mechanisms are spatial constraints and incentive changes. The patches are already visible in 2025 and 2026.\n")
    md.append("## Rule timeline sample\n")
    md.append(rules.to_markdown(index=False))
    md.append("\n## Caveats\n")
    md.append("This is descriptive, not causal. Starting field position is estimated from the next scrimmage-like play in nflverse play-by-play. Onside success is inferred from which team next takes possession. A stronger causal model should control for score, time, stadium, weather, postseason, and late-game onside contexts.\n")
    md.append("## Reproducibility\n")
    md.append("The analysis is generated by these scripts:\n")
    md.append("```bash")
    md.append("uv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025")
    md.append("uv run scripts/analyze_kickoff_adjusted.py")
    md.append("uv run scripts/write_kickoff_blog_post.py")
    md.append("```\n")
    md.append("Primary outputs used: `kickoff_pbp_summary_by_season_type.csv`, `kickoff_adjusted_by_score_bucket.csv`, `kickoff_rule_timeline.csv`, and the generated PNG charts.\n")
    OUT.write_text("\n".join(md))
    print(OUT)

if __name__ == "__main__": main()
