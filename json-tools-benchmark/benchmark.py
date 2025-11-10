#!/usr/bin/env python3
"""
Benchmark runner for JSON tools
"""
import subprocess
import time
import json
import sys
from pathlib import Path

def run_command(cmd, input_file=None, timeout=60):
    """Run a command and measure execution time"""
    start = time.perf_counter()
    try:
        if input_file:
            with open(input_file, 'r') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    shell=isinstance(cmd, str)
                )
        else:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                shell=isinstance(cmd, str)
            )
        elapsed = time.perf_counter() - start
        return {
            'success': result.returncode == 0,
            'time': elapsed,
            'output_size': len(result.stdout),
            'error': result.stderr.decode('utf-8') if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return {
            'success': False,
            'time': elapsed,
            'output_size': 0,
            'error': 'Timeout'
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            'success': False,
            'time': elapsed,
            'output_size': 0,
            'error': str(e)
        }

def benchmark_task(task_name, commands, data_file, runs=3):
    """Run a task multiple times and collect statistics"""
    print(f"\n  {task_name} on {data_file.name}:")
    results = {}

    for tool_name, cmd in commands.items():
        times = []
        success_count = 0

        for i in range(runs):
            result = run_command(cmd, data_file)
            if result['success']:
                times.append(result['time'])
                success_count += 1
            else:
                print(f"    {tool_name}: FAILED - {result['error']}")
                break

        if success_count == runs:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            print(f"    {tool_name}: {avg_time:.4f}s (min: {min_time:.4f}s, max: {max_time:.4f}s)")
            results[tool_name] = {
                'avg': avg_time,
                'min': min_time,
                'max': max_time,
                'times': times
            }
        else:
            results[tool_name] = None

    return results

def main():
    data_dir = Path('data')
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)

    # Test datasets
    datasets = {
        'small': data_dir / 'small.json',
        'medium': data_dir / 'medium.json',
        'large': data_dir / 'large.json',
        'nested': data_dir / 'nested.json'
    }

    all_results = {}

    # Task 1: Simple field selection
    print("\n=== Task 1: Simple field selection (.[].name) ===")
    task1_commands = {
        'jq': ['jq', '-r', '.[].name'],
        'dasel': ['/tmp/dasel', 'select', '-f', '-', '-p', 'json', '-m', '.[*].name'],
        'node-native': ['node', 'benchmarks/node_native.js', 'select_name'],
        'node-jsonpath': ['node', 'benchmarks/node_jsonpath.js', 'select_name'],
        'python-native': ['python3', 'benchmarks/python_native.py', 'select_name'],
        'python-jq': ['python3', 'benchmarks/python_jq.py', 'select_name'],
        'python-ujson': ['python3', 'benchmarks/python_ujson.py', 'select_name'],
    }

    all_results['task1_select'] = {}
    for ds_name, ds_file in datasets.items():
        all_results['task1_select'][ds_name] = benchmark_task(
            "Select name field", task1_commands, ds_file
        )

    # Task 2: Filter by condition
    print("\n=== Task 2: Filter by condition (select(.value > 500)) ===")
    task2_commands = {
        'jq': ['jq', '-c', '.[] | select(.value > 500)'],
        'node-native': ['node', 'benchmarks/node_native.js', 'filter_value'],
        'python-native': ['python3', 'benchmarks/python_native.py', 'filter_value'],
        'python-jq': ['python3', 'benchmarks/python_jq.py', 'filter_value'],
        'python-ujson': ['python3', 'benchmarks/python_ujson.py', 'filter_value'],
    }

    all_results['task2_filter'] = {}
    for ds_name, ds_file in datasets.items():
        all_results['task2_filter'][ds_name] = benchmark_task(
            "Filter value > 500", task2_commands, ds_file
        )

    # Task 3: Array mapping
    print("\n=== Task 3: Array mapping (map(.value * 2)) ===")
    task3_commands = {
        'jq': ['jq', '[.[] | .value * 2]'],
        'node-native': ['node', 'benchmarks/node_native.js', 'map_value'],
        'python-native': ['python3', 'benchmarks/python_native.py', 'map_value'],
        'python-jq': ['python3', 'benchmarks/python_jq.py', 'map_value'],
        'python-ujson': ['python3', 'benchmarks/python_ujson.py', 'map_value'],
    }

    all_results['task3_map'] = {}
    for ds_name, ds_file in datasets.items():
        all_results['task3_map'][ds_name] = benchmark_task(
            "Map values * 2", task3_commands, ds_file
        )

    # Task 4: Aggregation
    print("\n=== Task 4: Aggregation (sum of values) ===")
    task4_commands = {
        'jq': ['jq', '[.[] | .value] | add'],
        'node-native': ['node', 'benchmarks/node_native.js', 'sum_values'],
        'python-native': ['python3', 'benchmarks/python_native.py', 'sum_values'],
        'python-jq': ['python3', 'benchmarks/python_jq.py', 'sum_values'],
        'python-ujson': ['python3', 'benchmarks/python_ujson.py', 'sum_values'],
    }

    all_results['task4_aggregate'] = {}
    for ds_name, ds_file in datasets.items():
        all_results['task4_aggregate'][ds_name] = benchmark_task(
            "Sum all values", task4_commands, ds_file
        )

    # Task 5: Deep nested access
    print("\n=== Task 5: Deep nested access ===")
    task5_commands = {
        'jq': ['jq', '-r', '.[].user.profile.location.city // empty'],
        'node-native': ['node', 'benchmarks/node_native.js', 'deep_nested'],
        'python-native': ['python3', 'benchmarks/python_native.py', 'deep_nested'],
        'python-jq': ['python3', 'benchmarks/python_jq.py', 'deep_nested'],
        'python-ujson': ['python3', 'benchmarks/python_ujson.py', 'deep_nested'],
    }

    all_results['task5_nested'] = {}
    # Only test on nested dataset
    all_results['task5_nested']['nested'] = benchmark_task(
        "Deep nested access", task5_commands, datasets['nested']
    )

    # Save results
    with open('results/benchmark_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n\nBenchmark complete! Results saved to results/benchmark_results.json")

if __name__ == '__main__':
    main()
