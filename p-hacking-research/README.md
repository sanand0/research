# P-hacking research: reproducible claims to stress-test

> **Big lesson:** The association may be real, but the headline is often just one of many stories the same data could support.

I tried asking a simple question: when a study says “X helps you live longer,” how special is X really? In NHANES, 21 of 60 foods predicted mortality even after correcting for multiple tests; chili wasn’t special—cake, wine, pizza and chocolate looked stronger. In another dataset, books predicted longer life, but so did cleaning, cooking, gardening, music, prayer and many other activities. The big lesson: **the association may be real, but the headline is often just one of many stories the same data could support.**

The strongest executed target is now **NHANES food → mortality**: one frozen model across 60 comparable named foods produces 21 FDR-significant mortality associations, while the published hot-red-chili exposure ranks only 28th in the current linkage. **Female hurricane names → deaths** remains the cleanest classic specification-fragility example, and **Airbnb → crime** remains the best spatial analogue to the nuclear/cancer paper.

The objective should be narrower than “prove papers were p-hacked.” From observational papers alone we usually cannot know the authors' search process. The reproducible question is:

> **Would the headline have survived if every reasonable analytic choice—and relevant placebo—had been shown?**

That gives us a falsifiable output: a specification curve / multiverse plus a null or placebo distribution.

**Longevity follow-up:** [`nhanes3-food-scan.md`](nhanes3-food-scan.md) finds 21/60 named foods FDR-significant while hot red chili ranks only 28th. [`hrs-cams-scan.md`](hrs-cams-scan.md) independently reproduces the phenomenon: the published books→longevity effect near-replicates (adjusted HR 0.816 vs 0.80 published), but 18/31 everyday CAMS activities survive FDR and books rank only 11th among 28 estimable contrasts; cleaning, cooking, errands, music, gardening, prayer, volunteering, etc. are stronger. [`nhanes-pilot.md`](nhanes-pilot.md) and [`longevity-candidates.md`](longevity-candidates.md) cover supporting analyses/candidates.

## Shortlist

| Priority | Lay headline | Why it is unusually useful | Data / effort | Stress test |
|---|---|---|---|---|
| **1** | **Eating hot chili peppers helps you live longer** | **Executed:** 60 predefined named foods share the same monthly-frequency structure; 21 survive FDR under one frozen model while chili ranks 28th | **Excellent:** direct public CDC adult + mortality files; scripts/results now in this repo | Keep one survival model fixed and compare every named food; then replicate the published chili specification separately |
| **2** | **Female hurricanes kill more people** | Exact same-data critiques already show that defensible choices materially change the result; later used as a textbook specification-curve example | **Excellent:** 92–94 rows; supplementary XLSX ~171 KB; published OSF data/code | Model family × interaction terms × pre/post-1979 × extreme-storm exclusions × population/exposure controls |
| **3** | **Airbnb makes neighborhoods more violent** | Spatial/ecological, like the nuclear paper; the supplied Boston CSV already exposes many plausible exposure/outcome/lag choices | **Excellent:** public ~356 KB analysis CSV (1,177 rows); 2011–2018 tract panel | 3 Airbnb measures × 3 social/crime outcomes × current/lags/leads × model/covariate choices; compare with preregistered London study |
| **4** | **Air pollution increases COVID deaths** | Complete public code/data, major public-interest claim, substantial spatial/time/model flexibility—but strong prior mechanism makes it a useful *positive control* | **Excellent:** turnkey GitHub reproduction | Death-count cutoff × epidemic timing × covariates × spatial controls × model family; test whether effect is unusually stable |
| **5** | **Referees give more red cards to darker-skinned players** | 29 independent analyst teams attacked the exact same open question. It directly measures analytic variability rather than inferring it | **Excellent:** open data/materials | Recreate the distribution of defensible analyst choices; use it to calibrate how much spread to expect from a multiverse |
| **6** | **Marijuana dispensaries increase/decrease crime** | Two Denver papers point in opposite directions: association models report increases for most crime outcomes; an IV design estimates a ~19% decline | **Moderate:** exact turnkey replication data were not verified in this scan, so expect more reconstruction than the top choices | Reproduce naïve spatial association, then progressively address siting/endogeneity; see where sign changes |
| **Toy** | **Chocolate creates Nobel laureates** | Instantly understood ecological correlation and easy placebo-variable lesson | **Easy** | Substitute many foods/country attributes; show how easy it is to manufacture another “explanation” |

## 1. Female hurricanes: the strongest first experiment

Jung et al. (PNAS, 2014) reported that hurricanes with more feminine names caused more deaths, interpreting this through gender stereotypes and perceived risk.

Why start here:

- The published supplementary dataset is tiny (~171 KB) and contains the hurricane-level observations.
- Contemporary PNAS letters reanalyzed the same data and challenged the result. Critiques focused on the pre-1979 period (before male and female names alternated), extreme-fatality storms, and omitted interaction terms.
- Simonsohn, Simmons & Nelson's 2020 **Specification Curve Analysis** paper explicitly reused the hurricane example, with the data and code deposited on OSF.
- Therefore we are not inventing arbitrary alternatives after seeing the answer; the literature itself documents reasonable competing specifications.

**Experiment:** reproduce the headline model, enumerate a prespecified grid of defensible choices, plot every effect estimate, then generate a joint null by permutation. A lay reader should be able to see whether “female names kill” is a broad feature of the data or a narrow ridge in specification space.

Sources:
- Original: https://doi.org/10.1073/pnas.1402786111
- Malter reanalysis: https://doi.org/10.1073/pnas.1411428111
- Christensen & Christensen reanalysis: https://doi.org/10.1073/pnas.1410910111
- Specification-curve data/code: https://osf.io/9rvps/
- Specification-curve paper: https://doi.org/10.1038/s41562-020-0912-z

## 2. NHANES: build a “food headline factory”

Chopan & Littenberg (PLOS ONE, 2017) analyzed 16,179 NHANES III adults and reported an adjusted hazard ratio of **0.87 (95% CI 0.77–0.97)** for mortality among consumers of hot red chili peppers.

The more interesting fact for us is methodological: NHANES III asked an **81-item food-frequency questionnaire**. Instead of asking only “does chili predict mortality?”, ask:

> If I gave an analyst 81 foods and several reasonable mortality outcomes/codings, how many compelling “X helps you live longer” stories could the same dataset produce?

That is almost exactly the phenomenon behind *Things That Apparently Cause Cancer*, but with one coherent public dataset and a reproducible model.

A second published headline from the same NHANES III era makes the point concrete: a 2019 JACC study reported that never eating breakfast, versus eating it every day, was associated with cardiovascular mortality (HR **1.87, 95% CI 1.14–3.04**); its all-cause estimate was 1.19 (0.99–1.42).

**Experiment:** write one survey-weighted Cox template first. Apply it unchanged to every food item. Then add clearly separated multiverse dimensions—food coding, exclusions, covariate sets, all-cause vs cause-specific death—and control the family-wise/FDR error or use a permutation max-statistic. Chili becomes one dot in the full search space rather than the only dot shown.

Sources:
- Chili paper: https://doi.org/10.1371/journal.pone.0169876
- Breakfast paper: https://doi.org/10.1016/j.jacc.2019.01.065
- NHANES III: https://wwwn.cdc.gov/nchs/nhanes/nhanes3/default.aspx
- NCHS linked mortality files: https://www.cdc.gov/nchs/data-linkage/mortality-public.htm

## 3. Airbnb and crime: best spatial analogue

Ke, O'Brien & Heydari (PLOS ONE, 2021) concluded that increases in Airbnb listings—but not reviews—predicted more violence in Boston neighborhoods in later years, interpreting the pattern as an erosion of local social organization.

This is unusually convenient. Their public analysis CSV is only about 356 KB (1,177 data rows) and includes:

- three Airbnb exposure families: listing density, building penetration, and reviews/usage;
- private conflict, social disorder, and violence outcomes;
- contemporaneous, 1-year and 2-year lags, plus lead variables;
- tract/year structure and median income.

That creates a natural, finite specification space without inventing silly choices. There is also a 2024 London study by Lanfear & Kirk that was **preregistered** and publishes reproduction code/data, useful as an external check rather than merely another post-hoc model.

**Experiment:** enumerate every substantively defensible exposure × outcome × lag choice, with a small set of model/covariate specifications fixed in advance. Leads are especially valuable as falsification tests: if future Airbnb predicts past crime about as well as lagged Airbnb predicts later crime, the causal story is weakened.

Sources:
- Boston paper: https://doi.org/10.1371/journal.pone.0253315
- Boston data: https://github.com/heydarilab/AirbnbCrime
- London paper: https://doi.org/10.1111/1745-9125.12383
- London reproduction: https://github.com/clanfear/airbnb-crime_criminology_2024

## 4. PM2.5 and COVID mortality: a useful positive control

Wu et al. studied long-term PM2.5 exposure and county-level COVID mortality. Their repository includes the data plus preprocessing, modeling and figure code.

This differs from the first three: the point should **not** be “find a way to make it disappear.” Air pollution already has strong prior biological and epidemiological support. That makes this a good control for the method.

**Experiment:** vary defensible epidemic cutoff dates, spatial/covariate adjustments and model specifications. If the association remains directionally stable across most of the multiverse, it demonstrates that a specification-curve framework can distinguish a robust observational pattern from a fragile one.

Source/code: https://github.com/wxwx1993/PM_COVID

## 5. Many Analysts: use as the calibration benchmark

Silberzahn et al. gave the same dataset and research question—whether soccer referees give more red cards to darker-skinned players—to **29 independent analyst teams**. Their approaches varied substantially even though everyone was answering the same question; the paper publishes the data/materials.

This is the empirical answer to “but would reasonable researchers really make different choices?” Yes. Use this dataset to validate our tooling and visualization before applying the same ideas to contentious substantive claims.

Sources:
- Paper: https://doi.org/10.1177/2515245917747646
- Open data/materials are linked from the paper via OSF.

## 6. Marijuana dispensaries and crime: the sign can flip

Two Denver studies are a useful pair rather than a single replication target:

- Hughes, Schaible & Jimmerson modeled 3,981 grid cells and reported statistically significant increases in most neighborhood crime/disorder categories near medical and recreational dispensaries.
- Brinkman & Mok-Lamme used an instrumental-variable strategy aimed at endogenous dispensary siting and estimated that an additional dispensary led to **17 fewer crimes per month per 10,000 residents**, about a **19% decline** relative to the mean.

This is a more sophisticated lesson than multiple comparisons: *where businesses locate is itself selected*. A model can be precisely estimated and still answer the wrong causal question.

Sources:
- https://doi.org/10.1080/07418825.2019.1567807
- https://doi.org/10.1016/j.regsciurbeco.2019.103460

## Directly stress-testing the nuclear intuition

The Massachusetts nuclear paper is itself a good motivation for a placebo experiment. It models cancer incidence over 2000–2018 against an inverse-distance measure to seven nuclear plants within 120 km. Its site-specific analysis fits separate cancer × sex × age models, and the paper explicitly labels those site-specific significance results as **not adjusted for multiple comparisons**. It also reports sensitivity checks over 80–150 km radii and 1–8 year moving-average exposure windows.

Those checks ask, “does the result survive nearby versions of our nuclear model?” Your deeper question is different:

> **If I had picked some other set of places first, how often could I have produced an equally persuasive proximity story?**

### A clean placebo-location design

1. **Freeze the outcome and model first.** Pick one cancer outcome, one geography, covariates, and one proximity kernel before generating placebo locations.
2. Compute the statistic for actual nuclear plants.
3. Generate thousands of placebo point sets with the same number of “plants.” A simple version samples pseudo-sites geographically; a stronger version matches broad urban/rural or industrial geography.
4. Run the identical model on every placebo set.
5. Plot the actual nuclear statistic inside the placebo distribution.
6. Separately enumerate a prespecified set of reasonable distance kernels/radii and show the entire specification curve.
7. If using multiple cancer sites/sexes/ages, make the family of tests explicit and use joint inference/FDR/max-statistic rather than highlighting nominal p<0.05 cells.

For a fast public-data version, **State Cancer Profiles** exposes exportable county cancer-incidence tables, while **CDC PLACES** provides county, place, census-tract and ZCTA datasets through downloads/APIs. This would be a falsification experiment rather than an exact reproduction of the Massachusetts registry analysis, but it directly tests the “some locations will look dangerous by chance/confounding” hypothesis.

- State Cancer Profiles: https://statecancerprofiles.cancer.gov/
- CDC PLACES: https://www.cdc.gov/places/tools/explore-places-data-portal.html

## Why I would not start with several tempting papers

**Golf-course proximity and Parkinson disease (2025):** extremely vivid and spatial, but the underlying Rochester Epidemiology Project patient/control data are not an easy public download. It fails the reproducibility criterion.

**Fast-food proximity and obesity:** strong public-interest claim and a huge garden of distance/density definitions, but many of the strongest studies depend on restricted individual-level health records. A public reconstruction is possible, but it becomes a new study rather than a quick replication.

**The 2026 national nuclear-mortality follow-ups:** very close to the motivating claim, but the authors report that individual underlying cancer-mortality data are confidential; they are therefore less attractive than the top candidates for an exact, low-friction reproduction.

**Chocolate consumption and Nobel laureates:** keep it as a five-minute teaching demo. It is memorable, and substitute-food/country correlations make the ecological-fallacy point, but readers already expect it to be tongue-in-cheek. It is less useful for demonstrating how a serious-looking claim can survive peer review yet remain specification-sensitive.

## Suggested sequence

Do **three complementary experiments**, because each teaches a different failure mode:

1. **Hurricanes:** *reasonable model choices can reverse a famous result.*
2. **NHANES foods:** *a large hidden search space can manufacture attractive headlines.*
3. **Airbnb crime:** *spatial/temporal choices can create a persuasive causal story from observational geography.*

Then apply the same machinery to a **nuclear/placebo-location** analysis. PM2.5/COVID and Many Analysts are controls/calibration cases that keep the project from becoming an exercise in automatically debunking every observational result.

## Analysis protocol to preregister before touching each result

Use the same pattern for every case:

1. **Reproduce** the paper's headline estimate as closely as possible.
2. **List defensible choices before running alternatives**: sample exclusions, exposure coding, outcome definition, lag/window, covariates, model family, spatial/cluster handling.
3. **Enumerate the multiverse** rather than changing one thing until the answer moves.
4. Add **negative controls/placebos**: shuffled labels, leads, irrelevant outcomes/exposures, random/matched locations where scientifically appropriate.
5. Show effect sizes and uncertainty for **all** specifications; do not reduce the result to a count of p<0.05.
6. Use **joint inference** (permutation/max-statistic, FDR, or the specification-curve procedure) for the family actually searched.
7. State what would falsify the skeptical hypothesis too: a result that is directionally stable, sizable and extreme relative to placebos should count *for* robustness.

This follows the logic of Steegen et al.'s multiverse analysis and Simonsohn, Simmons & Nelson's specification-curve analysis. The latter explicitly demonstrates the method on the hurricane-name claim and makes its data/code public.

## Core methodology references

- Steegen et al. (2016), **Increasing Transparency Through a Multiverse Analysis** — https://doi.org/10.1177/1745691616658637
- Simonsohn, Simmons & Nelson (2020), **Specification Curve Analysis** — https://doi.org/10.1038/s41562-020-0912-z
- Silberzahn et al. (2018), **Many Analysts, One Data Set** — https://doi.org/10.1177/2515245917747646
