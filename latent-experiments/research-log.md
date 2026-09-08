# Research log

## 2026-09-08 — setup

Created a preregistration-like protocol before inspecting candidate outcomes. The central guardrail is that a hypothesis must be frozen before any computation involving its predictor/outcome relationship.


## 2026-09-08 — broad screening

Screened recent open datasets in behavioral ecology, thermal ecology, plant/herbivore plasticity, movement ecology and large comparative datasets. Recorded candidates and rejects in `screening.md`.

The Black-capped Chickadee 2024 spatial-use dataset initially looked unusually strong because its raw RFID data include per-visit timestamps that the published analysis code does not use. Downloaded the public OSF/Dryad data and complete author R analysis into `candidates/chickadees/` and saved SHA-256 hashes.

### Negative finding: obvious timestamp hypothesis already published

A literature search found Hobbs et al. 2024, *Exploring sources of (co-)variation in timing and total daily feeder visits in a wild population of black-capped chickadees*. It uses the same University of Alberta population and winter 2022-23, and directly models first/last feeder time relative to sunrise/sunset, temperature, daylength, age/sex and feeder visit totals. Therefore the initial idea “cold shifts feeding time” is not novel and was rejected before any new outcome analysis.

This is an important workflow lesson: searching only around the focal paper title is insufficient. Search by population, authors, field season, methods, and each candidate variable before claiming it was untested.

### Stronger cross-paper latent experiment

Hobbs et al. publish timing phenotypes but no survival analysis. LaRocque et al. publish next-fall apparent survival from the same winter/population but do not use raw time-of-day. The LaRocque survival file contains 138 individual IDs; all 138 IDs exist in Hobbs et al.'s historical age/sex metadata. Survival values have not been read or summarized.

A web literature search for combinations of black-capped chickadee / chronotype / first feeder visit / activity timing / annual survival found no direct test. Close prior work establishes that chronotype is a recognized repeatable trait in passerines and that its fitness consequences are uncertain; a 2026 great-tit study found no association with measured breeding fitness. This makes a survival test worthwhile, while “no indexed paper found” is not enough to claim novelty.

Candidate primary relation: environment-adjusted first-feeder chronotype -> apparent annual survival, specifically asking whether timing carries information beyond total feeder-use amount and age/sex. This is now ready for a formal freeze before opening survival labels.

### Prior-art correction before freeze

A broader chronotype-fitness search found two important great-tit studies that prevent any broad claim that "chronotype and fitness have never been linked":

- Meijdam et al. (2025), *Female chronotype is not related to annual and lifetime reproductive success in a free-living songbird* (Royal Society Open Science, DOI 10.1098/rsos.250380), tested morning chronotype against annual/lifetime reproductive success and longevity and found no clear association.
- Strauß et al. (2026), *Female chronotype relates to lay date but not fitness in an island population of great tits* (Oecologia, DOI 10.1007/s00442-025-05857-3), likewise found chronotype related to lay date but not measured fitness outcomes.

Therefore the novelty claim is deliberately narrower: I found no indexed direct test, as of 2026-09-08, of **winter first-feeder chronotype predicting next-fall apparent survival in black-capped chickadees, conditional on total feeder use**, despite the two components being available from overlapping studies of the same field season. This is a plausible latent cross-paper experiment, not evidence of globally unprecedented chronotype-fitness research.
