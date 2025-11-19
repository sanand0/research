# Finding Data Professionals in India - Research Report

## Executive Summary

This research project identified and collected information on **790 unique data scientists, data engineers, and related professionals** based in India using publicly available sources. The primary data source was GitHub's public API, which proved to be the highest ROI (Return on Investment) source for this task.

## Objective

Find all data scientists and data engineers in India from public sources, focusing on:
- Designation (Data Scientist, Sr. Data Scientist, Data Engineer, Data Consultant, etc.)
- Experience level
- Location within India
- Current company

## Methodology

### 1. Source Evaluation

We evaluated multiple public data sources based on:
- **Ease of access**: API availability, rate limits, legal/ethical considerations
- **Data volume**: Number of profiles accessible
- **Data quality**: Completeness of required fields
- **ROI**: (Volume × Quality) / Effort

### 2. Sources Evaluated

| Source | Access | Volume | Quality | Cost | ROI | Decision |
|--------|--------|--------|---------|------|-----|----------|
| **GitHub API** | Free API (5K req/hr with token) | Millions of users | High | Free | **Excellent** | ✅ **Selected** |
| Stack Overflow Survey | Public CSV downloads | 49K+ responses | Medium | Free | Good | ⚠️ Supplementary |
| Kaggle | Web scraping needed | 15M+ users | Medium | Free | Medium | ⚠️ Complex access |
| LinkedIn | No free API | Largest | High | Paid only | **Poor** | ❌ Not accessible |
| Twitter/X | Paid API only | Large | Medium | $100+/month | **Poor** | ❌ Too expensive |

**Winner: GitHub API** - Best combination of accessibility, volume, and data quality.

### 3. Data Collection Process

**GitHub API Collection:**
- Searched users by location (India, Bangalore, Bengaluru) + keywords (data scientist, data engineer, machine learning engineer)
- Fetched detailed profile information for each user
- Deduplicated across multiple search queries
- Extracted: username, name, company, location, bio, email, repos, followers, etc.

**Search Parameters:**
- **Locations**: India, Bangalore, Bengaluru (top 3 for initial collection)
- **Keywords**: data scientist, data engineer, machine learning engineer (top 3 keywords)
- **Max per query**: 100 profiles
- **Result**: 790 unique profiles after deduplication

## Results

### Overall Statistics

- **Total Profiles Collected**: 790
- **Profiles with Public Email**: 344 (43.5%)
- **Profiles with Blog/Website**: 438 (55.4%)
- **Average Public Repositories**: 64.7
- **Average Followers**: 111.4
- **Users with 100+ Followers**: 82 (10.4%)

### Geographic Distribution

**Top 15 Locations:**

| Location | Count | Percentage |
|----------|-------|------------|
| Bangalore | 177 | 22.4% |
| Bengaluru | 160 | 20.3% |
| India | 105 | 13.3% |
| Bengaluru, India | 57 | 7.2% |
| Bangalore, India | 53 | 6.7% |
| Bengaluru, Karnataka, India | 20 | 2.5% |
| Bengaluru, Karnataka | 14 | 1.8% |
| Bangalore, Karnataka, India | 12 | 1.5% |
| New Delhi, India | 9 | 1.1% |
| Chennai, India | 9 | 1.1% |
| Mumbai, India | 7 | 0.9% |
| Pune, India | 7 | 0.9% |
| Hyderabad, India | 6 | 0.8% |

**Key Insight**: Bangalore/Bengaluru represents over **42%** of all profiles, confirming it as India's data science hub.

### Company Distribution

**Top 20 Companies:**

| Company | Count |
|---------|-------|
| IBM | 7 |
| Google | 6 |
| Walmart | 5 |
| Tata Consultancy Services | 5 |
| Microsoft | 5 |
| Tesco | 4 |
| Amazon | 4 |
| Capgemini | 4 |
| Thoughtworks | 3 |
| Deloitte | 3 |
| LTIMindtree | 3 |
| Oracle | 3 |
| Societe Generale | 3 |
| Fractal Analytics | 3 |
| Gojek | 3 |
| Swiggy | 2 |
| h2oai | 2 |
| Optum | 2 |
| Jio Platforms Limited | 2 |

Mix of multinational tech giants (Google, Microsoft, Amazon), Indian IT services (TCS, Capgemini), and Indian startups (Swiggy, Jio).

### Role & Expertise Analysis

**Bio Keyword Matches:**

| Keyword | Profiles | Percentage |
|---------|----------|------------|
| Data Scientist | 323 | 40.9% |
| Machine Learning | 296 | 37.5% |
| Data Engineer | 179 | 22.7% |
| AI | 109 | 13.8% |
| Deep Learning | 35 | 4.4% |
| NLP | 25 | 3.2% |
| Big Data | 19 | 2.4% |
| Computer Vision | 16 | 2.0% |
| Analytics | 16 | 2.0% |

**Seniority Level Indicators:**

| Level | Count |
|-------|-------|
| Senior | 49 |
| Lead | 18 |
| Principal | 3 |
| Manager | 1 |
| Junior | 2 |
| Mid | 2 |

Note: Many profiles don't specify seniority level explicitly, so actual distribution may vary.

### Activity & Engagement

**Account Age Distribution:**

| Year Created | Accounts |
|--------------|----------|
| 2020 | 108 |
| 2017 | 107 |
| 2019 | 106 |
| 2018 | 105 |
| 2021 | 69 |
| 2016 | 73 |
| 2022 | 44 |
| 2023 | 17 |
| 2024 | 11 |
| 2025 | 4 |

Peak GitHub adoption among Indian data professionals was around 2017-2020.

## Data Files

The following files contain the collected data:

1. **github_profiles_20251119_103437.csv** (173 KB)
   - CSV format with all profile fields
   - Easily importable into Excel, Google Sheets, databases
   - Fields: username, name, company, blog, location, email, bio, public_repos, followers, following, created_at, updated_at, profile_url, twitter_username

2. **github_profiles_20251119_103437.json** (384 KB)
   - JSON format for programmatic access
   - Same data as CSV in structured format

3. **analysis_summary.md** (715 B)
   - Quick summary report with top locations and companies

## Tools & Scripts Created

### 1. github_collector.py
Python script that:
- Searches GitHub API for users by location and keywords
- Handles rate limiting (5000 requests/hour with token)
- Fetches detailed profile information
- Deduplicates results
- Saves to JSON and CSV formats

**Usage:**
```bash
export GITHUB_TOKEN="your_token_here"  # Optional but recommended
python3 github_collector.py
```

**Configuration:** Edit the `locations` and `keywords` lists in main() to customize search parameters.

### 2. analyze_data.py
Analysis script that:
- Loads collected data from JSON/CSV files
- Analyzes location, company, role distributions
- Generates statistics on activity and engagement
- Creates summary reports

**Usage:**
```bash
python3 analyze_data.py
```

### 3. stackoverflow_analyzer.py
Stack Overflow Developer Survey analyzer (created but not run due to pandas dependency)
- Downloads annual survey data
- Filters for India-based respondents
- Identifies data science roles

### 4. web_sources_collector.py
Template for collecting from other web sources (Kaggle, conferences, etc.)
- Demonstrates web scraping approaches
- Includes legal/ethical considerations

## Scaling Opportunities

The current collection (790 profiles) used limited search parameters for demonstration. To scale up:

### 1. Expand Location Coverage
Currently searched: India, Bangalore, Bengaluru

**Additional locations to search:**
- Mumbai, Delhi, New Delhi, Gurgaon, Noida
- Hyderabad, Pune, Chennai, Kolkata
- Ahmedabad, Jaipur, Kochi, Chandigarh
- State names: Maharashtra, Karnataka, Tamil Nadu, etc.

**Estimated additional profiles**: 500-1000

### 2. Expand Keyword Coverage
Currently searched: data scientist, data engineer, machine learning engineer

**Additional keywords:**
- ML engineer, AI engineer, analytics engineer
- data analyst, business intelligence, BI developer
- deep learning, NLP engineer, computer vision
- MLOps engineer, data platform engineer
- quantitative analyst, research scientist

**Estimated additional profiles**: 1000-2000

### 3. Reduce Per-Query Limits
Current limit: 100 profiles per query (for speed)
GitHub allows: up to 1000 results per search query

**Potential**: 10x increase in coverage

### 4. Alternative & Supplementary Sources

**Kaggle Profiles:**
- 15M+ users globally, many data scientists
- Profiles include: tier, rank, competitions, notebooks
- Challenge: No official API, requires web scraping
- Estimated India profiles: 10,000-50,000

**Stack Overflow:**
- Developer Survey: Annual data with thousands of Indian respondents
- User profiles: Location and tags visible
- Challenge: Aggregate data only in surveys
- Estimated relevant profiles: 5,000-10,000

**Conference Speaker Lists:**
- PyData Delhi, DataHack Summit, PyCon India, etc.
- Usually 50-200 speakers per conference
- High-quality leads (conference speakers typically experienced)
- Estimated total: 500-1000

**Research Paper Authors:**
- arXiv, Google Scholar with India affiliation
- High expertise level (researchers and academics)
- Estimated: 1,000-5,000

**Company Engineering Blogs:**
- Swiggy, Flipkart, Paytm, Ola, Zomato, etc. list their data teams
- Usually 10-50 members per company
- Estimated: 500-1,000

### Total Potential
With full implementation of all sources and expanded parameters:
- **Conservative estimate**: 15,000-30,000 profiles
- **Optimistic estimate**: 50,000-100,000 profiles

## Recommendations

### For Maximum Coverage

1. **GitHub API** (PRIMARY): Expand to all Indian cities and all data science keywords
   - Estimated time: 20-40 hours of API calls
   - Cost: Free (with rate limiting)
   - Expected: 3,000-5,000 unique profiles

2. **Kaggle** (SECONDARY): Implement profile scraper for India-based Kagglers
   - Estimated time: 2-4 hours development + crawling time
   - Cost: Free
   - Expected: 5,000-10,000 profiles
   - Risk: Must respect robots.txt and rate limits

3. **Stack Overflow Survey** (TERTIARY): Download and analyze recent surveys
   - Estimated time: 1-2 hours
   - Cost: Free
   - Expected: Aggregate stats, not individual profiles

4. **Manual Collection** (SUPPLEMENTARY): Conference lists, company blogs
   - Estimated time: 4-8 hours
   - Cost: Free
   - Expected: 500-1,000 high-quality leads

### For Highest Quality Leads

Focus on:
1. **Followers > 100**: More established professionals (82 in current dataset)
2. **Public email available**: Easier to contact (344 in current dataset)
3. **Senior/Lead/Principal**: Experienced professionals (70 identified)
4. **Conference speakers**: High expertise and visibility
5. **Active contributors**: Recent commits, high repo count

## Legal & Ethical Considerations

All data collected is:
- ✅ Publicly available on GitHub
- ✅ Accessible via official GitHub API
- ✅ Subject to GitHub's Terms of Service
- ✅ Not behind any authentication or paywall
- ✅ Collected with rate limiting to respect API limits

**Important Notes:**
- Data should be used for legitimate purposes only
- Respect user privacy and GDPR compliance
- Contact information should not be used for unsolicited marketing
- Always allow users to opt-out of any communications

## Conclusion

This research successfully identified **790 data scientists and engineers in India** using GitHub's public API as the primary source. The data shows:

- **Bangalore/Bengaluru dominates** with 42% of profiles
- **Major employers** include both MNCs (Google, Microsoft, IBM) and Indian companies (TCS, Swiggy)
- **Machine Learning expertise** is prevalent (37.5% mention ML)
- **Active community** with average 64.7 public repositories
- **Scaling potential** to 15,000-100,000 profiles with expanded parameters

The tools and methodology developed can be easily extended to:
- Collect more profiles from GitHub (expand locations/keywords)
- Add additional sources (Kaggle, conferences, etc.)
- Filter for specific criteria (seniority, expertise, location)
- Keep data updated with regular collection runs

## Files in This Repository

```
india-data-professionals/
├── README.md                           # This report
├── notes.md                            # Research notes and process log
├── github_collector.py                 # GitHub API collection script
├── analyze_data.py                     # Data analysis script
├── stackoverflow_analyzer.py           # Stack Overflow survey analyzer
├── web_sources_collector.py            # Web scraping templates
├── github_profiles_20251119_103437.csv # Collected profiles (CSV)
├── github_profiles_20251119_103437.json# Collected profiles (JSON)
└── analysis_summary.md                 # Quick summary
```

## Usage

To use the collected data:

1. **CSV**: Open in Excel, Google Sheets, or import into database
2. **JSON**: Use with Python, JavaScript, or any JSON parser
3. **Scripts**: Run collection again with expanded parameters for more data

To expand the collection:

1. Edit `github_collector.py`:
   - Add more locations to `locations` list
   - Add more keywords to `keywords` list
   - Increase `max_per_query` (up to 1000)

2. Run: `python3 github_collector.py`

3. Analyze: `python3 analyze_data.py`

---

**Research completed**: November 19, 2025
**Total profiles collected**: 790
**Primary source**: GitHub API
**Data format**: CSV + JSON
