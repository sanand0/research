# Experiment 001 process post-mortem

## What worked

- Cross-paper joins exposed a genuinely untested-looking relationship that neither source paper asked.
- Git freezes separated hypothesis choice, analysis design, and outcome access.
- Exact structural reconstruction (143 birds, 90 days, 11,761 bird-days) caught several interpretation errors early.
- Multiple optimizer checks prevented accepting an L-BFGS zero-variance artifact.
- Known-signal validation caught a scientifically bad residualized spatial phenotype that ordinary code checks would have accepted.
- Specification and leave-one-out checks showed the primary null was stable rather than driven by one convenient fork or bird.
- Independent-replication scouting began immediately after a null instead of searching the same dataset for a significant substitute.

## What failed and what changed

1. **Novelty search too narrow initially.** The first temperature→timing idea had already been tested by another paper on the same population. New rule: search by population, authors, season, instrumentation, and variables, not only focal-paper title.
2. **Outcome file physically present pre-freeze.** Labels were not inspected, but procedural blinding is weaker than access control. New rule: where feasible, keep only IDs + hashes until freeze.
3. **Exact source environment unavailable.** No R/MCMCglmm locally. We used Python approximations and validated them against published coefficients instead of presenting them as exact replication.
4. **L-BFGS false convergence.** It collapsed random-effect variance to zero. New rule: compare independent optimizers and known variance/repeatability targets before trusting a mixed model.
5. **Hard-coded plotting row misread as analytic N.** Author code appended a temporary 11,762nd row. New rule: trace data lineage through plotting mutations before using array dimensions as sample-size evidence.
6. **Residual means were not valid substitutes for hierarchical binary random effects.** The naive off-territory phenotype missed a known survival signal. New rule: every derived scientific phenotype should reproduce at least one source-paper signal or parameter if such a target exists.
7. **Stochastic validation was initially non-reproducible.** `fit_vb()` uses its own RNG. Global NumPy seeding did not fix it; explicit `fit_vb(rng=20260908)` did. New rule: rerun stochastic outputs and compare file hashes before calling them reproducible.
8. **Replication feasibility was briefly inferred from the wrong table.** `Birds_Yr1.csv` has 23 attribute rows, but the paper reports 74 Year-1 RFID birds. New rule: distinguish metadata subsets from the observational population and reconcile every feasibility count with the source paper.
9. **Dryad access is blocked by human confirmation.** API/file-stream attempts reach AWS WAF. We will not bypass CAPTCHA/WAF; acquisition remains an external blocker.
10. **Replication outcome semantics changed with sampling design.** Amherst used 10 feeders across two tracts in Year 1 but eight feeders in one tract in Year 2. New rule: define observable outcomes from actual detection opportunity; call this `next-winter redetection`, not survival.

## Method upgrades for Latent Experiments

A future agent should enforce these gates:

`source discovery → analysis inventory → latent cross-paper join → prior-art search → predictor seal → known-signal validation → bit-reproducibility check → outcome freeze → primary test → stability/influence checks → independent replication protocol → staged outcome unseal`

The most important upgrade is **epistemic-firewall engineering**: the system should make accidental outcome access difficult, not merely instruct the agent to behave.
