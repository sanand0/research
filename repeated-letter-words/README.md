# Repeated Letter Words: Finding Letter-Dominant English Words

## Overview

This project identifies all English words of 4+ letters where more than 50% of the letters are the same letter. For example, "LULL" is 75% L (3 out of 4 letters).

## Key Findings

- **333 words** out of 370,105 in our dictionary (0.09%) meet the criteria
- Highest percentages in real words: LULL, SASS, EPEE at 75%
- Longest qualifying words: POSSESSES, SASSINESS, BEEKEEPER (9 letters, 56%)
- The letter **E** dominates, appearing as the dominant letter in 89 words (27%)
- The letter **Z** is 8.6x more likely to be dominant than its frequency would suggest

### Champion Words by Length

| Length | Word | Dominant Letter | Percentage |
|--------|------|-----------------|------------|
| 4 | LULL | L | 75% |
| 5 | MUMMY | M | 60% |
| 6 | ASSESS | S | 67% |
| 7 | POSSESS | S | 57% |
| 8 | ASSESSES | S | 62.5% |
| 9 | POSSESSES | S | 56% |

## Statistical Scoring

To fairly compare words of different lengths, we developed an adjusted score:

```
score = (k/n - 1/26) * sqrt(n)
```

Where:
- `k` = count of dominant letter
- `n` = total letters
- `1/26` = expected frequency under uniform distribution

This rewards longer words achieving the same percentage, since that's statistically harder.

## Files

- **[analyze_words.py](analyze_words.py)** - Python script to analyze dictionary
- **[all_qualifying_words.csv](all_qualifying_words.csv)** - Complete list of 333 qualifying words
- **[analysis_results.json](analysis_results.json)** - Detailed analysis in JSON format
- **[notes.md](notes.md)** - Research notes and observations

## Articles

### [gardner.md](gardner.md) - "The Tyranny of a Single Letter"

Written in the style of Martin Gardner's Mathematical Games column. Presents the problem as an invitation to readers, catalogs interesting examples, explores edge cases (proper nouns? abbreviations?), and connects letter dominance to combinatorics and information theory. Includes puzzles for readers to solve.

### [munroe.md](munroe.md) - "LETTER DOMINANCE: A Computational Investigation"

Written in the style of Randall Munroe's XKCD/What If. Features Python code, ASCII histograms, stick-figure diagram descriptions, deadpan observations about dictionary edge cases ("Does 'mmmm' count?"), and absurd extrapolations about constructed words. Includes footnotes about Welsh and the ontological status of "www."

## Interesting Observations

1. **MISSISSIPPI doesn't qualify** - It's only 36% I (4/11 letters)
2. **BANANA is exactly 50%** - Just misses the >50% threshold
3. **S is the most grammatically productive letter** - Appears in plurals, possessives, and "-ness" suffixes
4. **Vowels dominate** - E, A, O are the top three dominant letters
5. **Some common letters rarely dominate** - T (9% of English) produces only 3% of dominant words

## Data Source

Dictionary: [dwyl/english-words](https://github.com/dwyl/english-words) (370,105 words)

## Running the Analysis

```bash
python3 analyze_words.py
```

Outputs:
- Sorted lists by percentage and statistical score
- Breakdown by dominant letter and word length
- Notable examples and edge cases
- CSV and JSON files for further analysis
