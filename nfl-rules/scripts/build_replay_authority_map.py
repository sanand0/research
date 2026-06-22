#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "matplotlib", "tabulate"]
# ///
"""Build a compact replay/officiating authority map artifact.

Inputs:
- data/analysis/replay_authority_events.csv

Outputs:
- data/analysis/replay_authority_map.csv/.parquet
- data/analysis/replay_authority_map.md
- data/analysis/replay_authority_map.png
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis"

STAGE_ORDER = [
    "coach_challenge_scope",
    "automatic_or_booth_review",
    "assistive_correction",
    "centralized_consultation",
    "emergency_centralized_override",
    "field_plus_replay",
]
STAGE_LABELS = {
    "coach_challenge_scope": "Coach / club challenge",
    "automatic_or_booth_review": "Replay official / booth review",
    "assistive_correction": "Replay assist",
    "centralized_consultation": "League consultation",
    "emergency_centralized_override": "Emergency centralized override",
    "field_plus_replay": "Field + replay baseline",
}


def build():
    events = pd.read_csv(ANALYSIS / "replay_authority_events.csv").fillna("")
    rows=[]
    for stage in STAGE_ORDER:
        g=events[events["authority_shift"].eq(stage)]
        if g.empty: continue
        years=sorted(pd.to_numeric(g["year"], errors="coerce").dropna().astype(int).unique())
        rows.append({
            "authority_stage": stage,
            "stage_label": STAGE_LABELS.get(stage, stage),
            "stage_order": STAGE_ORDER.index(stage)+1,
            "event_count": len(g),
            "first_year": min(years) if years else None,
            "last_year": max(years) if years else None,
            "statuses": ";".join(sorted(set(g["status"].astype(str)))),
            "review_objects": ";".join(sorted(set(g["review_object"].astype(str)))),
            "who_initiates": ";".join(sorted(set(g["who_initiates"].astype(str)))),
            "who_decides": ";".join(sorted(set(g["who_decides"].astype(str)))),
            "example_summary": g.sort_values(["year","status"]).iloc[0]["summary"],
        })
    m=pd.DataFrame(rows).sort_values("stage_order")
    m.to_csv(ANALYSIS / "replay_authority_map.csv", index=False)
    m.to_parquet(ANALYSIS / "replay_authority_map.parquet", index=False)
    draw(m)
    (ANALYSIS / "replay_authority_map.md").write_text(render(m, events))
    print(ANALYSIS / "replay_authority_map.md")
    print(m[["stage_order","stage_label","event_count","first_year","last_year","review_objects"]].to_string(index=False))


def draw(m: pd.DataFrame):
    if m.empty: return
    fig, ax = plt.subplots(figsize=(11, 4.8))
    y=0
    xs=list(range(len(m)))
    labels=[]
    for i,(_,r) in enumerate(m.iterrows()):
        ax.scatter(i, y, s=900 + int(r["event_count"])*120)
        ax.text(i, y, f"{r['stage_order']}\n{r['event_count']} events", ha="center", va="center", fontsize=9)
        labels.append(r["stage_label"])
    ax.plot(xs, [y]*len(xs), linewidth=1)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_yticks([])
    ax.set_title("Replay/officiating authority map")
    ax.set_xlabel("Authority migration path")
    ax.grid(axis="x", alpha=.2)
    plt.tight_layout()
    plt.savefig(ANALYSIS / "replay_authority_map.png", dpi=170)
    plt.close()


def render(m: pd.DataFrame, events: pd.DataFrame) -> str:
    md=["# Replay/officiating authority map\n"]
    md.append("The map summarizes replay/officiating changes as authority migration, not merely as more replay. The direction is from field-only judgment toward layered correction: coach challenge, booth/replay official review, replay assist, league consultation, and emergency centralized override.\n")
    md.append("## Authority stages\n")
    md.append(m[["stage_order","stage_label","event_count","first_year","last_year","who_initiates","who_decides","review_objects"]].to_markdown(index=False))
    md.append("\n## Reading the map\n")
    md.append("- Coach/club challenge expands what teams can ask to be corrected.")
    md.append("- Replay official / booth review expands automatic correction without requiring a coach challenge.")
    md.append("- Replay assist shifts correction into lightweight, fast interventions.")
    md.append("- League consultation centralizes judgment for high-stakes or conduct decisions.")
    md.append("- Emergency centralized override is the institutional fallback for officiating disruption.\n")
    md.append("## Representative events\n")
    cols=["year","status","authority_shift","review_object","who_initiates","who_decides","summary"]
    md.append(events[cols].head(50).to_markdown(index=False))
    md.append("\n## Files\n")
    md.append("- `data/analysis/replay_authority_map.csv`")
    md.append("- `data/analysis/replay_authority_map.png`\n")
    return "\n".join(md)

if __name__ == "__main__":
    build()
