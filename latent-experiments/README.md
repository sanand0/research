# Latent Experiments

Can an agent find a scientifically interesting relationship hidden in data that researchers already collected but did not test?

Current phase: paper/data search → understand published analyses → propose untested relationship → freeze hypothesis before outcome inspection.

See:

- `protocol.md` — anti-leakage / preregistration rules
- `screening.md` — candidate papers and rejects
- `research-log.md` — chronological process notes

## Current status

Experiment 001 has completed its first outcome test. The frozen chronotype -> apparent-survival hypothesis produced a **stable null**: OR 1.315 per SD earlier chronotype, 95% CI 0.873–1.980, p=.190 (N=137). See `RESULTS-001.md` for the primary result, robustness checks, known-signal validation, failures, and replication scout.

The key methodological outcome is positive: cross-paper latent joins are feasible, but derived phenotypes should pass a source-paper known-signal validation before being trusted.


## Replication phase

- `RESULTS-001.md` — completed Alberta result (stable null)
- `POSTMORTEM-001.md` — process failures and protocol upgrades
- `replication-amherst-001.md` — frozen independent-population replication design; Year-2 membership still sealed
- `analysis/portable_chronotype_calibration.json` — outcome-free calibration of portable timing/use phenotypes

Current blocker: Dryad raw-file downloads require human confirmation in this environment. Do not bypass it; obtain Year-1 data through normal authorized access before proceeding.

- `replication-alberta-farr-001.md` — frozen same-site 2018/19 survival-replication feasibility/design; Farr outcome rows still sealed
