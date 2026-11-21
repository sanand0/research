# Notes

## 21 Nov 2026

- Goal: catalog every technique in Felix Rieseberg's HTML-in-Canvas Explainer artifact and its 15 linked demos, in a README that sparks ideas.
- The Artifact tool's `read` action saved each artifact's raw HTML (they're third-party/public). Much easier than scraping the cross-origin iframe via CDP.
- Each file starts with ~43 KB of claude.ai frame runtime, plus base64 fonts and thumbnails. `perl -0pe 's/^.*frame-runtime -->//s'` and stripping `base64,...` brought the 16 files from 4 MB to 3.4 MB.
- The code is very heavily commented in plain English (e.g. "Silk does not stretch: pull back every point that got further from its clip than the cloth allows."). `tools/extract.py` pulls out block and line comments. `tools/dedupe.py` drops lines shared by 3+ files (the shared `unsupported.js` and the `hic.js` adapter). That came to about 300 KB of readable notes, and most of the catalog comes from these.
- Time Machine is minified, so the comments say less. The era list came from the bundle: print 1910, film 1948, phosphor 1982, vhs 1986, lcd 1989, eink 2007, oled 2026.
- Screenshots: `tools/shot.py` opens background tabs via CDP `Target.createTarget {background: true}`, sets a 1280x760 viewport, waits 14s, captures a JPEG and closes the tab. So the user's focus wasn't stolen. Running 4-5 tabs in parallel was fine.
- The Explainer needs scrolling inside the artifact iframe. CDP `Input.dispatchMouseEvent` type `mouseWheel` on the top-level page target reaches the iframe. `tools/scroll.py` wheels 800px per step and screenshots each step. My first run with 40 steps of 500px stalled after 4 shots (unclear why, maybe GPU load from the earlier tabs). Re-running with 26 steps worked. The last section (Paper) needs about 12 steps; the rest is just the pinned last scene.
- API generations (from the comments in `unsupported.js` and `hic.js`):
  - current (Chrome 157+): `<canvas content="drawable">`, `texElementSubImage2D`, `updateElementGeometry`
  - earlier (Chromium < 157 with the flag, Claude desktop app): `<canvas layoutsubtree>`, `texElementImage2D`, hit testing via CSS transform
  - Chrome 154-156 have `updateElementGeometry` but ignore it for hit testing, so every demo probes it.
  - The feature probe also lists `drawElementImage`/`drawElement` (2D) and `drawElementImageToTexture`/`copyElementImageToTexture` (WebGPU). I first assumed `copyElementImageToTexture` was Shatter's mipmap copy. Wrong: it's a WebGPU name in the probe. Fixed in the README.
- A side note from the user: make sure the README names the current API, not the older names that most explainer code calls. Done, with a table.
- Recurring engineering patterns across all demos: data colours (4 masks in one picture), unproject + local affine (Jacobian) fit for hit testing, hit-test cache invalidation by touching DOM outside the canvas, click "safety net", bake-then-relight, adaptive resolution, seeded randomness, synthesized Web Audio, self-demonstration until the visitor touches anything, a "plain page" toggle.
