# new-workflows-2: creative CLI workflows

## Goal
Explore underused capabilities of installed CLI tools (FFmpeg 6.1, SoX 14.4, ImageMagick 6.9, Poppler 24.02, Pandoc 3.1, Graphviz 2.43) and sketch a large backlog of novel workflows.

## What I did
- Installed multimedia/document stacks (`ffmpeg`, `sox`, `imagemagick`, `poppler-utils`, `pandoc`, `graphviz`) to inspect filters and outputs.
- Verified key features: FFmpeg visualization filters (`showcqt`, `showwavespic`, `showspectrumpic`, `avectorscope`, `aphasemeter`, `signature`, `displace`, `remap`, `chromashift`, `datascope`), SoX effects (`spectrogram`, `synth`, `stat`, `stretch`, `vad`, etc.), Pandoc outputs (`ipynb`, `pptx`, `revealjs`, `slidy`, `icml`), Poppler tools (`pdftoppm`, `pdftocairo`), and Graphviz availability (`dot -V`).
- Captured detailed ideation in [`ideas.md`](ideas.md) (40 ideas) and worklog in [`notes.md`](notes.md).

## Quick takeaways
- FFmpeg’s visualization filters plus `displace`/`remap` make it a no-code motion-graphics engine driven directly by audio or metadata.
- SoX can synthesize control signals and grain layers that become displacement maps or modulation tracks for FFmpeg visuals.
- Poppler + Pandoc turns PDFs/Markdown into multi-format assets (SVG, PNG, PPTX, Reveal.js) that can be animated with FFmpeg.
- Graphviz diagrams and ffmpeg `signature`/`drawgraph` filters enable data-driven overlays, live pipeline explainers, and fingerprint-based editing.

## Next steps
Pick items from `ideas.md` to implement; start with low-friction wins like “self-animating album art” (Idea #1) or “tempo-mapped slideshows” (Idea #27) that only need FFmpeg/ImageMagick.
