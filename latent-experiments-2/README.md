# Latent Experiments 2

## Objective

Build and demonstrate an agent-driven scientific loop that starts from a consequential unexplained observation or disagreement, commits a discriminating prediction before confirmation access, tests it against independent evidence, preserves failures, and leaves reusable FOSS tooling.

This project is separate from `latent-experiments/`. The pilot is evidence about failure modes, not the operating protocol. See `PILOT-LESSONS.md`.

## Current status

**C001 (repeated TEM-1 deep-mutational-scanning maps) stopped before confirmation. C002 (neuronal criticality vs subsampling/analysis artifact) is next for feasibility.**

C001 asked whether disagreements among same-protein DMS maps were mostly calibratable assay scale/noise or reproducible biological context dependence. Firnberg 2014 + Stiffler 2015 were discovery evidence; Jacquier 2013 was reserved confirmation and Deng 2012 a method-contrast control. **Jacquier and Deng scores remain unopened.**

### What C001 established

- ProteinGym discovery access is operationally excellent: range reads retrieved only the chosen assays; 4,782 missense mutations overlap Firnberg and Stiffler.
- ProteinGym leaves the chosen source scores numerically unchanged: Firnberg `linear`; Stiffler fitness at 2500 µg/mL ampicillin.
- The maps are strongly rank-correlated (Spearman ~0.937) but are on different numerical scales, so raw score subtraction is invalid.
- Primary literature already establishes selection-strength-dependent TEM-1 mutational effects; the broad “does context matter?” question is therefore not a good new scientific target.
- A sharper position-residual detector **fails empirical calibration**. After position-blocked monotone mapping, Firnberg→Stiffler residual position eta² is 0.215. Five actual same-condition Stiffler replicate pairs produce eta² 0.186–0.454 and all falsely reject the nominal residual-permutation null. The cross-study pattern therefore sits inside observed technical replicate structure.
- A known large context shift (Stiffler 39→2500) gives eta² 0.526, so the detector can see large selection changes; it simply cannot justify the subtler cross-study claim.
- `results/c001_calibration.json` reproduced exactly across two stochastic runs; SHA-256 `2eae5d560d0683778176677c167aa79a39458788556c0f1f249c7da6ebdb5e8b`.

Reusable lesson: **a cross-assay residual null must accept real same-condition replicate pairs before any structured residual is called biological.** Residual permutation alone was far too optimistic because technical errors are themselves position-structured.

## Candidate ranking

1. **C002 — neuronal criticality under subsampling.** Competing explanations: genuine near-critical cortical dynamics versus critical-looking avalanche statistics induced by subsampling/binning/analysis choices. Consequential, experimentally discriminable, and excellent live-demo potential. First Zenodo control-code probe timed out, but Allen public electrophysiology offers an independent and well-maintained evidence ecosystem.
2. **C003 — ecological Taylor's law.** Competing explanations: biological interactions/environmental stochasticity versus feasible-set/sampling constraints. Cheap interventions on census length and constrained randomization, with small open datasets; however the mechanism debate is mature and novelty space may be narrower.
3. **Fresh scout if C002/C003 fail cheap gates.** Do not preserve a candidate merely to keep activity going.

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

Current conference requirements checked 2026-09-09: 30-minute in-person talk including Q&A; FOSS/OSI-licensed focus; CFP closes 19 Oct 2026 23:59 IST. AI/data-driven discovery and reproducibility are plausible tracks. The eventual live loop should let the audience choose among prespecified discriminating tests, commit a prediction, and reveal a fresh computation without relying on proprietary software.
