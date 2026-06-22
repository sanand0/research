#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyyaml", "pyarrow"]
# ///
"""Build analysis-ready NFL rules tables from rules.csv.

Inputs:
- rules.csv
- data/processed/manual_links.yaml

Outputs:
- data/processed/rule_events.csv
- data/processed/rule_changes.csv
- data/processed/rule_lineages.csv
- data/processed/rule_proposal_links.csv
- parquet copies for each CSV
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RULES = ROOT / "rules.csv"
LINKS = PROCESSED / "manual_links.yaml"


def norm_text(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def proposer_class(proposer: str) -> str:
    p = norm_text(proposer)
    if not p:
        return "unknown_or_rulebook"
    if "competition committee" in p:
        return "competition_committee"
    if "commissioner" in p:
        return "commissioner"
    return "club"


def origin_team(proposer: str) -> str:
    if proposer_class(proposer) != "club":
        return ""
    return str(proposer).strip()


def infer_granularity(row: pd.Series) -> str:
    kind = row.get("source_kind", "")
    method = row.get("extraction_method", "")
    status = row.get("status", "")
    if "rulebook" in kind or "rulebook" in method:
        return "rulebook_section"
    if "full_proposal" in kind or "full_proposal" in method or "special" in method:
        return "full_proposal_or_special_article"
    if status == "proposed":
        return "proposal_summary"
    if status == "approved":
        return "approved_summary"
    if "history" in kind or "chronology" in method:
        return "historical_seed"
    return "event"


def infer_outcome(row: pd.Series) -> str:
    status = row.get("status", "")
    temporality = row.get("temporality", "")
    if status == "proposed":
        return "proposed_pending_or_not_adopted"
    if status == "historical_context":
        return "historical_seed"
    if status == "approved" and temporality == "one_year_trial":
        return "approved_one_year_trial"
    if status == "approved" and temporality == "made_permanent":
        return "approved_made_permanent"
    if status == "approved":
        return "approved"
    return status or "unknown"


def infer_proposal_group(row: pd.Series) -> str:
    section = norm_text(row.get("source_section", ""))
    if "competition committee" in section:
        return "competition_committee_section"
    if section.startswith("by clubs") or "club playing" in section:
        return "club_section"
    if "bylaw" in section:
        return "bylaw_section"
    if "resolution" in section:
        return "resolution_section"
    if "playing" in section or "rule changes" in section:
        return "playing_rules_section"
    return "unknown_section"


def infer_lineage_and_sublineage(text: str, category: str, rulebook_ref: str) -> tuple[str, str]:
    t = norm_text(" ".join([text, category, rulebook_ref]))

    # Club / league business must precede replay because "video call" is not replay authority.
    if any(k in t for k in ["two-day negotiation", "unrestricted free agent", "video or phone call", "travel arrangements", "prospective unrestricted free agent"]):
        return "club_business", "free_agent_negotiation"
    if "scouting credentials" in t:
        return "club_business", "postseason_scouting_credentials"
    if "point differential" in t or "awarding contracts" in t:
        return "club_business", "contract_award_tiebreaker"
    if "draft selections" in t and "traded" in t:
        return "club_business", "draft_pick_trade_horizon"

    if any(k in t for k in ["wild card teams", "division champions", "playoff seeding", "regular season record"]):
        return "competitive_equity", "playoff_seeding"
    if "afc championship" in t or "wild card game" in t or "competitive inequity" in t:
        return "competitive_equity", "emergency_resolution"

    if any(k in t for k in ["illegally handing", "illegal punts", "drop kicks", "placekicks", "extension of the half", "major foul", "change of possession", "fouls by both teams"]):
        return "penalty_enforcement", "foul_enforcement_consistency"

    if re.search(r"\b(forward pass|behind the line of scrimmage)\b", t):
        return "passing_rules", "forward_pass"

    if any(k in t for k in ["annual draft", "draft of college players", "waiver", "college class", "prohibited any team from signing"]):
        return "league_governance", "player_acquisition_rules"

    if any(k in t for k in ["hashmark", "hashmarks", "inbounds line", "goal posts"]):
        return "field_rules", "field_markings"

    if any(k in t for k in ["two additional dfr", "designate two players for return", "designated for return", "dfr"]):
        return "roster_management", "designated_for_return"
    if "reserve/injured" in t or "90-player limit" in t:
        return "roster_management", "reserve_injured"
    if "reserve/physically unable" in t or "21-day practice" in t:
        return "roster_management", "pup_practice_window"
    if "international game" in t and "roster reduction" in t:
        return "roster_management", "international_game_roster_deadline"
    if "labor day" in t or "business days" in t:
        return "roster_management", "personnel_notice_timing"
    if any(k in t for k in ["roster", "reserve", "physically unable", "designate", "53 players", "21-day practice", "substitution", "substitute"]):
        return "roster_management", "roster_flexibility"

    # Special teams. Punt touchbacks are special teams but not kickoff.
    if "punt" in t and "touchback" in t:
        return "special_teams", "punt_touchback"
    kickoff_pat = re.compile(r"\b(free kick|kickoff|kicking off|onside|k-balls?|touchback|fair catch|setup zone|landing zone|kicking footballs?|wedge)\b")
    if kickoff_pat.search(t):
        if re.search(r"\b(4th-and-20|onside)\b", t):
            return "kickoff", "onside_kick"
        if re.search(r"\b(fair catch|touchback|25-yard|35-yard)\b", t):
            return "kickoff", "touchback_or_fair_catch"
        if re.search(r"\b(setup zone|alignment|formation|landing zone)\b", t):
            return "kickoff", "alignment_or_formation"
        if re.search(r"\b(k-balls?|kicking footballs?)\b", t):
            return "kickoff", "k_ball_preparation"
        if re.search(r"\bwedge\b", t):
            return "kickoff", "wedge_blocking"
        return "kickoff", "general"

    if "overtime" in t or "opportunity to possess" in t:
        return "overtime", "possession_equity"

    if any(k in t for k in ["replay", "review", "challenge", "clear and obvious", "officiating", "official", "league personnel", "disqualification"]):
        if "challenge" in t:
            return "replay_officiating", "coach_challenge"
        if "disqualification" in t:
            return "replay_officiating", "disqualification_consultation"
        if "clock" in t:
            return "replay_officiating", "game_clock"
        if "work stoppage" in t or "replacement" in t:
            return "replay_officiating", "emergency_officiating_override"
        if "failed fourth" in t or "fourth-down" in t or "fourth down" in t:
            return "replay_officiating", "reviewable_play_expansion"
        if "passer down" in t or "out of bounds before throwing" in t:
            return "replay_officiating", "reviewable_play_expansion"
        if "replay assist" in t or "advise" in t:
            return "replay_officiating", "replay_assist"
        return "replay_officiating", "authority_expansion"

    if any(k in t for k in ["helmet", "launch", "tripping", "dangerous tackling", "hip-drop", "crackback", "split-flow", "roughing the passer"]):
        return "player_safety_contact", "prohibited_contact_technique"

    if "jersey" in t or "numeral" in t:
        return "equipment_identity", "jersey_numbering"

    if "automatic first down" in t or "defensive holding" in t or "illegal contact" in t:
        return "offense_defense_balance", "penalty_severity"

    if "pushing a teammate" in t or "snapper" in t:
        return "offensive_strategy", "tush_push"

    return "general_gameplay", "general"

def infer_target_metric(lineage: str, sublineage: str, text: str) -> str:
    t = norm_text(text)
    metrics: list[str] = []
    if lineage == "kickoff":
        if any(k in t for k in ["speed", "space", "dangerous", "safety"]):
            metrics.append("player_safety")
        if any(k in t for k in ["return", "touchback"]):
            metrics.append("return_rate_or_touchback_rate")
        if "onside" in t:
            metrics.append("comeback_equity")
        if "out of bounds" in t or "50-yard" in t:
            metrics.append("incentive_alignment")
    if lineage == "replay_officiating":
        metrics.extend(["error_correction", "officiating_consistency"])
    if lineage == "overtime":
        metrics.append("competitive_equity")
    if lineage == "player_safety_contact":
        metrics.append("player_safety")
    if lineage == "roster_management":
        metrics.append("roster_flexibility")
    if lineage == "club_business":
        metrics.append("club_operational_flexibility")
    if lineage == "penalty_enforcement":
        metrics.append("penalty_consistency")
    if lineage == "passing_rules":
        metrics.append("offensive_option_space")
    if lineage == "field_rules":
        metrics.append("field_geometry")
    if lineage == "league_governance":
        metrics.append("player_acquisition_governance")
    if not metrics:
        metrics.append("unspecified")
    return ";".join(dict.fromkeys(metrics))


def selector_matches(row: pd.Series, selector: dict[str, Any]) -> bool:
    combined = norm_text(" ".join(str(row.get(c, "")) for c in ["summary", "effect", "reason", "rulebook_ref", "source_section", "proposer", "source_key"]))
    for key, value in selector.items():
        if key in {"contains_all", "contains_any"}:
            continue
        if key == "year":
            vals = value if isinstance(value, list) else [value]
            if int(row.get("year_int", -9999)) not in [int(v) for v in vals]:
                return False
        elif key in row.index:
            if norm_text(row.get(key, "")) != norm_text(value):
                return False
        else:
            return False
    if "contains_all" in selector:
        if not all(norm_text(x) in combined for x in selector["contains_all"]):
            return False
    if "contains_any" in selector:
        if not any(norm_text(x) in combined for x in selector["contains_any"]):
            return False
    return True


def load_manual_links(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"canonical_changes": []}
    with path.open() as f:
        return yaml.safe_load(f) or {"canonical_changes": []}



def source_quality(row: pd.Series) -> tuple[str, int, str]:
    kind = str(row.get("source_kind", ""))
    method = str(row.get("extraction_method", ""))
    key = str(row.get("source_key", ""))
    status = str(row.get("status", ""))
    if "rulebook_pdf" in kind or "pdf_rulebook" in method:
        return "official_pdf_rulebook", 100, "Official NFL rulebook PDF or official PDF rulebook-change list"
    if "rulebook_change" in kind or "rulebook_change" in method:
        return "official_rulebook_page", 94, "Official NFL online rulebook change list"
    if "full_proposal_pdf" in kind or "pdf_full_proposal" in method:
        return "official_pdf_proposal", 95, "Official NFL proposal PDF"
    if "special" in method or "full_proposal_article" in kind or "resolution_article" in kind:
        return "official_special_article", 92, "Official NFL article for a specific adopted proposal/resolution"
    if "official_summary" in kind:
        return "official_summary_page", 88, "Official NFL proposal/approval summary page"
    if key == "nflops_evolution" or "official_history" in kind:
        return "official_history_seed", 70, "Official NFL historical narrative seed; not a complete annual rulebook source"
    if key == "hof_chronology" or "secondary_history" in kind:
        return "secondary_history_seed", 55, "Secondary historical chronology seed; requires confirmation"
    if status == "historical_context":
        return "historical_seed", 60, "Historical seed row requiring confirmation"
    return "unknown_quality", 40, "Unclassified source quality"

def build_events(df: pd.DataFrame) -> pd.DataFrame:
    events = df.copy()
    events["event_id"] = events["rule_id"]
    events["year_int"] = pd.to_numeric(events["year"], errors="coerce").astype("Int64")
    events["normalized_summary"] = events["summary"].map(norm_text)
    events["proposer_class"] = events["proposer"].map(proposer_class)
    events["origin_team"] = events["proposer"].map(origin_team)
    events["granularity"] = events.apply(infer_granularity, axis=1)
    events["outcome"] = events.apply(infer_outcome, axis=1)
    events["proposal_group"] = events.apply(infer_proposal_group, axis=1)
    lineages = events.apply(lambda r: infer_lineage_and_sublineage(" ".join([str(r.get("summary", "")), str(r.get("effect", "")), str(r.get("reason", ""))]), str(r.get("category", "")), str(r.get("rulebook_ref", ""))), axis=1)
    events["auto_lineage"] = [x[0] for x in lineages]
    events["auto_sublineage"] = [x[1] for x in lineages]
    events["target_metric_guess"] = events.apply(lambda r: infer_target_metric(r["auto_lineage"], r["auto_sublineage"], " ".join([str(r.get("summary", "")), str(r.get("effect", "")), str(r.get("reason", ""))])), axis=1)
    quality = events.apply(source_quality, axis=1)
    events["source_quality_tier"] = [x[0] for x in quality]
    events["source_quality_score"] = [x[1] for x in quality]
    events["source_quality_note"] = [x[2] for x in quality]
    events["analysis_include_default"] = events["source_quality_score"].ge(80)
    events["canonical_change_id"] = "event_" + events["event_id"].astype(str)
    events["manual_lineage"] = ""
    events["manual_sublineage"] = ""
    events["status_lifecycle"] = ""
    events["manual_title"] = ""
    events["needs_manual_review"] = events["granularity"].isin(["historical_seed"]) | events["category"].eq("gameplay")
    return events


def apply_manual_links(events: pd.DataFrame, manual: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    events = events.copy()
    link_rows: list[dict[str, Any]] = []
    for change in manual.get("canonical_changes", []):
        cid = change["canonical_change_id"]
        matched_ids: set[str] = set()
        for selector in change.get("selectors", []):
            mask = events.apply(lambda r: selector_matches(r, selector), axis=1)
            for _, row in events[mask].iterrows():
                if str(row["canonical_change_id"]).startswith("event_"):
                    matched_ids.add(row["event_id"])
                    link_rows.append({
                        "canonical_change_id": cid,
                        "event_id": row["event_id"],
                        "rule_id": row["rule_id"],
                        "year": row["year"],
                        "status": row["status"],
                        "item_type": row["item_type"],
                        "proposal_number": row["proposal_number"],
                        "proposer": row["proposer"],
                        "source_key": row["source_key"],
                        "link_type": "manual_selector_applied",
                        "selector": str(selector),
                        "title": change.get("title", ""),
                        "lineage": change.get("lineage", ""),
                        "sublineage": change.get("sublineage", ""),
                        "status_lifecycle": change.get("status_lifecycle", ""),
                        "target_metrics": ";".join(change.get("target_metrics", [])),
                    })
        if matched_ids:
            mask = events["event_id"].isin(matched_ids)
            unassigned_mask = mask & events["canonical_change_id"].astype(str).str.startswith("event_")
            events.loc[unassigned_mask, "canonical_change_id"] = cid
            events.loc[unassigned_mask, "manual_lineage"] = change.get("lineage", "")
            events.loc[unassigned_mask, "manual_sublineage"] = change.get("sublineage", "")
            events.loc[unassigned_mask, "status_lifecycle"] = change.get("status_lifecycle", "")
            events.loc[unassigned_mask, "manual_title"] = change.get("title", "")
            events.loc[unassigned_mask, "needs_manual_review"] = False
    return events, pd.DataFrame(link_rows)


def build_changes(events: pd.DataFrame, manual: dict[str, Any]) -> pd.DataFrame:
    manual_by_id = {c["canonical_change_id"]: c for c in manual.get("canonical_changes", [])}
    rows: list[dict[str, Any]] = []
    for cid, g in events.groupby("canonical_change_id", dropna=False):
        manual_change = manual_by_id.get(cid, {})
        years = sorted(int(y) for y in g["year_int"].dropna().unique())
        lineage = manual_change.get("lineage") or g["auto_lineage"].mode().iloc[0]
        sublineage = manual_change.get("sublineage") or g["auto_sublineage"].mode().iloc[0]
        status_values = sorted(set(g["status"].astype(str)))
        outcomes = sorted(set(g["outcome"].astype(str)))
        approved_count = int((g["status"] == "approved").sum())
        proposed_count = int((g["status"] == "proposed").sum())
        historical_count = int((g["status"] == "historical_context").sum())
        best = g.sort_values(["confidence", "year_int"], ascending=[False, False]).iloc[0]
        rows.append({
            "canonical_change_id": cid,
            "title": manual_change.get("title") or best["summary"][:140],
            "lineage": lineage,
            "sublineage": sublineage,
            "first_year": min(years) if years else None,
            "last_year": max(years) if years else None,
            "years": ";".join(map(str, years)),
            "status_lifecycle": manual_change.get("status_lifecycle") or ";".join(outcomes),
            "target_metrics": ";".join(manual_change.get("target_metrics", [])) or ";".join(sorted(set(g["target_metric_guess"].astype(str))))[:500],
            "event_count": len(g),
            "approved_event_count": approved_count,
            "proposed_event_count": proposed_count,
            "historical_event_count": historical_count,
            "source_keys": ";".join(sorted(set(g["source_key"].astype(str)))),
            "best_source_quality_score": int(pd.to_numeric(g["source_quality_score"], errors="coerce").fillna(0).max()),
            "source_quality_tiers": ";".join(sorted(set(g["source_quality_tier"].astype(str)))),
            "analysis_include_default": bool(g["analysis_include_default"].any()),
            "proposers": ";".join(sorted(x for x in set(g["proposer"].astype(str)) if x)),
            "rulebook_refs": ";".join(sorted(x for x in set(g["rulebook_ref"].astype(str)) if x)),
            "representative_summary": best["summary"],
            "needs_manual_review": bool(g["needs_manual_review"].any()) and cid not in manual_by_id,
        })
    return pd.DataFrame(rows).sort_values(["first_year", "lineage", "canonical_change_id"], na_position="last")


def build_lineages(events: pd.DataFrame, changes: pd.DataFrame) -> pd.DataFrame:
    lineage_source = events.copy()
    lineage_source["lineage"] = lineage_source["manual_lineage"].where(lineage_source["manual_lineage"].astype(bool), lineage_source["auto_lineage"])
    lineage_source["sublineage"] = lineage_source["manual_sublineage"].where(lineage_source["manual_sublineage"].astype(bool), lineage_source["auto_sublineage"])
    rows = []
    for (lineage, sublineage), g in lineage_source.groupby(["lineage", "sublineage"]):
        rows.append({
            "lineage": lineage,
            "sublineage": sublineage,
            "event_count": len(g),
            "canonical_change_count": g["canonical_change_id"].nunique(),
            "approved_event_count": int((g["status"] == "approved").sum()),
            "proposed_event_count": int((g["status"] == "proposed").sum()),
            "historical_event_count": int((g["status"] == "historical_context").sum()),
            "first_year": int(g["year_int"].dropna().min()) if g["year_int"].notna().any() else None,
            "last_year": int(g["year_int"].dropna().max()) if g["year_int"].notna().any() else None,
            "proposer_classes": ";".join(sorted(set(g["proposer_class"].astype(str))))
        })
    return pd.DataFrame(rows).sort_values(["event_count", "lineage", "sublineage"], ascending=[False, True, True])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default=str(RULES))
    parser.add_argument("--manual-links", default=str(LINKS))
    args = parser.parse_args()

    PROCESSED.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.rules).fillna("")
    manual = load_manual_links(Path(args.manual_links))

    events = build_events(df)
    events, proposal_links = apply_manual_links(events, manual)
    changes = build_changes(events, manual)
    lineages = build_lineages(events, changes)

    outputs = {
        "rule_events": events,
        "rule_changes": changes,
        "rule_lineages": lineages,
        "rule_proposal_links": proposal_links,
    }
    for name, table in outputs.items():
        csv_path = PROCESSED / f"{name}.csv"
        parquet_path = PROCESSED / f"{name}.parquet"
        table.to_csv(csv_path, index=False)
        table.to_parquet(parquet_path, index=False)
        print(f"wrote {csv_path} rows={len(table)} cols={len(table.columns)}")

    print("\nTop lineages by event_count:")
    print(lineages.head(12).to_string(index=False))
    print("\nManual links:", len(proposal_links))
    print("Canonical changes:", len(changes))
    print("Events needing review:", int(events["needs_manual_review"].sum()))


if __name__ == "__main__":
    main()
