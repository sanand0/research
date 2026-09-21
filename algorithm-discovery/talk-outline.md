# SciPy India 2026 talk outline

Working thesis:

> **Budget is part of the algorithm. AI can accelerate the scientific loop, but the valuable result may be the experiment that kills the clever story.**

## 1. Cold open — 2 minutes

"I asked an AI research loop to invent a better optimizer. It failed four times."

Show the four candidate names and one-line mechanisms. Do not explain them yet.

Then show the surprising comparison: same SciPy DE, same objective, same strict 50D budget, only population size changes.

Ask: "Which one is actually getting a chance to learn?"

## 2. Why the problem matters — 3 minutes

Scientific parameter fitting where one simulator call is expensive.

Explain the budget in evaluations per dimension, not wall time.

Show the 5D arithmetic:
- p15: 75 initial calls; only ~2.3 later population passes by 50D.
- p2: 10 initial calls; ~24 later passes.

## 3. The invention loop — 7 minutes

Use four quick falsification cards:

1. PairDE — balance donor usage. Failed.
2. RejDE — learn from rejected steps. Signal was real; intervention failed.
3. SwitchF — abort bad generation-level parameter draws. Prediction worked; decision rule failed.
4. CondInitDE — choose population from initial design geometry. Explanation partly right; optimizer still failed.

The recurring message: intermediate mechanistic evidence is not optimization evidence.

## 4. The boring baseline wins — 5 minutes

Show D vs 2D vs larger populations.

Explain the diversity/generation trade-off.

Important wording:
- "2D worked well here."
- Not: "2D is optimal."
- Not: "2D should be SciPy's default."

Mention L-SHADE and CMA as strong controls.

## 5. Leave BBOB — 6 minutes

Introduce the five-parameter two-compartment PK inverse problem.

Show the independently verified simulator, p2 vs p15 on all 8 subjects, the population/init 2×2 ablation, and target-hitting efficiency.

Then show the budget-dependent winner: p2 strong early; CMA extremely strong late on PK.

Add the identifiability caution: best curve fit need not mean best recovered parameters.

## 6. Preregister the claim — 4 minutes

Show the exact held-out criterion **before** the result:
- at least 0.5 decade median p2 advantage at 50D and 100D;
- at least 70% problem-unit wins.

Then reveal:
- 50D: +0.349, 23/25 — FAIL.
- 100D: +0.537, 23/25 — PASS.

Say explicitly: "The direction replicated. My promised effect size did not."

Show f2 vs f16 to make landscape heterogeneity concrete.

## 7. Live experiment — 5–8 minutes

Ask the audience for:
- D = 5 / 10 / 20;
- condition number;
- rotated? yes/no;
- seed.

Before running:
1. state a prediction aloud;
2. enter the same text in --prediction;
3. run live.py;
4. point to the printed SHA-256 commitment;
5. reveal 50D/100D/200D winners.

The prediction should be mechanistic and falsifiable, not "p2 will win."

Good prediction form:

> "With this budget and conditioning, I expect p15 to be disadvantaged by too few update rounds. Between p2, adaptive DE and CMA, I expect ___ because ___. I would change my mind if ___."

If the result disagrees, that is the demo working.

## 8. Close — 2 minutes

Three takeaways:

1. **Budget defines the operating regime.** Defaults tuned for ordinary budgets may be poor under simulation scarcity.
2. **A plausible mechanism is not a result.** Test the intervention, not only the explanatory signal.
3. **Precommitment makes live discovery credible.** A failed threshold can be more informative than a post-hoc win.

Final line:

> "The AI did not invent the optimizer I asked for. It helped me discover which story I should stop believing."
