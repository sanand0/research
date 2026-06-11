# Prompts

## Initial research, 11 Jun 2026

<!-- https://chatgpt.com/c/6a2a477a-9b84-83ec-a24a-aa97efde1d5d -->

<!--
cd /home/sanand/code/research/3dmesh
dev.sh
codex --yolo --model gpt-5.5 --config model_reasoning_effort=medium
-->

You are building a small CAD/mesh experiment for a future biomechanical fit study.

Goal: create a synthetic irregular “bone/skull/jaw-like” 3D mesh and a second close-fitting “implant shell” mesh on top of part of it. The result must be visual and inspectable.

Use Python. Prefer this stack - install what you need.

- numpy
- scipy
- trimesh
- pyvista or plotly
- optionally gmsh if useful

Do not use a GUI-only workflow. Everything must be reproducible from code.

Task:

1. Create a synthetic irregular base mesh.
   - It should look roughly like an organic skull/jaw/bone surface, not a box or sphere.
   - A deformed ellipsoid, bumpy mandible-like arch, or skull-like surface is acceptable.
   - Make it asymmetric.
   - Add depressions, protrusions, and local curvature variation.
   - Ensure the mesh is watertight if possible.
   - Export it as `bone_irregular_mesh.stl`.

2. Create a second mesh that just about fits on top of a local patch.
   - Treat this as a prototype titanium implant/joint shell.
   - Select a curved patch on the lower/front/right side of the base mesh.
   - Offset the patch outward by a small clearance, for example 0.5–1.0 mm.
   - Add shell thickness, for example 2–3 mm.
   - Close the side walls so the implant is a real shell/solid mesh.
   - Export it as `implant_fit_shell.stl`.

3. Add fit diagnostics.
   - Compute approximate clearance between the implant inner surface and the bone surface.
   - Report min, p05, median, p95, max, and mean clearance.
   - Check whether both meshes are watertight.
   - Save this as `fit_report.json`.

4. Create a visual output.
   - Generate an interactive browser-viewable `jaw_fit_experiment.html`.
   - Show the base bone mesh as semi-transparent.
   - Show the implant shell as a separate colored mesh.
   - Show clearance sample points or a clearance heatmap on the implant inner surface.
   - Add a few normal/clearance vectors so I can understand how the implant was constructed.
   - The viewer must allow rotate/zoom/pan.

5. Make the script easy to modify.
   - Put key parameters at the top: random seed, mesh resolution, patch location, patch size, clearance, shell thickness.
   - Add comments explaining where I can later plug in material expansion coefficients.
   - Add a placeholder function such as `simulate_uniform_thermal_expansion(alpha_bone, alpha_implant, delta_T)` that rescales the two meshes and recomputes clearance, even if it is only a first-order toy model.

6. Deliverables:
   - `jaw_fit_experiment.py`
   - `jaw_fit_experiment.html`
   - `bone_irregular_mesh.stl`
   - `implant_fit_shell.stl`
   - `fit_report.json`
   - `README.md` explaining how to run and what to inspect

Acceptance criteria:

- Running `python jaw_fit_experiment.py` regenerates all outputs.
- The visual clearly shows one irregular organic mesh and one close-fitting shell mesh.
- The fit report contains clearance metrics.
- The code is simple enough that I can change clearance, shell thickness, patch size, and material expansion assumptions.
- This is explicitly marked as a synthetic toy model, not a medical or anatomical design.

---

Download a publicly available head CT scan. Segment the skull. Create a hole near the mid-line. Create a patch to fill that hole. Visualize these. Share a fit report.

<!-- codex resume 019eb52e-d845-7490-bf41-fe21f0068e1c --yolo -->
