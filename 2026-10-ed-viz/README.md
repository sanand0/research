# Can AI read an engineering drawing?

Experiment for Anand's 7 Oct 2026 IIT Madras Engineering Design / Data Visualization session.

The question is stronger than “can AI make a plausible 3D shape?”:

> **Can an agent reconstruct the right editable parametric CAD model from a dimensioned engineering drawing — and know when it is wrong?**

The finished data story is index.html. It is a static GitHub Pages–friendly page with no build step.

## Result

We gave Codex only:

- a dimensioned mechanical engineering drawing;
- FreeCAD 1.1.0;
- a way to render its current CAD model;
- an instruction to produce one editable, valid PartDesign solid.

The hidden CAD Bench reference and verifier were withheld until the candidate was frozen.

Codex produced a plausible, editable model with:

- the **exact 150 × 48 × 88 mm envelope**;
- one valid closed solid;
- 7 sketches + 7 PartDesign operations;
- **27/30** hidden specification parameters reported consistent.

But the official CAD Bench geometry score was only **0.0423**. The combined score was **0.0798**.

The important lesson is:

> **Self-verification is only as strong as the verification kit.**

If an agent checks only “valid solid + right bounding box + looks plausible”, it can confidently converge on the wrong engineered object.

## What failed

The candidate captured many visible callouts, but attached them to a different geometric construction.

The official verifier found, among other things:

- bounding-box difference: **0.0%**;
- volume difference: **13.7%**;
- surface-type difference: **20.2%**;
- principal-moment difference: **16.8%**;
- aligned face-centre RMSE: **8.44 mm**.

Three explicit spec misses were:

- expected **R3** lower-profile radius; nearest candidate radius was R5;
- expected **R6** lower-profile radius; no final-geometry witness existed;
- expected **46.39 mm** fork reference; nearest candidate measurement was 48 mm.

A useful caution: 27/30 is not equivalent to “90% understood”. The spec checker searches pools of geometric measurements, so a value can occasionally match the wrong feature. The independent geometry score is the stronger evidence that the reconstructed object was wrong.

## Story structure

index.html narrates the experiment as:

**drawing → failed first workflow → first CAD model → self-correction → plausible final model → hidden reference → CAD Bench verification → surprising failure → verification-kit lesson**

The comparison visuals are deliberately conservative:

- reference and candidate are rigidly aligned into the same coordinate frame;
- both use the same center, scale, orientation and camera;
- the page includes both an interactive wipe and a blink comparison;
- outline-difference imagery compares geometry without relying on shaded renders.

All explanatory text, labels, scores and diagrams are HTML/CSS. The image assets themselves contain no added narrative text.

## Files

### Benchmark

CAD Bench V3 task f32bdb2966, a forked mounting bracket.

Agent-visible:

- benchmark/input/engineering-drawing.png
- benchmark/task/instruction.md

Held back during reconstruction:

- benchmark/hidden/reference.FCStd
- benchmark/hidden/spec.json

### Blind reconstruction

- candidate/answer.py
- candidate/answer.FCStd
- candidate/trajectory2.jsonl
- candidate/assumptions.md
- candidate/first-attempt.py
- candidate/first-attempt.FCStd

The first-attempt files were reconstructed from the saved trajectory so the story can show the model before Codex's self-correction.

### Official verifier evidence

- results/official-score/reward.json
- results/official-score/reward_details.json
- results/official-score/spec_findings.json

Research notes are in STEP1.md through STEP4.md; PLAN.md records the staged experiment.

## Web page and assets

index.html is standalone HTML/CSS/JS and can be published directly with GitHub Pages.

For a local preview:

    python3 -m http.server 8000

Then open http://localhost:8000/.

assets/ contains only the images used by the story. They are AVIF encoded at quality 50. The web-facing image payload is about **132 KB**; index.html + assets/ is about **180 KB**.

## Reproducing the FreeCAD runtime

Large portable runtimes are intentionally not stored in this repo.

    ./scripts/setup_freecad.sh

This downloads and extracts FreeCAD 1.1.0 under tools/freecad/ and verifies its recorded SHA-256.

Useful retained scripts include:

- scripts/freecadcmd.sh
- scripts/freecadgui.sh
- scripts/inspect_freecad.py
- scripts/render_fcstd.sh
- scripts/render_freecad_views.py
- scripts/create_freecad_smoke.py
- scripts/edit_freecad_smoke.py
- scripts/setup_freecad.sh
- scripts/score_candidate.sh

The full CAD Bench V3 verifier Docker context is also intentionally not committed. scripts/score_candidate.sh exits with instructions if that context has not been re-downloaded.

## Repository policy

Keep:

- benchmark input and held-back ground truth;
- blind agent artifacts and trajectories;
- raw verifier findings;
- compact published assets;
- research notes and reproduction scripts.

Do not commit:

- portable FreeCAD / Blender installations;
- cloned benchmark suites and Docker images;
- intermediate renders and contact sheets;
- abandoned IFC exploration artifacts.

See SOURCES.md for benchmark and runtime sources.
