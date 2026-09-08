# Replication 001B — UABG 2018/19 chronotype to later RFID apparent survival

**Status: FEASIBILITY / ANALYSIS DESIGN FROZEN BEFORE FARR `RFID.csv` INDIVIDUAL OUTCOME ACCESS**

Date: 2026-09-08 SGT

## Why this candidate

This links two independent publications from the same University of Alberta Botanic Garden population:

1. Arteaga-Torres, Wijmenga & Mathot (2020), predator-cue experiment, winter 2018/19. Eight RFID feeders recorded visit time and PIT-tag identity. Antennas were installed in early October 2018 and data were collected from memory cards every four days. The supplementary methods state that raw registrations contain date, time and PIT-tag hex code.
2. Farr, Haave-Audet, Thompson & Mathot (2021), PIT-tag method/survival study. Its OSF project `zvfpb` publicly contains an `RFID.csv` individual-level apparent-survival dataset plus analysis code. Metadata says it contains unique bird ID, redetection method, event time, censoring, catching season/date and sex.

The cross-paper relation chronotype -> later RFID survival is not an analysis either paper reports.

## Outcome seal

`candidates/replication-alberta-farr/RFID.csv` has **not** been downloaded or opened as of this freeze. Only its public metadata and the authors' R code were inspected.

The R code confirms that RFID-based survival is analysed using Cox proportional hazards models, but no individual event/censor values have been viewed.

## Hard feasibility gate: identifier mapping

The Arteaga timing stream is explicitly keyed by 10-digit PIT-tag hex code. Farr metadata calls its key `ID`, and Farr's public R code treats at least some IDs as short study numbers (e.g. `68`, `107`, `249`).

Therefore **no outcome unseal is allowed until an explicit public or author-provided mapping between Farr ID and PIT hex code is obtained**.

Do not infer mappings from row order, sex, dates, behaviour, or outcomes. If no auditable mapping exists, this replication stops.

## Predictor period and contamination control

Use 2018/19 RFID data after the autumn capture period and before the end of the predator experiment.

The predator experiment ran late Nov 2018 through early Mar 2019, with experimental treatment dates explicitly listed in supplementary Table S1. RFID readers were already operating from early Oct 2018.

Primary timing phenotype uses only **non-experimental calendar days**. All dates containing any control/acoustic/visual/combined predator treatment are excluded globally, not only at the treated feeder. This conservative rule avoids treatment-induced delays contaminating chronotype.

If the released raw archive contains only experimental windows rather than continuous all-day feeder logs, the replication is technically non-informative and stops.

## Portable predictor construction

Use the same external-study-compatible specification frozen for Amherst:

- bird-day eligibility: >=10 valid RFID registrations;
- remove duplicate RFID registrations separated by <5 seconds, matching Arteaga supplementary validation;
- first daily visit = minimum valid timestamp for the bird-day;
- `first_clock_minutes ~ C(date) + (1 | bird)`;
- sign-reverse and standardize the bird random intercept so +1 SD = earlier chronotype;
- `daily_total_events ~ C(date) + (1 | bird)` for feeder-use intensity.

Minimum individual eligibility: >=5 qualifying non-experimental bird-days and >=50 raw RFID registrations. Sensitivity: >=10 qualifying days.

This date-fixed-effect phenotype was calibrated on Alberta 2022/23 predictor data before any replication outcome: chronotype r=.961 / rho=.923 versus the full Hobbs phenotype; total-use r=.961 / rho=.955.

## Survival time origin: avoid immortal-time bias

Farr's `Event` clock starts at first capture, whereas chronotype is measured later in winter 2018/19. A standard Cox model from capture would incorrectly attribute pre-chronotype survival time to the chronotype predictor.

Primary analysis will therefore use a **landmark / left-truncated survival design**.

Landmark date: the first date after the chosen non-experimental chronotype window on which all predictor data used for an individual are complete. Prefer one common fixed landmark (end of the timing window) if the raw archive supports it.

For each matched bird:

- entry time = years from `Catch_Date` to landmark;
- stop time = Farr `Event` time;
- event indicator = Farr `Censored` under the authors' coding;
- include only birds known to be alive/observable through the landmark and with `stop > entry`.

Model:

`Surv(entry_time, Event, Censored) ~ early_chronotype_z + total_feeder_use_z + Sex`

If Farr's released event-time representation cannot support left truncation unambiguously, do **not** improvise. Downgrade to a prespecified binary post-landmark RFID-redetection endpoint only if it can be reconstructed directly from released follow-up dates without outcome-dependent choices; otherwise stop.

## Primary estimand

Hazard ratio per 1 SD earlier chronotype, conditional on total feeder use and sex.

Because hazard >1 means earlier mortality/non-redetection, direction is opposite the Experiment-001 odds ratio convention. For synthesis, convert results to a common direction explicitly; do not compare raw OR and HR signs mechanically.

Two-sided test. Report N, event count, HR, 95% CI, p, proportional-hazards diagnostics, chronotype reliability, and timing/use correlation.

## Reliability gates before outcome modelling

Before opening Farr outcomes, predictor-side work must establish:

- explicit hex-code <-> Farr-ID mapping with provenance;
- continuous-enough non-experimental RFID coverage;
- >=25 matched eligible birds;
- split-half chronotype correlation;
- random-intercept and residual variance;
- no accidental inclusion of observer PIT tags;
- treatment dates successfully excluded.

No threshold may be relaxed after seeing survival values.

## Failure conditions

Stop and report non-informative if:

- identifier mapping cannot be obtained;
- the raw archive contains only treatment-relative observations rather than full-day logs;
- fewer than 25 birds remain after auditable matching and timing eligibility;
- event-time coding cannot support a post-chronotype survival analysis without outcome-dependent reconstruction;
- raw Dryad data remain inaccessible through normal authorized access.

## Current blocker

Predictor-side documentation is strong, and Farr outcomes are openly hosted on OSF. The unresolved blocker is the **auditable ID mapping plus access to the 936.9 MB raw RFID archive**, currently on Dryad behind a human-confirmation/WAF flow. This is now a concrete data-engineering/authorship question rather than a statistical-design question.
