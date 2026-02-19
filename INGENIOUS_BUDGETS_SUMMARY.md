# Ingenious Projects with Budgets - Analysis Summary

## Direct Answers to Your Questions

### 1. Budget Analysis by Project Status (Excluding Requested, Cancelled, Draft)

**Total Projects Analyzed**: 291 projects with budgets  
**Total Budget Amount**: $56.7 billion  
**Average Budget per Project**: $195.0 million

| Project Status | Projects | Budget Records | Avg Budget per Project | Total Budget Amount |
|----------------|----------|----------------|------------------------|---------------------|
| **Design** | 31 | 261 | **$1,571.4M** | $48.7B |
| **Closed** | 19 | 160 | **$128.6M** | $2.4B |
| **Construct** | 30 | 555 | **$77.1M** | $2.3B |
| **Closeout** | 20 | 301 | **$74.7M** | $1.5B |
| **Construction** | 9 | 241 | **$28.9M** | $260.0M |
| **Planning/Design** | 47 | 706 | **$18.7M** | $879.4M |
| **Initiate** | 98 | 588 | **$6.5M** | $640.0M |
| **Pre-Construction** | 2 | 30 | **$889K** | $1.8M |
| **Plan** | 35 | 36 | **$1.8K** | $64.2K |

**Key Findings:**
- **Design phase** has the highest average budget per project ($1.57B) and represents 85.8% of total budget amount
- **Closed projects** have the second-highest average ($128.6M per project)
- **Initiate phase** has the most projects (98) but lower average budgets ($6.5M per project)
- **Plan phase** has minimal budgets ($1.8K average per project)

---

### 2. Average Budget Amounts per Project

**Overall Statistics:**
- **Total Projects with Budgets**: 291
- **Total Budget Records**: 2,878
- **Total Budget Amount**: $56,746,594,217.93
- **Average Budget per Project**: **$195,005,478.41**
- **Average Budget per Record**: $19,717,371.17

**Note**: Only projects that have budgets are included in this analysis. Projects without budgets are excluded.

---

### 3. Budget Breakdown by Categories/Codes

**⚠️ Important Finding**: 

Category and code fields are **NOT populated** for Ingenious budget records:
- `categoryname`: NULL for all 2,937 records with budget amounts
- `code`: NULL for all 2,937 records with budget amounts  
- `codename`: NULL for all 2,937 records with budget amounts
- `budgetitemname`: NULL for all 2,937 records with budget amounts

**Alternative Grouping Available:**
- **budgetidentifier**: Available for all records (can group by budget)
- **workitemidentifier**: Available for all records (can group by work item)

**Recommendation**: If category/code breakdown is needed, you may need to:
1. Link to other tables that contain category/code information
2. Use `budgetidentifier` or `workitemidentifier` as alternative grouping fields
3. Check if category/code data exists in source system tables

---

## Additional Insights

### Budget Distribution by Status

1. **Design Phase Dominance**: 
   - 31 projects in Design phase account for $48.7B (85.8% of total)
   - Average of $1.57B per project in Design phase
   - This suggests large-scale design projects with significant budgets

2. **Active Construction Phases**:
   - Construct: 30 projects, $2.3B total, $77.1M average
   - Construction: 9 projects, $260M total, $28.9M average
   - Closeout: 20 projects, $1.5B total, $74.7M average

3. **Planning Phases**:
   - Planning/Design: 47 projects, $879M total, $18.7M average
   - Initiate: 98 projects, $640M total, $6.5M average
   - Plan: 35 projects, $64K total, $1.8K average (very minimal)

4. **Completed Projects**:
   - Closed: 19 projects, $2.4B total, $128.6M average
   - These represent completed projects with final budget totals

### Data Quality Notes

- **Approved amounts are all zero**: All Ingenious budget records have `totalapprovedbudgetamount = 0`
- **Cost amounts are populated**: Using `totalbudgetcostamount` for analysis (2,937 records have values > 0)
- **Category/Code data missing**: No category or code information available in budgetdetail table for Ingenious

---

## Files Generated

1. **INGENIOUS_BUDGETS_FINAL.json** - Complete analysis data in JSON format
2. **INGENIOUS_BUDGETS_REPORT.md** - Detailed markdown report
3. **INGENIOUS_BUDGETS_SUMMARY.md** - This summary document

---

**Analysis Date**: Current  
**Source System**: Ingenious  
**Excluded Statuses**: requested, cancelled, draft  
**Amount Field Used**: totalbudgetcostamount
