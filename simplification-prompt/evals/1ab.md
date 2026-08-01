## Component table

| Explicitly requested component                       | Response A                                                                                                                   | Response B                                                                                                                                                                            |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Concrete task or task family for benchmarking agents | **Present** — “Ship the Release,” “Autograder Duel,” and “Reproduce and Improve”                                             | **Present** — micro-product, paper-to-demo, and workplace state-change tasks                                                                                                          |
| Relevant to the user’s actual work                   | **Present** — directly connects tasks to GenAI demos, TDS autograders, internal workflows, teaching, and research            | **Present** — business/research requests and working LLM micro-products are relevant, though less specifically tailored                                                               |
| Easy to evaluate                                     | **Present** — hidden tests, regression suite, end-to-end script, hard-failure conditions, and concrete scoring dimensions    | **Present** — hidden tests, database-state checks, artifact checks, and repeated runs                                                                                                 |
| Unlikely to saturate                                 | **Present** — private renewable backlog, expandable human-effort ladder, longer tasks, and adjustable difficulty dimensions  | **Present** — rolling private tasks, changing repositories and APIs, longer horizons, and environmental failures                                                                      |
| Measures capability growth comparably over time      | **Present** — proposes H80/H50, human-duration calibration, reliability, cost, intervention time, and controlled model swaps | **Partial** — records success, reliability, cost, and time, but replacing the suite with ten fresh instances per release risks confounding model improvement with task-set difficulty |

## A-only / B-only

**A-only:**

* Defines **H80** as the central longitudinal measure: the human-sized task horizon completed with 80% reliability.
* Separates complete-system evaluation from controlled model comparison by holding the harness, tools, context strategy, retries, and budget fixed.
* Gives a concrete release-level artifact contract including migrations, documentation, regression preservation, and runnable demonstration.
* Supplies a detailed grading decomposition covering hidden functionality, regressions, usability, requirements, agent-written tests, and unnecessary changes.
* Specifies hard failures for data corruption, fabricated results, unsafe irreversible actions, and build failure.
* Provides a process for converting real backlog items into benchmark instances by freezing repositories before solving them and later incorporating observed failure modes.
* Proposes an **Autograder Duel** with directly measurable false acceptance, false rejection, exploit survival, and feedback quality.
* Proposes a research benchmark requiring reproduction, discrepancy diagnosis, a justified extension, held-out improvement, clean reruns, and compute accounting.
* Gives an initial suite composition across several human-effort levels rather than merely a total instance count.
* Explicitly identifies variation in interacting requirements, mid-task requirement changes, independent verification, and fixed resource budgets as capability dimensions.

**B-only:**

* Proposes a workplace state-change benchmark involving messages, files, calendars, policies, permissions, and final database state.
* Explicitly includes privacy-policy compliance, such as avoiding disclosure of restricted information.
* Counts unsupported claims and unnecessary file or state changes as evaluation metrics.
* Explicitly advises against using an LLM judge as the primary evaluator.
* Suggests generating ten new instances for every important model release.
* Introduces a multiplicative `task success × reliability × efficiency` aggregate score.
* Uses adaptive multi-agent competition, through Agent Island, as an example of a fundamentally dynamic benchmark.

## Per-criterion winners

1. **Correctness — A**

A’s cited quantitative claims are supported, including SWE-Bench Pro’s increase from 23.3% to 80.3%, the estimate that roughly 30% of its tasks were broken, and the reported figures for the other benchmarks. ([OpenAI][1])

B’s statement that “current frontier agents still score below 65 percent” on Terminal-Bench repeats the January 2026 paper result, but was no longer current: by July 2026 the official Terminal-Bench 2.1 leaderboard included verified results of at least 78.4%. ([arXiv][2])

2. **Key drivers — A**

A identifies the factors that determine whether this particular benchmark remains useful: real-work relevance, task horizon, private renewable instances, reliability across runs, objective verification, resource budgets, and harness effects. B identifies several good difficulty knobs but does not adequately address how scores remain comparable when all ten tasks change between releases.

3. **Mechanism — A**

A explains how non-saturation works: measure a capability frontier indexed by estimated human effort, retain shorter anchor levels, and extend the ladder as systems improve. It also explains how hidden tests, regressions, end-to-end execution, and controlled configuration swaps isolate capability. B says to rotate tasks and increase difficulty, but does not explain how to distinguish genuine model progress from an easier or harder monthly sample.

4. **Caveats — A**

A flags contamination, broken benchmark tasks, the dependence of human-time estimates on familiarity with the stack, unsafe failure modes, harness confounding, reliability variance, and evaluation costs. B usefully warns about reward-design errors and LLM judging, but omits the main weakness of its own rolling design: task drift and loss of longitudinal comparability. Neither answer adequately discusses confidence intervals or that three to five runs give a noisy estimate of 80% reliability.

5. **Calibration — A**

A distinguishes its easiest-to-grade proposal from its highest-headroom but more expensive proposal, and qualifies human-duration calibration based on familiarity. B makes stronger claims such as “This must be your main benchmark” and “This benchmark will…grow with the models” without addressing sampling equivalence; its “current below 65 percent” statement is also outdated.

6. **Actionability — A**

A provides an implementable benchmark specification: inputs, outputs, task ladder, test structure, hard failures, scoring dimensions, instance-construction workflow, controlled comparisons, and a proposed initial suite. B is also actionable, especially its final-state benchmark, but its aggregate formula is not operationally defined—“efficiency” has no scale or direction—and replacing every instance at each release weakens comparison.

## Overall: A

Response B contains a valuable addition—the workplace state-change benchmark—which tests broader tool-using agents beyond software delivery. However, Response A better solves the central three-way constraint. Its decisive advantage is not extra detail but the **human-effort capability frontier plus renewable private tasks and controlled system comparisons**, which jointly address relevance, evaluation, non-saturation, and longitudinal measurement.

**Confidence: high**

[1]: https://openai.com/index/separating-signal-from-noise-coding-evaluations/ "Separating signal from noise in coding evaluations | OpenAI"
[2]: https://arxiv.org/abs/2601.11868?utm_source=chatgpt.com "Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces"
