# Analysis plan 006 — Duckweed early reproduction vs remaining lifespan

1. Obtain the public source CSVs for Experiment 2 and Experiment 1 only **after this plan is committed**.
2. Parse dates and daily offspring columns using the source README/code conventions.
3. Experiment 2: retain only `exclude == "No"`; normalize treatment labels to `1` and `1/4`.
4. Experiment 1 replication: retain only `L01`, `L02`, `L04`, `L08`, `L16`; exclude `L32` and `L00` because of source-study censoring at experiment termination.
5. For each landmark, calculate reproductive lifespan as `date.last.repro - date.birth + 1`; require lifespan >= landmark+1.
6. Sum detached daughters over age days 1..landmark inclusive. Values before birth are not observations and must not be included.
7. Standardize the early count within treatment using the landmark-eligible sample. Fail if any treatment has zero predictor variance.
8. Fit a Cox PH model with early standardized output as the only covariate and light treatment as strata. All retained subjects are treated as observed events.
9. Primary Experiment-2 landmark = day 7. Prespecified stability = day 5.
10. Independently run Experiment-1 day-7 replication regardless of Experiment-2 result.
11. After unseal, reproduce the published Experiment-2 direction of the light-treatment lifespan difference as a parsing/known-signal validation.
12. Record N, treatment counts, early-count distribution, HR, coefficient, SE, 95% CI, p-value, convergence, and support/stability/replication labels in `results/h006_duckweed.json`.
13. Run Cox proportional-hazard diagnostics for the early-output coefficient. Diagnostics may qualify interpretation but may not trigger selection of a different primary model. A gross PH violation is reported as a limitation.
14. Execute the complete analysis twice from the same source files and verify identical result-file hashes.

Implementation fixes after unseal are permitted only if they preserve the frozen populations, landmarks, predictors, outcome, model family, and decision rules; they must be documented before rerunning.
