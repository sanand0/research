# Checkpoint 009 — robustness study plan

Date: 2026-09-21
Status: new research question frozen at the planning stage; no robustness outcomes run yet.

## Question

The previous project found that population size can dominate clever DE modifications when the objective-evaluation budget is very small. A population around 2D was often much stronger than a default-like 15D population, transferred dramatically to one pharmacokinetic inverse problem, but the preregistered 50D BBOB effect-size criterion failed.

The new question is not "can we make p2 win again?"

It is:

> **How general is the population-size effect, and where does it fail?**

There are two distinct claims to test.

### Claim A — importance

Under tight objective-evaluation budgets, population size is a first-order variable: changing it can alter performance materially even when the DE strategy and total number of objective calls are held fixed.

### Claim B — robustness of ~2D

A population around 2D is a broadly useful low-budget operating point across problem families, dimensions, and budgets.

Claim A can be true while Claim B is false. The study must preserve that distinction.

## What "robust" means

For a fixed problem segment, dimension, budget and DE strategy, compare population multipliers:

    p in {1D, 2D, 4D, 8D, 15D}

Primary performance is fixed-budget log10 objective error, aggregated by problem unit before stochastic seeds.

For each segment/cell define:

- **population importance** = worst median log-error minus best median log-error across the five population sizes;
- **p2 regret** = median log-error at p2 minus the best population's median log-error;
- **p2-vs-p15 advantage** = median log-error(p15) minus median log-error(p2);
- **win rate** = fraction of problem units where p2 has lower error than p15.

Interpretation thresholds, frozen before the new experiments:

- population size is **material** in a cell if population importance >= 0.5 log10 decades;
- p2 is **near-best** in a cell if p2 regret <= 0.15 decades;
- p2 has a **meaningful failure** against p15 if p2-vs-p15 advantage <= -0.25 decades and p2 wins <=40% of problem units;
- p2 has a **meaningful advantage** over p15 if advantage >= +0.25 decades and p2 wins >=60%.

These are descriptive robustness thresholds, not significance tests.

## Predefined axes of generalization

The study should deliberately span variables that can change the breadth-vs-feedback trade-off.

### 1. Evaluation budget

Use objective calls per dimension, not generations:

    20D, 50D, 100D, 200D, 500D, 1000D

Hypothesis:
- small populations should help most at 20D–200D;
- the advantage should shrink as the budget gets large enough for bigger populations to receive many update rounds.

### 2. Dimension

Primary dimensions:

    D = 5, 20, 40

Optional D=80 only after the first map if runtime remains reasonable; it must not be used to alter population choices.

Hypothesis:
- a fixed multiplier such as 2D may become less robust as D rises because diversity requirements grow;
- if the important variable is mainly "number of generations available", the useful multiplier may remain approximately stable.

### 3. Landscape family

Use the standard BBOB functional classes as predefined segments rather than inventing categories after seeing results:

1. separable;
2. low/moderate conditioning;
3. highly conditioned unimodal;
4. multimodal with adequate global structure;
5. multimodal with weak global structure.

COCO's BBOB suite has 24 noiseless scalable functions and dimensions through at least 40, making it suitable for this map.

Hypotheses:
- smooth/separable/unimodal problems should favor smaller populations under tiny budgets;
- highly multimodal problems, especially weak-global-structure cases, are the most plausible segment where p2 loses because broad basin coverage matters.

### 4. Rotation and conditioning

Use synthetic quadratics as a controlled mechanism layer, independent of the BBOB class labels:

- axis-aligned vs randomly rotated;
- condition numbers 1, 1e2, 1e4, 1e6.

This separates "hard because narrow/correlated" from "hard because multimodal."

Hypothesis:
- conditioning alone may not require a larger DE population, but rotated high-dimensional problems may expose diversity failure earlier.

### 5. Noise

Noise is a major plausible failure mode for tiny populations because selection can lock onto lucky evaluations.

Use a separate noisy phase rather than mixing it into the noiseless primary map:
- moderate Gaussian noise;
- strong Gaussian noise;
- heavy-tailed/outlier noise.

Prefer a standard noisy black-box benchmark when practical; Nevergrad exposes explicit noisy benchmarks, and COCO defines a BBOB-noisy suite. If COCO's noisy harness is inconvenient, use a transparent noise wrapper whose latent noiseless objective is retained only for scoring, never given to the optimizer.

Hypothesis:
- p2 will become less robust as noise increases;
- adaptive/noise-aware methods may dominate regardless of population multiplier.

### 6. Position of the optimum / boundaries

Use synthetic transforms that place the optimum:
- centrally;
- near one boundary;
- near several corners.

Keep the underlying landscape identical.

Hypothesis:
- boundary handling can interact with a tiny population and create premature crowding.

### 7. DE strategy

The previous result is strongest for an exploitative SciPy best/1/bin configuration.

Test the population response under a small frozen strategy set:

- best1bin;
- rand1bin;
- currenttobest1bin;
- L-SHADE as the adaptive-DE comparator.

Do not tune F/CR separately for every population. Use one frozen setting per strategy.

Hypothesis:
- rand-based strategies may need larger populations than best-based strategies;
- if so, "2D is good" is strategy-specific while "population size matters" remains general.

### 8. Parallelism / wall-clock objective

The current result is about **number of function evaluations**, not elapsed time.

This distinction must be tested explicitly.

Use:
- sequential evaluation;
- 8 workers;
- 64 workers;
- one-shot / massively parallel execution.

Report both NFE and an explicit wall-clock cost model (and actual wall clock where practical).

Hypothesis:
- when many expensive evaluations run concurrently, a larger population may no longer be wasteful in elapsed time;
- in a fully one-shot regime, iterative small-population learning loses its main advantage.

Nevergrad includes one-shot and parallel benchmark settings, which are useful as an independent cross-suite check.

### 9. Scientific inverse-problem family

The PK result is only one scientific family. Add fresh transparent inverse problems before any new "general scientific fitting" claim.

Preselect three distinct families:

1. **Lotka–Volterra** predator-prey ODE parameter recovery — low-dimensional nonlinear dynamics.
2. **SEIR-style epidemic model** — correlated rate parameters and partial identifiability.
3. **1D heat/diffusion inverse problem** with piecewise material parameters — a spatial simulation with 6–10 fitted parameters.

For each:
- generate truths before optimizer runs;
- freeze bounds, observation times/locations, noise regime, seeds and target metrics;
- independently verify the simulator or synthetic truth;
- measure parameter recovery as well as objective value.

PK may be shown alongside them but must not count as a fresh confirmation family.

## Experimental sequence

### Batch 9 — noiseless population response surface

Purpose: establish the broad shape before studying exceptions.

Fresh data only. Do not reuse the old confirmation instances as development material.

Use:
- all 24 BBOB functions;
- fresh instances 21–22;
- D = 5 and 20;
- budgets = 20D, 50D, 100D, 200D, 500D, 1000D;
- population multipliers = 1, 2, 4, 8, 15;
- SciPy best1bin;
- Latin-hypercube initialization for every population size;
- F~U(0.5,1), CR=0.7, immediate updating for every population size;
- two optimizer seeds.

This is 5,760 runs and roughly 22.4 million cheap BBOB objective evaluations if every run consumes its full budget. Keep the run resumable and bounded.

Questions:
1. How often is population importance >=0.5 decades?
2. How does the best population multiplier move with budget?
3. In what fraction of cells is p2 near-best?
4. Which predefined BBOB classes show p2 failures?
5. Does the p2-vs-p15 effect diminish monotonically with budget?

No new population values are added after seeing this batch.

### Batch 10 — dimension, geometry, and strategy interactions

Freeze any analysis code before running.

Add:
- D=40;
- controlled rotated/axis-aligned quadratics;
- conditioning through 1e6;
- best1bin / rand1bin / currenttobest1bin;
- L-SHADE as the adaptive comparator.

Use fresh problem seeds/instances.

The goal is not to optimize each strategy. It is to estimate interactions:
- population × dimension;
- population × conditioning;
- population × rotation;
- population × DE strategy.

### Batch 11 — explicit failure modes

Test the segments where small populations have the strongest a-priori reason to fail:

- noisy objectives;
- strong multimodality / weak global structure;
- optima near boundaries;
- abundant budgets;
- massive parallelism / one-shot evaluation.

This batch should be able to falsify the p2 robustness claim.

For noisy and parallel settings, include suitable noise-aware or one-shot baselines rather than pretending DE is the only relevant family.

### Batch 12 — discover segments, then freeze them

Use only Batches 9–11 for **segment discovery**.

Fit simple interpretable models to problem-unit effects:
- shallow regression tree or rule list;
- regularized regression with predefined interactions;
- no opaque high-capacity model.

Features may include:
- log budget/D;
- dimension;
- BBOB class;
- separability/rotation flag;
- condition number;
- noise level/type;
- boundary proximity;
- strategy;
- worker count.

Target:
- p2 regret, or
- p2-vs-p15 advantage.

The purpose is to turn results into a small failure map, e.g.:

> "p2 is near-best for deterministic unimodal/moderately multimodal problems below 200D, but loses once noise is high or one-shot parallelism removes the value of extra generations."

Freeze at most the top **three** discovered interaction rules. Do not keep mining rules until they look clean.

### Batch 13 — scientific transfer across families

Run the three preregistered scientific inverse problems.

Use the same population grid and fixed budgets where computationally reasonable.

For each family report:
- objective error;
- parameter recovery;
- target success;
- calls-to-target;
- optimizer overhead;
- p2 regret to the best tested population;
- p2-vs-p15 effect.

The question is whether the synthetic robustness map predicts what happens on real simulation-fitting structure.

### Batch 14 — fresh-family confirmation

Only after the failure map is frozen.

Confirmation data must not have been used in Batches 9–13.

Use:
- fresh BBOB instances 31–35 at D=20 and 40;
- **FitzHugh–Nagumo neuron-model parameter recovery** as the scientific confirmation family; this family is selected now and must not be run during Batches 9–13;
- fresh seeds;
- all five population multipliers.

Primary robustness criteria, frozen now:

**Claim A — population size is first-order**
- At least 50% of confirmation segment-cells have population importance >=0.5 decades at budgets <=200D.

**Claim B — p2 is a robust low-budget operating point**
- Across confirmation cells with budgets <=200D, p2 is near-best (regret <=0.15 decades) in at least 70% of cells;
- and meaningful p2 failures against p15 occur in no more than 15% of cells.

Claim B is allowed to fail while Claim A passes.

**Failure-map validation**
- Each frozen failure rule from Batch 12 must reproduce directionally on fresh confirmation data; report effect sizes rather than inventing a new threshold after seeing them.

## Analysis discipline

Every batch follows the existing project process:

1. Read STATE.md and the latest checkpoint.
2. State the question and frozen design before running.
3. Keep a strict evaluator-owned budget.
4. Append machine-readable raw runs outside Git during exploration.
5. Aggregate stochastic seeds before treating problem units as evidence.
6. Report medians, means, win rates, and problem-unit bootstrap intervals.
7. Check counterexamples, not only aggregate averages.
8. Check prior literature before calling any pattern novel.
9. Write a checkpoint with the decision and next action.
10. Update STATE.md so the next "Continue" resumes exactly there.

No tuning may use the old Batch-7 confirmation data.

## What would change my mind

The current belief should be weakened substantially if any of these happen:

- p2 is not near-best in most low-budget cells once all 24 BBOB functions are considered;
- p2 loses systematically on multimodal, noisy, high-dimensional, or boundary-heavy segments;
- scientific families other than PK prefer much larger populations;
- the effect vanishes when the same initialization and strategy are held fixed;
- under realistic parallel evaluation, p15 gives equal or better wall-clock results despite using more evaluations.

Conversely, the claim becomes genuinely general if:
- population size remains material across suites and scientific families;
- p2 stays close to the best population over most deterministic low-budget segments;
- and the discovered failure segments are stable enough to predict where it should *not* be used.

## Expected deliverable

The target is not a single winning population.

It is a **robustness map**:

| Regime | Small population? | Why |
|---|---|---|
| Tight, deterministic, sequential budget | likely useful | more feedback rounds |
| Very multimodal / weak global structure | uncertain / larger may help | basin coverage |
| High noise | likely fragile | selection errors, premature collapse |
| Large budget | less important | large populations get enough generations |
| Massive parallel / one-shot | likely not useful | iteration is no longer the scarce resource |
| High-dimensional / strategy-dependent | empirical | diversity needs may dominate |

That map is the result to seek.

## Benchmark references

- COCO BBOB: https://numbbo.github.io/coco/testsuites/bbob — 24 noiseless scalable functions with standard dimensions and arbitrary instances.
- COCO BBOB-noisy: https://numbbo.github.io/coco/testsuites/bbob-noisy — 30 scalable noisy functions spanning noise types/levels.
- Nevergrad benchmarks: https://facebookresearch.github.io/nevergrad/benchmarking.html and https://facebookresearch.github.io/nevergrad/benchmarks.html — useful independent noisy and one-shot/parallel benchmark settings.
