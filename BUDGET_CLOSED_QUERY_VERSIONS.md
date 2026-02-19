# Budget Closed Query Versions (by category + state using mapping)

Both versions use the **same** category logic and **external** city→state mapping (JSON/Excel/CSV).  
State is applied in Python after the query; the SQL runs without the large inline city lookup.

---

## 1. Includes projects with missing area

- **Script:** `run_budget_query_closed_by_category_with_state_using_mapping.py`
- **SQL:** `budget_core_query_closed_by_category.sql`
- **Output:**  
  `budget_query_results_curated_closed_by_category_with_state_using_mapping.csv`  
  `budget_query_results_curated_closed_by_category_with_state_using_mapping.xlsx`

**Context:** This analysis **includes** all closed USD projects with budget in generictask, including those with **missing or zero area** (both `grossarea` and `usablearea` NULL or 0). The `area` column in the result may be NULL or 0 for some rows.

---

## 2. Excludes projects with no positive area

- **Script:** `run_budget_query_closed_by_category_with_state_using_mapping_exclude_missing_area.py`
- **SQL:** `budget_core_query_closed_by_category_exclude_missing_area.sql`
- **Output:**  
  `budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.csv`  
  `budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.xlsx`

**Context:** This analysis **excludes** projects where both area columns are missing or zero. Only projects with at least one positive area value (`COALESCE(NULLIF(grossarea, 0), usablearea) > 0`) are included.

---

## Area logic (curated.project)

- **Area** in the query: `COALESCE(NULLIF(p.grossarea, 0), p.usablearea)`  
- **Include version:** no filter on area.  
- **Exclude version:** filter `AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0` in the base CTE.

---

## Summary: projects with budget but missing/zero area

(From `summary_missing_area_projects.py`; run it to refresh.)

| Metric | Count |
|--------|-------|
| **Distinct projects with budget (any area)** | 50,166 |
| **Distinct projects with budget AND positive area** | 18,219 |
| **Distinct projects with budget but MISSING/ZERO area** | **31,947** |

| Output (aggregated rows) | Rows |
|--------------------------|------|
| Include missing area | 9,686 |
| Exclude missing area | 6,621 |
| Row difference | 3,065 |

So **31,947** closed USD projects have budget in generictask but both `grossarea` and `usablearea` are NULL or 0. The row difference (3,065) is the number of aggregated result rows that drop out when excluding those projects; it is not a project count because each row is a category × city × country × sector group.
