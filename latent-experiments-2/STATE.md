# STATE

Updated: 2026-09-09 SGT

## Phase

`SCOUT -> FEASIBILITY`, leading candidate C001 (repeated TEM-1 DMS maps). No mutation-level DMS scores have been accessed.

## Inspected

- `~/code/research/AGENTS.md`; Git root `~/code/research`.
- Relevant local skills: data-analysis, code, expert-lens, post-mortem, evidence-provenance, stability-check, verification-gate, blind-spot, ideation-protocol, failure-redteam.
- Pilot: `protocol.md`, `candidate-scorecard.md`, `NEXT-STEPS.md`, `research-log.md`, H001/H002/H004/H005 RESULTS+POSTMORTEM, H006 candidate/hypothesis/analysis plan.
- Current pilot Git state: `HEAD=f90a424`; H006 unresolved, no results file.
- Public-source scouting for three candidate discrepancies.
- ProteinGym metadata only; no mutation scores.

## Completed

- New project directory initialized without nested Git repo.
- Compact pilot lessons recorded with source paths/commit.
- Shortlist limited to three candidates and leading candidate selected provisionally.
- C001 evidence roles fixed before score access:
  - discovery: `BLAT_ECOLX_Firnberg_2014`, `BLAT_ECOLX_Stiffler_2015`
  - confirmation: `BLAT_ECOLX_Jacquier_2013`
  - calibration/method-contrast: `BLAT_ECOLX_Deng_2012`
- Cheap C001 feasibility check passed: official S3 + metadata are directly accessible; four TEM-1 maps exist; broader repeated-assay ecosystem has 24 proteins / 55 assays.
- Practical resource budget set in README.
- Minimal machine-readable claim and access ledger established; metadata input hash recorded.
- Current SciPy India 2026 CFP constraints checked and recorded.

## Scientific progress

One bounded feasibility result only. No discovery analysis and no scientific claim yet.

## Engineering progress

Durable project state, evidence-role freeze, ignore rules, metadata-access path, claim specification, and JSONL ledger established. No general platform has been built.

## Blockers / risks

- Need to verify actual mutation overlap, score units/dynamic ranges, and whether Firnberg/Stiffler are sufficiently comparable to make residual disagreement interpretable.
- Need source-paper methods/code review before treating ProteinGym-normalized scores as measurement-equivalent.
- Novelty is unestablished. Literature already studies DMS noise/context shifts; any eventual novelty must be a specific independently confirmed pattern.
- Confirmation is procedural, not cryptographically blinded. Scores are publicly available and may exist in model pretraining knowledge. This is a prospective analysis discipline, not a secure vault.

## Exact next action

Acquire **discovery assays only** (Firnberg + Stiffler). Verify mutation identifiers, units, overlap, source transformations, and dynamic range without opening Jacquier confirmation scores. Run null/injected-effect calibration before any confirmatory claim is frozen.

## First decision checkpoint

Stop/redirect C001 before confirmation access if any of these hold:

1. insufficient common single-mutant coverage for stable calibration;
2. score construction/selection conditions differ so strongly that a shared estimand is incoherent;
3. discovery disagreement is explainable only by arbitrary transformation choices rather than a small prespecified calibration family;
4. no residual pattern can be frozen that would make a scientifically meaningful prediction in Jacquier;
5. analysis calibration shows unacceptable false-positive behavior or weak power for meaningful residual effects.
