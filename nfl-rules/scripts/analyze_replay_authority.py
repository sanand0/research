#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "matplotlib", "tabulate"]
# ///
"""Analyze NFL replay/officiating authority expansion.

Inputs:
- data/processed/rule_events.csv
- data/processed/rule_changes.csv

Outputs under data/analysis/:
- replay_authority_events.csv/.parquet
- replay_authority_by_year.csv/.parquet
- replay_authority_by_mechanism.csv/.parquet
- replay_authority_report.md
- replay_authority_timeline.png
"""
from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ANALYSIS = ROOT / "data" / "analysis"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def classify_authority(row: pd.Series) -> tuple[str, str, str, str]:
    text = norm(" ".join(str(row.get(c, "")) for c in ["summary", "effect", "reason", "rulebook_ref", "source_section"]))
    who_initiates = "unknown"
    who_decides = "unknown"
    review_object = "general_review"
    authority_shift = "field_plus_replay"

    if "coach" in text or "challenge" in text:
        who_initiates = "coach_or_club"
        who_decides = "replay_official_or_referee"
        authority_shift = "coach_challenge_scope"
    if "replay official" in text:
        who_initiates = "replay_official"
        who_decides = "replay_official_or_referee"
        authority_shift = "automatic_or_booth_review"
    if "replay assist" in text or "advise" in text:
        who_initiates = "replay_assist_or_booth"
        who_decides = "on_field_official_with_assist"
        authority_shift = "assistive_correction"
    if "league personnel" in text or "officiating department" in text:
        who_initiates = "league_or_officiating_department"
        who_decides = "league_plus_on_field_officials"
        authority_shift = "centralized_consultation"
    if "work stoppage" in text or "replacement game officials" in text:
        authority_shift = "emergency_centralized_override"

    if "disqualification" in text:
        review_object = "disqualification"
    elif "clock" in text or "game clock" in text:
        review_object = "game_clock"
    elif "failed fourth" in text or "fourth-down" in text or "fourth down" in text:
        review_object = "failed_fourth_down"
    elif "passer down" in text or "out of bounds before throwing" in text:
        review_object = "passer_down_or_out_before_throw"
    elif "roughing the passer" in text:
        review_object = "roughing_the_passer"
    elif "personal fouls" in text or "personal foul" in text:
        review_object = "personal_foul"
    elif "foul" in text:
        review_object = "foul_or_penalty"

    standard = "unspecified"
    if "clear and obvious" in text:
        standard = "clear_and_obvious"
    if "objective" in text:
        standard = "objective_aspects"
    return who_initiates, who_decides, review_object, authority_shift + "|" + standard


def build() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    events = pd.read_csv(PROCESSED / "rule_events.csv").fillna("")
    events["year_int"] = pd.to_numeric(events["year"], errors="coerce").astype("Int64")
    manual_lineage = events["manual_lineage"].astype(str)
    lineage = manual_lineage.where(manual_lineage.str.len() > 0, events["auto_lineage"].astype(str))
    text = events[["summary", "effect", "reason", "rulebook_ref", "source_section"]].astype(str).agg(" ".join, axis=1).str.lower()
    mask = lineage.eq("replay_officiating") | text.str.contains("replay|challenge|officiating|official|disqualification|clear and obvious|league personnel|work stoppage", regex=True, na=False)
    replay = events[mask].copy()
    replay["lineage"] = lineage[mask]
    replay["manual_or_auto_sublineage"] = replay["manual_sublineage"].where(replay["manual_sublineage"].astype(str).str.len() > 0, replay["auto_sublineage"])

    classified = replay.apply(classify_authority, axis=1, result_type="expand")
    classified.columns = ["who_initiates", "who_decides", "review_object", "authority_and_standard"]
    replay = pd.concat([replay, classified], axis=1)
    replay[["authority_shift", "standard_of_evidence"]] = replay["authority_and_standard"].str.split("|", n=1, expand=True)
    replay = replay.drop(columns=["authority_and_standard"])

    cols = ["year", "status", "item_type", "proposal_number", "proposer", "canonical_change_id", "manual_title", "manual_or_auto_sublineage", "who_initiates", "who_decides", "review_object", "authority_shift", "standard_of_evidence", "summary", "source_key", "rule_id"]
    replay_out = replay[[c for c in cols if c in replay.columns]].sort_values(["year", "status", "source_key", "proposal_number"])

    by_year = replay_out.groupby(["year", "status"], dropna=False).size().reset_index(name="events").sort_values(["year", "status"])
    by_mech = replay_out.groupby(["authority_shift", "review_object", "status"], dropna=False).size().reset_index(name="events").sort_values("events", ascending=False)

    replay_out.to_csv(ANALYSIS / "replay_authority_events.csv", index=False)
    replay_out.to_parquet(ANALYSIS / "replay_authority_events.parquet", index=False)
    by_year.to_csv(ANALYSIS / "replay_authority_by_year.csv", index=False)
    by_year.to_parquet(ANALYSIS / "replay_authority_by_year.parquet", index=False)
    by_mech.to_csv(ANALYSIS / "replay_authority_by_mechanism.csv", index=False)
    by_mech.to_parquet(ANALYSIS / "replay_authority_by_mechanism.parquet", index=False)

    plot_df = replay_out.groupby(["year", "authority_shift"], dropna=False).size().reset_index(name="events")
    pivot = plot_df.pivot_table(index="year", columns="authority_shift", values="events", aggfunc="sum", fill_value=0)
    if not pivot.empty:
        plt.figure(figsize=(9, 4.8))
        for col in pivot.columns:
            plt.plot(pivot.index.astype(int), pivot[col], marker="o", label=col)
        plt.title("Replay/officiating authority events by year")
        plt.xlabel("Year")
        plt.ylabel("Events")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(ANALYSIS / "replay_authority_timeline.png", dpi=160)
        plt.close()

    report = render_report(replay_out, by_year, by_mech)
    (ANALYSIS / "replay_authority_report.md").write_text(report)
    return replay_out, by_year, by_mech, report


def md_table(df: pd.DataFrame, cols: list[str], n: int = 30) -> str:
    if df.empty:
        return "_No rows._\n"
    return df[[c for c in cols if c in df.columns]].head(n).to_markdown(index=False)


def render_report(replay: pd.DataFrame, by_year: pd.DataFrame, by_mech: pd.DataFrame) -> str:
    md = []
    md.append("# Replay and officiating authority expansion\n")
    md.append("This analysis treats replay/officiating changes as authority shifts: who can initiate correction, who decides, what object can be reviewed, and what evidence standard is invoked.\n")
    md.append("## Summary\n")
    md.append(f"Replay/officiating-related events captured: {len(replay)}\n")
    if len(replay):
        md.append("Authority-shift counts:\n")
        md.append(replay["authority_shift"].value_counts().reset_index(name="events").rename(columns={"index":"authority_shift"}).to_markdown(index=False))
    md.append("\n## Events by year/status\n")
    md.append(md_table(by_year, ["year", "status", "events"], 50))
    md.append("\n## Mechanisms\n")
    md.append(md_table(by_mech, ["authority_shift", "review_object", "status", "events"], 50))
    md.append("\n## Event sample\n")
    md.append(md_table(replay, ["year", "status", "proposal_number", "proposer", "manual_or_auto_sublineage", "who_initiates", "who_decides", "review_object", "authority_shift", "standard_of_evidence", "summary"], 40))
    md.append("\n## Interpretation\n")
    md.append("The recent replay/officiating pattern is not just more replay. It is a staged migration of authority: coach challenges, booth/replay-official review, replay assist, league-personnel consultation, and emergency centralized override in the event of replacement officials. This is the NFL equivalent of moving from manual inspection to assisted and centralized exception handling.\n")
    md.append("## Files\n")
    md.append("- `data/analysis/replay_authority_events.csv`")
    md.append("- `data/analysis/replay_authority_by_year.csv`")
    md.append("- `data/analysis/replay_authority_by_mechanism.csv`")
    md.append("- `data/analysis/replay_authority_timeline.png`\n")
    return "\n".join(md)


if __name__ == "__main__":
    replay, by_year, by_mech, report = build()
    print(ANALYSIS / "replay_authority_report.md")
    print(f"events={len(replay)}")
    print(by_mech.head(12).to_string(index=False))
