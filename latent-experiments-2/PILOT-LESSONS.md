# Pilot lessons carried forward

Source snapshot: `latent-experiments/` at monorepo commit `f90a424` (2026-09-08). These are evidence and lessons, not operating instructions for this project.
All source paths below are relative to `latent-experiments/`.
- Start from a consequential discrepancy with competing explanations, not merely an untested predictor/outcome pair. Sources: `protocol.md`, `candidate-scorecard.md`, `NEXT-STEPS.md`.
- Treat effective information, measurement semantics, and observation opportunity as feasibility gates. Sources: `RESULTS-004.md`, `POSTMORTEM-004.md`, `RESULTS-005.md`, `POSTMORTEM-005.md`.
- Derived individual traits need outcome-blind reliability and known-signal checks. Sources: `RESULTS-002.md`, `POSTMORTEM-002.md`, `research-log.md`.
- Trace temporal provenance of every feature ingredient; apparently early variables can leak later information. Source: `POSTMORTEM-005.md`.
- Verify archive contents, identifiers, missing-value semantics, and source-analysis reproduction before expensive modeling. Sources: `POSTMORTEM-001.md`, `POSTMORTEM-002.md`, `candidate-scorecard.md`.
- Preserve nulls and failed preregistrations; do not rescue them by mining the same outcome. Sources: `RESULTS-001.md`, `RESULTS-002.md`, `RESULTS-004.md`, `RESULTS-005.md`.
- Hashes establish artifact identity, not blinding. Source: `POSTMORTEM-001.md`.
- H006 duckweed is **unresolved** and is not a prerequisite here. Its preregistration and analysis script were committed at `f90a424`; current `HEAD` is exactly `f90a424`, with no `RESULTS-006.md` or `POSTMORTEM-006.md`. Do not execute it automatically. Sources: `candidates/duckweed-h006/CANDIDATE-H006.md`, `hypothesis-006.md`, `analysis-plan-006.md`, `research-log.md`.
