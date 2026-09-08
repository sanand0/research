# Latent Experiments 2

## Objective

Build and demonstrate an agent-driven scientific loop that starts from a consequential unexplained observation or disagreement, commits a discriminating prediction before confirmation access, tests it against independent evidence, preserves failures, and leaves reusable FOSS tooling.

This project is separate from `latent-experiments/`. The pilot is evidence about failure modes, not the operating protocol. See `PILOT-LESSONS.md`.

## Current leading question

**How much of disagreement between deep-mutational-scanning maps of the same protein is merely assay scale/noise, and how much is reproducible biological context dependence?**

TEM-1 beta-lactamase is the first case because ProteinGym currently contains four independent single-mutant maps (`Deng_2012`, `Jacquier_2013`, `Firnberg_2014`, `Stiffler_2015`) on the same protein, largely under beta-lactam selection. If a monotone calibration makes maps interchangeable, one DMS landscape can reasonably serve as a protein-level ground truth. If specific mutations or regions disagree reproducibly beyond calibration/noise, assay context is part of the scientific object and should be modeled explicitly.

Evidence roles are frozen before score access:

- discovery: Firnberg 2014 + Stiffler 2015;
- reserved confirmation: Jacquier 2013;
- calibration / method-contrast control: Deng 2012, whose selection/readout differs more strongly;
- no mutation-level `DMS_score` values have been inspected as of initialization.

## Shortlist

1. **C001 — repeated DMS maps / TEM-1.** Competing explanations: monotone assay scale + measurement noise versus genuine environment/readout-specific mutational effects. Cheapest discriminator: overlap the same single mutants, fit calibration only on discovery maps, freeze residual/sign-flip claims, then test them on Jacquier. Strong access and reuse across 24 repeated-protein groups in ProteinGym.
2. **C002 — neuronal criticality under subsampling.** Competing explanations: genuine near-critical cortical dynamics versus critical-looking avalanche statistics induced by subsampling/analysis. Scientifically consequential and excellent live-demo potential, but the first LocalMCP access probe to a 14.8 KB Zenodo control bundle timed out after 30 s; Allen data remain an alternative route.
3. **C003 — ecological Taylor's law.** Competing explanations: biological interactions/environmental stochasticity versus feasible-set/sampling constraints. Cheap interventions on census length and constrained randomization are possible, with small open datasets; however, the mechanism debate is mature and novelty space is narrower.

## Current evidence

- ProteinGym's public S3 bucket is directly reachable from LocalMCP. Its substitutions parquet is 92,652,794 bytes; metadata reference CSV is 208,734 bytes.
- The metadata has 24 UniProt proteins represented by multiple assays, comprising 55 assays. TEM-1 (`BLAT_ECOLX`) has four maps with 989–4,996 single mutants each.
- Public literature already establishes that DMS shifts can be biological or noise-driven, so this project will not claim novelty from absence of search hits. The novelty target, if any, must be a specific frozen residual pattern plus independent confirmation.

## Resource budget and first decision checkpoint

Until the first scientific checkpoint:

- FOSS/local computation only; no paid APIs or cloud compute.
- <= 2 GB downloaded source data total and <= 10 GB transient cache.
- <= 30 CPU-minutes for any single bounded analysis; no persistent/background jobs.
- Commit only code, metadata, small results, and documentation; raw/third-party data stay ignored.
- Checkpoint after discovery-map calibration + null/injected-effect calibration, before opening Jacquier confirmation scores.

Continue only if discovery data show enough overlapping mutations and measurement dynamic range to distinguish scale/noise from structured disagreement, and the proposed frozen claim has a plausible confirmation test that could change the conclusion.
