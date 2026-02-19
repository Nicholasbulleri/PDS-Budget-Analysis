# Budget Dashboard (local app)

A **Streamlit** dashboard that replicates your Excel pivot (filter by city/state, totals by 3 taskname categories, area, $/sqft) and adds visualizations for the **missing budget** and **missing area** summaries.

## Run the dashboard

From the project directory:

```bash
pip install streamlit pandas   # if not already installed
streamlit run budget_dashboard.py
```

Your browser will open to the app (usually http://localhost:8501).

## What it does

1. **Budget pivot view**
   - **Dataset:** Choose “Exclude projects with no area” (default) or “Include all (with missing area)”.
   - **Slicers:** State and City (multiselect). Include “(Blank)” to keep rows with no state or city.
   - **KPIs:** Total original budget, total projected budget, total area, project count, **$/sqft** (original budget ÷ area).
   - **Table:** Totals by taskname (Construction, FF&E + Millwork, Soft Costs) with total_original_budget, total_projected_budget, area, project_count, $/sqft.
   - **Chart:** Bar chart of original vs projected budget by category.

2. **Projects missing budget**
   - Total closed USD projects missing budget (5,132).
   - Bar chart and table by business line (from `closed_projects_missing_budget_by_business_line.csv`).

3. **Projects missing area**
   - Projects with budget but missing/zero area (31,947), and comparison counts (from `missing_area_summary.csv`).

## Data files used

| File | Purpose |
|------|--------|
| `budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.csv` | Default budget dataset (with area only). |
| `budget_query_results_curated_closed_by_category_with_state_using_mapping.csv` | Optional: include missing area. |
| `closed_projects_missing_budget_by_business_line.csv` | Missing-budget by business line. |
| `missing_area_summary.csv` | Missing-area project/row summary. |

Generate/refresh these with your existing scripts; the dashboard only reads the CSVs.

## No BI server needed

Everything runs locally. No Power BI / Tableau / database required. To share, run the script and share the URL (or use Streamlit Cloud if you host it).
