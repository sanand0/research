# Checkpoint 004 — within-generation prediction / PrefixResample DE

Date: 2026-09-20
Status: Candidate 3 rejected in development; confirmation reserve untouched.

## Question

SciPy dithers differential weight F once per generation. Under a tiny objective budget, can the first few trial outcomes identify a bad generation-level F early enough to reallocate the remaining expensive evaluations?

Predeclared diagnostic policy before fitting anything: inspect the first quarter of a 2D-population pass; if it has zero accepted trials, treat the current F as suspect. No trigger or threshold tuning was performed.

## Predictive diagnostic

generation_trace.py is an ordinary immediate best/1/bin implementation with a 2D Halton population and F sampled uniformly from 0.5 to 1, recording every trial. Development data are split before analysis:

- BBOB discovery: f={1,6,10,15,20}, instance 1, seeds 1–5.
- BBOB validation: f={3,8,12,17,23}, instance 2, seeds 6–10.
- Synthetic quadratics: d={5,10}, condition={1,100,1e4}, rotated/unrotated; seeds 1–5 discovery, 6–10 validation.

At generation level on disjoint BBOB validation:
- early acceptance count vs remaining acceptance count Spearman ~0.57;
- early normalized gain vs remaining normalized gain Spearman ~0.52;
- AUROC for predicting any remaining acceptance ~0.75;
- zero-early-accept marks ~43% of generations.

Generations are not independent evidence. Aggregating first by run, then taking medians across seeds at each BBOB problem unit (10 units):
- mean evaluation fraction nominally skipped: 0.303; problem-bootstrap 95% CI [0.195, 0.420];
- mean fraction of normalized remaining gain discarded: 0.208 [0.114, 0.326];
- mean fraction of remaining accepted trials discarded: 0.309 [0.200, 0.434].

The rule is especially unsafe on f23: depending on dimension, it labels roughly 59–64% of evaluations as skippable while those evaluations contain ~48–62% of remaining gain.

Thus early outcomes are predictive, but “predictably lower yield” is not the same as “safe to skip.”

## Candidate 3 implementations

Two versions tested the same fixed quarter/zero-success trigger.

1. run_sequential_best1: abort the current pass after the failed prefix, resample F, and restart target traversal. This changes target scheduling and performed poorly immediately. On the 20-run tuning slice it beat its exact mechanism-off wrapper only 5/20 times; paired median 200D advantage -0.453 decades. Rejected without a broad pilot.

2. PrefixResampleBest1 / SwitchF: cleaner public SciPy callable strategy. It does not skip any objective calls or restart target positions. If the first quarter causes no population change, it resamples F only for the unevaluated remainder of that pass. This isolates the hypothesized value of revoking a bad generation-level F.

SwitchF vs identical custom-strategy control on 40 development problem units, median over two stochastic seeds first:

- 50D: mean advantage +0.005 decades, median +0.018, 22/40 wins, mean bootstrap CI [-0.103,+0.135].
- 100D: +0.073 mean, +0.003 median, 21/40 wins, CI [-0.070,+0.255].
- 200D: +0.045 mean, -0.006 median, 19/40 wins, CI [-0.111,+0.208].

Successes by 200D were 12/80 to 1e-2 and 8/80 to 1e-5 for SwitchF versus 11/80 and 8/80 for its exact control. This is not a meaningful improvement.

Decision: reject Candidate 3; do not tune prefix, success threshold, F distribution, or confirmation data.

## Novelty assessment

The exact “generation-level F is a revocable commitment after a fixed prefix” rule did not surface in targeted searches, but adjacent mechanisms are mature:
- SciPy defines dithering as one F draw per generation.
- asynchronous or steady-state DE removes generation synchronization and updates after each trial;
- adaptive DE has extensive per-individual, success-history, strategy, population, and composite parameter-control literature;
- expensive-optimization DE already focuses heavily on function-evaluation efficiency.

So SwitchF is at most a small scheduling mechanism built from known ideas. Its null development result makes a stronger novelty search unwarranted.

## Scientific lesson / redirect

The important distinction is predictability versus decision value. Early failures predict lower subsequent yield, but the supposedly low-yield remainder still carries enough useful search progress that aggressively reallocating it does not improve the optimizer. Optimizing short-term acceptance is a poor proxy for final objective progress.

The obvious next “failure rescue” idea — line-searching or rescaling along a rejected DE direction — is also crowded: scale-factor local search in DE dates to Neri and Tirronen (2009). Batch 5 should therefore reset the invention search around the strongest empirical complementarity found so far: tiny-population DE is very efficient early, while CMA is stronger later on conditioned 10D problems. Novelty-screen budget-aware DE→CMA handoff and related hybrid methods before coding; only proceed if a compact handoff criterion has genuine headroom beyond existing hybrids.

## Confirmation reserve

Untouched: BBOB f={2,7,11,16,21}, instances 11–15, d=20.
