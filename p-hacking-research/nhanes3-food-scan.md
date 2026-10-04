# NHANES III food headline factory

Date: 2026-10-03

## Why this is the strongest example so far

The published 2017 PLOS ONE paper reported that eating hot red chili peppers was associated with lower all-cause mortality in NHANES III. The paper described an 81-item food-frequency questionnaire and classified chili consumers as anyone reporting more than zero hot-red-chili servings/times per month.

The public NHANES III adult file exposes 60 predefined named food/beverage fields with the same "times per month" structure, plus six free-text "other food" slots and additional non-frequency/check-item fields. For the counterexample experiment, the clean family is therefore the 60 predefined named monthly-frequency exposures. Free-text slots are excluded.

This gives a direct exposure-selection test:

> If hot red chili had never been chosen as the paper topic, how many of the other named foods could have supported an equally simple "X is associated with living longer" headline?

## Frozen primary analysis

Before looking at the mortality results for the 60-food family:

- Exposure family: all 60 predefined named monthly food/beverage frequency fields.
- Exposure coding: any consumption (>0 times/month) versus none, matching the chili paper's primary predictor coding.
- Outcome: all-cause mortality.
- Population: NHANES III adults age 18+.
- Mortality linkage: the current official 2019 public-use linked mortality file from CDC Stacks.
- Adjustment: age, sex, race, ethnicity, education, marital status, annual income below $20,000, and current employment. This matches the demographic/socioeconomic logic of the chili paper's Model 2.
- NHANES interview weights are used; standard errors are cluster-robust by pseudo-PSU within pseudo-stratum.
- Multiplicity: Benjamini-Hochberg FDR across the complete 60-food family.
- Every food uses the same model and coding. No food-specific model tuning is allowed.

The exact frozen exposure registry is nhanes3-food-registry.csv.

## Result

All 60 named foods had at least 100 consumers and 100 nonconsumers and could be modeled.

- 24/60 foods had nominal p < .05.
- 21/60 survived BH/FDR q < .05.
- 20 of those 21 were associated with lower mortality.
- 1 (liver/other organ meats) was associated with higher mortality.
- Hot red chili was only rank 28 of 60 by p-value.
- Hot red chili: HR 0.921, p = .0798, q = .171 in the current 2019 linkage.

### Some headlines available from exactly the same analysis

| Food consumed at least monthly | HR | BH q | Possible naive headline |
|---|---:|---:|---|
| Cakes, cookies, brownies | 0.773 | <1e-8 | "Eating cake is linked to 23% lower mortality" |
| Wine | 0.776 | <1e-6 | "Wine drinkers live longer" |
| Yogurt/frozen yogurt | 0.839 | <0.00001 | "Yogurt is linked to longer life" |
| Any other fruit | 0.739 | <0.0001 | "Fruit eaters live longer" |
| Rice | 0.853 | 0.00012 | "Rice is linked to lower mortality" |
| Pizza/calzone/lasagna | 0.884 | 0.0078 | "Pizza eaters live longer" |
| Hard liquor | 0.875 | 0.0093 | "Hard-liquor drinkers live longer" |
| Chocolate candy/fudge | 0.919 | 0.0178 | "Chocolate eaters live longer" |
| Salted snacks | 0.909 | 0.0181 | "Salty-snack eaters live longer" |
| Liver/other organ meats | 1.103 | 0.0178 | "Organ-meat eaters die sooner" |

These are deliberately phrased as the kind of headline a single-exposure observational paper could invite. They are not causal conclusions.

### The chili neighborhood is particularly revealing

Among the 12 predefined vegetable fields:

| Vegetable exposure | HR | p | BH q across all 60 foods |
|---|---:|---:|---:|
| Broccoli | 0.841 | <0.0001 | 0.00012 |
| Carrots | 0.818 | 0.0001 | 0.00047 |
| Other peppers | 0.874 | 0.0005 | 0.0030 |
| Tossed salad | 0.854 | 0.0007 | 0.0036 |
| Tomatoes | 0.862 | 0.0056 | 0.0178 |
| Brussels sprouts/cauliflower | 0.909 | 0.0160 | 0.0457 |
| Other vegetables | 0.834 | 0.0393 | 0.1025 |
| Hot red chili peppers | 0.921 | 0.0798 | 0.171 |
| Spinach/greens | 0.960 | 0.271 | 0.407 |
| Sweet potatoes/yams | 1.010 | 0.786 | 0.813 |
| Cabbage/coleslaw/sauerkraut | 0.992 | 0.845 | 0.859 |
| White potatoes | 1.005 | 0.966 | 0.966 |

So even if we restrict attention to "vegetables a researcher might plausibly single out," hot red chili is not unusual in the current data. Six neighboring vegetable exposures pass the much harsher 60-food FDR correction.

The especially clean counterexample is "other peppers": same broad food family, HR 0.874, q = .003, substantially stronger evidence in this analysis than hot red chili.

## Comparison with the published chili paper

Chopan & Littenberg (2017) analyzed an earlier public mortality linkage through December 31, 2011.

They reported:

- N = 16,179 complete cases.
- Unadjusted chili HR 0.59.
- Model 2 chili HR 0.87 (95% CI 0.78–0.98), p = .020.
- Model 3 chili HR 0.87 (95% CI 0.77–0.97), p = .014.

Their Model 2 added demographic/socioeconomic variables. Model 3 additionally adjusted for personal habits including alcohol, smoking, physical activity, and aggregate fruit/vegetable/meat intake.

Our result is not an exact replication of those coefficients because:

1. We use the current CDC 2019 mortality linkage, which extends follow-up by eight years.
2. CDC states that the 2019 release used an enhanced linkage algorithm and supersedes older releases; a small number of vital-status/cause assignments changed.
3. We do not force every food onto the original paper's 16,179 complete-case sample.
4. Lifelines supplies weighted Cox models with cluster-robust errors, not the full Taylor-linearized NHANES survey Cox estimator used by survey-statistics software.

Therefore the scientifically defensible claim is not "the chili paper is wrong."

It is:

> In the same source cohort, using the current official mortality linkage and one frozen Model-2-style analysis applied to every named food, many other foods support stronger mortality associations than hot red chili. Choosing chili as the sole exposure hides a large and highly productive alternative-headline space.

## Why this is better than a simple p-hacking demonstration

Classical p-hacking suggests many null tests generate a few p < .05 results by chance.

That is not what happened here.

Twenty-one of 60 foods survive FDR, far more than a pure-null multiple-testing story. The associations are structured: many foods and behaviors act as proxies for dietary diversity, health, frailty, income, social patterning, healthcare, and other latent characteristics.

That makes the example more important:

> Multiple-testing correction can protect against random false positives, but it does not protect against choosing one statistically real association and attaching a specific causal story to it.

"Cakes/cookies/brownies -> lower mortality" is probably not evidence that cake prevents death. Yet the association is much stronger statistically than the chili association under this frozen screen.

The failure mode is exposure selection plus causal storytelling, not merely p < .05 fishing.

## Model-3 replication status

An exploratory implementation of the chili paper's fuller lifestyle adjustment was attempted using:

- current smoking;
- current alcohol use;
- physical-activity category reconstructed from the NHANES III MET/frequency fields;
- aggregate fruit, vegetable, and meat frequencies.

Using the examination-file alcohol variable reduces the complete cohort to about 13,100, substantially below the paper's 16,179. In that exploratory version chili is HR about 0.95 and nonsignificant.

Do not use that result yet.

The discrepancy indicates that at least one historical covariate/sample construction detail has not been reproduced exactly. The code retains model2_common/model3 as diagnostics, but only model2 is reported as validated for this project.

A proper exact replication would need to reconcile:

- which NHANES III alcohol field/version the authors used;
- the precise physical-activity implementation;
- their complete-case cohort construction;
- the older mortality-file vintage or a defensible censoring reconstruction through 2011;
- full survey-variance estimation.

## Data availability and reproducibility

This experiment passes the original "easy data" criterion well.

Official source files:
- NHANES III adult household data: direct CDC download.
- NHANES III mortality: direct CDC Stacks ZIP.
- No restricted-use data are required.

Local raw files live under data/ and are ignored by git.

Committed reproducibility artifacts:
- nhanes3-food-registry.csv — frozen 60-food family, variable positions and labels.
- nhanes3_food_scan.py — fixed-width parser and mortality screen.
- test_nhanes3_food_scan.py — unit tests.
- results/nhanes3_food_headline_factory.csv — all 60 Model-2-style results.

Run:

    uv run nhanes3_food_scan.py --workers 12 --model model2

## Recommendation

This should now become the project's flagship example.

It is stronger than the generic "scan NHANES for anything" idea because:

1. The alternative exposure family is naturally defined by the original paper's own questionnaire.
2. Every alternative is understandable to a lay reader.
3. The exposure coding is identical to the paper's chili coding: any vs none.
4. The same cohort, outcome and model are used for every alternative.
5. Counterexamples are vivid: cake, pizza, chocolate, hard liquor and salted snacks.
6. The result survives multiple-testing correction; therefore the lesson cannot be dismissed as "of course some p-values are <.05."
7. Chili itself is not exceptional in the current data, even relative to other vegetables/peppers.

Next, do HRS/CAMS "books vs everyday activities" as an independent replication of the same phenomenon. If that produces the analogous pattern, the combined lesson becomes much harder to dismiss as an NHANES-specific dietary artifact.
