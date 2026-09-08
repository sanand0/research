# H006 — Early reproduction and subsequent lifespan in clonal duckweed

## Frozen question

Among *Lemna minor* fronds that remain reproductively alive through a fixed early-life landmark, is greater early clonal reproduction associated with a shorter **remaining** reproductive lifespan within the same light treatment?

## Biological prediction

Primary directional prediction: a trade-off / pace-of-life mechanism predicts that greater early reproductive output is associated with a higher subsequent reproductive-death hazard (HR > 1).

A plausible competing explanation is persistent individual vigour/resource acquisition, which could instead produce HR < 1. Therefore inferential decisions use a **two-sided 95% CI**; direction is frozen before outcome access but evidence in the opposite direction counts as contradiction rather than being ignored.

This is an observational individual-level association within randomized light treatment, not a causal estimate of reproduction itself.

## Discovery population — Experiment 2

- Source rows with `exclude == "No"` only (source-paper analytic inclusion).
- Two light treatments: full light and 1/4 light.
- Fixed **day-7 landmark**, where birth day is age day 1.
- Eligible only if reproductive lifespan is at least 8 days, so every included frond remains at risk after the entire predictor window.
- The eligibility rule is frozen before inspecting its resulting N.

## Primary predictor

`early_offspring_7`: total daughters detached during age days 1–7 inclusive.

Standardize this predictor **within light treatment** among landmark-eligible plants. The primary estimand is the hazard ratio per 1 treatment-specific SD greater early reproduction.

## Primary outcome

`remaining_lifespan_7 = reproductive_lifespan - 7`, in days from the day-7 landmark to last reproduction/reproductive death.

All Experiment-2 analytic subjects have observed reproductive-death events according to the source study.

## Primary model

Cox proportional-hazards model stratified by light treatment:

`remaining_lifespan_7 ~ z_within_treatment(early_offspring_7)`, strata = light treatment.

Every individual contributes one independent event; no repeated-subject clustering is required.

## Primary decision

- **SUPPORTED (trade-off):** two-sided 95% CI entirely above HR=1.
- **CONTRADICTED:** two-sided 95% CI entirely below HR=1.
- **NOT SUPPORTED / INCONCLUSIVE:** CI includes HR=1.

## Prespecified analytical stability fork

Repeat the discovery analysis using a fixed **day-5 landmark**:

- eligibility: reproductive lifespan >= 6 days;
- predictor: daughters detached during age days 1–5;
- outcome: reproductive lifespan - 5;
- same within-treatment standardization and stratified Cox model.

Stability:

- **STABLE:** day-5 coefficient has the same sign and same support/contradiction/not-supported class as day 7.
- **SENSITIVE:** sign or decision class changes.

No alternative landmark will be selected after outcome access as part of H006.

## Independent replication — Experiment 1

Run the day-7 model regardless of the Experiment-2 result, using only source-paper formal-analysis treatments:

`1`, `1/2`, `1/4`, `1/8`, `1/16`.

Exclude `1/32` and `0` light because the source experiment ended with censored surviving fronds in those extreme treatments.

Use the same day-7 eligibility, within-treatment standardization, remaining-lifespan definition, and Cox model stratified by light treatment.

Replication labels:

- **STRONG DIRECTIONAL REPLICATION:** coefficient has the same sign as Experiment 2 and its 95% CI excludes HR=1 in that direction.
- **DIRECTIONALLY CONSISTENT:** same sign but CI includes 1.
- **CONTRADICTORY:** CI excludes 1 in the opposite direction.
- Otherwise **INCONCLUSIVE**.

A positive discovery is not treated as credible without at least directional consistency in Experiment 1.

## Known-signal validation after unseal

Before trusting parsed outcomes, reproduce the source-paper aggregate light effect on Experiment-2 lifespan: lower light (1/4) has longer mean log10 reproductive lifespan than full light. This validation is not part of the H006 support criterion.

## Outcome seal

Before this freeze, no aggregate Experiment-2 early-reproduction/lifespan association, fitted coefficient, hazard ratio, or outcome distribution was inspected. One Dryad browser preview accidentally exposed one example row and its last-reproduction date; it is excluded from specification decisions and recorded as a minor seal imperfection.

## No-rescue rule

After H006 outcome access, do not search alternative early windows, early reproduction shapes, offspring-attached-at-death, morphology, positions, subgroups, or treatment interactions against these lifespan outcomes to rescue a null/sensitive result. New questions require a fresh outcome or explicit exploratory label.
