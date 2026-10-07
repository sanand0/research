# Step 1 findings — benchmark selection

Selected: CAD Bench V3 f32bdb2966, Forked Mounting Bracket.

## Drawing facts

The source drawing is 1569×862 px and contains front, plan and end views. The hidden benchmark spec identifies key dimensions including:

- overall front envelope: 150 × 88 mm
- upper width: 90 mm
- boss OD: 35.98 mm
- boss bore: 20.3 mm
- boss center height: 66.82 mm
- base thickness: 10 mm
- shoulder transitions: R12
- lower profile radii: R6 and R3
- two Ø10 base holes
- base-hole spacing: 126 mm
- stepped depths visible in the end view: 10 / 35 / 48 mm

These values are for evaluator design only; the reconstruction agent must infer them from the drawing.

## Hidden reference structure

The FCStd contains one PartDesign Body with this compact construction sequence:

- Sketch → Pad (Extrude0)
- Sketch001 → Pad (Extrude1)
- Sketch002 → Pad (Extrude2)
- Sketch003 → Pocket (Extrude3)

That is a good teaching target: genuinely parametric/editable, but not so feature-heavy that feature-history reconstruction overwhelms visual reasoning.

## Alternatives rejected for the first run

- f4e56c467a Double Clevis Mount Base: attractive and very engineering-like, but more repeated geometry and slots; good second benchmark.
- d3bc21a2d4 Gusseted Mounting Bracket: good, but gussets + four slots add complexity before we know the authoring loop is stable.
- 5f11f1b4e0 Relay Housing: excellent section-view reasoning test, but 11 PartDesign features and many stepped tiers; better after the pipeline works.
- 5aff0c8399 Right Angle Support Bracket: probably too easy and its drawing carries less cross-view information.

## Environment note

Harbor 0.23.0 runs cleanly via uvx. A global uv tool install could not create the ~/.local/bin/harbor symlink because that location is read-only, so use:

    uvx --from harbor==0.23.0 harbor ...

The official FreeCAD 1.1.0 Docker image recipe is present in the downloaded task. The first build exceeded the current remote-command time window and did not complete, so Step 2 begins by resolving/runtime-testing that separately. No claim that FreeCAD itself is locally working has been made yet.
