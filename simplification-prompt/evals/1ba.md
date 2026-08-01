## Component table

| Explicitly requested component                   | Response A                                                                                                                                                     | Response B                                                                                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Concrete benchmark task(s)                       | **Present** — proposes request-to-micro-product, paper-to-demo, and workplace state-change tasks.                                                              | **Present** — proposes Ship the Release, Autograder Duel, and Reproduce and Improve.                                                       |
| Relevant to the user’s agent work                | **Present** — tests coding, research, tool use, planning, debugging, and verification against real backlog items.                                              | **Present** — directly connects tasks to GenAI demos, TDS autograders, internal LLM workflows, and research implementation.                |
| Easy to evaluate                                 | **Present** — hidden tests, final-state checks, repeated runs, artifact checks, and hard gating on task success.                                               | **Present** — acceptance tests, regression tests, end-to-end scripts, hidden adversarial tests, hard failures, and a limited human rubric. |
| Unlikely to saturate                             | **Present** — private rolling tasks plus adjustable tools, horizon, failures, ambiguity, and dynamic information.                                              | **Present** — renewable private tasks, an expandable human-effort ladder, longer release-level work, and controlled difficulty dimensions. |
| Measures growing capability comparably over time | **Partial** — rolling tasks preserve difficulty, but changing the task population without calibrating difficulty makes scores across releases less comparable. | **Present** — H80 explicitly maps capability to the human-duration frontier at which the system remains reliable.                          |
| Gives an immediately usable benchmark design     | **Present** — recommends ten fresh request-to-product instances per important release.                                                                         | **Present** — recommends twelve Ship the Release tasks across three duration bands plus five Autograder Duel tasks.                        |

## A-only

* A proposes a simulated **workplace state-change task** involving messages, files, calendars, policies, restricted information, and verification of the final database state.
* A explicitly counts **unsupported claims** and **unnecessary file or state changes**.
* A proposes the multiplicative score `task success × reliability × efficiency`, with incorrect results forced to zero.
* A explicitly includes **recoverable tool failures** and delayed information as difficulty controls.
* A recommends producing **evidence against every stated requirement** as a required deliverable.
* A uses changing multi-agent opponents as an additional example of saturation-resistant evaluation.

## B-only

* B defines **H80**: the maximum human-sized task duration at which the agent succeeds in 80% of runs.
* B supplies a concrete **human-effort difficulty ladder**, from a short bug fix to a week-scale subsystem.
* B proposes **Autograder Duel**, evaluated by false acceptance, false rejection, exploit survival, runtime, and feedback quality.
* B distinguishes benchmarking the **whole agent system** from controlled model-only comparisons.
* B includes the original regression suite and specifies hard failures for **data corruption, fabricated results, and unsafe irreversible actions**.
* B recommends partial-credit grading for long workflows rather than relying only on binary completion.
* B identifies **harness choice** as a potentially large confound and instructs the evaluator to hold it fixed when comparing models.
* B explicitly discusses the weakness of human-duration calibration when evaluators lack normal project context.
* B provides a concrete initial suite size and distribution.
* B separates an easily graded task family from a more expensive research benchmark with greater headroom.

## Per-criterion winners

1. **Correctness — B**

   Both answers’ cited empirical claims are substantially accurate: A correctly represents Terminal-Bench, τ-bench, OSWorld 2.0, and benchmark-reward risks; B correctly represents the SWE-Bench Pro audit, METR time horizons, Long-Horizon-Terminal-Bench, SWE-EVO, and harness effects. ([arXiv][1])

   B wins because A’s rolling score lacks difficulty normalization: success rates on a new monthly task population do not by themselves measure capability growth. Its multiplication of undefined “reliability” and “efficiency” quantities is also not a well-specified metric. B’s human-duration frontier supplies a more defensible longitudinal scale.

2. **Key drivers — B**

   B identifies the central determinants for this particular problem: real-work relevance, objective outcome verification, repeated-run reliability, task-duration frontier, private renewable tasks, harness control, and expandable requirement interaction. A identifies most of these, but not a stable axis for comparing changing task sets.

3. **Mechanism — B**

   B explains how non-saturation and measurement work: fit success against human task duration, report H80, extend the ladder as systems improve, and hold harness variables constant for model comparisons. A mainly says to replace tasks and increase difficulty, without explaining how scores on successive sets remain comparable.

4. **Caveats — B**

   B flags broken graders, contamination, calibration bias in human-time estimates, regression risk, partial progress, harness effects, unsafe side effects, and the higher expense of research reproduction. A’s main caveats are reward design and avoiding LLM judges; it misses task-distribution drift and system-configuration confounding.

5. **Calibration — B**

   B appropriately distinguishes “probably easiest to evaluate” from “greatest long-term headroom, but more expensive,” and acknowledges limitations in human-time calibration. A overstates that its selected benchmark “will” grow with models despite not defining a comparable difficulty scale.

6. **Actionability — B**

   B gives the stronger operating recipe: task levels, H80, repeated-run protocol, grader components, hard failures, task-capture workflow, difficulty controls, comparison policy, and an initial suite composition. A is usable, but several central choices—especially score normalization and longitudinal comparison—remain unresolved.

## Overall: B

Response A is strong and answers all three core constraints. Response B is better because it adds the missing measurement principle: benchmark an expandable, calibrated capability frontier rather than merely rotating through different hard tasks.

**Confidence: high**

[1]: https://arxiv.org/abs/2601.11868?utm_source=chatgpt.com "Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces"
