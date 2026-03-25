#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "matplotlib>=3.9",
#   "numpy>=2.2",
#   "pandas>=2.2",
#   "pyarrow>=20.0",
#   "scikit-learn>=1.6",
#   "umap-learn>=0.5.7",
# ]
# ///
"""Analyze Tamil song audio embeddings and create UMAP visualization.

Loads embeddings from embeddings.parquet, merges with song metadata,
runs UMAP, and exports results.
"""

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import umap
from sklearn.preprocessing import normalize

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
INPUT_PATH = BASE_DIR / "embeddings.parquet"
OUT_DIR = Path(__file__).resolve().parent


def load_song_metadata() -> pd.DataFrame:
    """Load song metadata from songs.csv."""
    rows = []
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id'):
                rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    print("Loading embeddings...")
    embeddings = pd.read_parquet(INPUT_PATH)
    print(f"  {len(embeddings)} embeddings loaded")

    print("Loading song metadata...")
    metadata = load_song_metadata()
    print(f"  {len(metadata)} songs loaded")

    # Create clip_id to match embeddings
    metadata['clip_id'] = metadata['youtube_id'] + '_clip'

    # Drop duplicates - keep first occurrence
    metadata = metadata.drop_duplicates(subset='clip_id', keep='first')
    print(f"  {len(metadata)} unique clip_ids")

    # Merge embeddings with metadata
    frame = embeddings.merge(metadata, on='clip_id', how='left')
    print(f"  Merged {len(frame)} rows")

    # Extract embedding vectors
    vectors = np.vstack(frame["embedding"].to_numpy()).astype(np.float32)
    vectors = normalize(vectors)
    print(f"  Vector shape: {vectors.shape}")

    # Run UMAP
    print("Running UMAP dimensionality reduction...")
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.1,
        metric="cosine",
        random_state=42,
    )
    umap_coords = reducer.fit_transform(vectors)

    frame["umap_1"] = umap_coords[:, 0]
    frame["umap_2"] = umap_coords[:, 1]

    # Add decade column
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce")
    frame["decade"] = (frame["year"] // 10 * 10).fillna(2000).astype(int)

    # Save UMAP data as JSON for visualization
    umap_data = {
        "coords": umap_coords.tolist(),
        "metadata": [
            {
                "clip_id": str(row["clip_id"]),
                "song_title": str(row.get("song_title", "")),
                "movie": str(row.get("movie", "")),
                "year": int(row["year"]) if pd.notna(row["year"]) else 2000,
                "decade": int(row["decade"]),
                "composer": str(row.get("composer", "")),
                "singer": str(row.get("singer", "")),
                "youtube_id": str(row.get("youtube_id", "")),
            }
            for _, row in frame.iterrows()
        ],
        "summary": {
            "total_songs": int(len(frame)),
            "year_range": f"{int(frame['year'].min())}-{int(frame['year'].max())}",
            "decades": sorted(frame["decade"].unique().tolist()),
        }
    }

    output_json = BASE_DIR / "umap_data.json"
    with open(output_json, 'w') as f:
        json.dump(umap_data, f)
    print(f"\nSaved: {output_json}")

    # Save as CSV too for easy inspection
    output_csv = BASE_DIR / "umap_songs.csv"
    frame[["clip_id", "song_title", "movie", "year", "decade", "composer",
           "singer", "umap_1", "umap_2"]].to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")

    print(f"\nDone! {len(frame)} songs processed.")
    print(f"Decade distribution:\n{frame['decade'].value_counts().sort_index()}")


if __name__ == "__main__":
    main()