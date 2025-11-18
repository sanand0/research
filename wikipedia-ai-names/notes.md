# Research Notes: Wikipedia Names Beginning and Ending with AI

## Objective
Find all people in Wikipedia whose names begin and end with "AI" (case-insensitive).

## Example
- Aishwarya Rai

## Approach
1. Use Wikipedia API to search for people whose names match the pattern
2. Pattern: Full name starts with "AI" and ends with "AI" (case-insensitive)
3. Options explored:
   - `wikipedia` Python library - wraps MediaWiki API
   - `Wikipedia-API` library - recently updated (Jan 2025)
   - Direct MediaWiki API calls

## Implementation Strategy
1. Search Wikipedia for names starting with "Ai"
2. Filter to biographical/people articles
3. Check if full name ends with "ai" (case-insensitive)
4. Collect and analyze results

## Issues Encountered
1. Wikipedia API returning 403 Forbidden errors - likely needs User-Agent header
2. Need to add proper headers and retry logic

## Alternative Approach
1. Use web search to find people with names matching pattern
2. Set proper User-Agent in API requests
3. Use Wikipedia's allpages API which may be more lenient

## First Results
- Script found 136 results but most were false positives
- Only 1 true match found: **Ai Nagai** (Japanese artist)
- Missing: Aishwarya Rai (the example provided by user!)
- Need to search more specifically for this pattern

## Comprehensive Search Results
After targeted searches and manual verification, found 4 people:

1. **Ai Ai** (艾靉; 1906–1982)
   - Republic of China lieutenant general and Deputy Minister of Defense
   - Chinese name romanized as "Ai Ai"

2. **Ai Nagai** (永井愛; born October 16, 1951)
   - Japanese playwright and stage director
   - Co-founder and leader of theater company Nitosha

3. **Ai** (Ai Carina Uemura; born November 2, 1981)
   - Japanese-American singer, songwriter, and rapper
   - Known as "Queen of Hip-hop Soul"
   - Wikipedia page title: "Ai (singer)"

4. **Aishwarya Rai** (born November 1, 1973)
   - Indian actress and former Miss World 1994
   - Full married name is "Aishwarya Rai Bachchan" but maiden name "Aishwarya Rai" matches pattern

## Analysis
- Shortest name: **Ai Ai** (5 characters, or 2 characters without space)
- Longest name: **Aishwarya Rai** (13 characters)
