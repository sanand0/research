# Research Notes: Finding Data Professionals in India

## Task Overview
Find data scientists and data engineers in India from public sources, focusing on maximum ROI sources.

Target information:
- Designation (Data Scientist, Sr. Data Scientist, Data Engineer, Data Consultant, etc.)
- Experience level
- Location (within India)
- Current company

## Initial Research Plan

### Potential Public Data Sources (to evaluate):

1. **LinkedIn**
   - Largest professional network
   - Rich profile data with experience, location, company
   - Limitations: Need to assess API access and scraping policies

2. **GitHub**
   - Developer profiles often include location and employer
   - Can search by location and analyze profiles
   - Public data, good API access

3. **Kaggle**
   - Data science-focused community
   - Profiles include location, rank, competition history
   - Public profiles, API available

4. **Stack Overflow**
   - Developer community with profiles
   - Location and work info in profiles
   - Public data available

5. **Twitter/X**
   - Professionals often share their designation and company in bio
   - Can search by keywords and location
   - API available but may have limitations

6. **Conference speaker lists**
   - Data science conferences in India (e.g., PyData, DataHack, etc.)
   - Usually public information

7. **Research paper authors**
   - Academic databases (arXiv, Google Scholar)
   - Authors often list affiliations and location

8. **Company engineering blogs**
   - Companies often list their data team members
   - Public information

9. **Open source project contributors**
   - GitHub organizations
   - Public contribution data

10. **Job posting sites**
    - Sometimes show employee profiles or company data teams

## Evaluation Criteria
- **Ease of access**: API availability, rate limits, legal/ethical considerations
- **Data volume**: Number of profiles accessible
- **Data quality**: Completeness of required fields
- **ROI**: Volume × Quality / Effort

---

## Investigation Log

### Step 1: Evaluating High-ROI Sources

#### Research Findings (Initial Web Search)

**HIGH ROI Sources:**

1. **GitHub API** ✅
   - Status: FREE, well-documented API
   - Access: 60 requests/hour unauthenticated, 5000/hour with token
   - Search capability: Can search users by location + keywords
   - Example: `https://api.github.com/search/users?q=location:India+data+scientist`
   - Data available: Username, bio, company, location, repos, followers, blog/website
   - Limitations: Location field is freeform (users can enter anything)
   - Volume: Millions of users, many from India
   - **ROI: EXCELLENT** - Easy access, large volume, good data quality

2. **Kaggle** ⚠️
   - Status: Public profiles available
   - Access: Web scraping or unofficial APIs (need to investigate)
   - Data available: Username, rank, competitions, location, bio
   - Volume: 15M+ users globally, many data scientists
   - Limitations: Need to assess access methods
   - **ROI: GOOD** - Data scientist-focused, but access method unclear

3. **Stack Overflow Developer Survey** ✅
   - Status: Annual survey data publicly available as CSV
   - Access: Direct download from survey.stackoverflow.co
   - Data available: Aggregate data on developers including India
   - Volume: 49K+ responses in 2025, India is top 2 country
   - Limitations: Aggregate/anonymized data, not individual profiles
   - **ROI: GOOD** - Easy to download, reliable data, but not individual contacts

**LOW ROI Sources:**

4. **Twitter/X** ❌
   - Status: Paid API only
   - Cost: Minimum $100/month (Enterprise: $42K/month)
   - **ROI: POOR** - Too expensive for this research

5. **LinkedIn** ❌
   - Status: No free API, scraping violates ToS
   - Access: Only via commercial data providers
   - **ROI: POOR** - Not accessible for free/public research

**DECISION: Focus on GitHub API as primary source, supplement with Stack Overflow survey data**

---

### Step 2: Implementing GitHub API Data Collection

Created `github_collector.py` - a Python script that:
- Searches GitHub users by location (India + major cities) and keywords (data scientist, engineer, etc.)
- Fetches detailed profile information for each user
- Extracts relevant fields: username, name, company, location, bio, repos, followers, etc.
- Handles API rate limiting (5000 requests/hour with token)
- Saves results to both JSON and CSV formats

Search parameters configured:
- Locations: India, Bangalore, Bengaluru, Mumbai, Delhi, Hyderabad, Pune, Chennai, Kolkata, Gurgaon, Noida
- Keywords: data scientist, data engineer, machine learning engineer, ML engineer, data analyst, AI engineer, analytics

Status: Script is currently running and collecting data from GitHub API.

---

### Step 3: Implementing Stack Overflow Survey Analyzer

Created `stackoverflow_analyzer.py` - a script to analyze Stack Overflow Developer Survey data:
- Downloads annual survey data (CSV format)
- Filters for India-based respondents
- Identifies data science and engineering roles
- Analyzes experience levels, education, employment status
- Exports India-specific data professionals to CSV

Note: Requires pandas library (not installed yet) - will need to either install or rewrite without pandas.

---

### Step 4: Data Collection Results

**GitHub API Collection - COMPLETED**

Successfully collected **790 unique profiles** of data professionals in India.

Files generated:
- `github_profiles_20251119_103437.json` (384 KB)
- `github_profiles_20251119_103437.csv` (173 KB)
- `analysis_summary.md` (summary report)

Key statistics:
- Top locations: Bangalore (177), Bengaluru (160), India (105)
- Top companies: IBM (7), Google (6), Walmart (5), TCS (5), Microsoft (5)
- Average public repos: 64.7
- Average followers: 111.4
- Profiles with public email: 344 (43.5%)
- Profiles with blog/website: 438 (55.4%)

Bio keyword matches:
- "data scientist": 323 profiles
- "machine learning": 296 profiles
- "data engineer": 179 profiles
- "AI": 109 profiles
- "senior": 49 profiles

Seniority indicators:
- Senior: 49
- Lead: 18
- Principal: 3
- Junior: 2

---

### Step 5: Analysis and Insights

Created `analyze_data.py` - comprehensive analysis script that:
- Loads collected data from JSON/CSV files
- Analyzes location distribution across India
- Identifies top companies employing data professionals
- Analyzes seniority levels from bio/name keywords
- Generates statistics on repos, followers, activity
- Creates summary reports

Key insights:
1. **Bangalore/Bengaluru is the hub** - Over 42% of profiles are from Bangalore/Bengaluru
2. **Major tech companies** - IBM, Google, Microsoft, Amazon are top employers
3. **Active community** - Average of 64.7 public repos per user shows high engagement
4. **Machine learning focus** - 296 profiles mention ML, indicating strong ML community
5. **Experience levels** - Good mix with 49 senior-level professionals identified

---

### Step 6: Additional Data Sources Considered (Not Implemented)
