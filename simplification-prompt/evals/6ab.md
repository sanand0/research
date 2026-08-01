### Component table

| Explicit requirement                           | Response A | Response B | Evidence                                                                                                                                                                                                         |
| ---------------------------------------------- | ---------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Design a practical agent benchmark             | Present    | Present    | Both specify a local tool-using work environment, generated tasks, deterministic scoring, adaptive testing, and an MVP.                                                                                          |
| Automatically becomes harder as models improve | Present    | Present    | A continuously generates items near the estimated capability frontier and mutates recurring failures. B activates mined difficulty bands after repeated saturation.                                              |
| Remains cheap to run                           | Present    | Present    | Both use local deterministic environments, exact tests, adaptive item selection, and roughly 40-task maximum runs.                                                                                               |
| Remains auditable                              | Present    | Present    | Both retain seeds, traces, state changes, tests, configuration, and replay artifacts. A additionally specifies predicate-level verdicts, initial/final databases, state deltas, and a released witness solution. |
| Resists memorization                           | Present    | Present    | Both use private runtime seeds, procedural composition, post-run seed revelation, and counterfactual twins. B additionally withholds new composition operators temporarily.                                      |
| Resists verbosity                              | Present    | Present    | Both exclude explanatory prose from the main score and cap final responses.                                                                                                                                      |
| Resists superficial task completion            | Present    | Present    | Both require verified state changes, invariants, forbidden-action checks, and resource compliance rather than self-reported completion. A adds trace-derived causal and retry checks.                            |

### A-only

* Tasks are generated from a hidden valid witness plan, then checked by a deterministic reference solver; the witness is released afterward for auditing.
* Difficulty includes policy depth, temporal dynamics, reversibility, constraint coupling, optimization, schema novelty, context pressure, and interaction—not merely tool-call horizon and decoys.
* A failure archive produces controlled mutations of observed weaknesses, such as moving one decisive fact, changing an exception, or requiring safe retries.
* It reports both Frontier-50 and Frontier-80, emphasizing reliable rather than occasional success.
* Verification is explicitly divided into final-state predicates, global invariants, and trace-derived checks.
* Trace checks test whether retries were idempotent, updated records were observed before action, and approvals preceded irreversible actions.
* Counterfactual twins are scored jointly, requiring both success and the appropriate change in action.
* Anchor, frontier, probe, reliability-repeat, and twin allocations are separated, with procedures for linking generator versions longitudinally.
* Fixed-harness and open-system tracks are separated to avoid mixing model capability with scaffold quality.
* It specifies sequential stopping based on confidence intervals and several early-stop conditions.
* It defines a detailed per-episode audit bundle, including initial and final databases, state deltas, resource usage, witness, and replay script.
* Its MVP identifies concrete task operators and recommends composing three to eight of them.

### B-only

* The hardness miner is activated only after two consecutive saturation results, with 80% pass rate as the threshold.
* Candidate new-band tasks are sampled on three strong agents and retained when pass rates are 30–70%.
* It uses ten anchors, twenty adaptive tasks, and ten confirmation tasks, with confirmation tasks one band below estimated capability.
* It sets explicit leaderboard requirements of 90% reliability and zero severe violations, using efficiency only as a tiebreaker.
* It temporarily keeps 20% of composition operators private for one evaluation round.
* It suggests deriving public-leaderboard seeds from a future public random value.
* Its task families explicitly include adapting to goal changes and rejecting conflicting or unsafe instructions.
* Required textual reports can be validated against a strict JSON schema.
* It proposes permanent benchmark versions and a hashed manifest.

### Per-criterion winners

1. **Correctness — A**

A avoids B’s claim that the process gives the benchmark “no fixed maximum level.” Any fixed generator, task grammar, solver, and environment has a capability ceiling; A explicitly recognizes a “current generator ceiling” and requires extending the generation range. Both otherwise use technically sound evaluation principles.

2. **Key drivers — A**

A identifies the factors that determine real agent difficulty: causal dependency structure, policy exceptions, distributed observations, temporal changes, irreversibility, tool faults, coupled constraints, and optimization. B’s `H/B/C/P/F/G/T` vector is useful but omits several consequential dimensions or compresses them into broad counts.

3. **Mechanism — A**

A explains the full causal chain: construct a solvable witness, generate a world around it, estimate item difficulty, select near the ability frontier, mutate observed failures, and verify state plus trajectory. B specifies a workable procedure but gives less detail on how mutations produce meaningful rather than merely longer tasks.

4. **Caveats — A**

A addresses ambiguity, impossible generated tasks, moving-target comparability, generator-version changes, scaffold confounding, accidental success, irreversible actions, stale observations, severe violations, and the eventual generator ceiling. B recognizes benchmark-specific training and composition leakage but treats fewer operational failure modes.

5. **Calibration — A**

A begins by stating that no finite benchmark is literally unsaturable and narrows the achievable claim. B also acknowledges benchmark-specific training, but later overstates that its miner creates “no fixed maximum level.”

6. **Actionability — A**

Both could be implemented, and B’s fixed task counts and band rules are especially straightforward. A is more likely to produce a correct implementation because it specifies the task-construction method, verifier layers, adaptive stopping, audit schema, comparison tracks, and concrete MVP operators.

### Overall: A

### Confidence: high
