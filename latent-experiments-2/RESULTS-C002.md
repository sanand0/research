# C002 — Allen V1 criticality / MR applicability

Status: **STOPPED AFTER ONE DISCOVERY MOUSE; CONFIRMATION UNOPENED**

C002 asked whether long, spike-resolved individual-mouse V1 recordings could distinguish genuine near-critical population dynamics from critical-looking behavior caused by sampling/analysis choices, using a subsampling-aware multistep-regression (MR) estimator rather than relying only on avalanche power laws.

## Evidence boundary

- Dataset: Allen Visual Coding Neuropixels.
- Primary unit: mouse/session.
- Primary session type: `functional_connectivity`, chosen from design metadata before spike-value access because it contains a standardized ~30-minute spontaneous block.
- Metadata eligibility: >=32 Allen `quality=good` VISp units.
- Frozen eligible sets: 12 discovery + 12 confirmation mice.
- Spike values accessed: **discovery session 767871931 only**.
- Confirmation spike values accessed: **none**.
- Eleven other eligible discovery mice also remain unopened.

The holdout is procedural, not a security boundary.

## Calibrated estimator

`mrestimator==0.2.0`, 4-ms bins, lags 1..200, with a predeclared applicability gate of exponential-fit R² >= 0.90. Raw `m` is not interpreted when the gate fails.

Aggregate/binomial event-subsampling calibration:

- true m=.8, .98, .99: 45/45 fits applicable across 100%, 50%, 25% sampling; mean absolute errors roughly .0015-.0028;
- independent Poisson null: 0/5 applicable, despite meaningless raw `m` values sometimes near 1.

Result: `results/c002_mr_calibration.json`, SHA-256 `4cbdc7249d6f60ac9aa9025a8add628af7b58d5930b8f4d38c04cdbff65e492b`.

## First discovery mouse

Session 767871931 has 201 good VISp units and a continuous spontaneous interval >1800 s. The guarded analysis uses exactly 1800 s.

Primary deterministic subset:

- 32 units: raw m=.9633, R²=.8807 -> **not applicable**;
- nested 16 units: raw m=.9885, R²=.8799 -> not applicable;
- nested 8 units: raw m=.9966, R²=.6861 -> not applicable.

Ten alternative fixed 32-unit subsets from the same mouse: 7/10 applicable, 3/10 fail. Applicable raw m estimates span about .968-.990. Thus whether the single-timescale MR model is applicable depends materially on which neurons are observed.

Result: `results/c002_session_767871931.json`, SHA-256 `58d6b672550ece5843ea98d2643ab34b14b3c5c21aabe0552fea1873bc863365`.

This is **not** evidence that V1 is or is not critical; rejected fits make the corresponding `m` uninterpretable.

## Post-first-mouse method stress tests

These were specified after seeing one discovery mouse, so they are methodological diagnostics, not confirmatory scientific evidence.

### Fixed-neuron observation + static heterogeneity

A 512-neuron, eight-module branching observation model uses fixed neuron identities, lognormal within-module firing weights, and random fixed 32-neuron subsets.

- common true m=.98 despite heterogeneous rates: 30/30 applicable, R² >= .9974, m=.9767-.9819;
- mixed static module timescales m=.85... .995: 30/30 applicable, R² >= .9866.

Result SHA-256: `3757409dad78d6ac79e0b41f2f2d09277a4949c473b0e80f9f0fd37e5cfdb570`.

### Simple state-switch stress tests

Three 300-s state segments were tested with global `.90 -> .99 -> .90` changes and asynchronous module switches.

- global switches: 30/30 full-session fits applicable, R² >= .9860;
- asynchronous switches: 30/30 applicable, R² >= .9902;
- all 180 within-state segment fits across both scenarios also pass.

Result SHA-256: `6e0150da212fd74d65e0c5a4bdb7244bafe84b3dfabdc8a2e08d460b4af5ba20`.

These simple departures from homogeneous stationarity therefore do not reproduce the real mouse's low-R²/subset-dependent failures.

## Decision

**STOP C002 before any further discovery or confirmation spike access.**

The broad criticality/subsampling debate is mature. The first real mouse violates the calibrated single-timescale MR observation model in a way not reproduced by the bounded branching-family stress tests. Continuing would require inventing progressively richer dynamical models after seeing the real-data failure. That is adaptive rescue rather than a clean latent experiment.

Useful result: a supposedly subsampling-robust estimator can still fail at the **model-applicability** layer under real fixed-neuron recordings; calibration must test whether the assumed correlation form is valid, not merely whether the estimator is unbiased when its model is true.

## Reproducibility

All four stochastic/result-producing C002 scripts were rerun unchanged with explicit seeds/inputs and reproduced byte-identical result hashes:

- aggregate MR calibration: `4cbdc724...e492b`;
- first Allen mouse: `58d6b67...63365`;
- fixed-neuron calibration: `3757409...db570`;
- state-switch calibration: `6e0150d...5ba20`.

Tests cover discovery/confirmation guards, deterministic subset selection, synthetic recovery/null rejection, and simulation helper contracts.
