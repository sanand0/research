# Analysis plan 005 — Red-kite early range contraction

1. Use the frozen `analysis/red_kite_h005_features.csv` only for predictors.
2. Load the public NestTool `input_data_prepared.rds` **after the freeze** and extract only `year_id` + `success` from `summary`.
3. Join one-to-one on `year_id`; require every frozen eligible season to have an allowed success label (`yes`/`no` or numeric 1/0). Do not drop or redefine rows after outcome access.
4. Map `yes`/1 → 1 and `no`/0 → 0.
5. Standardize contraction, current range, and age on the frozen eligible cohort.
6. Fit the primary exchangeable-correlation binomial GEE clustered by bird ID with year and sex fixed effects.
7. Fit only the prespecified MCP99 sensitivity.
8. Write coefficients, robust SEs, ORs, 95% CIs, p-values, N, birds, outcome counts, and decision/stability labels to `results/h005_success.json`.
9. Re-run once and verify the result file hash is identical.

Implementation errors may be corrected only if they preserve the frozen estimand, cohort, predictor definitions, covariates, and sensitivity. Any such correction must be recorded before rerunning.
