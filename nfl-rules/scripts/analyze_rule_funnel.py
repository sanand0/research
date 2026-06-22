#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "tabulate"]
# ///
"""Analyze the NFL rule-change funnel from proposed events to approved changes.

Inputs:
- data/processed/rule_events.csv
- data/processed/rule_changes.csv
- data/processed/rule_proposal_links.csv

Outputs under data/analysis/:
- rule_funnel_summary.csv
- rule_funnel_by_year.csv
- rule_funnel_by_category.csv
- rule_funnel_by_proposer_class.csv
- rule_funnel_by_lineage.csv
- rule_funnel_canonical_outcomes.csv
- rule_funnel_pressure_signals.csv
- rule_funnel_report.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ANALYSIS = ROOT / "data" / "analysis"


def safe_int_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def lineage(events: pd.DataFrame) -> pd.Series:
    manual = events["manual_lineage"].fillna("").astype(str)
    return manual.where(manual.str.len() > 0, events["auto_lineage"].fillna(""))


def sublineage(events: pd.DataFrame) -> pd.Series:
    manual = events["manual_sublineage"].fillna("").astype(str)
    return manual.where(manual.str.len() > 0, events["auto_sublineage"].fillna(""))


def summarize_group(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, g in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row.update({
            "events": len(g),
            "proposed_events": int((g["status"] == "proposed").sum()),
            "approved_events": int((g["status"] == "approved").sum()),
            "historical_events": int((g["status"] == "historical_context").sum()),
            "canonical_changes": int(g["canonical_change_id"].nunique()),
            "proposed_canonical_changes": int(g.loc[g["status"] == "proposed", "canonical_change_id"].nunique()),
            "approved_canonical_changes": int(g.loc[g["status"] == "approved", "canonical_change_id"].nunique()),
            "distinct_proposers": int(g.loc[g["proposer"].astype(str).str.len() > 0, "proposer"].nunique()),
        })
        denom = row["proposed_canonical_changes"]
        row["canonical_approval_ratio"] = round(row["approved_canonical_changes"] / denom, 3) if denom else None
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["events"], ascending=False)


def build(args: argparse.Namespace) -> dict[str, pd.DataFrame | str]:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    events = pd.read_csv(PROCESSED / "rule_events.csv").fillna("")
    changes = pd.read_csv(PROCESSED / "rule_changes.csv").fillna("")
    links = pd.read_csv(PROCESSED / "rule_proposal_links.csv").fillna("")
    events["year_int"] = safe_int_series(events["year"])
    events["lineage"] = lineage(events)
    events["sublineage"] = sublineage(events)

    window = events[(events["year_int"] >= args.start_year) & (events["year_int"] <= args.end_year)].copy()
    funnel = window[window["status"].isin(["proposed", "approved"])].copy()

    canonical_rows = []
    for cid, g in funnel.groupby("canonical_change_id", dropna=False):
        proposed = g[g["status"] == "proposed"]
        approved = g[g["status"] == "approved"]
        historical = g[g["status"] == "historical_context"]
        representative = g.sort_values(["confidence", "year_int"], ascending=[False, False]).iloc[0]
        years = sorted(int(x) for x in g["year_int"].dropna().unique())
        canonical_rows.append({
            "canonical_change_id": cid,
            "title_or_summary": representative.get("manual_title") or representative["summary"][:180],
            "lineage": representative["lineage"],
            "sublineage": representative["sublineage"],
            "first_year": min(years) if years else None,
            "last_year": max(years) if years else None,
            "years": ";".join(map(str, years)),
            "has_proposal": len(proposed) > 0,
            "has_approval": len(approved) > 0,
            "has_historical": len(historical) > 0,
            "proposed_events": len(proposed),
            "approved_events": len(approved),
            "proposer_classes": ";".join(sorted(set(x for x in g["proposer_class"].astype(str) if x))),
            "proposers": ";".join(sorted(set(x for x in g["proposer"].astype(str) if x))),
            "source_keys": ";".join(sorted(set(g["source_key"].astype(str))))
        })
    canonical = pd.DataFrame(canonical_rows)
    if not canonical.empty:
        canonical["outcome_bucket"] = canonical.apply(
            lambda r: "proposed_and_approved" if r["has_proposal"] and r["has_approval"] else (
                "approved_without_captured_proposal" if r["has_approval"] else "proposed_only_pressure_signal"
            ), axis=1)
        canonical = canonical.sort_values(["has_proposal", "has_approval", "first_year", "lineage"], ascending=[False, False, True, True])

    pressure = canonical[canonical["outcome_bucket"] == "proposed_only_pressure_signal"].copy() if not canonical.empty else pd.DataFrame()
    if not pressure.empty:
        pressure["pressure_score"] = (
            pressure["proposed_events"].astype(int) * 2
            + pressure["proposers"].astype(str).str.count(";")
            + pressure["lineage"].isin(["kickoff", "replay_officiating", "player_safety_contact", "offense_defense_balance", "offensive_strategy"]).astype(int)
        )
        pressure = pressure.sort_values(["pressure_score", "first_year", "lineage"], ascending=[False, True, True])

    tables = {
        "rule_funnel_summary": pd.DataFrame([{
            "start_year": args.start_year,
            "end_year": args.end_year,
            "events": len(funnel),
            "proposed_events": int((funnel["status"] == "proposed").sum()),
            "approved_events": int((funnel["status"] == "approved").sum()),
            "canonical_changes": int(funnel["canonical_change_id"].nunique()),
            "proposed_canonical_changes": int(funnel.loc[funnel["status"] == "proposed", "canonical_change_id"].nunique()),
            "approved_canonical_changes": int(funnel.loc[funnel["status"] == "approved", "canonical_change_id"].nunique()),
            "proposed_and_approved": int((canonical["outcome_bucket"] == "proposed_and_approved").sum()) if not canonical.empty else 0,
            "approved_without_captured_proposal": int((canonical["outcome_bucket"] == "approved_without_captured_proposal").sum()) if not canonical.empty else 0,
            "proposed_only_pressure_signal": int((canonical["outcome_bucket"] == "proposed_only_pressure_signal").sum()) if not canonical.empty else 0,
        }]),
        "rule_funnel_by_year": summarize_group(funnel, ["year_int", "status"]),
        "rule_funnel_by_category": summarize_group(funnel, ["category", "status"]),
        "rule_funnel_by_proposer_class": summarize_group(funnel, ["proposer_class", "status"]),
        "rule_funnel_by_lineage": summarize_group(funnel, ["lineage", "sublineage", "status"]),
        "rule_funnel_canonical_outcomes": canonical,
        "rule_funnel_pressure_signals": pressure,
    }

    for name, table in tables.items():
        table.to_csv(ANALYSIS / f"{name}.csv", index=False)
        table.to_parquet(ANALYSIS / f"{name}.parquet", index=False)

    report = render_report(args, tables, links)
    (ANALYSIS / "rule_funnel_report.md").write_text(report)
    return {**tables, "report": report}


def md_table(df: pd.DataFrame, cols: list[str], n: int = 10) -> str:
    if df.empty:
        return "_No rows._\n"
    sub = df.loc[:, [c for c in cols if c in df.columns]].head(n).copy()
    return sub.to_markdown(index=False)


def render_report(args: argparse.Namespace, tables: dict[str, pd.DataFrame], links: pd.DataFrame) -> str:
    summary = tables["rule_funnel_summary"].iloc[0].to_dict()
    pressure = tables["rule_funnel_pressure_signals"]
    lineage_table = tables["rule_funnel_by_lineage"]
    proposer = tables["rule_funnel_by_proposer_class"]
    canonical = tables["rule_funnel_canonical_outcomes"]

    out = []
    out.append("# Rule funnel analysis\n")
    out.append(f"Window: {args.start_year}-{args.end_year}.\n")
    out.append("## Summary\n")
    for k, v in summary.items():
        out.append(f"- `{k}`: {v}")
    out.append("\n## Interpretation\n")
    out.append("The recent dataset is strongest for governance analysis: proposals, approvals, one-year trials, and proposal families. Treat approval ratios as indicative, not definitive, because some approved rules may have proposal records outside the currently captured sources.\n")
    out.append("## Proposer class × status\n")
    out.append(md_table(proposer, ["proposer_class", "status", "events", "canonical_changes", "proposed_canonical_changes", "approved_canonical_changes", "canonical_approval_ratio"], 20))
    out.append("\n## Lineage × status\n")
    out.append(md_table(lineage_table, ["lineage", "sublineage", "status", "events", "canonical_changes", "proposed_canonical_changes", "approved_canonical_changes", "canonical_approval_ratio"], 30))
    out.append("\n## Canonical outcome buckets\n")
    out.append(md_table(canonical, ["canonical_change_id", "lineage", "sublineage", "years", "outcome_bucket", "proposed_events", "approved_events", "proposers"], 30))
    out.append("\n## Proposed-only pressure signals\n")
    out.append(md_table(pressure, ["canonical_change_id", "lineage", "sublineage", "first_year", "proposed_events", "pressure_score", "proposers", "title_or_summary"], 30))
    out.append("\n## Files\n")
    out.append("- `data/analysis/rule_funnel_summary.csv`")
    out.append("- `data/analysis/rule_funnel_by_year.csv`")
    out.append("- `data/analysis/rule_funnel_by_category.csv`")
    out.append("- `data/analysis/rule_funnel_by_proposer_class.csv`")
    out.append("- `data/analysis/rule_funnel_by_lineage.csv`")
    out.append("- `data/analysis/rule_funnel_canonical_outcomes.csv`")
    out.append("- `data/analysis/rule_funnel_pressure_signals.csv`")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int, default=2023)
    parser.add_argument("--end-year", type=int, default=2026)
    args = parser.parse_args()
    result = build(args)
    print((ANALYSIS / "rule_funnel_report.md"))
    print(result["rule_funnel_summary"].to_string(index=False))
    pressure = result["rule_funnel_pressure_signals"]
    print(f"pressure_signals={len(pressure)}")


if __name__ == "__main__":
    main()
