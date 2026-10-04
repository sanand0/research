# Longevity headline factories

Research update: 2026-10-03.

The target is not just another surprising mortality paper. It is a **headline factory**: one public cohort with mortality follow-up and many plausible exposures measured together, so we can ask whether the published “X helps you live longer” headline is special or merely one attractive result among many.

The most useful design is:

> Pick a published exposure, reproduce its mortality association, then run the same prespecified model over every comparable exposure in that survey and show the full distribution.

This differs from ordinary robustness checking. It exposes the *latent choice of what to write the paper about*.

## Recommendation

| Rank | Dataset / published hook | Counterexample potential | Data friction | Why it is useful |
|---|---|---|---|---|
| **1** | **NHANES — chili / tea / coffee / sleep / teeth / religion → mortality** | **Very high** | **Very low** | One public mortality pipeline supports dozens to hundreds of exposures and already has many published “X predicts longevity” headlines |
| **2** | **HRS/CAMS — reading books → 20% lower mortality** | **Very high** | **Low: free account** | Same questionnaire measures ~31 everyday activities in hours: TV, music, walking, prayer, gardening, pets, affection, puzzles, concerts, volunteering, etc. Almost ideal matched counterexamples |
| **3** | **MIDUS — purpose in life → longer life** | **Very high** | **Low/moderate: public ICPSR/NACDA, account/terms** | Thousands of variables and many adjacent psychological/social scales; several have already been separately linked to mortality |
| **4** | **NHIS — hearing difficulty → mortality** | **High** | **Very low** | Huge public samples and public mortality files. Excellent power and many survey exposures, though alternative headlines are often less whimsical |
| **5** | **CLHLS — leisure activities → mortality** | **Already demonstrated** | **Moderate: request/access workflow** | A single paper finds six unrelated leisure activities all predict lower mortality. Excellent positive example of common-cause/healthy-participant structure |
| **6** | **ELSA — sustained enjoyment of life → mortality** | **Medium-high** | **Moderate: UK Data Service registration** | Rich social/wealth/health/psychology survey, but less frictionless and counterexamples are less immediately funny |
| **Hold** | **GSS-NDI — happiness / TV / trust → mortality** | **Very high** | **Currently uncertain** | Conceptually perfect, but current GSS/NCHS sharing changes make exact survival-data access less straightforward than older papers imply |

**NHANES and HRS/CAMS are now both executed.** The frozen 60-food NHANES III scan finds 21/60 foods FDR-significant while hot red chili ranks 28th; see [nhanes3-food-scan.md](nhanes3-food-scan.md). The independent HRS/CAMS scan near-replicates the published book effect (HR 0.816 vs 0.80) but finds 18/31 activities FDR-significant and books rank only 11th among 28 estimable contrasts; see [hrs-cams-scan.md](hrs-cams-scan.md). Together they make the exposure-selection argument much stronger than either alone.

---

## 1. NHANES: broaden from “food headline factory” to “mortality headline factory”

### Why this is stronger than chili alone

The linked mortality data are public for:

- NHANES III;
- continuous NHANES 1999–2018;
- 2017–March 2020 pre-pandemic NHANES.

CDC says mortality status itself is unchanged in the public-use files, although for some records follow-up time or underlying cause of death is replaced with synthetic values for disclosure protection.

Current linked-mortality page:
https://www.cdc.gov/nchs/linked-data/mortality-files/index.html

One data-loading and survey-weighted Cox pipeline can therefore support many headline classes.

### Published hooks already in the same ecosystem

#### Chili peppers → longer life

Chopan & Littenberg, PLOS ONE 2017:
- 16,179 NHANES III adults.
- Adjusted mortality HR about 0.87 for hot-red-chili-pepper consumers.
- The paper describes an 81-item food-frequency questionnaire. In the public adult file, 60 predefined named items share a directly comparable “times/month” field; these form the clean frozen counterexample family used in our scan.

https://doi.org/10.1371/journal.pone.0169876

#### Tea → longer life

Tian et al., Nutrition Journal 2024:
- NHANES 2001–2018, N=43,276; 6,275 deaths.
- 3 to <5 cups/day: all-cause mortality HR 0.79 versus non-drinkers.
- Estimated life expectancy at age 50: 32.93 years for 3–<5 cups/day versus 30.69 years for non-drinkers.
- But <1 cup, 1–<3 cups, and >=5 cups did not show the same significant all-cause result; >=5 cups had estimated life expectancy 29.68 years.

https://pmc.ncbi.nlm.nih.gov/articles/PMC11603940/

This is an especially good example of researcher degrees of freedom in **dose binning and curve shape**: the memorable headline depends on the middle-high consumption category.

#### Coffee → longer life

Recent NHANES analyses again report lower mortality among coffee drinkers. One NHANES 2001–2018 analysis reports a U-shaped association, with roughly 2 cups/day giving the lowest estimated all-cause mortality risk.

https://pmc.ncbi.nlm.nih.gov/articles/PMC12516614/

A 2025 NHANES analysis also splits coffee by caffeination, added sugar, saturated fat, and dose.

https://pmc.ncbi.nlm.nih.gov/articles/PMC12308089/

This creates a large but superficially reasonable specification space before even leaving “coffee.”

#### Seven hours of sleep → longest life

NHANES 2005–2014 linked mortality:
- <=5 h: adjusted all-cause HR 1.28;
- 7 h: reference;
- 8 h: HR 1.21;
- >=9 h: HR 1.53.

https://pmc.ncbi.nlm.nih.gov/articles/PMC10301724/

Another analysis of essentially the same exposure reports somewhat different estimates/cut points while preserving a U-shaped story:
https://pmc.ncbi.nlm.nih.gov/articles/PMC9334887/

#### Keeping your teeth → longer life

A pooled NHANES analysis reports:
- 17–24 teeth: all-cause HR 1.19 vs 25–28;
- 1–16 teeth: 1.30;
- no teeth: 1.43;
- each 10 missing teeth: HR 1.13.

https://pmc.ncbi.nlm.nih.gov/articles/PMC9365626/

#### Going to religious services → longer life

NHANES III, adults 40+:
- weekly attendance: HR 0.82;
- >weekly: HR 0.70;
- versus never attending, after reported sociodemographic/health adjustment.

https://pmc.ncbi.nlm.nih.gov/articles/PMC2659561/

### Counterexample strategy

Rather than hand-pick ridiculous variables, define **families before looking at results**:

1. Food-frequency items.
2. Beverages and dietary-recall components.
3. Sleep and daily routines.
4. Social/religious behaviors.
5. Oral-health measures.
6. Physical measurements.
7. Lab biomarkers.

Within each family, fit one fixed model template to *every* eligible exposure.

The core chart should be:

> **“Things in NHANES that apparently help you live longer.”**

Each dot is an exposure using the same outcome/model, colored by whether a paper has already made that exposure the headline.

A stronger second chart answers:

> **How special is chili/tea/coffee compared with every other thing we could have chosen?**

### Likelihood of useful counterexamples: VERY HIGH

Reasons:
- Large sample sizes make modest associations detectable.
- Hundreds of correlated measures proxy health, wealth, age, diet quality, engagement, frailty, healthcare use, etc.
- Multiple published headline papers already exist in unrelated domains.
- Food/beverage exposures alone provide many semantically comparable choices.
- Continuous variables permit many reasonable codings: linear, quantiles, thresholds, splines, servings, log transformations.

The danger is that a completely unrestricted scan becomes intentionally bad science. The demo is strongest if the exposure family and one analysis template are frozen in advance.

---

## 2. HRS/CAMS: “Reading books makes you live longer”

Bavishi, Slade & Levy (Social Science & Medicine, 2016) used 3,635 participants in the U.S. Health and Retirement Study and followed mortality for up to 12 years.

Reported result:
- book-reading tertile 2: HR 0.83;
- tertile 3: HR 0.77;
- adjusted book readers overall had about 20% lower mortality than non-book readers;
- the authors report an advantage beyond newspapers/magazines.

Paper:
https://pmc.ncbi.nlm.nih.gov/articles/PMC5105607/

### Why HRS/CAMS may be even cleaner than NHANES pedagogically

The exposure came from the **2001 Consumption and Activities Mail Survey (CAMS)**. That same questionnaire asks how many hours respondents spend on a long list of activities.

The 2001 codebook includes, among others:

**Weekly**
- watch TV;
- read newspapers/magazines;
- read books;
- listen to music;
- sleep/nap;
- walk;
- sports/exercise;
- visit people;
- phone/letters/email;
- work for pay;
- use a computer;
- pray/meditate;
- clean the house;
- wash/iron/mend;
- yard work/gardening;
- shopping/errands;
- prepare/clean up meals;
- personal grooming;
- care for pets;
- physically show affection.

**Monthly**
- help others;
- volunteer;
- attend religious services;
- attend clubs/groups;
- manage money;
- medical self-care;
- play cards/games/solve puzzles;
- attend concerts/movies/lectures/museums;
- sing/play music;
- arts/crafts;
- home improvement.

2001 CAMS codebook:
https://hrs.isr.umich.edu/sites/default/files/meta/2001/cams/codebook/CAMS2001a_r.htm

Dataset page:
https://hrsdata.isr.umich.edu/data-products/2001-consumption-and-activities-mail-survey-cams

The dataset has 3,866 CAMS respondents and requires an HRS login/account to download.

### The obvious experiment

Use the book paper's cohort construction and covariates as closely as possible, but swap the focal exposure:

> “Do people who spend more time **gardening / caring for pets / hugging / listening to music / solving puzzles / attending concerts / volunteering / managing money** also live longer?”

Run every CAMS activity through the same prespecified transformation:
- none vs any;
- tertiles among participants, mirroring the book paper where possible;
- continuous standardized hours as a secondary analysis.

Then compare:
- effect direction;
- hazard ratio;
- confidence interval;
- rank among activities;
- robustness after the exact same covariate set.

### Why the counterexamples should be interesting

This survey is full of variables that are likely to be **markers of the ability to do things**.

For an older population, time spent gardening, shopping, visiting friends, volunteering, managing money, playing games, or attending concerts may all encode mobility, cognition, health, wealth, social connection, or lack of frailty.

That makes this stronger than deliberately silly random variables. If many pleasant activities predict longevity, the audience immediately sees the alternative explanation:

> Maybe books do not add years. Maybe people who are healthy enough to have an active life both read books and live longer.

Conversely, if book reading is unusually strong while matched activities are null, that is evidence **for** the specificity of the book result.

### Data availability: GOOD

- CAMS 2001: free account/login required.
- HRS core/tracker mortality variables: public HRS products with registration.
- Exact restricted NDI detail is unnecessary for an all-cause survival replication; public HRS products contain vital-status/death-timing variables suitable for published-style analyses.
- Small sample/data compared with NHANES.

### Likelihood of useful counterexamples: VERY HIGH

This is my favorite *single-paper* candidate because the alternatives are measured in the same questionnaire, often in the same units, equally understandable, plausibly correlated with healthy aging, and not contrived after the fact.

---

## 3. MIDUS: “Having a purpose in life makes you live longer”

Hill & Turiano (2014) used the Midlife in the United States (MIDUS) cohort and reported that people with greater purpose in life survived longer over roughly 14 years, even after controlling for several other psychological/affective well-being measures.

Paper:
https://pmc.ncbi.nlm.nih.gov/articles/PMC4224996/

### Why it is a rich headline factory

MIDUS is explicitly designed around psychological, social and biological predictors of aging. Its baseline survey contains a huge range of overlapping constructs such as:

- purpose in life;
- positive affect;
- negative affect;
- life satisfaction;
- self-esteem;
- autonomy;
- environmental mastery;
- personal growth;
- positive relations;
- self-acceptance;
- perceived control;
- agency;
- neuroticism;
- extraversion;
- conscientiousness;
- agreeableness;
- openness;
- social support;
- religious/spiritual measures.

The current MIDUS mortality release (version dated 2026-08-13) contains information for **2,822 known decedents through December 2025** and can be linked to the MIDUS core samples.

Current mortality data:
https://www.icpsr.umich.edu/web/NACDA/studies/37237

MIDUS series:
https://www.icpsr.umich.edu/sites/nacda/midus

ICPSR says most MIDUS series are public-use/direct-download; registration and data-use terms apply. As of March 2026, MIDUS public-use terms also prohibit uploading downloaded data to public external LLM services. That does not prevent local scripted analysis, but it matters operationally for this project.

### Existing literature already hints at the experiment

Separate MIDUS studies have linked mortality to:
- purpose in life;
- religious service attendance / spirituality;
- conscientiousness and other personality traits;
- socioeconomic status.

Examples:
- Purpose: https://pmc.ncbi.nlm.nih.gov/articles/PMC4224996/
- Religion/spirituality: https://pmc.ncbi.nlm.nih.gov/articles/PMC10298693/
- Personality/SES: https://pmc.ncbi.nlm.nih.gov/articles/PMC2800299/

Particularly useful: a later MIDUS personality paper with longer follow-up says it **did not replicate** earlier mortality associations for neuroticism and agreeableness, while conscientiousness remained predictive.

https://pmc.ncbi.nlm.nih.gov/articles/PMC4103968/

That is exactly the kind of instability we want to make visible.

### Counterexample experiment

Freeze:
- baseline cohort;
- all-cause mortality definition;
- demographics/health covariates;
- missing-data rule;
- scaling to 1 SD;
- Cox model.

Then fit the same model to every eligible psychological/social scale.

Ask:

> “Among 20–50 things psychologists could have called ‘the key to a longer life,’ where does *purpose* rank?”

### Data availability: GOOD, with terms

Computationally tractable and mostly public-use, but more operational friction than CDC data:
- ICPSR/NACDA account / terms;
- joining baseline and current mortality data;
- do not send raw MIDUS data to external/public LLM services.

### Likelihood of useful counterexamples: VERY HIGH

This may be the best example for **construct multiplicity**: many different names can be attached to correlated psychological states.

---

## 4. NHIS: “Hearing difficulty predicts death”

A published analysis of National Health Interview Survey 2005–2009 data reports:
- “a lot of trouble” hearing: adjusted mortality OR 1.5;
- deaf: adjusted OR 1.6;
- versus excellent/good hearing.

https://pubmed.ncbi.nlm.nih.gov/30832489/

### Data availability: EXCELLENT

CDC currently provides public linked mortality files for NHIS 1986–2018. The public files preserve alive/dead status; some follow-up/cause values are perturbed for disclosure protection.

https://www.cdc.gov/nchs/linked-data/mortality-files/index.html

NHIS annual public-use survey files are also directly downloadable, and samples are very large.

### Counterexample experiment

Choose one NHIS year or small contiguous set first to avoid a harmonization project.

Compare hearing with other everyday/self-reported characteristics captured in the same Sample Adult file, restricting the search to non-disease exposures where possible.

Potential families:
- sensory limitations;
- sleep;
- social participation;
- functional limitations;
- work status;
- health behaviors;
- healthcare use;
- self-rated wellbeing.

### Likelihood of useful counterexamples: HIGH

The huge N means small residual associations will often be precisely estimated. But many alternative predictors are obvious manifestations of underlying health, so the demo risks becoming “sick people die sooner,” which is less surprising than pets/books/purpose.

Use NHIS if we want **zero-friction scale**, not maximum narrative charm.

---

## 5. CLHLS: many leisure activities already “make you live longer”

The Chinese Longitudinal Healthy Longevity Survey gives us an unusually revealing published result rather than merely a candidate for future scanning.

A prospective study of **30,070 adults aged 80+** recorded **23,661 deaths**. Compared with people who never did each activity, near-daily participation in each of these was associated with lower adjusted mortality:

- watching TV or listening to radio;
- playing cards or mah-jong;
- reading books/newspapers;
- gardening;
- keeping domestic animals/pets;
- attending religious activities.

Adjusted HRs ranged roughly **0.82–0.89**, all reported P<0.01.

https://pubmed.ncbi.nlm.nih.gov/31588027/
https://pmc.ncbi.nlm.nih.gov/articles/PMC8019061/

This is almost the punchline we hope to discover elsewhere:

> **Six very different leisure activities all appear to prolong life.**

The parsimonious story is not necessarily that TV, mah-jong, books, gardening, pets, and religion each independently cause longevity. Among people averaging roughly age 93, the ability and opportunity to engage in activities is itself informative.

### Data availability: MODERATE

CLHLS public documentation is accessible, but current data distribution uses a sign-in/request-access workflow rather than CDC-style anonymous downloads.

### Likelihood of useful counterexamples: ALREADY HIGH

Keep this as a **literature control / narrative example**, even if we never download the data. It demonstrates the phenomenon without accusing anyone of selective reporting—the researchers themselves report the whole set.

---

## 6. ELSA: “Enjoying life makes you live longer”

A BMJ analysis of 9,365 English adults aged 50+ found that repeatedly reporting high enjoyment of life was associated with lower mortality; 1,310 participants died during follow-up.

https://pmc.ncbi.nlm.nih.gov/articles/PMC5154976/

ELSA combines wellbeing, wealth, employment, social participation, health, physical activity, cognition, and daily behaviors.

### Data availability: MODERATE

The paper states that ELSA data are accessible to registered users through the UK Data Service. This is doable, but adds more account/download friction than NHANES or NHIS.

### Counterexample potential: MEDIUM-HIGH

“Enjoyment makes you live longer” is a good headline, but the competing variables are less beautifully matched than HRS activities or MIDUS psychological scales.

---

## 7. GSS-NDI: conceptually excellent, currently hold

The General Social Survey linked to mortality has produced papers such as happiness → lower mortality, television viewing → higher mortality, and generalized trust → lower mortality.

This would be a wonderful attitudes-and-habits headline factory because GSS asks hundreds of memorable social questions.

However, older papers that describe the full GSS-NDI linkage as public are not enough evidence for easy access **today**. Current NCHS/GSS sharing rules have changed, and exact survival linkage is less frictionless than the CDC NHANES/NHIS products.

Recommendation: **do not build around GSS until we confirm a currently obtainable individual-level survival file with the needed follow-up variables.**

---

# What I would actually build

## Phase 1 — NHANES as the reusable benchmark

Build one pipeline:

participants + linked all-cause mortality + exposure registry + fixed covariates
→ survey-weighted Cox model for every exposure
→ one long results table.

Start with three exposure groups:

1. **Foods/drinks** — chili, tea, coffee, breakfast and every comparable food/diet item.
2. **Everyday behaviors** — sleep, religious attendance, physical activity, etc.
3. **Visible body/health markers** — teeth and a small prespecified set of comparable measurements.

Do not initially vary the model. First vary only **what the paper could have been about**. That isolates the exact selection problem we care about.

### Best first story

> **Tea apparently adds 2.2 years to life. What else in NHANES “adds years”?**

Tea may be more vivid than chili because the paper itself translates the result into life expectancy, but its non-monotonic pattern is also an immediate warning sign: 3–<5 cups/day looks best while >=5 does not.

Then reveal chili, coffee, religion, sleep, teeth, etc. as other “keys to longevity.”

## Phase 2 — HRS/CAMS as an independent, cleaner replication

Reproduce **books → mortality** and run exactly the same analysis over the CAMS activity list.

The reveal can be almost comic:

> “Books make you live longer.”
>
> “So do gardening? Pets? Hugging? Puzzles? Concerts? Volunteering? Managing your money?”

This is likely the most compelling *single chart* in the whole project because the variables are concrete, everyday, and measured side-by-side.

## Phase 3 — MIDUS for psychological labels

Repeat the idea with “purpose in life,” testing every comparable psychological/social scale.

This shows a different kind of selection:
- NHANES: **which behavior/food?**
- HRS: **which daily activity?**
- MIDUS: **which name for a correlated psychological construct?**

Together they make a much stronger general case than any one replication.

# Methodological guardrail

Finding many significant alternatives does **not** prove the original factor has no causal effect, and does not prove p-hacking.

It demonstrates something narrower and defensible:

> **The data support many competing headlines, so a single selected association contains much less information than its p-value suggests.**

The decisive counterfactual is symmetric:

- If the focal exposure is an extreme, stable outlier among comparable exposures, that strengthens it.
- If dozens of unrelated exposures look equally good, specificity collapses.
- If almost everything associated with being active/healthy predicts survival, common-cause confounding becomes a more plausible explanation.
- If the result changes mainly when exposure binning/covariates change, specification choice is the main fragility.

That is the test to preregister before seeing the multiverse.
