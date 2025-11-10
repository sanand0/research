#!/usr/bin/env python3
"""
Evaluation script for DOM→Markdown converters
Analyzes objective metrics for each tool's output
"""
import re
import json
from pathlib import Path
from collections import defaultdict

TOOLS = ['turndown', 'node-html-markdown', 'html2text', 'markdownify', 'pandoc']

TEST_CASES = {
    '01-headings.md': {
        'name': 'Headings',
        'checks': {
            'h1_atx': r'^# ',
            'h2_atx': r'^## ',
            'h6_atx': r'^###### ',
        }
    },
    '02-links.md': {
        'name': 'Links',
        'checks': {
            'inline_link': r'\[.*?\]\(.*?\)',
            'link_preserved': r'\[simple link\]',
        }
    },
    '03-code.md': {
        'name': 'Code',
        'checks': {
            'inline_code': r'`[^`]+`',
            'fenced_code': r'```',
        }
    },
    '04-simple-table.md': {
        'name': 'Simple Table',
        'checks': {
            'table_pipe': r'\|',
            'table_header_sep': r'\|.*\-\-',
        }
    },
    '05-complex-table.md': {
        'name': 'Complex Table',
        'checks': {
            'table_pipe': r'\|',
            'preserves_checkmark': r'[✓✗]',
        }
    },
    '06-unordered-list.md': {
        'name': 'Unordered List',
        'checks': {
            'list_marker': r'^[\*\-\+] ',
        }
    },
    '07-ordered-list.md': {
        'name': 'Ordered List',
        'checks': {
            'numbered_list': r'^\d+\. ',
        }
    },
    '08-nested-lists.md': {
        'name': 'Nested Lists',
        'checks': {
            'nested_indent': r'^  ',
            'deeply_nested': r'^    ',
        }
    },
    '09-emphasis.md': {
        'name': 'Bold/Italic',
        'checks': {
            'bold': r'\*\*.*?\*\*',
            'italic': r'\*[^\*]+\*',
        }
    },
    '10-images.md': {
        'name': 'Images',
        'checks': {
            'image_syntax': r'!\[.*?\]\(.*?\)',
            'alt_text': r'!\[.*\]',
        }
    },
    '11-blockquotes.md': {
        'name': 'Blockquotes',
        'checks': {
            'blockquote': r'^> ',
            'nested_blockquote': r'^> > ',
        }
    },
    '12-mixed-formatting.md': {
        'name': 'Mixed Formatting',
        'checks': {
            'has_bold': r'\*\*.*?\*\*',
            'has_code': r'`.*?`',
            'has_link': r'\[.*?\]\(.*?\)',
        }
    },
    '14-definition-list.md': {
        'name': 'Definition List',
        'checks': {
            'preserves_terms': r'HTML|CSS|JavaScript',
        }
    },
    '15-horizontal-rules.md': {
        'name': 'Horizontal Rules',
        'checks': {
            'hr_marker': r'^[\*\-_]{3,}',
        }
    },
    '17-nested-structure.md': {
        'name': 'Nested Structure',
        'checks': {
            'h1': r'^# ',
            'h2': r'^## ',
            'h3': r'^### ',
            'fenced_code': r'```',
        }
    },
    '18-syntax-highlighting.md': {
        'name': 'Syntax Highlighting',
        'checks': {
            'fenced_python': r'```python',
            'fenced_javascript': r'```javascript',
            'fenced_sql': r'```sql',
        }
    },
    '19-multicolumn-table.md': {
        'name': 'Multi-column Table',
        'checks': {
            'table_pipe': r'\|',
            'preserves_dollar': r'\$',
        }
    },
    '20-real-world-docs.md': {
        'name': 'Real-world Docs',
        'checks': {
            'headings': r'^#+ ',
            'code_blocks': r'```',
            'tables': r'\|',
            'lists': r'^[\*\-\d]',
        }
    }
}

def count_pattern(content, pattern):
    """Count occurrences of a regex pattern"""
    return len(re.findall(pattern, content, re.MULTILINE))

def check_pattern(content, pattern):
    """Check if pattern exists in content"""
    return bool(re.search(pattern, content, re.MULTILINE))

def evaluate_tool(tool_name):
    """Evaluate a single tool's outputs"""
    output_dir = Path('outputs') / tool_name
    results = {}

    for test_file, test_info in TEST_CASES.items():
        md_path = output_dir / test_file
        if not md_path.exists():
            results[test_file] = {'error': 'File not found'}
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        test_results = {
            'passed': 0,
            'failed': 0,
            'details': {}
        }

        for check_name, pattern in test_info['checks'].items():
            passed = check_pattern(content, pattern)
            test_results['details'][check_name] = passed
            if passed:
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1

        results[test_file] = test_results

    return results

def calculate_scores(all_results):
    """Calculate overall scores for each tool"""
    scores = {}

    for tool, results in all_results.items():
        total_passed = 0
        total_checks = 0

        for test_file, test_result in results.items():
            if 'error' not in test_result:
                total_passed += test_result['passed']
                total_checks += test_result['passed'] + test_result['failed']

        score = (total_passed / total_checks * 100) if total_checks > 0 else 0
        scores[tool] = {
            'score': round(score, 1),
            'passed': total_passed,
            'total': total_checks
        }

    return scores

def analyze_readability(tool_name):
    """Subjective readability analysis"""
    output_dir = Path('outputs') / tool_name

    # Read a few sample files for analysis
    samples = ['01-headings.md', '12-mixed-formatting.md', '20-real-world-docs.md']

    metrics = {
        'avg_blank_lines': 0,
        'uses_atx_headers': False,
        'consistent_list_markers': False,
        'clean_output': True
    }

    blank_line_counts = []

    for sample in samples:
        path = output_dir / sample
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count blank lines
            blank_lines = content.count('\n\n')
            blank_line_counts.append(blank_lines)

            # Check for ATX headers
            if re.search(r'^#+ ', content, re.MULTILINE):
                metrics['uses_atx_headers'] = True

            # Check for weird artifacts
            if re.search(r'&[a-z]+;|<[^>]+>', content):
                metrics['clean_output'] = False

    if blank_line_counts:
        metrics['avg_blank_lines'] = sum(blank_line_counts) / len(blank_line_counts)

    return metrics

def main():
    print("=" * 70)
    print("DOM→Markdown Converter Evaluation")
    print("=" * 70)
    print()

    # Run evaluation for each tool
    all_results = {}
    for tool in TOOLS:
        print(f"Evaluating {tool}...")
        all_results[tool] = evaluate_tool(tool)

    # Calculate scores
    scores = calculate_scores(all_results)

    # Print results
    print("\n" + "=" * 70)
    print("OBJECTIVE METRICS SCORES")
    print("=" * 70)
    print()

    # Sort by score
    sorted_tools = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)

    for tool, data in sorted_tools:
        print(f"{tool:25} {data['score']:5.1f}%  ({data['passed']}/{data['total']} checks passed)")

    # Detailed results
    print("\n" + "=" * 70)
    print("DETAILED TEST RESULTS")
    print("=" * 70)

    for test_file, test_info in TEST_CASES.items():
        print(f"\n{test_info['name']} ({test_file}):")
        print("-" * 70)

        for tool in TOOLS:
            if test_file in all_results[tool]:
                result = all_results[tool][test_file]
                if 'error' not in result:
                    status = f"{result['passed']}/{result['passed'] + result['failed']}"
                    print(f"  {tool:25} {status}")

    # Save results to JSON
    output_data = {
        'scores': scores,
        'detailed_results': all_results
    }

    with open('evaluation-results.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    print("\n" + "=" * 70)
    print("Results saved to evaluation-results.json")
    print("=" * 70)

if __name__ == '__main__':
    main()
