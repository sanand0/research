# Alberta 2018/19 replication / latent-experiment sources

This directory intentionally separates predictor-side material from sealed survival outcomes.

## p3hz4 — Risk-taking and annual survival in chickadees

Public OSF project: `p3hz4`.

The authors' source dataset contains 18 columns including `survival`. Before H002 outcome access, only columns 1–17 were materialized as `p3hz4_predictors.csv`; its SHA256 is recorded in `analysis-plan-002.md`. The survival column was not included in this file.

`provenance/p3hz4-analysis.R` is the public author analysis code. It establishes the source mean model and the definition `survival2 = ifelse(survival > 0, 1, 0)`.

## 4xa6w — 2018/19 predator-cue experiment

Public OSF project: `4xa6w`.

`provenance/arteaga-analysis.R`, `FR_Filtered.csv`, and `FR_All_records.csv` document the treatment-window behavior analysis. An HTTP-range inspection of `BCCH_Mob.zip` showed that the ~937 MB archive consists of WAV stimulus files, not continuous RFID logs. This killed the proposed 2018/19 chronotype replication.

## q8a62 — Recapture bias

Public OSF project: `q8a62`.

The README/code expose both aluminum ring and PIT-hex identifier conventions and were used outcome-blind to investigate linkage. A direct aggregate set comparison ultimately showed that 74/79 p3hz4 IDs match the Arteaga PIT-hex IDs exactly; no fuzzy or outcome-assisted matching was used.
