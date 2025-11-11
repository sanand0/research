#!/usr/bin/env python3
"""
Analyze benchmark results and generate summary statistics
"""
import json
from pathlib import Path

def analyze_results():
    with open('results/benchmark_results.json', 'r') as f:
        results = json.load(f)

    print("=" * 80)
    print("DETAILED PERFORMANCE ANALYSIS")
    print("=" * 80)

    # Collect all timings for each tool across all tasks
    tool_times = {}

    for task_name, task_data in results.items():
        print(f"\n{task_name.upper()}")
        print("-" * 80)

        for dataset, tools in task_data.items():
            if tools is None:
                continue

            print(f"\n  Dataset: {dataset}")

            # Sort by average time
            sorted_tools = sorted(
                [(tool, data) for tool, data in tools.items() if data is not None],
                key=lambda x: x[1]['avg']
            )

            if sorted_tools:
                fastest_time = sorted_tools[0][1]['avg']

                for tool, data in sorted_tools:
                    slowdown = data['avg'] / fastest_time
                    bar_length = int(slowdown * 30)
                    bar = "█" * bar_length

                    fastest_mark = " ⚡" if slowdown == 1.0 else ""
                    print(f"    {tool:20s}: {data['avg']:7.4f}s  {bar}{fastest_mark}")

                    # Collect for overall analysis
                    if tool not in tool_times:
                        tool_times[tool] = []
                    tool_times[tool].append(data['avg'])

    # Overall performance summary
    print("\n" + "=" * 80)
    print("OVERALL PERFORMANCE SUMMARY")
    print("=" * 80)

    tool_averages = {}
    for tool, times in tool_times.items():
        avg = sum(times) / len(times)
        tool_averages[tool] = {
            'avg': avg,
            'count': len(times),
            'min': min(times),
            'max': max(times)
        }

    sorted_overall = sorted(tool_averages.items(), key=lambda x: x[1]['avg'])

    print("\nAverage time across all tasks and datasets:\n")
    fastest = sorted_overall[0][1]['avg']

    for rank, (tool, data) in enumerate(sorted_overall, 1):
        slowdown = data['avg'] / fastest
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "  ")
        print(f"{medal} {rank}. {tool:20s}: {data['avg']:7.4f}s  "
              f"(tests: {data['count']}, vs fastest: {slowdown:.1f}x)")

    # Performance matrix
    print("\n" + "=" * 80)
    print("PERFORMANCE MATRIX (times in seconds on large.json)")
    print("=" * 80)

    # Extract large dataset results
    tasks = ['task1_select', 'task2_filter', 'task3_map', 'task4_aggregate', 'task5_nested']
    tools_list = ['jq', 'node-native', 'python-native', 'python-ujson', 'python-jq']

    print("\n" + "Task".ljust(20) + " | " + " | ".join(t.ljust(15) for t in tools_list))
    print("-" * 120)

    for task in tasks:
        task_display = task.replace('task', '').replace('_', ' ').title()
        row = task_display.ljust(20) + " | "

        times = []
        for tool in tools_list:
            if task in results and 'large' in results[task]:
                tool_data = results[task]['large'].get(tool)
                if tool_data:
                    times.append(f"{tool_data['avg']:6.3f}s".ljust(15))
                else:
                    times.append("FAILED".ljust(15))
            else:
                times.append("N/A".ljust(15))

        row += " | ".join(times)
        print(row)

if __name__ == '__main__':
    analyze_results()
