# Hypothesis 001 — Does winter chronotype predict apparent survival beyond feeder-use amount?

**Status: FROZEN BEFORE INDIVIDUAL SURVIVAL OUTCOME ACCESS**

Freeze date: 2026-09-08 SGT

## Research question

Among black-capped chickadees using RFID feeders at the University of Alberta Botanic Garden in winter 2022–2023, does an individual's environment-adjusted timing of its first daily feeder visit predict whether it is detected the following fall, after accounting for how intensively it uses the feeders and its age-sex class?

A compact version is:

> **Does when a chickadee starts feeding predict apparent survival once we know how much it feeds?**

## Primary hypothesis

The individual-level first-feeder chronotype is associated with next-fall apparent survival **conditional on total feeder-use intensity and age-sex**.

This is deliberately **two-sided**. There are competing plausible mechanisms. Earlier feeder use could help replenish energy after the overnight fast and increase access to food; alternatively, unusually early activity could reflect energetic stress, social displacement, or greater exposure to costs. Existing great-tit chronotype-fitness studies are also largely null/inconclusive. Choosing a direction after seeing survival outcomes would therefore be HARKing.

## Population and unit of analysis

Unit: individual bird.

Population: birds that satisfy the published Hobbs et al. timing-analysis inclusion criteria and can be matched to the LaRocque et al. next-fall apparent-survival dataset. The timing study requires at least 10 recorded feeder visits on a bird-day before that day contributes first/last timing information.

If fewer than 100 birds have usable timing phenotype + apparent-survival outcome + age-sex data, the analysis will still be run but described as underpowered/exploratory rather than as a strong discovery test.

## Predictor: first-feeder chronotype

Primary predictor: the among-individual random effect for **first daily feeder visit relative to sunrise**, estimated using the Hobbs et al. multivariate timing model over the published winter window (1 Dec 2022–28 Feb 2023).

The model adjusts first-feeder timing for:

- age-sex class;
- daily mean temperature;
- daylength;
- repeated observations within bird.

For interpretation, the individual effect will be sign-reversed and standardized so that **+1 means 1 SD earlier than peers, after environmental adjustment**.

Why this metric: it uses the phenotype and model the timing paper already established as repeatable rather than inventing a new timing metric after seeing survival.

## Outcome

Binary **next-fall detection / apparent annual survival** from `THC_Survival.csv` in the LaRocque dataset.

Important terminology: this is *apparent survival*, not guaranteed biological survival, because a bird not detected the next fall could in principle have emigrated or escaped detection.

**Individual outcome labels have not been inspected, summarized, plotted, joined to chronotype, or modeled before this freeze.** The published paper's aggregate survival findings are public prior information and are not treated as outcome blinding violations.

## Primary adjustment variables

1. **Total feeder-use intensity**, represented by the corresponding among-individual total-daily-feeder-visits phenotype from the Hobbs multivariate model, standardized within the analytic population.
2. **Age-sex class**, using the same four-level classification used in the source analyses where available.

Rationale: first-feeder timing covaries with total feeder visits in Hobbs et al.; LaRocque et al. already found evidence that feeder-use intensity is related to apparent survival. The scientific question is therefore whether timing carries information beyond amount.

Off-territory feeder use will **not** be in the primary model because it is a distinct behavioral phenotype and adding it increases complexity/collinearity. It is predeclared as a sensitivity analysis after the primary result.

## Primary analysis

Reproduce the published Hobbs et al. timing model closely enough to obtain posterior individual effects for first-feeder timing and total feeder visits.

Then fit the survival model:

`apparent_survival ~ early_chronotype + total_feeder_use + age_sex`

The primary estimand is the odds ratio for apparent survival per 1 SD earlier first-feeder chronotype, conditional on the other terms.

To propagate uncertainty in the timing phenotypes rather than treating BLUP/posterior means as perfectly measured, use posterior draws of the individual timing and total-use effects in repeated survival fits. The exact uncertainty-combination implementation must be fixed *before* inspecting survival labels; if a statistically cleaner joint/measurement-error implementation is chosen, that choice and its code will be documented before the first outcome read. No model choice may be made by comparing which version gives a more interesting chronotype result.

## Evidence / failure rule

Always report:

- analytic N;
- odds ratio per 1 SD earlier chronotype;
- uncertainty interval;
- the chronotype coefficient with and without total feeder-use adjustment;
- model diagnostics / calibration appropriate to the chosen implementation.

A non-zero association is considered supported only if the primary 95% uncertainty interval excludes the null. A null or wide interval is a valid result and must not trigger substitution of another timing metric as the "real" hypothesis.

No causal claim will be made from this observational association.

## Predeclared sensitivity analyses

These are robustness checks, not alternate primary hypotheses:

1. **Window:** estimate timing using only the Jan 9–Feb 14 period shared with the main LaRocque analysis rather than the full 90-day Hobbs window.
2. **Phenotype construction:** use a simpler bird-level mean of environmentally residualized first-feed time rather than the mixed-model individual effect.
3. **Spatial behavior:** additionally adjust for off-territory propensity from LaRocque et al.
4. **Nonlinearity:** add a quadratic chronotype term because intermediate timing could outperform both extremes; this is especially relevant given prior chronotype-fitness literature.
5. **Related temporal traits:** last-feeder timing and feeding-window length may be reported as explicitly secondary/exploratory outcomes. They cannot replace first-feeder timing if the primary result is null.

A substantive conclusion is **stable** only if its sign and broad interpretation survive the first three reasonable specification forks. If they flip, the result will be reported as specification-sensitive.

## Mechanistic interpretation if an association exists

Possible mechanisms to investigate *after* the primary result include:

- overnight energy depletion / rapid morning replenishment;
- dominance-mediated feeder access;
- risk exposure at low-light periods;
- chronotype as a marker of energetic state rather than a causal driver;
- covariance with spatial exploration or feeder dependence.

These are explanations to discriminate later, not evidence already established by this experiment.

## Prior art checked before freeze

- Hobbs et al. (2024), DOI 10.1098/rsbl.2024.0365: first/last feeder timing, temperature/daylength, age-sex, repeatability, and covariance with total feeder visits in this population; no survival analysis in the public analysis code.
- LaRocque et al. (2024), DOI 10.1093/beheco/arae080: feeder-use rate, off-territory use, age/sex/temperature, and next-fall apparent survival; raw visit time is not used as a timing phenotype in the public analysis code.
- Meijdam et al. (2025), DOI 10.1098/rsos.250380: female great-tit chronotype vs annual/lifetime reproductive success and longevity; no clear relationship.
- Strauß et al. (2026), DOI 10.1007/s00442-025-05857-3: female great-tit chronotype related to lay date but not measured fitness.

As of the freeze, no indexed direct test was found of winter first-feeder chronotype predicting next-fall apparent survival in black-capped chickadees conditional on total feeder use. This is a search result, **not a proof of novelty**.

## Source files frozen / outcome sealed

See:

- `candidates/chickadees/SHA256SUMS`
- `candidates/chickadees-timing/SHA256SUMS`
- `protocol.md`
- `screening.md`
- `research-log.md`

The raw large timing file from Hobbs et al. has not yet been downloaded because the hypothesis can be fixed from the documented public model/code without inspecting its values. Download/reproduction of that predictor pipeline is the first next step.
