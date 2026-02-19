# Accessible Tables Summary - Curated Schema Profiling

## Overview

**Total Accessible Tables:** 8 out of 100 analyzed (8% of analyzed, 2% of total schema)  
**Total Rows:** 23,963,691  
**Total Columns:** 252  
**Total Source Systems:** 2 (Clarizen, Ingenious)  
**Geography Data:** Not available in accessible tables

---

## Source System Distribution

| Source System | Total Rows | Percentage | Tables Present |
|--------------|------------|------------|----------------|
| **Clarizen** | 23,925,743 | 99.8% | All 8 tables |
| **Ingenious** | 34,153 | 0.2% | 3 tables |

**Key Findings:**
- Clarizen is the dominant source system, contributing 99.8% of all accessible data
- Ingenious appears in 3 tables with smaller data volumes
- 3 tables contain data from both systems (multi-source integration)

---

## Accessible Tables Detail

### 1. commitment
- **Rows:** 5,768,034 | **Columns:** 55
- **Category:** Financial/Budget Management
- **Source Systems:**
  - Clarizen: 5,764,167 rows (99.9%)
  - Ingenious: 3,999 rows (0.1%)
- **Geography:** Not available

### 2. budgetdetail
- **Rows:** 5,661,644 | **Columns:** 53
- **Category:** Financial/Budget Management
- **Source Systems:**
  - Clarizen: 5,658,501 rows (100%)
- **Geography:** Not available

### 3. budgetchange
- **Rows:** 5,645,852 | **Columns:** 36
- **Category:** Financial/Budget Management
- **Source Systems:**
  - Clarizen: 5,643,301 rows (100%)
- **Geography:** Not available

### 4. budgetforecast
- **Rows:** 5,554,130 | **Columns:** 22
- **Category:** Financial/Budget Management
- **Source Systems:**
  - Clarizen: 5,554,150 rows (100%)
- **Geography:** Not available

### 5. directorycontactprojectlnk
- **Rows:** 1,186,886 | **Columns:** 21
- **Category:** Relationship/Link Table
- **Source Systems:**
  - Clarizen: 1,160,152 rows (97.7%)
  - Ingenious: 27,923 rows (2.3%)
- **Geography:** Not available

### 6. companysourcesystemrelationship
- **Rows:** 68,867 | **Columns:** 9
- **Category:** Metadata/System Integration
- **Source Systems:**
  - Clarizen: 68,872 rows (100%)
- **Geography:** Not available

### 7. customvalue
- **Rows:** 41,719 | **Columns:** 23
- **Category:** Custom Data
- **Source Systems:**
  - Clarizen: 41,723 rows (100%)
- **Geography:** Not available

### 8. costsave
- **Rows:** 36,559 | **Columns:** 33
- **Category:** Financial
- **Source Systems:**
  - Clarizen: 34,877 rows (95.4%)
  - Ingenious: 2,231 rows (4.6%)
- **Geography:** Not available

---

## Summary Statistics

### Data Volume by Category

| Category | Tables | Total Rows | Percentage |
|----------|--------|------------|------------|
| Financial/Budget | 4 | 22,629,660 | 94.4% |
| Relationship/Link | 1 | 1,186,886 | 5.0% |
| Metadata | 1 | 68,867 | 0.3% |
| Custom Data | 1 | 41,719 | 0.2% |
| Financial (Other) | 1 | 36,559 | 0.2% |

### Tables by Row Count Range

| Range | Count | Tables |
|-------|-------|--------|
| 1M+ rows | 5 | commitment, budgetdetail, budgetchange, budgetforecast, directorycontactprojectlnk |
| 10K-100K rows | 3 | companysourcesystemrelationship, customvalue, costsave |

### Multi-Source Tables

Three tables contain data from both Clarizen and Ingenious:

1. **commitment**: 99.9% Clarizen, 0.1% Ingenious
2. **directorycontactprojectlnk**: 97.7% Clarizen, 2.3% Ingenious
3. **costsave**: 95.4% Clarizen, 4.6% Ingenious

---

## Key Insights

1. **Budget/Financial Focus**: 94.4% of accessible data is budget/financial related
2. **Clarizen Dominance**: 99.8% of all rows originate from Clarizen
3. **Ingenious Integration**: Present in 3 tables, primarily for project management data
4. **High Volume Tables**: 5 tables exceed 1M rows, indicating substantial data volumes
5. **No Geography Data**: None of the accessible tables contain explicit country or region columns

---

## Limitations

- **92% of analyzed tables inaccessible** due to permission constraints
- **Geography data not available** in accessible tables
- **Limited scope**: Only 100 of 387 total tables analyzed
- **Column profiling**: Limited to first 10 columns per table for performance

---

## Files Generated

- `CURATED_SCHEMA_PROFILING_REPORT.md` - Detailed profiling report
- `CURATED_SCHEMA_PROFILING_REPORT.json` - JSON export
- `CURATED_PROFILING_ENHANCED.json` - Source system analysis
- `CURATED_PROFILING_OVERVIEW.md` - Comprehensive overview




