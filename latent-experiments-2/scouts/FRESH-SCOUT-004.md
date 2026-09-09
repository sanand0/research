# Fresh discrepancy scout 004 — no survivor; broad scouting stops

Date: 2026-09-09

## Search strategy

This was the final broad scout under the precommitted search funnel. Unlike scouts 001–003, it required **replicated interventions** rather than observational discrepancies:

- the same intervention repeated across independent labs/sites/gardens;
- proposed mediator and endpoint directly observed on the same experimental unit;
- identical measurement semantics across discovery and confirmation sources;
- source-level confirmation, not an arbitrary row split;
- exact-discriminator prior-art search before outcome analysis.

If no candidate survived, the project was required to stop broad scouting and reassess the SciPy talk direction rather than lower the gate.

## C012 — multi-lab Hue–Heat physiology

### Why it looked unusually strong

The coordinated Hue–Heat experiment is a genuine replicated intervention: 543 experimental rounds in eight laboratories across six countries, using a shared counterbalanced protocol. Participants experienced neutral, reddish and bluish white-light conditions under controlled thermal environments. Public OSF data are separated by laboratory and include environmental measurements, physiology and questionnaires.

A 2026 multi-site analysis reported no effect of roughly 3000–6000 K white-light CCT on thermal sensation/preference. The open physiological arm suggested a sharper unresolved question:

> Could hue alter physiology reproducibly across laboratories even if it does not alter conscious thermal sensation?

This would distinguish a genuinely absent cross-modal effect from a small physiological effect that is weakly coupled to perception.

### Frozen evidence split before CSV values

- Discovery: laboratories 1, 3, 5, 7.
- Confirmation: laboratories 2, 4, 6, 8.
- Split rule: odd/even laboratory ID, chosen before reading any CSV values.
- Confirmation values were never accessed.

Initial primary estimand: within-round reddish-minus-bluish terminal-window mean skin temperature, with lighting order and thermal condition adjusted. Heart rate was secondary.

### Calibration before real outcomes

Synthetic calibration exposed two tempting but invalid analysis choices before any Hue–Heat effects were computed.

1. A first fixed-effect/inverse-variance pool could produce severe false confidence because participant precision dominated the analysis rather than laboratory replication.
2. A simulation coding error also showed why a known-null generator must itself be checked: an uncentered treatment-context term silently injected a non-null mean.

The final analysis treats the **laboratory as the replication unit**: fit one hue effect per lab, then use an equal-weight one-sample t-test across four labs, require at least 3/4 lab effects positive, and require all leave-one-lab-out pooled effects positive.

Final calibration over 1,000 simulated four-lab experiments:

- true 0.00 °C effect: 3.0% pass rate;
- +0.05 °C: 47.6% power;
- +0.10 °C: 93.9% power;
- +0.15 °C: 99.9% power.

Result SHA-256: `8e72ae7abf9bd0f8c1440a5ccd3f06a409c1b0efb4e2d5c38e68c3fcc5576c83`; byte-identical on rerun.

### Discovery semantics gate — decisive stop

Only discovery laboratories 1/3/5/7 were downloaded. Before calculating any reddish-versus-bluish effect, sensor completeness was checked.

The nominally common `Tsk_*` schema does **not** represent a common anatomical measurement:

- Lab 1 records only back and shin skin temperatures.
- Lab 3 records most/all ten skin sites.
- Lab 5 records all ten sites with substantial variable missingness.
- Lab 7 records only hand skin temperature.

Therefore “mean available skin temperature” would compare different biological quantities across laboratories.

Heart rate cannot cleanly replace it:

- Lab 1 has no `HRinst` and only partial `HRave` terminal-window coverage.
- Lab 7 has `HRinst` throughout but effectively no usable terminal-window `HRave` rounds.

There is no common adequately observed heart-rate variable across all four discovery labs either.

**No reddish-versus-bluish physiological effect was computed. Confirmation laboratories 2/4/6/8 remain unopened.**

**Decision: STOP C012 BEFORE OUTCOME EFFECT.** Z-scoring different anatomical sites or switching HR definitions after seeing this structure would weaken the replicated-intervention claim rather than repair it.

Reusable lesson: **a shared column schema does not imply shared biological measurement semantics.**

## C013 — bur-oak reciprocal transplant / phenology versus stress physiology

The 2026 Quercus macrocarpa reciprocal-transplant dataset is operationally excellent: three common gardens (Minnesota, Illinois, Oklahoma), individual-tree physiology, growth, survival and 2023 budburst/senescence/growing-season phenology in a small open Dryad release.

A possible mechanism question was whether phenological adjustment rather than peak photosynthetic capacity explains the reported growth–survival decoupling at climatic extremes.

It was not promoted because:

- only three gardens exist;
- the two candidate “replication” gardens impose qualitatively opposite climatic stresses, so Oklahoma discovery → Minnesota confirmation would assume the same mechanism under heat/aridity and cold/season-length limitation;
- the 2026 publication family already analyzes local adaptation, physiological performance, selection and morphology extensively.

The source is scientifically valuable, but it does not provide clean same-mechanism source-level confirmation for this sharpened claim.

**Decision: REJECT AT SCOUT GATE; no outcome reanalysis.**

## C014 — global antipredator-colour replicated experiment

A 2026 global experiment deployed >15,000 artificial prey across 21 sites/6 continents, an unusually strong replicated intervention structure. But its paper already analyzes the heterogeneous mechanism of interest: relative aposematic/camouflaged performance changes with predation pressure, background/light and prey context.

Moreover, many contextual mediators are measured at site level rather than on each prey target, violating this scout's same-unit mediator requirement.

**Decision: REJECT ON PRIOR ART + UNIT ALIGNMENT; no secondary analysis.**

## Scout conclusion

**NO SURVIVOR. BROAD SCOUTING STOPS.**

Across four fresh scouts, progressively stricter filters eliminated candidates for distinct reasons:

1. exact discriminator already published;
2. decisive observable absent or disputed;
3. confirmation aggregates away the necessary analysis unit;
4. replicated datasets use nominally common variables with incompatible biological measurement semantics.

The project should not create scout 005. The next phase is a project-level scientific post-mortem and a decision about the SciPy talk itself.
