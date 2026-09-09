# Latent Experiments 2

## Objective

Build and demonstrate an agent-driven scientific loop that starts from a consequential unexplained observation or disagreement, commits a discriminating prediction before confirmation access, tests it against independent evidence, preserves failures, and leaves reusable FOSS tooling.

This project is separate from `latent-experiments/`. The pilot is evidence about failure modes, not the operating protocol. See `PILOT-LESSONS.md`.

## Current status

**C001 and C002 stopped before confirmation; C003 completed a positive discovery but failed frozen independent confirmation; fresh scouts 001–003 produced no survivor. Scout 003 rejected C010 because independent confirmation aggregated away the unit-level pairing needed by the mechanism test, and C011 because the exact pigmentation/perfusion pulse-oximetry discriminator is already mature prior art. No independently confirmed new scientific claim yet. Next: one replicated-intervention scout, then project-level reassessment if it also fails.**

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

1. **Fresh scout 004 — replicated interventions.** Prefer repeated interventions across independent batches/sites/labs with direct mediator + outcome and identical measurement semantics.
2. **Require unit-aligned confirmation.** Having the same variable names in two datasets is insufficient if aggregation destroys the analysis-unit pairing required by the discriminator.
3. **Reassess after scout 004.** If it produces no survivor, stop broad scouting and evaluate a talk centered on the disciplined scientific loop itself rather than lowering the gate.

### C003 — Taylor-law dominance interpretation: failed confirmation

A constraint-preserving null fixed every species total, census total, and occurrence mask. Discovery in three German steppe cover plots found extra dominance-like temporal organization in 2/3 plots. Frozen confirmation in five independent Danish heath plots found 0/5 passes despite every raw Taylor slope being below 2; study-level p=1.0 under both null generators.

Reusable lesson: **`b<2` alone is mechanistically non-diagnostic.** In all eight analyzed plots the constraint null itself typically produced `b<2` (median roughly 1.4–1.8). Some communities showed extra organization beyond those constraints, but it did not generalize. See `RESULTS-C003.md`.

### Fresh scout 001 — no survivor

C004 used newly released ABCFlux v2 to ask whether CH4 observation-network representativeness is a between-ecosystem/time problem or a within-stratum sparse-measurement problem. Synthetic calibration showed ecosystem×month weighting can remove class oversampling but not preferential high-flux-day sampling. The exact needed empirical chamber-vs-eddy-covariance comparison, however, was already published across ten sites and multiple timescales in July 2026, so C004 was rejected before real flux outcomes. C005 (unperceived LO decoding) and C006 (data-availability statements) were demoted for weak clean confirmation / mature prior art. See `scouts/FRESH-SCOUT-001.md`.

Reusable lesson: **search for the implied discriminating experiment before investing in a newly enabled dataset analysis.**


### Fresh scout 002 — no survivor

C007 (sea-star wasting disease) was an unusually consequential explicit causation dispute, but the critics' decisive requested evidence is lesion histopathology/spatial pathogen localization. The public Dryad/NCBI evidence contains disease trajectories and coelomic-fluid sequencing, not that pathology; reanalyzing the proxy cannot manufacture the missing observation. C008 (ReDeeM mitochondrial lineage tracing) had excellent orthogonal lineage ground truth, but the exact filter-vs-ground-truth discriminator is already addressed in the 2026 reply and MitoDrift work. C009 (InAs–Al parity readout versus a superconducting gap) had excellent open code and device-level holdout potential, but the obvious transport-derived "gap" score is itself the physical proxy under dispute; without an orthogonal gap measurement at the same tuning points, a correlation analysis cannot adjudicate the disagreement. See `scouts/FRESH-SCOUT-002.md`.

Reusable lesson: **verify that the decisive observable is actually present and independent of the disputed proxy before treating an open dataset as capable of resolving a mechanism dispute.**

### Fresh scout 003 — no survivor

C010 (MuST-C SunScan versus destructive LAI) had unusually good discovery-side measurement completeness and a concrete spatial-heterogeneity-versus-senescence discrepancy. The best independent open confirmation, however, averaged SunScan over 50 plots while destructive LAI came from five plots, so it could not preserve the same-unit structure needed by the mechanism test; no MuST-C numeric LAI outcomes were opened. C011 (pulse-oximetry pigmentation versus perfusion/anatomy) was rejected before OpenOximetry outcomes because controlled-desaturation multivariable work already directly studies pigmentation, perfusion, hypoxemia, finger anatomy and device error. See `scouts/FRESH-SCOUT-003.md`.

Reusable lesson: **measurement completeness includes unit alignment: discovery and confirmation must preserve the same unit-level pairing required by the discriminator.**

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
