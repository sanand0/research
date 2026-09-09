# Project reassessment — what is scientifically worth presenting?

Date: 2026-09-09

## Bottom line

The original goal was stronger than “find an interesting correlation”: have an agent discover something scientifically useful, test it against independent evidence, demonstrate a genuine scientific loop live, and leave reusable open-source tools.

After C001–C014, **there is no independently confirmed new domain-science claim. Do not pretend otherwise.**

The project did, however, generate a coherent and unusually concrete result about **how agentic scientific analysis fails unless it is treated like an experimental instrument that must be calibrated**. That result is better supported than any surviving domain claim and is a strong fit for a scientific-computing audience.

This is a case series, not a random benchmark. The 14 candidates were adaptively selected, so do not report “failure rates of AI science” as population estimates.

## What the project actually demonstrated

### 1. A significant null can be wrong

C001: a cross-assay TEM-1 residual looked highly structured against a permutation null. Real same-condition technical replicates contained as much or more structure. The attractive biological signal disappeared once the null represented the actual experiment.

**General rule:** calibrate against real known-null structure before interpreting synthetic/permuted significance.

### 2. A plausible parameter estimate can be uninterpretable

C002: a subsampling-aware neuronal branching estimator could return near-critical values, but its assumed correlation form failed on real data and depended on which neurons were sampled. Simulation calibration showed that ordinary subsampling/heterogeneity did not explain the failure.

**General rule:** test model applicability separately from estimator bias.

### 3. Positive discovery is not confirmation

C003: a pre-frozen constraint null found extra temporal organization in 2/3 German steppe plots. The same frozen test found 0/5 passes in a separate Danish heath ecosystem. Every raw Taylor exponent was below 2, including all confirmation plots, while the constraint null itself typically predicted values below 2.

**General rule:** a descriptive signature can be real yet mechanistically non-diagnostic; independent confirmation stays failed.

### 4. New data do not imply a new discriminator

C004/C008/C011/C014: several attractive newly released datasets enabled analyses whose exact discriminating experiment had already been performed in current literature.

**General rule:** search for the implied experiment, not merely topic novelty or dataset novelty.

### 5. Open data can omit the variable that matters

C007/C009: rich public datasets could not answer the actual expert disagreement because lesion pathology or an independent same-setting gap observable was absent.

**General rule:** identify the decisive observable before analyzing proxies.

### 6. Matching variable names do not imply matching evidence

C010: discovery and confirmation both contained “SunScan LAI” and destructive LAI, but the confirmation archive averaged one measurement across 50 plots while the other came from five plots. Unit alignment was destroyed.

C012: eight labs shared the same physiology CSV columns, but actual skin-temperature anatomy and heart-rate variables differed enough that a common cross-lab physiological estimand did not exist.

**General rule:** validate measurement semantics and analysis-unit alignment, not just schemas.

### 7. Replication must be calibrated at the replication unit

C012 synthetic calibration initially showed that participant-dominated inverse-variance pooling could be anti-conservative in a multi-lab claim. Treating laboratories as the inferential units produced a calibrated 3.0% null pass rate and 93.9% power for a 0.10 °C common effect under the frozen simulation.

**General rule:** hierarchical data do not create independent replication merely by having many rows.

## Recommended SciPy India 2026 talk direction

### Core proposition

**Treat an AI research agent as an uncalibrated scientific instrument.**

The interesting question is not “can it produce a hypothesis and a p-value?” It obviously can. The useful question is whether we can build a Python/FOSS workflow that makes the agent *earn the right to believe its own result*.

A concise working title:

> **How do you calibrate an AI scientist?**

Alternative, more memorable title:

> **I asked an AI to discover science. It mostly learned when to stop.**

### 30-minute narrative

1. **5 min — The challenge.** Give an agent open papers/data and ask it to discover something useful that was not known to the operator.
2. **12 min — Three scientific loops.** C001 (bad null), C002 (bad applicability), C003 (positive discovery → failed confirmation). These are scientifically different failure modes, not a blooper reel.
3. **6 min — The live gate.** Run a compact prepackaged candidate through claim freeze → calibration → semantic/access check. C012 is excellent because a seemingly standardized eight-lab dataset fails before outcome analysis when the physiology semantics are inspected.
4. **5 min — The reusable protocol.** Evidence roles, empirical nulls, known-positive calibration, unit-of-replication tests, source-level confirmation guards, deterministic reruns, failure ledger.
5. **2 min — What remains unknown.** No benchmark yet proves this agent selects good questions better than a human/baseline. That is the next experiment.

This matches SciPy India's stated audience around scientific computing, research software, AI/ML with scientific flavour, FOSS and open science. The 2026 CFP closes 19 Oct 2026 and talks are 30 minutes including Q&A.

## What not to claim

Do not claim:

- AI cannot discover science;
- a 0/14 confirmation rate for AI (candidate selection was adaptive and several candidates never reached outcomes);
- the Taylor-law analysis disproves biological stabilization globally;
- C012 proves there is no physiological Hue–Heat effect;
- novelty for the individual gate ideas by themselves.

Do claim, with demonstrations:

- this workflow repeatedly prevented specific false or overconfident conclusions;
- failure gates changed actual decisions about whether confirmation evidence should be spent;
- the project contains a complete positive-discovery → independent-confirmation-failure loop;
- the scripts/results are reproducible and FOSS-oriented.

## What reusable open-source material is worth polishing

Do **not** build a platform. Extract only small composable pieces already proven useful:

1. `claim.json` template: discovery/confirmation roles, estimand, stop rule, access state.
2. calibration pattern: known-null + known-positive simulation before outcome access.
3. evidence-access ledger: what was opened and when.
4. verification gate: hashes, deterministic rerun, independent calculation where practical.
5. a short `SCIENTIFIC-LOOP.md` protocol with examples from C001/C003/C012.

These are enough for attendees to reuse without maintaining a framework.

## Path to a genuine positive scientific discovery

The lack of a confirmed domain result is informative about source selection. Existing public datasets are usually designed to answer the authors' questions, not a new discriminator invented later; the missing piece is often exactly the measurement a new mechanism needs.

For a genuine positive result before December, the highest-value next move is **not broader web scouting**. It is one of:

1. obtain an unpublished/under-analysed dataset from a domain collaborator where two independent experimental batches and the decisive observable already exist; or
2. prospectively commission a small replicated experiment whose intervention, mediator and endpoint are chosen *before* collection.

That separates “can the workflow protect us from fooling ourselves?”—already demonstrated—from “can it produce a new scientific fact?”—still open.

## Next experiment on the agent itself

If evaluating scientific agency becomes part of the talk, run it as a separate benchmark rather than inferring from this case series:

- freeze a candidate-generation protocol;
- use a trusted evaluator to hold back source-level confirmation evidence;
- compare the agent with a simple baseline (for example, literature-only human/rule-based shortlist) on the same candidate packets;
- report separately: fraction passing feasibility, calibration validity, discovery hit rate, confirmation rate, and judged scientific usefulness;
- preserve all failed candidates.

This would test question-selection calibration. It is a different experiment from calibrating any one statistical analysis.

## Decision

**Stop broad domain scouting in this repo. Prepare the talk/protocol from the accumulated evidence, while pursuing true domain novelty only through a targeted collaborator/prospective dataset path.**
