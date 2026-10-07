# Sources

Checked 7 Oct 2026.

## Benchmark

- Parametric CAD Bench V3:
  https://www.gnucleus.ai/cad-bench/news/cad-bench-v3
- Task used here: f32bdb2966 (Forked Mounting Bracket), staged locally under benchmark/.
- CAD Bench V3 suite was downloaded during the experiment with Harbor 0.23.0.

## CAD runtime

- FreeCAD 1.1.0:
  https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.0
- Linux x86_64 AppImage used:
  https://github.com/FreeCAD/FreeCAD/releases/download/1.1.0/FreeCAD_1.1.0-Linux-x86_64-py311.AppImage
- SHA-256 recorded during the experiment:
  ef85f171f2d09eec93f358bc49c1730d33f72bfbd353e6465609b30e45acf2f0

## Verifier

The official task verifier used:
- FreeCAD 1.1.0
- gnucleus-freecad-validator 0.6.0
- CAD Bench V3 geometry scorer
- the task's hidden reference.FCStd, spec.json, and parameter checks

Raw outputs are preserved in results/official-score/.

## Earlier Straive context

The exploration was partly motivated by:
- Pavan's 3D Floor Plan Benchmark:
  https://pavankumart18.github.io/3d-benchmark-analysis/
- Pavan's AI-Driven 3D Design Journey / Blender MCP:
  https://pavankumart18.github.io/ai-blender-design-journey/

The mechanical CAD benchmark superseded the earlier IFC/floor-plan direction for this class.
