# Candidate screening

Started 2026-09-08. This records both positive and negative candidates. A reject is useful evidence about where the latent-experiment workflow fails.

## Selection rules

Strong candidates need: rich open raw data; narrow published question leaving measured variables unused; interpretable mechanism; clean unit of analysis; enough observations; plausible novelty after literature search; preferably an independent replication path; and a way to freeze the hypothesis before seeing the candidate relationship.

## 1. Black-capped chickadees, winter RFID feeder use — SELECTED

### Source A: spatial behavior + survival

Megan LaRocque, Jan J. Wijmenga, Kimberley J. Mathot (2024), *Age, sex, and temperature shape off-territory feeder use in black-capped chickadees*, Behavioral Ecology 35(6), arae080. DOI: 10.1093/beheco/arae080. Data: Dryad DOI 10.5061/dryad.47d7wm3pn; mirror/related repository OSF 7hnfk.

Raw data downloaded locally:

- `candidates/chickadees/data_FeederVisits.csv` — each RFID feeder visit, including date, **time**, feeder and individual PIT-tag ID; 392,974 visit rows plus header.
- `candidates/chickadees/data_AllDates.csv` — bird-day aggregates and temperature.
- `candidates/chickadees/THC_Survival.csv` — annual apparent-survival outcome for 138 birds. **Values remain sealed in this phase.** Only header/row count and IDs were accessed; no survival labels were inspected.
- `candidates/chickadees/analysis.R` — complete author analysis, including main and supplementary analyses.
- `candidates/chickadees/README.txt`, `SHA256SUMS`.

What Source A tested:

1. whether daily feeder visitation increased under colder temperatures, and whether effects differed by age/sex;
2. whether probability of visiting a non-core (off-territory) feeder varied with temperature and age/sex;
3. repeatability / among-individual variation in space use and feeder visit rate;
4. whether among-individual off-territory propensity and total feeder visit rate predicted detection the following fall (apparent annual survival);
5. robustness checks including all dates, alternate model families/transformations, individual-by-environment effects, and rarefaction by feeder.

Crucially, the author R code reads `data_FeederVisits.csv` but never uses the `Time` column. It aggregates raw records into feeder identity/count/space-use variables. Thus the raw timestamps are genuinely unused *in this paper*.

### Initial latent idea — REJECTED after literature search

**Rejected:** colder days shift first/last feeding time; age/sex modify this temporal response.

Reason: this is already a published analysis from the same population and same winter. See Source B below. This was a valuable failure: inspecting only Source A would have produced a false novelty claim.

### Source B: timing + feeding amount

Nathan L. Hobbs, Deborah M. Hawkshaw, Jan J. Wijmenga, Kimberley J. Mathot (2024), *Exploring sources of (co-)variation in timing and total daily feeder visits in a wild population of black-capped chickadees*, Biology Letters 20, 20240365. DOI: 10.1098/rsbl.2024.0365. Data/code: OSF DOI 10.17605/OSF.IO/XRT69.

Small metadata/code files downloaded locally under `candidates/chickadees-timing/`.

What Source B tested:

1. first feeder visit relative to sunrise;
2. last feeder visit relative to sunset;
3. total daily feeder visits;
4. effects of ambient temperature, daylength, and age-sex class on all three;
5. repeatability / among-individual differences in first/last timing and visits;
6. within- and among-individual covariance among first timing, last timing, and total daily visits;
7. post-hoc relationship between feeding-window length and feeding rate.

The analysis uses 90 continuous days from 1 Dec 2022 to 28 Feb 2023, largely encompassing Source A's Jan-Feb subset. The code contains no survival analysis and no reference to survival.

Published result relevant to hypothesis generation (safe because already public): colder conditions were associated with later first feeder visits, earlier last feeder visits, and *more* total daily visits. First/last timing was individually repeatable; first-visit timing was more repeatable than last-visit timing.

### The latent join

Source B contains an environment-adjusted chronotype / first-feeder timing phenotype. Source A contains next-fall apparent survival for 138 birds from the same winter population. All 138 survival-file IDs occur in Source B's historical individual metadata. The two papers cite overlapping feeder data but do not test **chronotype -> survival**.

Literature search through 2026-09-08 found no indexed study directly testing **winter first-feeder chronotype against next-fall apparent survival in black-capped chickadees**, especially conditional on total feeder use. This is *not proof of global novelty*. Broader chronotype-fitness work already exists: Meijdam et al. (2025; Royal Society Open Science, DOI 10.1098/rsos.250380) found female great-tit chronotype unrelated to annual/lifetime reproductive success or longevity, while Strauß et al. (2026; Oecologia, DOI 10.1007/s00442-025-05857-3) found chronotype related to lay date but not measured fitness. Black-capped chickadee work separately links survival to feeder-use amount and off-territory behavior. The novelty therefore lies in the species/season/resource-acquisition question and, methodologically, in joining two analyses of the same field season that did not ask this cross-paper question.

### Candidate relations generated before outcome access

A. Does environment-adjusted **first-feeder chronotype** predict annual apparent survival?

B. Does timing predict survival **after controlling for how much the bird feeds**? This distinguishes “when” from “how much”; Source B shows earlier starters tend to make more visits, while Source A shows total visit rate is moderately positively related to survival.

C. Does the *plasticity* of timing to temperature (individual random slope) predict survival? Mechanistic but more estimation-heavy and not directly quantified in Source B's main model.

D. Are temporal and spatial resource-acquisition strategies coupled: do birds with earlier/longer feeder-use windows also engage more or less in off-territory feeder use?

E. Does temporal-spatial strategy explain the negative survival association with off-territory use? Interesting mediation question but too ambitious for the first latent experiment.

**Selection:** A/B combined into one pre-registered primary question: does first-feeder chronotype predict survival conditional on total feeding amount and basic intrinsic covariates? See `hypothesis-001.md` once frozen.

Why selected: direct fitness endpoint; same individuals; measured but unjoined variables; interpretable; clean outcome sealing; manageable sample size; strong SciPy story; and negative/null result remains informative.

## 2. Urban dark-eyed juncos — HOLD

2026 Dryad DOI 10.5061/dryad.905qftv10, *An urban bird population exhibits more fear in the non-breeding season*.

Rich variables include FID, sex, age, observer, date/time, sunrise-relative time, temperature, wind, group size, conspecific/heterospecific context and precise breeding status. The paper focuses on seasonal flight-initiation distance and reports starting distance/group size effects, leaving plausible context/time interactions.

Why not first: direct Dryad file retrieval was blocked/403 in the LocalMCP environment, so I could inspect indexed README/schema but not independently audit the complete analysis code/data. Also FID determinants are heavily studied, making novelty harder to establish without a deeper domain search.

## 3. Collared pikas and thermal refugia — REJECT FOR NOW

Wall & Brodie (2026), Oikos, DOI 10.1002/oik.11677; Dryad 10.5061/dryad.gtht76j2v. Includes individual one-minute observations and a 6.5 MB temperature-logger series.

Attractive because raw microclimate and behavior are rich. But the published paper already directly asks how temperature and patch quality interact to alter pika surface detections / refuge use. The most obvious latent relationships are close variants of the headline analysis; individual-level data appear comparatively small. Replication path is weaker than chickadees.

## 4. Grasshopper multi-trait warming experiment — REJECT FOR FIRST PASS

Baker et al. (2026), *Trait Plasticity in Herbivore Populations Maintains Geographic Patterns of Herbivory on a Dominant Plant Species Under Warming*, DOI 10.1002/gcb4.70047; Dryad 10.5061/dryad.cc2fqz6m1.

Excellent open structure: separate behavior, physiological metrics, plant biomass, respiration, survival, and temperatures. But the paper's central claim is already explicitly integrative: it tests blends of behavioral and physiological plasticity, metabolic consequences, survivorship and trophic impact. Rich data, but less “unused dimension hiding in plain sight.” Keep as a future stress-test for automated cross-table hypothesis generation.

## 5. Moose thermal-refuge trade-offs — HOLD

Levine et al. (2025), *Sex-specific trade-offs influence thermoregulation under climate change*, Ecology. Dryad 10.5061/dryad.b2rbnzspx.

Rich used/random bedding-site data include sex, calf status, habitat, vegetation, soil, canopy, weather, animal age and—in a subset—body/fat condition. Potential latent question: does body condition or age shift wind-vs-canopy refuge choice, beyond sex/reproductive state?

Why lower priority: more fragmented/subset data, movement-choice modeling is specialized, and the apparent latent variables are likely confounded with sex/age/location. Independent replication is not obvious.

## 6. Fruit-fly long-term aggregation monitoring — HOLD

2026 Ecological Entomology; Dryad 10.5061/dryad.dfn2z35gd. Paper reports that larger fruit-fly aggregations persist longer, with environmental covariates apparently not explaining the persistence result.

Potential for temporal/sequential questions, but dataset is small (~29 KB) and likely already tailored to the paper's narrow analysis. Less latent richness than the RFID case.

## 7. Crop-pest abundance × temperature mega-dataset — HOLD

2026 Dryad 10.5061/dryad.ffbg79d87, *Field data challenge predictions of universal crop pest proliferation under warming*. ~21.7 MB abundance/temperature data plus species traits and analysis code.

Potentially powerful for trait-specific exceptions and cross-species latent hypotheses. But the published question is already broad and comparative, so multiple-testing and phylogenetic/non-independence issues make a “new relationship” easy to manufacture and hard to trust. Better as a later benchmark once the workflow is mature.

## 8. Tree seedling heat × drought survival — HOLD

2026 Dryad 10.5061/dryad.k3j9kd5ph. Seedling-level survival/growth plus substrate moisture and physiological traits (LMA, minimum conductance, turgor-loss point, root:shoot ratio).

Potential latent trait × treatment interactions are biologically meaningful, but they are also the first thing a plant physiologist would normally test. Novelty probability lower than the chickadee cross-paper join.

## Search lesson

The best candidate did **not** emerge by finding the largest dataset. It emerged by noticing that two papers from the same field season partitioned a rich measurement stream into different scientific questions. The latent experiment is therefore often a **join across papers**, not merely an unused column within one paper.
