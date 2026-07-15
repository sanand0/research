You are comparing outputs of two attempts at the same ideation task. You do not know how either was produced. Judge only what is on the page.

A mechanism is a distinct way a proposal creates value or produces the requested outcome. It may be an intervention, product, service, policy, business model, experience, or format.

Different wording, examples, audiences, channels, or implementation details do not constitute different mechanisms unless they materially change the value-producing or causal pathway.

Rules:

- Do not reward length, idea count, formatting, rhetorical polish, or apparent effort.
- Judge the quality and diversity of mechanisms, not the volume of material.
- Penalize padding, vague suggestions, and near-duplicates.
- Treat "tie" as a valid and common result. Do not force a winner.
- Cite short comparative evidence from both P and Q for every verdict.
- Output only the JSON object inside a Markdown code fence.

<task>{{task}}</task>

<output version="P">

{{p}}

</output>

<output version="Q">

{{q}}

</output>

Before comparing, normalize the outputs internally:

1. Extract the atomic mechanisms in each output.
2. Merge proposals that rely on substantially the same value-producing or causal pathway.
3. Do not count goals, themes, examples, slogans, benefits, or generic advice as mechanisms.
4. A mechanism that violates an explicit constraint or an unavoidable requirement of the task is ineligible for positive evidence. Do not invent constraints that the task does not imply.
5. For leverage, causal_soundness, viability, operational_clarity, and originality, compare up to the strongest four distinct eligible mechanisms from each output.
6. For mechanism_diversity and selectivity, consider the whole normalized output.
7. Do not reveal this normalization process.

Compare P and Q on each dimension:

- leverage: Which output's strongest mechanisms would produce more consequential progress toward the task objective if successful? Judge the importance of the bottleneck addressed and the magnitude of the likely benefit, not merely relevance.
- causal_soundness: Which output provides more credible paths from the proposed change to the desired outcome? Penalize magical leaps, unsupported assumptions, missing dependencies, and effects that do not follow from the proposal.
- viability: Which output proposes mechanisms more likely to survive real-world constraints and be adopted or sustained? Consider incentives, user acceptance, affordability, operational capacity, regulation, ethics, adverse effects, and required behaviour change. Do not require every constraint to be discussed explicitly; penalize only assumptions that materially weaken the proposal.
- operational_clarity: Which output states its mechanisms concretely enough that a capable reader can understand what would change, for whom, and how the proposal could be prototyped, tested, or used? Penalize generic advice and underspecified concepts. Do not require a full implementation plan or metrics unless the task asks for them.
- originality: Among mechanisms that are relevant and reasonably plausible, which output introduces more non-obvious value-producing levers, combinations, or reframings? Do not reward unusual wording, novelty for its own sake, or impractical eccentricity.
- mechanism_diversity: Which output's credible mechanisms span more important and causally distinct regions of the solution space? Count different value-producing levers, not phrasings, examples, audiences, or variants of the same intervention. Weak or random variety earns no credit.
- selectivity: Which output better curates the reader's limited attention? Penalize redundant mechanisms, vague items, repeated premises, non-mechanisms, and low-value additions that dilute the useful portfolio. Do not penalize explanation that materially improves understanding, evaluation, or execution.

winner must be "P", "Q", or "tie".

margin:

- 1 = a clear material advantage that could still reverse under a reasonable interpretation of the task.
- 2 = a decisive and structural advantage, supported by multiple concrete examples and unlikely to reverse under reasonable interpretations.
- Omit margin for ties.
- Margin 2 should be rare.

Evidence requirements:

- Include a short quote or precise reference from both P and Q.
- Explain the difference rather than merely describing each output.
- Do not cite length or number of ideas as an advantage.
- Keep each evidence field concise.
- Properly escape quotation marks so the output remains valid JSON.

JSON schema:

```json
{
  "comparisons": [
    { "dimension": "leverage", "winner": "Q", "margin": 1, "evidence": "P proposes '...', which addresses X; Q proposes '...', which targets the more consequential bottleneck Y." },
    { "dimension": "causal_soundness", "winner": "tie", "evidence": "P's '...' and Q's '...' both provide similarly credible intervention-to-outcome paths." },
    { "dimension": "actionability", "winner": "P", "margin": 1, "evidence": "..." },
  ]
}
```
