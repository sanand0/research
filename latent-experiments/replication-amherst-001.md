# Replication 001A — Amherst next-winter redetection

**Status: DESIGN FROZEN BEFORE YEAR-2 INDIVIDUAL MEMBERSHIP ACCESS**

Date: 2026-09-08 SGT

## Purpose

Independently test whether winter first-feeding chronotype predicts later re-detection in a different population of black-capped chickadees.

This is a replication of the *relationship*, not an exact replication of the Alberta study. The Amherst study used a different site, feeder layout, field protocol, and outcome opportunity.

## Source

Rothberg, Wolf & Clotfelter (2024), *Social network connections are positively related to temperature in winter flocks of black-capped chickadees*, Animal Behaviour 210:213–224, DOI 10.1016/j.anbehav.2024.02.007.

Dryad: DOI 10.5061/dryad.sj3tx96c2, version 7, published 2024-03-12, CC0.

Public metadata exposes:

- `RFID_data_Yr1.csv` (~15.35 MB)
- `RFID_data_Yr2.csv` (~6.39 MB)
- `Birds_Yr1.csv`
- `Birds_Yr2.csv`
- `README.md`

The article reports 74 unique RFID-detected chickadees in Year 1 (21 Nov 2020–1 Mar 2021), using 10 feeders across two forest tracts. In Year 2, eight feeders were deployed only in the larger tract. Therefore Year-2 absence cannot be called mortality or annual survival.

## Outcome seal

As of this freeze, individual Year-2 bird membership has **not** been inspected.

Specifically, neither `Birds_Yr2.csv` nor `RFID_data_Yr2.csv` has been opened or previewed for individual IDs. File names, sizes, study-level aggregate design facts, and public article summaries are allowed.

Dryad file downloads are currently blocked in this environment by an AWS WAF / human-confirmation page. This barrier will not be bypassed programmatically.

## Research question

Among Year-1 Amherst chickadees with adequate RFID timing data and meaningful Year-2 detection opportunity, is an individual's winter first-feeding chronotype associated with **next-winter RFID re-detection**?

Outcome terminology is deliberately `next-winter redetection`, not survival.

## Primary predictor — portable early chronotype

Use Year-1 RFID only.

For each bird-day:

1. count RFID events;
2. retain bird-days with >=10 events, matching the Hobbs daily eligibility rule;
3. record the first event's local clock time in minutes after midnight.

Fit:

`first_clock_minutes ~ C(date) + (1 | bird)`

The bird random intercept is sign-reversed so +1 = earlier than peers, then standardized among eligible birds.

Why date fixed effects: they absorb all day-common timing shifts — sunrise, daylength, weather, feeder schedule, calendar effects — without requiring Amherst demographic or weather covariates. Subtracting sunrise is algebraically unnecessary when every date has its own fixed effect.

### Outcome-blind calibration on Alberta data

`analysis/calibrate_portable_chronotype.py` compares reduced phenotypes against the already-established full Hobbs phenotype using predictor data only.

Date-fixed-effect early chronotype:

- Pearson r = 0.9612
- Spearman rho = 0.9230

Thus the portable specification preserves most of the full phenotype ordering.

A tempting alternative that additionally adjusts each bird-day first-feed time for that day's total feeder count performs much worse (Pearson r = 0.7692, Spearman rho = 0.6360) and is rejected **before Amherst outcomes**.

## Feeder-use adjustment

Construct an individual Year-1 total feeder-use phenotype with:

`daily_total_events ~ C(date) + (1 | bird)`

and standardize its bird random intercept.

On Alberta data this portable total-use phenotype correlates r = 0.9613 / rho = 0.9545 with the full Hobbs total-use phenotype.

## Year-1 bird eligibility

Primary eligibility is fixed before Year-2 membership is viewed:

- >=5 qualifying Year-1 bird-days with >=10 RFID events each;
- observations on >=3 distinct calendar dates;
- at least 50 raw RFID events in total.

The mixed model will estimate all eligible birds jointly; no threshold may be changed after Year-2 re-detection is known.

Sensitivity: repeat using >=10 qualifying bird-days. If this leaves fewer than 25 birds, report it descriptively rather than treating it as a decisive replication.

## Staged Year-2 unseal

Because field coverage changed, Year 2 is opened in two stages.

### Stage A — design-only unseal

A script may read Year-2 data only to output:

- unique feeder IDs;
- first and last timestamp;
- number of recording days;
- total event count.

It must not output, count, hash, sort, or otherwise expose individual bird IDs.

This design-only output is committed before Stage B.

### Exposure-matched primary cohort

After the Year-2 feeder set is known, calculate from **Year-1 only** the fraction of each bird's Year-1 events occurring at feeders that remain observable in Year 2.

Primary cohort: birds with >=80% of Year-1 events at feeders deployed in Year 2.

Predeclared sensitivity thresholds: >=50% and 100%.

If feeder identifiers cannot be linked across years, the replication is downgraded to exploratory and no non-redetection result will be interpreted biologically.

### Stage B — membership unseal

Only after Stage-A design output and the exposure-matched Year-1 cohort are committed:

`redetected = 1` if an eligible bird ID occurs at least once in Year-2 RFID data, otherwise `0`.

No minimum Year-2 event threshold is required for redetection: one valid event establishes presence.

## Primary model

`redetected ~ early_chronotype_z + total_feeder_use_z`

Primary estimand: odds ratio for next-winter redetection per 1 SD earlier chronotype.

The test is two-sided. Report beta, SE, OR, 95% CI, p-value, N, number redetected, and number not redetected.

Sex and dominance are not primary covariates because public bird-attribute metadata cover only a subset of RFID individuals. If adequate metadata exist, they may be reported as a predeclared subset sensitivity, not used to replace the primary result.

## Reliability diagnostics before Stage B

Before Year-2 membership unsealing, report:

- number of eligible birds and qualifying bird-days;
- distribution of qualifying days per bird;
- random-intercept variance / residual variance;
- split-half chronotype correlation (first vs second half of Year 1);
- correlation between early chronotype and total feeder-use phenotype.

A low split-half correlation does not trigger phenotype shopping. It lowers confidence in interpreting a null and is reported as a limitation.

## Interpretation / replication rule

This independent study cannot literally replicate `apparent survival` because Year-2 field coverage changed. It tests a narrower observable endpoint: re-detection conditional on comparable feeder opportunity.

Do not define success by p<.05 alone. Report:

1. Amherst effect and interval;
2. whether its sign is compatible with the Alberta estimate (OR 1.315 per SD earlier, CI 0.873–1.980);
3. inverse-variance pooled log-OR across Alberta + Amherst as a descriptive synthesis;
4. heterogeneity, with explicit warning that two studies cannot estimate between-study variance reliably.

No causal claim.

## Failure conditions

The replication is considered technically non-informative if any of these occur:

- Year-1 raw RFID cannot be obtained through normal authorized access;
- Year-1 and Year-2 feeder IDs cannot be linked;
- fewer than 25 exposure-matched eligible Year-1 birds remain;
- Year-1 timestamps cannot be interpreted consistently;
- Year-2 observation coverage is too different for redetection to be meaningful.

These are valid negative outcomes of the replication attempt and must be documented rather than relaxed after outcome access.
