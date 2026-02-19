# Ingenious Projects with Budgets - Analysis Report

## Summary

**Analysis Date**: current  
**Source System**: ingenious  
**Excluded Statuses**: requested, cancelled, draft  
**Amount Field Used**: totalbudgetcostamount

### Overall Statistics

- **Total Projects with Budgets**: 291
- **Total Budget Records**: 2,878
- **Total Budget Amount**: $56,746,594,217.93
- **Average Budget per Project**: $195,005,478.41
- **Average Budget per Record**: $19,717,371.17

---

## Budget Analysis by Project Status

| Status | Projects | Budget Records | Avg per Record | Total Cost | Avg per Project |
|--------|----------|---------------|----------------|------------|-----------------|
| Initiate | 98 | 588 | $1,088,373.13 | $639,963,401.67 | $6,530,238.79 |
| Planning/Design | 47 | 706 | $1,245,544.65 | $879,354,524.75 | $18,709,670.74 |
| Plan | 35 | 36 | $1,784.31 | $64,235.18 | $1,835.29 |
| Design | 31 | 261 | $186,642,772.59 | $48,713,763,644.99 | $1,571,411,730.48 |
| Construct | 30 | 555 | $4,168,305.40 | $2,313,409,499.09 | $77,113,649.97 |
| Closeout | 20 | 301 | $4,963,882.80 | $1,494,128,721.74 | $74,706,436.09 |
| Closed | 19 | 160 | $15,276,035.78 | $2,444,165,724.71 | $128,640,301.30 |
| Construction | 9 | 241 | $1,078,696.24 | $259,965,793.80 | $28,885,088.20 |
| Pre-Construction | 2 | 30 | $59,289.07 | $1,778,672.00 | $889,336.00 |

---

## Budget Breakdown by Category

**Note**: Category data (`categoryname`) is not populated for Ingenious budget records. All 2,937 records with budget amounts have NULL category values.

---

## Budget Breakdown by Code

**Note**: Code data (`code`, `codename`) is not populated for Ingenious budget records. All 2,937 records with budget amounts have NULL code values.

### Alternative Grouping Available

While category and code fields are not available, Ingenious budget records do have:
- **budgetidentifier**: Available for all 2,937 records (can be used to group by budget)
- **workitemidentifier**: Available for all 2,937 records (can be used to group by work item)

---

*Report generated from INGENIOUS_BUDGETS_FINAL.json*
