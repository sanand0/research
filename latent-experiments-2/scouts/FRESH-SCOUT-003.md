# Fresh discrepancy scout 003 — no survivor

Date: 2026-09-09

## Outcome

**No candidate survived the measurement-completeness + discriminator-prior-art + independent-confirmation gate.** No substantive numeric outcomes were opened for C010 or C011.

Scout 003 changed the order of screening: identify the decisive observable first; verify that discovery and an independent confirmation source preserve it at the required unit; then search the exact discriminator before downloading outcomes.

## C010 — MuST-C indirect versus destructive LAI discrepancy

### Why it looked promising

MuST-C (Chong et al. 2026, *Scientific Data*, DOI `10.1038/s41597-025-06462-y`) reports disagreement between indirect SunScan LAI and destructive green-leaf LAI and explicitly proposes two mechanisms:

1. **spatial representativeness** — heterogeneous plots, especially maize/soybean, make a localized destructive sample less representative while SunScan averages multiple locations;
2. **measurement-definition / senescence** — SunScan light interception can include brown/senescent vegetation, while destructive LAI retains green leaves, producing late-season positive indirect bias especially in wheat.

The decisive observables exist in MuST-C itself: repeated SunScan measurements, destructive LAI, plot/date/crop metadata and destructive-sample locations. The BonnData reference-data bundle is separately downloadable from the multi-terabyte imagery and is only ~2.06 MB. Repository/code/manifest structure was inspected; **numeric LAI values were not downloaded or opened.**

### Independent-confirmation gate

A targeted search found Edinburgh DataShare DOI `10.7488/ds/2989` (Revill et al. 2021), an independent Scottish winter-wheat trial with SunScan LAI and direct Li-Cor destructive LAI. The archive is open and exposes the relevant files separately.

However its README establishes an incompatible unit structure:

- SunScan LAI observations are already averaged across **50 trial plots** for each date x nitrogen treatment;
- destructive LAI is measured from **five plots**.

Therefore the archive discards the same-unit spatial information required to distinguish the spatial-mismatch mechanism from senescence. It could compare aggregate methods but cannot confirm the proposed mechanism decomposition.

A final bounded search found published SunScan/destructive comparisons and controlled-access/aggregated archives, but no independent open dataset preserving raw same-unit indirect + destructive green-LAI measurements with sufficient phenology.

**Decision: REJECT C010 BEFORE OUTCOME ACCESS.** Do not use crop splitting within MuST-C as “independent confirmation”; that would be an arbitrary within-trial holdout after the external-confirmation gate failed.

## C011 — pulse-oximetry pigmentation versus anatomy/perfusion

### Why it looked promising

OpenOximetry / UCSF controlled-desaturation data provide unusually strong direct observables: arterial blood-gas SaO2 reference, simultaneous pulse-oximeter SpO2, objective spectrophotometric skin pigmentation, participant/device metadata and physiologic covariates. A possible question was whether apparent pigmentation-related error is better explained by objective pigmentation itself versus finger anatomy/perfusion and hypoxemia.

No OpenOximetry numeric outcomes were accessed.

### Discriminator-specific prior-art rejection

The exact mechanism is already mature:

- controlled-desaturation work has used repeated-measures multivariable models showing **skin pigmentation, perfusion and hypoxemia jointly contribute to pulse-oximeter error**;
- the 2026 34-device controlled-desaturation study (Hughes et al., DOI `10.1213/ANE.0000000000008048`) objectively measures ITA pigmentation, finger diameter and percent infrared modulation/perfusion while comparing device-specific differential bias;
- the 2026 EquiOx prospective ICU study directly compares simultaneous SpO2/SaO2 with objective pigmentation and adjusts for perfusion index.

Thus “is pigmentation really perfusion/anatomy?” is not a fresh discriminator enabled by the new repository; it would be a reanalysis within an actively studied multivariable problem.

**Decision: REJECT C011 ON PRIOR ART BEFORE OUTCOME ACCESS.**

## Other screened direction

A synchronized 60-GHz radar/ECG/accelerometry dataset with breath-hold and post-exercise conditions passed measurement-completeness/size checks, but respiration harmonics, motion artifacts and breath-hold isolation are already standard radar-vital-sign validation questions. It was not promoted or assigned a claim ID.

## Scout 003 conclusion

No survivor.

The new reusable distinction is:

> **Measurement completeness has two levels: variable completeness and unit alignment.** It is insufficient for dataset A and dataset B to contain the same variables if the confirmation source has averaged away the unit-level pairing needed by the discriminator.

A second repeated lesson is that an exceptionally rich open dataset is not a discovery opportunity when its proposed mechanism already has direct multivariable prior art.

## Next search correction

Fresh scout 004 should de-emphasize flagship controversies and generic instrument-bias questions. Prefer **recent replicated interventions with multiple independent batches/sites and an unresolved heterogeneous response**, where:

1. intervention, mediator and outcome are all directly observed on the same experimental unit;
2. at least two independent batches/sites/files already exist with identical measurement semantics;
3. the disagreement concerns the *pattern of treatment response*, not an unmeasured latent mechanism;
4. exact heterogeneity/discriminator prior art is searched before code or outcome access;
5. the primary data needed for a live test are <1 GB and public without interactive authentication.
