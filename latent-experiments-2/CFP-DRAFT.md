# SciPy India 2026 CFP draft

Checked against the live SciPy India 2026 CFP on 2026-09-09.

## Submission fields

**Session type:** Talk

**Title:** How do you calibrate an AI scientist?

**Track:** AI, machine learning, and data-driven discovery

Secondary intellectual fit: Reproducibility in research.

## Abstract

Can an AI agent discover a scientific result—and know when not to believe it?

I gave an agent open papers and datasets, let it write and run Python, and required each scientific-looking result to survive attempts to falsify it. The most useful outcomes were stops: a significant signal failed a real technical-null check; a plausible dynamical estimate failed model applicability; a positive ecological discovery failed frozen independent confirmation; and a calibrated eight-laboratory analysis stopped because nominally standard physiology columns represented incompatible biological measurements.

I will reproduce one of these gates live and show a small Python workflow built on FOSS scientific tools for freezing claims and evidence roles, calibrating against known nulls and known positives, reserving source-level confirmation, checking the true replication unit, and verifying deterministic outputs.

This is not a claim that AI cannot do science, nor a benchmark of AI discovery success. It is a proposal to treat research agents like uncalibrated scientific instruments—and make them earn the right to believe their own outputs.

## Description

Large language model agents can already search papers, write analysis code, run statistics, and produce convincing scientific narratives. That makes hypothesis generation easier. It does not make the resulting science trustworthy.

For this project I gave a research agent a deliberately difficult goal: use public scientific literature and data to discover something useful that I did not already know, then test it against independent evidence. The agent was allowed to write and execute Python, inspect open datasets, and propose new analyses. The constraint was that a good-looking result did not count. Before confirmation, the analysis had to survive explicit calibration and measurement gates; confirmation evidence was reserved by source-level unit wherever possible; failures and unopened evidence were preserved.

The talk follows four concrete cases where those safeguards changed the conclusion.

**1. A p-value calibrated against the wrong world.** In repeated TEM-1 deep-mutational-scanning data, an apparently strong structured residual was highly significant under a permutation null. The same detector also fired on real same-condition technical replicates, whose structure was as large or larger. The candidate stopped and reserved confirmation remained unopened.

**2. An estimator that returned an answer outside its domain of validity.** A multistep-regression estimator recovered known branching parameters under synthetic subsampling. On real Allen Neuropixels data, near-critical-looking estimates appeared, but the frozen fit/applicability criterion failed or changed with the neuron subset. Rather than invent progressively richer post-hoc models, the analysis stopped before confirmation.

**3. A genuinely positive discovery that failed independent evidence.** A constraint-preserving null found extra temporal organisation in two of three German steppe communities. The confirmation rule was frozen, a separate Danish heath ecosystem was opened, and zero of five confirmation plots passed. This is the full scientific loop: a positive discovery that the workflow allowed to die.

**4. A live multi-laboratory example where calibrated statistics are still not enough.** An eight-lab Hue–Heat dataset has a common table schema and a clean laboratory-level discovery/confirmation split. Before looking at any real lighting effect, simulation showed that participant-dominated pooling was anti-conservative; treating the laboratory as the independent unit fixed the calibration. The live demo then inspects only discovery-data structure and stops: one lab measures back/shin skin temperature, another hand only, and no heart-rate field is adequately common across all discovery labs. No treatment effect is calculated and confirmation labs stay unopened.

The live computation takes only a few seconds and is designed to run fully offline from prewarmed open-source Python dependencies. Deterministic JSON fallbacks are committed for reliability.

From these cases I extract a compact, reusable scientific loop rather than a framework:

1. search for the exact discriminating experiment, not merely a novel topic;
2. verify that the decisive observable actually exists and means the same thing across evidence sources;
3. freeze discovery and confirmation roles before substantive outcome access;
4. test the analysis on empirical/known nulls;
5. test known-positive effects and power;
6. separate estimator output from model applicability;
7. make the true independent unit—not the largest row count—the replication unit;
8. run frozen independent confirmation;
9. rerun deterministically, verify independently where practical, and stop when the next test cannot change the conclusion.

### Audience

Scientists, research-software engineers, data scientists, and ML/LLM practitioners who use Python for empirical research. No prior experience with AI agents is required. Familiarity with basic ideas such as train/test separation, p-values, or replication is helpful but not necessary; the examples are explained visually.

### What attendees will leave with

- A concrete way to treat an AI research agent as an **uncalibrated scientific instrument**, rather than as an authority that emits hypotheses and p-values.
- A minimal claim/access/calibration protocol they can reuse in ordinary Python projects without adopting a platform.
- Practical examples of three different failure classes: invalid null, invalid model applicability, and invalid measurement/replication semantics.
- A clear distinction between calibrating an individual analysis and benchmarking whether an agent actually selects better scientific questions.

### FOSS and open-science fit

The work is implemented with Python and open scientific-computing tools, small reviewable scripts, machine-readable claim/result files, deterministic seeds/hashes, and open/public scientific data where licensing permits. The demo does not depend on proprietary software or a cloud model at presentation time. Slides and accompanying materials will be released under a permissive license as required by SciPy India.

### Session outline

- 0–3 min: challenge and falsification-first scientific loop;
- 3–6 min: empirical null kills an apparently significant result;
- 6–9 min: model applicability kills a plausible parameter estimate;
- 9–13 min: positive discovery fails independent confirmation;
- 13–18 min: live offline calibration + measurement-semantic STOP;
- 18–22 min: reusable nine-gate protocol;
- 22–24 min: what remains unproven and a prospective agent benchmark;
- ~6 min: questions.

## Notes for organisers

This is a critical assessment of AI-assisted scientific discovery, not a product pitch. The scientific cases form an adaptive case series; I will explicitly **not** present them as a 0/N benchmark or estimate of an AI system's discovery rate.

The live demo has been rehearsed from a clean Git worktree using only discovery-lab files. After dependency warm-up it runs in about five seconds, works under `uv --offline`, makes no Internet socket connection, reproduces committed result hashes, computes no real Hue–Heat treatment effect, and leaves reserved confirmation labs unopened. Precomputed deterministic JSON/screenshots are the fallback if terminal execution fails.

The public code/resource URL should be added **after the local research branch is pushed**; as of 2026-09-09 the local repository is ahead of `origin/main`, so linking it now would send reviewers to stale material.

## Resources to add before submission

- [ ] Push the relevant commits to the public repository.
- [ ] Add the stable URL for `latent-experiments-2/`.
- [ ] Add a permissive license for the talk-specific materials if the repository license does not already make this explicit.
- [ ] Optionally add a one-page diagram or short demo recording after a full physical-laptop rehearsal.

Expected repository URL after push:

`https://github.com/sanand0/research/tree/main/latent-experiments-2`

## Three takeaways, short form

1. **Calibrate the agent's analysis against worlds where you know the answer.**
2. **Reserve genuinely new evidence and make the real independent unit the replication unit.**
3. **A scientifically useful agent needs explicit permission—and machinery—to stop.**

## Claims deliberately not made

- AI cannot discover science.
- The adaptive C001–C014 sequence estimates an AI discovery or failure rate.
- The individual calibration/gating ideas are themselves novel.
- C003 disproves biological stabilization generally.
- C012 establishes absence of a physiological Hue–Heat effect.
- The current project proves that the agent selects better scientific questions than a human or simple baseline.

That final question is specified separately as a prospective benchmark requiring genuinely unseen confirmation evidence.
