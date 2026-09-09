# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED -> C002 STOPPED -> C003 FAILED CONFIRMATION -> SCOUT 001 NO SURVIVOR -> SCOUT 002 NO SURVIVOR -> SCOUT 003 NO SURVIVOR -> FRESH SCOUT 004`.

## Durable completed paths

### C001 — TEM-1 repeated DMS maps

**STOP before confirmation.** Cross-assay residual structure was no larger than real same-condition replicate structure; broad context dependence was already established. Jacquier confirmation and Deng control remain unopened. Commit `2d5a21e`.

Lesson: empirical replicate nulls can invalidate attractive permutation-based biological signals.

### C002 — neuronal criticality / subsampling

**STOP after one discovery mouse, before confirmation.** MR calibrated on branching simulations but failed its correlation-form applicability gate in the first Allen VISp mouse; bounded heterogeneity/state-switch simulations did not reproduce that failure. Eleven eligible discovery mice and all 12 confirmation mice remain unopened. Commit `eb02a4b`.

Lesson: subsampling robustness is conditional on model applicability.

### C003 — Taylor-law dominance interpretation

**FAILED CONFIRMATION / STOP.** Constraint-preserving null found extra dominance-like organization in 2/3 German steppe discovery plots but 0/5 reserved Danish heath confirmation plots. All raw slopes were `<2`; the null itself typically produced `b<2`. Commit `5afac40`.

Lesson: `b<2` alone is mechanistically non-diagnostic; positive discovery that fails frozen independent confirmation stays failed.

### Scout 001 — no survivor

C004 methane representativeness rejected because the exact chamber-vs-EC discriminator was already published; C005/C006 failed clean-confirmation/causal-leverage gates. Commit `3b47bc6`.

Lesson: search the implied discriminator, not merely the topic/dataset.

### Scout 002 — no survivor

C007 sea-star wasting lacked the decisive lesion-pathology observation; C008 mtDNA-lineage filtering already had orthogonal-ground-truth prior art; C009 parity-vs-gap had only the disputed transport proxy rather than an independent same-setting gap observable. No substantive numeric outcomes opened. Commit `4fe1dd2`.

Lesson: the decisive observable must exist and be independent of the disputed proxy.

### Scout 003 — no survivor

See `scouts/FRESH-SCOUT-003.md`.

- **C010 — MuST-C SunScan vs destructive LAI:** rejected before numeric outcomes. Discovery data have direct repeated SunScan + destructive green-LAI measurements and plausible spatial-mismatch vs senescence mechanisms. The best independent open confirmation (Edinburgh DataShare `10.7488/ds/2989`) averages SunScan over 50 plots by date/treatment while destructive LAI comes from five plots, destroying the same-unit pairing required by the discriminator. A bounded search found no independent open raw same-unit pairing. Do not substitute within-MuST-C crop splitting for independent confirmation.
- **C011 — pulse-oximetry pigmentation vs perfusion/anatomy:** rejected before OpenOximetry outcomes. Controlled-desaturation multivariable work already shows joint effects of pigmentation, perfusion and hypoxemia; the 2026 34-device study measures objective ITA, finger diameter and percent modulation, and 2026 EquiOx adjusts for perfusion.
- A synchronized radar/ECG/accelerometry/breath-hold dataset was screened but not promoted: respiration harmonics, body motion and breath-hold isolation are already standard radar-vital-sign validation questions.

Lesson: **variable completeness is insufficient; independent confirmation must preserve the same analysis-unit alignment needed by the discriminator.**

## Scientific progress vs engineering progress

Scientific progress: **no independently confirmed new scientific claim yet.** C001/C002 stopped at calibration/applicability, C003 passed discovery then failed confirmation, and three fresh scouts killed weak candidates before spending substantive outcome/confirmation evidence.

Engineering progress: sufficient. Evidence-role guards, semantic gates, calibrated nulls, independent verification, deterministic reruns and stop transitions work. Do not build more infrastructure.

Search-process progress:
1. search the implied discriminator, not only the topic/dataset;
2. verify the decisive observable exists and is independent of disputed proxies;
3. verify discovery and confirmation preserve the same **unit-level measurement alignment** needed by the test.

## Three-step assessment

1. **Did scout 003 find a well-measured unresolved discrepancy? Yes: C010.** But the independent archive aggregates away the decisive unit-level structure.
2. **Can C010/C011 be repaired cheaply without redefining the claim? No.** Within-trial crop splitting would weaken confirmation; C011 is mature prior art.
3. **Is another scout justified? Yes, once, with a stronger source structure.** Three no-survivor scouts are evidence that controversy/instrument-bias mining has low yield. Switch to replicated interventions. If scout 004 also has no survivor, reassess whether the SciPy talk should emphasize the disciplined discovery/failure loop rather than keep broad-scouting indefinitely.

## Exact next action — fresh scout 004

Run a **replicated-intervention scout** rather than another observational-measurement scout.

1. Search 2025–2026 primary studies/data for an intervention repeated across >=2 independent batches, laboratories, sites or organisms with **identical measurement semantics**.
2. Start from a consequential heterogeneous or unexpected treatment response for which two explanations make different predictions. Require intervention, proposed mediator and endpoint to be directly observed on the same experimental unit.
3. Require source-level confirmation from another batch/site/lab already present or from a genuinely independent public study; no arbitrary row split.
4. Search the exact treatment-response discriminator before coding. Reject if already published.
5. Prefer <1 GB, FOSS/public, no interactive authentication on live critical path.
6. Shortlist at most 3. For the leader, inspect metadata/access only and run a known-null/known-positive calibration thought experiment; freeze roles and stop rule before substantive outcomes.

If scout 004 has no survivor, stop broad scouting and explicitly reassess the talk direction using the accumulated C001–C011 evidence rather than lowering the scientific gate.

Resource budget remains FOSS/local, <=2 GB source data before next checkpoint, <=30 CPU-min per bounded analysis.

## Ranked next actions

1. Fresh scout 004 above: replicated interventions with direct mediator + outcome and source-aligned confirmation.
2. If no survivor, perform a project-level scientific post-mortem and evaluate a talk centered on why agentic science needs calibration, semantic gates and frozen confirmation.
3. Preserve untouched C001/C002 confirmation evidence; C003–C011 are closed/rejected under their current questions.
