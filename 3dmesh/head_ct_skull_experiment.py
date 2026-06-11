#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "numpy>=2.0",
#   "plotly>=6.0",
#   "rtree>=1.3",
#   "scikit-image>=0.25",
#   "scipy>=1.14",
#   "SimpleITK>=2.5",
#   "trimesh>=4.6",
# ]
# ///
"""Segment a public head CT, create a skull defect, and make a fitting patch.

Research/demo prototype only. This is not validated medical segmentation,
diagnosis, treatment planning, or an implant design.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import urllib.request

try:
    import numpy as np
    import plotly.graph_objects as go
    from scipy import ndimage
    import SimpleITK as sitk
    from skimage import measure
    import trimesh
except ModuleNotFoundError:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("Missing dependencies. Install uv, then rerun this script.") from None
    os.execv(uv, [uv, "run", "--script", str(Path(__file__).resolve()), *sys.argv[1:]])


# Key experiment parameters, in millimeters unless noted otherwise.
BONE_THRESHOLD_HU = 300
DEFECT_RADIUS_MM = 20.0
PATCH_CLEARANCE_MM = 0.8
FIT_SIDE_BAND_MM = 0.4
DEFECT_START_FRACTION_Z = 0.72
DEFECT_CENTER_OFFSET_X_MM = 2.0  # Small offset while remaining near the midline.
DEFECT_CENTER_OFFSET_Y_MM = 0.0
MARCHING_CUBES_STEP_SIZE = 2
FIT_SAMPLE_COUNT = 500
VECTOR_COUNT = 16
VECTOR_DISPLAY_SCALE = 5.0

OUTPUT_DIR = Path(__file__).resolve().parent
CT_PATH = OUTPUT_DIR / "head_ct_public.nrrd"
CT_URL = (
    "https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/"
    "6a5b6caccb76576a863beb095e3bfb910c50ca78f4c9bf043aa42f976cfa53d1"
)
CT_SHA256 = "6a5b6caccb76576a863beb095e3bfb910c50ca78f4c9bf043aa42f976cfa53d1"
DISCLAIMER = (
    "Research/demo prototype only. Not validated medical segmentation, diagnosis, "
    "treatment planning, or an implant design."
)


def sha256(path: Path) -> str:
    """Return a file SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_ct() -> None:
    """Download and verify the public 3D Slicer CT sample when absent."""
    if CT_PATH.exists() and sha256(CT_PATH) == CT_SHA256:
        print(f"Using verified CT: {CT_PATH.name}")
        return
    print(f"Downloading public CT to {CT_PATH.name}...")
    urllib.request.urlretrieve(CT_URL, CT_PATH)
    actual = sha256(CT_PATH)
    if actual != CT_SHA256:
        CT_PATH.unlink(missing_ok=True)
        raise RuntimeError(f"CT checksum mismatch: expected {CT_SHA256}, got {actual}")


def largest_component(mask: np.ndarray) -> np.ndarray:
    """Keep the largest 3D connected component."""
    labels, count = ndimage.label(mask, structure=ndimage.generate_binary_structure(3, 2))
    if count == 0:
        raise RuntimeError("Segmentation produced no connected components.")
    sizes = np.bincount(labels.ravel())
    return labels == np.argmax(sizes[1:]) + 1


def segment_skull(ct_array: np.ndarray) -> np.ndarray:
    """Create a simple high-density skull segmentation."""
    mask = ct_array >= BONE_THRESHOLD_HU
    mask = ndimage.binary_closing(mask, iterations=1)
    return largest_component(mask)


def index_to_physical(index_xyz: np.ndarray, image: sitk.Image) -> np.ndarray:
    """Transform continuous xyz voxel indices to physical xyz coordinates."""
    direction = np.asarray(image.GetDirection()).reshape(3, 3)
    scaled = index_xyz * np.asarray(image.GetSpacing())
    return scaled @ direction.T + np.asarray(image.GetOrigin())


def physical_to_index(points_xyz: np.ndarray, image: sitk.Image) -> np.ndarray:
    """Transform physical xyz coordinates to continuous xyz voxel indices."""
    direction = np.asarray(image.GetDirection()).reshape(3, 3)
    local = (points_xyz - np.asarray(image.GetOrigin())) @ direction
    return local / np.asarray(image.GetSpacing())


def mask_to_mesh(mask: np.ndarray, image: sitk.Image) -> trimesh.Trimesh:
    """Convert a zyx binary mask into a physical-coordinate triangle mesh."""
    padded = np.pad(mask.astype(np.uint8), 1)
    vertices_zyx, faces, _, _ = measure.marching_cubes(
        padded,
        level=0.5,
        spacing=tuple(reversed(image.GetSpacing())),
        step_size=MARCHING_CUBES_STEP_SIZE,
        allow_degenerate=False,
    )
    vertices_zyx -= np.asarray(tuple(reversed(image.GetSpacing())))
    index_xyz = vertices_zyx[:, ::-1] / np.asarray(image.GetSpacing())
    vertices_xyz = index_to_physical(index_xyz, image)
    mesh = trimesh.Trimesh(vertices=vertices_xyz, faces=faces, process=True)
    mesh.fix_normals(multibody=True)
    return mesh


def create_defect_and_patch(
    skull_mask: np.ndarray, image: sitk.Image
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    """Cut a superior near-midline cylindrical defect and create its patch."""
    z, y, x = np.where(skull_mask)
    spacing_x, spacing_y, _ = image.GetSpacing()
    center_x = 0.5 * (x.min() + x.max()) + DEFECT_CENTER_OFFSET_X_MM / spacing_x
    center_y = 0.5 * (y.min() + y.max()) + DEFECT_CENTER_OFFSET_Y_MM / spacing_y
    start_z = z.min() + DEFECT_START_FRACTION_Z * (z.max() - z.min())

    yy, xx = np.ogrid[: skull_mask.shape[1], : skull_mask.shape[2]]
    radial_mm = np.sqrt(
        ((xx - center_x) * spacing_x) ** 2 + ((yy - center_y) * spacing_y) ** 2
    )
    upper = np.arange(skull_mask.shape[0])[:, None, None] >= start_z
    defect_cylinder = upper & (radial_mm[None, :, :] <= DEFECT_RADIUS_MM)
    patch_cylinder = upper & (
        radial_mm[None, :, :] <= DEFECT_RADIUS_MM - PATCH_CLEARANCE_MM
    )

    defect_mask = skull_mask & ~defect_cylinder
    patch_mask = largest_component(skull_mask & patch_cylinder)
    parameters = {
        "center_index_x": float(center_x),
        "center_index_y": float(center_y),
        "start_index_z": float(start_z),
    }
    return defect_mask, patch_mask, parameters


def save_mask(mask: np.ndarray, reference: sitk.Image, filename: str) -> None:
    """Save a binary mask with the CT's spatial metadata."""
    image = sitk.GetImageFromArray(mask.astype(np.uint8))
    image.CopyInformation(reference)
    sitk.WriteImage(image, str(OUTPUT_DIR / filename), useCompression=True)


def clearance_diagnostics(
    defect_mesh: trimesh.Trimesh,
    patch_mesh: trimesh.Trimesh,
    image: sitk.Image,
    defect_parameters: dict[str, float],
) -> tuple[dict[str, float], np.ndarray, np.ndarray, np.ndarray]:
    """Measure patch-side clearance to the defect skull surface."""
    patch_index = physical_to_index(patch_mesh.vertices, image)
    spacing_x, spacing_y, _ = image.GetSpacing()
    dx = (patch_index[:, 0] - defect_parameters["center_index_x"]) * spacing_x
    dy = (patch_index[:, 1] - defect_parameters["center_index_y"]) * spacing_y
    radial = np.sqrt(dx**2 + dy**2)
    side_band = radial >= DEFECT_RADIUS_MM - PATCH_CLEARANCE_MM - FIT_SIDE_BAND_MM
    upper = patch_index[:, 2] >= defect_parameters["start_index_z"] - 1.0
    mating_ids = np.flatnonzero(side_band & upper)
    mating_points = patch_mesh.vertices[mating_ids]
    closest, distances, _ = trimesh.proximity.closest_point(defect_mesh, mating_points)
    metrics = {
        "min": float(np.min(distances)),
        "p05": float(np.percentile(distances, 5)),
        "median": float(np.median(distances)),
        "p95": float(np.percentile(distances, 95)),
        "max": float(np.max(distances)),
        "mean": float(np.mean(distances)),
    }
    return metrics, mating_points, closest, distances


def mesh_trace(mesh: trimesh.Trimesh, **kwargs: object) -> go.Mesh3d:
    """Create a Plotly triangle-mesh trace."""
    return go.Mesh3d(
        x=mesh.vertices[:, 0],
        y=mesh.vertices[:, 1],
        z=mesh.vertices[:, 2],
        i=mesh.faces[:, 0],
        j=mesh.faces[:, 1],
        k=mesh.faces[:, 2],
        showlegend=True,
        **kwargs,
    )


def create_visualization(
    complete_mesh: trimesh.Trimesh,
    defect_mesh: trimesh.Trimesh,
    patch_mesh: trimesh.Trimesh,
    mating_points: np.ndarray,
    closest_points: np.ndarray,
    distances: np.ndarray,
) -> None:
    """Write an interactive HTML view of complete, defect, and patch meshes."""
    rng = np.random.default_rng(20260611)
    exploded_patch = patch_mesh.copy()
    exploded_patch.apply_translation([0.0, 0.0, 35.0])
    sample_ids = rng.choice(
        len(mating_points), min(FIT_SAMPLE_COUNT, len(mating_points)), replace=False
    )
    vector_ids = rng.choice(
        len(mating_points), min(VECTOR_COUNT, len(mating_points)), replace=False
    )
    vector_x: list[float | None] = []
    vector_y: list[float | None] = []
    vector_z: list[float | None] = []
    for point_id in vector_ids:
        start = mating_points[point_id]
        end = start + VECTOR_DISPLAY_SCALE * (closest_points[point_id] - start)
        vector_x.extend([start[0], end[0], None])
        vector_y.extend([start[1], end[1], None])
        vector_z.extend([start[2], end[2], None])

    figure = go.Figure(
        data=[
            mesh_trace(
                complete_mesh,
                name="Original segmented skull",
                color="#d8c5a5",
                opacity=0.08,
                visible="legendonly",
            ),
            mesh_trace(
                defect_mesh,
                name="Skull with near-midline defect",
                color="#d8c5a5",
                opacity=0.48,
            ),
            mesh_trace(
                patch_mesh,
                name="Fitting patch (in position)",
                color="#f28e2b",
                opacity=0.92,
                visible="legendonly",
            ),
            mesh_trace(
                exploded_patch,
                name="Patch (exploded view)",
                color="#f28e2b",
                opacity=0.92,
            ),
            go.Scatter3d(
                x=mating_points[sample_ids, 0],
                y=mating_points[sample_ids, 1],
                z=mating_points[sample_ids, 2],
                mode="markers",
                name="Patch-side clearance samples",
                visible="legendonly",
                marker={
                    "size": 3.2,
                    "color": distances[sample_ids],
                    "colorscale": "Turbo",
                    "colorbar": {"title": "Clearance (mm)"},
                },
                text=[f"{value:.3f} mm" for value in distances[sample_ids]],
                hovertemplate="Nearest clearance: %{text}<extra></extra>",
            ),
            go.Scatter3d(
                x=vector_x,
                y=vector_y,
                z=vector_z,
                mode="lines",
                name=f"Clearance vectors ({VECTOR_DISPLAY_SCALE:g}x display)",
                visible="legendonly",
                line={"color": "#e63946", "width": 5},
                hoverinfo="skip",
            ),
        ]
    )
    figure.update_layout(
        title={
            "text": "Public Head CT: Skull Defect and Fitting Patch<br><sup>"
            + DISCLAIMER
            + "</sup>",
            "x": 0.5,
        },
        template="plotly_white",
        scene={
            "aspectmode": "data",
            "xaxis_title": "Physical X (mm)",
            "yaxis_title": "Physical Y (mm)",
            "zaxis_title": "Physical Z (mm)",
            "camera": {"eye": {"x": 1.35, "y": -1.55, "z": 1.2}},
        },
        legend={"orientation": "h", "y": 0.01, "x": 0.01},
        margin={"l": 0, "r": 0, "t": 80, "b": 0},
    )
    figure.write_html(
        OUTPUT_DIR / "skull_patch_experiment.html",
        include_plotlyjs=True,
        full_html=True,
        config={"displaylogo": False, "scrollZoom": True},
    )


def main() -> None:
    """Run the complete download, segmentation, defect, patch, and report pipeline."""
    download_ct()
    print("Reading CT and segmenting the dominant high-density skull component...")
    image = sitk.ReadImage(str(CT_PATH))
    ct_array = sitk.GetArrayFromImage(image)
    skull_mask = segment_skull(ct_array)
    defect_mask, patch_mask, defect_parameters = create_defect_and_patch(skull_mask, image)

    print("Creating physical-coordinate meshes...")
    complete_mesh = mask_to_mesh(skull_mask, image)
    defect_mesh = mask_to_mesh(defect_mask, image)
    patch_mesh = mask_to_mesh(patch_mask, image)
    metrics, mating_points, closest_points, distances = clearance_diagnostics(
        defect_mesh, patch_mesh, image, defect_parameters
    )

    complete_mesh.export(OUTPUT_DIR / "skull_segmented.stl")
    defect_mesh.export(OUTPUT_DIR / "skull_with_midline_defect.stl")
    patch_mesh.export(OUTPUT_DIR / "skull_patch.stl")
    save_mask(skull_mask, image, "skull_segmentation_mask.nrrd")
    save_mask(defect_mask, image, "skull_defect_mask.nrrd")
    save_mask(patch_mask, image, "skull_patch_mask.nrrd")
    create_visualization(
        complete_mesh,
        defect_mesh,
        patch_mesh,
        mating_points,
        closest_points,
        distances,
    )

    voxel_volume = float(np.prod(image.GetSpacing()))
    report = {
        "disclaimer": DISCLAIMER,
        "source": {
            "name": "3D Slicer CT-MR Brain sample: CT-brain.nrrd",
            "url": CT_URL,
            "sha256": CT_SHA256,
            "usage_note": (
                "3D Slicer's SampleData registry states CT-MR Brain was donated "
                "to the 3D Slicer project for use without restrictions."
            ),
        },
        "ct": {
            "size_xyz": list(image.GetSize()),
            "spacing_mm_xyz": list(image.GetSpacing()),
            "intensity_min": int(ct_array.min()),
            "intensity_max": int(ct_array.max()),
        },
        "parameters": {
            "bone_threshold_hu": BONE_THRESHOLD_HU,
            "defect_radius_mm": DEFECT_RADIUS_MM,
            "nominal_radial_patch_clearance_mm": PATCH_CLEARANCE_MM,
            "fit_side_band_mm": FIT_SIDE_BAND_MM,
            "defect_start_fraction_z": DEFECT_START_FRACTION_Z,
            **defect_parameters,
        },
        "segmentation": {
            "method": (
                "Threshold at 300 HU, one binary closing operation, then retain "
                "the largest 3D connected component."
            ),
            "skull_voxels": int(skull_mask.sum()),
            "skull_volume_mm3": float(skull_mask.sum() * voxel_volume),
            "removed_defect_voxels": int(skull_mask.sum() - defect_mask.sum()),
            "patch_voxels": int(patch_mask.sum()),
        },
        "mesh_checks": {
            "complete_skull_watertight": bool(complete_mesh.is_watertight),
            "defect_skull_watertight": bool(defect_mesh.is_watertight),
            "patch_watertight": bool(patch_mesh.is_watertight),
            "complete_skull_faces": int(len(complete_mesh.faces)),
            "defect_skull_faces": int(len(defect_mesh.faces)),
            "patch_faces": int(len(patch_mesh.faces)),
        },
        "fit_method": (
            "Nearest Euclidean distance from patch vertices in the cylindrical "
            "mating-side band to the defect-skull triangle surface."
        ),
        "fit_limitations": (
            "Clearance is quantized by the source voxel grid and marching-cubes "
            "resolution, especially the 2.528 mm slice spacing."
        ),
        "clearance_sample_count": int(len(distances)),
        "clearance_mm": metrics,
    }
    (OUTPUT_DIR / "skull_fit_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
