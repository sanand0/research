#!/usr/bin/env python3
"""
Test streaming capabilities of different JSON tools
"""
import subprocess
import time
import sys
from pathlib import Path

def test_streaming(tool_name, cmd, data_file):
    """Test if a tool produces streaming output"""
    print(f"\nTesting {tool_name}:")

    # Run command and capture output line by line
    start = time.perf_counter()
    first_output = None
    line_count = 0

    try:
        with open(data_file, 'r') as f:
            process = subprocess.Popen(
                cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )

            for line in process.stdout:
                if first_output is None:
                    first_output = time.perf_counter() - start
                line_count += 1
                if line_count >= 10:  # Just test first 10 lines
                    break

            process.terminate()
            process.wait(timeout=1)

        total_time = time.perf_counter() - start

        if first_output:
            print(f"  ✓ Streaming: YES")
            print(f"  Time to first output: {first_output:.4f}s")
            print(f"  Time for 10 lines: {total_time:.4f}s")
            return True
        else:
            print(f"  ✗ Streaming: NO (no output captured)")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    data_file = Path('data/large.json')

    print("=" * 60)
    print("STREAMING OUTPUT TEST")
    print("=" * 60)
    print(f"\nUsing dataset: {data_file} ({data_file.stat().st_size / 1024 / 1024:.1f} MB)")

    # Test different tools for streaming
    streaming_tests = {
        'jq': ['jq', '-r', '.[].name'],
        'node-native': ['node', 'benchmarks/node_native.js', 'select_name'],
        'python-native': ['python3', 'benchmarks/python_native.py', 'select_name'],
        'python-jq': ['python3', 'benchmarks/python_jq.py', 'select_name'],
    }

    results = {}
    for tool_name, cmd in streaming_tests.items():
        results[tool_name] = test_streaming(tool_name, cmd, data_file)

    print("\n" + "=" * 60)
    print("STREAMING SUMMARY")
    print("=" * 60)
    for tool_name, supports_streaming in results.items():
        status = "✓ Supports streaming" if supports_streaming else "✗ No streaming"
        print(f"{tool_name:20s}: {status}")

if __name__ == '__main__':
    main()
