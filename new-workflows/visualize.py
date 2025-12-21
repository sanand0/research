#!/usr/bin/env python3
"""
Multi-Format Data Visualization Pipeline
Demonstrates creative use of standard tools to visualize data in ASCII, SVG, and Audio
"""

import json
import math
import wave
import struct
import sys


def load_data(filename):
    """Load JSON data"""
    with open(filename, 'r') as f:
        return json.load(f)


def generate_ascii_visualization(data):
    """Generate beautiful ASCII terminal visualization with Unicode block characters"""
    print("\n" + "=" * 80)
    print(f"  {data['title']}")
    print("=" * 80 + "\n")

    values = [item['avg_response'] for item in data['data']]
    max_val = max(values)
    min_val = min(values)

    # Bar chart with gradient colors
    bar_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    for item in data['data']:
        month = item['month']
        value = item['avg_response']
        requests = item['requests']

        # Normalize to 0-50 range for display
        normalized = int((value - min_val) / (max_val - min_val) * 50) if max_val != min_val else 25

        # Create bar with Unicode blocks
        bar = '█' * normalized

        # Color coding based on performance (ANSI colors)
        if value < 140:
            color = '\033[92m'  # Green (good)
        elif value < 160:
            color = '\033[93m'  # Yellow (ok)
        else:
            color = '\033[91m'  # Red (slow)

        reset = '\033[0m'

        print(f"{month:>3} │ {color}{bar}{reset} {value}{data['unit']} ({requests:,} req)")

    # Statistics
    avg = sum(values) / len(values)
    print("\n" + "─" * 80)
    print(f"  Average: {avg:.1f}{data['unit']} | Min: {min_val}{data['unit']} | Max: {max_val}{data['unit']}")
    print("=" * 80 + "\n")

    # Sparkline
    print("  Trend: ", end="")
    for value in values:
        idx = int((value - min_val) / (max_val - min_val) * 7) if max_val != min_val else 3
        print(bar_chars[idx], end="")
    print(f" ({values[0]}→{values[-1]}{data['unit']})\n")


def generate_svg_visualization(data, output_file):
    """Generate SVG vector graphics visualization"""
    width = 800
    height = 400
    margin = 60

    values = [item['avg_response'] for item in data['data']]
    labels = [item['month'] for item in data['data']]

    max_val = max(values)
    min_val = min(values)

    # Calculate dimensions
    chart_width = width - 2 * margin
    chart_height = height - 2 * margin
    bar_width = chart_width / len(values)

    # Start SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#1e1e1e"/>

  <!-- Title -->
  <text x="{width/2}" y="30" font-family="Arial, sans-serif" font-size="20" fill="#ffffff" text-anchor="middle" font-weight="bold">
    {data['title']}
  </text>

  <!-- Grid lines -->
'''

    # Add horizontal grid lines
    for i in range(5):
        y = margin + (chart_height / 4) * i
        val = max_val - ((max_val - min_val) / 4) * i
        svg += f'  <line x1="{margin}" y1="{y}" x2="{width - margin}" y2="{y}" stroke="#444444" stroke-width="1"/>\n'
        svg += f'  <text x="{margin - 10}" y="{y + 5}" font-family="Arial, sans-serif" font-size="12" fill="#888888" text-anchor="end">{int(val)}</text>\n'

    svg += '\n  <!-- Bars -->\n'

    # Add bars
    for i, (value, label) in enumerate(zip(values, labels)):
        x = margin + i * bar_width + bar_width * 0.1
        bar_height_normalized = ((value - min_val) / (max_val - min_val)) if max_val != min_val else 0.5
        bar_height_px = bar_height_normalized * chart_height
        y = margin + chart_height - bar_height_px

        # Color based on value
        if value < 140:
            color = "#4ade80"  # Green
        elif value < 160:
            color = "#fbbf24"  # Yellow
        else:
            color = "#f87171"  # Red

        svg += f'  <rect x="{x}" y="{y}" width="{bar_width * 0.8}" height="{bar_height_px}" fill="{color}" opacity="0.9"/>\n'
        svg += f'  <text x="{x + bar_width * 0.4}" y="{y - 5}" font-family="Arial, sans-serif" font-size="11" fill="#ffffff" text-anchor="middle">{value}</text>\n'

    svg += '\n  <!-- Labels -->\n'

    # Add x-axis labels
    for i, label in enumerate(labels):
        x = margin + i * bar_width + bar_width / 2
        y = height - margin + 20
        svg += f'  <text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="12" fill="#888888" text-anchor="middle">{label}</text>\n'

    # Add axis labels
    svg += f'''
  <!-- Axis labels -->
  <text x="{width/2}" y="{height - 10}" font-family="Arial, sans-serif" font-size="14" fill="#888888" text-anchor="middle">Month</text>
  <text x="20" y="{height/2}" font-family="Arial, sans-serif" font-size="14" fill="#888888" text-anchor="middle" transform="rotate(-90, 20, {height/2})">Response Time ({data['unit']})</text>

</svg>'''

    with open(output_file, 'w') as f:
        f.write(svg)

    print(f"✓ SVG visualization saved to: {output_file}")


def generate_audio_sonification(data, output_file):
    """Generate audio sonification where pitch represents response time"""
    sample_rate = 44100
    duration_per_note = 0.4  # seconds per data point

    values = [item['avg_response'] for item in data['data']]
    max_val = max(values)
    min_val = min(values)

    # Map values to frequencies (200 Hz to 800 Hz)
    # Lower response time = lower pitch (better performance sounds lower)
    frequencies = []
    for value in values:
        # Normalize to 0-1
        normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        # Map to frequency range (inverted so higher values = higher pitch = worse performance)
        freq = 200 + normalized * 600
        frequencies.append(freq)

    # Generate audio
    frames = []
    for freq in frequencies:
        num_samples = int(sample_rate * duration_per_note)
        for i in range(num_samples):
            # Generate sine wave with envelope (fade in/out)
            t = i / sample_rate
            envelope = min(1.0, min(i / (sample_rate * 0.05), (num_samples - i) / (sample_rate * 0.05)))
            sample = math.sin(2 * math.pi * freq * t) * envelope
            # Convert to 16-bit integer
            frames.append(int(sample * 32767 * 0.5))

    # Write WAV file
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Pack frames as 16-bit signed integers
        packed_frames = struct.pack('h' * len(frames), *frames)
        wav_file.writeframes(packed_frames)

    print(f"✓ Audio sonification saved to: {output_file}")
    print(f"  (Lower pitch = faster response, Higher pitch = slower response)")


def generate_jq_visualization(input_file):
    """Show how to visualize with jq directly"""
    print("\n" + "─" * 80)
    print("  JQ One-Liner Visualization:")
    print("─" * 80)
    print(f'''
  Command:
    cat {input_file} | jq -r '.data[] | "\\(.month): " + ("█" * (.avg_response / 10 | floor))'

  Output:''')

    # Actually run it
    import subprocess
    result = subprocess.run(
        f"cat {input_file} | jq -r '.data[] | \"\\(.month): \" + (\"█\" * (.avg_response / 10 | floor))'",
        shell=True,
        capture_output=True,
        text=True
    )
    print("  " + result.stdout.replace("\n", "\n  "))


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <data.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "MULTI-FORMAT DATA VISUALIZATION PIPELINE" + " " * 22 + "║")
    print("║" + " " * 10 + "Showcasing Creative Uses of Standard Tools" + " " * 24 + "║")
    print("╚" + "═" * 78 + "╝")

    # Load data
    data = load_data(input_file)

    # 1. ASCII Terminal Visualization
    print("\n[1/4] Generating ASCII Terminal Visualization...")
    generate_ascii_visualization(data)

    # 2. SVG Vector Graphics
    print("\n[2/4] Generating SVG Vector Graphics...")
    svg_output = input_file.replace('.json', '.svg')
    generate_svg_visualization(data, svg_output)

    # 3. Audio Sonification
    print("\n[3/4] Generating Audio Sonification...")
    audio_output = input_file.replace('.json', '.wav')
    generate_audio_sonification(data, audio_output)

    # 4. Show jq alternative
    print("\n[4/4] Demonstrating jq Alternative...")
    generate_jq_visualization(input_file)

    print("\n" + "═" * 80)
    print("  ✓ Complete! Generated visualizations in 3 formats:")
    print(f"    • ASCII: Displayed above")
    print(f"    • SVG:   {svg_output}")
    print(f"    • Audio: {audio_output}")
    print("═" * 80 + "\n")

    # Show tool composition
    print("  Tools Used:")
    print("    • Python (orchestration, SVG generation, audio synthesis)")
    print("    • wave module (WAV file creation - no external dependencies)")
    print("    • jq (JSON processing and ASCII visualization)")
    print("    • Standard library only (json, math, struct)")
    print("")


if __name__ == '__main__':
    main()
