# STATE

Updated: 2026-09-09 SGT

## Phase

`C001 STOPPED -> C002 STOPPED -> C003 FEASIBILITY`.

No C001 confirmation/control scores were opened. No C002 confirmation spikes were opened; only discovery mouse `767871931` was accessed.

## Completed

### Project/pilot

- Monorepo instructions/Git root inspected; pilot lessons compacted in `PILOT-LESSONS.md`.
- Minimal claim/access ledger, resumable state, ignored raw-data cache, bounded analysis/results layer established.

### C001 — stopped before confirmation

- Discovery-only Firnberg/Stiffler raw + processed score semantics verified.
- 4,782 shared missense mutations; Spearman ~.937.
- Broad context-dependence premise found substantially established in prior literature.
- Proposed position-residual detector fails real same-condition replicate calibration.
- Stop decision stable under independent percentile-rank residualization.
- Jacquier confirmation and Deng control remain unopened.
- Checkpoint commit: `2d5a21e`.

### C002 — stopped after one discovery mouse, before confirmation

Data/design:

- Allen Visual Coding Neuropixels public S3 works through HTTP listing/range reads.
- 58 independent mouse/sessions in metadata; `functional_connectivity` chosen before spike values because it contains a standardized continuous ~30-minute spontaneous block.
- VISp metadata eligibility `>=32 quality=good` units leaves 12 discovery + 12 confirmation mice.
- Spike values accessed only for discovery session `767871931`; 11 other eligible discovery mice and all 12 confirmation mice remain unopened.

Method/calibration:

- `mrestimator==0.2.0`, 4-ms bins, lags 1..200, applicability gate R²>=.90.
- Aggregate/binomial-event calibration: true m=.8/.98/.99 recovered accurately under heavy sampling loss; Poisson known-null fails applicability.
- First real mouse: primary 32/16/8 subsets all fail applicability; 7/10 alternative fixed 32-unit subsets pass, 3/10 fail.
- Post-first-mouse fixed-neuron diagnostic: common m=.98 with strong rate heterogeneity 30/30 pass; static mixed m=.85... .995 modules 30/30 pass.
- Post-first-mouse state-switch diagnostic: global and asynchronous module switches each 30/30 full-session pass; all within-state segments pass.
- These bounded branching-family violations do not reproduce the real mouse's low-R²/subset-dependent failures.

Decision:

**STOP C002.** Further progress would require inventing richer dynamical models after seeing the real-data failure (oscillation/refractory/spatial/latent-state variants), turning method calibration into adaptive rescue. The criticality/subsampling debate is already mature, so this is not justified before confirmation.

Reusable result: subsampling robustness does not waive the need to validate the estimator's assumed dynamical/correlation form on real recordings.

Reproducibility hashes, each identical across two executions:

- `results/c002_mr_calibration.json`: `4cbdc7249d6f60ac9aa9025a8add628af7b58d5930b8f4d38c04cdbff65e492b`
- `results/c002_session_767871931.json`: `58d6b672550ece5843ea98d2643ab34b14b3c5c21aabe0552fea1873bc863365`
- `results/c002_fixed_neuron_calibration.json`: `3757409dad78d6ac79e0b41f2f2d09277a4949c473b0e80f9f0fd37e5cfdb570`
- `results/c002_state_switch_calibration.json`: `6e0150da212fd74d65e0c5a4bdb7244bafe84b3dfabdc8a2e08d460b4af5ba20`

See `RESULTS-C002.md`.

## Scientific progress vs engineering progress

Scientific progress: **no discovery claim yet.** Two plausible paths have been killed by calibration/applicability gates before confirmation. This is positive evidence about the research process, not evidence that the agent has discovered new biology.

Engineering progress: evidence-role guards, remote partial access, synthetic + empirical calibration, stochastic reproducibility, and explicit stop transitions are working. Do not expand this into a general platform yet.

## Three-step assessment

1. **Does C002 still matter as a general scientific debate? Yes, but not as this active experiment.** The current single-timescale MR route fails applicability on the first mouse and richer rescue would be adaptive.
2. **Can the next C002 test cleanly change the current conclusion? No.** Another discovery mouse or another post-hoc model would not repair the calibration boundary without redefining the experiment.
3. **Does progress justify redirecting? Yes.** C002 produced a reusable method lesson while preserving almost all discovery data and all confirmation data.

## Exact next action

Run **one bounded C003 Taylor's-law feasibility gate** before any exploratory outcome analysis:

1. Re-read the primary mechanism papers already identified and locate one small, coherent open ecological time-series dataset with explicit units/census semantics.
2. State a specific consequential disagreement, who cares, the two competing explanations, and one observation that could distinguish them. “Taylor's law appears” and “randomization changes the exponent” are insufficient because both are well studied.
3. Verify dataset granularity, repeated-unit identifiers, census effort, missingness, and an independent ecosystem/data source for later confirmation.
4. Designate discovery versus confirmation units/data before computing mean-variance relationships.
5. Run only a cheap metadata/feasibility calculation. **Reject C003 immediately** if the only available question simply reproduces the known feasible-set/sampling explanation.

If C003 fails that gate, do a fresh discrepancy scout rather than forcing the original shortlist.

## Ranked next actions

1. C003 feasibility gate above.
2. Fresh discrepancy scout across computational/experimental sciences, prioritizing clean independent confirmation and inexpensive perturbations.
3. Preserve C001/C002 unopened confirmation evidence; do not spend it on stopped methods.
