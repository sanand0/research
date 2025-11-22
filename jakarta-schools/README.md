# Jakarta Private Schools Research

## Overview

Spreadsheet of ~105 private K-12 educational institutions in Jakarta and Greater Jakarta, Indonesia, with decision-maker contact information where available.

## Output

**Main deliverable:** `schools.csv`

### CSV Columns:
- **School Name** - Official name of the institution
- **Website URL** - School's official website
- **Persona Name** - Name of decision-maker (blank if unknown)
- **Persona Title** - Position/title (Principal, Head of School, etc.)
- **Contact Details** - Email and/or phone number
- **Region** - Geographic location (Jakarta Selatan/Utara/Barat/Timur/Pusat or Greater Jakarta areas)
- **Source URL** - Where the information was obtained

## Key Statistics

| Metric | Count |
|--------|-------|
| Total entries | 105 |
| Unique schools | ~85 (some have multiple personnel entries) |
| Named decision-makers | ~20 (19%) |
| Jakarta proper (DKI Jakarta) | ~65 schools |
| Greater Jakarta (Tangerang, Bekasi, Bogor) | ~20 schools |

## Named Decision-Makers Found

| School | Name | Position |
|--------|------|----------|
| British School Jakarta | Phil Edwards | Interim Principal |
| British School Jakarta | Joanne Osman | Head of Primary |
| British School Jakarta | Daniel Harbridge | Interim Head of Secondary |
| ACG School Jakarta | Shawn Hutchinson | Principal |
| Jakarta Nanyang School | Mr. Lee Ting Jian | Head of School |
| Jakarta Nanyang School | Ms. Diah Ayu Putri Purbawati | Kindergarten Principal |
| Jakarta Nanyang School | Mr. Anjar Donny Prasetyo | Primary School Principal |
| Jakarta Nanyang School | Ms. Eliana Maria Setiawati | Secondary School Principal |
| Jakarta Montessori School | Siti Rohmatun | Principal |
| SPH | Matthew Mann | Executive Director |
| SMA Don Bosco II | L. Asri Indah Nursanti | Principal |
| BPK Penabur SDK 6 | Merinda S.E. M.Pd. | Principal |
| Sekolah Bakti Mulya 400 | Eliyani Umas Triyana | Principal SD |
| SD Islam Al-Ikhlas | Syifa Faridah | Principal |
| Jakarta Intercultural School | Edward Wexler | High School Principal |

## School Categories

| Category | Count | Examples |
|----------|-------|----------|
| International/SPK Schools | ~30 | JIS, BSJ, NJIS, SIS, GMIS |
| Christian Schools | ~35 | BPK Penabur, IPEKA, SPH, Kanisius, Santa Ursula |
| Islamic Schools | ~15 | Al-Azhar, GIS, Ananda, Madina, Embun Pagi |
| National-Plus Schools | ~20 | Cikal, HighScope, Sampoerna Academy |
| Other Private Schools | ~5 | Bunda Mulia, Pahoa |

## Self-Critique and Limitations

### Data Quality Issues:
1. **Decision-maker coverage is limited** - Only ~20% of schools have named contacts. The objective asked for "Head of English, Curriculum Director, Principal" but most entries only have general contact info.

2. **Geographic scope varies** - Dataset includes both DKI Jakarta proper and Greater Jakarta (Jabodetabek). The Region column now clarifies this.

3. **Source currency** - Data compiled November 2025 from web searches. School leadership changes frequently; some information may be outdated.

4. **Not exhaustive** - Jakarta Selatan alone has 75+ private SMA with A-accreditation. This dataset represents a sample of notable schools, not a complete census.

### What Would Improve This:
- Direct outreach to schools to verify current leadership
- LinkedIn research for curriculum coordinators
- Access to NOW! Jakarta's downloadable school directory
- Government NPSN database for complete listings

## Data Sources

### Primary Sources
1. **School websites** - Official contact and leadership pages
2. **expat.or.id** - Expatriate school directory
3. **international-schools-database.com** - School profiles

### Secondary Sources
4. **Indonesian news sites** (Kompas, Tirto, Media Indonesia) - School rankings
5. **spkindonesia.org** - SPK school association
6. **referensi.data.kemdikbud.go.id** - Ministry of Education database

## Regulatory Context

Since 2014/2015, Indonesian government regulations prohibit schools from using "International" in their names unless embassy-run. Former international schools are now designated as **SPK (Satuan Pendidikan Kerjasama)** - Collaborative Education Units.

As of 2020: 202 SPK schools in DKI Jakarta province.

## Files

- `README.md` - This report
- `notes.md` - Detailed research notes and methodology
- `schools.csv` - Main output (105 entries)
