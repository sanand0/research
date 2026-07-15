You are comparing outputs of two attempts at the same ideation task. You do not know how either was produced. Judge only what is on the page.

Rules:

- Do NOT reward length or idea count. Ignore volume; judge quality and diversity of mechanisms. Penalize padding and near-duplicates.
- Cite evidence (short quotes) for every verdict.
- "tie" is a valid and common answer. Do not force a winner.
- Output ONLY the JSON object in a Markdown code fence.

<task>{{task}}</task>

<output version="P">

{{p}}

</output>

<output version="Q">

{{q}}

</output>

First, per version, answer these binary checks:

- banned_list_present: did it explicitly list banned obvious ideas?
- survivors_avoid_banned: are finalists genuinely free of the banned ideas and their thin disguises?
- named_transfer_rules: does at least one finalist import a NAMED structural rule from an unrelated domain, and does the idea depend on it (not decoration)?
- practical_and_wildcard_distinct: are the practical pick and the wildcard both present and genuinely different from each other?

Then compare P vs Q on each dimension. winner is "P", "Q", or "tie".
margin: 1 = clear, 2 = decisive. Omit margin for ties.

- spread: number of genuinely distinct causal mechanisms in the pool
- non_obviousness: which set escapes further from what a smart generalist would list in 30 seconds?
- transfer_quality: depth and load of cross-domain borrowing
- selection_soundness: is the recommended idea truly among the strongest for this brief?
- critique_honesty: are assumptions and failure modes specific and real, or hand-waving?
- insight_articulation: is the stated non-obvious insight named, specific, and true - or a platitude?

JSON schema:

```json
{
  "checks": {
    "P": {"banned_list_present": true, "survivors_avoid_banned": true, "named_transfer_rules": true, "practical_and_wildcard_distinct": true},
    "Q": { ... }
  },
  "comparisons": [
    {"dimension": "spread", "winner": "Q", "margin": 1, "evidence": "..."},
    {"dimension": "non_obviousness", "winner": "tie", "evidence": "..."},
    ...
  ],
  "note": "one line on the biggest difference"
}
```
