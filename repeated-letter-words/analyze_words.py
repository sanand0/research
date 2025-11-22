#!/usr/bin/env python3
"""
Analyze words for letter dominance - finding words where >50% of letters are the same.
"""

import json
from collections import Counter
from math import sqrt, log
import csv

def get_dominant_letter_stats(word):
    """
    Returns the dominant letter and its statistics for a word.
    """
    word_lower = word.lower()
    letter_counts = Counter(word_lower)
    if not letter_counts:
        return None

    dominant_letter, count = letter_counts.most_common(1)[0]
    total_letters = len(word_lower)
    percentage = count / total_letters

    return {
        'word': word,
        'dominant_letter': dominant_letter,
        'count': count,
        'total': total_letters,
        'percentage': percentage
    }

def calculate_binomial_z_score(k, n, p=0.077):
    """
    Calculate z-score for seeing k occurrences of a specific letter in n letters.

    Under null hypothesis, each letter appears with probability p.
    Using p=0.077 (approximately 1/13) as rough average for common letters.
    But since we're looking at ANY dominant letter, we use p=1/26 ≈ 0.0385 per letter,
    but account for selection of the maximum.

    Actually, a better approach: compare against expected uniform distribution.
    Expected max frequency for random letters in word of length n.
    """
    # Expected value and std dev for binomial
    expected = n * p
    std_dev = sqrt(n * p * (1 - p))

    if std_dev == 0:
        return 0

    z_score = (k - expected) / std_dev
    return z_score

def calculate_concentration_score(k, n):
    """
    A more sophisticated scoring method that accounts for word length.

    Uses a modified z-score approach:
    - Assumes letters are uniformly distributed (p = 1/26)
    - Calculates how many standard deviations the observed count is above expected
    - Penalizes short words where high percentages are easier

    Higher scores = more impressive concentration.
    """
    p = 1/26  # Probability of any specific letter under uniform distribution

    # Expected count and standard deviation
    expected = n * p
    variance = n * p * (1 - p)
    std_dev = sqrt(variance) if variance > 0 else 0.001

    # Z-score: how many standard deviations above expected
    z_score = (k - expected) / std_dev

    return z_score

def calculate_adjusted_score(k, n):
    """
    An information-theoretic score based on the surprise of the observation.

    Uses negative log probability (surprisal) normalized by word length.
    This naturally handles the fact that longer words with high concentration
    are more impressive.
    """
    # Probability of getting exactly k of a specific letter in n positions
    # Using binomial approximation
    p = 1/26

    # For simplicity, use concentration ratio adjusted by length
    # Score = (k/n - 1/26) * sqrt(n)
    # This gives more credit to longer words achieving same percentage

    concentration_ratio = k / n
    baseline = 1/26

    # Length-adjusted excess concentration
    score = (concentration_ratio - baseline) * sqrt(n)

    return score

def analyze_dictionary(filepath, min_length=4, min_percentage=0.5):
    """
    Analyze all words in the dictionary and return those meeting criteria.
    """
    results = []
    all_stats = []

    with open(filepath, 'r') as f:
        for line in f:
            word = line.strip()
            if not word or not word.isalpha():
                continue

            stats = get_dominant_letter_stats(word)
            if stats is None:
                continue

            # Calculate various scores
            stats['z_score'] = calculate_concentration_score(stats['count'], stats['total'])
            stats['adjusted_score'] = calculate_adjusted_score(stats['count'], stats['total'])

            all_stats.append(stats)

            if stats['total'] >= min_length and stats['percentage'] > min_percentage:
                results.append(stats)

    return results, all_stats

def main():
    print("=" * 70)
    print("LETTER DOMINANCE ANALYSIS")
    print("Finding words where >50% of letters are the same letter")
    print("=" * 70)
    print()

    # Analyze dictionary
    results, all_stats = analyze_dictionary('words_alpha.txt', min_length=4, min_percentage=0.5)

    print(f"Total words analyzed: {len(all_stats)}")
    print(f"Words meeting criteria (4+ letters, >50% same letter): {len(results)}")
    print()

    # Sort by percentage, then by length (descending)
    results_by_percentage = sorted(results, key=lambda x: (-x['percentage'], -x['total']))

    # Sort by adjusted score (most impressive statistically)
    results_by_score = sorted(results, key=lambda x: -x['adjusted_score'])

    # Sort by z-score
    results_by_zscore = sorted(results, key=lambda x: -x['z_score'])

    print("=" * 70)
    print("TOP 50 BY PERCENTAGE")
    print("=" * 70)
    print(f"{'Word':<25} {'Letter':>6} {'Count':>6} {'Total':>6} {'Pct':>8} {'Score':>10}")
    print("-" * 70)
    for r in results_by_percentage[:50]:
        print(f"{r['word']:<25} {r['dominant_letter']:>6} {r['count']:>6} {r['total']:>6} {r['percentage']*100:>7.1f}% {r['adjusted_score']:>10.2f}")

    print()
    print("=" * 70)
    print("TOP 50 BY ADJUSTED SCORE (statistically most impressive)")
    print("=" * 70)
    print(f"{'Word':<25} {'Letter':>6} {'Count':>6} {'Total':>6} {'Pct':>8} {'Score':>10}")
    print("-" * 70)
    for r in results_by_score[:50]:
        print(f"{r['word']:<25} {r['dominant_letter']:>6} {r['count']:>6} {r['total']:>6} {r['percentage']*100:>7.1f}% {r['adjusted_score']:>10.2f}")

    # Group by dominant letter
    print()
    print("=" * 70)
    print("BREAKDOWN BY DOMINANT LETTER")
    print("=" * 70)

    by_letter = {}
    for r in results:
        letter = r['dominant_letter'].upper()
        if letter not in by_letter:
            by_letter[letter] = []
        by_letter[letter].append(r)

    for letter in sorted(by_letter.keys()):
        words = by_letter[letter]
        print(f"\n{letter}: {len(words)} words")
        top_words = sorted(words, key=lambda x: (-x['percentage'], -x['total']))[:10]
        for w in top_words:
            print(f"  {w['word']} ({w['percentage']*100:.0f}%)")

    # Analyze by word length
    print()
    print("=" * 70)
    print("ANALYSIS BY WORD LENGTH")
    print("=" * 70)

    by_length = {}
    for r in results:
        length = r['total']
        if length not in by_length:
            by_length[length] = []
        by_length[length].append(r)

    print(f"\n{'Length':>8} {'Count':>8} {'Avg %':>10} {'Max %':>10} {'Best Example':<25}")
    print("-" * 70)
    for length in sorted(by_length.keys()):
        words = by_length[length]
        avg_pct = sum(w['percentage'] for w in words) / len(words)
        max_pct = max(w['percentage'] for w in words)
        best = max(words, key=lambda x: x['percentage'])
        print(f"{length:>8} {len(words):>8} {avg_pct*100:>9.1f}% {max_pct*100:>9.1f}% {best['word']:<25}")

    # Notable examples section
    print()
    print("=" * 70)
    print("NOTABLE EXAMPLES")
    print("=" * 70)

    # Longest words with >50%
    long_words = [r for r in results if r['total'] >= 8]
    long_words_sorted = sorted(long_words, key=lambda x: (-x['total'], -x['percentage']))
    print("\nLongest words with >50% dominance:")
    for w in long_words_sorted[:20]:
        print(f"  {w['word']} ({w['total']} letters, {w['percentage']*100:.0f}% {w['dominant_letter'].upper()})")

    # Words with exactly 50%
    fifty_percent = [r for r in results if 0.5 < r['percentage'] <= 0.51]
    print(f"\nWords just barely over 50% ({len(fifty_percent)} words):")
    for w in sorted(fifty_percent, key=lambda x: -x['total'])[:10]:
        print(f"  {w['word']} ({w['percentage']*100:.1f}%)")

    # Highest percentage words by length
    print("\nHighest percentage by length category:")
    for min_len, max_len, label in [(4, 5, "Short (4-5)"), (6, 8, "Medium (6-8)"), (9, 15, "Long (9-15)"), (16, 100, "Very Long (16+)")]:
        subset = [r for r in results if min_len <= r['total'] <= max_len]
        if subset:
            best = max(subset, key=lambda x: x['percentage'])
            print(f"  {label}: {best['word']} ({best['percentage']*100:.0f}% {best['dominant_letter'].upper()})")

    # Save results to JSON for further analysis
    output_data = {
        'summary': {
            'total_words_analyzed': len(all_stats),
            'qualifying_words': len(results),
            'criteria': 'min_length=4, min_percentage>50%'
        },
        'by_percentage': [
            {
                'word': r['word'],
                'dominant_letter': r['dominant_letter'],
                'count': r['count'],
                'total': r['total'],
                'percentage': round(r['percentage'] * 100, 1),
                'adjusted_score': round(r['adjusted_score'], 2)
            }
            for r in results_by_percentage[:200]
        ],
        'by_score': [
            {
                'word': r['word'],
                'dominant_letter': r['dominant_letter'],
                'count': r['count'],
                'total': r['total'],
                'percentage': round(r['percentage'] * 100, 1),
                'adjusted_score': round(r['adjusted_score'], 2)
            }
            for r in results_by_score[:200]
        ],
        'by_letter': {
            letter: [w['word'] for w in sorted(words, key=lambda x: -x['percentage'])[:20]]
            for letter, words in by_letter.items()
        },
        'length_stats': {
            str(length): {
                'count': len(words),
                'avg_percentage': round(sum(w['percentage'] for w in words) / len(words) * 100, 1),
                'max_percentage': round(max(w['percentage'] for w in words) * 100, 1),
                'examples': [w['word'] for w in sorted(words, key=lambda x: -x['percentage'])[:5]]
            }
            for length, words in by_length.items()
        }
    }

    with open('analysis_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    # Save full results as CSV
    with open('all_qualifying_words.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'dominant_letter', 'count', 'total', 'percentage', 'adjusted_score', 'z_score'])
        for r in results_by_percentage:
            writer.writerow([
                r['word'],
                r['dominant_letter'],
                r['count'],
                r['total'],
                round(r['percentage'] * 100, 2),
                round(r['adjusted_score'], 3),
                round(r['z_score'], 3)
            ])

    print()
    print("=" * 70)
    print(f"Results saved to analysis_results.json and all_qualifying_words.csv")
    print("=" * 70)

if __name__ == '__main__':
    main()
