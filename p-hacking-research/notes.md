# Working notes

## 2026-10-03 — framing

Goal: find published, lay-friendly claims with data that are easy to obtain and reanalyse, specifically where reasonable analytic choices create a large researcher-degrees-of-freedom / multiple-testing surface.

Selection criteria:
1. Data are public and small/easy enough for a reproducible local analysis.
2. Claim is vivid to a nontechnical audience.
3. There are many plausible choices (exposure definition, outcome, subgroup, lag, covariates, functional form, geography, exclusions) so a multiverse / placebo analysis is meaningful.
4. Prefer an existing critique, reanalysis, replication package, or contradictory study so we have an external falsifier rather than inventing skepticism after seeing the result.
5. Prefer examples where the analysis can distinguish “claim survives a hard stress test” from “headline was selected from a large garden of forking paths.”

Important framing: the goal is not to label a paper “p-hacked” from the outside. The test is whether the headline is stable under a prespecified multiverse and against placebo exposures/outcomes.

## Motivating nuclear-power paper

Alwadi et al. (Environmental Health, 2025), “Residential proximity to nuclear power plants and cancer incidence in Massachusetts, USA (2000–2018)”.
- Ecological ZIP-code study, exposure = sum of inverse distance to operational plants within 120 km.
- Outcomes include all-cancer incidence and many site-specific cancers; analyses stratify by sex and age.
- The published paper explicitly says the site-specific associations were **not adjusted for multiple comparisons**.
- Open peer review raised latency, exposure-radius choice, migration, occupational exposure, and unexpected cancer-site findings.
- Authors added sensitivity analyses over 80–150 km radii and 1–8 year moving averages. These are useful, but do not test the broader “why nuclear plants rather than many other spatial landmarks?” placebo question.

## Candidate scan

### Tier 1

1. **Female hurricane names -> more deaths** — Jung et al., PNAS 2014.
   - 94 U.S. landfall hurricanes (92 after the paper's Katrina/Audrey exclusions); exact supplementary XLSX is only ~171 KB.
   - Same-data critiques showed strong specification sensitivity: pre-1979 naming regime, extreme-death storms, and omitted interactions matter.
   - Simonsohn, Simmons & Nelson (2020) later used this example in their specification-curve paper and published data/code at OSF.
   - This is probably the best first implementation: tiny, famous, already externally challenged, and the multiverse is finite enough to explain visually.

2. **Hot chili peppers -> lower mortality** — Chopan & Littenberg, PLOS ONE 2017.
   - NHANES III, 16,179 adults; adjusted HR 0.87 (95% CI 0.77–0.97).
   - The baseline questionnaire has an 81-item food-frequency questionnaire and the mortality linkage is public.
   - Better experiment than merely reproducing chili: apply the same defensible model template to every food item, plus cause-specific outcomes/codings, then locate chili inside the resulting empirical null/headline distribution.
   - Same data also produced a later headline: never eating breakfast associated with cardiovascular mortality (HR 1.87 vs daily breakfast).
   - Data assembly is more work than hurricanes, but one NHANES pipeline can support many future “X food extends/shortens life” stress tests.

3. **More Airbnb listings -> later violent crime** — Ke, O'Brien & Heydari, PLOS ONE 2021.
   - Boston census-tract panel, 2011–2018.
   - Public GitHub CSV is only ~356 KB (1,177 data rows) and already contains three Airbnb exposure families, crime/disorder outcomes, and lag/lead variables.
   - Natural multiverse: Airbnb density/penetration/usage × private conflict/social disorder/violence × concurrent/lag1/lag2/lead1/lead2 × model/covariate choices.
   - A 2024 London study is preregistered and publishes reproduction code/data, making it a useful external comparison.
   - Closest analogue here to the nuclear paper's spatial/ecological structure.

### Tier 2

4. **PM2.5 -> higher COVID mortality** — Wu et al., Science Advances 2020.
   - Full public GitHub data and R scripts.
   - Strong ecological/spatial confounding and time-cutoff degrees of freedom.
   - Good *positive control*: unlike a deliberately silly placebo, PM2.5 has a strong prior health mechanism. If our stress-test framework makes every serious association disappear, the framework is too aggressive.

5. **Referee red cards depend on player skin tone** — Silberzahn et al., “Many Analysts, One Data Set” (2018).
   - 29 teams answered the same question on the same open dataset and reached materially different estimates.
   - This is not a paper to “debunk”; it is the cleanest empirical benchmark showing that good-faith analyst choices alone create variation.
   - Use as a calibration case for our multiverse tooling and visualization.

6. **Marijuana dispensaries increase vs decrease neighborhood crime** — Denver studies.
   - Hughes et al.: dispensary presence associated with increases in most crime/disorder outcomes using Bayesian spatiotemporal Poisson models.
   - Brinkman & Mok-Lamme: using an IV strategy for endogenous dispensary locations, an additional dispensary estimated to reduce crime by ~19%.
   - Excellent demonstration that “same phenomenon, same city” can change sign when identification strategy changes.
   - Lower priority because exact raw-data reconstruction/package availability is less frictionless than the top three.

### Teaching/toy control

7. **Chocolate consumption -> more Nobel laureates** — Messerli, NEJM 2012.
   - Famous ecological correlation; later critiques show other foods/unrelated country variables can correlate similarly.
   - Extremely intuitive, but too obviously whimsical to test whether a serious-looking claim can fool us. Keep as a 5-minute introductory demo, not the main investigation.

## Rejected / deprioritized

- **Golf courses -> Parkinson disease (JAMA Network Open 2025):** vivid proximity claim and many distance/exposure choices, but the Rochester Epidemiology Project outcome data are private.
- **Fast-food proximity -> obesity:** very intuitive and many papers disagree, but exact individual outcome datasets are often restricted; recreating a comparable analysis from public sources is substantially more work.
- **2026 national nuclear mortality follow-ups:** close to the motivating question, but the papers state that individual underlying cancer-mortality data are confidential; source code is not deposited as a turnkey package.
- **Uber -> traffic fatalities:** public Harvard Dataverse replication exists but is hundreds of MB and much heavier than the alternatives.

## Best bespoke stress test for the motivating intuition

Rather than only ask whether the nuclear coefficient is significant, build a **placebo-landmark / placebo-location distribution**:

1. Fix a health-outcome surface and all modeling decisions *before* looking at landmark results.
2. Compute the nuclear-plant statistic.
3. Repeat the identical procedure for many placebo point patterns:
   - randomly relocated “plants” preserving the number of sites;
   - matched industrial/infrastructure landmarks if public coordinates are convenient;
   - spatial permutations that preserve broad regional density where possible.
4. Compare the observed nuclear statistic with the full placebo distribution, not only p=0.05.
5. Repeat over a prespecified grid of reasonable distance kernels/radii and report the entire specification curve.
6. Correct/jointly infer over outcomes if multiple cancer sites, ages or sexes are tested.

Public data make a version of this easy even without the Massachusetts registry microdata: State Cancer Profiles exports county cancer incidence tables, and CDC PLACES exposes county/tract/ZCTA data through downloads/APIs. It would not be an exact replication of Alwadi et al.; it would be a falsification exercise aimed directly at “many things are spatially correlated with cancer.”

## Method anchors

- Steegen et al. (2016), “Increasing Transparency Through a Multiverse Analysis”: enumerate reasonable preprocessing/analysis choices rather than silently choose one.
- Simonsohn, Simmons & Nelson (2020), “Specification curve analysis”: define justified/nonredundant specifications, visualize all results, and conduct joint inference. Their demonstrations include the hurricane-name study.
- Silberzahn et al. (2018), “Many Analysts, One Data Set”: analyst degrees of freedom are empirically large even without deliberate p-hacking.

## Sources

- Nuclear/cancer: https://doi.org/10.1186/s12940-025-01248-6
- Hurricane original: https://doi.org/10.1073/pnas.1402786111
- Hurricane critique (Malter): https://doi.org/10.1073/pnas.1411428111
- Hurricane critique (Christensen & Christensen): https://doi.org/10.1073/pnas.1410910111
- Specification curve: https://doi.org/10.1038/s41562-020-0912-z
- Hot chili/mortality: https://doi.org/10.1371/journal.pone.0169876
- Breakfast/mortality: https://doi.org/10.1016/j.jacc.2019.01.065
- Airbnb/Boston crime: https://doi.org/10.1371/journal.pone.0253315
- Airbnb/London crime: https://doi.org/10.1111/1745-9125.12383
- Airbnb Boston data: https://github.com/heydarilab/AirbnbCrime
- Airbnb London reproduction: https://github.com/clanfear/airbnb-crime_criminology_2024
- PM2.5/COVID reproduction: https://github.com/wxwx1993/PM_COVID
- Many Analysts: https://doi.org/10.1177/2515245917747646
- Multiverse analysis: https://doi.org/10.1177/1745691616658637
- Dispensaries/crime (Hughes et al.): https://doi.org/10.1080/07418825.2019.1567807
- Dispensaries/crime (Brinkman & Mok-Lamme): https://doi.org/10.1016/j.regsciurbeco.2019.103460
- Chocolate/Nobels: https://doi.org/10.1056/NEJMon1211064
- CDC PLACES portal: https://www.cdc.gov/places/tools/explore-places-data-portal.html
- State Cancer Profiles: https://statecancerprofiles.cancer.gov/

## 2026-10-03 — longevity headline factories

User preferred the NHANES logic: instead of asking only whether one published exposure predicts mortality, reveal the much larger set of other exposures that could have generated an equally attractive “X helps you live longer” headline.

### New ranking

1. **Broaden NHANES into a general mortality headline factory.**
   - CDC currently supplies public-use linked mortality files for NHANES III and continuous NHANES 1999–2018. Mortality status is unaltered; some follow-up/cause values are synthetic for disclosure protection.
   - Existing headline papers include chili, tea, coffee, sleep, tooth count and religious attendance.
   - Tea is especially useful: NHANES 2001–2018, 43,276 adults / 6,275 deaths; 3–<5 cups/day HR 0.79 and estimated age-50 life expectancy 32.93 vs 30.69 for non-drinkers, while >=5 cups/day did not continue the apparent advantage.
   - Recommendation: first vary only the exposure, using one frozen analysis template. Add specification curves later.

2. **HRS/CAMS books -> mortality** is the strongest new single-paper candidate.
   - Published cohort: 3,635, up to 12 years, adjusted ~20% lower mortality for book readers.
   - Exact same CAMS questionnaire measures ~31 daily/monthly activities: TV, papers/mags, books, music, sleep, walking, exercise, visits, phone/email, work, computer, prayer, cleaning, laundry, gardening, errands, cooking, grooming, pet care, affection, helping, volunteering, religious attendance, clubs, money management, medical self-care, cards/games/puzzles, concerts/movies/lectures, music-making, arts/crafts, home improvement.
   - This gives unusually clean, non-contrived counterexamples on the same questionnaire and often the same units.
   - HRS download requires account/login.

3. **MIDUS purpose -> mortality** is the best psychological-variable factory.
   - Current Aug-2026 mortality release contains 2,822 known decedents through Dec 2025.
   - Mostly public-use via ICPSR/NACDA; registration/terms apply.
   - Many overlapping constructs: purpose, affect, life satisfaction, self-esteem, mastery, growth, relationships, control, personality, social support, religion/spirituality.
   - Existing papers independently headline purpose, religion/spirituality, personality, SES.
   - Useful instability evidence: a longer-follow-up MIDUS personality analysis did not replicate earlier neuroticism/agreeableness mortality findings, though conscientiousness remained predictive.
   - Operational caveat: MIDUS 2026 terms prohibit sending downloaded public-use data to public/external LLM services; analyze locally.

4. **NHIS hearing -> mortality**: zero-friction/high-power backup.
   - CDC public mortality linkage + annual public survey files.
   - Hearing difficulty paper reports adjusted OR 1.5 for “a lot of trouble” and 1.6 for deaf.
   - Counterexample space broad but less charming; many variables are obvious health proxies.

5. **CLHLS leisure -> mortality** is a literature-level positive example.
   - N=30,070 adults age 80+, 23,661 deaths.
   - Near-daily TV/radio, cards/mah-jong, reading, gardening, pets/domestic animals, and religion all associated with lower mortality, HRs ~0.82–0.89.
   - This is nearly the result we hope to expose elsewhere and supports a healthy-enough-to-participate/common-cause interpretation.
   - Data access is request/sign-in rather than fully anonymous direct download.

6. **ELSA enjoyment -> mortality**: interesting but UK Data Service registration and less neatly matched alternatives.

7. **GSS-NDI happiness/TV/trust -> mortality**: conceptually excellent but hold; current mortality-linkage access is less clear/easy than older papers imply.

### Sources checked

- CDC linked mortality data: https://www.cdc.gov/nchs/linked-data/mortality-files/index.html
- Tea/NHANES: https://pmc.ncbi.nlm.nih.gov/articles/PMC11603940/
- Coffee/NHANES: https://pmc.ncbi.nlm.nih.gov/articles/PMC12516614/
- Sleep/NHANES: https://pmc.ncbi.nlm.nih.gov/articles/PMC10301724/
- Teeth/NHANES: https://pmc.ncbi.nlm.nih.gov/articles/PMC9365626/
- Religious attendance/NHANES III: https://pmc.ncbi.nlm.nih.gov/articles/PMC2659561/
- Books/HRS paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC5105607/
- HRS CAMS data: https://hrsdata.isr.umich.edu/data-products/2001-consumption-and-activities-mail-survey-cams
- HRS CAMS codebook: https://hrs.isr.umich.edu/sites/default/files/meta/2001/cams/codebook/CAMS2001a_r.htm
- MIDUS purpose: https://pmc.ncbi.nlm.nih.gov/articles/PMC4224996/
- MIDUS mortality 2026: https://www.icpsr.umich.edu/web/NACDA/studies/37237
- MIDUS series: https://www.icpsr.umich.edu/sites/nacda/midus
- MIDUS religion/spirituality: https://pmc.ncbi.nlm.nih.gov/articles/PMC10298693/
- MIDUS personality longer follow-up: https://pmc.ncbi.nlm.nih.gov/articles/PMC4103968/
- NHIS hearing: https://pubmed.ncbi.nlm.nih.gov/30832489/
- CLHLS leisure: https://pmc.ncbi.nlm.nih.gov/articles/PMC8019061/
- ELSA enjoyment: https://pmc.ncbi.nlm.nih.gov/articles/PMC5154976/

## 2026-10-03 — executed NHANES 2005–06 pilot

Built and ran nhanes_pilot.py after freezing a 15-exposure registry before mortality results.

Primary cohort/model:
- age >=40, NHANES 2005–06;
- 2019 public linked all-cause mortality;
- demographics: age, sex, race/ethnicity, education, PIR, marital status;
- interview weights + PSU/stratum cluster identifier;
- BH FDR across 15 exposures.

Primary result:
- 6/15 pass BH q<.05: moderate activity, walking/biking for transport, moderate home/yard work, vigorous activity, TV >=3h/day (harm direction), weekly religious attendance.
- All six remain BH-significant after adding smoking.

Same-sample sensitivity using MEC/self-rated-health complete cases and MEC weights:
- demographics: 5/15 BH-significant;
- + smoking: 4/15;
- + self-rated health: 0/15.
- Moderate activity, TV, walking/biking remain nominal p<.05 after health adjustment, all q≈.067.
- On the identical sample, adding self-rated health attenuates |log HR| about 14%–39% for the strongest activity/TV effects.

Interpretation:
- This is not a random false-positive factory: significant exposures cluster around being active/engaged and avoiding sedentary time.
- That is more useful: many plausible causal-sounding headlines can be projections of a shared health/frailty/participation state.
- Health adjustment may itself be over-adjustment if activity affects health before mortality. Treat attenuation as evidence of common structure/sensitivity, not proof that activity has no causal effect.
- Sleep was null when prespecified as a linear standardized exposure. Do not change that primary coding post hoc just because published sleep papers use U-shaped bins; reproduce published bins separately and label that analysis.

Provenance:
- Official CDC XPT downloads used for questionnaires.
- DEMO_D and PAQ_D hashes match the independent official-source manifest in profdrheld-eng/nhanes-activity-contrast.
- ftp.cdc.gov timed out from LocalMCP. A GitHub copy in ehsanx/Reproducible-NHANES-Analysis had LF-normalized mortality text: 496,426 bytes, 10,348 lines, Git blob cb1ac585d9703698c8912927f12a530ef10e0381.
- Restoring CRLF yielded 506,774 bytes and SHA-256 69388ea13a4f395f29d9d21bc51941b9759003490d4b00f6ff12a1bc5f8dba5c, exactly matching the independent CDC-source manifest. Therefore analyzed mortality bytes are bit-identical to the official CDC file.

Verification:
- 6 unit tests pass: mortality fixed-width parser, exposure-variable presence, binary/range cleaners, smoking recode, BH correction.
- results/nhanes_2005_2006_headline_factory.csv contains all 75 exposure × adjustment results.

Next: NHANES III 81-item food-frequency family. Keep one model fixed and vary only food exposure before adding any specification multiverse.

## 2026-10-03 — NHANES III 60-food scan executed

Frozen exposure family:
- Paper calls baseline questionnaire an 81-item FFQ.
- Public adult file contains 60 predefined named comparable "times/month" food/beverage fields plus six free-text other-food slots and nonfrequency/check fields.
- Frozen registry uses the 60 named monthly fields only; chili is HAN4JS.

Primary model:
- NHANES III adults 18+, current official 2019 mortality linkage.
- Any consumption vs zero for every food, matching published chili coding.
- Age, sex, race, ethnicity, education, marital status, low income (<$20k), employment.
- Interview weights + cluster-robust errors.
- BH FDR across all 60.
- Employment was added before finalizing results because the chili paper explicitly includes it in Model 2.

Final result:
- 24/60 nominal p<.05.
- 21/60 BH q<.05: 20 protective, 1 harmful.
- Chili: HR 0.921, p=.0798, q=.171, rank 28/60 by p.
- Strong counterexamples: cakes/cookies/brownies HR .773; wine .776; yogurt .839; pizza .884; hard liquor .875; chocolate/fudge .919; salted snacks .909.
- Liver/organ meat is harmful, HR 1.103, q=.0178.
- Among 12 vegetable fields, broccoli, carrots, other peppers, tossed salad, tomatoes and Brussels sprouts/cauliflower all pass the full 60-food FDR correction. Other peppers: HR .874, q=.003; chili: HR .921, q=.171.

Interpretation:
- This is stronger than classical p-hacking. The 21 FDR results are not just random false positives.
- Many foods are markers for correlated health/diet/social patterns. Multiple-testing correction does not solve exposure selection + causal storytelling.
- Scientifically safe claim: "many alternative foods support stronger mortality associations than chili under one frozen exposure-selection screen," not "the chili paper is wrong" or "cake prolongs life."

Replication caveat:
- Published chili paper used mortality follow-up through 2011 and N=16,179 complete cases; Model 2 HR=.87 p=.020, Model 3 HR=.87 p=.014.
- Current 2019 CDC linkage supersedes older releases and uses enhanced matching; some vital statuses changed.
- Exploratory Model-3 recreation using exam alcohol yields ~13.1k complete cases, not 16,179; chili ~.95 and nonsignificant. Do not use this result until historical covariate/sample construction is reconciled.
- Model2 is the only validated/reported food-scan mode.

Artifacts:
- nhanes3-food-scan.md
- nhanes3-food-registry.csv
- nhanes3_food_scan.py
- test_nhanes3_food_scan.py
- results/nhanes3_food_headline_factory.csv

Recommendation:
- Make NHANES III foods the flagship example.
- Next execute HRS/CAMS books vs ~31 everyday activities as independent replication.

## 2026-10-03 — HRS/CAMS books-vs-activities scan executed

Frozen family before mortality results:
- CAMS 2001 A1-A31: 31 side-by-side weekly/monthly activity-hour questions.
- Primary exposure coding: any time vs zero time, matching the paper's any-books vs none analysis.
- Exposure-specific complete cases primary; all-31 common complete-case sample sensitivity.
- Contrasts with <100 in either group declared non-estimable; TV, sleep/nap, grooming hit this rule. For conservative BH they remain in the 31-hypothesis family as p=1.

Published books paper calibration:
- Paper N=3,635; 62.1% female; 59% book readers; 27.4% mortality; adjusted any-book HR=.80; unadjusted ~.76; book tertiles .83/.77.
- HRS 2000 respondent weight, not the separate CAMS weight, reproduces paper composition: ~62.6% female, ~59.5% book readers, ~27.6% weighted NDI mortality through 2012.
- Near-replication primary book model: N=3,584, 1,079 deaths, adjusted HR=.816 (95% CI .709-.939), p=.00444, q=.01253.
- Unadjusted book HR=.7601, essentially exactly the published .76.
- Exact published tertile cutoffs: reconstructed T2 HR=.866; T3 HR=.779, with T3 essentially exactly the published .77.
- One published covariate, self-rated eyesight, is absent from the RAND HRS 2000-2014 v2 mirror used here, so call this near-replication, not exact replication.

Primary headline-factory result:
- 28/31 modelable.
- 20/28 nominal p<.05.
- 18/31 survive FDR.
- Books rank 11/28 by p.
- Stronger FDR associations: house cleaning .572; meal prep .595; errands .631; religious attendance .723; meetings .715; helping others .752; listening music .749; gardening .789; walking .772; prayer/meditation .759.
- Other FDR hits after books: volunteering .798; laundry/mending .785; sing/play music .779; paid work .724; affection .831; money management .815; sports/exercise .840.
- Periodicals HR=.840 but q>.05, preserving the published books-vs-periodicals contrast.

Common 2,805-person sample:
- 28 modelable, 19 nominal, 16/31 FDR.
- Books rank 12; HR=.778 q=.00742.
- 14 of primary 18 FDR hits overlap; primary-only: work, affection, sing/play music, money management.

Post-hoc mechanism sensitivity:
- Added baseline ADL, IADL, mobility limitation counts.
- Exposure-specific FDR 17/31; common sample 18/31.
- Books .816→.821; cleaning .572→.584; meal prep .595→.601; errands .631→.626; music .749→.745.
- Only sports/exercise drops from primary FDR list.
- Thus simple baseline functional limitations do not explain the headline multiplicity.

Interpretation:
- Independent cross-domain replication of NHANES exposure-selection story.
- Stronger than pure false-positive/p-hacking story because many results survive family correction.
- Defensible claim: statistical evidence can be strong for many possible exposures; p-values/FDR do not explain why one exposure deserved the causal narrative/headline.
- Do not infer that books/cleaning/cooking/etc are noncausal; this is a specificity/selection argument.

Data provenance/legal:
- Official HRS CAMS page says N=3,866; mirror CAMS file exactly N=3,866.
- Mirror Git blob hashes verified exactly:
  CAMS01_R.dta ebd182f03400ab47fb3dda703b141be0ab7890c2
  CAMSW_R.dta 1c1fad0ea9bcd82268a024aa678aadd9802e73a7
  RAND HRS ZIP ea293e1cf09519c614e3bff4102a3d50f93e1fda
- Current HRS Conditions of Use require registration and prohibit ordinary third-party redistribution.
- Raw mirror files must not be committed/distributed. Formal publication/presentation should rerun from files downloaded under Anand's own HRS registration.
- Aggregate results/code can remain in repo.

Artifacts:
- hrs-cams-scan.md
- hrs-cams-activity-registry.csv
- hrs_cams_scan.py
- test_hrs_cams_scan.py
- results/hrs_cams_activity_headline_factory.csv

HRS raw-file cleanup:
- Verified analysis inputs against public mirror Git object hashes and HRS official CAMS N=3,866.
- HRS current Conditions of Use require user registration and limit third-party redistribution.
- Deleted data/hrs/ mirror copies after producing aggregate results.
- test_hrs_cams_scan.py skips the local-file provenance test when official HRS data are not installed.
- Formal publication/presentation requires a rerun using Anand's own official registered HRS downloads.
