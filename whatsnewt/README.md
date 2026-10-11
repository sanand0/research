# whatsnewt: The complete expedition

Source: https://chatgpt.com/share/6acb9544-0860-83ec-8b63-366fe643342c <!-- https://chatgpt.com/c/6acb87ee-4e28-83ec-886c-8f4115237c14 -->

An offline-capable, static HTML walkthrough of Barry Warsaw's [whatsnewt](https://gitlab.com/flufl/whatsnewt), the Python 3.15 text adventure. [Open index.html](index.html) directly — no server, installation, Python runtime or web connection required. Optional Google Fonts improve the typography when online.

The guide uses **the upstream game itself as the answer key**: `extract.py` imports its puzzles, room model and canonical `tests/solutions.py` answers, walks the route in `tests/test_playthrough.py`, runs **all 18 puzzle verifiers under Python 3.15**, and asserts a complete perfect run of 375 points before generating `game.js`.

## How to explore

- **Follow the route:** start at the Startup Foyer, choose **Next encounter** to trace every detour and the Release Gate, or use **Previous** and arrow keys.
- **Jump:** click a room on the map or the chapters list; type part of a title/feature in the search bar (`/`).
- **Learn:** read each original puzzle briefing and starter; unfold the original hints, then reveal the **verified reference solution**. Copy answers to paste in the real TUI.
- **Play:** try `look`, `examine quill`, `take quill`, `inventory`, `hint`, `solve`, `score`, `map`, `secrets`, compass directions, the hidden words or `jump vault` in the simulated terminal. This is **not** a Python interpreter: code must be submitted in the original TUI.
- **Discover:** the secret stage lists all 11 hidden curiosities and lets you speak each one. The `zen` command selects randomly among **19** Zen of Python lines (six have custom 3.15 annotations), all included in the guide. The six contributor names unlock the real game's `jump ROOM` shortcut to **previously visited** rooms.
- **Finish:** the gate requires **6 sigils**, but maximum completion needs **18 puzzles, 8 floor souvenirs, 15 rooms and 11 curiosities**. Score `375/375`; the web UI tracks your *guide reading progress* separately from the upstream reference score.
- **Share:** the URL fragment includes the step, whether answers are shown, and light/dark theme. Your checklist persists locally in the browser.

The game's actual commands to start and resume remain:

```sh
uvx --python 3.15 whatsnewt
# In the game: solve, hint, inventory, map, score, secrets, jump ROOM
```

## Source & reproducibility

This walkthrough is an *independent companion*, not a fork or hosted copy of the game. Its original puzzle text, hints, solutions, room descriptions, item descriptions and Easter egg responses are derivative material from [whatsnewt (Apache-2.0)](https://gitlab.com/flufl/whatsnewt/-/blob/main/LICENSE), copyright 2026 Barry Warsaw. The visual design, interactive reader, navigation, and short storytelling passages are new.

Snapshot used: GitLab `flufl/whatsnewt` at **`7e2e8ce318`** (full SHA recorded in `game.js`). The upstream source was checked out under `/tmp/`, **not** committed to this research folder.

Regenerate from your own checkout:

```sh
git clone https://gitlab.com/flufl/whatsnewt.git /tmp/whatsnewt-upstream
uv run extract.py /tmp/whatsnewt-upstream
```

The extractor isolates `XDG_STATE_HOME` in a temporary directory so it never overwrites real game saves. It refuses to generate data if any reference puzzle stops passing or the expected score diverges.

## Quality checks

```sh
just check             # JS syntax + upstream counts/route integrity
just browser           # Playwright smoke tests against installed Edge/Chromium
```

Also test simply by opening `index.html` in a browser (no data fetching; remote fonts are optional). Browser tests cover desktop/mobile viewports, direct-link navigation, hints/solutions, all secrets and the unlocked jump command. The local browser checklist is not an actual game save.

See [notes.md](notes.md) for the research record.
