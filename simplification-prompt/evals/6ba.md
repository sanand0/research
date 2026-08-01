### Component table

| Explicit requirement                           | Response A                                                                                                                          | Response B                                                                                                                                                            |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Practical benchmark design                     | **Present** — specifies a local SQLite/JSON environment, task schema, solver, verifier, adaptive run, and minimum implementation.   | **Present** — specifies a seeded micro-organization, witness-based generator, verifier, adaptive evaluator, audit bundle, and minimum implementation.                 |
| Automatically becomes harder as models improve | **Present** — difficulty vectors, saturation thresholds, mutation-based hardness miner, and new bands.                              | **Present** — online difficulty calibration, frontier-targeted generation, failure-driven mutations, and generator-ceiling escalation.                                |
| Cheap to run                                   | **Present** — deterministic local tools, exact tests, no judge model, 40-task cap, and adaptive selection.                          | **Present** — local verification, sequential stopping, 16–48 episodes, and targeting only informative difficulty ranges.                                              |
| Auditable                                      | **Present** — records seeds, traces, state changes, tests, configuration, and replayable scoring.                                   | **Present** — records initial/final state, deltas, traces, witness, predicate-level verdicts, seed commitment, and replay script.                                     |
| Resistant to memorization                      | **Present, with an acknowledged limit** — private runtime seeds, composition holdouts, future randomness, and counterfactual twins. | **Present, with an acknowledged limit** — runtime causal structures, private HMAC-derived seeds, new operators, interface variation, twins, and container separation. |
| Resistant to verbosity                         | **Present** — prose earns no points; final answers are capped or schema-constrained.                                                | **Present** — prose is ignored or tightly capped and excluded from the core score.                                                                                    |
| Resistant to superficial completion            | **Present** — requires goal predicates, invariants, forbidden-event checks, and verified state changes.                             | **Present** — adds final-state, invariant, trace, provenance, temporal, retry, and counterfactual checks.                                                             |

### A-only

* Defines six explicit task families, including goal changes and rejection of conflicting or unsafe instructions.
* Uses discrete difficulty bands and activates a new band only after two consecutive saturation results above an 80% pass threshold.
* Proposes testing candidate frontier tasks on three strong agents and retaining tasks with 30–70% pass rates.
* Requires 90% reliability and zero severe violations for ranking eligibility, with efficiency used only as a tie-breaker.
* Keeps 20% of composition operators private for one evaluation round, then releases them.
* Gives a fixed default allocation of ten anchors, twenty adaptive tasks, and ten confirmation tasks.
* Provides a concrete starter size of 24 templates and eight difficulty bands.

### B-only

* Constructs each task from a hidden witness plan and dependency graph before rendering the request, rather than merely checking generated tasks afterward.
* Explicitly randomizes causal structure, not just entity values or wording.
* Includes temporal dynamics, irreversible actions, optimization, schema novelty, deterministic dialogue, and constraint coupling as independent difficulty dimensions.
* Updates an agent-capability posterior after every episode and stops when its confidence interval is sufficiently narrow.
* Maintains a failure archive and creates controlled mutations targeting observed failure mechanisms.
* Reports both Frontier-50 and Frontier-80, with Frontier-80 representing reliable rather than occasional capability.
* Checks causal trajectory properties such as idempotent retries, whether updated information was observed before action, and whether approval preceded irreversible action.
* Derives seeds with HMAC from the secret, model identity, run, and episode index, preventing post hoc episode selection while allowing exact regeneration.
* Separates stable anchors, adaptive frontier tasks, and novel probes, and describes how to link scores when the generator changes.
* Separates fixed-harness model evaluation from open-system agent evaluation.
* Uses sequential stopping for cost control and defines concrete early-stop conditions.
* Provides a predicate-by-predicate machine-readable verdict and releases the hidden witness after execution.
* Explicitly distinguishes legitimate learning of the task generator’s underlying competence from memorization of unknown instances.

### Per-criterion winners

1. **Correctness — B.** A calls a SHA-256 hash a way to “sign” the manifest, although an unkeyed hash is not a signature, and its claim of “no fixed maximum level” overlooks the finite expressiveness of its generator and solver. B explicitly recognizes a generator ceiling and uses a proper commitment and HMAC derivation scheme.

2. **Key drivers — B.** B identifies causal-structure novelty, constraint density, temporal effects, reversibility, policy exceptions, observability, and model-versus-scaffold confounding. A relies more heavily on generic counts such as tool calls, decoys, constraints, and hidden state.

3. **Mechanism — B.** B explains the complete loop from witness-plan generation through feature-based difficulty prediction, posterior updating, targeted mutation, trace verification, score linking, and sequential stopping. A specifies the components but leaves more of their interaction implicit.

4. **Caveats — B.** B flags literal unsaturability as impossible, acknowledges generator familiarity, warns that adaptive benchmarks become moving targets, accounts for generator ceilings, and separates model capability from scaffold capability. A acknowledges benchmark-specific training but otherwise makes stronger claims than its finite generator supports.

5. **Calibration — B.** B consistently limits claims to contamination resistance and a moving empirical frontier, with confidence intervals and explicit uncertainty updates. A’s “no fixed maximum level” and pass-rate filtering based on only three agents are insufficiently calibrated.

6. **Actionability — B.** Both are implementable, but B resolves more decisions that would otherwise cause an incorrect implementation: witness construction, task linking, seed derivation, causal trace checks, stopping rules, track separation, and exact audit artifacts.

**Overall: B**

**Confidence: high**
