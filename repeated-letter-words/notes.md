# Research Notes: Words with Repeated Letters

## Goal
Find English words of 4+ letters where over 50% of the letters are the same letter.
Develop a statistically robust scoring method for letter concentration.

## Progress Log

### Session 1 - Initial Setup

Starting research into letter-dominant words. Examples given:
- `lull` = 75% L (3 of 4 letters)
- `mummy` = 60% M (3 of 5 letters)

Need to:
1. Find comprehensive dictionary
2. Analyze all words programmatically
3. Develop scoring method
4. Write articles in Gardner and Munroe styles

### Dictionary Found
- Downloaded dwyl/english-words with 370,105 words
- This is one of the largest freely available English word lists

### Analysis Results
- **333 words** of 4+ letters have >50% of their letters as the same letter
- Highest percentages: `mmmm` and `oooo` at 100% (though questionable if real words)
- Most common 75% words (4 letters): `lull`, `sass`, `epee`, `brrr`, `zizz`
- Longest words at 62.5%: `assesses`, `swissess` (8 letters)
- Longest qualifying words: 9 letters like `possesses`, `sassiness`, `beekeeper`

### Interesting Findings
1. Letter E dominates with 89 qualifying words (27% of all)
2. Letter A is second with 57 words (17%)
3. Z is massively overrepresented: 8.6x more dominant than expected from frequency
4. R, T, I are underrepresented as dominant letters
5. MISSISSIPPI is only 36% I - doesn't qualify!
6. SYZYGY is exactly 50% Y - just misses the threshold

### Scoring Method
Developed an adjusted score: `(k/n - 1/26) * sqrt(n)`
- k = count of dominant letter
- n = total letters
- This rewards longer words achieving same percentage
- Top scorers: `mmmm`, `oooo` (1.92), then `assesses` (1.66)

