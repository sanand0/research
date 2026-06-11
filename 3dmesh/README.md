# Synthetic Jaw Fit Experiment

<!-- Output moved to ~/r2/files/pages/3dmesh/ = https://files.s-anand.net/pages/3dmesh/ -->

This is a **synthetic toy CAD/mesh experiment**. It is not a medical,
anatomical, surgical, or implant design and must not be used as one.

The generator creates:

- `bone_irregular_mesh.stl`: a watertight asymmetric, deformed organic solid.
- `implant_fit_shell.stl`: a closed solid shell fitted over a lower/front/right
  curved patch.
- `fit_report.json`: parameters, mesh checks, and nearest-surface clearance
  statistics.
- `jaw_fit_experiment.html`: a self-contained interactive Plotly viewer with
  rotate, zoom, pan, clearance samples, and construction vectors.

## Run

The script contains PEP 723 dependency metadata, so `uv` installs dependencies
into its managed environment and regenerates every output:

```bash
uv run jaw_fit_experiment.py
```

With `numpy`, `scipy`, `trimesh`, `rtree`, and `plotly` already installed in
the active Python environment, this equivalent command also works:

```bash
python jaw_fit_experiment.py
```

Open `jaw_fit_experiment.html` in a browser. Use the legend to hide/show the
bone, shell, clearance points, or clearance vectors. Hover over colored points
to inspect approximate nearest-surface clearance. The red clearance vectors are
displayed at 8x length for visibility; this does not alter the meshes or report.

## Modify

Edit the constants near the top of `jaw_fit_experiment.py`:

- `RANDOM_SEED` and `MESH_RESOLUTION`
- `PATCH_LOCATION` and `PATCH_SIZE`
- `CLEARANCE_MM` and `SHELL_THICKNESS_MM`

`simulate_uniform_thermal_expansion(...)` is a deliberately simple placeholder
for material expansion experiments. It applies first-order isotropic scaling
using `1 + alpha * delta_T`; replace it with a proper mechanics model before
using nonuniform temperatures, constraints, or real material behavior.

## Inspect

The implant is built by extracting a curved patch, offsetting it outward by the
nominal clearance, offsetting a second copy by the shell thickness, and closing
all boundary edges with side-wall triangles. `fit_report.json` records whether
both final meshes are watertight and reports min, p05, median, p95, max, and mean
clearance in millimeters.

## Public Head CT Skull Patch Experiment

`head_ct_skull_experiment.py` downloads the unrestricted-use CT-brain sample
listed in 3D Slicer's official `SampleData.py`, verifies its SHA-256 checksum,
segments the dominant high-density skull component, cuts a superior
near-midline defect, and creates a matching patch with nominal radial clearance.

Run:

```bash
python head_ct_skull_experiment.py
```

Outputs:

- [`head_ct_public.nrrd`](https://files.s-anand.net/pages/3dmesh/head_ct_public.nrrd): verified public source CT.
- [`skull_segmented.stl`](https://files.s-anand.net/pages/3dmesh/skull_segmented.stl): complete segmented skull.
- [`skull_with_midline_defect.stl`](https://files.s-anand.net/pages/3dmesh/skull_with_midline_defect.stl): skull after the controlled defect.
- [`skull_patch.stl`](https://files.s-anand.net/pages/3dmesh/skull_patch.stl): fitting patch derived from the removed skull region.
- `skull_{segmentation,defect,patch}_mask.nrrd`: reproducible voxel masks.
- [`skull_patch_experiment.html`](https://files.s-anand.net/pages/3dmesh/skull_patch_experiment.html): interactive complete-skull, defect, patch,
  exploded-patch, clearance-point, and clearance-vector view. Toggle the
  in-position patch and fit diagnostics from the legend.
- [`skull_fit_report.json`](https://files.s-anand.net/pages/3dmesh/skull_fit_report.json): source provenance, parameters, mesh checks, and fit
  metrics.

This second experiment is also a research/demo prototype only. The threshold
segmentation and patch are not validated for diagnosis, treatment planning, or
implant design.
