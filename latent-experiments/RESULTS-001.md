# Latent Experiment 001 — chronotype and apparent survival in black-capped chickadees

Status: **completed primary analysis; no preregistered discovery**

Outcome unsealed only after analysis freeze commit: `d15b1f54b4c9dfe08dd479fcea2734463616569e` at 2026-09-08T14:08:19+08:00.

## Question

Does an individual's environment-adjusted tendency to begin feeding earlier in winter predict whether it is detected again the following fall, after accounting for overall feeder-use intensity and age-sex?

The question was produced by joining two analyses of the same UABG winter-2022/23 RFID system:

- Hobbs et al. studied **when** birds first/last fed and **how much** they fed;
- LaRocque et al. studied **where/how much** birds fed and linked behaviour to next-fall apparent survival.

Neither source analysis linked the timing phenotype to apparent survival.

## Primary result

Analytic N = 137 birds: 79 detected next fall, 58 not detected.

Frozen model:

`Survived ~ early_chronotype_z + total_feeder_use_z + age_sex`

Chronotype estimate:

- beta = **+0.274 log-odds per 1 SD earlier chronotype**
- SE = 0.209
- OR = **1.315**
- 95% CI = **0.873–1.980**
- two-sided p = **0.190**

**Decision under the frozen rule: not supported.** The 95% interval includes the null.

The point estimate is in the direction of earlier birds being more likely to be re-detected, but the data are compatible with effects ranging from a small negative association to nearly a doubling of the odds. This is therefore an imprecise null, not evidence that timing has no biological relationship to survival.

Illustratively, at average total feeder use for a juvenile female, the fitted probabilities at -1, 0 and +1 SD earlier chronotype are 0.526, 0.594 and 0.658. These are model illustrations only, not causal effects.

## Preregistered robustness checks

| Analysis | N | OR / SD earlier | 95% CI | p | Conclusion |
|---|---:|---:|---:|---:|---|
| Primary, full 90 days | 137 | 1.315 | 0.873–1.980 | .190 | null |
| No total-feeder adjustment | 137 | 1.231 | 0.871–1.740 | .240 | null |
| Jan 9–Feb 14 shared window | 137 | 1.416 | 0.943–2.125 | .094 | null |
| Residual-mean phenotype | 137 | 1.324 | 0.876–2.001 | .183 | null |
| Frozen residualized spatial adjustment | 137 | 1.315 | 0.872–1.982 | .191 | null |
| Quadratic model: linear timing term | 137 | 1.302 | 0.767–2.211 | .328 | null |

Quadratic timing term itself: beta = -0.005, p = .956; no hint of a U-shaped relationship.

**Stability classification: STABLE NULL.** All predeclared phenotype/specification forks retain the same positive sign and all cross the null.

### Phenotype uncertainty

2,000/2,000 Gaussian random-effect uncertainty draws completed successfully.

- mean beta = +0.264
- combined SE = 0.213
- OR = 1.302
- uncertainty-propagated 95% CI = 0.857–1.978

The result remains null. Phenotype measurement uncertainty is small relative to survival-sample uncertainty: the SD of beta across phenotype draws was only 0.052 versus a mean survival-model SE of 0.207.

### Influence

All 137 leave-one-bird-out fits completed.

- chronotype beta range = +0.207 to +0.341
- median = +0.271
- sign reversals = **0**

Thus the positive point estimate is not created by one influential bird.

## Strong predictor-pipeline validation

Exact R/MCMCglmm reproduction was unavailable locally, but the Python timing phenotype is much better validated than initially expected.

The Python reconstruction exactly recovers the author's structural analysis population:

- 90 days
- 143 birds
- 11,761 bird-days

Using separate Gaussian random-intercept models with the selected Hobbs fixed effects, it reproduces their published parameter estimates extremely closely. Examples:

| Quantity | Published Hobbs | Python reconstruction |
|---|---:|---:|
| first-feed temperature effect | ~-1.74 | -1.738 |
| first-feed daylength effect | ~+23.36 | +23.356 |
| first-feed bird variance | ~754 | 743.9 |
| first-feed repeatability | ~0.22 | 0.216 |
| total-feed temperature effect | ~-4.16 | -4.153 |
| total-feed daylength effect | ~-8.31 | -8.315 |
| total-feed bird variance | ~457 | 457.8 |
| total-feed repeatability | ~0.41 | 0.417 |

Hobbs reported an among-individual correlation of roughly -0.51 between first-feed timing and total feeding. Our sign-reversed `early_chronotype` versus total-use BLUP correlation is +0.508.

This makes it unlikely that the null result is simply caused by a broken Python timing phenotype.

## Known-signal validation: important failure then recovery

A strong check is whether our machinery can recover a relationship already published from the same LaRocque data: greater off-territory propensity was associated with lower apparent survival.

### Failure: simple residualized spatial phenotype

The pre-outcome `offT_resid_mean` approximation completely missed that known relationship (coefficient approximately zero, p ~ .98). A simple bird-level off-territory rate also missed it.

This exposed a real methodological lesson: for strongly hierarchical binary behaviour, **mean residuals are not interchangeable with individual random effects**.

The frozen chronotype result is not invalidated by this failure because the timing phenotype itself has direct external parameter-validation against Hobbs and the frozen spatial term was only a sensitivity covariate. But the frozen spatial sensitivity must not be described as faithfully reproducing LaRocque's behavioural type.

### Recovery: binomial mixed-model reconstruction

Post outcome, `analysis/validate_sourceA.py` fitted the LaRocque off-territory behaviour with a binomial Bayesian mixed model using bird and core-feeder random effects and the published age-sex × temperature fixed structure.

The resulting bird random effects recover the known survival result:

- Python standardized off-territory beta = -0.352
- OR = 0.703
- 95% CI = 0.495–1.0005
- p = .0503
- author's simulation/posterior coefficient = about -0.245, CrI -0.503 to -0.050

This is not exact MCMCglmm replication but recovers direction and comparable magnitude.

A clearly labelled **post-hoc** primary-model adjustment using this improved off-territory random effect changes almost nothing:

- chronotype OR = **1.328**
- 95% CI = **0.879–2.004**
- p = .178
- early chronotype vs off-territory random effect correlation = -0.050

So the primary conclusion remains null even after the better spatial-behaviour adjustment.

## What succeeded

1. **Outcome blinding worked.** The hypothesis, sample, estimand, model, support rule and major forks were committed before survival labels were opened.
2. **The latent cross-paper join was real.** Separate papers exposed timing and survival on effectively the same experimental stream, leaving the cross-paper relationship untested.
3. **Raw preprocessing was reproducible.** We matched 143 birds and 11,761 bird-days exactly.
4. **The non-R timing approximation is externally credible.** It nearly reproduces the published coefficients, variance components, repeatabilities and cross-trait correlation.
5. **The primary result is specification-stable.** Full/shared windows, residual means, phenotype uncertainty, spatial adjustment and leave-one-out influence all tell the same broad story.
6. **A failed validation improved the method.** The spatial residual failure showed that latent-experiment agents need known-signal checks for every derived phenotype, not just unit tests.
7. **The null is useful.** We did not turn a p=.19 result into a new subgroup, last-feed, window-length or temperature-plasticity hypothesis.

## What failed / remains imperfect

1. **R is absent from LocalMCP.** Exact authors' MCMCglmm models could not be rerun.
2. **L-BFGS failed badly** for the Python timing mixed models, collapsing variance to zero; Powell/BFGS/CG agreed on a valid solution.
3. **A hard-coded 11,762 plotting index caused a false sample-size alarm.** The authors had appended a temporary duplicate row; true N was 11,761.
4. **The frozen spatial residual covariate was inadequate.** A proper binary mixed model was required to recover the known signal.
5. **Survival is apparent survival.** Non-detection is treated as death; it can also represent permanent movement or detection failure.
6. **The study is underpowered for modest effects.** With current SE, a rough first-order calculation says an effect around beta 0.585 (OR ~1.80) would be needed for ~80% power at conventional two-sided alpha=.05. If the observed beta ~0.274 were the true effect and information scaled ideally with N, roughly **627 comparable bird-years** would be needed. This is only a design approximation, not a formal power analysis.
7. **Independent replication is not yet in hand.** The first replication datasets scouted do not immediately provide both unrestricted raw timing and individual later-survival labels.

## Replication scout after the result

### UABG 2019–2020 sampling experiment — useful but not direct

Haave-Audet et al. studied 132 marked chickadees and found repeatable information-sampling behaviour associated with annual survival. Its OSF archive (`62Y7K`) is open and contains code, survival labels and experimental/baseline summaries from winter 2019–20. However, the archived analysis data contain experiment start/stop datetimes and baseline feeding rate, **not the raw all-day RFID visit stream needed to derive chronotype**. Good mechanistic/context dataset; not a direct timing replication.

### UABG 2018–2019 risk-taking experiment — extremely promising if raw survival join can be recovered

Mathot et al. followed 79 UABG birds with RFID feeders in winter 2018/19 and subsequent annual survival. The related 2020 predation experiment's Dryad archive includes `BCCH_Mob.zip` (~937 MB) plus feeder-rate files; the paper states RFID recorded individual ID, date and visit time. But the later paper's Figshare deposit appears to contain supplementary figures rather than an obvious ID-level survival table. This is currently a **data-linkage problem, not an absence-of-data problem**. It is the best same-population replication target if later-detection labels can be found in another archive or obtained from the authors.

### Wisconsin 2014–2015 extreme-winter data — survival but insufficient raw timing

The Dryad dataset for Latimer & Zuckerberg's extreme-weather study has a chickadee capture-history CSV and supports weekly/overwinter survival modeling, but the public version inspected exposes capture histories rather than the underlying high-resolution RFID visit stream. Not a direct chronotype replication as released.

### Amherst two-winter RFID data — best independent-population lead

The Dryad dataset for *Social network connections are positively related to temperature in winter flocks of black-capped chickadees* exposes:

- `RFID_data_Yr1.csv` (~15.4 MB)
- `RFID_data_Yr2.csv` (~6.4 MB)
- `Birds_Yr1.csv`
- `Birds_Yr2.csv`

This is the most promising **independent population** lead because year-1 chronotype can potentially be estimated from raw timestamps and year-2 re-detection can potentially be used as a return/apparent-survival proxy. The API metadata is public, but this environment's unauthenticated Dryad file-download endpoint returned HTTP 401, so ID persistence and sampling completeness are not yet verified locally.

## Most promising next steps

### 1. Replicate in the Amherst two-winter RFID dataset

Highest expected information gain. Verify first whether individual IDs persist between years and whether Year 2 coverage is sufficient that non-redetection has a defensible interpretation. If yes:

1. freeze a replication protocol before looking at Year2 membership;
2. derive Year1 first-feed chronotype with environment/daylight adjustment;
3. classify Year2 redetection;
4. test the same two-sided chronotype association;
5. meta-analyze Alberta + Amherst at the effect-size level.

An independent-population replication is far more valuable than refining the Alberta p-value.

### 2. Recover the 2018/19 UABG raw-ID + survival join

Search the related Dryad/OSF/Figshare archives more deeply, especially the 937 MB `BCCH_Mob.zip` and subsequent-year UABG data deposits. If survival IDs are not public, contact Mathot/Wijmenga with a very narrow request: the already-published 79-bird subsequent-detection vector, or permission to link publicly deposited IDs.

This would create a same-site, different-year replication with essentially the same protocol.

### 3. Build a multi-winter UABG analysis rather than chase single-season significance

The rough information calculation suggests the current N=137 is only decisive for large effects. The scientifically stronger question is whether chronotype predicts apparent survival **across winters**, with year-specific effects and a model for detection. A 5–7 winter archive could plausibly produce the hundreds of bird-years needed for useful precision.

Prefer a capture-mark-recapture / multi-state model to a simple binary fall detection outcome once multi-year histories are available. That directly addresses the survival-vs-detection limitation.

### 4. Reproduce both source papers exactly in R before public presentation

Lower information gain than independent replication, but necessary for a publishable/podium-quality artifact. Use R 4.3.x with `MCMCglmm`, `lme4`, `arm`, and the authors' scripts. Confirm that extracted timing posterior draws and LaRocque behaviour posteriors reproduce paper values, then rerun the frozen survival model propagating the joint posterior rather than independent Gaussian approximations.

### 5. Turn the methodology into the actual Latent Experiments asset

This pilot exposed a more useful agent workflow than “find unused columns”:

`same experiment → multiple papers → each paper projects different dimensions → find unjoined phenotypes/outcomes → validate phenotype reconstruction against a published signal → freeze → join outcome → replicate elsewhere`

The reusable system should enforce:

- a **data lineage graph** linking papers, datasets, cohorts, dates and identifiers;
- an explicit **outcome-seal** state;
- **known-signal validation** before testing new relationships;
- automatic git/hash preregistration;
- stability forks fixed before unsealing;
- a post-result **replication scout** rather than post-hoc hypothesis expansion;
- negative-results retention.

This may be the strongest SciPy contribution even if every substantive hypothesis is null.
