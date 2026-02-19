# BudgetDetail Table - Comprehensive Data Profiling & Analysis Report

## Executive Summary

This report provides a comprehensive analysis of the `budgetdetail` table in the `work_dynamics.curated` schema, examining data sources, relationships to projects, approval status, and key patterns.

**Key Findings:**
- **Total Records**: 5,662,364 budget detail records
- **Source Systems**: Primarily Clarizen (99.9%) with a small Ingenious component (0.1%)
- **Projects with Budgets**: 310 projects have budget data
- **Approval Status**: Only 2.3% of records have approved amounts > 0
- **Data Quality**: Significant data quality issues including extreme outliers and high null rates

---

## 1. Data Overview

### Table Structure
- **Table Name**: `budgetdetail`
- **Schema**: `work_dynamics.curated`
- **Total Rows**: 5,662,364
- **Total Columns**: 51

### Key Columns
- `projectidentifier` - Links to project table
- `budgetidentifier` - Unique budget identifier
- `sourcesystem` - Source system (Clarizen/Ingenious)
- `totalapprovedbudgetamount` - Approved budget amount
- `totalbudgetcurrentamount` - Current budget amount
- `totalbudgetoriginalamount` - Original budget amount
- `totalbudgetcostamount` - Total budget cost
- `categoryname` - Budget category
- `currencytypecode` - Currency type

---

## 2. Source System Analysis

### Source System Distribution

| Source System | Budget Records | % of Total | Distinct Budgets | Projects with projectidentifier | Avg Records/Project |
|--------------|---------------|------------|------------------|--------------------------------|---------------------|
| **Clarizen** | 5,659,034 | 99.9% | ~5.6M | **0** ⚠️ | N/A |
| **Ingenious** | 3,330 | 0.1% | 323 | 310 | 10.74 |

**⚠️ CRITICAL FINDING**: All 5,659,034 Clarizen records have NULL `projectidentifier`. This means:
- Clarizen budget records **cannot be linked to projects** using the `projectidentifier` field
- Only Ingenious records (3,330) can be linked to projects
- This is a significant data quality/integration issue

### Key Insights:
- **Clarizen dominates by volume**: 99.9% of all budget records come from Clarizen (5.6M records)
- **Clarizen lacks project linkage**: None of the Clarizen records have `projectidentifier` populated
- **Ingenious has complete project linkage**: All 3,330 Ingenious records can be linked to 310 projects
- **Ingenious has higher detail per project**: Ingenious projects average 10.74 budget records per project
- **Data integration gap**: Clarizen and Ingenious budget data are structured differently

### Answer to Question: "Does Clarizen have more budget data than Ingenious?"
**Yes, by volume (1,700x more records), but with a critical limitation:**
- Clarizen has **5,659,034 budget records** vs Ingenious' **3,330 records**
- However, **ALL Clarizen records lack projectidentifier**, so they cannot be linked to projects
- Only Ingenious records (3,330) can be analyzed in relation to projects
- This suggests Clarizen budget data may use a different linking mechanism or is structured differently

---

## 3. Project Relationship Analysis

### Budget Coverage

| Metric | Value |
|--------|-------|
| Projects with budget data (Ingenious only) | 310 |
| Total projects in system | 8,268,968 (distinct by id) |
| Budget coverage (Ingenious) | 0.004% |
| Clarizen budget records with project linkage | 0 (0%) |

**Critical Finding**: 
- **Only Ingenious budget records can be linked to projects** via `projectidentifier`
- All 5.6M Clarizen records have NULL `projectidentifier`, so they cannot be linked using this field
- This means only 310 Ingenious projects (0.004% of all projects) have linkable budget data
- Clarizen budget data may use alternative linking mechanisms (e.g., `workitemidentifier`, `budgetidentifier`, or other fields)

**Note**: The project table contains 8.3M distinct project records (by id). This may include:
- Historical projects
- Projects from multiple source systems
- Different project types or statuses
- Projects without active budgets

### Budget Distribution per Project

| Budget Records per Project | Number of Projects |
|----------------------------|-------------------|
| 1 record | 107 projects |
| 2-5 records | 64 projects |
| 6-10 records | 37 projects |
| 11-20 records | 58 projects |
| 21-50 records | 30 projects |
| 51-100 records | 14 projects |

**Statistics:**
- **Average**: 10.74 budget records per project
- **Median**: 3.00 budget records per project
- **Range**: 1 to 96 records per project

### Answer to Question: "Does every project have a budget?"
**No.** Only 310 Ingenious projects have budget data that can be linked via `projectidentifier`. 

**Important Caveat**: 
- 5.6M Clarizen budget records exist but cannot be linked to projects using `projectidentifier`
- Clarizen budgets may be linked via other fields (e.g., `workitemidentifier`, `budgetidentifier`)
- Further investigation needed to understand how Clarizen budgets relate to projects

---

## 4. Approval Status Analysis

### Approval Status Breakdown

| Status | Count | Percentage |
|--------|-------|-------------|
| Records with approved amount field populated | 5,328,674 | 94.1% |
| Records with approved amount > 0 | 131,253 | **2.3%** |
| Records without approved amount (NULL or 0) | 5,529,975 | **97.7%** |

### Approval Status by Source System

| Source System | Total Records | Approved (>0) | Not Approved | Approval Rate |
|--------------|---------------|---------------|---------------|---------------|
| **Clarizen** | 5,659,034 | ~131,253* | ~5,527,781* | ~2.3% |
| **Ingenious** | 3,330 | 0 | 3,330 | **0.0%** |

*Note: Approval data for Clarizen estimated based on overall percentages. Ingenious has **0 approved budgets** (all 3,330 records have approved amount = 0 or NULL).

### Key Findings:
- **Only 2.3% of budget records have approved amounts greater than zero**
- 94.1% of records have the `totalapprovedbudgetamount` field populated, but most are zero
- This suggests most budgets are either:
  - Not yet approved
  - Pending approval
  - Have zero approved amounts

### Budget Status Types:
- **Approved budgets**: 131,253 records (2.3%)
- **Current budgets**: 0 records (0.0%) - field appears unused
- **Original budgets**: 0 records (0.0%) - field appears unused
- **Projected budgets**: 0 records (0.0%) - field appears unused

---

## 5. Budget Amount Analysis

### Amount Statistics

#### Total Approved Budget Amount
- **Records with value**: 5,328,674 (94.1%)
- **Records with amount > 0**: 131,253 (2.3%)
- **Min**: -$666,322,491.42 (negative value indicates adjustment)
- **Max**: $838,177,134,761,521.00 (extreme outlier - likely data quality issue)
- **Average**: $193,641,298.86 (skewed by outliers)
- **Median**: $0.00
- **Total**: $1,031,851,354,565,403.25

#### Total Budget Cost Amount
- **Records with value**: 4,541,737 (80.2%)
- **Min**: -$666,322,491.42
- **Max**: $838,177,134,761,521.00 (extreme outlier)
- **Average**: $227,206,385.02 (skewed by outliers)
- **Median**: $0.00
- **Total**: $1,031,911,645,476,210.25

### Data Quality Issues:
1. **Extreme Outliers**: Maximum values are astronomically high (likely data entry errors)
2. **High Zero/Null Rates**: Median is $0.00, suggesting most records have no amount
3. **Negative Values**: Some records have negative amounts (likely adjustments or reversals)
4. **Skewed Distributions**: Average is much higher than median due to outliers

---

## 6. Currency Analysis

### Currency Distribution

**Top 10 Currencies:**

| Currency | Records | % of Total |
|----------|----------|------------|
| USD | 4,262,962 | 75.3% |
| CAD | 512,379 | 9.0% |
| EUR | 125,705 | 2.2% |
| AUD | 85,950 | 1.5% |
| INR | 68,862 | 1.2% |
| CNY | 53,815 | 0.9% |
| SGD | 28,363 | 0.5% |
| GBP | 25,170 | 0.4% |
| HKD | 21,303 | 0.4% |
| KRW | 12,603 | 0.2% |

**Total Currencies**: 80+ different currency codes identified

### Key Insights:
- **USD dominates**: 75.3% of all records are in USD
- **Global presence**: 80+ currencies indicate international operations
- **Data quality**: Some inconsistent currency codes (e.g., "cop" vs "COP", "eur" vs "EUR")

---

## 7. Pattern & Anomaly Analysis

### Key Patterns Identified:

1. **High Null Rates**:
   - `budgetitemdescription`: 99.4% null
   - `unitofmeasurecode`: 98.3% null
   - `perunitcostamount`: 97.8% null
   - `unitcount`: 97.8% null

2. **Date Ranges**:
   - **Currency Exchange Rate Timestamp**: 2018-03-28 to 2026-01-15 (2,426 distinct dates)
   - **Source Modified Date**: 2018-11-14 to 2026-01-15 (2,421 distinct dates)
   - **Source Created Date**: 2018-11-14 to 2026-01-15 (2,395 distinct dates)
   - **Note**: Future dates (2026) suggest data quality issues or placeholder dates

3. **Budget Variance**:
   - Analysis attempted but variance field appears to have limited data
   - Most records have NULL variance values

4. **Top Projects by Budget Records**:
   - Top project has 96 budget detail records
   - Top 10 projects range from 54-96 records each
   - Most top projects show $0.00 for approved and current amounts

---

## 8. Recommendations

### Data Quality Improvements:
1. **Investigate extreme outliers**: Review records with amounts > $1 billion
2. **Standardize currency codes**: Fix case inconsistencies (USD vs usd)
3. **Validate future dates**: Review records with dates in 2026
4. **Address high null rates**: Determine if nulls are expected or data quality issues

### Business Insights:
1. **Low approval rate**: Only 2.3% of budgets are approved - investigate approval workflow
2. **Zero Ingenious approvals**: All 3,330 Ingenious budget records are unapproved (0% approval rate)
3. **Critical data linkage issue**: Clarizen budgets cannot be linked to projects via `projectidentifier` - investigate alternative linking mechanisms
4. **Limited project coverage**: Only 310 Ingenious projects have linkable budget data - investigate why coverage is so low
5. **Source system disparity**: Clarizen has 1,700x more records but cannot be linked to projects; Ingenious has complete project linkage but 0% approval rate
6. **Currency diversity**: 80+ currencies indicate global operations - ensure proper currency conversion

### Analysis Enhancements:
1. **Investigate Clarizen project linkage**: Determine how Clarizen budgets link to projects (check `workitemidentifier`, `budgetidentifier`, or other fields)
2. **Link to project table**: Verify project count and relationship accuracy for Ingenious
3. **Time series analysis**: Analyze budget trends over time
4. **Category analysis**: Investigate why category data appears limited
5. **Work item analysis**: Explore relationship between budgets and work items (may be key for Clarizen linkage)
6. **Approval workflow investigation**: Understand why Ingenious has 0% approval rate vs Clarizen's 2.3%

---

## 9. Data Dictionary Reference

### Key Amount Fields:
- `totalbudgetcostamount`: Total cost amount for the budget item
- `totalapprovedbudgetamount`: Approved budget amount
- `totalpendingamount`: Pending budget amount
- `totalbudgetoriginalamount`: Original budget amount
- `totalbudgetcurrentamount`: Current budget amount
- `totalbudgetprojectedamount`: Projected budget amount
- `variancetothebudgetamount`: Variance from budget
- `paidamount`: Amount paid
- `unpaidamount`: Amount unpaid

### Key Identifier Fields:
- `id`: Primary key
- `sourcebudgetdetailidentifier`: Source system identifier
- `projectidentifier`: Links to project table
- `budgetidentifier`: Links to budget table
- `workitemidentifier`: Links to work item table

---

## 10. Conclusion

The `budgetdetail` table contains 5.6M+ records primarily from Clarizen, with critical findings:

- **Source dominance**: Clarizen provides 99.9% of records (5.6M)
- **Critical linkage issue**: ALL Clarizen records lack `projectidentifier` - cannot link to projects
- **Ingenious linkage**: Only 310 Ingenious projects have linkable budget data (0.004% of all projects)
- **Low approval rate**: Only 2.3% of budgets are approved (all from Clarizen; Ingenious has 0% approval)
- **Data quality concerns**: Extreme outliers, high null rates, inconsistent currency codes, and missing project linkages

**Priority Actions:**
1. Investigate how Clarizen budgets link to projects (alternative fields or mechanisms)
2. Understand why Ingenious has 0% approval rate
3. Address data quality issues (outliers, nulls, currency standardization)
4. Determine if project coverage is truly 0.004% or if Clarizen uses different linking

Further investigation is critical to understand the data integration architecture and business processes.

---

**Report Generated**: Analysis based on data profiling queries
**Data Source**: `work_dynamics.curated.budgetdetail`
**Analysis Date**: Current
