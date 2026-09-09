# Latent Experiments 2

## Objective

Build and demonstrate an agent-driven scientific loop that starts from a consequential unexplained observation or disagreement, commits a discriminating prediction before confirmation access, tests it against independent evidence, preserves failures, and leaves reusable FOSS tooling.

This project is separate from `latent-experiments/`. The pilot is evidence about failure modes, not the operating protocol. See `PILOT-LESSONS.md`.

## Current status

**C001 and C002 both stopped before confirmation. No substantive discovery claim yet. Next: one bounded C003 feasibility gate, then fresh scouting if it only restates mature Taylor's-law results.**

### C001 — repeated TEM-1 DMS maps: stopped

Firnberg 2014 + Stiffler 2015 were discovery evidence; Jacquier 2013 was reserved confirmation and Deng 2012 a method-contrast control. **Jacquier and Deng scores remain unopened.**

What survived:

- 4,782 common missense mutations; rank correlation ~.937 despite incompatible raw scales.
- ProteinGym preserves the chosen source scores numerically.
- Primary literature already establishes selection-strength-dependent TEM-1 effects.
- A tempting structured-residual statistic fails its empirical null: Firnberg→Stiffler position eta²=.215, while five actual same-condition Stiffler replicate pairs span .186-.454 and all reject the naive permutation null.
- Independent percentile-rank residuals make the stop stronger: cross-study eta²=.246 versus replicate range .298-.470.

Reusable lesson: **a cross-assay residual null must accept real same-condition replicates before structured residuals are called biology.** See `results/c001_calibration.json` and commit `2d5a21e`.

### C002 — neuronal criticality / subsampling: stopped

Allen Visual Coding Neuropixels supplied a strong operational testbed. Design metadata were used before spike access to freeze `functional_connectivity` sessions with a continuous ~30-minute spontaneous period. A VISp eligibility rule produced 12 discovery + 12 confirmation mice.

Only discovery mouse `767871931` was opened. **Eleven other eligible discovery mice and all 12 confirmation mice remain unopened.**

A FOSS multistep-regression (MR) estimator was calibrated at 4-ms bins with a frozen exponential-fit applicability gate R²>=.90:

- aggregate branching simulations at true m=.8/.98/.99 remain essentially unbiased under 100%/50%/25% event sampling;
- independent Poisson/null data fail applicability despite occasionally returning raw m near 1;
- the real mouse's primary 32/16/8-unit subsets all fail applicability; across ten alternative 32-unit subsets only 7/10 pass;
- fixed-neuron simulations with strong rate heterogeneity and static mixed timescales give 60/60 valid fits;
- simple global/asynchronous state-switch stress tests give 60/60 valid full-session fits.

Thus the real subset-dependent low-R² behavior is not reproduced by the bounded branching-family calibrations. Continuing would require progressively richer post-outcome model invention in a mature criticality debate, so C002 is stopped rather than rescued. See `RESULTS-C002.md`.

Reusable lesson: **“subsampling-invariant” estimation is conditional on model applicability. Gate the correlation/dynamical form itself before interpreting a near-one parameter.**

All four stochastic C002 result files reproduced byte-identically across two runs.

## Candidate ranking

1. **C003 — ecological Taylor's law, feasibility only.** Competing explanations: biological interactions/environmental stochasticity versus feasible-set/sampling constraints. Proceed only if primary literature + a specific dataset expose a sharper unresolved discriminator than “constraints can create Taylor's law.”
2. **Fresh discrepancy scout.** Preferred immediately if C003's cheap gate shows the mechanism debate already covers the obvious tests.
3. **Do not reopen C001/C002 confirmation.** Their active methods/questions failed before confirmation; preserved holdouts are not invitations to rescue them.

## Minimal execution layer

- `claims/` — claim/evidence-role/access state.
- `ledger.jsonl` — machine-readable input versions, access, calibration/results, decisions and resource events.
- `analysis/` — only analysis needed by an active investigation.
- `results/` — small reproducible outputs.
- `STATE.md` — exact resumable action.
- Raw data and third-party archives remain ignored.

## Resource budget

- FOSS/local computation only; no paid APIs or cloud compute without an explicit new budget.
- <=2 GB downloaded source data before a scientific checkpoint and <=10 GB transient cache.
- <=30 CPU-minutes for any single bounded analysis; no persistent/background jobs.
- Commit only code, metadata, small results, and documentation.
- Stop a path when the next test cannot change the scientific conclusion.

## SciPy India fit

Current conference requirements checked 2026-09-09: 30-minute in-person talk including Q&A; FOSS/OSI-licensed focus; CFP closes 19 Oct 2026 23:59 IST. AI/data-driven discovery and reproducibility are plausible tracks. The live loop should make **failed calibration and stopping** first-class outcomes, not only successful discoveries.
