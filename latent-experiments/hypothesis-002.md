# H002 — Behavioral predictability and annual survival

Status: **FROZEN BEFORE SURVIVAL OUTCOME ACCESS**

## Question

Do individual black-capped chickadees that are more or less behaviorally predictable in repeated standardized predator-cue trials differ in subsequent annual survival, after accounting for their mean risk-taking behavior and sex?

The source study tested whether **mean** latency-to-resume-feeding and mean pre-disturbance feeding rate predicted annual survival. Its released code does not test bird-specific residual behavioral variability (predictability) against survival.

## Why this is a latent experiment

The expensive experiment already happened: 79 birds received repeated combinations of acoustic and visual predator cues, with 1,009 latency observations, and annual survival was recorded later. The published abstraction compresses each bird to its mean behavior. H002 asks whether a component discarded by that abstraction — persistent within-individual residual variability — carries fitness information.

## Outcome seal

All H002 screening used `candidates/replication-alberta-2018/p3hz4_predictors.csv`, which contains the 17 predictor columns and **does not contain `survival`**. `analysis/h002_predictability_preoutcome.py` fails if an outcome-like column is present.

No H002 survival values were inspected before this freeze.

## Frozen primary hypothesis

Two-sided:

> Individual residual behavioral unpredictability is associated with subsequent annual survival, conditional on mean latency-to-resume-feeding and sex.

No directional sign is preregistered. Both greater predictability (reliable decision-making) and greater unpredictability (harder-to-predict behavior) are biologically plausible.

## Primary phenotype

Model log latency using a hierarchical location-scale model:

- mean: sex + treatment + standardized daily temperature + treatment × temperature + partially pooled bird intercept;
- residual scale: each bird has a partially pooled `log(sigma_i)`;
- likelihood: Normal on log latency;
- four NUTS chains with explicit random seeds.

`log(sigma_i)` is the unpredictability phenotype: larger values mean less predictable behavior after accounting for the source mean structure.

Eligibility: **at least 4 latency observations per bird**. This threshold was fixed before outcome access. Sensitivity thresholds: >=6 and >=8 observations.

## Pre-outcome phenotype gates and observed results

The phenotype advanced only because all prespecified gates passed:

- N=1,009 observations / 79 birds in the full predictor data;
- between-bird log-scale SD `sigma_log_sigma`: median 0.268, 95% interval 0.196–0.348;
- all primary/split/robust fits: max R-hat 1.00, zero divergences; minimum bulk ESS >=620;
- split reliability Rep 1–2 vs 3–4: Spearman rho 0.373, bootstrap 95% CI 0.134–0.575;
- split reliability odd vs even: rho 0.442, CI 0.230–0.614;
- primary vs expanded mean model (+ feeder + replicate): rho 0.969, CI 0.936–0.985;
- primary Normal vs Student-t(5) likelihood: rho 0.969, CI 0.938–0.982;
- unpredictability vs observation count: rho 0.182;
- visual-containing treatments remain strongly positive on log-latency scale (~+1.2), reproducing the known source signal qualitatively.

A material pre-outcome correlation remains between unpredictability and mean latency (rho = -0.457), therefore mean latency is a mandatory primary covariate.

## Primary survival model

The source code defines annual survival as `survival2 = 1 if survival > 0 else 0` and uses binomial GLMs. H002 mirrors that outcome definition.

For 1,000 deterministically selected posterior draws from the frozen location-scale fit:

1. restrict to birds with >=4 repeated latency observations;
2. within each draw, z-standardize bird `log(sigma_i)` among eligible birds;
3. z-standardize the corresponding partially pooled bird mean-latency effect;
4. fit `survival2 ~ unpredictability_z + mean_latency_z + Sex` by binomial GLM;
5. combine the unpredictability coefficient and its within-fit variance across posterior imputations using Rubin-style total variance: `T = mean(U_m) + (1 + 1/M) Var(beta_m)`.

Primary estimand: odds ratio for annual survival per 1 SD greater behavioral unpredictability.

Report coefficient, OR, 95% interval, two-sided p-value, eligible N, survivor/non-survivor counts, convergence/failure count across imputations, and mean-latency coefficient.

Primary support rule: H002 is supported only if the combined 95% interval for the unpredictability coefficient excludes zero. Otherwise report **not supported / inconclusive**, not evidence of no effect.

## Prespecified sensitivity analyses

- repeat primary procedure with >=6 observations per bird;
- repeat with >=8 observations per bird;
- report the unadjusted `survival2 ~ unpredictability_z + Sex` model to show the impact of the known mean–variance correlation, but it cannot replace the primary adjusted result;
- report a point-estimate outcome model using the robust Student-t phenotype only if regenerated outcome-blind from the same fixed model; it is descriptive and cannot rescue the primary result.

No subgroup, treatment-specific survival model, alternative residual metric, or directional hypothesis may be substituted after unsealing.

## Interpretation limits

Annual survival here is apparent survival/redetection as defined by the source study, not a causal effect of predictability. H002 is a secondary analysis of an existing cohort and has limited power. Moderate phenotype reliability implies attenuation remains plausible if the result is null.
