# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED -> C002 STOPPED -> C003 FAILED CONFIRMATION -> FRESH DISCREPANCY SCOUT`.

C001 confirmation/control scores remain unopened. C002 confirmation spikes remain unopened; only one discovery mouse was accessed. C003 completed a genuine discovery/confirmation loop and failed its frozen independent confirmation.

## Completed

### C001 — repeated TEM-1 DMS maps

**STOP before confirmation.** A structured cross-assay residual looked significant against a shuffled null but was no larger than structure in real same-condition replicate pairs. Broad context dependence was already established. Jacquier confirmation and Deng control remain unopened. See commit `2d5a21e`.

Reusable lesson: empirical replicate nulls can invalidate attractive permutation-based biological signals.

### C002 — neuronal criticality / subsampling

**STOP after one discovery mouse, before confirmation.** A subsampling-aware MR estimator calibrated well on aggregate and fixed-neuron branching simulations, including bounded heterogeneity/state-switch stress tests, but applicability depended strongly on which real VISp neurons were sampled. Further dynamical-model expansion would be post-outcome rescue. Eleven eligible discovery mice and all 12 confirmation mice remain unopened. See `RESULTS-C002.md` and commit `eb02a4b`.

Reusable lesson: subsampling robustness is conditional on model/correlation-form applicability.

### C003 — within-community Taylor law / dominance stabilization

**FAILED CONFIRMATION / STOP.** See `RESULTS-C003.md`.

Scientific discrepancy:

- Gracia et al. 2026 interpret within-community temporal Taylor slopes `b<2` as a widespread potential dominance-stabilizing effect in plant communities.
- Feasible-set literature shows Taylor-law form can emerge from abundance/census constraints.
- Frozen discriminator: compare observed `b` and a dominance-CV statistic against a continuous null preserving exact species totals, exact census totals, and the observed occurrence mask.

Method:

- percentage-cover data only;
- species present >=15% census years, nonzero variance; >=4 species/plot;
- OLS `b` primary; CVratio secondary;
- 999 nulls; Exponential positive weights + IPF primary, lognormal weights sensitivity;
- plot pass requires `p_b<=.025` AND `p_CV>=tail .025` (upper-tail p<=.025);
- null calibrated on toy and actual discovery support before observed slopes.

Discovery — BioTIME 713, German steppe, 3 permanent plots x 24 census years:

- all raw `b<2`: 1.5065, 1.3218, 1.2587;
- Plots 1 and 3 pass both metrics under both null families; Plot 2 does not;
- discovery gate 2/3 passed;
- result `cca844ad9bf90f2efb488bc98f38ae9fb286576843b793e8a264352650cebe21`, reproduced exactly.

Confirmation-source gates:

- BioTIME 569 rejected before raw values: Count only, no Cover field.
- BioTIME 240 opened for structure only, then rejected: 40 quadrat-years had two distinct Sep/Oct fall samples; no outcome statistic computed.
- BioTIME 627 chosen as fresh executable confirmation: Danish heath, Cover, exactly 5 permanent plots x 10 unique censuses.

Frozen confirmation — BioTIME 627:

- raw `b` again all <2: 1.6561, 1.7254, 1.6659, 1.6716, 1.8473;
- 0/5 plots pass either constraint-null family;
- study-level pass-count p=1.0 under both families;
- confirmation failed;
- result `4e75f219116a59786e8bce6a2493145f034a8bcf5e58e939b7fc65b58583125b`, reproduced exactly;
- independent DuckDB derivation matched all eight observed slopes.

Narrow result that survives without rescue: **`b<2` alone is mechanistically non-diagnostic in these communities.** The prespecified occurrence+margin null itself typically produces `b<2` (null medians ~1.4–1.8). Some discovery plots contain extra temporal organization beyond that null, but it did not generalize to the reserved ecosystem. This is consistent with older feasible-set work and is not a claim that the 2026 global study is generally wrong.

Do not decompose which preserved constraint generates low `b`, change the null, or choose another confirmation on these C003 data without opening a new claim with fresh evidence.

## Scientific progress vs engineering progress

Scientific progress:

- **No independently confirmed new biological/scientific claim yet.**
- C003 is the first complete positive-discovery -> frozen-confirmation-failure loop in this project.
- It produced a useful narrower methodological observation but failed the intended generalization.
- C001/C002 were stopped even earlier by calibration/applicability gates.

Engineering progress:

- evidence-role/access guards, partial remote reads, measurement-semantic gates, continuous fixed-support/margin randomization, known-null/known-positive calibration, independent re-derivation, deterministic reruns, and explicit stop transitions all work;
- do not turn this into a platform yet.

## Three-step assessment

1. **Does the C003 scientific question still matter? Yes.** Mechanistic interpretation of dominance/stability matters, and the 2026 claim is current.
2. **Can another test on the current C003 evidence cleanly repair the failed confirmation? No.** Another ecosystem, null decomposition, or altered census rule would be a new hypothesis after failure.
3. **Does progress justify redirecting? Yes.** The discovery/confirmation failure is informative and fully documented; continuing C003 would reduce epistemic discipline rather than add it.

## Exact next action

Run a **fresh discrepancy scout**, not another member of the original shortlist.

1. Search current primary literature (prefer 2025–2026) across computational/experimental sciences for consequential observations where two credible explanations make different predictions.
2. Shortlist **at most 3**. For each state:
   - observed disagreement/anomaly;
   - who cares / what decision changes;
   - competing explanations;
   - cheapest discriminating intervention or analysis;
   - open raw discovery evidence and a genuinely independent confirmation source;
   - contamination/prior-art risk.
3. Prefer candidates where the central measurement is direct, one analysis unit maps cleanly to one independent experimental/observational unit, and confirmation can be withheld by source/file/session—not merely by row split.
4. Penalize mature debates whose obvious discriminator is already published, and datasets requiring ambiguous census aggregation, derived traits, or brittle access.
5. Choose one leader and run **metadata/access feasibility only** plus one cheap calibration thought experiment. Do not open substantive outcomes until discovery/confirmation roles and a stop rule are frozen.

Resource budget remains FOSS/local, <=2 GB source data before next checkpoint, <=30 CPU-min per bounded analysis.

## Ranked next actions

1. Fresh discrepancy scout above.
2. If no candidate clears the relevance + clean-confirmation gate, broaden domains rather than lowering the gate.
3. Preserve C001/C002 untouched confirmation evidence; C003 is closed after confirmation failure.
