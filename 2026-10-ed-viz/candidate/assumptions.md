# Blind reconstruction assumptions

Provenance: this file was reconstructed after the blind run from the agent's own answer.py and trajectory2.jsonl because the agent hit its execution cap before writing the promised assumptions file. No hidden reference FCStd, grader spec, or Step 4 score was used.

## Dimensions the agent treated as directly read from the drawing

- Overall front envelope: 150 mm wide × 88 mm high.
- Lower inner/back-plate width: 138 mm.
- Upper width: 90 mm.
- Base/rear-plate thickness: 10 mm.
- Main mounting depth: 35 mm.
- Overall eye depth: 48 mm.
- Shoulder transitions: R12.
- Eye outside diameter: 35.98 mm.
- Eye bore: Ø20.3 mm.
- Eye center height: 66.82 mm.
- Fork opening width: 50.39 mm.
- Fork opening height/reference: 25 mm.
- Two base mounting holes: Ø10 mm.
- Base-hole pitch: 126 mm.
- Base-hole depth offset: 23 mm.

## Construction interpretations made by the agent

- X is the front-view horizontal direction, Y is depth, Z is height.
- The base is represented as a 150 × 35 mm plan profile padded 10 mm.
- The rear upright is modeled from the front outline and padded 10 mm.
- A central rectangular support stem is padded to 35 mm depth.
- The circular eye is a separate additive feature padded to the full 48 mm depth.
- The fork is modeled as a rectangular pocket through the relevant front geometry.
- The eye bore is modeled as a through pocket.
- The two mounting holes are modeled together in one plan sketch/pocket.
- The R12 shoulder regions are represented by circular arcs joining the lower 138 mm region to the 90 mm upper region.

## Approximations / known uncertainties in this reconstruction

- The lower R6 / R3 profile details visible in the engineering drawing were not explicitly modeled.
- The fork profile was simplified to a rectangular opening; small corner/transition details were not reconstructed.
- The exact tangent construction of the shoulder curves was inferred rather than constrained dimensionally in Sketcher.
- The relation between the 10, 35 and 48 mm depth steps was interpreted from the side/plan views rather than built from explicit datums.
- No additional small fillets/chamfers were introduced unless they were necessary to form the main outline.
- Sketch dimensions are encoded by Python coordinates rather than named dimensional constraints, so the result is editable/parametric at the feature level but not a fully constrained engineering Sketcher model.
