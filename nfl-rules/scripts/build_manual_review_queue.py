#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "tabulate"]
# ///
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ANALYSIS = ROOT / "data" / "analysis"


def reason_list(row: pd.Series) -> list[str]:
    out: list[str] = []
    if str(row.get("needs_manual_review", "")).lower() in {"true", "1"}:
        out.append("flagged_by_processing")
    try:
        if float(row.get("confidence", 1)) < 0.7:
            out.append("low_confidence_source_or_extraction")
    except Exception:
        pass
    if str(row.get("status", "")) == "historical_context":
        out.append("historical_seed_requires_confirmation")
    if str(row.get("granularity", "")) == "historical_seed":
        out.append("historical_seed_granularity")
    if str(row.get("auto_lineage", "")) == "general_gameplay":
        out.append("generic_lineage_needs_more_specific_taxonomy")
    if str(row.get("canonical_change_id", "")).startswith("event_"):
        out.append("not_linked_to_canonical_group")
    if str(row.get("item_type", "")) in {"league_rule", "resolution", "bylaw"} and str(row.get("category", "")) in {"gameplay", "administration"}:
        out.append("non_playing_rule_classification_check")
    return list(dict.fromkeys(out))

def priority(row: pd.Series) -> int:
    rs = str(row.get("review_reasons", "")).split(";") if row.get("review_reasons", "") else []
    score = 0
    if "low_confidence_source_or_extraction" in rs:
        score += 5
    if "historical_seed_requires_confirmation" in rs:
        score += 4
    if "generic_lineage_needs_more_specific_taxonomy" in rs:
        score += 3
    if "not_linked_to_canonical_group" in rs:
        score += 2
    if int(row.get("year_int", 0) or 0) >= 2023:
        score += 2
    if str(row.get("status", "")) == "approved":
        score += 1
    return score


def suggested_action(row: pd.Series) -> str:
    rs = str(row.get("review_reasons", ""))
    if "historical_seed" in rs:
        return "Confirm against primary source; decide whether to keep as seed, split, relabel, or remove."
    if "generic_lineage" in rs:
        return "Assign a more specific lineage/sublineage or add a taxonomy rule."
    if "not_linked" in rs:
        return "Decide whether this belongs to an existing canonical group or should remain singleton."
    if "non_playing" in rs:
        return "Check item_type/category distinction: playing rule, league rule, bylaw, or resolution."
    return "Review summary, lineage, canonical grouping, and confidence."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    events = pd.read_csv(PROCESSED / "rule_events.csv").fillna("")
    events["year_int"] = pd.to_numeric(events["year"], errors="coerce").fillna(0).astype(int)
    events["review_reasons_list"] = events.apply(reason_list, axis=1)
    events["review_reasons"] = events["review_reasons_list"].apply(lambda x: ";".join(x))
    queue = events[events["review_reasons"].astype(str).str.len() > 0].copy()
    queue["review_priority"] = queue.apply(priority, axis=1)
    queue["suggested_action"] = queue.apply(suggested_action, axis=1)
    cols = [
        "review_priority", "year", "status", "item_type", "category", "auto_lineage", "auto_sublineage",
        "canonical_change_id", "proposal_number", "proposer", "confidence", "review_reasons", "suggested_action",
        "summary", "source_key", "source_url", "rule_id"
    ]
    queue = queue[[c for c in cols if c in queue.columns]].sort_values(["review_priority", "year", "source_key"], ascending=[False, True, True])
    queue.to_csv(ANALYSIS / "manual_review_queue.csv", index=False)
    queue.to_parquet(ANALYSIS / "manual_review_queue.parquet", index=False)
    reason_counts = (
        queue.assign(reason=queue["review_reasons"].str.split(";"))
        .explode("reason")
        .groupby("reason", dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("rows", ascending=False)
    )
    md = []
    md.append("# Manual review queue\n")
    md.append(f"Rows requiring review: {len(queue)}\n")
    md.append("## Reason counts\n")
    md.append(reason_counts.to_markdown(index=False))
    md.append("\n## Highest-priority rows\n")
    show_cols = ["review_priority", "year", "status", "item_type", "auto_lineage", "auto_sublineage", "review_reasons", "summary", "source_key"]
    md.append(queue[[c for c in show_cols if c in queue.columns]].head(40).to_markdown(index=False))
    md.append("\n## Suggested workflow\n")
    md.append("1. Start with recent approved rows with generic lineage.")
    md.append("2. Then resolve historical seed rows: keep, split, relabel, or remove.")
    md.append("3. Update `data/processed/manual_links.yaml` for canonical grouping decisions.")
    md.append("4. Update `scripts/build_analysis_tables.py` if the change should become automatic taxonomy logic.")
    md.append("5. Re-run `uv run scripts/build_analysis_tables.py && uv run scripts/build_manual_review_queue.py && uv run scripts/validate_processing.py`.\n")
    (ANALYSIS / "manual_review_queue.md").write_text("\n".join(md))
    print(ANALYSIS / "manual_review_queue.csv")
    print(f"rows={len(queue)}")
    print(reason_counts.to_string(index=False))


if __name__ == "__main__":
    main()
