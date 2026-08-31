#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "click>=8.1", "numpy", "spacy",
#   "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
# ]
# ///
"""Score every result against the source task and write measurements back into the JSON.

Adds to each result:   "measured": {axis: z-score vs the baseline style}, "drift": %novel content words
Adds to each style:    "measured_coordinates": mean of the above across tasks
Adds a top-level:      "_scoring": {baseline, axes, proxies, n}

Leaves update.py and every prompt untouched. Run it after each update.py pass:
    ./score.py --file results2.json
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import click
import numpy as np
import spacy

NLP = spacy.load("en_core_web_sm")

EPISTEMIC = set(
    "observed observation inferred inference infer evidence suggests suggest indicate indicates "
    "appears appear seems seem likely unlikely uncertain unclear unknown assumed assume assumption "
    "confirmed unconfirmed established reported estimate estimated apparently possibly probably "
    "presumably believe believed unresolved untested plausible attributed".split()
)
DEONTIC = set("must should shall need needs required require requires ought".split())
CONNECTIVE = set(
    "therefore however thus because since although though while whereas unless so hence "
    "consequently moreover furthermore but and or nor yet if then also besides instead rather".split()
)
CLAUSE_DEPS = {"ROOT", "ccomp", "advcl", "relcl", "acl", "xcomp", "conj", "csubj", "pcomp"}
SUBORD_DEPS = {"advcl", "relcl", "acl", "ccomp", "csubj"}
AGENT_NOUNS = set(
    "team teams engineer engineers manager managers people person someone staff analyst director "
    "lead leads owner owners customer customers student students user users developer developers "
    "desk support sales board committee reviewer reviewers author writer teacher".split()
)
STOP = set(
    "the a an and or but of to in for on at by with from as is are was were be been being it its "
    "this that these those not no nor if then so than there their they them he she his her you your "
    "we our us i me my one two more most less least will would can could should must may might do "
    "does did done have has had".split()
)

# Proxies chosen after validating each one against a known-direction prompt pair.
# Where an obvious proxy failed, the reason is noted; do not silently swap these back.
AXES = {
    "density": "content words per sentence",              # NOT per clause: packing happens via embedding
    "shared_ground": "bare demonstratives per 100 words",  # weak proxy, treat results as provisional
    "link_explicitness": "connectives per clause",
    "writer_presence": "first-person pronouns per 100 words",
    "agency": "% of clause subjects that are agents",      # NOT passive rate: prompts forbid passive directly
    "stance_marking": "epistemic markers per clause",
    "social_force": "deontic + imperative per clause",
    "architecture": "subordinate clauses per sentence",
    "sequence": "Kendall tau of output vs source sentence order (undirected)",
    "concreteness": "proper nouns + numerals per 100 words",
    "rhythm": "coefficient of variation of sentence length",
}


def stem(word: str) -> str:
    return re.sub(r"(ing|ed|es|s|ly|er)$", "", word)


def content_words(text: str) -> list[str]:
    words = (w.lower() for w in re.findall(r"[A-Za-z]+", text))
    return [w for w in words if w not in STOP and len(w) > 3]


def is_agentive(tok) -> bool:
    if tok.ent_type_ in ("PERSON", "ORG", "NORP") or tok.pos_ == "PROPN":
        return True
    if tok.lemma_.lower() in AGENT_NOUNS:
        return True
    return tok.pos_ == "PRON" and tok.text.lower() in {"i", "we", "he", "she", "they", "you", "someone", "who"}


def sentence_order_tau(out_sents: list[str], src_sents: list[str]) -> float:
    """How much the output preserves the source's order of ideas. 1.0 = same order."""
    def bag(s: str) -> set[str]:
        return set(re.findall(r"[a-z]{4,}", s.lower()))

    src = [bag(s) for s in src_sents]
    matched: list[int] = []
    for sent in out_sents:
        b = bag(sent)
        if not b:
            continue
        sims = [len(b & s) / max(len(b | s), 1) for s in src]
        if sims and max(sims) > 0.05:
            matched.append(int(np.argmax(sims)))
    if len(matched) < 3:
        return float("nan")
    conc = disc = 0
    for i in range(len(matched)):
        for j in range(i + 1, len(matched)):
            conc += matched[i] < matched[j]
            disc += matched[i] > matched[j]
    return (conc - disc) / max(conc + disc, 1)


def measure(text: str) -> dict:
    doc = NLP(text)
    toks = [t for t in doc if not t.is_space]
    words = [t for t in toks if t.is_alpha]
    nw = max(len(words), 1)
    sents = [s for s in doc.sents if s.text.strip()]
    ns = max(len(sents), 1)
    lengths = [len(s.text.split()) for s in sents] or [1]
    mean_len = float(np.mean(lengths))
    clauses = [t for t in toks if t.dep_ in CLAUSE_DEPS and t.pos_ in ("VERB", "AUX")]
    nc = max(len(clauses), 1)
    subjects = [t for t in toks if t.dep_ in ("nsubj", "nsubjpass")]
    lower = [t.text.lower() for t in words]

    bare = 0
    for t in toks:
        if t.text.lower() in {"this", "that", "these", "those", "it", "they", "them"} and t.pos_ in ("PRON", "DET"):
            nxt = t.nbor(1) if t.i + 1 < len(doc) else None
            if nxt is None or nxt.pos_ not in ("NOUN", "PROPN"):
                bare += 1

    imperatives = sum(
        1 for t in toks
        if t.pos_ == "VERB" and t.dep_ == "ROOT" and t.tag_ == "VB"
        and not any(c.dep_ in ("nsubj", "nsubjpass") for c in t.children)
    )
    return {
        "density": sum(1 for t in words if t.pos_ in ("NOUN", "VERB", "ADJ", "ADV", "PROPN", "NUM")) / ns,
        "shared_ground": bare / nw * 100,
        "link_explicitness": sum(1 for w in lower if w in CONNECTIVE) / nc,
        "writer_presence": sum(1 for t in toks if t.pos_ == "PRON" and t.text.lower()
                               in {"i", "me", "my", "mine", "we", "us", "our", "ours"}) / nw * 100,
        "agency": 100 * sum(1 for s in subjects if is_agentive(s)) / max(len(subjects), 1),
        "stance_marking": sum(1 for w in lower if w in EPISTEMIC) / nc * 100,
        "social_force": (sum(1 for w in lower if w in DEONTIC) + imperatives) / nc * 100,
        "architecture": sum(1 for t in toks if t.dep_ in SUBORD_DEPS) / ns,
        "concreteness": sum(1 for t in toks if t.pos_ in ("PROPN", "NUM")) / nw * 100,
        "rhythm": float(np.std(lengths) / mean_len) if mean_len else 0.0,
        "_sents": [s.text for s in sents],
        "_nwords": nw,
    }


@click.command()
@click.option("--file", "path", type=click.Path(path_type=Path, exists=True, dir_okay=False),
              default=Path("results.json"), show_default=True)
@click.option("--baseline", default="ctl_contract_only", show_default=True,
              help="Style id used as the zero point. Every effect is measured against it, task by task.")
def main(path: Path, baseline: str) -> None:
    data = json.loads(path.read_text())
    tasks = {t["id"]: t["text"] for t in data["tasks"]}
    src = {k: measure(v) for k, v in tasks.items()}
    src_content = {k: {stem(w) for w in content_words(v)} for k, v in tasks.items()}

    raw: dict[tuple[str, str], dict] = {}
    for row in data["results"]:
        m = measure(row["output"])
        m["sequence"] = sentence_order_tau(m.pop("_sents"), src[row["task"]]["_sents"])
        out_content = content_words(row["output"])
        stems = {stem(w) for w in out_content}
        m["drift"] = 100 * len([w for w in out_content if stem(w) not in src_content[row["task"]]]) / max(len(out_content), 1)
        m["source_recall"] = 100 * len([w for w in src_content[row["task"]] if w in stems]) / max(len(src_content[row["task"]]), 1)
        m["length_ratio"] = m.pop("_nwords") / max(src[row["task"]]["_nwords"], 1)
        raw[(row["style"], row["task"])] = m

    if not any(s == baseline for s, _ in raw):
        raise click.ClickException(f"baseline style {baseline!r} has no results in {path}")

    sd = {a: float(np.nanstd([m[a] for m in raw.values()])) + 1e-9 for a in AXES}
    per_style: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in data["results"]:
        key = (row["style"], row["task"])
        base = raw.get((baseline, row["task"]))
        m = raw[key]
        row["rewording"] = round(m["drift"], 1)  # NOT a fidelity score - see _scoring.caveats
        row["source_recall"] = round(m["source_recall"], 1)
        row["length_ratio"] = round(m["length_ratio"], 2)
        if base:
            row["measured"] = {a: round((m[a] - base[a]) / sd[a], 2) for a in AXES if m[a] == m[a] and base[a] == base[a]}
            for a, v in row["measured"].items():
                per_style[row["style"]][a].append(v)

    for style in data["styles"]:
        vals = per_style.get(style["id"])
        if vals:
            style["measured_coordinates"] = {a: round(float(np.mean(v)), 2) for a, v in vals.items()}
        d = [raw[(style["id"], t)]["drift"] for t in tasks if (style["id"], t) in raw]
        if d:
            style["measured_rewording"] = round(float(np.mean(d)), 1)

    data["_scoring"] = {
        "baseline": baseline,
        "units": "z-scores, standard deviations across all outputs in this file, paired by task",
        "axes": AXES,
        "n_results": len(data["results"]),
        "caveats": {
            "noise_floor": "A posture moves an axis it does not name by 0.66 SD at the 90th percentile. Treat |effect| "
                           "under ~0.7 SD as unmeasured, not as a failed prompt.",
            "second_proxy": "A near-zero effect can mean the prompt failed OR the proxy is blind. Before retiring a "
                            "prompt, measure that axis a second, structurally different way.",
            "rewording_is_not_fidelity": "`rewording` counts source content words the output does not reuse. It cannot "
                                         "tell invented facts from framing verbs, naive-reader explanation, or arithmetic "
                                         "the source entails. Verified: one style scored 32% and invented facts; another "
                                         "scored 38% and invented none. Use it to track a file against itself over time. "
                                         "Never use it to grade or relabel a single style without reading the outputs.",
            "circularity": "Lexicon-based axes (stance_marking, link_explicitness, social_force) count words their own "
                           "prompts supply. Roughly a quarter of the measured effect is echo.",
        },
    }
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)
    click.echo(json.dumps({"file": str(path), "scored": len(data["results"]), "styles": len(per_style)}))


if __name__ == "__main__":
    main()
