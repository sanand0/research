# Talk narrative — How do you calibrate an AI scientist?

## Proposition

**Treat an AI research agent as an uncalibrated scientific instrument.**

The agent can generate plausible hypotheses, analyses and p-values. The scientific-computing problem is making it earn the right to believe them.

Recommended title:

> **How do you calibrate an AI scientist?**

Alternate title:

> **I asked an AI to discover science. It mostly learned when to stop.**

## Audience takeaway

A first-time attendee should leave with one reusable idea:

> Before letting an agent claim a discovery, force it through empirical-null calibration, applicability/measurement gates, reserved confirmation evidence, and explicit stop rules.

The talk is not “AI failed.” It is a live demonstration that ordinary scientific-computing safeguards repeatedly changed what the agent was allowed to conclude.

## Timing: 24 minutes talk + 6 minutes Q&A

### 0:00–1:30 — Hook: “Find me something I don't know”

Start with the challenge on one slide:

> Give an AI papers + open data. Ask it to discover something scientifically useful that I did not already know. Let it write and run Python. Do not reward a good-looking answer; reward a result that survives attempts to kill it.

Then show the final scorecard without percentages:

- one tempting signal killed by a real null;
- one plausible parameter killed by model applicability;
- one positive discovery killed by independent confirmation;
- one calibrated multi-lab analysis killed by measurement semantics.

Say explicitly: this is an adaptive case series, **not** a 0/N benchmark of AI science.

### 1:30–3:30 — The scientific loop

Draw a five-box loop:

`discrepancy → evidence-role freeze → calibration → discovery → confirmation`

Put a red STOP arrow under every transition.

Key sentence:

> “The feature I ended up valuing most was not autonomous hypothesis generation. It was the ability to stop before spending more evidence.”

### 3:30–6:30 — C001: the null was wrong

Visual: three horizontal bars/points:

1. cross-study TEM-1 residual structure;
2. same-condition technical replicate range;
3. naive permutation-null range.

Story:

- The agent finds mutation-position structure in disagreements between two deep-mutational-scanning maps.
- Nominal permutation says it is extremely significant.
- We ask a harder calibration question: **does the same detector stay quiet on real same-condition replicates?**
- It does not. Technical replicate structure is as large or larger.
- Reserved confirmation remains unopened.

Punchline:

> **A p-value can be calibrated against the wrong world.**

### 6:30–9:30 — C002: the estimator returned a number; the model did not apply

Visual: synthetic calibration versus real mouse.

- Multistep regression correctly recovers branching parameter `m` under synthetic subsampling.
- An independent Poisson process can return a raw `m` near 1, but the exponential-fit applicability check rejects it.
- In real Allen VISp data, subsets return near-critical-looking numbers, yet the frozen fit-quality gate fails or changes with neuron subset.
- Bounded heterogeneity/state-switch simulations do not reproduce the failure.
- Stop before confirmation rather than invent richer post-hoc models.

Punchline:

> **An estimate is not a result until the model that gives it meaning has passed.**

### 9:30–13:30 — C003: the discovery really was positive—and still died

This is the full scientific loop.

Visual 1: three German steppe plots.

- all have raw Taylor slope `b<2`;
- 2/3 are unusually low under the constraint-preserving null;
- one plot with a lower raw `b` is *less* exceptional once its own constraints are respected.

Visual 2: five Danish heath confirmation plots.

- again all `b<2`;
- frozen confirmation: **0/5** pass;
- study-level confirmation p=1.0 under both null families.

Punchline:

> **A good workflow must make a positive discovery easy to kill.**

Do not claim that biological stabilization is absent globally. The narrower result is that `b<2` alone is not a mechanism test in these communities.

### 13:30–18:30 — Live demo: C012 fails safely before an effect estimate

Goal: demonstrate two different calibration layers without calculating the real red-vs-blue effect.

#### Step 1 — Show the frozen evidence split

```bash
jq '{question,evidence_roles,access_guard}' claims/C012.json
```

Point out:

- odd labs 1/3/5/7 = discovery;
- even labs 2/4/6/8 = confirmation;
- split frozen before CSV values;
- confirmation remains unopened.

#### Step 2 — Run statistical calibration

```bash
uv run analysis/c012_calibrate.py
```

Expected final calibration:

- true 0.00 °C: 3.0% pass;
- +0.05 °C: 47.6% power;
- +0.10 °C: 93.9% power;
- +0.15 °C: 99.9% power.

Explain the failure that preceded this final version:

- participant-dominated inverse-variance pooling was anti-conservative across heterogeneous labs;
- laboratory-level equal-weight inference fixed it.

Key sentence:

> “If the claim is that an effect replicates across laboratories, the laboratory—not the number of participant-minutes—is the unit that must calibrate the claim.”

#### Step 3 — Run the semantic gate

```bash
uv run analysis/c012_semantic_gate.py --data-dir cache/c012-discovery
```

Expected headline:

- lab 1 usable skin sites: back, shin;
- lab 7 usable skin sites: hand;
- common skin site across discovery labs: none;
- `HRinst` absent in lab 1;
- `HRave` has inadequate terminal-window coverage in lab 7;
- semantic gate: STOP.

Then show:

```bash
jq '{stop_reason,outcome_effects_computed,confirmation_accessed}' claims/C012.json
```

Punchline:

> **The statistics were calibrated. The measurement was not comparable. So we stopped before seeing whether the effect looked exciting.**

#### Offline fallback

Do not make the live talk dependent on the network. Prefetch only the discovery files. If the local cache is unavailable, show the committed deterministic artifacts:

```bash
cat results/c012_calibration.json
cat results/c012_semantic_gate.json
```

The live demo should never open labs 2/4/6/8.

### 18:30–22:00 — The reusable protocol

Show one slide with nine gates, grouped into three questions.

**Is the question identifiable?**

1. exact-discriminator prior-art search;
2. decisive observable exists;
3. measurement semantics/unit alignment match.

**Is the analysis calibrated?**

4. empirical known-null behavior;
5. known-positive/power behavior;
6. model applicability distinct from estimator output;
7. replication at the true independent unit.

**Did the result survive new evidence?**

8. source-level discovery/confirmation guards;
9. deterministic rerun + independent verification + stop rule.

Show the tiny `claim.json` and append-only ledger patterns from `SCIENTIFIC-LOOP.md`, not a software architecture diagram.

### 22:00–24:00 — What remains unknown

Say clearly:

> “This project shows that these gates can prevent us from fooling ourselves. It does **not** show that this agent chooses better scientific questions.”

Introduce the prospective benchmark:

- unpublished/prospective source-level confirmation;
- identical candidate packets;
- agent versus rule/random/human selectors;
- neutral common executor;
- confirmation success and blinded scientific usefulness reported separately;
- calibration of the agent's own predicted confirmation probability.

End on:

> **Maybe the first job of an AI scientist is not to discover faster. It is to know what evidence would make it stop.**

## Slide/storyboard plan

1. Title + challenge.
2. “What would count as discovery?” — confirmation and usefulness, not p-value.
3. Scientific loop with STOP gates.
4. C001 nominal null versus empirical replicate null.
5. C002 estimate versus applicability.
6. C003 discovery plots.
7. C003 confirmation plots.
8. C012 evidence split.
9. Live calibration terminal.
10. Live semantic gate terminal.
11. Nine reusable gates.
12. Minimal claim + ledger files.
13. Prospective agent benchmark.
14. Closing sentence.

Keep charts large and tables tiny. One visual fact per slide.

## Demo safety checklist

Before the session:

- [ ] clean checkout of the committed talk checkpoint;
- [ ] `uv` dependencies warmed in cache;
- [ ] discovery-only C012 files present under ignored `cache/c012-discovery/`;
- [ ] verify no `lab2`, `lab4`, `lab6`, `lab8` file exists in the C012 cache;
- [ ] run `uv run analysis/c012_calibrate.py` twice and compare result hash;
- [ ] run semantic gate once and compare committed result;
- [ ] disable network for rehearsal to prove offline operation;
- [ ] keep screenshots/precomputed JSON as fallback;
- [ ] do not improvise a real hue-effect calculation on stage.

## Claims to avoid

Do not say:

- “AI failed fourteen times.”
- “AI cannot discover science.”
- “These gates are individually novel.”
- “C003 disproves dominance stabilization.”
- “C012 shows there is no physiological Hue–Heat effect.”

Do say:

- explicit gates repeatedly changed whether a scientific-looking result deserved belief;
- confirmation evidence was sometimes deliberately left unopened;
- one positive discovery was allowed to fail independent confirmation;
- the workflow, code and failures are reviewable and reproducible;
- whether an agent selects better questions remains an open empirical question.

## Short CFP-style abstract

Can an AI agent discover a scientific result—and know when not to believe it? I gave an agent open papers and datasets, let it write and run Python, and required every candidate to survive calibration and independent evidence. The interesting outcomes were mostly stops: a significant signal failed a real technical-null check; a plausible dynamical estimate failed model applicability; a positive ecological discovery failed frozen independent confirmation; and a calibrated eight-lab analysis stopped because nominally standard physiology columns represented incompatible measurements. I will reproduce one of these gates live and show a small open workflow for claim freezing, empirical-null and known-positive calibration, source-level confirmation holds, replication-unit checks and deterministic verification. The result is not a claim that AI cannot do science. It is a proposal to treat research agents like uncalibrated scientific instruments—and make them earn the right to believe their own outputs.
