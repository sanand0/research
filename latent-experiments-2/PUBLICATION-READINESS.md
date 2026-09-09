# Publication readiness

Checked 2026-09-09 after the offline talk rehearsal.

## Current state

The Git remote is `https://github.com/sanand0/research`, and the repository is public. Local `main` is 24 commits ahead of `origin/main`.

Those 24 commits are all research work:

- 9 commits for `latent-experiments-2` through the talk/protocol extraction checkpoint;
- 15 earlier `latent-experiments` pilot commits;
- the root README index update.

There are no unrelated top-level project commits in `origin/main..HEAD`, although the working tree contains unrelated untracked directories/files that are not part of these commits.

Therefore a normal `git push origin main` would publish both the pilot and this project history. Do not push merely to populate the CFP resource field unless that publication boundary is acceptable.

## License blocker

There is currently **no root or project-level LICENSE/COPYING file** in the research repository.

Consequences:

- the source is publicly viewable after push, but public visibility alone does not make it open-source;
- `CFP-DRAFT.md` should not claim that this repository itself is FOSS until an explicit license is chosen;
- SciPy India requires sessions to be grounded in FOSS and requires slides to be published under a permissive license.

Do not select a license implicitly. Licensing is a user decision.

Reasonable choices to consider:

- code/scripts: MIT, BSD-3-Clause, or Apache-2.0;
- talk prose/slides/diagrams: a permissive content license such as CC BY 4.0, or another license the author explicitly prefers.

A single OSI software license can also be applied to the whole project if preferred, but that choice should be explicit.

## Data boundary

Raw third-party datasets and ignored caches are not committed. The public artifact consists of:

- analysis code;
- small derived/calibration result JSON;
- claim/access ledgers;
- protocols, notes and talk material;
- source identifiers and hashes where applicable.

The C012 discovery CSVs remain ignored locally and confirmation labs 2/4/6/8 remain unmaterialized.

## CFP resource boundary

Before adding the expected resource URL

`https://github.com/sanand0/research/tree/main/latent-experiments-2`

complete all three:

1. explicitly choose/add a license suitable for the code and talk materials;
2. decide whether publishing both `latent-experiments` and `latent-experiments-2` histories is acceptable;
3. push the relevant branch/commits and verify the link from an unauthenticated browser.

If the pilot should not be published, do **not** push current `main` as-is. Instead create a deliberately scoped public artifact/repository after an explicit user instruction.

## Submission state

`CFP-DRAFT.md` is ready for review but has **not** been submitted. No push, proposal creation, or external mutation has been performed in this phase.
