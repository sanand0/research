#!/usr/bin/env python3
# /// script
# dependencies = ["pandas"]
# ///
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
errors = []

def check(name, condition, detail=""):
    if not condition:
        errors.append((name, detail))

rules = pd.read_csv(ROOT / "rules.csv").fillna("")
events = pd.read_csv(ROOT / "data/processed/rule_events.csv").fillna("")
changes = pd.read_csv(ROOT / "data/processed/rule_changes.csv").fillna("")
lineages = pd.read_csv(ROOT / "data/processed/rule_lineages.csv").fillna("")
links = pd.read_csv(ROOT / "data/processed/rule_proposal_links.csv").fillna("")

check("rules_nonempty", len(rules) > 0, str(len(rules)))
check("event_count_matches_rules", len(events) == len(rules), f"events={len(events)} rules={len(rules)}")
check("no_duplicate_rule_ids", rules["rule_id"].duplicated().sum() == 0, str(rules["rule_id"].duplicated().sum()))
check("no_duplicate_event_ids", events["event_id"].duplicated().sum() == 0, str(events["event_id"].duplicated().sum()))
check("no_blank_summaries", (rules["summary"].astype(str).str.len() == 0).sum() == 0)
check("no_pre_1920_rows", (pd.to_numeric(rules["year"], errors="coerce") < 1920).sum() == 0)
check("no_unknown_item_types", ~rules["item_type"].eq("unknown").any(), rules["item_type"].value_counts().to_string())

# Known previously failing rows.
text_2026_4 = " ".join(rules[(rules.source_key == "nflops_2026_full_proposals_pdf") & (rules.proposal_number.astype(str) == "4")]["category"].astype(str))
check("pdf_2026_prop4_not_kickoff", "special_teams" not in text_2026_4, text_2026_4)
prop5_reason = " ".join(rules[(rules.source_key == "nflops_2026_full_proposals_pdf") & (rules.proposal_number.astype(str) == "5")]["reason"].astype(str))
check("pdf_2026_prop5_no_bylaw_leak", "Bylaw Proposals Summary" not in prop5_reason, prop5_reason[:200])
check("pdf_2026_prop5_officiating", rules[(rules.source_key == "nflops_2026_full_proposals_pdf") & (rules.proposal_number.astype(str) == "5")]["category"].eq("officiating").all())

kball = events[events["summary"].str.contains("K-Ball|kicking football", case=False, regex=True)]
check("kball_classified_kickoff", len(kball) == 0 or kball["auto_lineage"].eq("kickoff").all(), kball[["summary", "auto_lineage"]].to_string())

challenge = events[events["canonical_change_id"].eq("challenge_system_expansion_detroit_2023_2024")]
check("detroit_challenge_group_has_approved_2024", ((challenge["year"].astype(str) == "2024") & (challenge["status"] == "approved")).any(), challenge[["year","status","summary"]].to_string())

substitution = events[events["summary"].str.contains("substitution", case=False, regex=False)]
check("substitution_lineage_roster", len(substitution) == 0 or substitution["auto_lineage"].eq("roster_management").all(), substitution[["year","summary","auto_lineage"]].to_string())

hof = rules[rules.source_key == "hof_chronology"]
check("hof_no_pre_nfl", (pd.to_numeric(hof["year"], errors="coerce") < 1920).sum() == 0)
check("hof_no_franchise_move_noise", ~hof["summary"].str.contains("moved the Redskins|moved the Championship|renamed the", case=False, regex=True).any(), hof[["year","summary"]].to_string())

check("links_are_applied_only", links["link_type"].eq("manual_selector_applied").all() if len(links) else True, links["link_type"].value_counts().to_string() if len(links) else "")

print(f"rules_rows={len(rules)}")
print(f"events_rows={len(events)} changes_rows={len(changes)} lineages_rows={len(lineages)} links_rows={len(links)}")
if errors:
    print("FAIL")
    for name, detail in errors:
        print(f"- {name}: {detail}")
    raise SystemExit(1)
print("PASS")
