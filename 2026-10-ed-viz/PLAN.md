# ED Viz mechanical drawing experiment

Goal: test whether an AI agent can read a dimensioned mechanical engineering drawing well enough to reconstruct a real, editable parametric CAD model, then verify that result with engineering checks.

## Current benchmark

CAD Bench V3 task f32bdb2966 — Forked Mounting Bracket.

Why this task:
- unmistakably a mechanical engineering drawing, not an architectural plan;
- three orthographic views with dimensions, radii, diameters and stepped depth;
- requires cross-view reasoning: raised bored boss, central fork opening, shoulder radii, base thickness/depth and two mounting holes;
- reference construction is modest enough for a live session: one PartDesign Body, three Pads and one Pocket;
- still has enough geometry that "looks plausible" and "is correct" can diverge.

Input exposed to the agent:
- benchmark/input/engineering-drawing.png
- benchmark/task/instruction.md

Held back from the agent:
- benchmark/hidden/reference.FCStd
- benchmark/hidden/spec.json

Source: Parametric CAD Bench V3, downloaded with Harbor 0.23.0:
uvx --from harbor==0.23.0 harbor download gnucleus-ai/cad-bench@v3

## Plan

### Step 1 — Select and stage a real engineering-drawing benchmark
Status: DONE.

- Download the 100-task V3 suite.
- Identify the 40 image-to-CAD engineering-drawing tasks.
- Compare moderate bracket-like candidates visually and by reference feature-tree complexity.
- Select f32bdb2966.
- Stage agent-visible input separately from held-back ground truth.
- Confirm the reference is a real parametric PartDesign model, not a baked shape.

### Step 2 — Make the FreeCAD authoring runtime boringly reliable
Status: DONE.

- Reproduce the benchmark's FreeCAD 1.1.0 runtime.
- Open the held-back reference and inspect Body/features/solid validity.
- Prove a tiny script can create and save a PartDesign model.
- Determine the cleanest agent interface: raw FreeCAD Python, GUI/computer use, or an MCP/tool wrapper.
- Prefer the simplest mechanism that reliably supports inspect → edit → render → verify loops.

### Step 3 — Blind reconstruction
Status: DONE. In practice Codex shell plus the exact FreeCAD runtime was simpler than adding MCP to Codex; the run was isolated by hiding the evaluator repo.

- Give the agent only the drawing and benchmark instruction.
- Ask it to produce answer.py + answer.FCStd.
- Preserve its trajectory, assumptions and intermediate screenshots/renders.
- Do not expose hidden grader/reference files.

### Step 4 — Deterministic evaluation
Status: DONE. Official reward 0.079809; geometry 0.042317, spec 0.70.

- Run the official CAD Bench verifier first.
- Add transparent classroom-friendly checks:
  - solid validity;
  - bounding box / overall dimensions;
  - boss and bore diameters;
  - hole count/diameter/spacing;
  - cross-view depth;
  - volume / surface comparisons;
  - feature-tree/editability checks;
  - regenerated orthographic views against the original.

### Step 5 — Engineering follow-through
Next. Prefer assembly/editability before FEM because Step 4 showed geometry/relationship errors despite correct callouts.

Pick one based on what Step 3 reveals:
- edit test: change boss bore or mounting-hole spacing and rebuild;
- assembly fit: create a mating pin/shaft and check clearance/interference;
- simple FEM/load test if the geometry and available solver make this robust enough for a live class.

### Step 6 — Turn it into the class story
Status: DONE. See index.html.

Narrative:
drawing → interpretation → parametric model → deterministic verification → engineering action

Revise based on actual agent failures. The failure should drive the lesson.
