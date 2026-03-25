# Tamil Film Music UMAP Visualization

Interactive visualization of Tamil film songs mapped by audio similarity using UMAP dimensionality reduction on Gemini audio embeddings.

**View the visualization:** serve this directory with any HTTP server and open `index.html`.

```bash
cd /home/vscode/code/research/tamil-music-history
python3 -m http.server 8080
# Open http://localhost:8080/
```

## Features

- **Color by:** Composer, Singer, or Decade
- **Filter by:** Composer, Singer, Lyricist
- **Year range slider:** dual-thumb slider to filter by year range (1950–2026)
- **Brush selection:** click-drag on scatterplot to select songs
- **Song popup:** sortable table with movie, song title, composer, singer, lyricist, year, duration — clicking opens the YouTube video

## Data Pipeline

```
songs.csv  →  download audio  →  clips_50s/  →  Gemini embeddings  →  UMAP  →  index.html
```

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fetch_all.py` | Search YouTube for Tamil songs and build the catalog (`songs.csv`) |
| `scripts/download_songs.py` | Download audio from YouTube IDs in `songs.csv` |
| `scripts/extract_clips.py` | Extract 50-second clips from downloaded audio |
| `scripts/embed_audio.py` | Generate Gemini multimodal embeddings for clips (resumable via DuckDB) |
| `scripts/analyze_audio.py` | Run UMAP dimensionality reduction and produce `umap_data.json` |

### Run the full pipeline

```bash
# 1. Fetch songs and build catalog
uv run python3 scripts/fetch_all.py

# 2. Download audio files
uv run python3 scripts/download_songs.py

# 3. Extract 50s clips
uv run python3 scripts/extract_clips.py

# 4. Generate embeddings (resumable — interrupt safely, re-run to continue)
uv run python3 scripts/embed_audio.py 2>&1 | tail -f embeddings.log

# 5. Run UMAP
uv run --with pyarrow --with pandas --with numpy --with scikit-learn --with umap-learn \
  python3 scripts/analyze_audio.py
```

## File Guide

| File | Description |
|------|-------------|
| `songs.csv` | Master catalog — YouTube ID, title, movie, composer, singer, lyricist, year, duration |
| `songs/` | Raw downloaded audio (`.mp4`/`.m4a`) |
| `clips_50s/` | 50-second clips extracted at 30s offset for embedding |
| `embeddings.parquet` | Gemini embedding vectors (768-dim) in Parquet format |
| `embeddings.duckdb` | DuckDB with WAL checkpointing — tracks processed clips for resumability |
| `umap_data.json` | UMAP 2D coordinates + full metadata (song title, movie, composer, singer, lyricist, year, decade, YouTube ID, duration) |
| `umap_songs.csv` | UMAP coordinates merged with song metadata as CSV |
| `index.html` | Interactive visualization (open in browser) |

## Key Statistics

- **448 songs** with Gemini audio embeddings
- **9 composers:** A.G.R., A.R. Rahman, Anirudh, Ilaiyaraaja, K.V. Mahadevan, M.S. Viswanathan, S.V. Venkatraman, Vidyasagar, Viswanathan Ramamoorthy
- **10+ singers** (primary): A.R. Rahman, Anirudh, Jey, K.S. Chithra, Mohan, P. Susheela, S. Janaki, S.P. Balasubrahmanyam, T.M. Soundararajan, T.T. Manickam (songs may list multiple singers, separated by `;`)
- **Year range:** 1950–2026
- **Embedding:** Gemini multimodal (`gemini-embedding-2-preview`), 768 dimensions
- **UMAP:** `n_neighbors=15`, `min_dist=0.1`, `metric=cosine`

## Resuming Embedding Generation

The embedding script is fully resumable. It tracks processed clips in DuckDB by SHA-256 hash. To continue after interruption:

```bash
uv run python3 scripts/embed_audio.py 2>&1 | tail -f embeddings.log
```

To force re-embed a specific song, delete its row from DuckDB first:

```bash
duckdb embeddings.duckdb -c "DELETE FROM embeddings WHERE clip_id = 'YOUTUBE_ID_clip';"
```

## Adding More Songs

1. Add YouTube IDs to `songs.csv` (or run `scripts/fetch_all.py` to discover songs)
2. Standardize metadata in `songs.csv` (composer/singer/lyricist names)
3. Run steps 2–5 of the pipeline above
