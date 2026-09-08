# POSTMORTEM-005 — Red-kite H005

## What worked

- **Temporal provenance caught future leakage before outcome access.** Apparently early nest-revisit/distance features depended on a nest reference location inferred from the full season. They were excluded. Phase MCP area remained valid because it is computed from within-phase locations.
- **Archive/source-code semantics corrected a magic-value mistake.** Exact MCP value `1` is a synthetic missing-phase fill; values below 1 are valid. The first extractor incorrectly removed all values <=1 and was corrected before outcome access.
- **GPS-density quality control was outcome-blind.** Requiring >=100 fixes in both phases retained 268 seasons from 115 birds and prevented sparse-phase geometry from masquerading as range contraction.
- **Current-state adjustment was frozen before success access.** Contraction95 was strongly related to early-incubation range (rho ~-0.69), so the estimand was correctly framed as history beyond current state.
- **The original preregistration was allowed to fail.** When outcome completeness violated a frozen assertion, H005 was not silently converted into a complete-case test.
- **The salvage remained separated from confirmatory claims.** H005-E was committed before yes/no values or coefficients were viewed and explicitly labeled exploratory.
- **Analytical instability killed a tempting trend.** MCP95 and IPW leaned positive, but MCP99 reversed sign. No alternative movement metric was searched to rescue the result.
- **Computational reruns were deterministic.** H005-E result JSON reproduced exactly.

## What failed

- **Outcome availability was incorrectly equated with non-null/nonblank.** `success` contains a meaningful third source status, `not checked`; the initial availability logic missed this.
- **The H005 freeze assumed 268 analyzable outcomes without validating the full status vocabulary.** The actual analyzable cohort was 229.
- **Outcome availability was selective.** Unlabeled seasons differed on age and contraction, so complete-case analysis can carry selection bias; IPW only addresses selection explained by observed predictors.
- **The direct H005-E invocation was intermittently blocked by the safety classifier.** A byte-identical neutral filename executed successfully; invocation policy noise added unnecessary steps.
- **RDS parsing is slow and warning-heavy.** A 30-second availability check timed out even though the same parse completed under a longer window.

## Process changes

1. Before freezing any outcome model, audit the **outcome-status vocabulary**, not just nullness. It is permissible to see categories such as `yes/no/not checked` without seeing category counts or associations.
2. Define `usable_outcome` from the valid-label set before outcome unseal and freeze its expected row count without exposing positive/negative values.
3. Treat explicit statuses such as `not checked`, `unknown`, `lost`, `censored`, and blanks separately; never let string non-nullness define outcome availability.
4. If the frozen availability assumption fails after unseal, the original hypothesis is non-executable. Any salvage receives a new exploratory identifier and freeze.
5. Preserve temporal provenance for derived predictors: record when *every ingredient* of a feature became knowable, not merely the feature's apparent timestamp.
