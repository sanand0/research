# Methodology

## Scope

This dataset is an impact-evaluation first pass, not a complete grantee directory. It includes:

- Official FOSS United project grants from `https://fossunited.org/grants/projects`.
- Direct fellowships or Season of Commits grants when the funded object is a FOSS project, durable FOSS artifact, digital commons, or community infrastructure.
- Direct project-showcase grants from the 2025 grants recap when FOSS United funded a named FOSS project to showcase at an external event.

It excludes ordinary event grants and scholarships that do not directly fund a FOSS project, durable artifact, or FOSS/community infrastructure. Examples excluded from the final TSV: generic event grants, YLAC course-fee scholarships, and the graduate public-policy course line that the recap says is outside the grants pool.

## Funding Rules

`Funding (INR)` includes only FOSS United-administered INR amounts from official FOSS United records. Co-sponsored grants listed on FOSS United records are included because FOSS United administered them; the co-sponsor is only noted in `evidence.tsv`.

External funding such as GitHub Sponsors, OpenCollective, FLOSS/fund, Mozilla, OSOM, donations, product revenue, or hosting sponsorships is not added to `Funding (INR)`. It is recorded only as sustenance or external-funding evidence.

For Rethink DNS, the official project-grants page lists `2023` and `2024`; the Jan 2025 follow-on announcement is treated as announcement timing, not grant year. The 2025 FOSDEM showcase travel grant is included separately because the 2025 recap directly names RethinkDNS@FOSDEM and gives an INR amount.

## Rubric

Sustenance:

- `Yes`: Can plausibly continue without fresh FOSS United grant funding through revenue, donations, institutional backing, broad volunteer base, or durable organization support.
- `Partial`: Active and has some support model, but still materially depends on grants, unstable donations, or one/two heroic maintainers.
- `No`: Appears dormant or unlikely to continue meaningfully without fresh grants/maintainer sacrifice.
- `Unknown`: Evidence insufficient.

Contributors:

- `Healthy`: Multiple meaningful non-founder/non-funded contributors or repeat organizers active across time.
- `Thin`: More than one person involved, but repeat contribution depth is weak or unclear.
- `Maintainer-only`: Primarily one maintainer or funded maintainer(s).
- `Inactive`: Little or no recent contribution evidence.
- `Unknown`: Cannot determine.

Usage:

- `High`: Strong usage in niche with quantified evidence or credible institutional/community adoption.
- `Moderate`: Visible users/adoption, limited quantification, or niche reach.
- `Low`: Little visible adoption beyond demo, hackathon, or stars.
- `Historical`: Meaningful past usage but current usage unclear.
- `Unknown`: Insufficient evidence.

Quality:

- Software: docs, installability, releases, tests/CI, issue response, security posture, packaging, UX, and production readiness.
- Community/org/nonprofit: program maturity, transparency, continuity, public outputs, governance, and reproducible community infrastructure.
- Labels: `Mature`, `Usable`, `Rough`, `Dormant`, `Unknown`.

GitHub stars alone were not used as usage evidence. They are treated only as weak visibility/context evidence.

## Known Limitations

This is conservative and public-evidence biased. It is likely to understate impact where FOSS United or maintainers have private reports, internal grant updates, community metrics, spending records, or before/after evidence.

Contributor health is the weakest field for several rows. A stronger pass should inspect non-maintainer commits/PRs/issues over the last 6-12 months for code projects and repeat organizer/volunteer activity for community grants.

Non-cash support is probably under-recorded. Unless a public FOSS United source directly mentioned FOSDEM, infrastructure, storage drives, mentorship, or travel, the field is marked `Unknown; check...`.

Fellowships are included only when they appear tied to a durable FOSS artifact, public digital commons, FOSS education artifact, or community infrastructure. This boundary should be reviewed by FOSS United.

## Questions For Ansh / FOSS United

1. For each `Unknown; check...` cell, did FOSS United provide non-cash support such as cloud credits, hardware, space, introductions, security review, UX review, accessibility review, compliance help, or governance mentoring?
2. Which grants had formal milestones or completion reports, and can those URLs be added to `evidence.tsv`?
3. Which projects should be marked as donor highlights based on internal evidence not visible publicly?
4. Which projects need follow-up support most: funding, contributors, adoption/discovery, resources, or skills?
5. Should direct project-showcase grants like Ente@FOSDEM and Vibinex@Ubucon remain in this impact dataset, or be tracked in a separate support-interventions sheet?
6. For Free Software Community of India/FSCI, should the canonical project name follow the 2026 official record, or should the 2023 alias remain canonical for continuity?
