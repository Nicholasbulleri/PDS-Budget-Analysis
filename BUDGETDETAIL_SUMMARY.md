# BudgetDetail Analysis - Executive Summary

## Direct Answers to Your Questions

### 1. What are the sources and types?

**Sources:**
- **Clarizen**: 5,659,034 records (99.9% of total)
- **Ingenious**: 3,330 records (0.1% of total)

**Types:**
- Budget types are not clearly defined in a single column
- Budget records are categorized by various amount fields:
  - Approved budgets: 131,253 records (2.3%)
  - Current/Original/Projected: Fields exist but appear unused
- Category data (`categoryname`) appears to be mostly NULL

### 2. How does it relate to projects?

**CRITICAL FINDING**: 
- **Only Ingenious records can be linked to projects** via `projectidentifier`
- **ALL 5.6M Clarizen records have NULL `projectidentifier`** - they cannot be linked to projects using this field
- Only **310 Ingenious projects** have linkable budget data
- This represents **0.004% of all projects** in the system (8.3M total projects)

**Budget Distribution per Project (Ingenious only):**
- Average: 10.74 budget records per project
- Median: 3.00 budget records per project
- Range: 1 to 96 records per project
- 107 projects have 1 record
- 64 projects have 2-5 records
- 37 projects have 6-10 records
- 58 projects have 11-20 records
- 30 projects have 21-50 records
- 14 projects have 51-100 records

### 3. Does every project have a budget?

**No.** 
- Only 310 Ingenious projects (0.004% of all projects) have budget data that can be linked via `projectidentifier`
- 5.6M Clarizen budget records exist but cannot be linked to projects using the standard `projectidentifier` field
- Clarizen budgets may use alternative linking mechanisms (e.g., `workitemidentifier`, `budgetidentifier`)

### 4. Does Clarizen have more budget data than Ingenious?

**Yes, by volume, but with a critical limitation:**

| Metric | Clarizen | Ingenious | Ratio |
|--------|----------|-----------|-------|
| **Total Records** | 5,659,034 | 3,330 | 1,700x more |
| **Records with projectidentifier** | **0** ⚠️ | 3,330 | N/A |
| **Linkable Projects** | 0 | 310 | N/A |
| **Avg Records per Project** | N/A | 10.74 | N/A |
| **Approval Rate** | ~2.3% | 0.0% | N/A |

**Key Insight**: Clarizen has 1,700x more budget records, but **NONE can be linked to projects** using `projectidentifier`. Ingenious has complete project linkage but represents only 0.1% of total budget records.

### 5. Approval Status

**Overall:**
- **2.3% approved** (131,253 records with approved amount > 0)
- **97.7% not approved** (5,529,975 records)

**By Source System:**
- **Clarizen**: ~2.3% approval rate (~131,253 approved out of 5.6M)
- **Ingenious**: **0.0% approval rate** (0 approved out of 3,330)

**Key Finding**: All Ingenious budget records are unapproved. This may indicate:
- Ingenious budgets are in draft/pending status
- Different approval workflow for Ingenious
- Data integration issue

### 6. Patterns and Standout Findings

#### Data Quality Issues:
1. **Extreme Outliers**: Maximum budget amounts are astronomically high ($838 trillion+) - likely data entry errors
2. **High Null Rates**: 
   - 99.4% of records have NULL `budgetitemdescription`
   - 98.3% have NULL `unitofmeasurecode`
   - 97.8% have NULL `perunitcostamount` and `unitcount`
3. **Currency Inconsistencies**: 80+ currency codes with case inconsistencies (USD vs usd, EUR vs eur)
4. **Future Dates**: Some records have dates in 2026 (likely placeholders or data quality issues)

#### Amount Statistics:
- **Median**: $0.00 (most records have zero amounts)
- **Average**: $193M-$227M (heavily skewed by extreme outliers)
- **25th-75th Percentile**: $0.00 - $0.00 (most records are zero)

#### Currency Distribution:
- **USD**: 75.3% of records
- **CAD**: 9.0%
- **EUR**: 2.2%
- **80+ total currencies** indicating global operations

#### Top Projects (Ingenious):
- Top project has 96 budget detail records
- Top 10 projects range from 54-96 records each
- Most top projects show $0.00 for approved and current amounts

## Critical Issues Identified

1. **Project Linkage Gap**: Clarizen budgets cannot be linked to projects - investigate alternative linking fields
2. **Zero Ingenious Approvals**: All Ingenious budgets are unapproved - investigate workflow
3. **Extreme Outliers**: Astronomical budget amounts need data quality review
4. **Low Coverage**: Only 0.004% of projects have linkable budget data
5. **Data Integration**: Clarizen and Ingenious appear to use different data structures

## Recommendations

1. **Immediate**: Investigate how Clarizen budgets link to projects (check `workitemidentifier`, `budgetidentifier`, or other fields)
2. **Data Quality**: Review and clean extreme outliers (>$1B amounts)
3. **Approval Workflow**: Understand why Ingenious has 0% approval rate
4. **Standardization**: Fix currency code inconsistencies
5. **Documentation**: Document the different data structures between Clarizen and Ingenious

---

**Full detailed report**: See `BUDGETDETAIL_ANALYSIS_REPORT.md`
**Analysis data**: See `BUDGETDETAIL_ANALYSIS_ENHANCED.json`
