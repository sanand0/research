# Prompts

<!--

cd ~/code/research/foss-united-outcomes/
dev.sh -v /home/sanand/Dropbox/notes/transcripts:/home/sanand/Dropbox/notes/transcripts
codex --yolo

-->

<!-- Prompts are from https://chatgpt.com/c/6a069fcf-e2bc-83ec-8d4d-4ced66ed2a96 -->

Create a TSV file that has 1 row per project funded by FOSS United, with these columns:

- Project
- Sustenance
- Contributors
- Usage
- Quality
- Community
- Funding (INR)
- Resources
- Skills
- Grant Year

````markdown

The best plan is to create two files:

1. A working evidence sheet with extra columns for URLs, notes, and raw metrics.
2. A final clean TSV with exactly the requested columns.

The TSV should be a compact “impact + support” file, while the evidence sheet makes the values defensible.

## 1. Define the columns as outcomes vs inputs

Use the transcript’s logic:

Outcome columns:

`Project`
Canonical project name.

`Sustenance`
Whether the project can continue without fresh grant funding or heroic maintainer sacrifice. Use: `Yes`, `Partial`, `No`, `Unknown`.

`Contributors`
Contributor health. Suggested rule: number of non-maintainer contributors who made meaningful contributions across at least two different months in the last 6–12 months. Use: `Healthy`, `Thin`, `Maintainer-only`, `Inactive`, `Unknown`.

`Usage`
Evidence that the project has real users in its niche. Use: `High`, `Moderate`, `Low`, `Unknown`, with compact evidence in the cell if needed, e.g. `High; 5k-10k F-Droid downloads/week`.

`Quality`
Whether the project feels mature enough for serious users: docs, releases, UX, tests, security posture, installability, issue response. Use: `Mature`, `Usable`, `Rough`, `Dormant`, `Unknown`.

Input/support columns:

`Community`
What FOSS United did to help create discovery, adoption, or community around the project. Examples: `FOSS Hack`, `Season of Commits`, `Conference showcase`, `Maintainer network`, `Corporate intro`, `None known`.

`Funding (INR)`
Only FOSS United funding, not external ecosystem funding unless FOSS United directly disbursed it. For Rethink DNS, based on the transcript, this would be `1000000`, not including the Zerodha FLOSS Fund $25k unless you explicitly decide to track ecosystem funding too.

`Resources`
Non-cash support: cloud/GPU/tool credits, co-working space, travel scholarship, infra support, FOSDEM booth, subscriptions, etc.

`Skills`
Training or mentorship provided: security, compliance, accessibility, UX, docs, AI/data guidance, open-source governance, project management.

`Grant Year`
Since the TSV is one row per project, allow multiple years separated by semicolons, e.g. `2023; 2025`.

## 2. Use a simple reproducible rubric

For each project, fill the outcome columns using this rule:

`Yes/Healthy/High/Mature` only when there is visible evidence.

`Partial/Thin/Moderate/Usable` when there is some evidence but still a dependency, risk, or immaturity.

`No/Maintainer-only/Low/Rough` when evidence clearly points downward.

`Unknown` when the public evidence or FOSS records are insufficient.

This is important because the transcript explicitly asks for values that are “defensible” and “reproducible,” not vibes or 1–10 ratings.

## 3. Build the project master list first

Start from FOSS United’s internal grants records, not GitHub search. For each grantee, capture:

Project name
Maintainer name(s)
Grant amount(s)
Grant year(s)
Grant purpose
Project URL / repo URL
Any FOSS United program touchpoints: FOSS Hack, Season of Commits, FOSDEM, travel scholarship, maintainer program, etc.

Then deduplicate by project. If a project received two grants, keep one row and aggregate `Funding (INR)` and `Grant Year`.

## 4. Collect evidence in a working sheet

Before producing the TSV, create an audit sheet with these temporary evidence columns:

`Project URL`
`Repo URL`
`Grant Notes`
`Sustenance Evidence`
`Contributor Evidence`
`Usage Evidence`
`Quality Evidence`
`Community/Support Evidence`
`Reviewer`
`Confidence`

These columns should not go into the final TSV, but they are necessary to resolve disagreements between Anand and Ansh.

## 5. Evaluate each outcome column with concrete signals

For `Sustenance`, look for:

Paid plans, donations, sponsorships, consulting model, grants runway, institutional backing, active maintainer employment risk. The key question from the transcript is: “If grants stop, can this project continue without the maintainer jumping through hoops?”

For `Contributors`, look for:

GitHub/GitLab contributors in the last 6–12 months, PRs from non-maintainers, repeat contributors across multiple months, issue triage by non-maintainers, active maintainers beyond founder(s).

For `Usage`, look for:

App downloads, package downloads, Docker pulls, GitHub stars as weak evidence, real deployments, public users, institutional adoption, testimonials, community mentions, traffic if available.

For `Quality`, look for:

Recent releases, working install instructions, docs, tests, CI, security posture, issue response, UX maturity, packaging, roadmap visibility, contributor guide.

## 6. Fill inputs from FOSS United records, not public guessing

The input columns need internal knowledge from Ansh/FOSS United:

`Funding (INR)` should come from grant records.

`Community` should come from program participation: FOSS Hack, Season of Commits, maintainer community, conference showcase, discovery help, corporate adoption help.

`Resources` should include concrete non-cash support: infra credits, travel, workspace, tools, subscriptions, FOSDEM stand, introductions.

`Skills` should include concrete training or mentorship: security, compliance, accessibility, UX, documentation, AI/data help.

If FOSS United did not provide or does not know, use `None known` rather than leaving it blank.

## 7. Use independent evaluation, then reconcile

From the transcript, the right process is:

Ansh fills the sheet based on internal context.

Anand independently fills it using public evidence and any available grant notes.

Compare mismatches.

For every mismatch, classify the reason:

Public evidence missing
Internal context unavailable to Anand
Rubric ambiguity
Project has changed recently
Subjective judgment difference

Then update the rubric, not just the cell. This will make the evaluation more reusable.

## 8. Produce the final TSV

Final TSV should have exactly this header:

```tsv
Project	Sustenance	Contributors	Usage	Quality	Community	Funding (INR)	Resources	Skills	Grant Year
```

Example row from the transcript, with uncertainty preserved:

```tsv
Rethink DNS	No; working on subscriptions but not yet self-sustaining	Thin/Unknown; check repeat non-maintainer contributors	High; F-Droid usage reportedly 5k-10k downloads/week	Mature/Usable; popular app with active usage	Unknown/maintainer support	1000000	Cloud-cost support; maintainer support	Unknown	2023; 2025
```

For multi-value cells, use semicolons. Avoid tabs and line breaks inside cells.

## 9. Recommended first pass

Do a fast first pass over all ~20 grantees with only four values per outcome:

`Yes`, `Partial`, `No`, `Unknown`.

Then do a second pass only for the “highlight” and “uncertain” projects, adding compact evidence phrases.

This avoids getting stuck on perfect measurement before you have a usable impact map.

## 10. What this TSV enables

The final file can support three decisions:

Which projects show strong impact and should be highlighted to donors.

Which projects are promising but need non-cash help: contributors, adoption, skills, resources.

Which grants had unclear impact and need better grant design or follow-up metrics.

The most useful framing is: “For each rupee and each non-cash intervention, what changed in project sustainability, contributor health, usage, and quality?”

````

Use sub-agents for token-efficiency.

---

You produced a useful first-pass TSV for FOSS United-funded projects. Now revise it into a defensible impact-evaluation dataset aligned with this objective:

Create a TSV with 1 row per project/grantee funded by FOSS United, showing what FOSS United support appears to have produced in terms of sustenance, contributor health, usage, and quality, plus what inputs FOSS United provided.

Important context:
- This is not just a directory of grantees. It is a donor/impact artifact.
- Anand and Ansh want values that are defensible and reproducible enough that two people can independently fill the sheet and reconcile differences.
- FOSS United’s goal is to strengthen the Indian FOSS ecosystem through grants, maintainer support, discovery, community-building, and non-cash support.
- Anand’s goal is to understand and communicate grant impact: “I gave money; what good did it do, which projects should be highlighted, and which projects need more help?”

Please improve the output in 6 steps.

STEP 1 — Rebuild the canonical grantee list
Use official FOSS United sources first:
- current grants pages
- all grantees page
- annual grant recap posts
- archived FOSS United grant pages if needed
- FOSS Hack / fellowship pages only if the grant was directly for a project or maintainable FOSS artifact

Create an internal audit list with:
Project/Recipient
Grant type: project / infrastructure / community / fellowship / hackathon / organization / public-interest nonprofit / unclear
Official grant amount
Official grant year
Announcement date if different
Source URL

Deduplicate by project/recipient. If there are multiple grants to the same project, keep one final row and sum FOSS United-administered funding.

Do not include event grants unless the funded object is itself a FOSS project or durable FOSS/community infrastructure.

STEP 2 — Fix the meaning of Funding (INR)
The final `Funding (INR)` column must include only FOSS United-administered INR funding.

Do not include external FLOSS/fund, GitHub Sponsors, OpenCollective, unrelated donations, or other ecosystem funding in `Funding (INR)` unless the official FOSS United record says FOSS United administered that amount.

If a grant was co-sponsored by Zerodha but appears on FOSS United’s official grant record, include it, but record the co-sponsor only in the evidence notes.

For Rethink DNS, do not add the later $25,000 FLOSS/fund grant into `Funding (INR)`. Mention it only as sustenance evidence.

Use integer rupees without commas, e.g. `1000000`.

STEP 3 — Apply a strict rubric
Use the following controlled vocabulary unless the cell includes a short evidence note.

Sustenance:
- `Yes` = can plausibly continue without fresh FOSS United grant funding, via revenue, donations, institutional backing, broad volunteer base, or durable org support.
- `Partial` = active and has some runway/support model, but still materially dependent on grants, one or two heroic maintainers, or unstable donations.
- `No` = unlikely to continue meaningfully without fresh grant/maintainer sacrifice, or appears dormant.
- `Unknown` = public/internal evidence insufficient.

Contributors:
- `Healthy` = multiple meaningful non-founder/non-funded contributors or organizers active across time; not bus-factor-one.
- `Thin` = more than one person involved, but repeat contribution depth is weak or unclear.
- `Maintainer-only` = primarily one maintainer or funded maintainer(s).
- `Inactive` = little/no recent contribution evidence.
- `Unknown` = cannot determine.

For code projects, prefer evidence like non-maintainer PRs/commits/issues across at least two different months in the last 6–12 months.
For community/org grants, use repeat organizers, active chapters, ongoing volunteers, or documented program participation.

Usage:
- `High` = strong usage in its niche, with quantified evidence or credible institutional/community adoption.
- `Moderate` = visible users/adoption, but limited quantification or niche reach.
- `Low` = little visible adoption beyond demo/hackathon/stars.
- `Historical` = meaningful past usage but current usage unclear.
- `Unknown` = insufficient evidence.

Do not treat GitHub stars alone as usage. Stars can support a claim but cannot be the only basis.

Quality:
For software projects, assess docs, installability, releases, tests/CI, issue response, security posture, packaging, UX, and production readiness.
For community/org/nonprofit grants, assess program maturity, transparency, continuity, public outputs, governance, and reproducible community infrastructure.

Use:
- `Mature`
- `Usable`
- `Rough`
- `Dormant`
- `Unknown`

STEP 4 — Preserve evidence separately
Produce two outputs:

A) `projects.tsv` with exactly these columns and no extra columns:
Project
Sustenance
Contributors
Usage
Quality
Community
Funding (INR)
Resources
Skills
Grant Year

B) `evidence.tsv` with these columns:
Project
Project Type
Official FOSS United Source URL
Project URL
Repo URL
Grant Evidence
Sustenance Evidence
Contributor Evidence
Usage Evidence
Quality Evidence
Community Evidence
Resources Evidence
Skills Evidence
External Funding Evidence
As Of Date
Confidence
Reviewer Notes

The final `projects.tsv` can contain compact values like:
`High; 500k+ Play Store downloads`
But all detailed justification must go into `evidence.tsv`.

STEP 5 — Correct specific likely problems in the previous output
Review and correct these issues:

- Separate project, organization, community, and public-interest nonprofit rows. Do not apply a pure GitHub-project rubric to VGLUG, TinkerHub, IFF, SMC, or FSCI.
- Verify whether “Free Software Community of India” vs “Free Software Services of India” is the correct official name in the grant record. Use the official name in `Project`, and aliases in evidence notes.
- Verify whether Fika lang should be included as a project grant, FOSS Hack grant, or excluded from the main project-grants list. If included, mark the grant type clearly in evidence.
- Verify Rethink DNS grant years using official FOSS United records. If the official page says 2024 but the announcement is Jan 2025, use the official grant year in `Grant Year` and note the announcement date in evidence.
- Do not mark “Yes” for sustenance merely because a donation page exists.
- Do not mark “Healthy” contributors merely because an organization has many repos or a community has existed for years. Tie the label to active, repeat contributors/organizers.
- Do not mark “Mature” quality for orgs based only on legal registration; use outputs, transparency, program continuity, and public artifacts.
- Do not infer “FOSDEM support” unless there is direct evidence that this specific project received that support.
- For every `Unknown`, explain exactly what evidence is missing.

STEP 6 — Add impact-usefulness
For each row, make the cells useful for three decisions:
1. Should donors highlight this as an impact story?
2. What follow-up support would help most: funding, contributors, adoption, resources, or skills?
3. Is the grant outcome clear, unclear, or disappointing?

Do not add new columns to `projects.tsv`, but encode compact signals in existing columns where useful.

Examples:
- `Sustenance`: `Partial; subscriptions emerging`
- `Contributors`: `Thin; 2 maintainers, repeat external unclear`
- `Usage`: `High; 500k+ Play Store downloads`
- `Resources`: `Infra-cost support; maintainer runway`
- `Skills`: `Unknown; check if security/UX/AI mentoring provided`

Output:
1. Revised `projects.tsv`
2. Revised `evidence.tsv`
3. A short `methodology.md` explaining the rubric, inclusion/exclusion rules, known limitations, and questions for Ansh/FOSS United.

Be conservative. Prefer `Unknown` over confident but weak claims. Prefer exact official grant records over public guesses. Make the dataset boringly defensible.

---

`ansh.tsv` was filled by Ansh. Where are the discrepancies between your responses and his? Keep in mind that Ansh may have access to private information. Create an inventory of the gaps, sorted by most important first.
