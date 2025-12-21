# Creative tool workflows (new-workflows-2)

## Strategy scaffolding
- **Audio-to-visual morphing (FFmpeg-only):** Lean on visualization filters (`showcqt`, `showwavespic`, `showspectrumpic`, `avectorscope`, `aphasemeter`) and post-process with filters like `displace`, `remap`, `chromashift`, `signature` to turn waveforms into motion graphics.
- **Audio preprocessing as control data (SoX + FFmpeg):** Use SoX effects (`synth`, `spectrogram`, `stretch`, `vad`, `stat`) to generate or clean control tracks, then feed them into FFmpeg visualization filters for procedural animation.
- **Image-to-video remixes (ImageMagick + FFmpeg):** Leverage `convert` for per-frame warps (e.g., `-distort`, `-hald-clut`, `-morphology` via `datascope` inputs) and stitch with FFmpeg for kinetic posters or morphing slideshows.
- **Document shape-shifting (Poppler + Pandoc + FFmpeg):** Decompose PDFs with `pdftoppm`/`pdftocairo`, restyle content via Pandoc (to `ipynb`, `pptx`, `revealjs`, `slidy`), and animate page-turn or slide builds with FFmpeg.
- **Graph-based automation (Graphviz + FFmpeg/SoX):** Generate dot graphs of pipelines, then render them into explainer overlays or interactive node-to-clip maps.
- **Fingerprinting & metadata play (FFmpeg signature + Pandoc/Graphviz):** Use FFmpeg’s `signature` and `adrawgraph/drawgraph` to fingerprint/plot media, then convert reports to diagrams or slide decks.

## Concrete idea backlog (long list)
1. **Self-animating album art:** Drive `showcqt` + `chromashift` + `paletteuse` to create aurora-style spectrogram canvases, then warp with `displace` maps derived from the cover image for music videos with zero manual keyframes.
2. **Phase lace tunnels:** Feed a SoX-generated drone (`sox -n -r 48k -b 16 drone.wav synth 12 sin 40-120`) into FFmpeg `aphasemeter` + `avectorscope` to render hypnotic polar ribbons; layer `remap` to make tunnels that respond to phase shifts.
3. **Audio topography maps:** Use `showspectrumpic` to emit single-frame heightmaps, run through ImageMagick `-shade`/`-emboss`, then animate camera pans in FFmpeg for moving “sound terrain” flyovers.
4. **Voiceprint kaleidoscope:** Capture mic input with `ffmpeg -f alsa -i default` (or wav) and apply `showwavespic` + `displace` driven by a SoX `spectrogram` PNG as the displacement map for live kaleidoscopes.
5. **Beat-synced text liquifier:** Convert lyrics to transparent PNGs, then `ffmpeg -filter_complex "[0:v][1:v]displace,chromashift"` where `0:v` is text and `1:v` is `showcqt` output, making letters melt on kick drums.
6. **Audio-driven comic panels:** Slice a PDF comic with `pdftoppm -png`, detect silence ranges with `ffmpeg -af silencedetect`, then interleave panels only when sound is present, creating rhythm-aware panel reveals.
7. **“Mix the mix” fingerprints:** Batch-run `ffmpeg -filter_complex "signature=detectmode=full"` on DJ sets to generate MPEG-7 hashes, cluster similar drops, and auto-build a sampler video of matching transitions.
8. **Glitch quilts from metadata:** Use `ffmpeg -filter_complex "datascope,remap"` to expose raw pixel bytes, convert a few frames to ImageMagick `-hald-clut` LUTs, and reapply as color-warp overlays across the timeline.
9. **Spectrogram flipbooks:** Generate frame-by-frame spectrograms via `ffmpeg showspectrumpic=s=1024x1024:color=intensity` and assemble with `ffmpeg -framerate 12 -pattern_type glob "*.png" -vf palettegen/paletteuse` for dithery flipbooks that still react to audio.
10. **Zoomable waveform mosaics:** Export multi-scale waveforms (`showwavespic` at several resolutions), tile them with ImageMagick `montage`, then add FFmpeg’s `zmq`/`sendcmd` to pan/zoom based on amplitude.
11. **Synthetic foley via SoX grains:** Chop noise bursts with SoX `trim` + `stat`, then chain `stretch` + `tempo` to make morphable grain libraries; feed amplitude envelopes into FFmpeg `adrawgraph` to produce motion cues.
12. **Speech-to-slide concordance:** Poppler + `pdftocairo -svg` to get page vectors, Pandoc to convert a transcript to `revealjs`, then FFmpeg to overlay page SVGs whenever pocketsphinx (lib is present) or external ASR timestamps hit a keyword.
13. **PDF-to-trailer generator:** `pdftoppm -png` for pages, use ImageMagick to punch out key phrases, then FFmpeg `zoompan` + `showwavespic` from a soundtrack to make a cinematic trailer of a whitepaper.
14. **Kinetic course builder:** Write Markdown once, Pandoc it to `pptx` and `revealjs`, record narration, then FFmpeg `concat` the slide deck (as PNG renders) with `showcqt` stingers between sections for automatically-styled learning modules.
15. **Document heatmaps:** Use Poppler’s `pdftocairo -svg` + `rg` counts to colorize frequency of terms via ImageMagick `-colorize` masks, output as video that fades between topics with FFmpeg `blend`.
16. **Sonified diagrams:** Generate Graphviz diagrams of workflows, render to PNG, then map node degrees to tones via SoX `synth` chords; mux with FFmpeg `adrawgraph` overlaying the node metrics as they play.
17. **Pipeline explainer reels:** Auto-produce a short video where each Graphviz edge animates in sync with narration beats (detected by `ffmpeg astats` / `silencedetect`), using `drawgraph` to render live counters.
18. **Realtime AV moodboard:** Launch FFmpeg with `-filter_complex "amovie=track.mp3,showcqt,split[v1][v2];[v1]chromashift;[v2]datascope"` and route to `sdl2` output for VJ-ing without NLEs.
19. **Audio-driven LUT painting:** Derive 3D LUTs from songs by sampling `showcqt` frames, converting to Hald CLUTs via ImageMagick, and applying them back onto music videos for per-track color identities.
20. **Pattern-aware timestretch:** Use SoX `stat -freq` to find dominant frequencies, then feed as arguments to FFmpeg `rubberband` filter (enabled in this build) for harmonic-preserving slowmos.
21. **Noiseprint masking:** Generate a SoX `noiseprof` from room tone, use it to denoise audio, then map the removed noise to a grayscale alpha mask and multiply it over video to visualize cleanliness over time.
22. **Datascope thumbnails:** Render `datascope` snapshots of each clip in a folder to create glitchy preview spritesheets for quick visual triage of assets.
23. **Color-in-color subtitles:** Render subtitles twice—once normally, once as `showwavespic`—and `blend=all_mode=multiply` them so the text texture pulses with voice energy.
24. **Adaptive bitrate artbook:** Convert a Markdown zine to `revealjs` with Pandoc, record a flip-through using `ffmpeg -f x11grab`, then re-encode segments at varying bitrates and stitch with `concat` to visibly teach compression artifacts as an artistic effect.
25. **SVG oscilloscope stickers:** Take `showwavespic` outputs, vectorize them via `potrace` (from netpbm flow), and place them onto device mockups with ImageMagick `-composite` for merch-ready assets.
26. **Spectral music lightfield:** Use multi-angle mics to capture stems, generate separate `showcqt` planes, then use FFmpeg `remap` to fold them into RGB channels, creating a parallax lightfield when rotated.
27. **Tempo-mapped slideshows:** Detect BPM with `ffmpeg astats`, set `zoompan` durations to beat intervals, and auto-align photo sequences so every downbeat introduces a new frame without manual editing.
28. **Graphviz-driven batch renders:** Store render graph in DOT, then script FFmpeg to read edge weights as filter strengths (e.g., heavier edges increase `chromashift`), creating data-driven visuals from pipeline metadata.
29. **CLI VJ sampler:** Pre-render short `showcqt`/`avectorscope` loops, then use `ffplay` with `-fs -loop 0` and hot-swapping playlists via `stdin` to perform live without a GUI.
30. **PDF marginalia over music:** Extract page margins with Poppler, overlay handwritten notes scanned separately, and animate highlight sweeps paced by `showvolume` output to sync reading emphasis with soundtrack.
31. **Auto-hyperlapse from speech gaps:** Use `ffmpeg -af silencedetect` to find quiet spans, accelerate video during silence and pause on speech, yielding a talk-focused hyperlapse without editing.
32. **Sox-driven binaural bubbles:** Generate HRTF-aware sweeps with SoX `synth` + `binaural` LADSPA plugins, then visualize path trajectories via FFmpeg `adrawgraph` and Graphviz node tracks.
33. **Contrastive clip matcher:** Compute `signature` hashes for b-roll, find nearest neighbors to an anchor clip, and auto-build split-screen comparisons using FFmpeg `xstack` + `signature` distance metrics.
34. **Audio QR steganography:** Encode short URLs as dual-tone signals with SoX `synth` (DTMF-style), hide them under music, then render an `adrawgraph` QR-like visualization as a hint overlay.
35. **Procedural album teasers:** For each track, auto-generate a 10s teaser combining `showcqt` burst, ImageMagick `-motion-blur` on cover art, and `ffmpeg` `afade`/`xfade` chains; stitch all tracks into a catalog reel.
36. **Term-frequency karaoke:** Convert docs to `ipynb`/`pptx` via Pandoc, compute term spikes with `rg`, and animate on-screen word clouds whose size follows `showvolume` of corresponding narration segments.
37. **Data-to-tone dashboards:** Use Graphviz to render metric graphs, map metric deltas to SoX `synth` sequences, and assemble daily AV status updates where the soundtrack encodes alert severity.
38. **Beat-aware OCR overlays:** Run `tesseract`-style OCR alternatives via ImageMagick preprocessing, then animate recognized words appearing on beats detected by `astats` peaks for rhythm-synced captions.
39. **Zero-G book previews:** Apply ImageMagick `-distort perspective` animated over time to PDF pages exported via `pdftoppm`, while FFmpeg `showcqt` drives the spin rate to match soundtrack energy.
40. **Datascope-driven crypto art:** Take raw video with `datascope` filter, convert frames to ASCII with `aalib` (via `aafire` if installed) or ImageMagick `-threshold` + `-monochrome`, mint as sequence NFTs (concept) with unique hash overlays from `signature` bits.

