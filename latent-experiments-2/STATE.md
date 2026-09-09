# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED -> C002 STOPPED -> C003 FAILED CONFIRMATION -> SCOUT 001 NO SURVIVOR -> SCOUT 002 NO SURVIVOR -> FRESH SCOUT 003`.

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

### Fresh scout 001

**NO SURVIVOR.** C004 methane representativeness was rejected before real outcomes because the sharpened paired chamber-vs-eddy-covariance discriminator had already been published in July 2026. C005/C006 failed clean-confirmation/causal-leverage gates. See `scouts/FRESH-SCOUT-001.md`; commit `3b47bc6`.

Lesson: search for the implied discriminating experiment before implementing a new-dataset analysis.

### Fresh scout 002

**NO SURVIVOR.** See `scouts/FRESH-SCOUT-002.md`.

- **C007 — sea-star wasting / Vibrio causation:** rejected before substantive outcomes. The explicit 2026 critique requires lesion histopathology/spatial pathogen localization. Public Dryad/NCBI data contain gross disease trajectories plus coelomic-fluid sequencing, not that decisive pathology; the original authors state retained experimental samples could be examined pathologically. A proxy reanalysis cannot answer the measurement dispute.
- **C008 — ReDeeM mtDNA lineage tracing:** rejected on discriminator-specific prior art. Filtering low-support/end variants against orthogonal lineage ground truth is already substantially tested in the 2026 reply and MitoDrift work.
- **C009 — InAs–Al parity signal versus gap robustness:** rejected before measured outcomes. Open code/data have attractive device-level structure, but the transport-derived gap proxy is exactly what critic and authors disagree about. Without an independent spectroscopic gap observable at the same tuning points, parity-vs-gap correlation is non-identifying.

No substantive numeric outcome table from C007–C009 was opened. Metadata/code-only inspection was sufficient to reject them.

Lesson: **a decisive observable must actually exist in the evidence and be independent of the disputed proxy.** Open data do not imply the data can adjudicate the mechanism.

## Scientific progress vs engineering progress

Scientific progress: **no independently confirmed new scientific claim yet.** C001/C002 stopped at calibration/applicability; C003 passed discovery then failed confirmation; scouts 001/002 killed six later candidates before wasting confirmation evidence.

Engineering progress: the execution layer is sufficient. Evidence-role guards, semantic/access gates, calibrated nulls, reproducibility, and stop transitions work. Do not build more platform.

Search-process progress: the screening funnel has improved twice:
1. search the implied discriminator, not only the topic/dataset;
2. verify the decisive observable is measured directly and independently enough to identify the disagreement.

## Three-step assessment

1. **Did scout 002 find consequential scientific disagreements? Yes.** C007 and C009 are real, current expert disagreements with important implications.
2. **Can available public evidence execute the decisive test? No.** C007 lacks pathology; C009 lacks an orthogonal same-setting gap measurement; C008's discriminator is already published.
3. **Would more analysis rescue them cleanly? No.** It would substitute disputed proxies for missing observations or replicate prior art. Redirect.

## Exact next action — fresh scout 003

Run a **measurement-complete discrepancy scout**.

1. Before ranking any candidate, write down the *decisive observable* that would distinguish explanations A/B and verify that it is already contained in the public data. Reject immediately if it is latent/unmeasured or available only through the proxy whose interpretation is disputed.
2. Prefer one of these evidence structures:
   - paired instrument/protocol A and B measurements plus a third independent reference standard on the same units;
   - randomized perturbation with both a directly measured mediator and outcome on independent experimental units;
   - lineage/barcode experiment with pre-perturbation state and post-perturbation fate on the same units plus an orthogonal lineage label;
   - natural experiment with an unaffected control and a directly measured intermediate mechanism.
3. Require at least two independent batches/devices/sites/files so discovery and confirmation can be withheld by source-level unit, not arbitrary rows. Prefer <1 GB input and FOSS/public access without interactive auth on the live critical path.
4. Search the **exact proposed discriminator** in current literature before coding. Reject if already published.
5. Shortlist at most 3. For the leader, perform metadata/access feasibility and a known-null/known-positive calibration thought experiment only. Freeze discovery/confirmation and stop rule before substantive outcomes.

Resource budget remains FOSS/local, <=2 GB source data before next checkpoint, <=30 CPU-min per bounded analysis.

## Ranked next actions

1. Fresh scout 003 above, measurement-completeness first.
2. If no candidate survives, broaden domains while preserving the gate; do not lower it.
3. Preserve untouched C001/C002 confirmation evidence; C003–C009 are closed/rejected under their current questions.
