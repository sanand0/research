# Analysis Plan 002 — Behavioral predictability → survival

Frozen companion to `hypothesis-002.md`.

## Inputs

Predictor-only source:
- `candidates/replication-alberta-2018/p3hz4_predictors.csv`
- SHA256 `f31426bdebfc873cc896879236551b634e0ad0429cef6e17f51a431de0f74924`

Pre-outcome phenotype artifacts:
- `analysis/h002_predictability_preoutcome.py`
- `analysis/h002_predictability_preoutcome.json`
- `analysis/h002_predictability_scores.csv`
- `analysis/h002_predictability_draws.npz`

Outcome file to be created only after this plan is committed:
- `candidates/replication-alberta-2018/p3hz4_survival.csv`
- permitted columns: `ID,survival2` only.

## Outcome extraction rule

After freeze, obtain the public p3hz4 source dataset and extract only:

- `ID`;
- `survival2 = 1 if survival > 0 else 0` exactly as in the authors' R code.

Do not inspect cross-tabs, counts, plots, or associations while extracting. Save the two-column file and hash it before running H002.

## Multiple-imputation propagation

Use 1,000 posterior draws selected reproducibly from `h002_predictability_draws.npz` with seed 20260908. For each draw and eligibility threshold:

- z-score `bird_log_sigma` among eligible birds;
- z-score `bird_mean` among eligible birds;
- take sex from the sealed predictor-only file (one unique value per bird);
- fit binomial GLM.

Combine coefficient uncertainty using Rubin-style total variance. Any failed GLM is counted and reported. If >5% of the 1,000 fits fail or separate, mark the result technically unstable and do not substitute a different estimator without labeling it post-hoc.

## Stability labels

- STABLE: primary conclusion is unchanged for >=6 and >=8 observation thresholds.
- SENSITIVE: interval/magnitude changes materially but all thresholds give the same support/not-support decision.
- FLIPS: support decision changes across thresholds; report H002 as specification-sensitive.

## Explicit non-goals

- no treatment-specific fishing;
- no survival-based phenotype selection;
- no replacing predictability with visual-slope or temperature-slope plasticity (both failed pre-outcome reliability gates);
- no claim that non-redetection is biological death beyond the source study's own interpretation.
