# Budget Analysis — Ingenious Project-Level Budgets

**Source:** `INGENIOUS_BUDGETS_PROJECT_LEVEL.json`  
**System:** Ingenious  
**Excluded statuses:** Requested, Cancelled, Draft

---

## 1. Portfolio Overview

| Metric | Value |
|--------|--------|
| **Total projects** | 1,424 |
| **Avg total approved budget (per project)** | $29.7M |
| **Avg original budget (per project)** | $804.2M |
| **Avg total projected budget (per project)** | $81.5M |

*Note: “Original” amounts are much larger than approved/projected in the source data; consider validating units or data quality for original budget.*

---

## 2. Budgets by Project Status

### Counts (projects and budget records)

| Status | Projects | Distinct budgets | Budget records | Avg budgets per project |
|--------|----------|------------------|----------------|-------------------------|
| Initiate | 87 | 88 | 671 | 1.05 |
| Planning/Design | 50 | 51 | 802 | 1.03 |
| Construct | 30 | 34 | 495 | 1.17 |
| Design | 26 | 26 | 198 | 1.00 |
| Closed | 17 | 18 | 174 | 1.29 |
| Closeout | 16 | 19 | 324 | 1.27 |
| Construction | 10 | 12 | 269 | 1.10 |
| Plan | 3 | 3 | 4 | 1.00 |
| Pre-Construction | 2 | 2 | 30 | 1.00 |

### Approved / Original / Projected by status (totals in dataset)

| Status | Project count | Total approved | Total original | Total projected |
|--------|----------------|----------------|----------------|-----------------|
| Design | 238 | $31.2B | $410.5B | $54.9B |
| Initiate | 496 | $1.9B | $188.8B | $11.1B |
| Construct | 228 | $4.0B | $296.3B | $33.3B |
| Planning/Design | 114 | $3.0B | $139.9B | $3.8B |
| Closeout | 78 | $1.6B | $55.6B | $3.4B |
| Closed | 82 | $156.2M | $37.8B | $1.7B |
| Construction | 10 | $328.4M | $12.5B | $333.6M |
| On Hold | 31 | $46.5M | $838.1M | $156.1M |
| Plan | 97 | $55.4M | $2.8B | $7.3B |
| Pre-Construction | 2 | $1.7M | $52.7M | $1.8M |
| Pursuit | 48 | $0 | $0 | $174K |

*Totals above are sums within each status; the same project can appear in only one status in this view.*

---

## 3. Top Budget Line Items (by total cost)

Sample of the largest **budget item descriptions** and their total cost across projects:

| Budget item description | Projects | Total cost | Avg cost |
|-------------------------|----------|------------|----------|
| Construccion | 1 | $23.8B | $23.8B |
| Construcción | 1 | $15.3B | $15.3B |
| Mobiliario | 2 | $6.3B | $3.2B |
| Pisos | 2 | $1.3B | $644.5M |
| Art | 1 | $508.5M | $508.5M |
| Arquitectura | 1 | $474.3M | $474.3M |
| GMP | 1 | $419.3M | $419.3M |
| JLL | 1 | $314.9M | $314.9M |
| Diseño | 1 | $307.0M | $307.0M |
| Furniture | 24 | $282.6M | $11.3M |
| Lighting | 3 | $268.3M | $67.1M |

The file contains **hundreds** of line items; many are small (e.g. &lt;$100). High-cost items are concentrated in construction, furniture, design, and contingency.

---

## 4. Observations

1. **Design and Construct** dominate by total approved and projected amounts and by project count.
2. **Pursuit** has no approved or original budget and only $174K total projected.
3. **Closed** and **On Hold** have relatively low total approved vs. original, consistent with completed or paused work.
4. **Budget line diversity:** Many one-off line items (single project, single budget) and a long tail of very small amounts; consider grouping or roll-up for reporting.
5. **Data quality:** “Original” budget totals are an order of magnitude (or more) above approved and projected in several statuses; worth confirming definitions and currency/units.

---

## 5. Suggested Next Steps

- Validate **original vs. approved vs. projected** definitions and units (e.g. currency, scale).
- Roll up **budget_breakdown_by_item** into categories (e.g. Construction, FF&E, Design, Contingency, PM) for clearer reporting.
- Add **variance** metrics (e.g. projected vs. approved, actual vs. projected) if actuals are available.
- Filter or segment by **region, program, or portfolio** if those dimensions exist in the source system.
