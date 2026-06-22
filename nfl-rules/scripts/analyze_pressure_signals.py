#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "tabulate"]
# ///
"""Rank proposed-only NFL rule-change pressure signals.

Inputs:
- data/analysis/rule_funnel_pressure_signals.csv
- data/processed/rule_events.csv

Outputs:
- data/analysis/pressure_signals_ranked.csv/.parquet
- data/analysis/pressure_signals_report.md
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis"
PROCESSED = ROOT / "data" / "processed"

HIGH_SIGNAL_LINEAGES = {
    "kickoff", "replay_officiating", "player_safety_contact", "offense_defense_balance",
    "offensive_strategy", "competitive_equity", "penalty_enforcement", "special_teams"
}
STRATEGIC_TERMS = ["tush", "pushing", "snapper", "automatic first down", "defensive holding", "illegal contact", "4th-and-20", "onside", "wild card", "division champions", "draft selections"]
MEASURABLE_TERMS = ["yard", "touchback", "kickoff", "penalty", "first down", "record", "replay", "challenge", "draft", "seeding", "overtime"]


def score(row: pd.Series) -> tuple[int, list[str]]:
    s = 0
    reasons: list[str] = []
    lineage = str(row.get("lineage", ""))
    text = " ".join(str(row.get(c, "")) for c in ["canonical_change_id", "title_or_summary", "proposers", "sublineage"]).lower()
    proposed_events = int(row.get("proposed_events", 0) or 0)
    s += proposed_events * 2
    if proposed_events > 1:
        reasons.append("multiple proposed events")
    if lineage in HIGH_SIGNAL_LINEAGES:
        s += 3
        reasons.append(f"high-signal lineage: {lineage}")
    if any(t in text for t in STRATEGIC_TERMS):
        s += 3
        reasons.append("strategic exploit or structural pressure")
    if any(t in text for t in MEASURABLE_TERMS):
        s += 2
        reasons.append("clear measurable outcome")
    if "competition committee" in text:
        s += 2
        reasons.append("competition committee involvement")
    if ";" in str(row.get("proposers", "")):
        s += 1
        reasons.append("multiple proposers")
    if int(row.get("first_year", 0) or 0) >= 2025:
        s += 1
        reasons.append("recent signal")
    return s, reasons


def main() -> None:
    pressure = pd.read_csv(ANALYSIS / "rule_funnel_pressure_signals.csv").fillna("")
    events = pd.read_csv(PROCESSED / "rule_events.csv").fillna("")
    rows=[]
    for _, r in pressure.iterrows():
        sc, reasons = score(r)
        ev = events[events["canonical_change_id"].eq(r["canonical_change_id"])]
        rows.append({
            **r.to_dict(),
            "signal_score": sc,
            "signal_reasons": "; ".join(reasons),
            "event_summaries": " || ".join(ev["summary"].astype(str).head(5)),
            "recommended_tracking_metric": recommend_metric(str(r.get("lineage", "")), str(r.get("title_or_summary", ""))),
            "recommended_next_research": recommend_next(str(r.get("lineage", "")), str(r.get("title_or_summary", "")))
        })
    ranked = pd.DataFrame(rows).sort_values(["signal_score", "first_year", "canonical_change_id"], ascending=[False, False, True]) if rows else pd.DataFrame()
    ranked.to_csv(ANALYSIS / "pressure_signals_ranked.csv", index=False)
    ranked.to_parquet(ANALYSIS / "pressure_signals_ranked.parquet", index=False)
    report = render(ranked)
    (ANALYSIS / "pressure_signals_report.md").write_text(report)
    print(ANALYSIS / "pressure_signals_report.md")
    print(f"signals={len(ranked)}")
    if len(ranked): print(ranked[["canonical_change_id","lineage","sublineage","first_year","signal_score","signal_reasons"]].to_string(index=False))


def recommend_metric(lineage: str, title: str) -> str:
    text=(lineage+" "+title).lower()
    if "kickoff" in text or "onside" in text: return "onside attempt rate, success rate, comeback win probability"
    if "tush" in text or "pushing" in text: return "short-yardage success rate, injury reports, defensive penalty rate"
    if "automatic first down" in text or "defensive holding" in text: return "EPA swing by penalty type, automatic-first-down conversion impact"
    if "playoff" in text or "wild card" in text: return "seeding inversions, home-field allocation, win-probability fairness"
    if "draft" in text: return "trade volume by future-year horizon, pick valuation volatility"
    if "punt" in text: return "punt touchback rate, coffin-corner rate, post-punt starting field position"
    return "event recurrence, proposer recurrence, and measurable game/club impact"


def recommend_next(lineage: str, title: str) -> str:
    text=(lineage+" "+title).lower()
    if "kickoff" in text: return "Compare with 2026 kickoff/on-side changes and nflverse late-game kickoff outcomes."
    if "replay" in text: return "Map to replay-authority framework and check if later Competition Committee proposals absorb club ideas."
    if "player_safety" in text or "tush" in text: return "Track injury/safety rhetoric and whether Competition Committee adopts a softened version."
    if "competitive" in text or "playoff" in text: return "Simulate past seasons to count teams affected by this seeding rule."
    return "Track recurrence in future proposals and whether the idea reappears in modified form."


def render(ranked: pd.DataFrame) -> str:
    md=["# Proposed-only pressure signals\n"]
    md.append("These are proposed rule changes with no captured approval in the current dataset. They are useful as indicators of latent stress in the game or league operations.\n")
    md.append(f"Signals ranked: {len(ranked)}\n")
    if len(ranked):
        cols=["canonical_change_id","lineage","sublineage","first_year","signal_score","signal_reasons","recommended_tracking_metric","title_or_summary"]
        md.append(ranked[[c for c in cols if c in ranked.columns]].to_markdown(index=False))
    md.append("\n## How to use\n")
    md.append("The highest-scoring signals should be watched in future annual proposal pages. If a club proposal later appears as a Competition Committee proposal, it is evidence that the issue moved from local pain point to league-recognized governance problem.\n")
    return "\n".join(md)+"\n"

if __name__ == "__main__":
    main()
