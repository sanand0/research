# Research log

## 2026-09-08 — setup

Created a preregistration-like protocol before inspecting candidate outcomes. The central guardrail is that a hypothesis must be frozen before any computation involving its predictor/outcome relationship.


## 2026-09-08 — broad screening

Screened recent open datasets in behavioral ecology, thermal ecology, plant/herbivore plasticity, movement ecology and large comparative datasets. Recorded candidates and rejects in `screening.md`.

The Black-capped Chickadee 2024 spatial-use dataset initially looked unusually strong because its raw RFID data include per-visit timestamps that the published analysis code does not use. Downloaded the public OSF/Dryad data and complete author R analysis into `candidates/chickadees/` and saved SHA-256 hashes.

### Negative finding: obvious timestamp hypothesis already published

A literature search found Hobbs et al. 2024, *Exploring sources of (co-)variation in timing and total daily feeder visits in a wild population of black-capped chickadees*. It uses the same University of Alberta population and winter 2022-23, and directly models first/last feeder time relative to sunrise/sunset, temperature, daylength, age/sex and feeder visit totals. Therefore the initial idea “cold shifts feeding time” is not novel and was rejected before any new outcome analysis.

This is an important workflow lesson: searching only around the focal paper title is insufficient. Search by population, authors, field season, methods, and each candidate variable before claiming it was untested.

### Stronger cross-paper latent experiment

Hobbs et al. publish timing phenotypes but no survival analysis. LaRocque et al. publish next-fall apparent survival from the same winter/population but do not use raw time-of-day. The LaRocque survival file contains 138 individual IDs; all 138 IDs exist in Hobbs et al.'s historical age/sex metadata. Survival values have not been read or summarized.

A web literature search for combinations of black-capped chickadee / chronotype / first feeder visit / activity timing / annual survival found no direct test. Close prior work establishes that chronotype is a recognized repeatable trait in passerines and that its fitness consequences are uncertain; a 2026 great-tit study found no association with measured breeding fitness. This makes a survival test worthwhile, while “no indexed paper found” is not enough to claim novelty.

Candidate primary relation: environment-adjusted first-feeder chronotype -> apparent annual survival, specifically asking whether timing carries information beyond total feeder-use amount and age/sex. This is now ready for a formal freeze before opening survival labels.

### Prior-art correction before freeze

A broader chronotype-fitness search found two important great-tit studies that prevent any broad claim that "chronotype and fitness have never been linked":

- Meijdam et al. (2025), *Female chronotype is not related to annual and lifetime reproductive success in a free-living songbird* (Royal Society Open Science, DOI 10.1098/rsos.250380), tested morning chronotype against annual/lifetime reproductive success and longevity and found no clear association.
- Strauß et al. (2026), *Female chronotype relates to lay date but not fitness in an island population of great tits* (Oecologia, DOI 10.1007/s00442-025-05857-3), likewise found chronotype related to lay date but not measured fitness outcomes.

Therefore the novelty claim is deliberately narrower: I found no indexed direct test, as of 2026-09-08, of **winter first-feeder chronotype predicting next-fall apparent survival in black-capped chickadees, conditional on total feeder use**, despite the two components being available from overlapping studies of the same field season. This is a plausible latent cross-paper experiment, not evidence of globally unprecedented chronotype-fitness research.

## 2026-09-08 — Step 6 preparation, still outcome-blind

### LocalMCP verification

LocalMCP access was explicitly tested before continuing and succeeded. The project was at preregistration commit `c01f0fa2f00c` with a clean project subtree before new analysis artifacts were created.

### Success: obtained the missing raw timing stream

Downloaded Hobbs et al.'s OSF `2022-2023data.csv` from OSF project XRT69. File size ~154 MiB, 1,532,565 data rows, 10 columns. SHA-256:

`c002dae47475c2deaa5fccb6431f81cbab85dbf139131f9eb999e9e6ab8216b3`

This completed the largest missing input from steps 1–5.

### Failure: exact published R pipeline cannot run locally

The authors used R 4.3.1 + MCMCglmm 2.35. LocalMCP has no `Rscript`, so exact reproduction could not be executed. Rather than install an unplanned statistical stack or silently replace it, this was recorded as a method deviation and a Python approximation was designed before outcome access.

### Success: exact raw-data filtering reproduced

`analysis/prepare_timing.py` implements the published data-selection pipeline using the raw OSF stream and author metadata. It matches the author analysis structure:

- 90 study days;
- 52 explicit feeder-14 bird exclusions;
- five unsexed exclusions;
- >=10 feeder visits per bird-day;
- 143 birds;
- 11,761 retained bird-days.

### Failure/recovery: false 11,762-row verification alarm

An initial assertion expected 11,762 bird-days because the authors' plotting code indexes 11,762 predictions. Inspection showed that their code deliberately appends one duplicate row solely to prevent a prediction-function error, then explicitly removes prediction row 11,762 and rejoins to the original 11,761-row dataset. The correct analytic count is therefore 11,761; the assertion was corrected.

This is a useful reproducibility lesson: hard-coded plotting dimensions are not necessarily analysis sample sizes.

### Failure/recovery: L-BFGS produced a bogus singular mixed model

The first statsmodels MixedLM approximation used L-BFGS. It converged numerically to zero random-intercept variance for both first-feeder timing and total visits and therefore could not return random effects. This contradicted the published evidence of repeatable among-individual variation.

Outcome-blind optimizer stress test:

- Powell: converged, first-feed random variance ~743.90, total-feed ~457.82;
- BFGS: converged to essentially the same values;
- CG: converged to essentially the same values;
- L-BFGS: singular zero-variance boundary with infinite log-likelihood artifact.

Therefore Powell was frozen as the Python implementation. This is not model shopping on the survival result: survival labels were still unopened, and three independent optimizers agreed on the non-singular predictor model.

### Success: predictor phenotypes are internally stable before outcome access

Full-window Python random-intercept approximation:

- first-feed random variance = 743.90;
- first-feed residual variance = 2701.08;
- approximate repeatability = 0.216;
- total-feed random variance = 457.82;
- total-feed residual variance = 640.67;
- approximate repeatability = 0.417.

Of 138 survival-study IDs, 137 have valid Hobbs timing phenotypes. The excluded ID (`01103F82A5`) is one of Hobbs et al.'s five predeclared unsexed birds, so exclusion is not outcome-driven.

Outcome-blind stability checks:

- full-window vs Jan 9–Feb 14 early-chronotype phenotype: r = 0.957;
- full-window vs Jan 9–Feb 14 total-feeding phenotype: r = 0.953;
- mixed-model vs residual-mean early phenotype: r = 0.981;
- mixed-model vs residual-mean total-feeding phenotype: r = 0.987;
- early chronotype vs total feeder-use phenotype: r = 0.508.

The last correlation reinforces the preregistered need to adjust for feeding amount.

### Success: off-territory sensitivity covariate reproduced without outcomes

`analysis/prepare_spatial.py` follows LaRocque et al.'s core-feeder definition and correctly recovers the two explicitly documented two-core-feeder birds (`3B001878E9`, `3B0018A4C3`). It builds a transparent residualized off-territory propensity for later sensitivity analysis using the published age-sex-specific temperature fixed-effect structure. It does not read survival outcomes.

### Freeze before outcome opening

`analysis-plan-001.md` now fixes:

- Python method deviation from MCMCglmm;
- primary 137-bird population;
- primary logistic model;
- predictor standardization;
- uncertainty-propagation approximation;
- shared-window, residual-mean, spatial-adjustment and nonlinear sensitivity forks;
- separation/sparse-event/null-result rules;
- explicit false victories that will not count as discovery.

Individual survival labels remain unopened as of this entry.
