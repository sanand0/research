# Checkpoint 003 — geometry loss and low-budget population size

Date: 2026-09-10
Status: diagnosis complete; no Candidate 3 promoted; confirmation reserve untouched.

## Question

After Batch 2 showed that DE donor proposals already contain useful inverse-Hessian geometry, where is that information lost, and how much of the CMA gap is actually caused by insufficient generations under a strict 50–200D budget?

## Geometry diagnosis

Fresh synthetic quadratics, d={5,10}, condition={1,100,1e4}, rotated/unrotated, best/1 mutation, 5D population, Halton initialization, strict 100D diagnostic budget.

On rotated condition-1e4 cases, pooling dimensions/seeds/generations:
- inverse donor covariance vs Hessian directional curvature: median Spearman ~0.88;
- after binomial crossover CR=0.7: ~0.49;
- with CR=1: ~0.70;
- accepted-step covariance after selection: ~0.46 at CR=0.7 and ~0.77 at CR=1.

Median final diagnostic error: CR=0.7 ~1064; CR=1 ~427. Thus crossover can materially destroy contour-fitting correlations. Selection causes additional loss, but crossover is the larger geometry break on rotated cases.

BBOB transfer is heterogeneous. At popsize=5D, CR=1 vs CR=0.7 at 200D over 40 problem units: mean advantage +0.076 log10 decades, median +0.066, 24/40 wins, but the mean bootstrap interval crosses zero widely. By function, median advantages include f10 +0.901, f12 +1.238, f1 -1.655, f3 -0.224. Full-vector mutation is therefore not a robust algorithm; it is evidence that coordinate crossover is harmful on some correlated landscapes and helpful on separable ones.

## Baseline correction: population size

A bounded tuning pass found that even the previous 5D SciPy population was too large for 200D budgets.

Tuning slice median log10 error at 200D:
- SciPy best1bin, Halton, population 2D: +0.051
- population 3D: +0.317
- population 5D: +0.681
- CMA sigma0=0.30: +0.187
- modDE L-SHADE initial 4D: +0.064

Broader development, 80 runs each:

| Algorithm | Median log10 error @200D | <=1e-2 | <=1e-5 |
|---|---:|---:|---:|
| SciPy best1bin, p=2D, Halton | +0.238 | 11/80 | 8/80 |
| CMA-ES, sigma0=0.30 box width | +0.187 | 18/80 | 8/80 |
| modDE L-SHADE modules, p0=4D | +0.289 | 10/80 | 4/80 |
| prior SciPy p=5D | +0.566 | 7/80 | 2/80 |

At problem-unit level, 2D SciPy beats 5D SciPy on 34/40 units; median advantage +0.557 decades. Against CMA it wins 17/40; median disadvantage only -0.134 decades, although mean disadvantage is larger (-0.663) because CMA reaches much smaller errors on easy functions.

Dimension split at 200D:
- 5D median log-errors: SciPy 2D +0.091, CMA +0.086, L-SHADE-4D +0.152.
- 10D: SciPy +0.301, CMA +0.214, L-SHADE-4D +0.609.

Decision: update trusted baselines to SciPy p=2D and modDE L-SHADE p0=4D. The apparent CMA gap was partly a population/generation-count artifact.

## Novelty/headroom assessment after three batches

Do **not** claim CR=1, covariance/eigen-coordinate crossover, adaptive CR, population resizing, or restarts as Candidate 3: all are established mechanisms. There remains modest but structured headroom at 10D and on conditioned functions, but another geometry adaptation is unlikely to be novel enough.

Next high-value branch: evaluation scheduling rather than search geometry. Test whether early outcomes within a generation predict the quality of the remaining trials. If so, a sequential generation mechanism could abort a bad generation-level F/CR draw and resample parameters before spending the full NP objective calls. This targets wasted evaluations directly and is especially relevant when one simulation is expensive.

Before implementation, screen against asynchronous DE and per-evaluation parameter adaptation. Candidate 3 exists only if the predictive diagnostic is strong and the exact mechanism has novelty headroom.

## Confirmation reserve

Untouched: BBOB f={2,7,11,16,21}, instances 11–15, d=20.
