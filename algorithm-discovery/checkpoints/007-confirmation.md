# Checkpoint 007 — frozen BBOB confirmation

Date: 2026-09-20
Status: preregistered primary criterion failed narrowly at 50D; no retuning or reinterpretation.

## Frozen protocol

Before the confirmation comparison, Batch 6 fixed:
- BBOB functions f={2,7,11,16,21};
- instances 11–15;
- dimension 20;
- optimizer seeds 1,2;
- budgets/milestones 50D, 100D, 200D;
- SciPy default-like best1bin p15 LHS;
- SciPy best1bin p2 Halton;
- modDE L-SHADE p0=2D;
- CMA-ES sigma0=0.30;
- uncertainty unit = function × instance, median over seeds first.

Primary pass criterion:
1. SciPy p2 must beat p15 by at least 0.5 log10 error decades median at both 50D and 100D.
2. SciPy p2 must win at least 70% of the 25 problem units at both milestones.

The machine-readable protocol is results/confirmation-protocol.json.

## Procedural caveat

The algorithm settings and pass criterion were already frozen in checkpoints/006-pk-transfer.md and STATE.md, and no held-out performance result had been inspected. However, before the protocol JSON self-check succeeded, test_confirmation.py ran a strict-budget smoke test on one reserved problem (f2, instance 11, 20D) for 400 calls per optimizer. That test asserted only evaluation accounting; it did not save or display objective/error results and no parameter choice changed afterward.

Therefore this confirmation is performance-unseen but not perfectly pristine. The test was subsequently moved to non-reserve f1/instance1/5D so future verification does not touch held-out cases.

A separate serialization bug initially prevented confirm_bbob.py from starting; the confirmation ledger was absent at that point. It was fixed without changing protocol contents.

## Primary result

The frozen primary criterion did not pass.

SciPy p2 versus default p15, problem unit = function×instance:

| Budget | Median advantage | Mean advantage | Wins | Win rate | Bootstrap mean 95% CI | Criterion |
|---|---:|---:|---:|---:|---:|---|
| 50D | +0.349 | +0.556 | 23/25 | 92% | [0.344, 0.790] | FAIL: median < +0.500 |
| 100D | +0.537 | +0.884 | 23/25 | 92% | [0.537, 1.257] | PASS |
| 200D | +0.904 | +1.410 | 23/25 | 92% | [0.830, 2.036] | descriptive only |

At 50D, the bootstrap median interval is [0.192, 0.561]. The effect direction is broad but the preregistered point-estimate magnitude threshold is missed. Do not weaken the threshold after seeing this.

## Landscape heterogeneity

Median p2 advantage over p15 across the five held-out instances of each function:

| Function | 50D | 100D | 200D | Wins at 50D |
|---|---:|---:|---:|---:|
| f2 | +1.59 | +2.39 | +4.06 | 5/5 |
| f7 | +0.40 | +0.54 | +0.92 | 5/5 |
| f11 | +0.21 | +0.19 | +0.13 | 5/5 |
| f16 | +0.04 | +0.00 | +0.03 | 3/5 |
| f21 | +0.56 | +0.93 | +1.85 | 5/5 |

This explains the failed magnitude criterion: smaller population is broadly non-worse/better, but the size of the benefit is strongly landscape-dependent. The claim "2D dramatically beats p15 everywhere" is too strong.

## Frozen algorithms on confirmation

Median log10 error across 50 runs/algorithm:

| Algorithm | 50D | 100D | 200D | <=1e-2 | <=1e-5 |
|---|---:|---:|---:|---:|---:|
| SciPy p15 | +2.365 | +2.274 | +2.007 | 0/50 | 0/50 |
| SciPy p2 | +1.958 | +1.602 | +1.212 | 2/50 | 0/50 |
| L-SHADE p2 | +1.839 | +1.339 | +0.987 | 6/50 | 0/50 |
| CMA-ES | +1.595 | +1.398 | +1.356 | 1/50 | 1/50 |

Target hits are sparse on these hard 20D held-out cases, so NFE-to-target is not a robust discriminator.

## Secondary descriptive questions

### Early-DE / late-CMA crossover

It does not reproduce cleanly on this 20D holdout.

SciPy p2 versus CMA:
- 50D: median -0.002 decades, 12/25 p2 wins;
- 100D: -0.009, 12/25;
- 200D: +0.054, 13/25.

They are essentially tied by problem-unit median at all three budgets. The strong late-CMA advantage seen in the 5D PK inverse problem and some 5D/10D development cases is therefore not universal.

### L-SHADE p2 versus plain SciPy p2

L-SHADE is comparable early and stronger later:
- p2 vs L-SHADE at 50D: median 0.000, p2 13/25 wins;
- 100D: -0.093, p2 8/25 wins;
- 200D: -0.227, p2 6/25 wins.

Thus a tiny population remains useful, but adaptive DE is a better robust late-budget choice on this held-out 20D set.

## What is confirmed, and what is not

Confirmed directionally:
- conventional p15 SciPy DE is a poor use of a 50D–200D budget in this bounded regime;
- reducing the population to p2 improves fixed-budget error on 23/25 held-out problem units;
- the effect grows with budget on average because p2 obtains far more evolutionary updates.

Not confirmed as preregistered:
- a universal or typical at-least-0.5-decade p2 advantage by 50D.

Not confirmed:
- a universal p2-to-CMA crossover near 100D–200D.

The defensible operating-regime statement is:

Under very tight evaluation budgets, DE population size is a first-order tuning variable. Around 2D population members can be dramatically better than default-like 15D settings on some problems and is broadly better in these experiments, but the magnitude is landscape-dependent; adaptive DE and CMA remain competitive or better depending on landscape and budget.

## Talk decision

Do not present "2D is the new default" or the preregistered confirmation as a success.

A stronger SciPy India story is the scientific loop itself:
1. Try to invent a new DE operator.
2. Falsify four plausible mechanisms.
3. Discover that a boring parameter — population size under a strict evaluation budget — dominates many clever mechanisms.
4. Transfer that effect strongly to a real simulation-fitting problem.
5. Preregister a held-out confirmation and miss the strict effect-size criterion, despite 23/25 directional wins.
6. Show why benchmark averages, objective depth, parameter recovery, and operating regime must be separated.

## Next step

No more tuning against BBOB confirmation.

Batch 8, if continued, should convert the research into the talk/live experiment:
- finalize the reproducible report;
- update the live harness to a fresh audience-selected inverse problem or quadratic variation;
- commit a prediction before running it;
- make the live point "budget changes the algorithm you should want", not "p2 always wins";
- preserve the failed preregistered criterion visibly.
