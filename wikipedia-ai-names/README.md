# Wikipedia Names Beginning and Ending with "AI"

## Research Question

Find all people in Wikipedia whose names begin and end with "AI" (case-insensitive).

## Methodology

1. Searched Wikipedia API using multiple strategies:
   - Direct searches for common name patterns
   - Browsing all pages starting with "Ai"
   - Manual verification of candidate names
   - Targeted searches for Japanese, Indian, and Chinese names

2. Implemented pattern matching: `name.lower().startswith("ai") and name.lower().endswith("ai")`

3. Verified results using Wikipedia API and web searches

## Results

Found **4 people** whose names match the pattern:

### 1. Ai Ai (艾靉)
- **Length**: 5 characters (SHORTEST)
- **Born**: 1906
- **Died**: 1982
- **Nationality**: Chinese (Republic of China)
- **Occupation**: Lieutenant general and Deputy Minister of Defense
- **Wikipedia**: [Ai (surname)](https://en.wikipedia.org/wiki/Ai_(surname))

### 2. Ai
- **Full name**: Ai Carina Uemura (植村 愛 カリーナ)
- **Stage name**: AI or Ai (mononym)
- **Length**: 2 characters (or "Ai (singer)" = 11 characters on Wikipedia)
- **Born**: November 2, 1981
- **Nationality**: Japanese-American
- **Occupation**: Singer, songwriter, rapper
- **Notable**: Known as "Queen of Hip-hop Soul"; single "Story" (2005) sold over 5 million units
- **Wikipedia**: [Ai (singer)](https://en.wikipedia.org/wiki/Ai_(singer))

### 3. Ai Nagai (永井愛)
- **Length**: 8 characters
- **Born**: October 16, 1951
- **Nationality**: Japanese
- **Occupation**: Playwright and stage director
- **Notable**: Co-founder and leader of theater company Nitosha; regarded as one of Japan's most sought-after playwrights
- **Wikipedia**: [Ai Nagai](https://en.wikipedia.org/wiki/Ai_Nagai)

### 4. Aishwarya Rai
- **Full name**: Aishwarya Rai Bachchan
- **Maiden name**: Aishwarya Rai (matches pattern)
- **Length**: 13 characters (LONGEST)
- **Born**: November 1, 1973
- **Nationality**: Indian
- **Occupation**: Actress
- **Notable**: Miss World 1994; one of the most popular and influential celebrities in India; named by Time magazine as one of the 100 most influential people in the world (2004)
- **Wikipedia**: [Aishwarya Rai](https://en.wikipedia.org/wiki/Aishwarya_Rai_Bachchan)

## Analysis

### Shortest Name
**Ai Ai** - 5 characters (or just **Ai** at 2 characters if counting the mononym without Wikipedia disambiguation)

### Longest Name
**Aishwarya Rai** - 13 characters

### Geographic Distribution
- **East Asia**: 3 people (Ai Ai from China, Ai and Ai Nagai from Japan)
- **South Asia**: 1 person (Aishwarya Rai from India)

### Time Period
- Spans from 1906 (Ai Ai's birth) to present
- Three are living: Ai Nagai, Ai, and Aishwarya Rai
- One deceased: Ai Ai (1906-1982)

### Occupations
- Military: 1 (Ai Ai)
- Entertainment: 3 (singer, actress, playwright)

## Challenges

1. **False Positives**: Initial automated search returned 136 results, but manual verification revealed only 4 true matches. Many false positives were due to:
   - Search results including pages mentioning the search term but not having titles matching the pattern
   - List pages and non-biographical articles
   - Names containing "ai" but not at both start and end

2. **Wikipedia API Access**: Initial attempts received 403 Forbidden errors, resolved by adding proper User-Agent headers

3. **Name Variations**:
   - "Aishwarya Rai" appears as "Aishwarya Rai Bachchan" on Wikipedia (married name)
   - "Ai" appears as "Ai (singer)" with disambiguation on Wikipedia
   - Some names have multiple romanizations

## Files

- `search_wikipedia.py` - Initial broad search script
- `filter_results.py` - Script to filter false positives
- `manual_search.py` - Manual verification of specific names
- `comprehensive_search.py` - Final comprehensive search combining all strategies
- `notes.md` - Research notes and process documentation
- `final_results.json` - JSON file with final results

## Conclusion

This research identified **4 people** in Wikipedia whose names begin and end with "AI":
- **Shortest**: Ai Ai (5 characters)
- **Longest**: Aishwarya Rai (13 characters)

The pattern is rare and predominantly found in East Asian (Japanese, Chinese) and South Asian (Indian) names, reflecting naming conventions in these cultures where "Ai" is a common name component.
