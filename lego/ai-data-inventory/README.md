# AI ↔ DATA from the bricks on hand

This is an inventory-constrained version of the ../ai-data/ dual-perspective sculpture.

The goal is unchanged: from the front, the bright bricks spell AI; from the right, they spell DATA. The difference is that this version is designed around the actual bricks available rather than assuming transparent supports.

## Design

The optimized structure uses 80 1×1 bricks in 13 vertical columns:

- 52 bright signal bricks form the AI / DATA projections.
- 28 dark support bricks hold those signal bricks up.

The support palette uses maroon, grey, black, and brown. Those colors visually recede compared with the white, light-blue, cream, yellow, orange, red, green, pink, and lime signal bricks. This contrast is important: an earlier render using white supports looked much less legible because the support pixels competed with the letters.

The structure is 7 bricks high on a 7×15-stud footprint. It sits on the existing green baseplate; the generator renders it using a green 16×32 LDraw baseplate.

## Inventory

inventory.json records the supplied counts. The "+ similar piece" allowances are included for brown, red, and black.

The final design uses:

| Color | Used | Available |
|---|---:|---:|
| Maroon | 13 | 13 |
| Light blue | 9 | 15 |
| Grey | 7 | 7 |
| Cream | 7 | 10 |
| Red | 6 | 7 |
| Yellow | 6 | 8 |
| Orange | 6 | 6 |
| Green | 5 | 5 |
| Black | 5 | 5 |
| Brown | 3 | 6 |
| Pink (5-piece shade) | 2 | 5 |
| Pink (3-piece shade) | 2 | 3 |
| Light green | 1 | 3 |
| White | 8 | 28 |

Blue and the five white 2×1 bricks are not needed by this version.

## Generate and render

From the parent lego/ directory:

    just build ai-data-inventory
    just render ai-data-inventory

Generated artifacts go under ai-data-inventory/build/ and are ignored by git.

Important outputs:

- ai-data.ldr — complete LDraw model.
- bom.csv — parts used by the design.
- inventory-usage.csv — used / available / remaining counts.
- columns.csv — physical build guide, one stack per row.
- front.png, right.png, home.png, top.png — canonical renders.
- steps/ — one render per build layer.

## Reproducibility and checks

The generator performs a two-stage integer optimization:

1. Minimize the number of occupied 1×1 positions while enforcing continuous support.
2. Among minimum-piece solutions, prefer a centered, visually coherent 13-column arrangement.

It then asserts:

- the optimum is exactly 80 bricks;
- the signal projection is exactly AI from the front and DATA from the right;
- every elevated brick has support below it;
- all columns sit on real baseplate studs and remain within its bounds;
- every color count stays within inventory.json;
- the model contains exactly 52 signal bricks and 28 support bricks.

The geometry and palette are intentionally separate. The optimizer decides where bricks go; the palette makes the information readable in the real opaque-brick build.

## Iterations

The first inventory draft used pale/white supports and saturated signal colors. The real LeoCAD render showed that opaque white supports created distracting false pixels in the canonical views.

The second draft inverted that relationship: dark supports and pale signals. It was much more readable, but the isometric view was visually flat.

The final version keeps dark supports but uses a controlled bright/rainbow signal palette. The front/right views preserve strong contrast while the angled view looks like an intentional multicolor sculpture.
