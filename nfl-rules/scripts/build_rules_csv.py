#!/usr/bin/env python3
# /// script
# dependencies = ["beautifulsoup4", "lxml", "pandas", "requests", "pypdf", "pyarrow"]
# ///
from __future__ import annotations
import argparse, csv, hashlib, re, sys, io, contextlib
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "rules.csv"
UA = "Mozilla/5.0 (compatible; nfl-rules-research/0.1)"
SOURCES = [
    {"key":"nflops_approved_2026","season":2026,"status":"approved","kind":"official_summary","url":"https://operations.nfl.com/updates/the-game/approved-2026-playing-rules-bylaws-and-resolutions/"},
    {"key":"nflops_proposals_2026","season":2026,"status":"proposed","kind":"official_summary","url":"https://operations.nfl.com/updates/the-rules/2026-playing-rules-bylaw-and-resolution-proposals/"},
    {"key":"nflops_approved_2025","season":2025,"status":"approved","kind":"official_summary","url":"https://operations.nfl.com/updates/the-rules/approved-2025-playing-rules-bylaws-and-resolutions/"},
    {"key":"nflops_proposals_2025","season":2025,"status":"proposed","kind":"official_summary","url":"https://operations.nfl.com/updates/the-rules/2025-rules-change-proposals/"},
    {"key":"nflops_approved_2024","season":2024,"status":"approved","kind":"official_summary","url":"https://operations.nfl.com/updates/the-rules/approved-2024-playing-rules/"},
    {"key":"nflops_rulebook_2022_changes","season":2022,"status":"approved","kind":"official_rulebook_pdf_change_list","url":"https://operations.nfl.com/media/5kvgzyss/2022-nfl-rulebook-final.pdf"},
    {"key":"nflops_approved_2023","season":2023,"status":"approved","kind":"official_summary","url":"https://operations.nfl.com/updates/the-rules/approved-2023-playing-rules/"},
    {"key":"nflops_proposals_2023","season":2023,"status":"proposed","kind":"official_summary","url":"https://operations.nfl.com/updates/the-rules/2023-rules-change-proposals/"},
    {"key":"nflops_adopted_2023_fair_catch","season":2023,"status":"approved","kind":"official_full_proposal_article","url":"https://operations.nfl.com/updates/the-rules/adopted-playing-rules-change-proposal-putting-ball-in-play-after-fair-catch/"},
    {"key":"nflops_resolution_2023_g1_special","season":2022,"status":"approved","kind":"official_resolution_article","url":"https://operations.nfl.com/updates/football-ops/2023-resolution-g-1-approved-at-special-league-meeting/"},
    {"key":"nflops_rulebook_2025_changes","season":2025,"status":"approved","kind":"official_rulebook_change_list","url":"https://operations.nfl.com/the-rules/nfl-rulebook/"},
    {"key":"nflops_rulebook_2025_pdf","season":2025,"status":"approved","kind":"official_rulebook_pdf_change_list","url":"https://operations.nfl.com/media/e4sneelu/2025-nfl-rulebook-final.pdf"},
    {"key":"nflops_evolution","season":None,"status":"historical_context","kind":"official_history","url":"https://operations.nfl.com/the-rules/evolution-of-the-nfl-rules/"},
    {"key":"hof_chronology","season":None,"status":"historical_context","kind":"secondary_history","url":"https://www.profootballhof.com/football-history/chronology-of-professional-football/"},
    {"key":"nflops_2026_full_proposals_pdf","season":2026,"status":"proposed","kind":"official_full_proposal_pdf","url":"https://operations.nfl.com/media/dxfj3uak/2026-playing-rules-bylaw-and-resolution-proposals.pdf"},
]

@dataclass
class RuleRow:
    rule_id: str; season: int|None; year: int|None; status: str; item_type: str
    proposal_number: str; proposer: str; rulebook_ref: str; summary: str; effect: str; reason: str
    category: str; mechanism: str; affected_phase: str; affected_party: str; temporality: str
    source_kind: str; source_key: str; source_url: str; source_section: str; extraction_method: str; confidence: float

def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:90] or "x"

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()

def fetch(src, refresh=False):
    RAW.mkdir(parents=True, exist_ok=True)
    ext = ".pdf" if src["url"].endswith(".pdf") else ".html"
    path = RAW / f'{src["key"]}{ext}'
    if path.exists() and path.stat().st_size and not refresh:
        return path
    r = requests.get(src["url"], headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path

def split_num(text):
    m = re.match(r"^((?:G-)?\d+[A-Z]?(?:-[A-Z])?|\([A-Z]\))\.?\s+(.*)$", text)
    return (m.group(1).rstrip("."), m.group(2).strip()) if m else ("", text.strip())

def parse_proposer(text):
    m = re.match(r"^By\s+([^;]+);\s*(.*)$", text, re.I)
    return (norm(m.group(1)), norm(m.group(2))) if m else ("", norm(text))

def item_type(section):
    s = section.lower()
    if "bylaw" in s: return "bylaw"
    if "resolution" in s: return "resolution"
    if "playing" in s or "rule" in s: return "playing_rule"
    if s.startswith("by "): return "playing_rule"
    return "unknown"

def rule_ref(text):
    refs = []
    for pat in [
        r"Rule\s+\d+(?:,\s*Section\s+\d+)?(?:,\s*Article\s+\d+)?",
        r"Article\s+[IVXLC]+,\s*Section\s+[\d.]+(?:\\s*\([A-Z]\))?",
        r"Article\s+[IVXLC]+",
    ]:
        refs += re.findall(pat, text, re.I)
    out = []
    for r in map(norm, refs):
        if r not in out: out.append(r)
    return "; ".join(out)

def classify(text, typ):
    t = text.lower()
    cat = "league_governance" if typ == "league_rule" else ("administration" if typ in {"bylaw","resolution"} else "gameplay")
    mech = "rule_text_change"; phase = "general"; party = "league"
    # Primary business/governance classifications before replay: "video or phone call" is a free-agency rule, not replay.
    if any(w in t for w in ["free agent", "unrestricted free agent", "two-day negotiation", "video or phone call", "travel arrangements"]):
        return "club_business_rules", "rule_text_change", "free_agent_negotiation", "clubs/players"
    if any(w in t for w in ["scouting credentials", "draft selections", "point differential", "awarding contracts"]):
        return "club_business_rules", "rule_text_change", "league_business", "clubs"
    if any(w in t for w in ["playoff seeding", "wild card", "division champions", "afc championship"]):
        return "competitive_equity", "rule_text_change", "postseason_format", "clubs"
    # Primary game-phase classification. Do this before replay/officiating because kickoff rules may contain replay subclauses.
    if re.search(r"\b(free kick|onside|k-balls?|kickoff|kicking off|kicking footballs?|touchback|setup zone|landing zone|fair catch|wedge)\b", t):
        return "special_teams", "rule_text_change", "kickoff", "kicking_team/receiving_team"
    if "overtime" in t:
        return "competitive_equity", "rule_text_change", "overtime", "both_teams"
    if any(w in t for w in ["replay","review","clock expired","officiating","official","league personnel","disqualification","challenge"]):
        return "officiating", "review_or_officiating_authority", "game_administration", "officials/league"
    if any(w in t for w in ["tackle","helmet","launch","tripping","dangerous","violent gesture","nose wipe","crackback","roughing the passer"]):
        return "player_safety", "prohibit_contact_technique", "contact", "players"
    if any(w in t for w in ["jersey","numeral"]):
        return "equipment_identity", "rule_text_change", "roster/equipment", "players"
    if any(w in t for w in ["roster","reserve","physically unable","designate","designated for return","dfr","dfrs","53 players","substitution","substitute"]):
        return "roster_management", "rule_text_change", "roster", "clubs/players"
    if typ == "league_rule" or any(w in t for w in ["waiver", "annual draft", "draft of college players", "college class"]):
        return "league_governance", "rule_text_change", "player_acquisition", "clubs/players"
    if any(w in t for w in ["free agent","negotiation","contracts","draft selections","scouting credentials"]):
        return "club_business_rules", "rule_text_change", "league_business", "clubs"
    return cat, mech, phase, party

def temporal(text):
    t = text.lower()
    if "one year only" in t or "one-year only" in t: return "one_year_trial"
    if "make permanent" in t or "permanent" in t: return "made_permanent"
    return "permanent_or_unspecified"

def row(src, typ, num, proposer, body, section, effect="", reason="", method="html_summary", confidence=0.9, year=None):
    body, effect, reason = norm(body), norm(effect), norm(reason)
    cat, mech, phase, party = classify(" ".join([body,effect,reason]), typ)
    seed = "|".join(map(str, [src.get("season") or year, src["status"], typ, num, proposer, body[:140], src["key"]]))
    rid = slug(f'nfl-{src.get("season") or year}-{src["status"]}-{typ}-{num}-{hashlib.sha1(seed.encode()).hexdigest()[:8]}')
    return RuleRow(rid, src.get("season"), year or src.get("season"), src["status"], typ, num, proposer,
                   rule_ref(" ".join([body,effect])), body, effect, reason, cat, mech, phase, party,
                   temporal(" ".join([body,effect,reason])), src["kind"], src["key"], src["url"], section, method, confidence)

def main_content(soup):
    blocks = soup.select(".content") or soup.select(".content-block") or [soup.body]
    return max(blocks, key=lambda b: len(b.get_text(" ", strip=True)))

def parse_html(src, path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    content = main_content(soup)
    rows, section = [], ""
    for el in content.find_all(("h2","h3","h4","p","ol","ul"), recursive=True):
        if not isinstance(el, Tag): continue
        tag = el.name.lower(); text = norm(el.get_text(" ", strip=True))
        if not text: continue
        if tag in {"h2","h3","h4"}:
            section = text; continue
        if tag in {"ol","ul"}:
            for idx, li in enumerate(el.find_all("li", recursive=False), 1):
                raw = norm(li.get_text(" ", strip=True))
                num, rest = split_num(raw)
                proposer, body = parse_proposer(rest)
                rows.append(row(src, item_type(section), (f"{idx}-{num.strip("()")}" if num.startswith("(") and num.endswith(")") else (num or str(idx))), proposer, body, section))
        elif tag == "p" and section and (section.lower()[:3] == "by " or any(x in section.lower() for x in ["summary","proposal","rules","bylaw","resolution"])):
            num, rest = split_num(text)
            proposer, body = parse_proposer(rest)
            if proposer or num:
                rows.append(row(src, item_type(section), num, proposer, body, section))
    return rows


def parse_pdf_rule_changes(src, path):
    with contextlib.redirect_stderr(io.StringIO()):
        reader = PdfReader(str(path))
    text = reader.pages[2].extract_text() or ""
    text = norm(text.replace("2022 Rules Changes", "").replace("Rule-Section-Article", ""))
    rows = []
    parts = [("6-1-3", "Makes permanent the free kick formation change implemented during the 2021 season."), ("16-1-4", "Modified overtime in postseason games to require that each team has the opportunity to possess the ball.")]
    for ref, desc in parts:
        rr = row(src, "playing_rule", ref, "", desc, "2022 Rules Changes", desc, "", "pdf_rulebook_change_list", 0.96)
        rr.rulebook_ref = ref
        rows.append(rr)
    return rows


def parse_pdf_rulebook_change_list(src, path):
    with contextlib.redirect_stderr(io.StringIO()):
        reader = PdfReader(str(path))
    text = "\n".join((p.extract_text() or "") for p in reader.pages[:4])
    year = src.get("season")
    heading = f"{year} Rules Changes" if year else "Rules Changes"
    start = text.find(heading)
    if start >= 0:
        text = text[start:]
    # Stop before preface/table of contents if present.
    for stop in ["PREFACE", "TABLE OF CONTENTS", "Rule 1"]:
        ix = text.find(stop)
        if ix > 0:
            text = text[:ix]
    text = norm(text.replace(heading, "").replace("Rule-Section-Article", ""))
    parts = re.findall(r"((?:Rule\s+)?\d+(?:-\d+)*(?:-\d+)?)\s+(.+?)(?=\s+(?:Rule\s+)?\d+(?:-\d+)*(?:-\d+)?\s+|$)", text)
    rows = []
    for ref, desc in parts:
        ref, desc = norm(ref), norm(desc)
        if not desc or ref.lower() == "rule":
            continue
        rr = row(src, "playing_rule", ref, "", desc, f"{year} Rules Changes", desc, "", "pdf_rulebook_change_list", 0.98)
        rr.rulebook_ref = ref
        rows.append(rr)
    return rows

def parse_pdf_2026(src, path):
    text = "\n\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    rows = []
    pat = re.compile(r"2026 PLAYING RULE PROPOSAL NO\.\s(\d+)\s+(.*?)(?=\n2026 PLAYING RULE PROPOSAL NO\.|\n2026 Bylaw Proposals Summary|\n2026 BYLAW PROPOSAL NO\.|\n2026 Resolution Proposals Summary|\n2026 RESOLUTION PROPOSAL NO\.|\Z)", re.S)
    for m in pat.finditer(text):
        num, block = m.group(1), norm(m.group(2))
        sm = re.search(r"Submitted by\s+(.+?)?(\s+Effect:|\s+Reason:|$)", block, re.I)
        em = re.search(r"Effect:\s*(.*?)(?:\s+Reason:|$)", block, re.I)
        rm = re.search(r"Reason:\s*(.*?)(?:\s+2026 Bylaw Proposals Summary|\s+2026 Resolution Proposals Summary|$)", block, re.I)
        proposer = norm(sm.group(1)) if sm and sm.group(1) else ""
        effect = norm(em.group(1)) if em else ""
        reason = norm(rm.group(1)) if rm else ""
        rr = row(src, "playing_rule", num, proposer, effect or block[:600], "2026 PLAYING RULE PROPOSAL", effect, reason, "pdf_full_proposal", 0.97)
        if not rr.rulebook_ref: rr.rulebook_ref = rule_ref(block)
        rows.append(rr)
    return rows

def parse_nflops_history(src, path):
    txt = main_content(BeautifulSoup(path.read_bytes(), "lxml")).get_text(" ", strip=True)
    items = [
        (1933, "Forward pass allowed from anywhere behind the line of scrimmage."),
        (1943, "Substitution restrictions relaxed during wartime roster pressure."),
        (1949, "Free substitution restored, accelerating specialist offensive, defensive, and kicking roles."),
        (1974, "Kickoff spot moved from the 40-yard line to the 35-yard line to increase returns."),
        (1994, "Kickoff spot moved to the 30-yard line after return rates fell."),
        (2009, "Three-or-more-player blocking wedge on returns banned."),
        (2011, "Kickoff spot moved from the 30-yard line to the 35-yard line."),
    ]
    rows=[]
    for y, summary in items:
        pseudo=dict(src); pseudo["season"]=y
        rows.append(row(pseudo, "playing_rule", "", "", summary, "NFL Ops evolution narrative", summary, "", "curated_history_seed", 0.75, y))
    return rows

def parse_hof(src, path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    rows = []
    keep_pat = re.compile(r"\b(new rule|waiver rule|annual draft|draft of college players|legalized from anywhere|forward pass was legalized from anywhere|inbounds line|inbounds lines|hashmarks?|goal posts? on the goal lines|15-yard penalty for roughing the passer|prohibited any team from signing)\b", re.I)
    league_rule_pat = re.compile(r"\b(waiver|annual draft|draft of college players|college class|signing)\b", re.I)
    for h in soup.find_all("h3"):
        y = norm(h.get_text(" ", strip=True))
        if not re.fullmatch(r"\d{4}", y):
            continue
        year = int(y)
        if year < 1920:
            continue
        paras=[]; sib=h.find_next_sibling()
        while sib and not (isinstance(sib, Tag) and sib.name=="h3"):
            if isinstance(sib, Tag) and sib.name in {"p","ul","ol"}:
                paras.append(norm(sib.get_text(" ", strip=True)))
            sib=sib.find_next_sibling()
        text = " ".join(paras)
        sentences = [norm(x) for x in re.split(r"(?<=[.!?])\s+", text) if norm(x)]
        kept = [sent for sent in sentences if keep_pat.search(sent)]
        for idx, summary in enumerate(kept, 1):
            typ = "league_rule" if league_rule_pat.search(summary) else "playing_rule"
            pseudo=dict(src); pseudo["season"]=year
            rows.append(row(pseudo, typ, str(idx), "", summary[:800], "Pro Football Hall of Fame chronology", summary[:800], "", "chronology_sentence_filter", 0.65, year))
    return rows

def parse_special_article(src, path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    content = main_content(soup)
    paras = [norm(x.get_text(" ", strip=True)) for x in content.find_all("p")]
    flat = norm(" ".join([x for x in paras if x]))
    rows = []
    if src["key"] == "nflops_adopted_2023_fair_catch":
        prop = "Competition Committee" if "Submitted by Competition Committee" in flat else ""
        effect = "For one year only, puts the ball in play at the receiving team's 25-yard line if there is a fair catch on a free kick behind the receiving team's 25-yard line."
        reason = "Player Safety"
        rr = row(src, "playing_rule", "16A", prop, effect, "2023 PLAYING RULE PROPOSAL NO. 16A", effect, reason, "special_adopted_article", 0.98)
        rr.rulebook_ref = "Rule 10, Section 2, Article 4"
        rows.append(rr)
    elif src["key"] == "nflops_resolution_2023_g1_special":
        prop = "Commissioner's Office, with support of the Competition Committee"
        effect = "To require the AFC Championship Game to be played at a neutral site and to provide for a possible site change in a Wild Card Game under defined conditions."
        reason = "To mitigate competitive effects in the AFC playoffs resulting from two clubs playing fewer regular season games."
        rows.append(row(src, "resolution", "G-1", prop, effect, "2023 Resolution G-1", effect, reason, "special_resolution_article", 0.96, 2022))
    return rows

def parse_rulebook_2025_changes(src, path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    h = soup.find(lambda tag: tag.name == "h2" and "2025 Rule Changes" in tag.get_text(" ", strip=True))
    rows = []
    if not h:
        return rows
    node = h.find_next_sibling()
    while node and not (isinstance(node, Tag) and node.name == "h2"):
        if isinstance(node, Tag) and node.name in {"ul", "ol"}:
            for li in node.find_all("li", recursive=False):
                txt = norm(li.get_text(" ", strip=True))
                if "|" not in txt:
                    continue
                ref, desc = [norm(x) for x in txt.split("|", 1)]
                rr = row(src, "playing_rule", ref, "", desc, "2025 Rule Changes", desc, "", "rulebook_change_list", 0.96)
                rr.rulebook_ref = ref
                rows.append(rr)
        node = node.find_next_sibling()
    return rows

def build(refresh=False):
    INTERIM.mkdir(parents=True, exist_ok=True)
    all_rows=[]; manifest=[]
    for src in SOURCES:
        try:
            path=fetch(src, refresh)
            manifest.append({**src, "cached_path": str(path), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            if src["key"] == "nflops_rulebook_2022_changes": all_rows += parse_pdf_rule_changes(src, path)
            elif src["key"] == "nflops_rulebook_2025_pdf": all_rows += parse_pdf_rulebook_change_list(src, path)
            elif path.suffix == ".pdf": all_rows += parse_pdf_2026(src, path)
            elif src["key"] == "nflops_evolution": all_rows += parse_nflops_history(src, path)
            elif src["key"] == "hof_chronology": all_rows += parse_hof(src, path)
            elif src["key"] == "nflops_rulebook_2025_changes": all_rows += parse_rulebook_2025_changes(src, path)
            elif src["key"] in {"nflops_adopted_2023_fair_catch", "nflops_resolution_2023_g1_special"}: all_rows += parse_special_article(src, path)
            else: all_rows += parse_html(src, path)
        except Exception as e:
            print(f"WARN failed {src['key']}: {e}", file=sys.stderr)
    df=pd.DataFrame([asdict(r) for r in all_rows])
    cols=list(RuleRow.__dataclass_fields__)
    if not df.empty:
        df=df.reindex(columns=cols).drop_duplicates()
        df=df.sort_values(["year","status","item_type","proposal_number","source_key"], na_position="last")
    df.to_csv(OUT, index=False, quoting=csv.QUOTE_MINIMAL)
    df.to_parquet(INTERIM/"rules.parquet", index=False)
    pd.DataFrame(manifest).to_csv(INTERIM/"source_manifest.csv", index=False)
    return df

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args=ap.parse_args()
    df=build(args.refresh)
    print(f"wrote {OUT} rows={len(df)}")
    if len(df):
        print(df.groupby(["source_key","status","item_type"], dropna=False).size().to_string())

if __name__ == "__main__":
    main()
