#!/usr/bin/env python3
"""
Direct UV cache benchmark - measures cache performance without Docker.
Tests different cache strategies by manipulating cache directories and measuring performance.
"""

import subprocess
import time
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple


def get_dir_size(path: str) -> int:
    """Get total size of directory in bytes."""
    if not os.path.exists(path):
        return 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"


def run_uv_install(venv_path: str, cache_path: str, requirements: str) -> Tuple[float, str]:
    """
    Run uv pip install and return elapsed time and output.
    """
    env = os.environ.copy()
    env['UV_CACHE_DIR'] = cache_path
    env['VIRTUAL_ENV'] = venv_path

    start = time.time()

    cmd = [
        'uv', 'pip', 'install',
        '-r', requirements,
        '--python', f'{venv_path}/bin/python'
    ]

    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True
    )

    elapsed = time.time() - start
    output = result.stdout + result.stderr

    return elapsed, output


def create_venv(venv_path: str):
    """Create a virtual environment."""
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)

    subprocess.run(
        ['python3', '-m', 'venv', venv_path],
        check=True,
        capture_output=True
    )


def benchmark_strategy(
    strategy_name: str,
    cache_dir: str,
    clear_cache: bool,
    run_num: int,
    requirements_file: str
) -> Dict:
    """
    Benchmark a single cache strategy.

    Args:
        strategy_name: Name of the strategy being tested
        cache_dir: Path to cache directory
        clear_cache: Whether to clear cache before run
        run_num: Run number (1 for cold, 2+ for warm)
        requirements_file: Path to requirements file
    """
    print(f"\n{'='*70}")
    print(f"Strategy: {strategy_name} - Run {run_num} ({'COLD' if clear_cache else 'WARM'} cache)")
    print(f"{'='*70}")

    # Setup cache directory
    if clear_cache and os.path.exists(cache_dir):
        print(f"Clearing cache at {cache_dir}...")
        shutil.rmtree(cache_dir)

    os.makedirs(cache_dir, exist_ok=True)

    # Get initial cache size
    cache_size_before = get_dir_size(cache_dir)

    # Create a fresh venv for this test
    venv_path = f'./venv-{strategy_name}-{run_num}'
    print(f"Creating virtual environment at {venv_path}...")
    create_venv(venv_path)

    # Run installation
    print(f"Running uv pip install...")
    print(f"Cache directory: {cache_dir}")

    install_time, output = run_uv_install(venv_path, cache_dir, requirements_file)

    # Get final cache size
    cache_size_after = get_dir_size(cache_dir)
    cache_size_delta = cache_size_after - cache_size_before

    # Parse output for download info
    downloads_count = output.count('Downloading')
    cached_count = output.count('Using cached') + output.count('cached')

    result = {
        'strategy': strategy_name,
        'run': run_num,
        'cache_type': 'cold' if clear_cache else 'warm',
        'install_time_seconds': round(install_time, 3),
        'cache_size_before_bytes': cache_size_before,
        'cache_size_after_bytes': cache_size_after,
        'cache_size_delta_bytes': cache_size_delta,
        'cache_size_before_mb': round(cache_size_before / (1024*1024), 2),
        'cache_size_after_mb': round(cache_size_after / (1024*1024), 2),
        'cache_size_delta_mb': round(cache_size_delta / (1024*1024), 2),
        'downloads_detected': downloads_count,
        'cached_packages_detected': cached_count,
    }

    # Cleanup venv
    shutil.rmtree(venv_path)

    print(f"✓ Install time: {install_time:.2f}s")
    print(f"✓ Cache size: {format_bytes(cache_size_after)} (Δ {format_bytes(cache_size_delta)})")
    print(f"✓ Downloads: {downloads_count}, Cached: {cached_count}")

    return result


def main():
    """Run all benchmarks."""
    print("="*70)
    print("UV CACHE MOUNT STRATEGY BENCHMARK")
    print("="*70)
    print()

    # Ensure we're in the right directory
    os.chdir('/home/user/research/uv-cache-mount-benchmark')

    # Create requirements file
    requirements_file = 'requirements.txt'
    with open(requirements_file, 'w') as f:
        f.write("""pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
fastapi>=0.100.0
scikit-learn>=1.3.0
pillow>=10.0.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
""")

    results = []

    # Strategy 1: No cache (always clear)
    # This simulates Docker builds without cache mounts
    print("\n" + "="*70)
    print("STRATEGY 1: No Cache (Baseline)")
    print("Simulates: Docker build without cache mount")
    print("="*70)

    for run in [1, 2]:
        result = benchmark_strategy(
            strategy_name='no-cache',
            cache_dir='./cache-nocache',
            clear_cache=True,  # Always clear
            run_num=run,
            requirements_file=requirements_file
        )
        results.append(result)
        time.sleep(1)  # Small delay between runs

    # Strategy 2: Persistent local cache
    # This simulates Docker BuildKit cache mount
    print("\n" + "="*70)
    print("STRATEGY 2: Persistent Cache (BuildKit-style)")
    print("Simulates: Docker BuildKit --mount=type=cache")
    print("="*70)

    for run in [1, 2]:
        result = benchmark_strategy(
            strategy_name='persistent-cache',
            cache_dir='./cache-persistent',
            clear_cache=(run == 1),  # Clear only on first run
            run_num=run,
            requirements_file=requirements_file
        )
        results.append(result)
        time.sleep(1)

    # Strategy 3: Shared cache directory
    # This simulates bind mount or volume mount
    print("\n" + "="*70)
    print("STRATEGY 3: Shared Cache Directory")
    print("Simulates: Docker volume mount or bind mount")
    print("="*70)

    for run in [1, 2]:
        result = benchmark_strategy(
            strategy_name='shared-cache',
            cache_dir='./cache-shared',
            clear_cache=(run == 1),
            run_num=run,
            requirements_file=requirements_file
        )
        results.append(result)
        time.sleep(1)

    # Save results
    results_file = 'benchmark_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70)

    strategies = {}
    for result in results:
        strategy = result['strategy']
        if strategy not in strategies:
            strategies[strategy] = []
        strategies[strategy].append(result)

    for strategy, runs in strategies.items():
        print(f"\n{strategy.upper()}:")
        cold_run = [r for r in runs if r['cache_type'] == 'cold'][0]
        warm_runs = [r for r in runs if r['cache_type'] == 'warm']

        print(f"  Cold cache: {cold_run['install_time_seconds']:.2f}s")
        if warm_runs:
            warm_run = warm_runs[0]
            print(f"  Warm cache: {warm_run['install_time_seconds']:.2f}s")

            time_saved = cold_run['install_time_seconds'] - warm_run['install_time_seconds']
            pct_saved = (time_saved / cold_run['install_time_seconds']) * 100 if cold_run['install_time_seconds'] > 0 else 0

            print(f"  Time saved: {time_saved:.2f}s ({pct_saved:.1f}%)")
            print(f"  Cache size: {format_bytes(warm_run['cache_size_after_bytes'])}")

    print(f"\n{'='*70}")
    print(f"Results saved to: {results_file}")
    print(f"{'='*70}")

    # Cleanup
    print("\nCleaning up temporary files...")
    for item in Path('.').glob('cache-*'):
        if item.is_dir():
            shutil.rmtree(item)
    for item in Path('.').glob('venv-*'):
        if item.is_dir():
            shutil.rmtree(item)
    if os.path.exists(requirements_file):
        os.remove(requirements_file)

    print("✓ Cleanup complete")


if __name__ == '__main__':
    main()
