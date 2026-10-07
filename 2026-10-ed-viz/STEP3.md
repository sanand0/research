# Step 3 findings — blind reconstruction

Status: DONE.

## Isolation

The successful reconstruction run used a sanitized workspace containing only:

- engineering-drawing.png
- sanitized instruction.md
- README.md
- standalone freecadcmd and render-fcstd executables on PATH

During the run the entire 2026-10-ed-viz research repo was renamed and chmod 000, so the agent could not access:

- benchmark/hidden/reference.FCStd
- benchmark/hidden/spec.json
- the downloaded CAD Bench task's verifier/reference files
- prior Step 1/2 notes containing evaluator-derived details

The visible task text also removed the CAD Bench task ID to discourage online lookup.

Trajectory audit found no web search and no curl/wget/http access. The successful second run stayed within the blind workspace for its modeling commands.

## Agent / runtime

- Codex CLI 0.160.0
- model reported by local smoke test: GPT-6.1 Sol
- reasoning effort for successful run: medium
- exact FreeCAD runtime: 1.1.0
- visual feedback: FCStd → STL → Blender render

The first strict sandbox attempt failed because Codex's bwrap sandbox cannot initialize on this host. A later blind run used filesystem isolation instead.

## Result

Outputs:

- candidate/answer.py
- candidate/answer.FCStd
- candidate/render.png
- candidate/assumptions.md
- candidate/trajectory2.jsonl

The agent hit the 95-second execution cap immediately after a second geometry refinement and render, so it did not write assumptions.md itself. That file was reconstructed afterward strictly from the agent's source and trajectory, without reading the hidden evaluator.

## Self-checks before revealing ground truth

The candidate opens cleanly in FreeCAD 1.1.0 and has:

- exactly 1 PartDesign Body
- exactly 1 solid
- Shape.isValid() == True
- closed solid
- bounding box: 150 × 48 × 88 mm
- volume: 153070.938368 mm³
- area: 37297.379769 mm²

Feature tree: 14 Body members = 7 sketches + 7 PartDesign operations:

1. BasePlan → Pad BasePlate_10mm
2. UprightOutline → Pad RearUpright_10mm
3. StemOutline → Pad StemSupport_35mm
4. EyeOuterProfile → Pad CircularEye_48mm
5. ForkOpening → Pocket ForkClearance_50_39mm
6. EyeBoreProfile → Pocket EyeBore_20_3mm
7. MountingHolesPlan → Pocket TwoMountingHoles_10mm

The generated isometric render is visually recognisable as the bracket in the source drawing: broad mounting foot, shaped upright, raised bored eye, lower central opening and two mounting holes.

## Interesting blind-run behavior

The first blind run spent nearly all its budget trying to generate enlarged image crops and never authored CAD. The second prompt explicitly prohibited cropping and told the agent to start modeling immediately. It then produced a valid model quickly.

That is already a useful class observation: agent orchestration / representation strategy can dominate capability. The same model went from "no artifact" to a usable parametric solid just by changing the workflow constraints.

The successful agent initially modeled the eye/support as one deep feature, rendered it, then revised the design into:
- a 35 mm support stem; and
- a separate circular eye extending to 48 mm depth.

So the render/check loop did cause a structural revision before the run ended.

## Do not interpret accuracy yet

This step intentionally checks only internal validity and blind-run integrity.

No comparison to the hidden reference.FCStd or spec.json has yet been made. That is Step 4.
