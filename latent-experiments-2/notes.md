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

## 2026-09-09 — C002 Allen Neuropixels feasibility and first discovery calibration

### Access and observation semantics

- Allen Visual Coding Neuropixels is operationally accessible through the public `allen-brain-observatory` S3 bucket using unsigned HTTP. The documented `aws s3` route could not be used because LocalMCP lacks the AWS CLI; direct public HTTP listing/range access works.
- Cached metadata only: 58 sessions / 58 mice: 32 `brain_observatory_1.1`, 26 `functional_connectivity`. Metadata hashes are in `ledger.jsonl`.
- Session NWBs are ~2.6–2.9 GB, but HDF5-over-HTTP range reads work. Raw AP-band files are hundreds of GB/probe and are not needed.
- A design-only inspection of `brain_observatory_1.1` session 715093703 found fragmented spontaneous periods. No spike values were read.
- A primary-source check plus design-only inspection showed `functional_connectivity` sessions contain a standardized continuous ~30-minute spontaneous/no-stimulus block. The initial 16/16 BO role split was therefore explicitly superseded, before spike values, by a sex+genotype-stratified 13/13 FC split. The 32 BO sessions remain an external reserve.
- VISp metadata then supplied a further pre-spike eligibility gate: 24/26 FC sessions have >=32 `quality=good` VISp units. One discovery session (`819701982`) and one confirmation session (`819186360`) lack qualifying VISp units. Frozen analyzable sets are therefore 12 discovery + 12 confirmation mice. Confirmation spikes remain untouched.

### Cheap execution feasibility

- Discovery session 767871931 has a longest spontaneous interval of 1802.507 s and 201 good VISp units.
- A preliminary 64-unit range-read/binned probe needed ~30 MB of timestamp payload and ~22 s locally for a full 30-minute block. Controlled unit-count reductions and 1/5/10 ms binning are operationally cheap.
- Final guarded VISp script range-reads 114 MB of timestamp payload to reconstruct all 201 qualifying VISp units for the first 1800 s of the spontaneous block; no full NWB is downloaded.

### Sharpened scientific discrepancy

The mature question “does subsampling affect avalanche statistics?” is not enough. A sharper target emerged from current literature:

- a 2026 reviewed preprint reports near-critical spontaneous mouse-V1 dynamics from pooled Allen two-photon recordings because individual spontaneous recordings are short;
- Destexhe & Touboul show noncritical systems can satisfy common avalanche criticality hallmarks;
- Wilting & Priesemann's multistep-regression (MR) method is designed to infer propagation strength under subsampling;
- recent work on the same Allen functional-connectivity recordings reports distinct neural states separated by abrupt transitions, making stationarity itself a material assumption.

Working discriminator: in long spike-resolved individual-mouse V1 recordings, does a subsampling-aware dynamical estimator remain applicable and stable across observed-neuron subsets, and eventually does it agree with prespecified avalanche criteria? This is not a direct falsification of calcium-imaging results because modality and animals differ.

### MR calibration before Allen interpretation

`analysis/c002_mr_calibrate.py` uses `mrestimator==0.2.0`, 4 ms bins, lags 1..200, and a frozen applicability gate R² >= .90. The gate is essential: independent Poisson simulations return meaningless raw `m` values near 1 but have R² around zero/negative.

Synthetic aggregate branching calibration, five seeds each and 100%/50%/25% binomial event sampling:

- true m=.8: 15/15 applicable, MAE ~.002;
- true m=.98: 15/15 applicable, MAE ~.0021;
- true m=.99: 15/15 applicable, MAE ~.0015;
- Poisson/non-propagating null: 0/5 applicable.

This validates the implementation for the published aggregate/binomial-subsampling setting. It does **not** yet calibrate fixed-neuron subsampling in a heterogeneous spatial network.

### First discovery mouse: method assumption under test, not criticality result

Only discovery session `767871931` spike values have been accessed. Confirmation spike values remain untouched.

Final guarded result from `results/c002_session_767871931.json`:

- primary deterministic 32-unit VISp subset: m=.9633, R²=.8807 -> **not applicable**;
- nested 16 units: m=.9885, R²=.8799 -> not applicable;
- nested 8 units: m=.9966, R²=.6861 -> not applicable;
- ten alternative deterministic random 32-unit subsets: 7/10 pass the R² gate; passing raw estimates span ~.968-.990; 3/10 fail applicability;
- all six fixed 300-second windows of the primary 32-unit subset fail the R² gate.

Earlier ad-hoc exploratory subsets gave different pass/fail patterns (including one 32-unit subset with R²>.94 and a 128-unit window split in which late windows passed). The standardized rerun did not reproduce that pattern. This strengthens, rather than weakens, the key feasibility finding: **which recorded neurons are selected materially changes whether the MR model is applicable in this mouse.**

Do not call this evidence for or against near-criticality. Synthetic event thinning and real fixed-unit thinning are different observation processes. The next calibration must explicitly simulate fixed neuron identities, heterogeneous rates/connectivity, and random fixed-neuron subsets before the real subset variability can be judged surprising.

### Three-step checkpoint

- Does the question still matter? **Yes.** “Near-critical cortex” is a substantive dynamical claim, and pooled/threshold-based versus individual/subsampling-aware evidence could change that interpretation.
- Can the next test change the conclusion? **Yes.** Fixed-neuron network simulations can show whether the apparent real subset instability is expected under the MR method's intended assumptions or signals a model/observation mismatch.
- Does progress justify another step? **Yes, narrowly.** One discovery mouse exposed a load-bearing calibration gap before confirmation was spent. Do not scan the remaining 11 mice until that gap is resolved.

## 2026-09-09 — C002 fixed-neuron calibration, stress tests, and stop

### Fixed-neuron calibration

After the first discovery mouse showed strong dependence on which 32 VISp neurons were selected, a post-outcome **method diagnostic** was specified. This is not confirmatory evidence because the simulation family was designed after one mouse was inspected.

`analysis/c002_fixed_neuron_calibrate.py` models 512 explicit neuron identities in eight modules, with fixed lognormal within-module event weights and random fixed 32-neuron observation subsets. It preserves the 4-ms bin and MR estimator/gate used previously.

- Common m=.98 with strong rate heterogeneity: **30/30 applicable**, R² .9974-.9997, m .9767-.9819.
- Static mixed module timescales m=.85,.90,.94,.96,.975,.985,.99,.995: **30/30 applicable**, R² .9866-.9998, applicable m .9711-.9966.

Thus fixed-neuron sampling and substantial static rate/timescale heterogeneity do not reproduce the Allen mouse's low-R² failures.

### State-switch stress test

Because primary literature reports state transitions in these Allen recordings, a second explicitly post-first-mouse method diagnostic used three fixed 300-s segments.

- Global `.90 -> .99 -> .90`: 30/30 full fits applicable, minimum R² .9860.
- Asynchronous module switches: 30/30 full fits applicable, minimum R² .9902.
- Every within-state segment fit also passes the .90 gate.

These deliberately simple state changes also fail to reproduce the real observation. This does **not** prove nonstationarity is irrelevant; it only says these prespecified branching-family stress cases are insufficient.

### C002 stop decision

C002 is stopped after one discovery mouse and before confirmation. Eleven eligible discovery mice and all 12 confirmation mice remain unopened.

The next move on C002 would require progressively richer post-outcome model invention (oscillations, refractory structure, latent state models, spatial coupling, etc.) until some simulation reproduces the first mouse. In a mature criticality debate, that is adaptive rescue rather than a clean discriminating experiment. Preserve the failure instead.

Reusable lesson: “subsampling-invariant estimator” is conditional on the dynamical/correlation model being applicable. Always gate the fit form itself on real data; a plausible raw near-one parameter is not evidence when the fit fails.

### Computational reproducibility

All four C002 result-producing scripts were executed twice with identical explicit inputs/seeds and reproduced byte-identical SHA-256 hashes:

- aggregate MR calibration: `4cbdc7249d6f60ac9aa9025a8add628af7b58d5930b8f4d38c04cdbff65e492b`;
- Allen session 767871931: `58d6b672550ece5843ea98d2643ab34b14b3c5c21aabe0552fea1873bc863365`;
- fixed-neuron calibration: `3757409dad78d6ac79e0b41f2f2d09277a4949c473b0e80f9f0fd37e5cfdb570`;
- state-switch calibration: `6e0150da212fd74d65e0c5a4bdb7244bafe84b3dfabdc8a2e08d460b4af5ba20`.

### Tool/engineering failures

- LocalMCP has no AWS CLI; unsigned S3 HTTP listing/range reads were used instead.
- First remote HDF5 attempt lacked `aiohttp`; adding the explicit dependency fixed it before spike access.
- An initial fixed-neuron calibration exceeded a 120-s command limit without producing a result; the exact design was preserved and rerun with a bounded 300-s execution allowance, completing in ~125 s.
- Inspecting `mrestimator.coefficients.sm_method` initially failed because the package-level name resolves to the exported function rather than the module; `importlib.import_module` fixed the source inspection.
