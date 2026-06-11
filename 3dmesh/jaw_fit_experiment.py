#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "numpy>=2.0",
#   "plotly>=6.0",
#   "rtree>=1.3",
#   "scipy>=1.14",
#   "trimesh>=4.6",
# ]
# ///
"""Generate a synthetic bone-like mesh and close-fitting implant shell.

This is a synthetic toy model for CAD/mesh experimentation. It is not a
medical, anatomical, or implant design.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys

try:
    import numpy as np
    import plotly.graph_objects as go
    import trimesh
    from scipy.spatial import cKDTree
except ModuleNotFoundError:
    # Keep `python jaw_fit_experiment.py` reproducible on machines with uv installed.
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("Missing dependencies. Install uv, then rerun this script.") from None
    os.execv(uv, [uv, "run", "--script", str(Path(__file__).resolve()), *sys.argv[1:]])


# Key experiment parameters, in millimeters unless noted otherwise.
RANDOM_SEED = 20260611
MESH_RESOLUTION = 4  # Icosphere subdivisions; 4 produces 5,120 triangles.
PATCH_LOCATION = np.array([0.58, 0.66, -0.48])  # right, front, lower
PATCH_SIZE = (0.48, 0.38)  # angular half-widths around patch center
CLEARANCE_MM = 0.75
SHELL_THICKNESS_MM = 2.5
CLEARANCE_SAMPLE_COUNT = 500
VECTOR_COUNT = 12
VECTOR_DISPLAY_SCALE = 8.0  # Visual exaggeration only; does not alter geometry.

OUTPUT_DIR = Path(__file__).resolve().parent
DISCLAIMER = (
    "Synthetic toy model only. Not a medical, anatomical, surgical, or implant design."
)


def unit_rows(values: np.ndarray) -> np.ndarray:
    """Normalize an array of row vectors."""
    return values / np.linalg.norm(values, axis=1, keepdims=True)


def gaussian_direction(
    directions: np.ndarray, center: tuple[float, float, float], width: float
) -> np.ndarray:
    """Return a smooth directional bump centered on a unit-sphere direction."""
    center_unit = np.asarray(center, dtype=float)
    center_unit /= np.linalg.norm(center_unit)
    angular_distance = np.arccos(np.clip(directions @ center_unit, -1.0, 1.0))
    return np.exp(-0.5 * (angular_distance / width) ** 2)


def create_irregular_bone() -> trimesh.Trimesh:
    """Create an asymmetric, watertight, skull/jaw-like synthetic solid."""
    rng = np.random.default_rng(RANDOM_SEED)
    sphere = trimesh.creation.icosphere(subdivisions=MESH_RESOLUTION, radius=1.0)
    directions = unit_rows(sphere.vertices)

    # Smooth low-frequency organic variation plus deliberate local anatomy-like forms.
    noise = np.zeros(len(directions))
    for _ in range(14):
        center = unit_rows(rng.normal(size=(1, 3)))[0]
        amplitude = rng.uniform(-0.055, 0.055)
        width = rng.uniform(0.18, 0.52)
        noise += amplitude * gaussian_direction(directions, tuple(center), width)

    shape = 1.0 + noise
    shape += 0.18 * gaussian_direction(directions, (0.0, 0.85, -0.52), 0.27)  # chin
    shape += 0.10 * gaussian_direction(directions, (0.66, 0.63, -0.40), 0.22)
    shape += 0.07 * gaussian_direction(directions, (-0.72, 0.52, -0.35), 0.24)
    shape -= 0.13 * gaussian_direction(directions, (0.58, 0.70, 0.25), 0.19)
    shape -= 0.09 * gaussian_direction(directions, (-0.50, 0.78, 0.28), 0.22)
    shape -= 0.08 * gaussian_direction(directions, (0.68, -0.20, -0.68), 0.20)

    # Narrow the lower half and flatten the back to move away from an ellipsoid.
    lower = np.clip(-directions[:, 2], 0.0, 1.0)
    shape *= 1.0 - 0.16 * lower**1.7
    shape *= 1.0 - 0.06 * np.clip(-directions[:, 1], 0.0, 1.0)

    axes = np.array([54.0, 45.0, 61.0])
    vertices = directions * shape[:, None] * axes
    vertices[:, 0] += 2.3 * directions[:, 1] * directions[:, 2]  # asymmetry
    vertices[:, 1] += 1.7 * np.clip(directions[:, 0], 0.0, 1.0) ** 2

    bone = trimesh.Trimesh(vertices=vertices, faces=sphere.faces, process=True)
    bone.fix_normals()
    return bone


def patch_coordinates(directions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project directions onto a tangent frame around PATCH_LOCATION."""
    center = PATCH_LOCATION / np.linalg.norm(PATCH_LOCATION)
    tangent_a = np.cross(center, np.array([0.0, 0.0, 1.0]))
    tangent_a /= np.linalg.norm(tangent_a)
    tangent_b = np.cross(center, tangent_a)
    denominator = np.maximum(directions @ center, 0.15)
    return (directions @ tangent_a) / denominator, (directions @ tangent_b) / denominator


def create_implant_shell(
    bone: trimesh.Trimesh,
) -> tuple[trimesh.Trimesh, trimesh.Trimesh, np.ndarray]:
    """Extract a local bone patch and turn its offsets into a closed solid shell."""
    directions = unit_rows(bone.vertices)
    patch_u, patch_v = patch_coordinates(directions)
    inside = (patch_u / PATCH_SIZE[0]) ** 2 + (patch_v / PATCH_SIZE[1]) ** 2 <= 1.0
    selected_faces = inside[bone.faces].all(axis=1)

    patch = bone.submesh([selected_faces], append=True, repair=False)
    patch.remove_unreferenced_vertices()
    patch.fix_normals()
    if len(patch.faces) < 30:
        raise RuntimeError("Patch is too small; increase PATCH_SIZE.")

    normals = patch.vertex_normals.copy()
    inner_vertices = patch.vertices + CLEARANCE_MM * normals
    outer_vertices = patch.vertices + (CLEARANCE_MM + SHELL_THICKNESS_MM) * normals
    vertex_count = len(patch.vertices)

    edge_counts: dict[tuple[int, int], int] = {}
    oriented_edges: dict[tuple[int, int], tuple[int, int]] = {}
    for face in patch.faces:
        for start, end in zip(face, np.roll(face, -1)):
            key = tuple(sorted((int(start), int(end))))
            edge_counts[key] = edge_counts.get(key, 0) + 1
            oriented_edges[key] = (int(start), int(end))
    boundary_edges = [oriented_edges[key] for key, count in edge_counts.items() if count == 1]

    outer_faces = patch.faces.copy() + vertex_count
    inner_faces = patch.faces[:, ::-1].copy()
    side_faces = []
    for start, end in boundary_edges:
        side_faces.extend(
            [
                [start, end, end + vertex_count],
                [start, end + vertex_count, start + vertex_count],
            ]
        )

    implant = trimesh.Trimesh(
        vertices=np.vstack([inner_vertices, outer_vertices]),
        faces=np.vstack([inner_faces, outer_faces, np.asarray(side_faces)]),
        process=True,
    )
    implant.fix_normals(multibody=True)
    inner_surface = trimesh.Trimesh(
        vertices=inner_vertices, faces=patch.faces.copy(), process=False
    )
    return implant, inner_surface, normals


def clearance_diagnostics(
    bone: trimesh.Trimesh, inner_surface: trimesh.Trimesh
) -> tuple[dict[str, float], np.ndarray]:
    """Measure approximate nearest-surface clearance at inner-surface vertices."""
    closest, clearance, _ = trimesh.proximity.closest_point(bone, inner_surface.vertices)
    del closest
    metrics = {
        "min": float(np.min(clearance)),
        "p05": float(np.percentile(clearance, 5)),
        "median": float(np.median(clearance)),
        "p95": float(np.percentile(clearance, 95)),
        "max": float(np.max(clearance)),
        "mean": float(np.mean(clearance)),
    }
    return metrics, clearance


def mesh_trace(mesh: trimesh.Trimesh, **kwargs: object) -> go.Mesh3d:
    """Create a Plotly mesh trace."""
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
    bone: trimesh.Trimesh,
    implant: trimesh.Trimesh,
    inner_surface: trimesh.Trimesh,
    normals: np.ndarray,
    clearance: np.ndarray,
) -> None:
    """Write an interactive, self-contained Plotly HTML inspection view."""
    rng = np.random.default_rng(RANDOM_SEED)
    sample_count = min(CLEARANCE_SAMPLE_COUNT, len(inner_surface.vertices))
    sample_ids = rng.choice(len(inner_surface.vertices), sample_count, replace=False)
    vector_ids = rng.choice(len(inner_surface.vertices), min(VECTOR_COUNT, sample_count), False)

    vector_x: list[float | None] = []
    vector_y: list[float | None] = []
    vector_z: list[float | None] = []
    for vertex_id in vector_ids:
        start = inner_surface.vertices[vertex_id] - CLEARANCE_MM * normals[vertex_id]
        end = start + CLEARANCE_MM * VECTOR_DISPLAY_SCALE * normals[vertex_id]
        vector_x.extend([start[0], end[0], None])
        vector_y.extend([start[1], end[1], None])
        vector_z.extend([start[2], end[2], None])

    figure = go.Figure(
        data=[
            mesh_trace(
                bone,
                name="Synthetic bone",
                color="#d8c5a5",
                opacity=0.42,
                flatshading=False,
                lighting={"ambient": 0.55, "diffuse": 0.8, "specular": 0.2},
            ),
            mesh_trace(
                implant,
                name="Implant shell",
                color="#2878b8",
                opacity=0.72,
                flatshading=False,
                lighting={"ambient": 0.45, "diffuse": 0.8, "specular": 0.7},
            ),
            go.Scatter3d(
                x=inner_surface.vertices[sample_ids, 0],
                y=inner_surface.vertices[sample_ids, 1],
                z=inner_surface.vertices[sample_ids, 2],
                mode="markers",
                name="Inner-surface clearance",
                marker={
                    "size": 3.5,
                    "color": clearance[sample_ids],
                    "colorscale": "Turbo",
                    "colorbar": {"title": "Clearance (mm)"},
                },
                text=[f"{value:.3f} mm" for value in clearance[sample_ids]],
                hovertemplate="Nearest clearance: %{text}<extra></extra>",
            ),
            go.Scatter3d(
                x=vector_x,
                y=vector_y,
                z=vector_z,
                mode="lines",
                name=f"Clearance vectors ({VECTOR_DISPLAY_SCALE:g}x display)",
                line={"color": "#e63946", "width": 5},
                hoverinfo="skip",
            ),
        ]
    )
    figure.update_layout(
        title={
            "text": "Synthetic Jaw Fit Experiment<br><sup>"
            + DISCLAIMER
            + "</sup>",
            "x": 0.5,
        },
        template="plotly_white",
        scene={
            "aspectmode": "data",
            "xaxis_title": "Right / left (mm)",
            "yaxis_title": "Front / back (mm)",
            "zaxis_title": "Up / down (mm)",
            "camera": {"eye": {"x": 1.45, "y": 1.45, "z": 0.75}},
        },
        legend={"orientation": "h", "y": 0.02, "x": 0.02},
        margin={"l": 0, "r": 0, "t": 80, "b": 0},
    )
    figure.write_html(
        OUTPUT_DIR / "jaw_fit_experiment.html",
        include_plotlyjs=True,
        full_html=True,
        config={"displaylogo": False, "scrollZoom": True},
    )


def simulate_uniform_thermal_expansion(
    bone: trimesh.Trimesh,
    implant: trimesh.Trimesh,
    alpha_bone: float,
    alpha_implant: float,
    delta_T: float,
) -> tuple[trimesh.Trimesh, trimesh.Trimesh, dict[str, float]]:
    """Apply first-order uniform expansion and estimate vertex-to-vertex clearance.

    Replace this toy isotropic scaling model when real material coefficients,
    temperature fields, constraints, or nonlinear mechanics become available.
    """
    expanded_bone = bone.copy()
    expanded_implant = implant.copy()
    expanded_bone.apply_scale(1.0 + alpha_bone * delta_T)
    expanded_implant.apply_scale(1.0 + alpha_implant * delta_T)
    tree = cKDTree(expanded_bone.vertices)
    distances, _ = tree.query(expanded_implant.vertices)
    metrics = {
        "min": float(np.min(distances)),
        "median": float(np.median(distances)),
        "max": float(np.max(distances)),
        "mean": float(np.mean(distances)),
    }
    return expanded_bone, expanded_implant, metrics


def main() -> None:
    """Generate all experiment artifacts."""
    print("Generating synthetic irregular bone mesh...")
    bone = create_irregular_bone()
    print("Constructing close-fitting implant shell...")
    implant, inner_surface, normals = create_implant_shell(bone)
    print("Computing clearance diagnostics...")
    metrics, clearance = clearance_diagnostics(bone, inner_surface)

    bone.export(OUTPUT_DIR / "bone_irregular_mesh.stl")
    implant.export(OUTPUT_DIR / "implant_fit_shell.stl")
    create_visualization(bone, implant, inner_surface, normals, clearance)

    report = {
        "disclaimer": DISCLAIMER,
        "units": "mm",
        "parameters": {
            "random_seed": RANDOM_SEED,
            "mesh_resolution": MESH_RESOLUTION,
            "patch_location": PATCH_LOCATION.tolist(),
            "patch_size": list(PATCH_SIZE),
            "nominal_clearance_mm": CLEARANCE_MM,
            "shell_thickness_mm": SHELL_THICKNESS_MM,
        },
        "mesh_checks": {
            "bone_is_watertight": bool(bone.is_watertight),
            "implant_is_watertight": bool(implant.is_watertight),
            "bone_vertices": int(len(bone.vertices)),
            "bone_faces": int(len(bone.faces)),
            "implant_vertices": int(len(implant.vertices)),
            "implant_faces": int(len(implant.faces)),
        },
        "clearance_method": (
            "Nearest Euclidean distance from each implant inner-surface vertex "
            "to the synthetic bone triangle surface."
        ),
        "clearance_sample_count": int(len(clearance)),
        "clearance_mm": metrics,
    }
    (OUTPUT_DIR / "fit_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
