# Budget Task Name → Category Mapping

This mapping simplifies budget line items (task names / cost codes) into **three categories** for commercial real estate project and construction management reporting.

**Source of task names:** The mapping is built from the **budget Closed query results** (`budget_query_results_curated_closed.csv`) so it covers every task name that appears in that result set (Clarizen Cost Code Item + Ingenious budget). To refresh after re-running the Closed query, run:  
`python3 rebuild_mapping_from_closed_results.py`

## Categories

| Category | Description |
|----------|-------------|
| **FF&E + Millwork** | Furniture, finishings, equipment and millwork; decorative materials; IT/security integrator; POS systems; storage shelving; owner-supplied items. |
| **Soft Costs** | Designer, architect, engineers, expeditor, project management, special inspections, landmark consultant. |
| **Construction** | General contractor and construction trade costs. |

## Files

| File | Use |
|------|-----|
| **budget_taskname_category_mapping.json** | Full mapping + category descriptions. Use in apps or to look up by `taskname`. |
| **budget_taskname_category_mapping.csv** | Same mapping as CSV (`taskname`,`category`) for SQL joins or Excel. |
| **budget_taskname_category_mapping.xlsx** | Same mapping in Excel. |
| **budget_mapping_summary.txt** | Count of task names per category and a sample of **Uncategorized** items for review. |
| **rebuild_mapping_from_closed_results.py** | **Use this** to rebuild the mapping from the latest budget Closed query CSV. Run after re-running the Closed query. |
| **build_taskname_mapping.py** | Builds mapping from `INGENIOUS_BUDGETS_PROJECT_LEVEL.json` (legacy); categorization logic is shared. |

## Using the mapping in SQL

With your core query (e.g. `budget_core_query.sql` or `budget_core_query_closed.sql`), you can roll up by category by joining to the mapping:

- Load the CSV into a table, e.g. `budget_taskname_mapping(taskname, category)`.
- Join: `... FROM ... gt LEFT JOIN budget_taskname_mapping m ON m.taskname = gt.taskname`
- Then `GROUP BY m.category, p.city, p.country, p.sector` (and any other dimensions) to get totals by category.

Example (conceptual):

```sql
SELECT
    COALESCE(m.category, 'Uncategorized') AS category,
    p.city,
    p.country,
    p.sector,
    SUM(COALESCE(NULLIF(p.grossarea, 0), p.usablearea)) AS area,
    SUM(gt.originalbudgetamount) AS total_original_budget,
    SUM(gt.totalprojectedbudgetamount) AS total_projected_budget,
    COUNT(p.id) AS project_count
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
LEFT JOIN budget_taskname_mapping m ON m.taskname = gt.taskname
WHERE ...
GROUP BY COALESCE(m.category, 'Uncategorized'), p.city, p.country, p.sector;
```

## Uncategorized items

Task names that could not be confidently assigned are left as **Uncategorized**. Review `budget_mapping_summary.txt` and, if needed, add overrides in `build_taskname_mapping.py` (or maintain a small override list and apply it when building the JSON/CSV).

## Regenerating the mapping

After updating budget data or rules:

```bash
python3 build_taskname_mapping.py
```

This overwrites the JSON, CSV, and summary from the current contents of `INGENIOUS_BUDGETS_PROJECT_LEVEL.json`.
