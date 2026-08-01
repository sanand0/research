## Component table

| Explicit component                                | Response A                                                                                                                               | Response B                                                                                                                                                                                           |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Identify one widely accepted belief               | **Present** — success rate is treated as the best proxy for production value                                                             | **Present** — average task-success rank is treated as portable across operating conditions                                                                                                           |
| Establish that the belief is widely accepted      | **Present** — connects deployment motives, evaluation practice, and lack of baseline comparisons                                         | **Partial** — cites the dominance and deployment use of task-success scores, but the production survey does not directly show that firms assume rankings transfer across environments                |
| Use primary evidence against it                   | **Present** — randomized productivity trial, maintainer reviews, production-session data, company-sourced benchmark and deployment study | **Present** — controlled infrastructure experiment, reliability study, production survey and randomized productivity trial                                                                           |
| Explain the mechanism of error                    | **Present** — success scores omit review, repair, integration, handoff and failure costs                                                 | **Present** — scores conflate the model with infrastructure, harness, stochastic reliability and human-control policy                                                                                |
| Address the strongest innocent alternative        | **Present** — production-derived task evaluation may work when calibrated to workflow and business outcomes                              | **Partial** — describes task success as an initial filter under ideal conditions, but this mostly modifies the claimed practice rather than offering a strong competing explanation for the evidence |
| Design the cheapest decisive test                 | **Present** — reuse representative cases, existing configurations and ordinary operators in shadow mode                                  | **Present** — paired shadow replay with sequential sampling and selective review                                                                                                                     |
| State an explicit falsification condition         | **Present** — pass-rate winner must also maximize net value, with workflow variables adding no useful prediction                         | **Present** — offline winner must show decisively lower production loss, no worse severe failures and equal or better consistency                                                                    |
| Ensure the test measures the claimed failure mode | **Present** — directly measures remaining human effort and net value                                                                     | **Partial** — shadow outputs and selective review may not reveal actual human repair, delay, escalation or common-mode defects                                                                       |

## A-only

* The economically relevant quantity is “autonomous surplus”: accepted-work value minus review, repair, clarification, handoff, rework, compute and expected failure loss.
* Companies report adopting agents mainly to reduce human effort, yet only 38.7% compare against a human or other non-agent baseline. The study surveyed 306 practitioners and used 86 deployed/pilot systems for its main results. ([arXiv][1])
* In a small holistic review, none of 15 agent pull requests was mergeable as submitted; test-passing patches still required an estimated 26 minutes of repair. ([Metr][2])
* In a larger blinded study of 296 patches, maintainer acceptance was about 24 percentage points below normalized automated scores. ([Metr][3])
* In 20,574 real coding-agent sessions, 90.5% of identified misalignment episodes imposed effort or trust costs, and 91.49% of visible resolutions required explicit correction. ([arXiv][4])
* Economic weighting can produce a different ranking from aggregate benchmark scores. ([arXiv][5])
* Nubank provides a concrete innocent alternative: production-derived offline evaluation correlated with online satisfaction and self-service outcomes. ([arXiv][6])
* The distinction between distribution mismatch and objective mismatch: representative tasks fix the former but not necessarily the latter.
* The test includes a human-only baseline and directly calculates net human minutes saved.

## B-only

* An agent score is a property of the whole workflow—model, harness, tools, infrastructure, user and handoff policy—not simply the model.
* Anthropic held model, harness and tasks constant while changing resources; Terminal-Bench success shifted by six percentage points. ([Anthropic][7])
* Reliability must include consistency, robustness to perturbations, predictability and bounded failure severity; these improved much less than accuracy across 15 models and 24 months of releases. ([arXiv][8])
* Human-control policy is explicitly treated as part of the evaluated system.
* Production loss includes delay, missed-value cost and severity-weighted failure cost, not just correction and compute.
* The experiment repeats every agent run three times to measure stochastic consistency.
* It uses paired comparison, a minimum worthwhile effect size, confidence sequences and sequential sampling.
* It proposes requiring successful transfer across several independent workflows before rejecting the broad conclusion.

## Per-criterion winners

1. **Correctness — A.**
   A represents the production survey sample accurately and ties its conclusion to observed repair and integration burden. B says the study “surveyed 86 practitioners,” although it surveyed 306 and filtered to 86 deployed/pilot cases; it also changes “systems are deliberately bounded to ten steps before intervention” into the stronger claim that 68% “needed” human action. ([arXiv][1])

2. **Key drivers — A.**
   A identifies the variables that determine production value directly: review time, repair effort, handoffs, rework, operating cost and failure loss. B identifies important determinants of score portability, but several—prompt sensitivity and generic reliability dimensions—are less directly connected to whether a company’s deployment creates value.

3. **Mechanism — Tie.**
   A explains objective mismatch: a correct final artifact can require enough hidden human work to destroy its economic value. B explains system confounding: infrastructure and control policy alter what the score measures. Both provide a substantive causal account rather than merely asserting benchmark failure.

4. **Caveats — A.**
   A presents a strong positive counterexample in which offline evaluation predicted online outcomes, then narrows its claim to raw success as a sufficient statistic. B’s alternative—success as an early filter followed by other testing—does not strongly challenge its portability thesis because it already abandons reliance on one portable score.

5. **Calibration — A.**
   A explicitly limits the strongest causal evidence to experienced software maintainers, distinguishes randomized from observational evidence and assigns moderate confidence. B also states limits, but overstates that its four listed conditions are sufficient for one score to predict production loss; those conditions cannot exclude omitted costs or workflow effects.

6. **Actionability — A.**
   A’s test measures the proposed target directly by having operators take outputs to completion and recording review, repair, escalation and downstream acceptance. B’s selective review of only disagreements and unstable runs can miss common-mode defects or burdens shared by both systems, while its exact-output matching rule may flag harmless differences.

## Overall: A

Response B has the stronger treatment of infrastructure confounding, run-to-run reliability and sequential experimental design. Response A nevertheless answers the business-evaluation question more directly, supplies a stronger innocent alternative, measures its proposed mechanism in the falsification test, and contains fewer potentially misleading interpretations.

**Confidence: high**

[1]: https://arxiv.org/html/2512.04123v1 "Measuring Agents in Production"
[2]: https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/ "Research Update: Algorithmic vs. Holistic Evaluation - METR"
[3]: https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ "Many SWE-bench-Passing PRs Would Not Be Merged into Main - METR"
[4]: https://arxiv.org/abs/2605.29442?utm_source=chatgpt.com "How Coding Agents Fail Their Users: A Large-Scale Analysis of Developer-Agent Misalignment in 20,574 Real-World Sessions"
[5]: https://arxiv.org/html/2604.12162v1 "AlphaEval: Evaluating Agents in Production"
[6]: https://arxiv.org/abs/2606.08867?utm_source=chatgpt.com "Building Customer Support AI Agents at 100M-User Scale: An Evaluation-Driven Framework"
[7]: https://www.anthropic.com/engineering/infrastructure-noise "Quantifying infrastructure noise in agentic coding evals \ Anthropic"
[8]: https://arxiv.org/html/2602.16666v3 "Towards a Science of AI Agent Reliability"
