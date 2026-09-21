# Checkpoint 002 — rejected-trial geometry / RejDE

Date: 2026-09-10
Status: Candidate 2 rejected in development; confirmation reserve untouched.

## Question

Can DE extract useful curvature information from objective evaluations it normally discards—especially rejected trial-parent pairs—without spending any additional objective evaluations?

Candidate 2 (`RejDE`) whitens one generation of observed step directions by their proposal covariance, estimates which whitened directions are disproportionately rejected, then contracts those directions in the next generation. It is determinant-normalized so the intended intervention is shape rather than global scale.

Novelty classification: **useful combination / transfer**, not a new mechanism. Active CMA uses bad offspring in covariance updates; HE-ES directly estimates Hessian curvature; DE covariance/eigen-space methods and failure-information adaptation already exist. No exact match to the proposal-whitened rejection construction surfaced in the targeted search, but that is insufficient for a strong novelty claim.

## Mechanism evidence

Fresh synthetic quadratics, d={5,10}, condition={1,100,1e4}, rotated/unrotated, 20 seeds, 100D diagnostic budget:

- Raw rejected-step covariance is not a stiffness estimator. It is strongly anti-correlated with Hessian curvature on conditioned problems.
- The reason appears to be DE's existing contour fitting: **inverse proposal covariance** predicts Hessian directional curvature with median Spearman about 0.74–0.94 on conditioned quadratics.
- Removing proposal anisotropy exposes some extra rejection signal on rotated problems: rejection contrast vs true curvature median Spearman about +0.45 (condition 100) and +0.54 (condition 1e4). Axis-aligned cases show the opposite sign (~-0.39), predicting a regression regime.

This was strong enough to justify one implementation, but not a general covariance claim.

## Optimization result

Development BBOB remains f={1,3,6,8,10,12,15,17,20,23}, instances={1,2}, d={5,10}, seeds={1,2}, strict 200D budget.

RejDE vs the exact mechanism-off control through the same SciPy custom-strategy/vectorized path, problem unit=(function,instance,dimension), median over seeds:

- 200D mean log10 advantage: **-0.063 decades**
- median advantage: **-0.059**
- wins: **15/40**
- problem-bootstrap 95% CI for mean: **[-0.141,+0.012]**
- median CI: **[-0.090,+0.009]**

Against built-in deferred SciPy the conclusion is similar: mean -0.043, median -0.051, 17/40 wins.

Fresh synthetic 200D matched on/off tests give only a weak pocket at condition 100 rotated (+0.092 mean decades, 7/10 wins; CI crosses zero). Condition 1e4 rotated is essentially null and isotropic/axis-aligned cases often regress.

Decision: **reject RejDE; no parameter tuning and no confirmation run.** The incremental curvature signal is statistically visible but too noisy / poorly actionable to improve optimization reliably.

## New explanation to test

The most surprising evidence is that DE's *proposal covariance already contains a strong inverse-Hessian signal*. Therefore the large CMA-vs-DE gap on conditioned functions cannot simply be explained by DE failing to learn geometry.

Batch 3 should diagnose where this useful geometry is lost or underused. Highest-value tests:

1. Compare full-vector DE mutation (CR=1) with binomial crossover on rotated vs axis-aligned quadratics/BBOB to quantify how much crossover destroys contour-fitting correlations. This is diagnosis/parameter behavior, not invention.
2. Compare proposal covariance before vs after crossover and accepted-step covariance, with true Hessian available only on synthetic evaluator problems.
3. Test whether the dominant remaining loss is crossover, global step scale, greedy selection, or insufficient generations. Only then propose Candidate 3.

Do not build another generic covariance/eigen-space adaptation: that search space is crowded and the diagnostic says DE already has useful shape information.
