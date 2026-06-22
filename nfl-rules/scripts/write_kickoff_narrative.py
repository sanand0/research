#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "tabulate"]
# ///
"""Write a short publishable narrative from the kickoff case-study outputs.

Inputs:
- data/analysis/kickoff_rule_timeline.csv
- data/analysis/kickoff_pbp_summary_by_season_type.csv

Output:
- data/analysis/kickoff_publishable_narrative.md
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis"
OUT = ANALYSIS / "kickoff_publishable_narrative.md"


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def read_reg_summary() -> pd.DataFrame:
    df = pd.read_csv(ANALYSIS / "kickoff_pbp_summary_by_season_type.csv")
    reg = df[df["season_type"].astype(str).eq("REG")].copy()
    reg["season"] = reg["season"].astype(int)
    return reg.sort_values("season")


def delta(reg: pd.DataFrame, year1: int, year2: int, col: str) -> float:
    a = float(reg.loc[reg.season.eq(year1), col].iloc[0])
    b = float(reg.loc[reg.season.eq(year2), col].iloc[0])
    return b - a


def value(reg: pd.DataFrame, year: int, col: str) -> float:
    return float(reg.loc[reg.season.eq(year), col].iloc[0])


def main() -> None:
    reg = read_reg_summary()
    timeline = pd.read_csv(ANALYSIS / "kickoff_rule_timeline.csv").fillna("")

    r2021 = value(reg, 2021, "return_rate")
    r2023 = value(reg, 2023, "return_rate")
    r2024 = value(reg, 2024, "return_rate")
    r2025 = value(reg, 2025, "return_rate")
    t2023 = value(reg, 2023, "touchback_rate")
    t2025 = value(reg, 2025, "touchback_rate")
    s2023 = value(reg, 2023, "avg_start_yardline_own")
    s2025 = value(reg, 2025, "avg_start_yardline_own")
    p2025 = value(reg, 2025, "penalty_rate")

    summary_table = reg[[
        "season", "kickoffs", "return_rate", "touchback_rate", "fair_catch_rate", "onside_attempt_rate", "avg_start_yardline_own", "penalty_rate"
    ]].copy()
    for c in ["return_rate", "touchback_rate", "fair_catch_rate", "onside_attempt_rate", "penalty_rate"]:
        summary_table[c] = summary_table[c].map(lambda x: f"{x*100:.1f}%")
    summary_table["avg_start_yardline_own"] = summary_table["avg_start_yardline_own"].map(lambda x: f"{x:.1f}")

    rule_rows = timeline[["year", "status", "canonical_change_id", "auto_sublineage", "summary"]].copy()
    rule_rows = rule_rows[rule_rows["year"].astype(str).isin(["2022", "2023", "2024", "2025", "2026"])]
    rule_rows = rule_rows.drop_duplicates(subset=["year", "canonical_change_id", "summary"]).head(18)

    md = []
    md.append("# Kickoff is the NFL's rules laboratory\n")
    md.append("The NFL's kickoff rules are not a simple safety story. They look more like a live product-control system: change the incentive, measure the result, patch the loophole, and repeat.\n")
    md.append("The clearest signal is the 2021-2025 play-by-play pattern. In the 2023 regular season, only " + pct(r2023) + " of kickoffs were returned, while touchbacks rose to " + pct(t2023) + ". In 2025, after the dynamic kickoff was made permanent and tuned, return rate jumped to " + pct(r2025) + " and touchbacks fell to " + pct(t2025) + ". That is not a marginal adjustment; it is a redesign of the play's operating model.\n")
    md.append("The field-position cost is visible too. Estimated average starting field position after kickoffs moved from the receiving team's own " + f"{s2023:.1f}" + " in 2023 to its own " + f"{s2025:.1f}" + " in 2025. The league appears to have bought more returns and more live plays at the cost of giving offenses better starting position.\n")
    md.append("The 2025 penalty rate is also worth watching. It rose to " + pct(p2025) + " in the regular season, consistent with the idea that new spatial constraints and alignment rules create an adjustment period. This is exactly the kind of hidden cost that a rules-as-control-system analysis should track.\n")

    md.append("## Regular-season kickoff metrics\n")
    md.append(summary_table.to_markdown(index=False))

    md.append("\n## Rule-design sequence\n")
    md.append("The modern sequence is the important part:\n")
    md.append("1. 2022: make a prior free-kick formation change permanent.")
    md.append("2. 2023: add the fair-catch touchback incentive, sharply reducing returns.")
    md.append("3. 2024: trial the dynamic kickoff to restore returns while reducing high-speed collisions.")
    md.append("4. 2025: make the dynamic kickoff permanent and modify touchback/setup-zone details.")
    md.append("5. 2026: continue tuning onside-kick and out-of-bounds incentives.\n")

    md.append("## Rule timeline sample\n")
    md.append(rule_rows.to_markdown(index=False))

    md.append("\n## The non-obvious insight\n")
    md.append("Kickoff is the NFL's best example of governance by iterative mechanism design. The league is not merely deciding whether a play is safe or exciting. It is tuning a multi-objective system: return rate, injury risk, touchback rate, starting field position, onside-kick comeback equity, penalty burden, and viewer excitement.\n")
    md.append("This suggests a broader framework for analyzing rule changes: every rule change should be coded as a control intervention with a target metric, mechanism, expected direction, observed result, and later patch.\n")

    md.append("## Caveats\n")
    md.append("- Starting field position is estimated from the next scrimmage-like play in nflverse play-by-play.")
    md.append("- Onside success is a heuristic based on whether the next offensive team appears to be the kicking team.")
    md.append("- 2026 appears only in the rule timeline; no 2026 play-by-play outcome data is included.")
    md.append("- This is descriptive, not a causal model. A causal design should control for weather, game state, score, stadium, and late-game onside situations.\n")

    md.append("## Files behind this narrative\n")
    md.append("- `data/analysis/kickoff_pbp_summary_by_season_type.csv`")
    md.append("- `data/analysis/kickoff_rule_timeline.csv`")
    md.append("- `data/analysis/kickoff_return_touchback_rates.png`")
    md.append("- `data/analysis/kickoff_starting_field_position.png`\n")

    OUT.write_text("\n".join(md))
    print(OUT)
    print(f"return_rate_2023={pct(r2023)} return_rate_2025={pct(r2025)}")
    print(f"touchback_rate_2023={pct(t2023)} touchback_rate_2025={pct(t2025)}")
    print(f"avg_start_2023={s2023:.1f} avg_start_2025={s2025:.1f}")


if __name__ == "__main__":
    main()
