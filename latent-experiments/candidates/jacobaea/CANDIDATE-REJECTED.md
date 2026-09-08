# Jacobaea vulgaris Markov-history candidate — REJECTED

## Proposed latent question

Do individual *Jacobaea vulgaris* plants violate the first-order Markov assumption used by the source demographic transition matrices — i.e. does a plant's previous life stage improve prediction of its next stage after conditioning on its current stage?

## Why it looked promising

The source study followed tens of thousands of marked plants over five years and analyzes population dynamics with first-order stage-transition matrices. A reproducible history effect would test a load-bearing model assumption rather than merely add another predictor.

## Hard-gate failure: released granularity

The sole released S1 workbook (`S1_dataset.xlsx`) contains 280 field-year-treatment aggregate rows, not persistent individual histories. Its sheet `stages_cover_div` has columns for field, region, year, treatment, stage totals/means, plant cover, richness, and related aggregate measures. There is no persistent plant ID or individual stage sequence.

Therefore the released data cannot answer the individual-history question. An aggregate population-memory analysis would be a materially different estimand and is not a substitute.

## Decision

**REJECTED before outcome analysis.** Do not infer individual Markov dependence from aggregate stage counts.

## Reusable lesson

A paper's methods may describe individually marked subjects while its public deposit exposes only aggregates. Candidate screening must verify the **released unit of analysis**, not infer it from the study design.
