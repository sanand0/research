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

### Post-H002 next-step scout

A focused scan of the already-discovered Mathot-lab OSF graph found many adjacent projects (diurnal feeder use, body temperature, social information, caching, recapture bias), but no immediate clean pairing of the 2020/21 raw timestamp stream with a fresh, subsequent annual-survival outcome. The q8a62 recapture dataset concerns recapture attempts in 2019/2020 and is not a direct future-survival endpoint for the 2020/21 timing stream.

Decision: stop mining the now-unsealed p3hz4 outcome and stop lateral chickadee archaeology for now. The next agent-led experiment should move to a fresh outcome/dataset, while Amherst remains the best independent H001 replication if its Year-1 raw file becomes normally accessible.

## 2026-09-08 — fresh-domain scout after H002

### Red kite NestTool candidate: scientifically strong, operationally blocked

A fresh candidate was identified in Oppel et al.'s red-kite NestTool data: 258 Swiss individual-seasons plus an independent German GPS validation population. The public analysis script shows the published nesting-success classifier uses movement summaries across settlement, incubation and chick phases; late chick-stage nest attendance is explicitly important to success classification. A latent early-warning question therefore remains: whether settlement/pre-breeding movement alone predicts later breeding success.

The 26.9 KB analysis script downloaded successfully from Zenodo, but Zenodo blob delivery for larger files repeatedly timed out: API metadata, a 6.6 MB package ZIP, a 4 KB range request on the German tracking CSV, and a normal 53 MB German CSV download all failed. These failures were logged. The candidate is preserved but not pursued in this environment rather than weakening data-access safeguards.

### Blue-tit Silwood candidate: accessible and explicitly latent

Figshare record 11856108 is fully accessible and contains small public data/code. The author code confirms the source analysis tests female laying-date intercept and budburst reaction-norm slope against lifetime breeding success. The paper explicitly discusses heterogeneity in individual residual variance as potentially interesting but does not model it.

A streaming extractor now persists predictor columns only; clutch-size/hatchling outcomes remain sealed. The predictor file has 2,278 rows from 1,447 females. Budburst is available for only 658 rows / 517 females and yields only 32 females with >=3 paired LD-BD observations, so an individual residual-variance phenotype conditional on observed budburst is rejected as too sparse. The full laying-date record is much richer: 502 females have >=2 observations, 220 >=3, and 77 >=4 (maximum 7). Candidate H003 therefore uses laying-date predictability after year and age adjustment, with split-half reliability evaluated among >=4-observation females.

### Blue-tit H003 candidate rejected before outcome

Outcome-blind feasibility found 1,282 females whose last observed year was before 2019; 439 had >=2 laying records, 193 >=3, 69 >=4. A cheap year+age-adjusted residual-SD screen already had weak independent-half reliability (odd/even rho=.083; early/late rho=.148).

A partially pooled Bayesian location-scale model nevertheless found clear population heterogeneity in female residual laying-date SD (`sigma_log_sigma` median .533, 3–97% quantiles .446–.636), with the full fit converging. However, among the 69 females with >=4 observations the independent odd/even posterior ranking was rho=.166, below the frozen .20 gate; split fits also had 6 and 31 divergences. Candidate H003 is therefore rejected without viewing clutch-size or hatchling values. No sampler tuning or phenotype search was attempted after failure.

This is a useful distinction: population-level heterogeneity in residual variance does not imply a sufficiently measurable individual "predictability" phenotype. With 3–7 lifetime breeding records, ranking individuals by variance is too noisy for the proposed fitness join.

## 2026-09-08 — fresh-domain continuation: blue tit rejection, red-kite blocker, honey-bee H004 freeze

### Blue-tit H003 closed before outcome

The Silwood laying-date predictability candidate was outcome-blind. Although the full hierarchical location-scale fit estimated clear population heterogeneity, individual predictability rankings failed the frozen independent-half gate (odd/even posterior rho ~0.166 < 0.20) and split fits had divergences. H003 was rejected without opening clutch-size/hatchling outcomes. No sampler/threshold tuning was done after failure.

### Red-kite early-warning candidate preserved, not executed

NestTool's published success model uses information from later nesting/chick stages, leaving a distinct question about pre-breeding movement predicting later reproductive success. Small code files were accessible but Zenodo delivery of the large GPS streams repeatedly timed out, including range requests. Candidate preserved; no outcome mining.

### Honey-bee H004 — predictor-side gate

Peirson et al.'s PLOS supplements provide 362 colonies with repeated population measurements and survival. Raw outcome-containing CSV was never saved. A streaming extractor persisted only Alberta May/June/August 2014 predictors.

Predictor cohort:
- 240 Alberta colonies total;
- 225 complete adult-population histories (116 Southern Alberta, 109 Northern Alberta);
- 6 apiaries;
- May/June/August 2014 use the same source visual population-estimation method.

Primary history predictor is the OLS slope of log1p adult population vs actual inspection date across the three 2014 points. Outcome-blind diagnostics:
- three-point vs June→August slope rho ~0.759;
- three-point slope vs August size rho ~0.781, so August size is mandatory;
- after August size + region + treatments, residual slope SD remains ~44.9% of marginal slope SD.

Interpretation is deliberately **history beyond snapshot**, not an independent biological "growth trait." The slope conditional on final size necessarily contains prior-size information.

H004 asks whether that history predicts first-winter viability at April 2015. Primary logistic model adjusts August size, region, protein supplementation and fumagillin assignment. Recent-slope and apiary-fixed-effect models are frozen sensitivities.

Before freeze, outcome-bearing source fields (`Viable`, `Colony Death`, `Last Viable`) were absent from persisted predictor data and no post-August individual outcome values were viewed or summarized.

### H004 unseal implementation erratum

The first frozen H004 execution failed before fitting any model because `Colony Number` was parsed as integer in the precomputed feature CSV and string in the freshly streamed PLOS source. Set intersection was therefore empty and Patsy later failed while trying to encode zero-level categorical factors. Diagnosis viewed only aggregate row/type counts; no coefficient/result existed. One aggregate source fact became visible during debugging: across all 362 study colonies, April 2015 contained 278 `Viable` and 84 `Not Viable` rows. This was not used to change any predictor, cohort, model, sensitivity, or decision rule.

Erratum: cast `Colony Number` to string on both sides before the frozen join. Scientific specification unchanged.

### H004 result and closure

After the ID-type erratum, the frozen model fit 225 Alberta colonies: 204 survived to the April 2015 assessment and 21 did not.

Primary three-point trajectory OR 0.864 (95% CI 0.301–2.478, p=.785). The prespecified June→August trajectory flipped sign (OR 1.221, CI 0.590–2.528); apiary-fixed three-point model OR 0.743 (CI 0.247–2.230). Decision: **H004 not supported; SENSITIVE** because the trajectory sign is not stable.

A post-hoc known-signal validation found August size in the expected positive direction but also imprecise (region-adjusted OR 1.529, CI 0.958–2.440). With only 21 failures, the full model had ~3.5 failure events per parameter and rough 80% detectable OR ~4.5 at the observed SE. This converts H004 from an apparent N=225 design into an outcome-information failure.

Protocol updated: future candidate screening uses event count/effective outcome information, not raw sample size alone.

## 2026-09-08 — H005 red-kite early range-contraction candidate, pre-outcome freeze preparation

A fresh NestTool candidate was screened after H004's outcome-information failure. The public Swiss prepared data contain 697 individual-seasons and sufficient known nesting-success outcomes; the H005 predictor cohort restricts to field-observed nests with early movement data.

A temporal-provenance audit rejected seemingly early nest-relative variables (`revisitsSettle`, `timeSettle`, distance-to-nest metrics): NestTool first infers a candidate nest location from season-wide tracking and then computes those phase summaries, so they leak future information. Phase-specific MCP areas are self-contained and retained.

An archive-semantics failure was caught outcome-blind: NestTool uses exact MCP area `1` as a synthetic missing-phase fill; the first extractor incorrectly treated all values <=1 as missing even though sub-unit areas are valid. Correcting to exact-1 exclusion yielded 287 complete early MCP histories.

A GPS-density gate requiring >=100 fixes in settlement and >=100 fixes in early incubation yields 268 seasons from 115 birds across six years. MCP95 and MCP99 contraction rankings agree strongly (rho ~0.83). Contraction95 is strongly related to current early-incubation range (rho ~-0.69), making current MCP mandatory: H005 is explicitly a history-beyond-current-state estimand.

H005 asks whether settlement-to-early-incubation MCP contraction predicts eventual nesting success among observed nesting attempts, using bird-clustered binomial GEE. The primary MCP95 model and MCP99 sensitivity are fixed in `hypothesis-005.md` and `analysis-plan-005.md`; no success labels have been persisted or inspected before the freeze.

### H005 outcome-availability failure and exploratory salvage freeze

Frozen H005 commit `b6245d6158252c74fbd12a02ca290951993d0d08` failed before model fitting because an eligible season had an empty `success` label. A post-unseal diagnostic inspected **availability only**, not yes/no values: 245/268 frozen seasons have known success and 23 are missing/blank. Missingness is not obviously random: unlabeled seasons are younger on average and have lower mean contraction.

Therefore H005 is **not executable as preregistered**; it will not be retroactively rewritten as a successful preregistration. Before viewing any yes/no counts or coefficients, H005-E freezes an explicitly exploratory complete-case GEE plus MCP99 and observed-predictor IPW sensitivities. Any H005-E signal requires independent replication.

#### H005-E source-status parser erratum

The first H005-E execution failed before any fit or yes/no count because NestTool `success` also contains the explicit status `not checked`. The frozen H005-E plan already defines complete cases as only `yes`, `no`, 1, or 0; therefore `not checked` is outcome-unavailable by the frozen rule. Implementation erratum: map exactly `not checked` to missing. No cohort criterion, predictor, model, sensitivity, or interpretation changed.
