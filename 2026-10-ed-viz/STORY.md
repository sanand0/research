# Development storyboard

> The canonical visual story is index.html. This file preserves the narrative notes used to build it.

# Can AI actually read an engineering drawing?


The question is deliberately stronger than **“Can AI make a plausible 3D object from a drawing?”**

An engineering drawing encodes dimensions, views, relationships and design intent. If an agent really understands it, we should be able to compile the drawing into an executable CAD model — and then test that model.

---

## 1. Give the agent the drawing, a CAD tool, and nothing else


We gave Codex:

- one dimensioned mechanical engineering drawing with front, side and plan views;
- FreeCAD 1.1.0 through freecadcmd;
- render-fcstd, which renders the generated FCStd for visual inspection;
- no reference CAD model;
- no grader;
- no web/search.

The core instruction was:

> Reconstruct the part shown in the engineering drawing as a parametric FreeCAD PartDesign model. The drawing is the only source of geometry. Produce one valid solid with named, editable features. Iterate: author, run, inspect, render, improve.

The successful run used Codex CLI 0.160.0. A local smoke test reported **GPT-6.1 Sol**; the saved reconstruction trajectory itself does not record model identity, so treat that model label as environment evidence rather than provenance embedded in the run.

---

## 2. The first run did not even get to CAD


Codex began sensibly: compare the three views and inspect the fork opening and radius callouts.

Then it got caught in a viewing/tooling detour. It tried to make enlarged crops of the front, side and plan views. One ImageMagick path hit an AppImage/FUSE problem; another crop command recovered, but the run spent its budget inspecting rather than constructing.

**Result: no CAD model before the run ended.**

We changed the orchestration, not the underlying task:

> Use the attached drawing directly. Do not crop it. Start CAD authoring immediately. Prefer a reasonable valid reconstruction over endless interpretation.

That small change mattered.

---

## 3. Codex built a plausible first model


The next run immediately wrote answer.py, ran it through FreeCAD, and produced an editable PartDesign model.

Its first self-check looked excellent:

- bounding box: **150 × 48 × 88 mm**;
- exactly **1 solid**;
- FreeCAD said the shape was **valid**;
- volume: **161,285 mm³**;
- the rendered part looked like the object in the drawing.

At this point it would have been easy to declare success.

---

## 4. It did notice something and correct itself


After rendering the first version, Codex explicitly reconsidered its interpretation:

> “The first model is a valid single solid with a 150 × 48 × 88 mm bounding box. I’ll refine the eye to use the visible Ø35.98 circular profile and a 35 mm-deep support…”

Putting **before and after in the same isometric view** makes the correction much easier to see without any callout boxes.

The first construction treated the eye and its support as one 48 mm-deep feature. Codex revised that into:

- a **35 mm-deep support stem**, and
- a **48 mm-deep circular eye**.

It rebuilt and rendered the CAD model again.

This is real self-correction. The agent did not merely emit one answer.

---

## 5. The final model passed every test Codex had chosen for itself


The final candidate had:

- the exact **150 × 48 × 88 mm** envelope;
- one valid, closed solid;
- an editable PartDesign feature tree;
- seven sketches and seven additive/subtractive CAD operations;
- a convincing isometric render.

Its final volume was **153,071 mm³**.

Nothing in its own checks said “wrong.”

So: **did it understand the engineering drawing?**

---

## 6. Only now reveal the hidden reference


The benchmark had a hidden reference FreeCAD model that the agent never saw.

For every comparison from here onward, I rigidly re-oriented the reference into the Codex coordinate frame and render both with the **same center, scale, orientation, and camera**. No independent auto-cropping or camera fitting.

From a casual glance, the aligned reference and candidate still look like the same class of part.

That is why visual plausibility is such a dangerous stopping criterion.

---

## 7. What does CAD Bench actually verify?


For this task, the benchmark gives the verifier three things:

1. the agent's **candidate FCStd**;
2. a **held-back reference FCStd**;
3. a **held-back specification** containing 30 parameters.

The task wrapper calls freecad_validator.Validator().validate(...), which returns two largely independent scores.

### Geometry fidelity

The reported geometry diagnostics include:

- solid-count match;
- an oriented-bounding-box gate;
- surface-type distribution;
- volume;
- surface area;
- principal moments of the solid;
- ICP alignment of face centres, including RMSE and maximum residual.

These feed a geometry-similarity score. The task wrapper exposes the final geometry score and the diagnostic breakdown; it does not expose the validator's internal weighting of every geometry sub-check.

### Specification consistency

The held-back spec asks whether required dimensions/counts can be found in the candidate geometry and feature history.

For this candidate:

- **27 consistent**;
- **2 inconsistent**;
- **1 not found**.

This benchmark version uses a failure budget of 10, so three failures produce a **0.70 spec score**.

Finally, CAD Bench combines geometry similarity and spec consistency using their **harmonic mean**. That matters: doing very well on dimensions cannot rescue a geometrically wrong model.

---

## 8. Now the score is surprising


The verifier reported:

**Spec consistency = 0.700.**

But:

**Geometry similarity = 0.0423 — just 4.2%.**

Combined:

**0.0798.**

Even the outer oriented bounding box matched exactly.

So the agent had read most of the numbers, built a valid editable CAD object, and matched the overall dimensions — while still reconstructing substantially the wrong engineered object.

One caution: “27/30” is not equivalent to “90% semantically correct.” The spec checker searches measurement pools for matching values, so a few values can match the wrong feature. The independent geometry comparison is the more revealing signal.

---

## 9. Put reference and candidate in the same isometric view


This is the comparison that makes the mistake easiest to see. No arrows or feature boxes are needed: the overall envelope is similar, but the **distribution of material around the fork, support and eye is visibly different**.

Blinking between the two removes even more distraction:


A third view removes shading altogether and compares only the aligned silhouettes:


This makes “same bounding box” look much less reassuring.

---

## 10. The deeper error: two different construction stories


The hidden reference builds the object with **three interlocking additive profiles and one final pocket**.

Those profiles encode the detailed shape together — including the **R3, R6 and R12 transitions**, fork geometry, boss and depth relationships.

Codex chose a different decomposition:

**base + upright → rectangular stem + separate eye → rectangular fork pocket + bore → mounting holes.**

That is a perfectly reasonable *story* for how the object might be built.

It just is not geometrically equivalent to the drawing.

The most explicit spec misses were exactly in the simplified lower profile:

- expected **R3**, nearest candidate radius was **R5**;
- expected **R6**, but no R6 witness existed in the final geometry;
- expected one **46.39 mm** fork reference, nearest candidate measurement was **48 mm**.

The bigger failure is not any single number. It is that the numbers were attached to the **wrong geometric relationships**.

---

## 11. Independent geometry checks caught what visual plausibility missed


Reference versus candidate:

- bounding box difference: **0.0%**;
- volume difference: **13.7%**;
- surface-type difference: **20.2%**;
- principal-moment difference: **16.8%**;
- aligned face-centre RMSE: **8.44 mm**;
- maximum aligned residual: **23.45 mm**.

The envelope was right.

The material distribution and surfaces were not.

---

## 12. Why did self-correction still fail?


A plausible explanation is that the agent optimized what it could observe.

It checked:

- the bounding box;
- solid validity;
- solid count;
- editability;
- its own rendered image.

Those are useful tests — but they are **weak proxies for engineering fidelity**.

It did not independently test:

- whether the R3/R6 profile geometry existed in the final solid;
- whether mass was distributed correctly;
- whether surface topology matched;
- whether a dimension had been attached to the **right feature and relationship**.

So its self-correction made the model more internally coherent without making it sufficiently faithful.

This is an inference from the trajectory and evaluation, not a demonstrated internal mechanism of the model.

---

## 13. The practical lesson: give the agent a CAD-Bench-like verification kit


This may be the most important lesson from the experiment.

If we tell an agent only:

> “Build the CAD model, make it valid, and check that it looks right.”

then **valid + plausible** becomes a natural stopping rule.

Instead, the specification / verification kit should include the kinds of things an independent CAD benchmark checks:

- valid solid and editable feature structure;
- required dimensions, counts, radii, holes and offsets;
- checks that those dimensions belong to the **right features**;
- bounding box;
- volume and surface area;
- mass / principal moments;
- surface types and topology;
- geometric alignment / residuals;
- where relevant, assembly, clearance, manufacturability or physics tests.

And crucially, these checks should be available **during generation**, not only afterward.

The loop becomes:

**draw → model → test → diagnose → repair → retest.**

A broader lesson:

> **Self-verification is only as strong as the verification kit.**

If we want an agent to behave like an engineer, we have to give it engineering-grade ways to know when it is wrong.

---

## 14. So what does “understand an engineering drawing” mean?


Is understanding:

- reading the dimension callouts?
- producing a recognizable shape?
- recovering exact geometry?
- recovering feature relationships and design intent?
- producing a model that survives independent engineering tests?

The experiment suggests a useful distinction:

> **Reading the numbers is not enough. The numbers have to constrain the right geometry and relationships.**

And that turns “Can AI read an engineering drawing?” from a vision question into a much richer engineering question:

**What representation should it produce, and what tests would convince us that it understood?**