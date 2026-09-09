# Fresh discrepancy scout 001 — no survivor

Date: 2026-09-09

## Outcome

**No candidate cleared the full relevance + novelty/prior-art + clean-confirmation gate.** Do not force a leader from this batch.

The scout deliberately started outside C001–C003 and preferred 2025–2026 primary literature, direct observables, source/file-level holdouts, inexpensive perturbations, and FOSS/open data.

## C004 — Arctic-boreal methane measurement representativeness

### Initial discrepancy

ABCFlux v2 (Virkkala et al., 2026; DOI `10.5194/essd-18-5853-2026`; ORNL DAAC `10.3334/ORNLDAAC/2448`) is a newly released synthesis of monthly Arctic-boreal CO2/CH4 observations from >1,000 sites. Its methods/coverage analysis documents uneven ecosystem, season, geography, and measurement-method coverage. The user guide also exposes CH4 measurement method, chamber measurement-day count, gap filling, ecosystem class, month, and quality flags.

A plausible consequential question was whether sparse/manual chamber measurement produces biased monthly/annual CH4 fluxes relative to continuous eddy covariance, beyond simple ecosystem/month coverage imbalance. This matters for synthesis/upscaling of wetland methane budgets.

### Competing explanations

1. **Between-stratum representativeness:** bias comes mainly from over-/under-sampling high-emission ecosystem×month strata and can be corrected by target-area/time reweighting.
2. **Within-stratum measurement representativeness:** sparse chamber days/placements preferentially capture high- or low-flux conditions, so class/time reweighting cannot repair the bias.

### Cheap calibration before real outcomes

`analysis/c004_sampling_calibration.py` used synthetic two-class monthly fluxes only; no ABCFlux flux outcomes were accessed.

- With unbiased sparse days plus deliberate oversampling of the high-flux class, naive record weighting had mean relative bias +0.323 while ecosystem×month target weighting reduced bias to -0.003.
- With preferential sampling of high-flux days, target weighting still had +0.423 mean bias.

Result SHA-256: `3e76e854e3a09a31db83b9986383b7d9410913c3491ac9d44f2d79c90b8fc0ea`.

Lesson: class/time weighting can fix between-stratum representation but cannot diagnose preferential within-stratum measurement. An empirical paired EC-versus-chamber comparison is required.

### Decisive prior-art rejection

That exact empirical discriminator was already published on 2026-07-03 by Määttä et al., *Biogeosciences*, DOI `10.5194/bg-23-4379-2026`: ten sites with coincident chamber and eddy-covariance CH4, compared at half-hourly through annual scales. The study reports systematic scale differences and explicitly investigates chamber spatial heterogeneity, selective placement/footprint effects, measurement frequency/protocol, ebullition handling, and environmental drivers.

**Decision: REJECT C004 ON PRIOR ART.** ABCFlux v2 is new, but using it to rediscover chamber-vs-EC representativeness would duplicate a result published two months ago. No real ABCFlux flux values were opened.

Operational note: the ORNL bundle is only 5.4 MB and has a detailed public user guide, but file download requires Earthdata sign-in/controlled access. This is acceptable for offline research with a local hash-verified copy but poor as a live fresh-pull dependency.

## C005 — human lateral-occipital decoding without reported awareness

Primary source: Vanhoyland et al. 2025, *Nature Communications*, backward masking / intracranial Utah arrays. The paper explicitly leaves residual long-delay decoding among verbally “unperceived” targets ambiguous between genuine unconscious target information and occasional perceptual/report errors.

Why it matters: whether human LO represents stimulus identity without conscious perception.

Potential discriminator: mixture-vs-graded predictions on trial-level decoder evidence, then confirmation in a no-report paradigm.

Why it did not clear the gate:

- the report-confound/unconscious-perception debate is mature;
- the no-report confirmation is not cleanly matched to the same target-identity estimand;
- the public Figshare backward-masking archive is ~94.3 GB, with related paradigms 20–46 GB, too heavy for the intended live loop without substantial pre-extraction.

**Decision: DEMOTE / DO NOT OPEN OUTCOMES.** Metadata only was inspected.

## C006 — oceanography data-availability statements versus actual sharing

Primary source: Dunić & Vilibić 2026, *Research Integrity and Peer Review*, 1,400 sampled oceanography papers from 2018–2024. The aggregate result is striking: data-availability statements rose sharply while public data accessibility stayed broadly flat.

Potential alternative: composition/Simpson's paradox — journal/country mix may obscure within-journal improvements, so an aggregate flat trend may not show DAS ineffectiveness.

A 648 KB supplementary XLSX is article-level and operationally excellent; schema inspection showed year sheets with journal, country, open-access status, DAS, author-available data and publicly accessible data.

Why it did not clear the gate:

- a within-journal association remains observational and cannot cleanly identify DAS policy effects;
- natural-experiment/interrupted-time-series literature already shows journal data-sharing mandates can change availability when policies are stringent/enforced;
- the policy decision is therefore not well captured by re-regressing one cross-sectional sample.

**Decision: DEMOTE / NO ACTIVE CLAIM.** Supplementary schema/sample rows were inspected only; no model was fit.

## Three-step assessment

1. **Does any candidate in this scout still justify an active experiment? No.** C004's exact discriminator is published; C005 lacks a cheap clean confirmation; C006 lacks a clean causal discriminator and has substantial policy prior art.
2. **Can another cheap test rescue one without redefining the question? No.** Doing so would lower the project's gate or turn feasibility into adaptive candidate polishing.
3. **Does the scout justify another fresh search? Yes.** It improved the search filter: current *datasets* are not enough; search the implied discriminator itself before investing in access/calibration.

## Reusable scout lesson

Before promoting a candidate because a new dataset enables a tempting analysis, search explicitly for the **implied discriminating experiment** (for example, “paired chamber eddy covariance methane multiple timescales”), not just for papers using the new dataset or broad topic. This would have rejected C004 before synthetic implementation.
