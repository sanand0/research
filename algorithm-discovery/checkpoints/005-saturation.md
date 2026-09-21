# Checkpoint 005 — hybrid novelty screen, micro-populations, and saturation

Date: 2026-09-20
Status: Candidate 4 rejected; generic scalar-objective DE invention branch redirected; confirmation reserve untouched.

## Intended branch: DE → CMA handoff

The empirical motivation was real: tiny-population DE is often strongest early, while CMA-ES is stronger later, especially in 10D conditioned problems.

The novelty screen blocks a handoff candidate before implementation:
- DE/CMA hybrids have existed for well over a decade.
- Published sequential hybrids explicitly run one algorithm after another for a prefixed number of generations.
- Sequential algorithm portfolios learn which optimizer to run and when to stop it.
- Recent work learns switching times in sequential hybrid evolutionary algorithms with Q-learning/deep Q-learning.
- Current software such as fcmaes even documents chaining DE → CMA emitters.

Decision: do not spend development evaluations rediscovering a fixed or adaptive DE→CMA switch. It would be, at best, a useful combination/portfolio mechanism rather than the small new algorithm sought here.

## Baseline correction: the micro-population regime goes further

A final bounded population-size check was warranted because Batch 3 had tested 2D, 3D, 5D but not 1D.

Tuning slice at 200D:
- SciPy best1bin p=1D: median log10 error +0.996.
- SciPy best1bin p=2D: +0.051.
- modDE L-SHADE p0=1D: +0.333.
- modDE L-SHADE p0=2D: +0.093.
- modDE L-SHADE p0=4D: +0.064.
- CMA-ES: +0.187.

So “smaller is always better” is false. There is a sharp diversity/generation trade-off.

Broader development confirms that the adaptive-DE baseline should move from 4D to 2D:
- L-SHADE p0=2D median 200D log-error +0.197, versus p0=4D +0.289.
- CMA-ES +0.187.
- SciPy p=2D +0.238.

Against CMA at 200D, L-SHADE-2D loses by only +0.168 decades median over 40 problem units, but CMA has a larger mean advantage (+0.754) because it reaches much deeper errors on easy/moderately conditioned problems. At 5D the median gap is only +0.042; at 10D it is +0.222.

A virtual-best oracle over SciPy-2D, L-SHADE-2D, and CMA shows:
- 50D winners: SciPy 21/40, L-SHADE 6/40, CMA 13/40.
- 100D: 14/40, 10/40, 16/40.
- 200D: 6/40, 15/40, 19/40.
At 200D CMA's median gap to this oracle is only 0.039 decades (mean 0.238). Thus there is real complementarity, but most of the remaining aggregate headroom is already an algorithm-selection/portfolio problem, which is established prior art.

## Candidate 4: condition-aware objective-free initialization

The failure of p=1D suggested an affine-geometry explanation. D points in D dimensions have centered affine rank at most D-1. D+1 Halton points restore full rank, but their sample covariance is often extremely ill-conditioned. In 10D, median centered-covariance condition numbers across Halton seeds are roughly:
- 11 points: ~610
- 15 points: ~40
- 18 points: ~20
- 20 points: ~15

This motivated CondInitDE: before any objective evaluation, generate a Halton prefix and choose the shortest prefix whose centered covariance condition number is <=20 (cap 4D). The threshold was fixed from objective-free design geometry, not optimized on objective results. SciPy's public array-valued init API makes this a tiny wrapper.

Novelty classification: a potentially new population-initialization rule, but only moderate novelty confidence because DE population-size/initialization literature is extensive. It is parameter-policy innovation, not a new mutation mechanism.

Result on the tuning slice versus an exact custom-Halton fixed-2D control:
- 50D: +0.050 median paired advantage, +0.193 mean, 11/20 wins.
- 100D: 0.000 median, +0.033 mean, 9/20 wins.
- 200D: 0.000 median, -0.113 mean, 7/20 wins.

The D+1 variant itself improves on D points but remains poor (median +0.682 versus +0.996 for D points and +0.051 for 2D). Full rank / design conditioning explains part of the micro-population cliff but does not create a better optimizer.

Decision: reject CondInitDE without a broad pilot; do not tune the condition threshold.

## Other baseline probe

SciPy DIRECT was added as a missing bounded deterministic baseline. The combined exploratory command timed out because DIRECT cost roughly tens of milliseconds of optimizer overhead per evaluation. Before termination it appended 30 engineering-probe rows covering 16 unique tune cases; 14 keys were duplicated by the interrupted/replayed command. Median recorded overhead was ~49 ms/evaluation and total DIRECT wall time was ~993 s. These rows are explicitly excluded from scientific conclusions and retained in the append-only ledger for provenance. `results/ledger-audit.json` separates the 2,120 unique scientific rows from these probe rows.

## Five-batch assessment

Four structural candidates have failed:
1. PairDE: donor derandomization.
2. RejDE: rejected-trial curvature correction.
3. PrefixResample/SwitchF: within-generation F revocation.
4. CondInitDE: condition-aware low-discrepancy population sizing.

Several apparently promising follow-ups were stopped before coding because they are direct prior art: covariance/eigen crossover, adaptive CR/population resizing, archive-backed micro-DE, DE→CMA handoff, algorithm portfolios, and rejected-direction scale-factor local search.

The useful scientific result is increasingly the bounded operating regime, not a new DE operator: with only 200D calls, population sizes around 2D are dramatically more competitive than conventional settings, but going down to D is too small. CMA remains the most reliable deep-convergence baseline, while tiny DE is often better early.

This is a legitimate saturation point for generic scalar-objective DE invention. More benchmark-only operator search is unlikely to change the explanation enough to justify its selection cost.

## Redirect

Batch 6 should test the strongest surviving empirical claim on a scientific inverse problem before doing more algorithm invention:
- choose one reproducible bounded 5–10 parameter simulation-fitting problem (ODE or similarly transparent model);
- compare default SciPy DE, tuned 2D SciPy DE, L-SHADE-2D, and CMA under exact 50D/100D/200D budgets;
- keep simulator calls auditable and solutions independently checkable;
- if the tiny-population advantage transfers, retain this operating-regime result as a possible talk contribution and search for mechanisms specifically exposed by inverse-problem structure;
- if it does not transfer, stop this target rather than continue BBOB-driven invention.

Confirmation BBOB remains untouched.
