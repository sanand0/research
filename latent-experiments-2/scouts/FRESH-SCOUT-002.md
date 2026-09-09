# Fresh discrepancy scout 002 — intervention-enabled, no survivor

Date: 2026-09-09

## Outcome

**No candidate cleared the full scientific-identifiability + prior-art + open-evidence gate.** This scout was deliberately stricter than scout 001: a computationally attractive disagreement is not enough if the decisive variable is unmeasured or the proposed discriminator uses the same proxy whose meaning is disputed.

No substantive raw outcome table was opened for any candidate below.

## C007 — sea-star wasting disease causation

### Disagreement

Prentice et al. (2025, Nature Ecology & Evolution, DOI `10.1038/s41559-025-02797-2`) report controlled challenge experiments in which *Vibrio pectenicida* strain FHCF-3 induced sunflower sea-star wasting disease (SSWD). Work et al. (2026, DOI `10.1038/s41559-026-03091-5`) argue that the gross wasting case definition does not establish that the bacterium causes the lesion-generating tissue process; they call for microscopy/pathology linking bacteria spatially to lesion development. The authors reply (DOI `10.1038/s41559-026-03092-4`) that such pathology would be useful and state that experimental samples were retained for pathological examination.

Earlier histopathology work is an important control: wasting-like gross lesions can be experimentally reproduced by non-infectious organic material, so gross lesion morphology is not pathogen-specific.

### Cheapest decisive discriminator

Pathogen burden/localization in the relevant tissue should precede or spatially co-localize with lesion formation in exposed animals and not in matched controls. A stronger version would use serial tissue pathology before gross clinical signs.

### Open-evidence gate

- Dryad DOI `10.5061/dryad.5mkkwh7g9`, current version 19, is CC0 and only ~1.2 MB.
- Metadata expose separate figure/data bundles, gross disease trajectories, animal/sample IDs and coelomic-fluid sequencing summaries; sequencing is also archived under NCBI BioProject `PRJNA1195080`.
- The public dataset does **not** contain the lesion histology/spatial pathogen localization requested by the critique.
- Documented post-exposure sequencing samples are collected at/around substantial clinical signs rather than as a clean preclinical temporal series.
- Dryad API file metadata were accessible; direct file content through the API returned 401 during feasibility. No numeric outcome rows were downloaded.

### Decision

**REJECT C007 BEFORE OUTCOMES.** A computational reanalysis of coelomic-fluid abundance plus gross disease timing cannot answer the expert disagreement because the load-bearing pathology measurement was never made/publicly released. The authors themselves describe retained material for future pathology, which is effectively the missing experiment.

Reusable lesson: when a scientific dispute concerns *what was measured*, more sophisticated analysis of a correlated proxy does not create the missing observation.

## C008 — ReDeeM mitochondrial lineage-tracing artefacts

### Disagreement

Lareau et al. (2026, Nature, DOI `10.1038/s41586-026-10777-0`) argue that low-support, fragment-end-enriched mitochondrial variants in ReDeeM can create spurious cell connections and unstable phylogenies. Weng, Weissman & Sankaran reply (DOI `10.1038/s41586-026-10776-1`) that these variants preserve mitochondrial mutational signatures and that biological conclusions remain robust under alternate filters/alignment choices.

Data are public at GEO `GSE219015`; both sides publish analysis code.

### Initially attractive discriminator

Choose filtering rules without looking at biological conclusions, then score lineage reconstruction against an orthogonal lineage ground truth (CRISPR/lentiviral barcode), reserving a separate sample for confirmation.

### Prior-art gate

This exact idea is already substantially executed. The 2026 author reply evaluates alternate filtering, one-molecule variants, edge trimming and agreement with CRISPR lineage tracing. Independent 2026 MitoDrift work also benchmarks ReDeeM filtering regimes against orthogonal lineage ground truth and reports performance differences among filters.

### Decision

**REJECT C008 ON DISCRIMINATOR-SPECIFIC PRIOR ART.** Re-running a cleaner filter benchmark would be useful software validation, not a new scientific loop.

## C009 — parity signal versus superconducting-gap robustness in InAs–Al devices

### Disagreement

Microsoft's 2025 Nature paper (DOI `10.1038/s41586-024-08445-2`) reports h/2e-periodic bimodal quantum-capacitance random-telegraph signals interpreted as fermion-parity readout. Legg (2026, DOI `10.1038/s41586-026-10567-8`) argues that the transport data place parity measurements in highly disordered, apparently gapless regions, inconsistent with a superconducting-parity interpretation. Microsoft's reply (DOI `10.1038/s41586-026-10568-7`) argues that finite subgap local conductance in the strong-coupling regime does not directly imply finite density of states, and that a stable h/2e-periodic bimodal RF signal itself is inconsistent with a gapless system.

### Operational feasibility

- Original data/code are exceptionally transparent: Zenodo `10.5281/zenodo.14804380` plus GitHub `microsoft/azure-quantum-parity-readout`.
- The archive is ~96.5 GB total, but TGP tune-up is a separate ~20 MB ZIP and converted parity data are in a ~4.8 GB shared ZIP; raw A2 parity traces alone are ~10 GB.
- Code inspection (no measured values) shows A2 parity data include a `V_wire` dimension and the published A2 parity operating point (`V_wire≈-1.8446 V`) lies inside the A2 TGP wire-plunger range (`-1.846` to `-1.841 V`). TGP data are separately available for A1, A2 and B1, so in principle A2 could be discovery and B1 an independent physical-device confirmation.
- Zenodo access from LocalMCP timed out during this scout, so selective range extraction was not demonstrated.

### Initially attractive discriminator

Across matched `(B_parallel, V_wire)` settings, ask whether parity-bimodality quality deteriorates as an independently measured superconducting gap collapses; discover on A2 and confirm on B1.

### Scientific-identifiability failure

The obvious “gap robustness” quantity in the archived transport experiment is *not independent*: its interpretation is exactly what the two sides dispute. Legg treats finite low-bias conductance as evidence for low-energy states/gaplessness; Microsoft argues strong-coupling Andreev enhancement invalidates that inference and that the RF signal itself constrains the spectrum. Correlating parity quality with the same contested conductance-derived proxy would therefore not decide which physical interpretation is correct.

A decisive test needs an orthogonal spectroscopic gap observable acquired at the same tuning points. A 2026 Microsoft InAs–Pb experiment introduces a more direct RF energy-splitting measurement, but it is a different device/material and cannot ground-truth the 2025 Al-device phase space retrospectively.

### Decision

**REJECT C009 BEFORE MEASURED OUTCOMES.** It is technically sophisticated but scientifically non-identifying with the available measurements. The data-volume/live-access burden is an additional, secondary penalty.

## Three-step assessment

1. **Did scout 002 find a consequential live disagreement? Yes — several.** Sea-star pathology and topological-gap interpretation are real, explicit expert disagreements.
2. **Can the available public evidence run the decisive test? No.** C007 lacks tissue pathology; C009 lacks an independent gap observable. C008 has the needed ground truth but the discriminator is already published.
3. **Does further polishing help? No.** It would turn missing measurements into proxy analysis or prior-art replication. Redirect.

## Search correction for scout 003

The next scout should ask **“is the decisive observable already in the public data?” before ranking a candidate**. Prefer experiments with orthogonal measurements collected simultaneously or paired interventions where one measurement directly grounds the mechanism. Good forms include:

- paired instrument A/B measurements plus a third independent reference standard;
- randomized perturbation with a measured mediator and outcome, allowing mediation-vs-selection predictions;
- lineage/barcode experiments with pre-perturbation state and post-perturbation fate measured on the same independent units;
- natural experiments with a genuinely unaffected control and a directly measured intermediate mechanism.

Reject a candidate before implementation if the central dispute is about an unmeasured latent variable and every available quantity is a disputed proxy.
