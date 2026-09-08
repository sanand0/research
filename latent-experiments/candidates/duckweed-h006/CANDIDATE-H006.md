# H006 candidate — early reproduction and remaining lifespan in clonal duckweed

## Scientific question

Within a fixed light treatment, do *Lemna minor* fronds that reproduce more during their first week subsequently have shorter remaining reproductive lifespans?

Memorable version: **does spending early make a clone die sooner?**

This is an individual-level pace-of-life / allocation question within genetically clonal plants under the same light treatment, not the source paper's treatment-level caloric-restriction comparison.

## Why this appears latent

The source paper/code tests light treatment effects on lifespan, lifetime reproduction, intrinsic rate of increase, survival scaling, reproductive timing distributions, and final frond size. It does not test whether individual early reproductive output predicts later lifespan within treatment.

The study discusses life-history allocation mechanisms, so the relationship is biologically interpretable rather than an arbitrary unused-column association.

## Data and replication

Two independent experiments were conducted.

- **Discovery: Experiment 2.** 224 initial fronds; source exclusions leave 206, under full light vs 1/4 light. All included plants were followed to reproductive death.
- **Replication: Experiment 1.** Use only the five treatments used in the source paper's uncensored formal lifespan analyses (1, 1/2, 1/4, 1/8, 1/16), N=159 from the published ANOVA residual df. Exclude 1/32 and zero-light treatments because the experiment ended with surviving/censored fronds there.

## Rejected variants before outcome access

- **Morphology -> lifespan:** rejected because size/shape photographs were taken after death or experiment termination; this fails temporal provenance.
- **Unlandmarked early-output correlation:** rejected because variable observation windows can mechanically make longer-lived plants accumulate more 'early' observations.

## Minor seal imperfection

While testing whether Dryad's browser preview exposed row data, one Experiment-2 example row was rendered and included one `date.last.repro` value. No aggregate outcome distribution, predictor-outcome relationship, model, ordering, or additional outcome rows were inspected. That row is not used for specification choices.

## Candidate scorecard

- Open access: **partial pass** — landing page/code/previews are public; direct file blobs are operationally awkward in this environment.
- Original-analysis gap: **pass**.
- Outcome vocabulary: **pass** — reproductive death is represented by `date.last.repro`; Experiment 2 has complete deaths; Experiment 1 replication excludes the source-paper censored treatments.
- Outcome information: **pass** — continuous time-to-event, discovery N=206; replication N=159 before landmark eligibility.
- Temporal provenance: **pass with landmark design**.
- Predictor measurability: fixed 7-day count; no latent-trait estimation required.
- Join/schema integrity: same row contains ID, treatment, dates, and daily reproduction; no cross-file join required.
- Fresh outcome: **pass**.
- Replication path: **pass**, Experiment 1 is visible before Experiment-2 outcome analysis.

## Ranking among gate-passers

| Criterion | Score (0–2) | Rationale |
|---|---:|---|
| Scientific need | 1 | Fundamental life-history allocation question, though less directly operational than H004/H005. |
| Novelty | 2 | Within-treatment early-output -> later-lifespan landmark estimand is absent from source analyses found. |
| Information | 2 | Continuous completed lifespan, Experiment 2 N=206 before landmarking; replication N=159 before landmarking. |
| Interpretability | 2 | One early count, one remaining-lifespan outcome, treatment-stratified Cox HR. |
| Live-demo value | 2 | Fixed early window followed by literal future-lifespan reveal is easy to explain. |
| Reusable asset | 2 | Landmarking converts many longitudinal datasets into leak-resistant early-history tests. |
| Replication ease | 2 | Independent Experiment 1 is in the same public deposit and frozen before Experiment-2 analysis. |

**Total: 13/14.** Promote to H006 freeze, subject to source-file acquisition after commit.
