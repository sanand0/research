#!/usr/bin/env python3
"""
Generate Gemini embeddings for audio clips and create UMAP visualization.
"""

import os
import csv
import json
import subprocess
from pathlib import Path
import numpy as np
import umap
import matplotlib.pyplot as plt

BASE_DIR = Path("/home/vscode/code/research/tamil-music-history")
SONGS_CSV = BASE_DIR / "songs.csv"
CLIPS_DIR = BASE_DIR / "clips_50s"
EMBEDDINGS_FILE = BASE_DIR / ".clip_embeddings.json"
UMAP_OUTPUT = BASE_DIR / "umap_tamil_songs.png"

# Gemini API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def get_audio_features(audio_path):
    """
    Extract audio features using ffmpeg and audio analysis.
    Returns a feature vector suitable for embedding/UMAP.
    """
    features = {}

    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(audio_path)],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        features['duration'] = float(data['format']['duration'])
    except:
        features['duration'] = 0

    # Extract audio for analysis - use low quality for speed
    temp_wav = audio_path.with_suffix('.wav')
    try:
        # Convert to WAV for analysis
        subprocess.run([
            "ffmpeg", "-y", "-i", str(audio_path),
            "-ac", "1", "-ar", "16000", "-t", "50",
            "-acodec", "pcm_s16le", str(temp_wav)
        ], capture_output=True, timeout=60)

        if temp_wav.exists():
            # Get basic stats using ffprobe
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "stream=sample_rate,channels,bit_rate",
                "-of", "json", str(temp_wav)
            ], capture_output=True, text=True)
            data = json.loads(result.stdout)
            if 'streams' in data and len(data['streams']) > 0:
                s = data['streams'][0]
                features['sample_rate'] = int(s.get('sample_rate', 16000))
                features['channels'] = int(s.get('channels', 1))
                features['bit_rate'] = int(s.get('bit_rate', 0))
            else:
                features['sample_rate'] = 16000
                features['channels'] = 1
                features['bit_rate'] = 0

            # Use ffprobe to get loudness info
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "stream_tags=loudness,rms",
                "-of", "json", str(temp_wav)
            ], capture_output=True, text=True)
            try:
                data = json.loads(result.stdout)
                if 'streams' in data and len(data['streams']) > 0:
                    tags = data['streams'][0].get('tags', {})
                    features['loudness'] = float(tags.get('loudness', -20))
                    features['rms'] = float(tags.get('rms', -30))
                else:
                    features['loudness'] = -20
                    features['rms'] = -30
            except:
                features['loudness'] = -20
                features['rms'] = -30

            # Get file size as proxy for audio complexity
            features['file_size'] = temp_wav.stat().st_size

            # Clean up temp file
            temp_wav.unlink()
        else:
            features['sample_rate'] = 16000
            features['channels'] = 1
            features['bit_rate'] = 0
            features['loudness'] = -20
            features['rms'] = -30
            features['file_size'] = 0

    except Exception as e:
        print(f"    Audio analysis error: {e}")
        features['sample_rate'] = 16000
        features['channels'] = 1
        features['bit_rate'] = 0
        features['loudness'] = -20
        features['rms'] = -30
        features['file_size'] = 0

    return features


def generate_embedding_with_gemini(audio_path, title, year):
    """
    Generate embedding vector using Gemini API.
    Falls back to audio features if no API key.
    """
    if GEMINI_API_KEY:
        # Use Gemini API for actual embeddings
        try:
            import urllib.request
            import urllib.parse

            # Read audio file and encode as base64
            with open(audio_path, 'rb') as f:
                audio_data = f.read()

            # For now, use audio features as proxy for embedding
            # Gemini multimodal can analyze audio but embedding API is limited
            prompt = f"""Analyze this Tamil film song clip "{title}" ({year}).
            Provide a feature vector as JSON with these numeric scores 0-1:
            - era_score: musical modernity (0=1950s classic, 1=2020s modern)
            - tempo_score: perceived tempo/speed (0=slow, 1=fast)
            - orchestration_score: instrumental complexity (0=minimal, 1=rich)
            - vocal_style_score: traditional to modern vocal approach
            - mood_score: emotional intensity (0=mellow, 1=intense)
            Return ONLY valid JSON."""

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

            # Create multipart request with audio
            import base64
            audio_b64 = base64.b64encode(audio_data).decode()

            data = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {
                            "mime_type": "audio/mp3",
                            "data": audio_b64
                        }}
                    ]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())

            text = result['candidates'][0]['content']['parts'][0]['text']
            embedding = json.loads(text)
            return [embedding['era_score'], embedding['tempo_score'],
                    embedding['orchestration_score'], embedding['vocal_style_score'],
                    embedding['mood_score']]

        except Exception as e:
            print(f"    Gemini API error: {e}, falling back to audio features")
            return None
    return None


def main():
    print("Tamil Song UMAP Generator")
    print("=" * 60)

    # Load songs metadata
    songs = {}
    with open(SONGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('youtube_id'):
                songs[row['youtube_id']] = row

    # Find all clips
    clips = list(CLIPS_DIR.glob("*_clip.mp3"))
    print(f"Found {len(clips)} clips")

    # Load existing embeddings
    embeddings = {}
    if EMBEDDINGS_FILE.exists():
        with open(EMBEDDINGS_FILE, 'r') as f:
            embeddings = json.load(f)

    feature_vectors = []
    labels = []
    years = []
    composers = []
    singers = []
    song_titles = []
    clip_ids = []

    for clip_path in clips:
        clip_id = clip_path.stem.replace('_clip', '')

        # Get song metadata
        song = songs.get(clip_id, {})
        year = song.get('year', 'unknown')
        composer = song.get('composer', 'unknown')
        singer = song.get('singer', 'unknown')
        title = song.get('song_title', clip_id)

        # Check if we have embedding from Gemini
        if clip_id in embeddings:
            vec = embeddings[clip_id]
        else:
            # Generate embedding using Gemini or audio features
            print(f"Processing: {title[:40]}...")

            # Try Gemini first
            gemini_vec = generate_embedding_with_gemini(clip_path, title, year)

            if gemini_vec:
                vec = gemini_vec
                embeddings[clip_id] = vec
            else:
                # Fall back to audio features
                features = get_audio_features(clip_path)
                # Create feature vector from audio analysis
                vec = [
                    features.get('loudness', -20) / -60,  # Normalize to 0-1
                    features.get('duration', 180) / 300,  # Normalize duration
                    features.get('file_size', 1000000) / 2000000,  # Normalize size
                    features.get('bit_rate', 128000) / 320000,  # Normalize bitrate
                    features.get('rms', -30) / -60,  # Normalize RMS
                ]
                embeddings[clip_id] = vec

            # Save progress
            with open(EMBEDDINGS_FILE, 'w') as f:
                json.dump(embeddings, f)

        feature_vectors.append(vec)
        years.append(int(year) if year.isdigit() else 2000)
        composers.append(composer)
        singers.append(singer)
        song_titles.append(title)
        clip_ids.append(clip_id)

    print(f"\nGenerated {len(feature_vectors)} feature vectors")

    # Convert to numpy array
    X = np.array(feature_vectors)

    # Apply UMAP
    print("Running UMAP dimensionality reduction...")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='euclidean', random_state=42)
    embedding = reducer.fit_transform(X)

    # Create visualization
    print("Creating visualization...")

    # Color by decade
    decades = [(y // 10) * 10 for y in years]
    decade_colors = {
        1950: '#1a1a2e', 1960: '#16213e', 1970: '#0f3460', 1980: '#533483',
        1990: '#e94560', 2000: '#ff6b35', 2010: '#f7d794', 2020: '#78e08f'
    }
    colors = [decade_colors.get(d, '#888888') for d in decades]

    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot all points
    scatter = ax.scatter(
        embedding[:, 0], embedding[:, 1],
        c=colors, alpha=0.6, s=30
    )

    # Add legend for decades
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w',
                   markerfacecolor=decade_colors[d], label=f"{d}s", markersize=8)
        for d in sorted(set(decades))
    ]
    ax.legend(handles=legend_elements, title="Decade", loc='best')

    ax.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax.set_title('Tamil Film Songs (1950-2026)\nAudio Embedding UMAP', fontsize=14)

    plt.tight_layout()
    plt.savefig(UMAP_OUTPUT, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {UMAP_OUTPUT}")

    # Also save embedding data for interactive use
    output_data = {
        'embeddings': embedding.tolist(),
        'metadata': [
            {'id': clip_ids[i], 'title': song_titles[i], 'year': years[i],
             'composer': composers[i], 'singer': singers[i]}
            for i in range(len(clip_ids))
        ]
    }

    with open(BASE_DIR / "umap_data.json", 'w') as f:
        json.dump(output_data, f)
    print(f"Saved: {BASE_DIR / 'umap_data.json'}")

    print("\nDone!")


if __name__ == "__main__":
    main()