# Tamil Nadu Vehicle Registration Analysis - Research Notes

## Research Timeline
- **Date**: November 2025
- **Objective**: Analyze TN vehicle registrations for investigative journalism angles

## Data Sources Explored

### Successfully Downloaded
1. **OpenCity Urban Data Portal** - Primary source, FREE
   - https://data.opencity.in/dataset/tamil-nadu-vehicles-registration-data
   - Downloaded 8 CSV files covering 2001-2023

### Explored but Limited Access
2. **data.gov.in** - Required API key, pages wouldn't render properly
3. **Vahan/Parivahan Portal** - Individual lookups only, no bulk download
4. **Dataful.in** - Has monthly data but requires subscription (~₹5000)
5. **India Data Portal (CKAN)** - Dataset existed but "Datastore active: False"
6. **Kaggle** - "Vehicle Registered In India" - aggregate only, not TN-specific

### Key Limitation Discovered
**Individual vehicle-level data is NOT publicly available in bulk.**
Only aggregate statistics (district/state totals, category breakdowns) are accessible.
This is likely due to privacy regulations around vehicle owner information.

## Data Downloaded (from OpenCity)

| File | Size | Description | Period |
|------|------|-------------|--------|
| tn-vehicular-position-2001-2023.csv | 7.2KB | Stock by category | 2001-2023 |
| tn-newly-registered-2008-21.csv | 3.2KB | New registrations | 2008-2021 |
| tn-districtwise-commercial-vehicles.csv | 4.4KB | Commercial by district | 2021 |
| tn-districtwise-non-commercial-vehicles.csv | 3.1KB | Non-commercial by district | 2021 |
| tn-commercial-vehicles-distwise-2023.csv | 4.6KB | Commercial by district | 2023 |
| tn-non-commercial-vehicles-distwise-2023.csv | 3.4KB | Non-commercial by district | 2023 |
| tn-autorickshaws-2023.csv | 310B | Autorickshaws by zone | 2023 |
| tn-list-of-autorickshaws.csv | 311B | Autorickshaws (older) | 2021 |

## Key Findings

### 1. The Privatization of Mobility
- Cars: 26:1 ratio to public buses in 2001 → 166:1 in 2023
- Public buses barely grew (17K → 20K) while cars exploded (447K → 3.34M)
- **This is a policy failure forcing private vehicle purchases**

### 2. 10x District Inequality
- Coimbatore: 843 vehicles per 1,000 people
- Tirupathur: 84 vehicles per 1,000 people
- Industrial districts: 550 avg vs Agricultural: 213 avg (2.6x gap)

### 3. Moped Decline Story
- 2001: Mopeds 2.3M, Motorcycles 1.1M
- 2023: Mopeds 5.7M, Motorcycles 19.2M
- Motorcycle share: 33% → 77%

### 4. School Bus Explosion (16x growth)
- 2,141 → 34,835 school buses
- Compensating for inadequate public transit

### 5. LCV Rise and Fall
- Peaked at 231K in 2015, now down to 186K
- Signals structural changes in last-mile logistics

### 6. Ride-Hailing Decline
- Motor cabs peaked at 134K in 2019
- Down to 115K in 2023 (-14%)

### 7. Chennai Autorickshaw Dominance
- Chennai zones: 132,647 autos (44% of state)
- Rest of state: 170,271 autos (56%)

### 8. Ambulance Inequality
- 10x gap between best and worst covered districts
- Thiruvallur: 54.7/lakh vs Dindigul: 11.5/lakh

## Cross-Verification

### Population Data
- Used 2011 Census projections to 2023
- TN population ~77 million in 2023
- Could refine with more recent economic surveys

### National Comparison
- India avg: 163 vehicles/1000 people
- TN avg: 343 vehicles/1000 people (2.1x national)
- Coimbatore: 5.2x national average

## What the Data Can't Tell Us

1. **Electric vehicle penetration** - No fuel type breakdown
2. **Vehicle age/scrapping** - Registration doesn't track active vs. scrapped
3. **Ownership patterns** - No data on multiple vehicle ownership
4. **Usage patterns** - No km traveled data
5. **Individual demographics** - No owner income/occupation data

## Methodology Notes

- Per-capita calculations used population estimates (not official census)
- District boundaries changed with new districts carved out post-2011
- 2022 data gap in the time series
- Used pandas/matplotlib for analysis and visualization

## Files Produced
- `README.md` - Full investigative report
- `notes.md` - This file
- `visualizations/` - 8 PNG charts
- `data/` - 8 source CSV files
