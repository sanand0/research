# Checkpoint 006 — scientific transfer to a two-compartment PK inverse problem

Date: 2026-09-20
Status: low-budget population-size regime transfers strongly; operating-regime claim merits frozen confirmation; BBOB confirmation reserve untouched.

## Scientific problem

Independent transfer target: noiseless oral two-compartment pharmacokinetic parameter fitting.

Five positive parameters are fitted:
- ka — first-order absorption rate;
- CL — central clearance;
- Vc — central volume;
- Q — intercompartmental clearance;
- Vp — peripheral volume.

State equations use a depot, central compartment, and peripheral compartment. A 100 mg oral dose is observed at 15 fixed times from 0.25 to 48 hours. This is the standard two-compartment first-order-absorption structure used in pharmacokinetic modeling.

Optimization is performed in normalized [0,1]^5 coordinates mapped logarithmically to physical parameter bounds. Eight synthetic subjects were generated before optimizer runs with a scrambled Sobol design constrained to the central 70% of the log-bounds. Data are noiseless. Optimizer seeds are 1,2,3.

Frozen budgets: 50D=250, 100D=500, 200D=1000 simulator calls.

Objective: mean squared natural-log concentration error.
Targets:
- 1e-4 objective: about 1% RMS log-concentration error;
- 1e-6 objective: about 0.1%.

Independent parameter-recovery metric: RMS natural-log fitted/truth ratio; 0.05 and 0.01 are roughly 5% and 1% errors.

Protocol: results/pk-protocol.json.

## Independent simulator verification

The fast evaluator uses the exact matrix exponential of the linear three-state ODE. Before optimizer comparison it was checked against scipy.integrate.solve_ivp using DOP853 at tight tolerances on the eight truths plus eight independent interior parameter sets.

Maximum discrepancy:
- concentration absolute error: 5.50e-11;
- concentration relative error: 1.11e-11.

After optimization, all 144 final primary+ablation fits were independently re-evaluated with solve_ivp. Maximum objective difference versus the matrix-exponential evaluator was 2.67e-13 absolute (5.9e-6 relative, occurring only at extremely tiny objectives).

Thus the optimization result is not an evaluator artifact.

## Primary comparison

Frozen algorithms:
1. SciPy default-ish DE: best1bin, popsize=15D, Latin hypercube, F~U(0.5,1), CR=0.7, no polish.
2. SciPy tiny DE: same best1bin/F/CR, popsize=2D, Halton.
3. modDE L-SHADE: previously tuned p0=2D.
4. CMA-ES: sigma0=0.30 box width.

96 runs total: 8 subjects x 3 stochastic seeds x 4 algorithms. Every run received at most 1000 simulator calls; zero budget overshoots.

Median log10 objective across 24 runs/algorithm:

| Algorithm | 50D | 100D | 200D |
|---|---:|---:|---:|
| SciPy default p15 | -1.912 | -2.267 | -3.058 |
| SciPy p2 Halton | **-3.261** | -4.713 | -6.052 |
| L-SHADE p2 | -2.749 | -3.928 | -6.093 |
| CMA-ES | -2.604 | **-4.786** | **-10.618** |

Median parameter RMS log-error:

| Algorithm | 50D | 100D | 200D |
|---|---:|---:|---:|
| SciPy default p15 | 0.310 | 0.262 | 0.109 |
| SciPy p2 Halton | **0.165** | 0.047 | 0.0081 |
| L-SHADE p2 | 0.268 | 0.108 | 0.0046 |
| CMA-ES | 0.236 | **0.0468** | **7.7e-5** |

## Problem-level transfer evidence

Problem unit = synthetic subject; first take median over three optimizer seeds.

SciPy p2 versus default p15:
- 50D: +1.324 mean log10 advantage, +1.426 median, 8/8 subjects; bootstrap mean CI [1.100, 1.528].
- 100D: +2.446 mean, +2.292 median, 8/8; CI [1.999, 2.959].
- 200D: +3.126 mean, +3.025 median, 8/8; CI [2.748, 3.523].

Thus the low-population effect transfers decisively to this scientific inverse problem.

SciPy p2 versus CMA:
- 50D: +0.624 mean advantage, +0.731 median, 6/8 subjects; CI [0.144, 1.048].
- 100D: +0.242 mean, +0.285 median, 4/8; CI [-0.459, 0.904].
- 200D: -3.969 mean, -4.887 median, 0/8; CI [-5.438, -2.405].

This cleanly reproduces the development regime: tiny DE is unusually efficient early, roughly tied around 100D, and CMA dominates deep convergence by 200D.

SciPy p2 versus L-SHADE p2:
- 50D: +0.626 mean, 8/8 wins; CI [0.383, 0.875].
- 100D: +0.782 mean, 7/8 wins; CI [0.359, 1.262].
- 200D: -0.092 mean, 3/8 wins; CI crosses zero widely.

## Target-hitting efficiency

Objective <=1e-4:
- SciPy p2: 22/24 successes, median 70.7D evaluations among successes.
- CMA: 21/24, median 84.8D.
- L-SHADE p2: 24/24, median 101.0D.
- default SciPy p15: 1/24, 188.4D.

Objective <=1e-6:
- CMA: 19/24, median 111.4D.
- SciPy p2: 13/24, 123.6D.
- L-SHADE p2: 12/24, 141.2D.
- default p15: 0/24.

Parameter RMS log-error <=0.05:
- SciPy p2: 18/24, median 64.8D.
- CMA: 19/24, median 72.8D.
- L-SHADE: 19/24, median 102.6D.
- default p15: 5/24, median 155.4D.

## Population-size ablation

Primary SciPy p2 differs from default in both population size and initialization, so a frozen 2x2 ablation was run:
- p2 LHS;
- p2 Halton;
- p15 LHS;
- p15 Halton.

Population effect with LHS held fixed, p2 vs p15:
- 50D: +1.319 mean decades, 8/8 subjects.
- 100D: +1.976, 8/8.
- 200D: +3.073, 8/8.

Population effect with Halton held fixed:
- 50D: +1.365, 8/8.
- 100D: +2.356, 8/8.
- 200D: +3.060, 8/8.

Halton-vs-LHS effects are much smaller and inconsistent. Therefore the transfer result is fundamentally population size / number-of-generations, not initialization design.

At 50D a p15 population spends 75 of 250 calls on initialization and has only about 2.3 population passes afterward. A p2 population spends 10 calls on initialization and can make about 24 passes. At 100D the approximate comparison is 5.7 versus 49 passes; at 200D, 12.3 versus 99.

## Domain-specific geometry

Finite-difference Jacobians of log concentrations with respect to normalized parameters at the true parameters show strongly variable local sloppiness:
- Gauss-Newton condition numbers range from ~55 to ~3.9e6;
- median ~580.

But condition number does not predict CMA's late objective advantage; Spearman is about -0.60 across the eight subjects. Subject 7 is instructive: condition ~3.9e6, and all strong optimizers reach ~1e-6 objective while parameter RMS error remains ~4-5%. In very sloppy inverse problems, deeper scalar-objective convergence is not equivalent to better parameter identification.

This is a useful scientific caution for the talk: report parameter recovery alongside objective value when synthetic truth is available.

## Interpretation

The strongest surviving result is now independently transferred:

**For expensive smooth 5D fitting under only 50-100D objective calls, conventional DE population sizes spend too much budget on breadth and too little on evolutionary generations. A population around 2D can be dramatically more evaluation-efficient. At larger budgets, CMA-ES becomes the better deep-convergence choice.**

This is an operating-regime result, not a new algorithm. Population-size adaptation itself is prior art, and the project has failed to find a novel operator after four candidate mechanisms.

The result is nevertheless scientifically useful and highly explainable:
- finite evaluation budget sets a direct population-vs-generations trade-off;
- going all the way to D members fails, so donor diversity remains necessary;
- around 2D was robust across BBOB development and this independent PK problem;
- CMA's later strength should not be confused with early-budget efficiency.

## Confirmation decision

This operating-regime claim now merits the untouched BBOB confirmation reserve.

Freeze for Batch 7:
- algorithms: SciPy default p15, SciPy p2 Halton, L-SHADE p2, CMA s30;
- budgets: 50D, 100D, 200D;
- confirmation set: BBOB f={2,7,11,16,21}, instances 11-15, dimension=20;
- no parameter changes after seeing confirmation;
- primary confirmation claim: SciPy p2 beats default p15 by at least 0.5 log10 decades median at 50D and 100D and wins >=70% of problem units;
- secondary descriptive test: identify whether the early-DE / late-CMA crossover persists at unseen 20D problems;
- uncertainty unit: function x instance, median stochastic seeds first.

If the primary confirmation claim fails, retain the PK transfer as context but do not generalize a universal 2D recommendation.
