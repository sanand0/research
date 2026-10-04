# NHANES 2005–2006 mortality headline-factory pilot

Date: 2026-10-03

## Result in one sentence

A deliberately frozen screen of 15 ordinary NHANES exposures produced six FDR-significant mortality "headlines" after demographic adjustment—four ways of being physically active, low TV time, and weekly religious attendance—but none survived FDR after adding baseline self-rated health on the same complete-case sample.

That is a useful result for this project: the data do not make every random variable significant. They make a coherent family of "active / engaged / healthy enough to do things" variables look protective, which is exactly how many plausible causal stories can grow from one underlying health/frailty structure.

## Design frozen before seeing mortality results

The primary screen was fixed before the mortality file was successfully obtained:

- Population: NHANES 2005–2006 participants age 40+.
- Outcome: all-cause mortality in the 2019 public-use linked mortality file.
- Follow-up: through December 31, 2019.
- Primary adjustment: age, sex, race/ethnicity, education, family income-to-poverty ratio, marital status.
- Survey handling: NHANES interview weights plus cluster-robust standard errors by masked variance PSU within stratum.
- Multiplicity: Benjamini–Hochberg FDR across the 15 prespecified exposures.
- Principle: vary what the hypothetical paper is "about", not the model, in the primary screen.

The 15 exposures were declared before mortality analysis:

1. hours of sleep;
2. walked/bicycled for transportation;
3. moderate home/yard work;
4. vigorous leisure activity;
5. moderate leisure activity;
6. muscle-strengthening activity;
7. TV/video >=3 hours/day;
8. computer >=2 hours/day;
9. emotional support;
10. financial support;
11. number of close friends;
12. religious services >=weekly;
13. >=12 alcoholic drinks in a year;
14. teeth rated good/very good/excellent;
15. no mouth/tooth aching in the past year.

The exact registry and transformations live in nhanes_pilot.py.

## Primary result: six publishable-sounding headlines from one frozen screen

| Exposure | HR | 95% CI | p | BH q |
|---|---:|---:|---:|---:|
| Moderate activity | 0.732 | 0.635–0.843 | 0.000015 | 0.00022 |
| Walked/bicycled for transport | 0.735 | 0.628–0.861 | 0.00013 | 0.00098 |
| Moderate home/yard work | 0.734 | 0.618–0.871 | 0.00041 | 0.00172 |
| Vigorous activity | 0.664 | 0.528–0.835 | 0.00046 | 0.00172 |
| TV/video >=3 h/day | 1.430 | 1.146–1.783 | 0.00152 | 0.00456 |
| Religious services >=weekly | 0.753 | 0.624–0.910 | 0.00329 | 0.00822 |

All six survive FDR at 5%.

Possible newspaper versions from the exact same cohort/model include:

- "Moderate exercise cuts death risk 27%."
- "Walking or biking for errands cuts death risk 27%."
- "Yard work cuts death risk 27%."
- "Vigorous exercise cuts death risk 34%."
- "Three hours of TV raises death risk 43%."
- "Weekly religious services cut death risk 25%."

Those are associations, not causal estimates. The provocative point is that an analyst choosing only one exposure to study could write six different simple headlines from the same underlying cohort.

The other nine prespecified exposures did not pass FDR. In particular, hours of sleep treated linearly was null (HR 1.04 per SD, q=0.57), which is useful discipline: the screen is not simply generating significance everywhere.

## Smoking sensitivity

Adding smoking status leaves the same six primary headlines FDR-significant:

- moderate activity HR 0.764, q=0.0029;
- walking/biking HR 0.747, q=0.0031;
- home/yard work HR 0.744, q=0.0042;
- >=3 h TV HR 1.413, q=0.0084;
- vigorous activity HR 0.717, q=0.0169;
- weekly religious attendance HR 0.789, q=0.0441.

So cigarette smoking alone does not explain the headline factory.

## Same-sample baseline-health sensitivity

Self-rated health is collected in the MEC, so adding it changes both the eligible sample and the correct weight. To distinguish covariate adjustment from sample selection, three models were therefore run on the identical complete-case MEC sample with the same MEC weights:

| Model on identical sample | Nominal p<.05 | BH q<.05 |
|---|---:|---:|
| Demographics only | 6/15 | 5/15 |
| + smoking | 5/15 | 4/15 |
| + smoking + self-rated health | 3/15 | **0/15** |

For the strongest associations, adding self-rated health moves every hazard ratio toward 1:

| Exposure | HR after smoking | HR after + self-rated health | Approx. attenuation of |log(HR)| |
|---|---:|---:|---:|
| Moderate activity | 0.757 | 0.796 | 18% |
| TV/video >=3 h/day | 1.468 | 1.394 | 14% |
| Walking/biking | 0.775 | 0.802 | 14% |
| Home/yard work | 0.770 | 0.826 | 27% |
| Vigorous activity | 0.735 | 0.829 | 39% |
| Weekly religious services | 0.816 | 0.855 | 23% |

After health adjustment, TV (p=.0068), moderate activity (p=.0099), and walking/biking (p=.0134) remain nominally significant, but all three have BH q≈0.067 across the prespecified 15-test family.

## What this does—and does not—show

### It does show: headline specificity is weak

The interesting result is not "we found false positives." The significant results are too coherent for that description. Instead, several ordinary behaviors are strong proxies for a broader latent state: mobility, baseline health, frailty, socioeconomic opportunity, or being able to participate in everyday life.

A paper centered on one of these variables can therefore produce a clean, intuitive causal-sounding narrative even when neighboring variables support equally clean narratives.

This is closer to the user's original concern than classical multiple-testing alone:

> Why this exposure? Why this story? How many equally plausible stories were available in the same data?

### It does not show that physical activity is not causal

There is strong external evidence that physical activity affects health. Also, self-rated health may partly lie on a causal pathway from past activity to later mortality, so conditioning on it can be over-adjustment. The disappearance of FDR significance after health adjustment is evidence of sensitivity/common structure, not proof that the activity effects are spurious.

Likewise, the religious-attendance association may reflect health selection, social connection, socioeconomic factors, causal effects, or several at once. This pilot cannot identify the mechanism.

### It does not exactly reproduce the published sleep paper

The screen deliberately treats sleep as one standardized continuous exposure. Published NHANES sleep-mortality papers use nonlinear categories (for example <=5, 6, 7, 8, >=9 hours) and multiple cycles. Our linear sleep screen is null.

Do not change the primary sleep coding after seeing that null result. A published-specification sleep reproduction should be a separate, declared analysis. Otherwise this project would demonstrate the behavior it is criticizing.

## Survey-statistics limitation

The pilot uses NHANES weights and cluster-robust standard errors, but lifelines does not implement the full NHANES stratified Taylor-linearized survey Cox estimator. Point estimates are useful for screening; exact p-values/intervals should be reproduced in R's survey package before publication.

The finding that several effects attenuate toward 1 under identical-sample health adjustment depends mainly on point estimates and is less sensitive to this variance-estimation limitation.

## Data provenance

Questionnaire XPT files came directly from official CDC NHANES URLs.

As an independent spot-check:

- DEMO_D.xpt SHA-256: bf9cc79cce501b2fbe5aa8d5b403b618548d02d4aefeb528335cdd9f4c40a3af
- PAQ_D.xpt SHA-256: a2c21b90a964aaa08a854d66526b29a1a7ad009d8a26c3cc9a8c18bf70f0c0aa

Both match the reproducibility manifest in profdrheld-eng/nhanes-activity-contrast.

The local environment could not reach CDC's ftp.cdc.gov mortality endpoint. Instead:

1. The same public mortality file was obtained from ehsanx/Reproducible-NHANES-Analysis on GitHub.
2. GitHub had normalized CRLF to LF, producing 496,426 bytes across 10,348 lines.
3. The Git blob hash locally matched GitHub: cb1ac585d9703698c8912927f12a530ef10e0381.
4. Restoring one CR byte per line produced the official 506,774-byte file.
5. Its SHA-256 became:
   69388ea13a4f395f29d9d21bc51941b9759003490d4b00f6ff12a1bc5f8dba5c
6. That exactly matches the independently published CDC-source manifest in profdrheld-eng/nhanes-activity-contrast.

So the analyzed mortality bytes are cryptographically identical to the official CDC file despite the FTP connectivity problem.

CDC notes that in the 2019 public-use mortality files vital status is unchanged, while follow-up time and cause of death are replaced by synthetic values for some records to reduce disclosure risk.

## Reproduce

Questionnaire files and mortality data stay under ignored data/.

Commands:

    uv run nhanes_pilot.py download --skip-mortality
    uv run nhanes_pilot.py inventory
    uv run nhanes_pilot.py analyze
    uv run --no-project --with pandas --with lifelines -- python -m unittest -v test_nhanes_pilot.py

Results are written to results/nhanes_2005_2006_headline_factory.csv.

## Recommendation after the pilot

This changes the priority slightly.

**Keep NHANES as the main platform, but do not scan hundreds of arbitrary variables next.** The 15-variable pilot already shows that a coherent latent factor can generate multiple stories. A giant unrestricted variable scan would make the critique easier to dismiss as intentionally fishing.

The strongest next experiment is a matched exposure family:

1. **NHANES III food-frequency questionnaire:** run one fixed mortality model over all 81 food-frequency items. This is the cleanest test of "why chili rather than one of the other 80 foods?"
2. **HRS/CAMS activities:** independently run the book-reading model over the roughly 31 side-by-side everyday activities. This tests "why books rather than gardening, pets, affection, puzzles, volunteering, concerts, etc.?"
3. Only after those two exposure-selection experiments, add specification curves within the published winners.

The key reusable artifact should therefore be an exposure-registry-driven mortality runner: one cohort/model/outcome, many declared comparable exposures, one long result table. nhanes_pilot.py is the first minimal version of that runner.
