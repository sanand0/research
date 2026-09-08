# Post-mortem 002 — 2018/19 latent traits and H002

## What worked

- The outcome seal prevented survival from influencing candidate selection.
- Exact public-ID overlap solved 74/79 cohort linkage without fuzzy matching.
- HTTP ZIP-range inspection disproved a false raw-data assumption cheaply: `BCCH_Mob.zip` is WAV stimuli, not RFID events.
- Split-half phenotype validation killed visually attractive random-slope hypotheses before outcome access.
- Hierarchical location-scale modeling separated mean behavior from residual predictability with partial pooling.
- Four-chain and robust-likelihood checks made the H002 phenotype computationally credible before survival was opened.
- Git/hash freezing made it possible to prove the outcome script did not change after unsealing.
- Uncertainty propagation preserved the source paper's spirit while accounting for noisy individual phenotypes.

## Failures and corrections

### Random-effect variance mistaken for trait validity

A visual-cue random-slope model estimated substantial among-bird variance, which initially looked promising. Independent-half slopes correlated negatively. **Correction:** an individual-difference hypothesis must reproduce within the dataset before it can be tested against outcomes.

### Large archive semantics inferred from its name

`BCCH_Mob.zip` was assumed to contain raw RFID data. Its central directory showed it was eight WAV mobbing-call files. **Correction:** inspect archive manifests and README semantics before budgeting download/analysis effort.

### Identifier semantics inferred from appearance

Several short/numeric/hex-looking IDs were initially interpreted as different namespaces. Direct outcome-blind set intersections ultimately showed 74/79 exact overlap. **Correction:** never infer identifier meaning from formatting; prove namespace equivalence through exact joins or explicit crosswalks.

### Survival `NA` semantics differed between R and pandas

R's `ifelse(NA > 0, 1, 0)` preserves `NA`; pandas `(NaN > 0).astype(int)` produces 0. This made repeated rows appear to have changing survival. **Correction:** when reproducing source code across languages, explicitly test missing-value semantics before transforming outcomes.

### Global-only MCMC diagnostics were insufficient

The first H002 diagnostic summarized global parameters while PyMC warned about some bird-level latent effects. **Correction:** convergence gates now include every sampled latent parameter; the four-chain rerun passed max R-hat 1.00 and ESS >=620.

### Tool safety classifier intermittently blocked benign ecology commands

Several LocalMCP calls were blocked before execution, including one run of the committed animal-survival script; an identical minimal retry succeeded. **Correction:** log the failure, reduce the invocation to one narrow operation, retry once, and do not redesign the science around a classifier false positive.

### Over-batched shell commands made small syntax mistakes costly

A DuckDB alias parse error and a pandas merge suffix error each killed a larger verification batch. **Correction:** batch network/discovery work, but keep load-bearing numerical verification in small commands with explicit intermediate contracts.

## Protocol improvements promoted from this experiment

1. **Trait reproducibility gate:** a fitted individual random-effect variance is insufficient; require within-dataset split-half or replicate stability when the trait is supposed to be persistent.
2. **Archive semantics gate:** inspect manifest/metadata before downloading or interpreting large artifacts.
3. **Cross-language NA gate:** test outcome/missing-value transformations when reproducing analysis in a different language.
4. **Full latent convergence gate:** diagnose bird-level/random-effect parameters, not only globals.
5. **Fresh-outcome rule:** after a sealed outcome is unsealed, do not mine new predictor definitions against it; move to replication/fresh data.
