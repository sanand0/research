# Jakarta Schools Research Notes

## Objective
Create a spreadsheet of ~100 private K-12 educational institutions in Jakarta, Indonesia, with decision-maker contact information.

## Research Log

### Session 1 - Initial Research

**Date:** 2025-11-22

#### Step 1: Identify aggregator sites and directories

Looking for:
- Indonesian government education directories
- School association listings (e.g., NPSN - National School Identification Number database)
- International school aggregators
- Private school directories

**Key Sources Identified:**
1. **international-schools-database.com** - Lists 71+ international schools in Jakarta
2. **edarabia.com** - School directory with fees and ratings
3. **nowjakarta.co.id** - School guide with comprehensive listings
4. **expat.or.id** - Expatriate-focused school directory (most useful for contact details)
5. **referensi.data.kemdikbud.go.id** - Indonesian government's official school database (NPSN)
6. **spkindonesia.org** - SPK (Satuan Pendidikan Kerjasama) school association
7. **Individual school websites** - For leadership/staff information

#### Step 2: Understanding Indonesian School Categories

**Key findings:**
- **SPK (Satuan Pendidikan Kerjasama)**: Since 2014/2015, schools cannot use "International" in their names. Former international schools are now designated as SPK schools.
- As of 2020, there are 202 SPK schools in DKI Jakarta province
- Nationally, 681 schools have SPK permits

**School Types Researched:**
- International curriculum schools (IB, Cambridge, British, American)
- National-plus schools (Indonesian curriculum with international elements)
- Christian schools (Catholic, Protestant)
- Islamic schools (Al-Azhar network, etc.)
- Specialized schools (Montessori, HighScope, etc.)

#### Step 3: Data Collection

**Schools compiled by category:**

1. **Large International Schools:**
   - Jakarta Intercultural School (JIS)
   - British School Jakarta (BSJ)
   - North Jakarta Intercultural School (NJIS)
   - Australian Independent School (AIS)
   - Singapore Intercultural School (SIS)
   - Gandhi Memorial Intercontinental School (GMIS)

2. **Christian/Catholic Schools:**
   - BPK Penabur network
   - IPEKA Christian School
   - Raffles Christian School
   - Sekolah Pelita Harapan (SPH)
   - Kolese Kanisius
   - Santa Ursula
   - Tarakanita
   - Don Bosco
   - Santa Theresia
   - Regina Pacis

3. **National-Plus/SPK Schools:**
   - Sekolah Cikal
   - HighScope Indonesia
   - Global Sevilla
   - Tunas Muda
   - Mentari Intercultural School
   - Jakarta Multicultural School
   - Sampoerna Academy

4. **Islamic Schools:**
   - Al-Azhar network
   - Madania
   - Embun Pagi Islamic School

5. **Other Notable Schools:**
   - Bina Bangsa School
   - Stella Maris
   - Kinderfield-Highfield
   - Bunda Mulia
   - Sinarmas World Academy
   - Global Jaya School

#### Step 4: Decision-Maker Contact Collection

**Leadership data obtained for:**
- British School Jakarta: Phil Edwards (Interim Principal), Joanne Osman (Head of Primary), Daniel Harbridge (Interim Head of Secondary)
- ACG School Jakarta: Shawn Hutchinson (Principal)
- Jakarta Nanyang School: Mr. Lee Ting Jian (Head of School), various principals
- Jakarta Montessori School: Siti Rohmatun (Principal)
- SPH: Matthew Mann (Executive Director)
- Don Bosco II: L. Asri Indah Nursanti (Principal)

**Challenges encountered:**
- Many school websites don't publicly list leadership names
- Contact forms often preferred over direct email addresses
- Some websites blocked or returned errors (503, SSL issues)

## Final Output

Created `schools.csv` with 102 entries containing:
- School Name
- Website URL
- Persona Name (where available)
- Persona Title
- Contact Details (email/phone)
- Source URL

## Data Quality Notes

- Direct decision-maker names available for ~15% of schools
- Most entries include general school contact (admissions office, school office)
- All schools verified to have active websites
- Contact information sourced from official school websites and aggregator sites

---

## Self-Critique and Revision (v2)

### Issues Identified in v1:

1. **Decision-Maker Data Quality**
   - Most entries labeled "Admissions Office" or "School Office" - these are NOT decision-makers
   - The objective was "Head of English, Curriculum Director, Principal" - v1 only had ~15 actual names
   - Labeling generic contacts as "Persona Name" was misleading

2. **Geographic Scope Creep**
   - Included BSD, Tangerang, Bekasi schools without clarifying they're outside DKI Jakarta
   - Some schools like Sekolah Madania are in Bogor, not Jakarta

3. **Source Currency Concerns**
   - Some aggregator data may be outdated
   - Leadership info from search results not always verified as current

4. **Coverage Gaps**
   - Over-indexed on international/SPK schools
   - Under-represented Indonesian national curriculum private schools
   - Many prominent local private schools (Bakti Mulya, Al-Ikhlas, etc.) missing

5. **Duplicate Inflation**
   - Same school appeared multiple times for different campuses/personnel
   - Inflated the "102 schools" count

### Revisions Made in v2:

1. **Added Region column** - Clarifies if school is in Jakarta proper (Jakarta Selatan, Utara, Barat, Timur, Pusat) or Greater Jakarta (Tangerang, Bekasi, Bogor)

2. **Fixed Persona field** - Left blank when no actual decision-maker name known, rather than misleading "Admissions Office"

3. **Added more national curriculum schools:**
   - SD Islam Al-Ikhlas (with principal name: Syifa Faridah)
   - Sekolah Bakti Mulya 400 (with principal: Eliyani Umas Triyana)
   - Global Islamic School
   - Ananda Islamic School
   - SD Kupu-Kupu
   - Sekolah Al-Izhar
   - Multiple Catholic high schools (Gonzaga, Fons Vitae, Pangudi Luhur, etc.)

4. **Consolidated duplicate entries** - Merged multi-campus entries where appropriate

### Known Limitations (Honest Assessment):

- **Named decision-makers**: Only ~20 schools (~20%) have actual named contacts
- **Currency**: Data current as of November 2025 but school leadership changes frequently
- **Completeness**: This is not an exhaustive list of all 75+ private SMA in Jakarta Selatan alone
- **Website verification**: Not all website URLs verified as currently active
- **Contact accuracy**: Phone numbers and emails not tested for validity
