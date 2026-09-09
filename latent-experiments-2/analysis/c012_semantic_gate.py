#!/usr/bin/env python3
"""Structure-only C012 gate: check whether discovery labs share a physiological estimand.

This script deliberately never computes reddish-minus-bluish effects. It inspects only
schema, missingness, measurement-site availability, and terminal-window coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SKIN_SITES = {
    "Tsk_A": "head",
    "Tsk_D": "shoulder",
    "Tsk_F": "forearm",
    "Tsk_H": "hand",
    "Tsk_J": "back",
    "Tsk_K": "chest",
    "Tsk_M": "abdomen",
    "Tsk_O": "thigh",
    "Tsk_Q": "shin",
    "Tsk_T": "foot",
}
HR_VARS = ("HRinst", "HRave")
DISCOVERY_LABS = (1, 3, 5, 7)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_observed(value: str | None) -> bool:
    return value is not None and value.strip() != ""


def summarize_lab(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    if not rows:
        raise ValueError(f"empty CSV: {path}")

    required = {"ID_full", "Lc", *SKIN_SITES, *HR_VARS}
    missing = required.difference(rows[0])
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")

    rounds = sorted({r["ID_full"] for r in rows})
    available_skin = [
        col for col in SKIN_SITES if any(is_observed(r.get(col)) for r in rows)
    ]

    terminal = {var: 0 for var in HR_VARS}
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        grouped[r["ID_full"]][r["Lc"]].append(r)

    # Protocol periods are stored in time order within each round. A round has usable
    # terminal HR coverage when both reddish and bluish periods contain >=8 observed
    # values among their last 10 one-minute records.
    for by_lc in grouped.values():
        for var in HR_VARS:
            usable = True
            for lc in ("r", "b"):
                tail = by_lc.get(lc, [])[-10:]
                if len(tail) < 10 or sum(is_observed(r.get(var)) for r in tail) < 8:
                    usable = False
                    break
            terminal[var] += int(usable)

    return {
        "file": path.name,
        "sha256": sha256(path),
        "rows": len(rows),
        "rounds": len(rounds),
        "available_skin_columns": available_skin,
        "available_skin_sites": [SKIN_SITES[c] for c in available_skin],
        "terminal_hr_rounds": terminal,
    }


def build_result(data_dir: Path) -> dict:
    labs = {}
    for lab in DISCOVERY_LABS:
        path = data_dir / f"env_physiological_lab{lab}.csv"
        if not path.exists():
            raise FileNotFoundError(f"missing discovery file: {path}")
        labs[str(lab)] = summarize_lab(path)

    skin_sets = [set(v["available_skin_columns"]) for v in labs.values()]
    common_skin_cols = sorted(set.intersection(*skin_sets)) if skin_sets else []

    common_hr = []
    for var in HR_VARS:
        # No arbitrary coverage threshold is needed for the stop: a common HR variable
        # would at least need one usable terminal-window round in every discovery lab.
        if all(v["terminal_hr_rounds"][var] > 0 for v in labs.values()):
            common_hr.append(var)

    semantic_pass = bool(common_skin_cols or common_hr)
    return {
        "claim_id": "C012",
        "analysis_kind": "structure_and_missingness_only",
        "hue_effect_computed": False,
        "confirmation_accessed": False,
        "discovery_labs": list(DISCOVERY_LABS),
        "labs": labs,
        "common_skin_columns": common_skin_cols,
        "common_skin_sites": [SKIN_SITES[c] for c in common_skin_cols],
        "common_hr_variables_with_any_terminal_round_in_every_lab": common_hr,
        "semantic_gate_pass": semantic_pass,
        "decision": (
            "PASS: at least one common physiological measurement is structurally usable"
            if semantic_pass
            else "STOP: no common skin site and no HR variable has a usable terminal-window round in every discovery lab"
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=Path("cache/c012-discovery"))
    p.add_argument("--output", type=Path, default=Path("results/c012_semantic_gate.json"))
    args = p.parse_args()

    result = build_result(args.data_dir)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)

    print("C012 structure-only semantic gate")
    for lab, x in result["labs"].items():
        print(
            f"lab {lab}: skin={','.join(x['available_skin_sites']) or 'none'}; "
            f"HRinst terminal={x['terminal_hr_rounds']['HRinst']}/{x['rounds']}; "
            f"HRave terminal={x['terminal_hr_rounds']['HRave']}/{x['rounds']}"
        )
    print("common skin sites:", result["common_skin_sites"] or "none")
    print("common HR variables:", result["common_hr_variables_with_any_terminal_round_in_every_lab"] or "none")
    print(result["decision"])


if __name__ == "__main__":
    main()
