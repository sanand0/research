# Latent Experiments — prioritized next steps after H001–H005

## 1. Run H006 only after the new candidate scorecard passes every hard gate

Highest priority. Stop optimizing for “interesting dataset”; optimize for **clean discoverability**.

H001–H005 have now exposed the expensive failure modes: already-tested hypotheses, unreliable derived traits, weak event counts, inaccessible blobs, temporal leakage, join-type bugs, and unusable outcome statuses. `candidate-scorecard.md` turns those into cheap pre-analysis gates.

For H006, prefer:

- >=300 independent units or a continuous/time-to-event outcome with high information;
- repeated/raw measurements with a low-dimensional latent transform;
- source paper/code that leaves the transform demonstrably untested;
- outcome status vocabulary known before freeze;
- an independent replication dataset visible before unseal;
- normal PLOS/Figshare/GitHub/OSF access rather than WAF-dependent archives.

## 2. Prefer a continuous or well-powered time-to-event outcome next

Binary outcomes have repeatedly wasted nominal N. H004 had 225 colonies but 21 failures; H005 had adequate known successes/failures but 39/268 unavailable outcomes and selection concerns.

Best next class: continuous future performance, count outcome, or well-observed survival time with censoring semantics already explicit.

Candidate rejection from the latest scout: the killifish lifelong-behavior dataset has 121 natural deaths and superb longitudinal data, but the source paper already directly forecasts future lifespan from young behavior. It therefore fails the original-analysis-gap gate despite excellent information.

## 3. Build the cohort/data-lineage + temporal-provenance scout

The recurring high-value agent work is graph construction, not hypothesis prose:

`paper -> dataset -> cohort -> time -> identifier -> variable -> derivation -> when knowable -> tested relationship -> outcome status -> replication dataset`

Minimum assets:

- `sources.jsonl` — papers/datasets/projects + source provenance;
- `relations.jsonl` — same-cohort/season/ID links;
- `tested-relations.jsonl` — exact author models/relationships;
- `feature-provenance.jsonl` — derived feature ingredients and latest time each becomes knowable;
- `seals.json` — outcome fields/status vocabularies and access state.

The scout should reject candidates automatically when a hard scorecard gate fails.

## 4. Preserve H001–H005 as the benchmark portfolio

- H001 chronotype -> chickadee survival: stable imprecise null.
- H002 behavioral predictability -> chickadee survival: stable null.
- H003 blue-tit laying-date predictability: rejected before outcome because individual ranking did not reproduce.
- H004 bee trajectory -> winter viability: unsupported and sensitive; too few failures.
- H005 red-kite range contraction -> nest success: preregistration non-executable due outcome-status assumptions; exploratory recovery unsupported and sign-sensitive.

This portfolio is evidence that the process is not a significance generator.

## 5. SciPy asset: make the epistemic compiler executable

The reusable system should emit an auditable research state machine:

`SCOUT -> PROVENANCE -> SEAL -> PREDICTOR GATES -> FREEZE -> UNSEAL -> TEST -> STABILITY -> REPLICATE/REJECT`

Every transition gets a machine-checkable artifact/hash. A live SciPy demonstration can deliberately stop when a gate fails; failure itself becomes a visible scientific result.

## Lower-priority parked paths

- **Amherst H001 replication:** good if Year-1 RFID becomes normally accessible; do not fight Dryad WAF.
- **Multi-winter Alberta chickadees:** scientifically strong but likely needs author collaboration/crosswalks.
- **Red-kite German validation:** do not pursue H005 specifically because Swiss H005-E is unsupported and sign-sensitive; retain the dataset for a future *independently motivated* question.
- **Blue-tit reproductive outcome:** remains sealed; H003 predictor failed reliability and should stay rejected.
