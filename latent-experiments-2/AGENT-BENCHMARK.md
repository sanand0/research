# Prospective benchmark: does an agent select better scientific questions?

The C001–C014 case series is **not** a benchmark. Candidate generation was adaptive, several candidates never reached outcomes, and public evidence may have been present in model pretraining.

This document specifies a separate prospective experiment whose unit is a scientific question selected **before** confirmation evidence is opened.

## Primary question

Given identical discovery-only research packets, does a protocol-guided research agent select questions that are more likely than simple baselines to become **independently confirmed and scientifically useful**?

This tests question selection. It deliberately holds analysis execution constant across selectors.

## Evidence source

Use only packets where confirmation evidence is genuinely unavailable to the selector at selection time:

1. unpublished/embargoed collaborator datasets with at least two independent source-level batches/sites/experiments; or
2. prospective experiments in which confirmation is collected after selection.

Do not use a public historical “holdout” as the primary benchmark and call it blind. Model pretraining and web access make that contamination difficult to exclude.

A trusted evaluator controls confirmation files and source identities until the frozen confirmation stage.

## Benchmark unit: one research packet

Each packet must contain:

- a consequential domain decision/question area;
- primary literature available up to the packet cutoff;
- discovery-source methods and metadata;
- direct measurement definitions and unit identifiers;
- one discovery batch/source available for common execution;
- at least one independent confirmation batch/source held by the evaluator;
- no confirmation outcome leakage in filenames, summaries or metadata.

Target 20–100 MB per packet where practical; hard cap 1 GB unless justified.

## Candidate pool

To isolate **selection** from generation, each selector ranks the same frozen candidate pool.

For each packet, before any selector sees it:

1. two domain scientists independently propose plausible questions using methods/metadata/literature but not confirmation outcomes;
2. a mechanical enumerator adds simple treatment×mediator, treatment×context and paired-measurement candidates when supported by the design;
3. a trusted adjudicator deduplicates them and removes questions whose decisive observable is absent or whose exact discriminator is already published;
4. freeze **6–10 candidate questions** per packet.

Each candidate includes only:

- question;
- competing explanations;
- decisive observable;
- independent unit;
- executable discovery/confirmation sources.

The pool is frozen before selector assignment.

## Selection arms

Every arm sees the same packet and candidate pool.

### A. Protocol-guided agent

The research agent may inspect discovery metadata/methods and search literature up to the cutoff. It must apply `SCIENTIFIC-LOOP.md` gates and rank all candidates.

For each candidate it reports:

- rank;
- predicted probability of passing discovery, `p_discovery`;
- predicted probability of confirmation conditional on discovery, `p_confirm_given_discovery`;
- predicted scientific usefulness if confirmed, 1–5;
- expected compute/data cost;
- one-sentence rejection reason if not selected.

It selects one primary candidate per packet.

### B. Simple rule baseline

A deterministic score, frozen before the main study:

- +2 direct intervention or repeated-measure contrast;
- +2 decisive observable directly measured;
- +2 source-level independent confirmation;
- +1 >=10 independent units per source;
- +1 exact measurement semantics match;
- -2 obvious discriminator-specific prior art;
- -2 ambiguous aggregation/unit alignment;
- -1 >1 GB or authenticated live critical path.

Ties are broken lexicographically by candidate ID. The highest score is selected.

This baseline deliberately contains no outcome-aware reasoning.

### C. Random baseline

Uniform random selection from the frozen executable candidate pool, with seed committed before the main run.

### D. Human selector — optional but valuable

A domain scientist or scientifically literate researcher ranks the same candidates under the same time budget and without confirmation access.

Human selectors must report confidence on the same probability scale as the agent.

## Common executor

Selection and execution must be separated.

A **neutral common executor**—the same scripted agent/protocol for all arms—runs every distinct selected candidate. This prevents an apparent selector advantage from actually being better coding, statistics or persistence.

Before discovery outcomes, the executor freezes:

- estimand;
- eligibility;
- primary analysis;
- known-null and known-positive calibration;
- applicability checks;
- multiplicity;
- discovery pass rule;
- confirmation pass rule;
- stop conditions.

If two arms select the same candidate in a packet, execute it once and credit the same result to both.

## Outcome hierarchy

Do not collapse everything into “significant/not significant.”

For every selected candidate report separately:

1. **Executable:** survived prior-art, measurement-semantic and source-alignment gates.
2. **Calibration valid:** known-null/applicability checks passed with adequate known-positive power.
3. **Discovery pass:** frozen discovery rule passed.
4. **Confirmation pass:** frozen independent confirmation rule passed.
5. **Scientific usefulness:** blinded expert panel rating after seeing the question, methods and confirmed effect, but not selector identity.

### Primary endpoint

`confirmed_useful = 1` only when:

- confirmation passes; and
- median blinded expert usefulness rating is >=4 on a 1–5 scale.

This prevents selectors from winning by choosing trivial but reproducible effects.

### Secondary endpoints

- confirmation rate among all selected questions;
- confirmation rate conditional on discovery;
- feasibility rejection rate;
- calibration-failure rate;
- discovery false-lead rate = discovery pass but confirmation fail;
- median expert usefulness among confirmed claims;
- compute/data/time cost;
- probability calibration of selector forecasts.

## Selector confidence calibration

The agent/human must forecast confirmation before outcomes.

Use:

- Brier score for `p_confirm`;
- log loss as sensitivity;
- reliability plot in coarse predeclared bins;
- calibration slope/intercept if sample size supports it.

Do **not** call the proportion of selected questions that fail confirmation “AI FDR.” It is not a multiple-testing false-discovery-rate estimand.

## Main statistical comparison

Because every selector acts on the same packets, treat **packet as the paired unit**.

Primary comparison: protocol-agent versus deterministic rule baseline on `confirmed_useful`.

Use:

- paired difference in mean outcome across packets;
- exact/randomization or paired bootstrap confidence interval;
- McNemar-style discordant-pair test as a binary sensitivity analysis.

Report agent versus random and agent versus human separately. Do not average baselines together.

Cluster expert ratings by packet/candidate where relevant.

## Sample-size plan

Do not pretend the existing 14 adaptive candidates inform efficacy.

### Logistics pilot

Run **12 packets** only to validate:

- contamination controls;
- candidate-pool construction;
- trusted-evaluator workflow;
- common-executor timing;
- outcome prevalence and expert-rating reliability.

The pilot is excluded from the main selector-effect test.

### Main benchmark

Use a new set of packets. Before opening any main confirmation outcome, choose and preregister sample size from pilot-estimated discordance/event rates.

Practical target: **40–60 independent packets**. If collaborators cannot supply enough genuinely independent packets, label the exercise a pilot rather than making a superiority claim.

## Whole-agent calibration controls

Question-selection performance and analysis calibration are different objects. Track both.

Alongside real packets, run a separate canary suite:

- known-null synthetic datasets preserving realistic clustering/missingness;
- known-positive injected effects near meaningful thresholds;
- deliberately invalid model/applicability cases;
- measurement-semantic mismatches.

These canaries test whether the common executor stops correctly. They do not count toward selector scientific-success rates.

## Access and contamination protocol

Trusted evaluator should maintain an append-only manifest:

```json
{
  "packet_id": "P001",
  "discovery_sources": ["D1"],
  "confirmation_sources": ["C1"],
  "confirmation_public": false,
  "confirmation_release_time": null,
  "selector_cutoff": "YYYY-MM-DDTHH:MM:SSZ",
  "confirmation_hash": "..."
}
```

Before selection:

- confirmation bytes are unavailable to selector/executor;
- confirmation filenames and summaries do not reveal outcomes;
- public-web tools are allowed only up to the packet literature cutoff;
- selectors cannot query collaborators about hidden results.

After discovery freeze, evaluator releases only the specific frozen confirmation source.

## Failure handling

No rescue within a packet.

If a selected candidate fails because:

- decisive measurement is absent;
- calibration fails;
- discovery fails;
- confirmation fails;

record that outcome. Do not let the selector choose a replacement after seeing the failure.

This is essential: allowing second choices after failure turns the benchmark into an adaptive search-budget comparison.

## Predeclared benchmark outputs

Publish:

- every packet and frozen candidate pool when embargo permits;
- selector rankings/confidences before outcomes;
- common-executor claim specs;
- access ledger;
- calibration results;
- discovery and confirmation outcomes;
- blinded expert usefulness ratings;
- compute/time usage;
- all failed candidates.

## Decision rule

A claim that the protocol-guided agent selects better questions requires, at minimum:

1. higher primary `confirmed_useful` rate than the deterministic rule baseline on the preregistered paired analysis;
2. no materially worse confirmation-probability calibration;
3. the advantage not being explained only by higher compute/data cost;
4. results surviving a sensitivity analysis excluding packets with any contamination concern.

If the benchmark is too small, report estimates and uncertainty without a superiority claim.

## Why this is different from C001–C014

The existing project tested whether individual analyses deserved belief while candidate selection evolved adaptively. This benchmark freezes the candidate universe, selectors, confirmation evidence, executor and primary endpoint **before** the main outcomes.

That makes “does the agent choose better questions?” an actual scientific question rather than a story inferred from a research diary.
