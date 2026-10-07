# Step 2 findings — FreeCAD authoring/runtime

Status: DONE.

## Exact runtime

Installed the official FreeCAD 1.1.0 Linux x86_64 AppImage released 25 Mar 2026.

- file: tools/freecad/FreeCAD_1.1.0.AppImage
- SHA-256: ef85f171f2d09eec93f358bc49c1730d33f72bfbd353e6465609b30e45acf2f0
- runtime reports: FreeCAD 1.1.0 Revision 20260325

This machine has no working FUSE mount for AppImages, so the AppImage is extracted to tools/freecad/squashfs-root and invoked directly. This avoids root/kernel changes.

Reproducible setup:

    ./scripts/setup_freecad.sh

## Hidden reference successfully opened

benchmark/hidden/reference.FCStd opens cleanly in FreeCAD 1.1.0.

Reference facts measured directly from the model:

- exactly 1 PartDesign Body
- 8 body features:
  - Sketch
  - Pad
  - Sketch001
  - Pad
  - Sketch002
  - Pad
  - Sketch003
  - Pocket
- tip: Extrude3
- exactly 1 solid
- Shape.isValid(): true
- Shape.isClosed(): true
- bounding box: 150 × 88 × 48 mm
- volume: 177334.540463 mm³
- area: 39564.622775 mm²

This confirms the benchmark target is a real editable parametric model, not a baked Part::Feature.

## Direct FreeCAD Python authoring test

scripts/create_freecad_smoke.py created:

    Sketch -> PartDesign::Pad

with a 40 × 25 mm sketch padded to 10 mm.

Measured result:
- 1 valid closed solid
- volume: 10,000 mm³
- bounding box: 40 × 25 × 10 mm

scripts/edit_freecad_smoke.py then changed Pad.Length from 10 to 15 mm and recomputed.

Measured result:
- volume changed 10,000 -> 15,000 mm³
- Z extent changed 10 -> 15 mm
- model remained one valid closed solid

So raw FreeCAD Python is a clean, deterministic authoring mechanism and preserves parametric editability.

## FreeCAD MCP test

Tested current neka-nat/freecad-mcp:

- package version: 0.1.25
- git commit tested: 8e14693 (2026-10-06)
- MCP server exposed 17 tools
- useful tools include:
  - execute_code_headless
  - execute_code
  - execute_code_async
  - create/edit/get object
  - get_view
  - reload_document
  - run_fem_analysis

A real stdio MCP client called execute_code_headless with our exact FreeCAD 1.1 runtime and created a second parametric Sketch -> Pad model.

Measured result:
- 1 valid solid
- volume: 4,800 mm³
- bounding box: 30 × 20 × 8 mm

Important architectural observation: the MCP headless tool is mainly a clean agent boundary around arbitrary FreeCAD Python. That is a feature, not a weakness. It gives us timeout/crash isolation and a standard tool call while retaining full CAD expressiveness.

The GUI RPC addon was not required for the headless call.

## GUI / visual inspection test

A transient FreeCAD GUI session under Xvfb can open the reference and exit cleanly, but activeView().saveImage() produced blank white images on this machine. Therefore FreeCAD/Xvfb rendering is NOT reliable enough to put on the demo critical path.

Instead, a reliable visual path is now:

    FCStd -> FreeCAD Mesh.export(STL) -> Blender 5.2 Workbench render -> PNG

Tested on the hidden reference:
- FreeCAD exported a valid STL
- Blender imported and rendered it headlessly
- render time is a few seconds
- output is visibly correct and useful for inspection

One-command renderer:

    ./scripts/render_fcstd.sh model.FCStd output.png

Blender is only the renderer. FreeCAD remains the source of semantic/parametric truth.

## Interface decision

### Default for Step 3

**Agent -> FreeCAD MCP execute_code_headless -> raw FreeCAD Python -> FCStd**

Then independently:

**FCStd -> deterministic inspection/checks**

and when a visual is useful:

**FCStd -> STL -> Blender render**

### Why not GUI automation as the primary path?

- slower;
- stateful;
- visually fragile;
- unnecessary for most PartDesign operations;
- harder to reproduce in a classroom;
- screenshot behavior already exposed an Xvfb/OpenGL edge case.

The GUI remains useful for Anand/student inspection if desired, but the agent should author through code.

### Why keep MCP instead of only shell/Python?

MCP adds:
- an explicit bounded tool surface;
- crash/timeout isolation for headless OCCT work;
- a future path to live GUI inspection/get_view and FEM;
- a clean agent interaction transcript.

But MCP should not hide FreeCAD Python. The Python program itself is part of the artifact we want students to inspect.

## Revised Step 3

Blind reconstruction will use the selected engineering drawing only.

The reconstruction agent gets:
- benchmark/input/engineering-drawing.png
- benchmark/task/instruction.md
- FreeCAD MCP with execute_code_headless
- ability to render its own candidate via scripts/render_fcstd.sh

It does NOT get:
- benchmark/hidden/reference.FCStd
- benchmark/hidden/spec.json
- official grader internals

Outputs:
- candidate/answer.py
- candidate/answer.FCStd
- candidate/assumptions.md
- candidate/render.png
- trajectory/log of attempts

Do not score it until reconstruction is complete.
