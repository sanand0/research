# AI ↔ DATA sculpture

A small anamorphic LEGO sculpture: viewed from the front, the red bricks spell **AI**; viewed from the right, they spell **DATA**.

The interesting part is that the geometry is solved rather than hand-designed. Each possible (x, z, height) brick position is a binary variable. The optimizer minimizes occupied positions subject to:

- every required **AI** pixel appearing in the front projection;
- every required **DATA** pixel appearing in the side projection;
- red bricks appearing only where both projections permit red;
- every elevated brick having a continuous stack beneath it.

Transparent bricks provide the support needed to make the sparse red solution physically constructible.

## Result

The optimized design uses:

| Part | Color | Quantity |
|---|---|---:|
| 3005 Brick 1×1 | Red | 65 |
| 3005 Brick 1×1 | Trans-Clear | 70 |
| 3857 Baseplate 16×32 | Black | 1 |
| **Total** | | **136** |

The colored structure occupies 9×23 studs, is 7 bricks high (~6.7 cm), and consists of 20 vertical columns.

## Generate

From the parent lego/ directory:

~~~sh
just build ai-data
~~~

Important generated files:

~~~text
ai-data/build/
├── ai-data.ldr
├── bom.csv
├── bricklink-wanted-list.xml
├── columns.csv
├── front-ai.txt
└── side-data.txt
~~~

columns.csv is also a compact physical construction guide. Coordinates are 1-based positions on the 16×32 baseplate; each stack is written bottom-to-top with R for red and C for trans-clear.

## Render and verify

~~~sh
just render ai-data
~~~

This creates four canonical views and one image per LDraw construction step under ai-data/build/.

The generator itself checks the important nonvisual invariants:

- exact front and side red projections;
- support below every elevated brick;
- every column centered on a real stud;
- every column within the rotated 16×32 baseplate.

## Ordering bricks

ai-data/build/bricklink-wanted-list.xml contains the exact three-line parts request for BrickLink's Wanted List mass-upload flow. bom.csv contains the same quantities in a human-readable form.

The shopping list is generated rather than committed, so it cannot silently drift away from the geometry.

## Design notes

The first drafts exposed two useful CAD traps. LDraw brick coordinates are tied to the part origin, so level 0 initially intersected the baseplate and had to be moved one brick-height upward. Separately, the 9×23 structure has odd dimensions while the baseplate dimensions are even, so zero-centering placed columns between studs. The final model offsets X and Z by half a stud (10 LDU) and asserts alignment.

The current design deliberately uses only 1×1 bricks above the baseplate. That makes the optimization and build sheet simple, but it is probably not the best final physical engineering. A later version can merge support runs into larger transparent pieces and optimize for price, availability, strength, or ease of assembly while preserving the same two projections.
