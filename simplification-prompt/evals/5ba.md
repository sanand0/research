## Component table

| Explicit component                                        | Response A                                                                                                                                                                                                                                                  | Response B                                                                                                                                                                                                                                                                                                                 |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Identify a widely accepted belief likely to be wrong      | **Present** — higher average task-success scores are assumed to provide portable agent rankings.                                                                                                                                                            | **Present** — representative end-to-end success is assumed to be the best proxy for production value.                                                                                                                                                                                                                      |
| Establish that the belief is widely accepted by companies | **Partial** — Anthropic supports the claim that small benchmark differences influence deployment, but the cited company survey mainly shows human evaluation is common; it does not establish that companies rely on one portable ranking. ([Anthropic][1]) | **Present** — directly contrasts companies’ productivity and human-effort objectives with their emphasis on output correctness and the low rate of comparison against human or non-agent baselines. The underlying study reports 73% citing productivity but only 38.7% conducting such baseline comparisons. ([arXiv][2]) |
| Use primary evidence against the belief                   | **Present** — cites Anthropic’s infrastructure experiment, a controlled reliability study, the production-practitioner survey, and METR’s randomized productivity trial. ([Anthropic][1])                                                                   | **Present** — cites the practitioner survey, randomized productivity evidence, direct maintainer reviews, real-world session analysis, AlphaEval, and Nubank’s production deployments. ([Metr][3])                                                                                                                         |
| Address the strongest innocent alternative                | **Partial** — gives conditions under which task success can work and describes it as an early filter, but does not clearly formulate the strongest alternative explanation for the contrary evidence.                                                       | **Present** — explicitly considers that task success is valid but existing benchmarks are merely unrepresentative, then tests that explanation against Nubank’s production-derived evaluations.                                                                                                                            |
| Design a cheap test                                       | **Present** — paired shadow replay, existing cases, blocked writes, blinded review, disagreement sampling, and sequential expansion.                                                                                                                        | **Present** — shadow evaluation using existing configurations, tasks, operators, and a small human-only comparison.                                                                                                                                                                                                        |
| Give a decisive falsification rule                        | **Partial** — the statistical rule is explicit, but success on one workflow cannot falsify the broader portability conclusion; reviewing only disagreements also risks missing shared defects relevant to absolute production value.                        | **Partial** — directly tests whether burden-aware variables change selection or prediction, but “more than 10%” is not operationally defined, and 100 cases divided among three or four configurations may be insufficient for a decisive result.                                                                          |

## A-only

* Infrastructure allocation and enforcement alone can shift Terminal-Bench performance by six percentage points, potentially exceeding model leaderboard gaps. ([Anthropic][1])
* Reliability can lag accuracy across consistency, prompt robustness, self-prediction and failure severity; recent evidence covers 15 models over 24 months. ([arXiv][4])
* The challenged belief is specifically about **ranking portability across infrastructure, tools, users and handoff policies**, rather than primarily about economic objective mismatch.
* Production loss explicitly includes delay cost and missed-value cost, not only human review and repair.
* The test uses paired cases, three repeated runs and a confidence sequence, with separate requirements for severe failures and repeat consistency.

## B-only

* Companies commonly cite productivity and reduced human effort as deployment goals while rarely comparing agents with human or non-agent alternatives. ([arXiv][2])
* In METR’s initial holistic review, a 38% test-pass rate coexisted with zero mergeable submissions among 15 reviewed patches; test-passing patches still needed an estimated 26 minutes of repair. ([Metr][3])
* Maintainers rejected roughly half of SWE-bench-passing patches, producing a maintainer score about 24 percentage points below the automated score after normalization. ([Metr][5])
* In 20,574 real-world coding-agent sessions, 90.5% of observed misalignment episodes imposed effort or trust costs, and 91.49% of visible resolutions required user correction. ([arXiv][6])
* AlphaEval found a concrete case in which aggregate-score ordering differed from domain-weighted economic-value ordering. ([arXiv][7])
* Nubank provides a positive counterexample: offline evaluation predicted online outcomes when evaluation included self-service, customer satisfaction, handoff and fallback behavior. ([arXiv][8])
* The proposed test measures operators actually taking outputs to completion and includes a human-only baseline, allowing direct estimation of net human time saved.

## Per-criterion winners

1. **Correctness — B.** B’s evidence more directly supports its stated conclusion: the survey demonstrates an objective–evaluation mismatch, and the maintainer studies directly measure the work hidden behind apparent success. A’s individual empirical claims are largely accurate, but its inference that companies generally assume a single ranking is portable is less directly established. ([arXiv][2])

2. **Key drivers — B.** B identifies the variables that determine production value in this question: human effort removed, verification and repair burden, handoffs, downstream acceptance, costs and failure loss. A’s infrastructure and stochastic-reliability factors matter, but they are only some ways an evaluation ranking can fail.

3. **Mechanism — B.** B explains a coherent causal path: nominally successful output creates review, correction and integration work; those costs consume or reverse the expected productivity gain, so success rate and business value can rank systems differently. The METR repair and maintainer-review results directly illustrate this mechanism. ([Metr][3])

4. **Caveats — B.** B presents the strongest favorable case for conventional evaluation—Nubank’s production-derived offline evals—and explains precisely why that evidence supports calibrated workflow evaluation rather than raw success as a sufficient statistic. It also separates coding-specific causal evidence from broader observational evidence. ([arXiv][8])

5. **Calibration — A.** A more carefully limits its conclusion to a default hypothesis, states that some companies may satisfy the necessary conditions, lists study limitations, and defines falsification separately for one workflow and for the broader claim. B’s statement that human work eliminated is the economically relevant unit for “most enterprise agents” is broader than its evidence, since some deployments optimize customer value, revenue or risk instead.

6. **Actionability — A.** A’s paired design controls case difficulty, repeated runs test instability, blinded disagreement review reduces human cost, and sequential sampling avoids committing to a fixed large sample. B measures the better business outcome, but allocating only 100 cases across three or four configurations and using an undefined 10% prediction threshold makes its decision rule less reliable.

## Overall: B

B gives the stronger answer because its central belief is better demonstrated as an actual company-evaluation mistake, its evidence more directly connects evaluation scores to hidden production costs, and its innocent alternative is both stronger and addressed with a genuine positive deployment case. A supplies the better experimental design and is somewhat better calibrated, but its evidence does not establish its claimed widespread belief as directly.

**Confidence: high**

[1]: https://www.anthropic.com/engineering/infrastructure-noise "Quantifying infrastructure noise in agentic coding evals \ Anthropic"
[2]: https://arxiv.org/html/2512.04123v1 "Measuring Agents in Production"
[3]: https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/ "Research Update: Algorithmic vs. Holistic Evaluation - METR"
[4]: https://arxiv.org/html/2602.16666v3 "Towards a Science of AI Agent Reliability"
[5]: https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ "Many SWE-bench-Passing PRs Would Not Be Merged into Main - METR"
[6]: https://arxiv.org/abs/2605.29442?utm_source=chatgpt.com "How Coding Agents Fail Their Users: A Large-Scale Analysis of Developer-Agent Misalignment in 20,574 Real-World Sessions"
[7]: https://arxiv.org/html/2604.12162v1 "AlphaEval: Evaluating Agents in Production"
[8]: https://arxiv.org/html/2606.08867v1 "Building Customer Support AI Agents at 100M-User Scale: An Evaluation-Driven Framework"
