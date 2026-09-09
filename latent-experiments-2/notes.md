# Notes

## 2026-09-09 — initialization

- Verified LocalMCP before work. Git root is `~/code/research`; applicable root instructions are `AGENTS.md`. `latent-experiments-2/` did not exist. Existing unrelated untracked directories were left untouched.
- Read local skills for investigative data analysis, code, expert judgment, evidence provenance, stability, verification, post-mortems, blind spots, ideation, and failure red-teaming.
- Inspected pilot `protocol.md`, `candidate-scorecard.md`, `NEXT-STEPS.md`, full `research-log.md`, H001/H002/H004/H005 result/post-mortem files, and H006 candidate/hypothesis/analysis plan. Compact carry-forward lessons are in `PILOT-LESSONS.md`.
- Verified H006 status: monorepo `HEAD` is `f90a424` (`latent-experiments: preregister H006 duckweed landmark test`); H006 has no result/post-mortem file. It remains unresolved and will not be executed here automatically.

## Candidate search

### C001 — repeated DMS maps of the same protein (leading)

Observation/disagreement: MAVE/DMS measurements are used as functional ground truth, yet different assays can disagree. Credible explanations include ordinary measurement noise/nonlinear assay scaling and genuine context-specific biology. Recent work explicitly warns that apparent shifts across DMS experiments may be either biological signal or experimental noise (e.g. Bloom-lab joint DMS modeling, DOI 10.1093/bioinformatics/btad470), and MaveDB treats assay context separately.

Who cares / decision: protein-variant interpretation, protein engineering, antibiotic-resistance evolution, and benchmark designers deciding whether to aggregate assays at the protein level.

Feasibility evidence, before score access:
- ProteinGym public S3 bucket listing succeeded from LocalMCP in <1 s. `DMS_substitutions.parquet` is 92,652,794 bytes.
- ProteinGym reference metadata downloaded normally (208,734 bytes) from its official GitHub repository.
- Metadata-only count found 24 proteins with multiple assays, 55 assays in those groups.
- TEM-1 (`BLAT_ECOLX`) has four independent maps: Deng 2012, Jacquier 2013, Firnberg 2014, Stiffler 2015. All cover the mature TEM-1 region and report 989–4,996 single mutants.
- Evidence roles frozen before mutation scores: discovery = Firnberg + Stiffler; confirmation = Jacquier; calibration/method-contrast control = Deng.

Primary sources/entry points:
- ProteinGym official repo: https://github.com/OATML-Markslab/ProteinGym
- ProteinGym public data registry: https://registry.opendata.aws/proteingym/
- Jacquier et al. 2013: DOI 10.1073/pnas.1215206110
- Firnberg et al. 2014: DOI 10.1093/molbev/msu081
- Stiffler et al. 2015: DOI 10.1016/j.cell.2015.01.035
- Deng et al. 2012: DOI 10.1016/j.jmb.2012.09.014

### C002 — neuronal criticality versus subsampling artifact

Observation/disagreement: power-law avalanche signatures have been interpreted as evidence for critical brain dynamics, while noncritical simulated systems can pass commonly used criticality tests and subsampling can produce or erase apparent signatures. This could change claims about cortical operating regimes.

Cheap discriminator: compare metrics under controlled thinning/binning and perturbation in models, then test frozen predictions on held-out open electrophysiology sessions. Allen Neuropixels provides a natural confirmation ecosystem.

Feasibility warning: LocalMCP `curl` to Zenodo record 4591877 (published noncritical-control code, 14.8 KB) timed out after 30 s. This is not a scientific rejection, but weakens live reliability relative to C001.

Primary sources:
- Destexhe & Touboul 2021 control code: DOI 10.5281/zenodo.4591877
- Levina & Priesemann 2017 subsampling scaling: DOI 10.1038/ncomms15140
- Allen Brain Observatory Visual Coding public dataset: https://registry.opendata.aws/allen-brain-observatory/

### C003 — Taylor's law: mechanism or statistical constraint?

Observation/disagreement: ecological variance often scales as a power of mean abundance. Explanations range from species interactions/environmental dynamics to process-independent feasible-set and sampling constraints. The biological meaning of the exponent remains debated.

Cheap discriminator: vary census length and perform constraint-preserving randomization; ask which aspects of exponent variation survive the null, then confirm in another ecological time-series ecosystem.

Primary sources:
- Kalyuzhny et al. 2014: DOI 10.1890/13-0326.1
- Xiao, Locey & White 2015: DOI 10.1086/682050; Dryad DOI 10.5061/dryad.h1c09
- Johnson et al. 2017 joint biological/statistical test: DOI 10.1098/rspb.2017.1388

## Tooling failures

- A first multi-file write call was blocked before LocalMCP execution. Retrying as narrow single operations worked. This confirms the user's warning against over-batched commands.
- A later heredoc Python metadata analysis was similarly blocked; a narrow shell pipeline succeeded.
- `duckdb -readonly` against an in-memory database failed because DuckDB 1.5.5 does not allow an in-memory DB in read-only mode. This was a CLI invocation error, not a data problem.
- Direct remote DuckDB query was blocked before execution by the platform safety classifier; no data were accessed through that call.

## SciPy India 2026 constraints checked on 2026-09-09

- CFP closes 19 Oct 2026, 23:59 IST; rolling review.
- Talk format: 30 minutes including Q&A, in person on 20 Dec 2026.
- Sessions must be grounded in OSI-licensed FOSS; proprietary software cannot be the session focus.
- Best current track fits: AI, machine learning, and data-driven discovery; reproducibility in research is also plausible.
- Proposal should make the specific scientific problem, audience, take-away, source code/data, and references concrete.
- Slides must ultimately be shared under a permissive license.
- Official sources: https://cfp.scipy.in/scipy-india-2026/cfp and https://scipy.in/2026/faq

## Three-step decision checkpoint

- Does the question still matter? **Yes.** Treating same-protein DMS maps as interchangeable versus context-specific changes variant interpretation and benchmark design.
- Can the next test change a conclusion? **Yes.** Verifying score semantics, common mutation coverage, and discovery-map calibration can reject C001 before confirmation access.
- Does progress justify another step? **Yes, narrowly.** The source is operationally clean, the discovery/confirmation split is available, and the next action is cheap. This is not yet evidence for a biological context effect.

## 2026-09-09 — C001 discovery-only audit and calibration

### Discovery access boundary

- Retrieved only the frozen discovery assays, Firnberg 2014 and Stiffler 2015, using HTTP range reads from ProteinGym's official ZIP. Jacquier confirmation and Deng control scores remain unopened.
- Processed file SHA-256: Firnberg `cfb814a5a5f81ad3f86d3203ac7f04dee3fd996e7c2c624b75656712ab5e54df`; Stiffler `82835aeecc2001c742434457102e02b5aaf38673274aaba00ac85e07bcd94f35`.
- Raw discovery file SHA-256: Firnberg `2272faf35e982e762cfabdb32cb6a74b823998106a914ca6a00cf083930a997b`; Stiffler `94442e9b6c19e9183ad035e19a5881dab89d4d3634e940ff3056beaba787117b`.
- The Stiffler raw discovery file exposes the planned 2500-ug/mL score plus 0/39/156/625 concentration series, same-condition replicate columns, cefotaxime, `km`, and `vmax`. This broader discovery-side access is recorded in the claim/ledger.

### Measurement semantics and overlap

- ProteinGym applies no numerical transformation to these two chosen scores: processed Firnberg `DMS_score` equals raw `linear`, and processed Stiffler `DMS_score` equals raw `2500`, max absolute difference ~1e-16.
- Firnberg processed: N=4,783 unique missense mutations, range 0.0008–2.9024, median 0.4257.
- Stiffler processed: N=4,996 unique missense mutations, range -3.7433–0.3558, median -1.1595.
- Common mutations: 4,782. The maps have Spearman rho ~0.9373 despite incompatible numerical scales.
- Firnberg raw contains 5,032 rows; the 249 rows removed by ProteinGym are all same-amino-acid/synonymous protein entries. Stiffler's 4,996 rows are retained exactly.
- Source methods make a nonlinear mapping scientifically expected: Firnberg estimates an underlying resistance landscape across a wide resistance range; Stiffler shows fitness changing sharply with ampicillin selection strength. Therefore raw score subtraction is invalid; only residuals after a small monotone calibration family were considered.

### Prior-art correction

The broad C001 premise is not an unresolved scientific disagreement. Stiffler 2015 directly establishes selection-strength-dependent mutational effects, later adaptive-landscape reviews explain the same function-to-fitness mechanism, and later work explicitly compares Firnberg/Stiffler/Jacquier/Deng-like TEM-1 mutation-effect datasets. C001 could only remain useful if it exposed a sharper residual phenomenon that survived empirical noise calibration.

### Calibration experiment

`analysis/c001_calibrate.py` uses position-blocked five-fold isotonic calibration. It compares:

1. discovery: Firnberg -> Stiffler 2500;
2. empirical known-null: Stiffler replicate 1 -> replicate 2 at 0, 39, 156, 625, and 2500;
3. known context shift: Stiffler 39 -> Stiffler 2500;
4. injected random position effects scaled to same-condition replicate residual noise.

The proposed statistic was variance in cross-fitted residuals explained by amino-acid position (`eta2_position`), with a nominal null formed by permuting residuals within Firnberg-score deciles.

### Decisive calibration failure

- Firnberg -> Stiffler 2500: position eta² = **0.2151**, nominal permutation p ~.0025.
- Same-condition replicate nulls all also reject the nominal null: eta² ranges **0.1863–0.4535**, each p ~.0025.
- Thus the cross-study position structure lies *inside the empirical same-condition technical-null range*. It cannot be interpreted as biological context dependence.
- The known 39 -> 2500 selection-strength shift is much larger: eta² = **0.5255**, showing that large real context changes are detectable, but not validating the cross-study residual signal.
- Injected-effect power is numerically 1.0 at 0.5x/1x/2x replicate-noise SD, but is explicitly **not interpretable** because the null model fails real same-condition cases.
- Result file `results/c001_calibration.json` reproduced byte-identically across two stochastic reruns: SHA-256 `2eae5d560d0683778176677c167aa79a39458788556c0f1f249c7da6ebdb5e8b`.

### Decision

**STOP C001 before confirmation access.** Do not open Jacquier or Deng for this question. Two independent reasons are sufficient: the broad context-dependence claim is already established, and the proposed sharper position-residual detector fails empirical-null calibration. Further detector engineering would be engineering progress, not justified scientific progress.

Reusable lesson: a permutation/null model for cross-assay DMS residuals must first accept actual same-condition replicate pairs. Randomly shuffled residuals are too optimistic because technical errors themselves can be strongly position-structured.

Independent stability check: replacing isotonic residuals with simple percentile-rank differences gives cross-study position eta² **0.2462**, while all five same-condition replicate pairs are larger (**0.2975–0.4703**). Thus the stop decision is not an artifact of isotonic calibration choice.

### Implementation/tool failures during C001

- Hugging Face datasets-server row filtering returned 404/500, so it could not enforce discovery-only retrieval. Recovery: ProteinGym's official Harvard ZIP supports byte ranges; `remotezip` fetched only named discovery members while leaving confirmation payloads unread.
- A combined LocalMCP schema+summary call was blocked before execution by the platform safety filter. Narrow single-purpose calls worked.
- Two DuckDB exploratory queries failed from query-construction mistakes (window function inside aggregate; CTE reused across statements). Neither affected stored scientific results; corrected narrow queries were used.
- First calibration execution stopped before results because 19/4,996 Stiffler rows lack the second replicate column at every duplicated concentration. Recovery: each real-null pair now has an explicit complete-case cohort (N=4,763 within the cross-study overlap), while the cross-study/context-shift cohorts remain N=4,782.
- Expanded calibration exceeded the default 30-second LocalMCP cap. The identical code was rerun unchanged with a bounded 60-second cap, then rerun again; result hashes matched.
