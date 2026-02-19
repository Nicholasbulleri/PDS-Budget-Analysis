#!/usr/bin/env python3
"""
Budget Closed + Summary Dashboard (local visualization).
- Pivot-style view: filter by city/state (including blank), totals by 3 taskname categories,
  total area, $/sqft (PSF). Uses same data as your Excel pivot.
- Summary views: projects missing budgets (by business line), projects missing area.

Run: streamlit run budget_dashboard.py
Requires: pip install streamlit pandas
"""
import os

import pandas as pd
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# File names (relative to script dir)
BUDGET_EXCLUDE = "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.csv"
BUDGET_INCLUDE = "budget_query_results_curated_closed_by_category_with_state_using_mapping.csv"
MISSING_BUDGET = "closed_projects_missing_budget_by_business_line.csv"
MISSING_AREA = "missing_area_summary.csv"


def load_budget(path: str) -> pd.DataFrame:
    p = os.path.join(SCRIPT_DIR, path)
    if not os.path.isfile(p):
        return pd.DataFrame()
    df = pd.read_csv(p)
    for c in ["area", "total_original_budget", "total_projected_budget", "project_count"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_missing_budget() -> pd.DataFrame:
    p = os.path.join(SCRIPT_DIR, MISSING_BUDGET)
    if not os.path.isfile(p):
        return pd.DataFrame()
    return pd.read_csv(p)


def load_missing_area() -> pd.DataFrame:
    p = os.path.join(SCRIPT_DIR, MISSING_AREA)
    if not os.path.isfile(p):
        return pd.DataFrame()
    return pd.read_csv(p)


def main():
    st.set_page_config(page_title="Budget Closed & Summaries", layout="wide")
    st.title("Budget Summary by City/State")
    st.caption("Filter by city/state (including blank). Totals by category, area, $/sqft. Plus missing-budget and missing-area summaries.")

    # Dataset choice
    use_exclude = st.sidebar.radio(
        "Budget dataset",
        ["Exclude projects with no area (recommended)", "Include all (with missing area)"],
        index=0,
    )
    budget_path = BUDGET_EXCLUDE if "Exclude" in use_exclude else BUDGET_INCLUDE
    df = load_budget(budget_path)
    if df.empty:
        st.warning(f"Data file not found: {budget_path}. Run the budget query scripts first.")
        st.stop()

    # Normalize state/city for slicers: treat null/empty as "(Blank)"
    df = df.copy()
    df["state_display"] = df["state"].fillna("(Blank)").replace("", "(Blank)")
    df["city_display"] = df["city"].fillna("(Blank)").replace("", "(Blank)")

    # Slicers (cascading: city list depends on selected state(s)); "(Select All)" option for each
    st.sidebar.subheader("Filters")
    all_states = ["(Blank)"] + sorted([s for s in df["state_display"].dropna().unique() if s != "(Blank)"])
    state_options = ["(Select All)"] + all_states
    selected_states = st.sidebar.multiselect("State", state_options, default=["(Select All)"], help="Use (Select All) or pick specific states. City list updates to cities in selected state(s).")
    states_for_filter = all_states if "(Select All)" in selected_states else [s for s in selected_states if s != "(Select All)"]
    # Cities in selected states only (cascading)
    df_state_filtered = df[df["state_display"].isin(states_for_filter)]
    available_cities = ["(Blank)"] + sorted([c for c in df_state_filtered["city_display"].dropna().unique() if c != "(Blank)"])
    city_options = ["(Select All)"] + available_cities
    selected_cities = st.sidebar.multiselect("City", city_options, default=["(Select All)"], help="Use (Select All) or pick specific cities (only in selected state(s)).")
    cities_for_filter = available_cities if "(Select All)" in selected_cities else [c for c in selected_cities if c != "(Select All)"]

    filtered = df[df["state_display"].isin(states_for_filter) & df["city_display"].isin(cities_for_filter)]

    # KPIs
    total_budget = filtered["total_original_budget"].sum()
    total_proj_budget = filtered["total_projected_budget"].sum()
    total_area = filtered["area"].sum()
    total_projects = filtered["project_count"].sum()
    psf = (total_proj_budget / total_area) if total_area and total_area > 0 else None

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total original budget", f"${total_budget/1e9:.2f}B" if total_budget >= 1e9 else f"${total_budget/1e6:.2f}M")
    col2.metric("Total projected budget", f"${total_proj_budget/1e9:.2f}B" if total_proj_budget >= 1e9 else f"${total_proj_budget/1e6:.2f}M")
    col3.metric("Total area (sq ft)", f"{total_area/1e6:.2f}M" if total_area >= 1e6 else f"{total_area:,.0f}")
    col4.metric("Project count", f"{total_projects:,.0f}")
    col5.metric("Total Projected Budget/SQFT", f"${psf:,.2f}" if psf is not None else "—")

    # By taskname (3 categories)
    st.subheader("Totals by Category")
    by_cat = (
        filtered.groupby("taskname", dropna=False)
        .agg(
            total_original_budget=("total_original_budget", "sum"),
            total_projected_budget=("total_projected_budget", "sum"),
            area=("area", "sum"),
            project_count=("project_count", "sum"),
        )
        .reset_index()
    )
    by_cat["psf"] = by_cat.apply(
        lambda r: r["total_projected_budget"] / r["area"] if r["area"] and r["area"] > 0 else None,
        axis=1,
    )
    # Grand totals (sums; last column = grand total projected budget / grand total area)
    gt_orig = by_cat["total_original_budget"].sum()
    gt_proj = by_cat["total_projected_budget"].sum()
    gt_area = by_cat["area"].sum()
    gt_count = by_cat["project_count"].sum()
    gt_psf = (gt_proj / gt_area) if gt_area and gt_area > 0 else None
    # Display table: headers and formatted columns + grand total row
    display_df = pd.DataFrame({
        "Cost type": list(by_cat["taskname"]) + ["Grand Total"],
        "Total Orig Budget": list(by_cat["total_original_budget"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")) + [f"${gt_orig:,.0f}"],
        "Total Projected Budget": list(by_cat["total_projected_budget"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")) + [f"${gt_proj:,.0f}"],
        "Total Area": list(by_cat["area"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")) + [f"{gt_area:,.0f}"],
        "Project Count": list(by_cat["project_count"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")) + [f"{gt_count:,.0f}"],
        "Total Projected Budget/SQFT": list(by_cat["psf"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) and x is not None else "")) + [f"${gt_psf:,.2f}" if gt_psf is not None else ""],
    })
    # Highlight Grand Total row with light gray (similar to table header)
    styled = display_df.style.apply(
        lambda s: ["background-color: #e8e8e8"] * len(s) if s.name == len(display_df) - 1 else [""] * len(s),
        axis=1,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Bar chart by category (half width)
    chart_col, _ = st.columns([1, 1])
    with chart_col:
        st.bar_chart(by_cat.set_index("taskname")[["total_original_budget", "total_projected_budget"]], height=350)

    # --- Summary: projects missing budget ---
    st.divider()
    st.subheader("Projects missing budget (closed USD, no positive budget in generictask)")
    mb_df = load_missing_budget()
    if not mb_df.empty:
        total_row = mb_df[mb_df["business_line"] == "(Total)"]
        total_missing = int(total_row["closed_projects_missing_budget"].iloc[0]) if len(total_row) else int(mb_df["closed_projects_missing_budget"].sum())
        st.metric("Closed projects missing budget", f"{int(total_missing):,}")
        mb_display = mb_df[mb_df["business_line"] != "(Total)"].copy()
        if not mb_display.empty:
            st.bar_chart(mb_display.set_index("business_line")["closed_projects_missing_budget"], height=280)
            st.dataframe(mb_df, use_container_width=True, hide_index=True)
    else:
        st.info("Run closed_projects_missing_budget_by_business_line to generate this data.")

    # --- Summary: projects missing area ---
    st.divider()
    st.subheader("Projects with budget but missing/zero area")
    ma_df = load_missing_area()
    if not ma_df.empty:
        d = ma_df.set_index("metric")["value"].to_dict()
        proj_missing = int(d.get("Distinct projects with budget but MISSING/ZERO area", 0))
        proj_any = int(d.get("Distinct projects with budget (any area)", 0))
        proj_with_area = int(d.get("Distinct projects with budget AND positive area", 0))
        st.metric("Projects with budget but no area", f"{proj_missing:,}")
        c1, c2, c3 = st.columns(3)
        c1.metric("With budget (any area)", f"{proj_any:,}")
        c2.metric("With budget + positive area", f"{proj_with_area:,}")
        c3.metric("Missing/zero area", f"{proj_missing:,}")
        st.caption("Source: missing_area_summary.csv. Run summary_missing_area_projects.py to refresh.")
    else:
        st.info("Add missing_area_summary.csv (or run summary_missing_area_projects.py) for this section.")

    st.sidebar.caption("Data: budget closed by category + state mapping (CSV in project folder).")


if __name__ == "__main__":
    main()
