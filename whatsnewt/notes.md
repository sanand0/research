# Lab notes: whatsnewt

2026-10-11
- Inspected Barry Warsaw's upstream whatsnewt at https://gitlab.com/flufl/whatsnewt (shallow checkout outside this repository).
- LocalMCP2 connection terminated on initial read-only attempt. Continued on the same graphene host through its connected Desktop Commander; no destructive retries.
- Upstream reference solutions live in tests/solutions.py and a complete canonical route in tests/test_playthrough.py. We should derive, not invent, puzzle solutions.
- The game has 15 rooms, 18 executable puzzles, 26 items, 6 required sigils, 8 floor souvenirs, 11 hidden curiosities, and 375 possible points. A six-sigil finish is NOT a perfect game.
- Hidden curiosity words: xyzzy, plugh, newt, spam, zen, plus six contributor names. The contributor set unlocks jump to *previously visited* rooms. The command secrets lists discoveries after the release manifest is signed.
- Design choice: separate a strictly sourced canonical walkthrough from the original illustrative narrative; preserve all clues, starters, answers, floor items, route detours and secrets, and give exact source links.
- Extract via a pinned source checkout and run each puzzle verifier under Python 3.15 with an isolated XDG_STATE_HOME, then embed as game.js: no runtime dependencies or CORS barriers on file://.

2026-10-11 — verification and design decisions
- PyPI uvx reports whatsnewt 3.15.3; the inspected upstream source also reports 3.15.3, commit 7e2e8ce318a64c86037e6cdaf2a8d6f6fae0cc00.
- The generator executed all 18 source answers, traversed every room, collected every item, exercised all 11 curiosities, unlocked jump and asserted 375/375; isolated autosave in temporary XDG_STATE_HOME.
- Upstream pytest: tests/test_playthrough.py and tests/test_secrets.py, 29 passed.
- Browser: Edge headless against local file://, 1440x900 and 390x844: 17 chapters, 15 map rooms, navigation, solution toggles, theme, feature search, all 11 secret cards, six-person jump unlock, Zen's 19 aphorisms, ending, zero JS exceptions and no horizontal overflow.
- Fixed defects found through execution: a malformed JS string; feature search ignored puzzle terms; the Great Loop's empty puzzle list appeared completed; an initial justfile heredoc ran Python lines in separate shells; corrected floor souvenirs from 9 to 8.
- Discoveries are kept distinct from the *upstream reference score*, because a static walkthrough does not execute puzzle submissions in the browser. Date-aware Hugo messages are sourced from the game's version at extraction time; Zen random choices are modeled explicitly with all 19 aphorisms.
- The repository carries only new explanatory/app files plus generated derived puzzle data; upstream clone, browser screenshots and dependency caches remain outside the project.
