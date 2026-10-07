# Step 4 findings — hidden-ground-truth evaluation

Status: DONE.

The candidate was frozen before any hidden evaluator/reference was revealed.

## Official CAD Bench V3 score

Ran the task's own verifier unchanged:

- FreeCAD 1.1.0
- gnucleus-freecad-validator 0.6.0
- v2 geometry scorer
- hidden reference.FCStd
- hidden spec.json + case-specific param_check.py

Reproduction:

    ./scripts/score_candidate.sh

Official result:

| Axis | Score |
| --- | ---: |
| Geometry similarity | **0.0423166** |
| CAD spec consistency | **0.7000000** |
| Combined harmonic score | **0.0798085** |

The low combined score is not a tooling failure. Candidate and reference each contain one valid solid and the OBB bounding-box gate passes exactly.

## The revealing contradiction

The spec checker reports:

- 27 / 30 parameters consistent
- 2 inconsistent
- 1 not found

Yet geometry similarity is only 0.042.

This is the central result:

> **The agent read most dimension callouts correctly, but did not reconstruct the same part.**

The bounding envelope also matches:
- reference: 150 × 88 × 48 mm
- candidate: same oriented dimensions (candidate local axes are 150 × 48 × 88)

So correct dimensions and correct envelope are both insufficient tests of engineering-drawing understanding.

## Official geometry diagnostics

The v2 scorer reports:

- solid count: matched (1 vs 1)
- OBB bbox difference: **0.000%**, gate passes
- volume difference: **13.682% — Far**
- surface area difference: **5.730% — Close**
- surface-type difference: **20.205% — Far**
- principal-moment difference: **16.758% — Far**
- ICP face-centre RMSE: **8.4357 mm**
- ICP max residual: **23.452 mm**
- ICP spatial reward: **0**
- overall geometry score: **0.0423166**

Measured directly:

| | Hidden reference | Blind candidate |
| --- | ---: | ---: |
| Volume | 177,334.54 mm³ | 153,070.94 mm³ |
| Surface area | 39,564.62 mm² | 37,297.38 mm² |
| Volume error | — | **−24,263.60 mm³ / −13.68%** |
| Solid count | 1 | 1 |
| Valid / closed | yes | yes |

The model therefore has approximately the right exterior scale but substantially the wrong mass distribution and surfaces.

## Exact failed dimensional/spec checks

### Inconsistent

1. lower_profile_radii_2
   - expected: **R3**
   - nearest measured candidate radius: **R5**
   - source found by checker: mounting-hole circle radius
   - relative error: 40%

2. fork_horizontal_references_1
   - expected: **46.39 mm**
   - nearest measured candidate length: **48 mm**
   - source: eye extrusion length
   - relative error: 3.35%

### Not found

3. lower_profile_radii_1
   - expected: **R6**
   - no final-geometry R6 witness

These correspond closely to what the blind agent itself admitted after construction: it simplified the lower/fork profile and omitted the R6/R3 details.

## Caution: 27/30 does NOT mean 90% of the drawing was correctly understood

The raw consistency report exposes an important benchmark/evaluation lesson.

Some passes are semantically strong:
- boss OD 35.98 found in final geometry
- base-hole Ø10 found twice in final geometry
- 150 / 88 envelope
- 90 / 138 widths
- 20.3 bore
- 12 mm shoulder radii

But several pass because the checker deliberately searches a pool for the nearest matching measurement:
- base_holes_count = 2 matched two equal base-plan segments
- lower_profile_radii_1_count = 2 also matched two equal base-plan segments
- lower_profile_radii_2_count = 4 matched four R12 shoulder arcs
- base_hole_spacing = 126 matched an unrelated 126 mm profile offset

Thus the 0.70 spec score is useful evidence of callout capture, but **the 0.042 geometry score is the stronger evidence of whether the drawing was reconstructed correctly**.

Also note that v2 spec scoring uses a failure budget of 10, not plain accuracy:
- 3 failed parameters → 1 − 3/10 = **0.70**
- the raw consistent fraction is 27/30 = 0.90

## What the reference actually does

Hidden reference PartDesign history:

1. Sketch → Pad 48 mm
2. Sketch001 → Pad 10 mm
3. Sketch002 → Pad 35 mm
4. Sketch003 → Pocket 35 mm

Its three additive sketches jointly encode the interlocking front/depth profiles.

Reference sketches include:

- first profile: arcs for the Ø35.98 boss and Ø20.3 bore geometry
- second profile: **R3 + four R12 + boss arcs**
- third profile: **two R6 + R3 + R12 + lower/fork geometry**
- final sketch: two Ø10 mounting holes

Blind candidate instead used seven operations:

1. rectangular base Pad 10
2. shaped upright Pad 10
3. rectangular stem Pad 35
4. circular eye Pad 48
5. rectangular fork Pocket
6. eye-bore Pocket
7. two mounting-hole Pocket

This is a plausible decomposition, but it is not geometrically equivalent.

## Visual result

results/official-score/comparison.png places:

1. engineering drawing
2. hidden reference render
3. blind candidate render

The candidate is immediately recognisable as "the same kind of bracket", which makes the 0.042 geometry score more interesting, not less.

The human-eye trap is exactly the lesson:
- plausible render: yes
- correct outer dimensions: yes
- most callout values somewhere in model: yes
- valid editable CAD: yes
- same engineered part: **no**

## Proposed teaching punchline

Start by showing only the candidate render and ask:

> "Did the AI read the engineering drawing?"

Most people will probably say "pretty well."

Then reveal, one at a time:

1. **150 × 88 × 48 exactly right**
2. **27/30 spec checks found**
3. **valid parametric solid**
4. **but geometry score = 4.2%**
5. show reference and candidate side-by-side

Then ask:

> **What does it mean to understand an engineering drawing?**

A useful answer is:

> Reading the numbers is not enough. The numbers must constrain the *right geometry and relationships*.

This bridges directly into verification, semantic representation, and why agent workflows need executable tests.

## Step 5 implication

I would NOT jump straight to FEM yet.

The stronger next experiment is an **engineering edit / assembly-fit test** that exposes the semantic consequences of the wrong reconstruction.

Candidate options:
- insert a mating Ø20.3 / Ø20-ish pin or shaft through the boss and test fit/alignment;
- change one dimension such as boss bore or fork width and see whether both the reference-style model and agent model respond coherently;
- construct a mating part for the fork and run clearance/interference.

Only after that, if useful, add FEM. FEM on the wrong geometry can produce beautifully precise but irrelevant stresses — itself a possible later lesson.
