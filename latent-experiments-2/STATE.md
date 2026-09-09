# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED -> C002 STOPPED -> C003 FAILED CONFIRMATION -> FRESH SCOUT 001 NO SURVIVOR -> FRESH SCOUT 002`.

## Durable completed paths

### C001 — TEM-1 repeated DMS maps

**STOP before confirmation.** A cross-assay structured residual looked significant against a shuffled null but was no larger than real same-condition replicate structure. Broad context dependence was already established. Jacquier confirmation and Deng control remain unopened. Commit `2d5a21e`.

Lesson: empirical replicate nulls can invalidate attractive permutation-based biological signals.

### C002 — neuronal criticality / subsampling

**STOP after one discovery mouse, before confirmation.** MR calibrated well on branching simulations but its assumed correlation form was subset-dependent/non-applicable in the first Allen VISp mouse and bounded heterogeneity/state-switch simulations did not reproduce the failure. Eleven discovery mice and all 12 confirmation mice remain unopened. Commit `eb02a4b`.

Lesson: subsampling robustness is conditional on model applicability.

### C003 — Taylor-law dominance interpretation

**FAILED CONFIRMATION / STOP.** A fixed occurrence+species-total+census-total null found extra dominance-like temporal organization in 2/3 German steppe discovery plots, but 0/5 reserved Danish heath confirmation plots. All eight raw slopes were `<2`, while the constraint null itself typically produced `b<2`. See `RESULTS-C003.md`; commit `5afac40`.

Lesson: `b<2` alone is mechanistically non-diagnostic; a positive discovery that fails frozen independent confirmation stays failed.

## Fresh discrepancy scout 001

**NO SURVIVOR.** See `scouts/FRESH-SCOUT-001.md`.

### C004 — Arctic-boreal methane measurement representativeness

**REJECTED ON PRIOR ART BEFORE REAL FLUX OUTCOMES.**

- ABCFlux v2 is a new 2026 >1,000-site monthly CO2/CH4 synthesis with measurement-method and coverage metadata.
- Synthetic calibration showed ecosystem×month target weighting corrects between-stratum oversampling but cannot repair preferential within-stratum measurement-day sampling.
- Calibration result SHA: `3e76e854e3a09a31db83b9986383b7d9410913c3491ac9d44f2d79c90b8fc0ea`.
- Määttä et al. 2026 (`10.5194/bg-23-4379-2026`, published 2026-07-03) already perform the sharpened coincident chamber-vs-eddy-covariance CH4 comparison across ten sites and multiple timescales, including the relevant sampling/footprint/protocol drivers.
- No ABCFlux methane flux values were opened.

Lesson: search for the **implied discriminating experiment**, not just the new dataset/topic, before implementation.

### C005 — human LO unperceived decoding

**DEMOTED / no outcomes opened.** Explicit report-error-vs-unconscious-information ambiguity is interesting, but the debate is mature, matched no-report confirmation is weak, and backward-masking raw data are ~94 GB.

### C006 — oceanography data-availability statements

**DEMOTED / no model fit.** Small article-level supplement is operationally excellent, but a journal-fixed-effects association would remain observational and policy-effect natural experiments already exist.

## Scientific progress vs engineering progress

Scientific progress: **no independently confirmed new scientific claim yet.** C001/C002 stopped at calibration/applicability; C003 had a positive discovery and failed independent confirmation; fresh scout 001 correctly rejected/demoted all candidates before substantive new outcomes.

Engineering progress: evidence-role guards, partial remote access, semantic gates, calibrated nulls, independent verification and reproducible stop transitions are sufficient. Do not expand into a general platform.

## Three-step assessment

1. **Did scout 001 produce an active question worth pursuing? No.** C004's exact discriminator is already published; C005/C006 lack clean causal/confirmatory leverage.
2. **Can another cheap test rescue these candidates without redefining them? No.** That would be candidate polishing after a failed gate.
3. **Does another scout remain justified? Yes.** The process is killing weak ideas cheaply, and there is time before the CFP. Change the search strategy rather than lower the standard.

## Exact next action — fresh scout 002

Search for **intervention-enabled discrepancies**, not merely observational anomalies.

1. Prefer 2025–2026 primary studies/data with one of:
   - randomized or quasi-random perturbations where two mechanisms predict different heterogeneous responses;
   - repeated measurements of the same physical/biological quantity by independent instruments or protocols;
   - natural experiments with a discontinuity/change point and an unaffected control population;
   - rich open experimental datasets whose published headline leaves a concrete mechanism ambiguity unresolved.
2. Search the *implied discriminator* before promoting each candidate. Reject it if that exact perturbation/comparison is already published.
3. Shortlist at most 3. For each record: who cares/decision; explanations A/B; cheapest discriminator; direct measurement semantics; discovery source; independent confirmation source; contamination/prior-art risk.
4. Prefer source-level/file-level/session-level holdouts and <1 GB raw input. Penalize archives requiring interactive auth for the live critical path.
5. On the leader, perform metadata/access feasibility and a known-null/known-positive calibration thought experiment only. Freeze roles and stop rule before substantive outcomes.

Resource budget remains FOSS/local, <=2 GB source data before the next checkpoint and <=30 CPU-min per bounded analysis.

## Ranked next actions

1. Fresh scout 002 above, emphasizing intervention/natural-experiment leverage.
2. If no candidate clears the gate, broaden domains again rather than revisiting C001–C006.
3. Preserve C001/C002 untouched confirmation evidence; C003/C004 are closed.
