# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED BEFORE CONFIRMATION -> C002 FEASIBILITY`.

C001 confirmation (`BLAT_ECOLX_Jacquier_2013`) and control (`BLAT_ECOLX_Deng_2012`) mutation scores have **not** been accessed.

## Inspected / completed

- Monorepo instructions and Git root; pilot lessons compacted in `PILOT-LESSONS.md`.
- C001 ProteinGym metadata plus discovery-only Firnberg/Stiffler processed and raw files.
- ProteinGym score semantics and preprocessing verified: chosen processed scores are numerically identical to source Firnberg `linear` and Stiffler `2500` columns.
- C001 overlap: 4,782 common missense mutations; Spearman ~0.9373.
- Primary literature/prior-art check: selection-strength-dependent TEM-1 context effects are already established; later work compares multiple TEM-1 mutation-effect maps.
- `analysis/c001_calibrate.py`: position-blocked monotone residual calibration with five same-condition Stiffler replicate nulls, known 39→2500 context shift, and injected effects.
- `results/c001_calibration.json`: deterministic across two stochastic reruns, SHA-256 `2eae5d560d0683778176677c167aa79a39458788556c0f1f249c7da6ebdb5e8b`.

## C001 scientific result

**STOP / NO CONFIRMATION ACCESS.**

The proposed position-residual detector is invalid for the intended claim:

- Firnberg→Stiffler 2500 residual position eta² = 0.2151.
- Five real same-condition Stiffler replicate pairs have eta² = 0.1863–0.4535 and all reject the nominal within-score-bin permutation null at p≈0.0025.
- Thus the cross-study structured residual is within empirical technical-replicate structure.
- Known large selection shift Stiffler 39→2500 has eta² = 0.5255.
- Independent rank-residual re-derivation strengthens the stop: cross-study eta² 0.2462 versus same-condition replicate range 0.2975–0.4703.
- Injected-effect power numbers are explicitly uninterpretable because the real-null calibration failed.

Reusable scientific/method lesson: shuffled/permuted residual nulls can severely understate structured experimental noise; same-condition replicate pairs are a stronger calibration target.

## Engineering progress

- Minimal claim/access ledger working.
- Discovery-only remote ZIP range extraction demonstrated without downloading confirmation score payloads.
- One bounded reusable calibration script and deterministic result added; no general platform built.
- Tool/safety failures logged separately; project notes preserve scientific failures.

## Current blockers / risks

### C001
Closed. Do not rescue by opening Jacquier/Deng or scanning alternative residual structures for significance.

### C002
- Need to establish an operationally reliable open electrophysiology source and exact observation units before avalanche analysis.
- First small Zenodo control-code request timed out; do not make that archive a live dependency unless a stable alternate route exists.
- Criticality/subsampling debate is mature; the candidate survives only if a specific consequential unresolved discriminator emerges, not by rediscovering that subsampling matters.
- Discovery/confirmation split must be by scientifically independent units (prefer animals/sessions), not random spikes/time bins.

## Three-step assessment

1. **Does C001 still matter as an active question? No.** Its broad premise is established and the sharper detector fails empirical-null calibration.
2. **Can another C001 test change that conclusion without adaptive rescue? No.** Opening reserved confirmation would spend evidence on an invalid detector.
3. **Does progress justify redirecting? Yes.** The failure produced a reusable calibration lesson while preserving untouched confirmation evidence.

## Exact next action

For **C002 neuronal criticality vs subsampling/analysis artifact**:

1. Verify current Allen public electrophysiology/Neuropixels access from LocalMCP and inspect only manifests/documentation first.
2. Identify the actual independent units, recording duration, spike-time semantics, brain regions, and manageable source sizes.
3. Find a stable FOSS implementation or reproduce the minimal published criticality/subsampling metrics from primary methods; do not depend on the timed-out Zenodo bundle.
4. Before opening substantive spike outcomes, designate discovery animals/sessions and reserved confirmation animals/sessions plus a synthetic known-null/known-positive calibration suite.
5. Run one cheap feasibility calculation only: estimate usable unit counts and whether controlled thinning/binning can be performed locally within the resource budget.

Reject/redirect C002 before exploratory avalanche analysis if independent confirmation units are too few, recording semantics make comparisons incoherent, or the only planned result restates already-established subsampling sensitivity.

## Ranked next actions

1. **C002 feasibility above** — highest consequence/live-loop value if clean independent sessions are accessible.
2. **C003 Taylor's law feasibility** — fallback if C002 access or unresolved-question gate fails; start with dataset semantics and an explicit biological-vs-feasible-set discriminator.
3. **Fresh discrepancy scout** — preferred over forcing either mature debate if neither leaves a sharp unanswered test.
