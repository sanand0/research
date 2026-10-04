# HRS/CAMS activity headline factory

Date: 2026-10-03

## Result in one sentence

The published finding that **book readers live longer** reproduces closely in effect size, but books are only one of many everyday activities in the same questionnaire that support an equally simple mortality headline.

With one frozen paper-like Cox model applied to 31 side-by-side CAMS activities:

- 28 activities had enough people in both "none" and "any" groups to estimate.
- 20/28 were nominally significant.
- **18/31 survive BH/FDR at 5%**, conservatively counting the three sparse non-estimable activities as p=1 in the original 31-activity family.
- Books rank **11th of 28 modelable activities by p-value**.
- Books: HR **0.816**, 95% CI 0.709–0.939, p=.0044, q=.0125.
- House cleaning, meal preparation, shopping/errands, religious attendance, meetings, helping others, listening to music, gardening, walking and praying/meditating all produce stronger associations.

The common-sample sensitivity says nearly the same thing: 16/31 survive FDR and books rank 12th.

This independently reproduces the NHANES "headline factory" phenomenon using a different cohort, measurement domain, and focal published claim.

## Published claim

Bavishi, Slade & Levy (2016), "A Chapter a Day – Association of Book Reading with Longevity", analyzed the U.S. Health and Retirement Study / 2001 Consumption and Activities Mail Survey (CAMS).

They reported:

- final N = 3,635;
- 34,496 person-years;
- 27.4% mortality through December 31, 2012;
- 59% read books;
- adjusted any-books vs no-books HR = **0.80**;
- book tertiles HR = **0.83** for 0.01–3.49 hours/week and **0.77** for >=3.5 hours/week;
- periodicals were less protective.

Paper:
https://pmc.ncbi.nlm.nih.gov/articles/PMC5105607/

The paper adjusted for age, sex, race, education, seven comorbidities, self-rated health, visual acuity, wealth, marital status, job status, and depression.

## Why CAMS is an unusually fair counterexample factory

The same 2001 questionnaire asks hours spent on 31 named weekly/monthly activities:

TV; newspapers/magazines; books; music; sleep; walking; sports/exercise; visits; phone/letters/email; paid work; computers; prayer/meditation; house cleaning; laundry/mending; gardening; shopping/errands; meal prep; grooming; pet care; showing affection; helping; volunteering; religious attendance; meetings; money management; self-care; cards/games/puzzles; concerts/movies/lectures; singing/playing music; arts/crafts; and home improvements.

The frozen family is in hrs-cams-activity-registry.csv.

The central counterfactual is:

> If the investigators had chosen gardening, house cleaning, listening to music, showing affection, or volunteering rather than books as the focal behavior, what mortality story would the same survey have supported?

## Frozen primary design

The exposure family and coding were fixed before looking at activity-mortality associations.

### Exposure

For every A1–A31 activity:

- any reported time vs zero time;
- identical coding for all activities;
- directly mirrors the paper's later any-book vs no-book analysis.

Three activities are nearly universal and have fewer than 100 nonparticipants: TV, sleep/nap, and personal grooming. Those contrasts are declared non-estimable by rule and remain in the 31-hypothesis BH family as p=1.

### Outcome and weights

- National Death Index-specific death date from RAND HRS;
- follow-up censored December 31, 2012, matching the paper;
- common baseline date September 1, 2001;
- HRS 2000 respondent weight.

This weight choice reproduces the paper's weighted sample composition closely:

| Quantity | Paper | Reconstruction |
|---|---:|---:|
| Female | 62.1% | ~62.6% |
| Any book reading | 59% | ~59.5% |
| Weighted mortality through 2012 | 27.4% | ~27.6% |

### Covariates

Available paper covariates are age, sex, race, years of education, self-rated health, continuous wealth, married vs not, employed vs not, depression, cancer, lung disease, heart disease, stroke, arthritis, diabetes, and hypertension.

**Visual acuity is the one published covariate unavailable in the RAND HRS 2000–2014 v2 mirror used for this provisional reconstruction.**

Primary sample: exposure-specific complete cases.

Sensitivity sample: one common 2,805-person sample complete on all 31 activities and paper-like covariates.

## Near-replication of the book result

Despite the missing eyesight covariate and slightly different final cohort, the main book effect is remarkably close.

| Analysis | Published | Reconstruction |
|---|---:|---:|
| Unadjusted any books vs none | HR ~0.76 | **0.760** |
| Adjusted any books vs none | HR 0.80 | **0.816** |
| 0.01–3.49 h/week vs 0 | HR 0.83 | **0.866** |
| >=3.5 h/week vs 0 | HR 0.77 | **0.779** |

The primary adjusted book model has N=3,584, 1,079 deaths, HR=0.816, 95% CI 0.709–0.939, p=.0044.

The paper reports N=3,635 and p<.0001. Because the cohort is not exact, eyesight is missing, and our weighted model uses robust variance, this is a **near-replication**, not an exact reproduction.

## Headline factory result

### Paper-like covariates, exposure-specific samples

| Activity: any vs none | HR | 95% CI | BH q |
|---|---:|---:|---:|
| House cleaning | **0.572** | 0.490–0.667 | <1e-9 |
| Meal prep/clean-up | **0.595** | 0.501–0.706 | <1e-7 |
| Shop/run errands | **0.631** | 0.522–0.762 | 0.00002 |
| Religious attendance | 0.723 | 0.624–0.837 | 0.00011 |
| Attend meetings | 0.715 | 0.612–0.836 | 0.00015 |
| Help others | 0.752 | 0.655–0.862 | 0.00023 |
| Listen to music | 0.749 | 0.643–0.873 | 0.00096 |
| Yard work/garden | 0.789 | 0.684–0.910 | 0.00436 |
| Walk | 0.772 | 0.653–0.913 | 0.00885 |
| Pray/meditate | 0.759 | 0.633–0.912 | 0.00979 |
| **Read books** | **0.816** | 0.709–0.939 | **0.01253** |
| Volunteer work | 0.798 | 0.681–0.935 | 0.01345 |
| Wash/iron/mend | 0.785 | 0.654–0.942 | 0.02205 |
| Sing/play music | 0.779 | 0.635–0.955 | 0.03538 |
| Work for pay | 0.724 | 0.554–0.945 | 0.03538 |
| Show affection | 0.831 | 0.712–0.969 | 0.03538 |
| Money management | 0.815 | 0.685–0.968 | 0.03634 |
| Sports/exercise | 0.840 | 0.723–0.977 | 0.04005 |

All q-values use the full frozen 31-activity family, with sparse contrasts assigned p=1.

Possible single-exposure headlines include:

- "House cleaning is associated with 43% lower mortality."
- "Cooking is associated with 41% lower mortality."
- "Running errands is associated with 37% lower mortality."
- "Listening to music is associated with 25% lower mortality."
- "Gardening is associated with 21% lower mortality."
- "Prayer and meditation are associated with 24% lower mortality."
- "Helping others is associated with 25% lower mortality."
- "Singing or playing music is associated with 22% lower mortality."
- "Showing affection is associated with 17% lower mortality."
- "Reading books is associated with 18% lower mortality."

These are associations, not causal estimates. That is the point.

## Common-sample sensitivity

On the identical 2,805-person sample complete for every activity and covariate:

- 28 estimable contrasts;
- 19 nominal p<.05;
- **16/31 survive FDR**;
- books rank **12th** by p-value;
- book HR = **0.778**, q=.0074;
- 14 of the primary 18 FDR-significant activities also survive.

The broad conclusion is not a missing-data artifact.

## Post-hoc functional-limitation sensitivity

The obvious alternative explanation is that people healthy enough to clean, shop, cook, garden, visit others, volunteer and read are also healthy enough to live longer.

A post-hoc sensitivity therefore adds baseline:

- ADL limitations;
- IADL limitations;
- mobility limitations.

The headline factory remains:

| Model | Exposure-specific FDR hits | Common-sample FDR hits |
|---|---:|---:|
| Paper-like covariates | 18/31 | 16/31 |
| + ADL/IADL/mobility | **17/31** | **18/31** |

Examples:

- books: 0.816 → **0.821**;
- house cleaning: 0.572 → **0.584**;
- meal prep: 0.595 → **0.601**;
- shopping/errands: 0.631 → **0.626**;
- listening to music: 0.749 → **0.745**.

Only sports/exercise drops out of FDR significance in the exposure-specific functional model.

Simple baseline functional limitations therefore do not explain the multiplicity away. That does not establish causality; many unmeasured/common causes remain.

## What this demonstrates

This is not mainly a classical false-positive example. Eighteen activity associations survive a conservative family-wide FDR correction. Books remain one of them.

The stronger lesson is:

> **A statistically robust observational association does not tell us why that variable deserved to become the headline.**

The same dataset supports narratives about cognitive engagement, physical activity, social engagement, altruism, spirituality, music, independence, domestic activity, and affection.

Many may contain genuine causal components. A p-value—even an FDR-corrected one—does not select among these stories.

The hidden researcher degree of freedom is not only "which model?" It is **"which exposure became the paper?"**

## Why this complements NHANES

The two executed studies tell the same story in different domains.

### NHANES III foods

- 60 named foods;
- 21 FDR-significant;
- hot chili rank 28;
- cake, pizza, wine, chocolate, other peppers, etc. can generate stronger mortality associations.

### HRS/CAMS activities

- 31 everyday activities;
- 18 FDR-significant in the primary analysis;
- books rank 11 among 28 estimable;
- cleaning, cooking, errands, music, gardening, prayer, volunteering, affection, etc. can generate stronger mortality associations.

This cross-dataset replication is harder to dismiss as a peculiarity of nutritional epidemiology.

## Data provenance and licensing caveat

HRS's official 2001 CAMS product page reports **N=3,866**, exactly matching the CAMS file used in this exploratory run.

The raw CAMS/RAND files for this exploratory run came from a public research repository. Their local Git object hashes exactly matched the blobs advertised by that repository:

- CAMS01_R.dta: ebd182f03400ab47fb3dda703b141be0ab7890c2
- RAND HRS 2000–2014 v2 ZIP: ea293e1cf09519c614e3bff4102a3d50f93e1fda

However, **HRS's current Conditions of Use require user registration and restrict third-party redistribution of public-release files.**

Therefore:

- raw HRS files are not committed;
- the mirror is not a canonical redistribution route;
- before publishing/presenting this as a formal replication, rerun using files downloaded under the researcher's own HRS registration from the official HRS site;
- share only scripts, the activity registry, and aggregate statistical results.

Official CAMS product:
https://hrsdata.isr.umich.edu/data-products/2001-consumption-and-activities-mail-survey-cams

HRS Conditions of Use:
https://hrs.isr.umich.edu/data-products/access-to-public-data/conditions-of-use

## Reproduce after official HRS download

Place the official HRS public-use inputs under data/hrs/:

- CAMS01_R.dta
- randhrs2000_2014v2.dta, or the equivalent archived RAND HRS 2000–2014 v2 file

Then run:

    uv run hrs_cams_scan.py

Tests:

    uv run --no-project --with pandas --with lifelines --with pyreadstat -- python -m unittest -v test_hrs_cams_scan.py

Outputs:

- hrs-cams-activity-registry.csv
- results/hrs_cams_activity_headline_factory.csv

Raw HRS data are intentionally not committed. The exploratory mirror copies used for this run were deleted after provenance/hash verification; place registered official HRS files under ignored `data/hrs/` to rerun.

## Recommendation

**Keep NHANES foods as the most vivid flagship visual, and use HRS/CAMS as the decisive independent replication.**

A two-panel story is stronger than either alone:

1. "Hot chili helps you live longer." Reveal cake, pizza, wine, chocolate, other peppers, and many other FDR-significant foods.
2. "Reading books helps you live longer." Reveal cleaning, cooking, errands, music, gardening, prayer, volunteering, affection, etc.

Then make the conceptual point:

> **Maybe the association is real. The hidden choice is which real association we chose to explain.**

That is more defensible—and more interesting—than accusing either paper of deliberate p-hacking.
