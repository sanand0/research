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
