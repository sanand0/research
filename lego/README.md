# Agent-designed LEGO

This directory is a reproducible workspace for designing physical LEGO models with code and agents.

The basic loop is:

1. Describe a structure and its constraints.
2. Generate an [LDraw](https://www.ldraw.org/) model programmatically.
3. Render it headlessly with [LeoCAD](https://www.leocad.org/).
4. Inspect the renders and machine-check geometry/buildability constraints.
5. Iterate on the design.
6. Emit an exact bill of materials and BrickLink Wanted List for buying the physical bricks.

Each LEGO structure lives in its own subdirectory. Shared fetching/rendering machinery stays here so future models do not duplicate it.

## Projects

- [ai-data/](ai-data/) — a 136-piece dual-perspective sculpture that reads **AI** from the front and **DATA** after a 90° rotation.
- [ai-data-inventory/](ai-data-inventory/) — an 80-piece version constrained to the bricks on hand, using bright signal bricks over dark structural supports.

## Why this approach

LDraw is unusually agent-friendly: a model is plain text describing real parts, colors, positions, and rotations. An agent can therefore edit the actual geometry rather than drive a CAD GUI with mouse clicks. LeoCAD can render LDraw from the command line, giving a tight generate → render → inspect → revise loop.

The first experiment also showed why rendering alone is not enough. Two visually plausible drafts were physically wrong:

- the first vertical placement intersected the baseplate;
- centering a 9×23-stud structure on an even-sized baseplate put every column half a stud off-grid.

The current generator asserts stud-grid alignment, baseplate bounds, exact text projections, and continuous vertical support. The main reusable lesson is: **encode buildability as constraints, not as visual judgment after generation.**

## Repository layout

~~~text
lego/
├── README.md
├── justfile
├── scripts/
│   ├── fetch_ldraw.py      # shared minimal LDraw-library fetcher
│   └── render.sh           # shared headless rendering
├── ai-data/
│   ├── README.md
│   ├── generate.py         # model-specific optimizer + artifact generator
│   └── parts.txt           # top-level LDraw parts this model needs
└── ai-data-inventory/
    ├── README.md
    ├── generate.py
    ├── inventory.json      # available physical brick counts
    └── parts.txt
~~~

Generated files go under PROJECT/build/ and downloaded official LDraw geometry under .cache/ldraw/. Both are ignored by git.

A future structure should normally add only a new directory containing a generator, a short README, and parts.txt. Promote code to scripts/ only when multiple structures genuinely share it.

## Requirements

- [uv](https://docs.astral.sh/uv/) to run Python with declared dependencies.
- [just](https://github.com/casey/just) for the small build interface.
- LeoCAD for rendering.

On Ubuntu, the normal system install is:

~~~sh
sudo apt update
sudo apt install --no-install-recommends leocad
~~~

The build does **not** require a preinstalled LDraw parts library. just parts recursively downloads only the official geometry referenced by the selected model from library.ldraw.org.

If LeoCAD is not on PATH, set LEOCAD explicitly. On the machine where this project was created it is installed user-locally:

~~~sh
export LEOCAD="$HOME/.local/opt/leocad/leocad"
~~~

## Run

From this directory:

~~~sh
just build
~~~

This generates the LDraw model, BOM, BrickLink XML, coordinate build sheet, and text projections for the default ai-data project.

~~~sh
just render
~~~

This additionally fetches the required LDraw geometry and renders front/right/home/top views plus each construction step.

~~~sh
just test
~~~

test is currently the end-to-end verification: generation assertions must pass and all renders must complete.

All recipes accept another project name, so future models follow the same interface:

~~~sh
just build my-new-model
just render my-new-model
~~~

## Outputs

A model generator should produce, where applicable:

- *.ldr — canonical LDraw model;
- bom.csv — exact parts/colors/quantities;
- bricklink-wanted-list.xml — importable shopping list;
- a coordinate/build sheet when that is clearer than visual instructions;
- projection or other machine-readable verification artifacts.

Renders are evidence and diagnostics, not source files, so they are regenerated instead of committed.

## What we learned so far

**Plain-text CAD works well with agents.** The model can be generated and modified structurally, diffed in git, and rendered without GUI automation.

**Optimize the physical object, not just the picture.** The AI↔DATA model is an integer program minimizing occupied 1×1 brick positions while satisfying two exact orthogonal projections and continuous support.

**Coordinate systems are a real failure mode.** LDraw uses 20 LDU per stud and 24 LDU per brick height. Part origins and odd/even grid parity matter; a model can look plausible while being impossible to attach.

**A minimal parts library is enough.** The shared fetcher follows LDraw references recursively, so a model can render without downloading the full official parts archive.

**Headless rendering works; LeoCAD's HTML instruction exporter did not.** In this Linux/Qt setup the HTML exporter segfaulted. Rendering individual LDraw steps with -f/-t worked reliably and is the chosen path.

## Current limitations

The AI↔DATA design has been checked geometrically but has not yet been physically built. In particular, tall 1×1 columns are valid LEGO connections but may be easy to knock over, and transparent bricks are not optically invisible. A useful next refinement is to replace compatible runs with larger common transparent elements while preserving the projections and minimizing cost/fragility.
