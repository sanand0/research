# Latent Experiments — prioritized next steps after H001/H002

## 1. Move to a fresh scientific outcome in a new dataset/domain

Highest priority.

Why: H001 and H002 both produced stable nulls and demonstrated that the epistemic gates work. The current chickadee survival outcome is now unsealed, so further phenotype mining in that cohort would be post-hoc. A fresh dataset restores a clean discovery opportunity and avoids increasingly specialized ecology-side data archaeology.

Target datasets with:

- >=200 independent units or hundreds of unit-periods where possible;
- rich repeated/raw measurements rather than only paper-ready summaries;
- at least one meaningful outcome not central to the focal paper;
- multiple papers/projects from the same experiment/cohort, enabling cross-paper latent joins;
- public code/data and an independent replication path;
- simple enough statistical structure that a live SciPy explanation remains possible.

Prefer ecology, behavioral science, astronomy, or science-of-science over clinical medicine for the next pilot.

## 2. Automate the highest-value part discovered manually: the cohort/data-lineage graph

Build a scout that represents:

`paper -> dataset -> cohort -> field season -> individual identifier namespace -> measured variables -> tested relationships -> outcomes -> related papers`

The agent's surprising successes came from joining projections across papers and tracing OSF/Dryad project graphs, not from generic hypothesis generation. Automating this graph should make the next candidate search much faster and more auditable.

Minimum reusable asset:

- `sources.jsonl`: papers/datasets/projects with provenance;
- `relations.jsonl`: same-cohort/same-ID/same-season links and confidence;
- `tested-relations.jsonl`: what authors actually modeled;
- `seals.json`: fields/files that are outcomes and their access state;
- a command that proposes candidate cross-paper joins without opening sealed outcomes.

## 3. Keep Amherst as H001's best independent replication, but only if raw download becomes normally accessible

Year-2 membership remains sealed. The portable chronotype phenotype is already frozen and validated on Alberta at rho~0.96 versus the full phenotype.

Proceed only by normal human-authorized access:

1. obtain Amherst Year-1 RFID only;
2. compute chronotype reliability and feeder/site exposure;
3. freeze the Year-2 observation model;
4. only then unseal Year-2 IDs.

Do not spend more agent time fighting Dryad's WAF.

## 4. Treat multi-winter UABG as a later high-value collaboration, not the next agent-only task

The public Mathot-lab OSF graph contains many related winters and outcomes, but continuous RFID streams and survival/capture histories are fragmented. A direct author request or collaboration could turn this into hundreds of bird-years and a proper capture-mark-recapture study.

This is scientifically stronger than another single-winter analysis but slower and dependent on unpublished/undeposited linkage data.

## 5. For SciPy India, preserve the nulls

Do not regard H001/H002 as failed demo material. They are evidence the process does not simply manufacture significance.

The emerging talk spine is:

> An AI agent tried to discover something in public scientific data. The statistical tests were easy; the hard part was preserving the right to believe the answer.

Before the talk, aim for one independently replicated positive discovery **or** a portfolio of 5–10 preregistered latent experiments whose hit/null rate is itself informative. The latter may be scientifically more honest and a better reusable benchmark.
