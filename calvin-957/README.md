# Calvin & Hobbes: how Calvin got 957 (video project)

A 94-second, 1080×1350 (4:5) video for LinkedIn and Instagram. It replays a 33-move
Scrabble game that slides from honest play into Calvinball and ends with ZQFMGB
scoring exactly 957.

## Files
- `storyboard.json` - everything you'd want to edit: intro and outro text, act names,
  dialogue per move, timings, colours, output size, quality (`crf`, lower = bigger/sharper).
- `moves.json` - the game itself: every move's tiles, score, cheat level and each word
  formed with its dictionary grade (US = TWL06, UK = Collins/SOWPODS only, NO = neither).
- `render.py` - draws every frame with Pillow and pipes them to ffmpeg.
- `fonts/` - Rammetto One, Gochi Hand, Archivo Black, Atkinson Hyperlegible (SIL Open Font License).

## Render
    pip install pillow        # ffmpeg must be on your PATH
    python3 render.py                       # writes calvin-957.mp4 (about 2 minutes)
    python3 render.py --frames 12 58.5 88   # writes PNG stills at those seconds, for checking

## Common edits
- Speed: `timing.hold_by_act` (seconds each move stays on screen, per act) and
  `timing.dialogue_per_char`.
- Dialogue: `moves.<number>.say` is a list of `[speaker, line]`; an empty list means none.
- Square video: set `video.width` and `video.height` to 1080; the board stays centred,
  but you may want to shrink `BX/BY/PITCH` at the top of render.py.
- Credit line at the end: `outro.credit`.

Source: https://claude.ai/share/d89b2cb5-4a56-48ee-9f9c-3c8316dc8be9

<!-- https://claude.ai/chat/5c7f058a-1139-46cf-95e4-b8eb3be88c2f -->
