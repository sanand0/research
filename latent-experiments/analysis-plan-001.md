# Analysis plan 001 — frozen before survival-label access

Freeze date: 2026-09-08 SGT

This plan operationalizes `hypothesis-001.md` after downloading and reproducing the Hobbs et al. timing data. Individual `Survived` values in `candidates/chickadees/THC_Survival.csv` remain unopened at this point. Only its header, ID column, and row count have been used.

## Question

Does an individual's environment-adjusted timing of first winter feeder use predict next-fall apparent survival after controlling for total feeder-use intensity and age-sex?

Primary test remains two-sided.

## Reproduction before outcome access

Downloaded OSF `2022-2023data.csv` (1,532,565 rows; SHA-256 `c002dae47475c2deaa5fccb6431f81cbab85dbf139131f9eb999e9e6ab8216b3`).

`analysis/prepare_timing.py` reproduces the authors' filtering directly from their published code:

- bird records only;
- 1 Dec 2022 through 28 Feb 2023;
- authors' explicit 52 feeder-14 exclusions;
- exact age/sex metadata and five unsexed exclusions;
- bird-days with at least 10 feeder visits;
- first feeder visit relative to sunrise;
- same temperature, daylength and age-sex fixed effects as Hobbs et al.'s selected no-interaction model.

Independent structural checks match the authors' code:

- 90 calendar days;
- 143 birds;
- 11,761 analytic bird-days.

A temporary 11,762nd row in the authors' plotting code initially caused a false verification alarm; the code then explicitly drops back to 11,761. This is documented as a failure/recovery in the research log.

## Deviation from the published phenotype model

Exact `MCMCglmm` reproduction is unavailable because LocalMCP has no R installation.

A first Python attempt with `statsmodels` MixedLM + L-BFGS failed: the optimizer collapsed the random-effect variance to zero and produced singular covariance matrices, contradicting published repeatability. Alternative optimizers were tested outcome-blind. Powell, BFGS and CG all converged to the same non-zero solution; L-BFGS alone was pathological.

Therefore the frozen Python primary implementation uses **Powell REML random-intercept models**, one per phenotype, with the same fixed effects as the Hobbs no-interaction model:

`first_feed_relative_to_sunrise ~ age_sex + z_temperature + z_daylength + (1 | bird)`

`total_daily_feeder_visits ~ age_sex + z_temperature + z_daylength + (1 | bird)`

This is not identical to Hobbs et al.'s multivariate Bayesian model because it does not estimate cross-trait random-effect covariance jointly. It is accepted as the primary executable approximation because:

1. it preserves the exact analysis population and fixed-effect adjustment;
2. random-intercept variance is well away from zero with three independent optimizers;
3. the resulting phenotype is highly correlated with a model-independent residual-mean sensitivity phenotype before outcome access.

Full-window estimates before outcome access:

- first-feed random variance: 743.90; residual variance: 2701.08; approximate repeatability = 0.216;
- total-feed random variance: 457.82; residual variance: 640.67; approximate repeatability = 0.417.

## Analytic population

The survival file has 138 unique bird IDs.

137 have a valid full-window timing phenotype and age-sex value. The one excluded survival-study bird is `01103F82A5`, which is one of Hobbs et al.'s five predeclared unsexed exclusions.

Primary N is therefore **137 birds**, subject only to an unexpected missing/invalid survival label discovered after unsealing. No bird will be added back post hoc.

Age-sex composition among the 137 birds, before survival labels are read:

- Adult Female: 32
- Adult Male: 35
- Juvenile Female: 37
- Juvenile Male: 33

## Primary predictors

From the full 90-day window:

- `early_chronotype = - first_feed_random_intercept`, so larger values mean earlier first feeder use after environmental adjustment;
- `total_feeder_use = total_daily_visits_random_intercept`.

Both are standardized to mean 0, SD 1 **within the 137-bird joined analytic population** before survival fitting.

The two point-estimate phenotypes correlate at r = 0.508 before outcome access. This justifies retaining both in the primary survival model rather than interpreting a raw chronotype association as independent of feeding amount.

## Primary survival model

Frequentist binomial GLM with logit link:

`Survived ~ early_chronotype_z + total_feeder_use_z + C(AgeSex)`

Reference age-sex category will be whichever Patsy/statsmodels chooses lexicographically; the chronotype estimand is invariant to that coding.

Primary estimand: odds ratio for apparent survival per 1 SD earlier chronotype, conditional on total feeder use and age-sex.

Support rule remains: the two-sided 95% interval for the chronotype coefficient must exclude 0 (equivalently OR interval excludes 1).

Also report:

- coefficient/OR without total feeder-use adjustment but still adjusting age-sex;
- analytic N and survival event count;
- likelihood-based fit diagnostics and convergence/separation warnings;
- effect as predicted survival probabilities at -1 SD, 0, +1 SD chronotype for an illustrative age-sex category only if model fit is valid.

No causal language.

## Phenotype uncertainty propagation

The point-estimate GLM is the primary executable test because exact Bayesian multivariate posterior draws are unavailable without R/MCMCglmm.

A predeclared uncertainty sensitivity will use 2,000 Gaussian draws of each bird's random intercept around its BLUP, conditional on fitted variance components. For a random-intercept Gaussian model, conditional SD is approximated as:

`sd_i = sqrt(1 / (1/tau^2 + n_i/sigma^2))`

Timing and total-use draws are generated independently because the Python approximation lacks the published cross-trait random-effect covariance. For each draw:

1. sign-reverse timing, standardize both phenotypes in the 137 birds;
2. fit the same survival GLM;
3. store chronotype beta and model SE.

Combine uncertainty approximately using:

`Var_total = mean(SE_j^2) + Var(beta_j)`

and report `mean(beta_j) ± 1.96*sqrt(Var_total)` as an uncertainty-propagated sensitivity interval.

This is explicitly secondary because ignoring cross-trait posterior covariance is a model deviation.

## Predeclared stability forks

The interpretation is called **STABLE** only if the chronotype sign and broad interpretation survive all first three forks; otherwise SENSITIVE/FLIPS will be reported.

### 1. Shared-window phenotype

Refit the same Powell mixed models using 9 Jan–14 Feb 2023, matching LaRocque et al.'s main-analysis window.

Outcome-blind check: shared-window vs full-window phenotype correlations are already high:

- early chronotype r = 0.957;
- total feeder use r = 0.953.

### 2. Residual-mean phenotype

Use bird-level mean residuals after ordinary fixed-effect models with age-sex, temperature and daylength, sign-reversing first-feed residuals.

Outcome-blind checks:

- mixed-model vs residual-mean early chronotype r = 0.981;
- mixed-model vs residual-mean total feeder use r = 0.987.

### 3. Spatial-behavior adjustment

Add an independently constructed off-territory propensity covariate from LaRocque et al.'s Jan 9–Feb 14 data.

`analysis/prepare_spatial.py` reproduces their core-feeder definition, including the exact two two-core birds (`3B001878E9`, `3B0018A4C3`), and derives each bird's mean off-territory residual after the published age-sex-specific temperature fixed effects.

Use standardized `offT_resid_mean` as one additional covariate. Because R is unavailable, this is a transparent residualized-mean approximation rather than the authors' MCMCglmm BLUP.

### 4. Nonlinearity

Add `early_chronotype_z^2` to the primary model. This cannot replace the primary linear result.

## Failure / fallback rules fixed before unsealing

1. **Perfect or quasi-separation:** if the unpenalized GLM fails or has extreme/non-finite coefficients, do not tune predictors until significance appears. Report primary model as non-estimable and fit a weakly L2-penalized logistic regression only as descriptive sensitivity.
2. **Sparse survival events:** if there are fewer than 10 events in either outcome class, label inference underpowered regardless of p-value/CI.
3. **Specification flip:** if shared-window, residual-mean or spatial-adjusted models reverse chronotype sign or move materially across the null, classify the result SENSITIVE/FLIPS rather than a discovery.
4. **Null result:** do not substitute last-feeder time, window length, temperature plasticity, subgroup effects or nonlinear terms as the new primary hypothesis.
5. **Positive association:** still call this observational prediction of *apparent survival*. Detection next fall is not confirmed biological survival, and the timing phenotype may proxy condition, dominance, feeder dependence or another latent trait.
6. **Published-result overlap:** if a post-result novelty search finds the same relationship already tested elsewhere, retain the analysis as a replication/failure of the novelty screen rather than claiming discovery.

## Tempting false victories explicitly ruled out

- a nominally significant coefficient that disappears under one reasonable phenotype specification;
- treating optimizer pathology as biological evidence;
- calling fall non-detection death;
- claiming causality from an observational relationship;
- searching many timing traits after a null and promoting the best one;
- claiming global novelty because indexed keyword searches found no paper.

## Frozen artifacts before outcome access

- `analysis/prepare_timing.py`
- `analysis/prepare_spatial.py`
- `analysis/timing_phenotypes_full.csv`
- `analysis/timing_phenotypes_shared_window.csv`
- `analysis/timing_phenotypes_residual_means.csv`
- `analysis/spatial_propensity.csv`
- `analysis/timing_preoutcome_summary.json`
- `analysis/spatial_preoutcome_summary.json`
- this file

Outcome analysis must occur only after these are committed to git.
