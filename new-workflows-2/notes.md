# Research notes

## Session start
- Set up workspace and plan to explore creative workflows using installed tools.

## Tool availability check
- `ffmpeg`, `sox`, `magick`, `convert`, `pdftoppm`, `pdftocairo` not in PATH by default (via `which`).
- `rg`, `jq`, and `uv` available.

- Ran `apt-get update` to enable package installs for tool inspection.

## Installed tools for research
- Installed multimedia and document tools via `apt-get install -y ffmpeg sox imagemagick graphviz poppler-utils pandoc` (pulled dependencies including Netpbm, pocketsphinx, VA drivers).
- Confirmed tool paths: `ffmpeg`, `sox`, `convert` (ImageMagick), `pdftoppm`, `pdftocairo`, `pandoc` now available.
- Verified ffmpeg filter availability (6.1.1 build includes chromashift, datascope, displace, remap, signature, drawgraph/adrawgraph, aphasemeter, avectorscope, showcqt, showspectrumpic, showvolume, showwavespic). Command: `ffmpeg -filters | rg 'showcqt|showspectrumpic|avectorscope|aphasemeter|showvolume|adrawgraph|showwavespic|signature|displace|remap|chromashift'`.
- `sox --help` shows effects: e.g., `spectrogram`, `synth`, `stat`, `stretch`, `vad`, `ladspa`, etc. (`sox --help | tail -n 40`).
- `pandoc --list-output-formats` confirms wide outputs (asciidoc, beamer, docx, pptx, revealjs, ipynb, etc.) for multi-target conversions.
- Confirmed pandoc targets include `ipynb`, `pptx`, `revealjs`, `slidy`, `icml` via `pandoc --list-output-formats | rg 'pptx|revealjs|ipynb|slidy|icml'`.
- `dot -V` shows Graphviz 2.43.0 available for generating graphs.
- Poppler utilities available (e.g., `pdftoppm 24.02.0`).
- Inspected `ffmpeg` filter options for `signature` (MPEG-7 fingerprint) via `ffmpeg -h filter=signature`.
- `ffmpeg -h filter=showcqt` confirms configurable CQT spectrum video options (size, fps, bar graph heights/volumes, sonogram controls).
