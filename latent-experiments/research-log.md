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

## 2026-09-08 — Step 6 outcome unsealed and tested

### Outcome unsealing boundary

The step-6 analysis plan and derived predictors were committed at `d15b1f54b4c9dfe08dd479fcea2734463616569e`, timestamp `2026-09-08T14:08:19+08:00`. Individual `Survived` labels were read only after that commit.

Outcome counts: 138 source-A birds total; 80 detected next fall and 58 not detected. The predeclared timing join contains 137 birds because one source-A bird (`01103F82A5`) was already excluded by Hobbs et al.'s sex-data rule. Primary joined outcome count: 79 detected, 58 not detected.

### Primary result: stable null

Frozen model: `Survived ~ early_z + total_z + C(AgeSex)`.

Early-chronotype beta = +0.2736 (SE 0.2090), OR 1.3147 per SD earlier, 95% CI 0.8728–1.9803, p=.1904. This does not meet the preregistered support rule.

All preregistered major specifications retained the positive sign and crossed the null:

- no total-feeder adjustment: OR 1.231, CI 0.871–1.740, p=.240;
- Jan9-Feb14 timing window: OR 1.416, CI 0.943–2.125, p=.094;
- residual-mean timing phenotype: OR 1.324, CI 0.876–2.001, p=.183;
- frozen spatial-residual adjustment: OR 1.315, CI 0.872–1.982, p=.191;
- quadratic term: p=.956.

2,000/2,000 predictor-uncertainty draws also remained null: combined OR 1.302, CI 0.857–1.978.

Leave-one-bird-out beta range +0.207 to +0.341; zero sign reversals. The positive point estimate is not driven by one bird.

Conclusion under frozen rules: **STABLE NULL / INCONCLUSIVE FOR MODEST EFFECTS**, not discovery.

### Post-outcome known-signal validation: failure

A naive check used mean off-territory rate and the frozen residualized off-territory phenotype to see whether they recovered LaRocque et al.'s known negative association with survival. Both were essentially zero (p~.98), even though the published random-effect analysis found a negative association.

This showed that the residualized-mean approximation was inadequate for hierarchical binary off-territory behaviour. It also demonstrated why a latent-experiment pipeline needs source-paper known-signal reproduction, not merely plausible feature engineering.

### Post-outcome known-signal validation: recovery

`analysis/validate_sourceA.py` fitted a binomial mixed model with random bird and core-feeder effects and the source paper's fixed age-sex × temperature structure. Its bird random effects recover the published survival direction and similar magnitude:

- Python beta -0.352 per standardized off-territory random effect; OR 0.703; 95% CI 0.495–1.0005; p=.0503.
- source author-code posterior mode ~-0.245, CrI -0.503 to -0.050.

A clearly post-hoc chronotype model adjusted using this improved off-territory random effect still gives OR 1.328, CI 0.879–2.004, p=.178. Early chronotype and off-territory propensity correlate only r=-0.050.

Thus correcting the weak frozen spatial approximation does not rescue or overturn the chronotype result.

### Information / power limitation

Using the observed primary SE as a first-order information approximation, a beta around 0.585 (OR ~1.80) would be needed for ~80% conventional two-sided power at the current N. If the observed beta ~0.274 were the true effect and SE scaled ideally as 1/sqrt(N), about 627 comparable bird-years would be required. This is a planning approximation, not formal prospective power analysis.

The current confidence interval itself is the more important message: effects from OR 0.87 to 1.98 remain compatible with the data. The null is not evidence of no effect.

### Replication scout

1. Haave-Audet 2019/20 UABG OSF `62Y7K`: public survival labels + experimental/baseline summaries, but archived analysis data do not contain the raw all-day RFID visit stream needed for chronotype. Not a direct replication as released.
2. Mathot et al. 2018/19 UABG risk-taking/survival: paper explicitly states RFID recorded ID/date/time and later survival for 79 birds. Related Dryad archive has a ~937 MB `BCCH_Mob.zip`, but the 2022 Figshare deposit inspected exposes supplementary material without an obvious individual survival table. Very promising same-site replication if IDs can be linked across deposits or obtained from authors.
3. Latimer & Zuckerberg 2014/15 Dryad: public capture histories support weekly/overwinter survival but the inspected release contains capture history rather than raw timestamped RFID. Not direct.
4. Amherst College two-winter Dryad `10.5061/dryad.sj3tx96c2`: explicitly has raw `RFID_data_Yr1.csv` and `RFID_data_Yr2.csv` plus bird metadata for both years. This is the strongest independent-population replication lead if IDs persist and Year2 redetection is biologically defensible. Dryad's file API returned HTTP 401 from this environment, so the raw files were not yet inspected locally.

Full result, limitations and ranked next steps are in `RESULTS-001.md`.

## 2026-09-08 — replication hardening and portable phenotype calibration

### LocalMCP verification

LocalMCP was explicitly checked at the start of this continuation and worked. The existing experiment artifacts and the pre-outcome freeze commit `d15b1f5` were intact.

### Failure/recovery: stochastic known-signal validation

A repository verification rerun found that `analysis/validate_sourceA.py` was not bit-reproducible: `BinomialBayesMixedGLM.fit_vb()` produced slightly different random effects across runs. Setting NumPy's global seed was insufficient. Current statsmodels exposes an explicit `rng=` argument; using `fit_vb(rng=20260908)` fixed the source of nondeterminism. The substantive off-territory validation remains unchanged (OR ~0.703, p ~.0503).

### Amherst replication: design evidence and access blocker

Rothberg et al. report 74 unique RFID-detected chickadees in Year 1 (21 Nov 2020–1 Mar 2021), using 10 feeders across two forest tracts. Year 2 used eight feeders only in the larger tract. Thus Year-2 absence cannot be interpreted as death; the external endpoint must be next-winter redetection conditional on comparable observation opportunity.

Dryad metadata confirms Year1/Year2 raw RFID files and bird tables. Actual file downloads currently trigger AWS WAF / human confirmation. Several ordinary curl/API/browser attempts failed. The CAPTCHA/WAF was not bypassed. Year-2 individual membership remains sealed.

A process error was corrected: `Birds_Yr1.csv` contains 23 attribute records, but this is not the Year-1 RFID population; the paper reports 74 RFID birds. Feasibility counts must be grounded in the observational stream, not a metadata subset.

### Success: portable chronotype calibrated before external outcomes

`analysis/calibrate_portable_chronotype.py` tests external-study-compatible phenotype constructions on Alberta predictor data only. No survival outcome is read.

Against the full Hobbs phenotype:

- no-demographics (temperature + daylength) early chronotype: Pearson r=.9615, Spearman rho=.9247;
- daylength-only: r=.9614, rho=.9248;
- intercept-only: r=.9482, rho=.8812;
- **date-fixed-effects**: r=.9612, rho=.9230;
- date-fixed-effects + daily total count: only r=.7692, rho=.6360 — rejected before external outcome access.

For total feeder use, the date-fixed-effect phenotype correlates r=.9613 / rho=.9545 with the full Hobbs total-use random effect.

This supports a portable external model using only RFID timestamps and dates: `first_clock_minutes ~ C(date) + (1|bird)` and `daily_total_events ~ C(date) + (1|bird)`. Date fixed effects absorb all common day-level timing shifts, making explicit sunrise/weather covariates unnecessary for the cross-population phenotype.

### Amherst protocol frozen

`replication-amherst-001.md` freezes a staged replication before Year-2 IDs are viewed. Key safeguards: >=10 events per bird-day, >=5 qualifying days, date-fixed-effect phenotypes, design-only Year-2 feeder unseal first, primary exposure-match >=80% of Year-1 events at feeders still observable in Year 2, and only then individual redetection membership.

The replication is explicitly labelled `next-winter redetection`, not survival.


## 2026-09-08 — second replication scout: Oregon rejected, Farr/Arteaga promoted

### Oregon lead: promising filenames, wrong outcome

Dryad DOI `10.5061/dryad.hdr7sqvj9` (*Experimentally induced flight costs do not lead to increased reliance on supplemental food in winter by a small songbird*) initially looked promising because its archive includes `hourly_visitation_rate.csv` and `proportion_returning.csv`. Metadata/API inspection showed six small analysis datasets. Direct Dryad file downloads returned HTTP 401 in this environment.

Reading the source-paper description clarified that `proportion returning` refers to birds returning to feeders after an experimental feather-clipping treatment, not next-winter return or annual survival. It is therefore **rejected as a replication of chronotype -> later survival/redetection**. This is another reminder not to infer outcome semantics from filenames.

### Farr et al. 2021: public UABG RFID survival outcome found on OSF

A much stronger same-site lead was found: Farr, Haave-Audet, Thompson & Mathot (2021), *No effect of passive integrated transponder tagging method on survival or body condition in a northern population of Black-capped Chickadees*. Their OSF project `zvfpb` is directly accessible and contains four files: `RFID.csv`, `NORFID.csv`, metadata, and complete R analysis code.

Crucially, `RFID.csv` has **not been downloaded or opened**. Only the metadata and code were read. Public metadata says the RFID survival file contains unique individual ID, redetection method, survival/event time, censoring, catching season/date and sex. The R code confirms Cox survival analysis and an RFID-only (`PIT == D`) survival analysis.

### Arteaga-Torres 2018/19 predictor stream confirmed in detail

The Figshare electronic supplement for the 2018/19 predator experiment was downloaded and inspected. It establishes that:

- RFID antennas were installed at feeders from early October 2018;
- batteries and SD cards were serviced every four days;
- registrations stored **date, time and PIT-tag hex code**;
- antenna clock drift was checked against observer tags and was never >1 minute over a four-day interval;
- duplicated RFID registrations within 5 seconds were removed in the authors' analyses;
- one feeder had a four-day battery failure, which the authors excluded;
- treatment dates and times are fully enumerated in supplementary Table S1.

The main paper additionally states that the readers registered the time and identity of all PIT-tagged feeder visitors, and treatment days occurred every second day with rest periods. Thus the archive is potentially suitable for a conservative chronotype phenotype using only non-experimental days.

### Blocker: identifier namespace mismatch

The predictor stream is keyed by 10-digit PIT-tag hex code. Farr's survival release is keyed by a study `ID`; its R code treats at least some values as short numeric identifiers (`68`, `107`, `249`). No public mapping has yet been found.

A related 2019/20 UABG open dataset (Haave-Audet) demonstrates that the group otherwise publishes individual outcomes directly under `TransponderHexCode`, reinforcing that an explicit mapping is the correct linkage mechanism rather than probabilistic matching.

**Hard rule:** do not open Farr `RFID.csv` until an auditable `ID <-> PIT hex` mapping is obtained. Never infer mapping from row order, sex, capture dates or outcome patterns.

### Design failure caught before outcome: survival clock / immortal time

Farr's event clock begins at capture, but the candidate chronotype is measured later in winter 2018/19. A naive Cox model from capture would assign pre-chronotype immortal time to the chronotype predictor.

`replication-alberta-farr-001.md` therefore freezes a landmark/left-truncated survival design before any Farr outcome rows are opened. The primary timing phenotype uses non-experimental days only, date-fixed-effect random intercepts, duplicate removal <5s, and feeder-use adjustment. The analysis stops if mapping, continuous raw coverage, sample size, or left-truncation semantics cannot be established.

### Current replication ranking

1. **Farr/Arteaga UABG 2018/19** — scientifically clean same-site different-year replication if ID mapping and raw Dryad access are solved; strongest outcome follow-up, but currently two hard data-linkage/access blockers.
2. **Amherst 2020/21 -> 2021/22** — independent population and raw two-winter RFID; cleaner independence, but Year-2 feeder coverage changed and Dryad raw download is WAF-blocked.
3. **Multi-winter UABG archive** — highest eventual information/power and best route to capture-mark-recapture, but requires assembling data across projects/authors.
4. **Oregon experimental feeder dataset** — rejected for current replication because its return outcome is post-treatment feeder return, not annual redetection.

## 2026-09-08 — H002 candidate mining inside the 2018/19 risk-taking cohort

### Replication linkage success, raw-timestamp failure

Public OSF projects from the Mathot lab were traced systematically rather than by filename search alone. The `p3hz4` risk-taking/survival cohort contains 79 birds. Outcome-blind direct identifier comparison established that **74/79 p3hz4 IDs match the Arteaga 2018/19 PIT-hex IDs exactly**. This resolved the earlier belief that a separate ID crosswalk was required for most of the cohort.

A second earlier assumption failed: HTTP range inspection of the ~937 MB `BCCH_Mob.zip` central directory showed eight large WAV files plus housekeeping entries. It is a mobbing-call stimulus archive, **not continuous RFID feeder logs**. The public 2018/19 release therefore does not provide the all-day timestamp stream required for the proposed chronotype replication. That replication remains blocked despite successful identifier linkage.

A 2020/21 OSF project (`h4693`) does contain a ~16.9 MB timestamp-level feeder stream, confirming the lab's later data format, but it is the wrong winter for the p3hz4 outcome cohort.

### Outcome-blind alternative hypotheses inside p3hz4

The source paper/code models average feeding rate and average latency-to-resume-feeding against annual survival. It does not test individual response slopes or residual behavioral predictability against survival.

A predictor-only copy of the public source was created with the survival column physically excluded: 1,009 observations, 79 birds. Sixty-nine birds experienced all four treatments; 73 had at least two visual-present and two visual-absent observations; median repeated observations per bird = 14.

#### Rejected A: individual visual-cue plasticity

A random visual-cue slope model converged and estimated nonzero slope variance, but the individual slope ranking **failed replication within the experiment**: Rep 1–2 vs Rep 3–4 slopes correlated negatively (Pearson ~-0.34; Spearman ~-0.32). Rejected before survival access.

Lesson: a fitted random-slope variance does not establish a reproducible individual trait.

#### Rejected B: individual temperature plasticity

The full random temperature-slope variance was essentially on the optimizer boundary (~0.0024) and split fits were inconsistent. Rejected before survival access.

#### Advanced C: residual behavioral predictability

Simple outcome-blind residual metrics showed modest but consistently positive split-half reliability. This motivated a proper hierarchical location-scale model rather than choosing whichever residual metric looked best.

### Hierarchical location-scale pre-outcome gate

`analysis/h002_predictability_preoutcome.py` models bird-specific mean log latency and bird-specific residual log-SD with partial pooling. Acceptance thresholds were recorded before viewing the hierarchical result. Four-chain NUTS reruns then produced:

- full between-bird log-SD heterogeneity `sigma_log_sigma`: median 0.268, 95% interval 0.196–0.348;
- max R-hat 1.00 and zero divergences in all primary/split/robust fits; minimum bulk ESS >=620;
- Rep 1–2 vs 3–4 predictability rho 0.373 (bootstrap 95% CI 0.134–0.575);
- odd vs even rho 0.442 (0.230–0.614);
- primary vs mean model expanded with feeder+replicate rho 0.969 (0.936–0.985);
- Normal vs Student-t(5) likelihood rho 0.969 (0.938–0.982);
- predictability vs number of observations rho 0.182;
- predictability vs mean latency rho -0.457, making mean latency a mandatory survival covariate.

The phenotype therefore passes the pre-outcome gate but is only moderately reliable; a future null may be attenuated by measurement error.

H002 is frozen in `hypothesis-002.md` and `analysis-plan-002.md` before survival unsealing.

## 2026-09-08 — H002 freeze, unseal and result

H002 passed all predictor-side gates and was frozen at git commit `63d7838337926959e1b147b6fcf06783b2132b9d` at 2026-09-08T16:49:34+08:00. The survival file was absent at commit time; manifest and script syntax checks passed.

### Outcome extraction surprise

The public p3hz4 source file has 1,009 repeated behavioral rows but only 79 non-missing annual-survival entries — one per bird. An initial pandas assertion failed because `(NaN > 0)` becomes False, unlike R `ifelse`, which preserves NA. The source author code binarizes and then `slice(1)` per ID. Reproducing that exact first-row convention yields 44 positive and 35 zero outcomes, matching the publication.

### Frozen H002 result

The preregistered uncertainty-propagating logistic analysis completed all 1,000 imputations without failure:

- primary N>=4: OR 0.831, 95% CI 0.439–1.573, p=.570;
- N>=6: OR 0.824, CI 0.426–1.594, p=.565;
- N>=8: OR 0.812, CI 0.397–1.659, p=.567;
- unadjusted for mean latency: OR 0.865, CI 0.485–1.545, p=.625.

Decision: **H002 not supported; STABLE across preregistered forks.**

A separate scipy logistic fit using posterior-mean phenotypes gave OR 0.754 (CI 0.437–1.301), independently confirming the negative/null direction. The frozen outcome JSON hash was identical across two reruns.

Per the fresh-outcome rule, no H003 will be mined against this now-unsealed survival column.
