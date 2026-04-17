#!/usr/bin/env python3
"""
Budget Closed + Summary Dashboard (local visualization).
- Pivot-style view: filter by city/state (including blank), totals by 3 taskname categories,
  total area, $/sqft (PSF). Uses same data as your Excel pivot.
- Summary views: projects missing budgets (by business line), projects missing area.

Run from project root: streamlit run Python/apps/budget_dashboard.py  OR  python budget_dashboard.py
Requires: pip install streamlit pandas
"""
import json
import os

import altair as alt
import pandas as pd
import streamlit as st

import sys
from pathlib import Path

for _p in Path(__file__).resolve().parents:
    if (_p / "repo_paths.py").is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break
else:
    raise RuntimeError("Not inside project Python tree")
from repo_paths import repo_root

PROJECT_ROOT = repo_root()
DATA_BUDGET = os.path.join(PROJECT_ROOT, "data", "budget")
DATA_PROJECTS = os.path.join(PROJECT_ROOT, "data", "projects")
DATA_QUALITY = os.path.join(PROJECT_ROOT, "data", "quality")
SECTOR_MAPPING_FILE = os.path.join(PROJECT_ROOT, "data", "sector", "sector_mapping.json")
CANONICAL_SECTOR_ORDER = [
    "Office", "Retail", "Industrial and Logistics", "Data Center", "Hotels/Hospitality",
    "Residential", "Education", "Mixed-use", "Infrastructure/Energy", "Special Purpose Facility",
]

# File names (relative to script dir)
BUDGET_SECTOR_PROJECT_TYPE = "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area_with_property_sector_and_project_type.csv"
BUDGET_EXCLUDE = "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.csv"
BUDGET_INCLUDE = "budget_query_results_curated_closed_by_category_with_state_using_mapping.csv"
MISSING_BUDGET = "closed_projects_missing_budget_by_business_line.csv"
MISSING_BUDGET_BY_SOURCE = "closed_projects_missing_budget_by_source.csv"
MISSING_BUDGET_ALL_PHASES = "projects_missing_budget_by_source_all_phases.csv"
MISSING_AREA = "missing_area_summary.csv"
PROJECTS_BUDGET_AREA = "projects_closed_usd_with_budget_and_area.csv"
DATA_QUALITY_MISSING_AREA_BY_SOURCE = "data_quality_missing_area_by_source.csv"


def load_budget(path: str) -> pd.DataFrame:
    p = os.path.join(DATA_BUDGET, path)
    if not os.path.isfile(p):
        return pd.DataFrame()
    df = pd.read_csv(p)
    for c in ["area", "total_original_budget", "total_projected_budget", "project_count"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_missing_budget() -> pd.DataFrame:
    p = os.path.join(DATA_PROJECTS, MISSING_BUDGET)
    if not os.path.isfile(p):
        return pd.DataFrame()
    return pd.read_csv(p)


def load_missing_budget_by_source() -> pd.DataFrame:
    """CSV with columns: sourcesystem, total_closed_projects, closed_projects_missing_budget (run_closed_projects_missing_budget_by_source.py)."""
    p = os.path.join(DATA_PROJECTS, MISSING_BUDGET_BY_SOURCE)
    if not os.path.isfile(p):
        return pd.DataFrame()
    df = pd.read_csv(p)
    for c in ["total_closed_projects", "closed_projects_missing_budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_missing_budget_by_source_all_phases() -> pd.DataFrame:
    """CSV with columns: phasetext, sourcesystem, total_projects, projects_missing_budget, pct_missing_budget (from projects_missing_budget_by_source_all_phases.sql)."""
    p = os.path.join(DATA_PROJECTS, MISSING_BUDGET_ALL_PHASES)
    if not os.path.isfile(p):
        return pd.DataFrame()
    df = pd.read_csv(p)
    for c in ["total_projects", "projects_missing_budget", "pct_missing_budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_missing_area() -> pd.DataFrame:
    p = os.path.join(DATA_QUALITY, MISSING_AREA)
    if not os.path.isfile(p):
        return pd.DataFrame()
    return pd.read_csv(p)


def _load_sector_mapping():
    """Load sector_mapping.json into a raw -> canonical lookup (same logic as budget run script)."""
    if not os.path.isfile(SECTOR_MAPPING_FILE):
        return {}
    with open(SECTOR_MAPPING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    lookup = {}
    for canon in CANONICAL_SECTOR_ORDER:
        raw_list = data.get(canon)
        if not isinstance(raw_list, list):
            continue
        for raw in raw_list:
            s = (raw or "").strip()
            if s:
                lookup[s] = canon
                lookup[s.lower()] = canon
    return lookup


@st.cache_data(ttl=600)
def _load_projects_csv_cached(path: str, mtime: float) -> pd.DataFrame:
    """Load and process projects CSV; cache by path + mtime so we re-read when file changes."""
    df = pd.read_csv(path)
    if "area" in df.columns:
        df["area"] = pd.to_numeric(df["area"], errors="coerce")
    if "sector" in df.columns:
        sector_lookup = _load_sector_mapping()
        if sector_lookup:
            default_sector = "Special Purpose Facility"
            def map_sector(s):
                if pd.isna(s):
                    return ""
                v = str(s).strip()
                if not v:
                    return ""
                return sector_lookup.get(v) or sector_lookup.get(v.lower()) or default_sector
            df["sector"] = df["sector"].apply(map_sector)
    return df


def load_projects_budget_area() -> pd.DataFrame:
    """Project-level CSV (one row per project × cost category). Cached so re-read only when file changes."""
    for p in (
        os.path.join(DATA_PROJECTS, PROJECTS_BUDGET_AREA),
        os.path.join(PROJECT_ROOT, "data", "projects", PROJECTS_BUDGET_AREA),
        os.path.join(os.getcwd(), "data", "projects", PROJECTS_BUDGET_AREA),
        os.path.join(os.getcwd(), "data", PROJECTS_BUDGET_AREA),
        os.path.join(os.getcwd(), PROJECTS_BUDGET_AREA),
    ):
        if os.path.isfile(p):
            mtime = os.path.getmtime(p)
            return _load_projects_csv_cached(p, mtime)
    return pd.DataFrame()


def _area_sum_distinct_per_project(df: pd.DataFrame, project_id_col: str, groupby_col: str = None):
    """
    Area is repeated for each (project × category) row. Return sum of area counting each project once.
    If groupby_col is None: return scalar total. Else: return Series of area per group (one area per project within each group, then summed).
    Uses groupby + first() instead of drop_duplicates to avoid a full dedup scan on large data.
    """
    if "area" not in df.columns:
        return 0.0 if groupby_col is None else pd.Series(dtype=float)
    if groupby_col is None:
        # One area per project, then sum: groupby project_id, take first area, sum
        return df.groupby(project_id_col)["area"].first().sum()
    return df.groupby([groupby_col, project_id_col])["area"].first().reset_index().groupby(groupby_col)["area"].sum()


def load_missing_area_by_source() -> pd.DataFrame:
    """CSV with columns: sourcesystem, projects_with_budget, projects_with_area, projects_missing_area (from run script)."""
    p = os.path.join(DATA_QUALITY, DATA_QUALITY_MISSING_AREA_BY_SOURCE)
    if not os.path.isfile(p):
        return pd.DataFrame()
    return pd.read_csv(p)


def _compute_data_quality_metrics_by_source() -> pd.DataFrame:
    """
    Compute data quality metrics for Clarizen, Ingenious, and Combined.
    Returns long-form DataFrame: Issue, Metric, Source, Value, Pct.
    """
    rows = []
    projects_df = load_projects_budget_area()
    missing_area_by_source = load_missing_area_by_source()
    ma_df = load_missing_area()

    # Issue 1: Missing property mapping / area measurement
    if not missing_area_by_source.empty and "sourcesystem" in missing_area_by_source.columns:
        for _, r in missing_area_by_source.iterrows():
            src = (r.get("sourcesystem") or "").strip().lower()
            if src not in ("clarizen", "ingenious"):
                continue
            with_budget = int(r.get("projects_with_budget", 0) or 0)
            missing = int(r.get("projects_missing_area", 0) or 0)
            pct = (100 * missing / with_budget) if with_budget else 0
            rows.append({"Issue": 1, "Metric": "Projects missing area (no property mapping)", "Source": src.capitalize(), "Value": f"{missing:,}", "Pct": pct})
        if not ma_df.empty:
            d = ma_df.set_index("metric")["value"].to_dict()
            combined_with = int(d.get("Distinct projects with budget (any area)", 0))
            combined_miss = int(d.get("Distinct projects with budget but MISSING/ZERO area", 0))
            rows.append({"Issue": 1, "Metric": "Projects missing area (no property mapping)", "Source": "Combined", "Value": f"{combined_miss:,}", "Pct": (100 * combined_miss / combined_with) if combined_with else 0})
    else:
        if not ma_df.empty:
            d = ma_df.set_index("metric")["value"].to_dict()
            with_budget = int(d.get("Distinct projects with budget (any area)", 0))
            missing = int(d.get("Distinct projects with budget but MISSING/ZERO area", 0))
            pct = (100 * missing / with_budget) if with_budget else 0
            rows.append({"Issue": 1, "Metric": "Projects missing area (no property mapping)", "Source": "Combined", "Value": f"{missing:,}", "Pct": pct})
        for s in ["Clarizen", "Ingenious"]:
            rows.append({"Issue": 1, "Metric": "Projects missing area (no property mapping)", "Source": s, "Value": "—", "Pct": None})

    if not projects_df.empty and "sourcesystem" in projects_df.columns:
        id_col = "sourceprojectid" if "sourceprojectid" in projects_df.columns else "project_name"
        for src in ["clarizen", "ingenious"]:
            sub = projects_df[projects_df["sourcesystem"].fillna("").str.strip().str.lower() == src]
            if sub.empty:
                continue
            n_proj = sub[id_col].nunique()
            miss_any_geo = sub[
                sub["city"].fillna("").astype(str).str.strip().isin(("", "(Blank)")) |
                sub["state"].fillna("").astype(str).str.strip().isin(("", "(Blank)")) |
                sub["country"].fillna("").astype(str).str.strip().isin(("", "(Blank)"))
            ][id_col].nunique()
            pct_geo = (100 * miss_any_geo / n_proj) if n_proj else 0
            rows.append({"Issue": 2, "Metric": "Projects missing city/state/country", "Source": src.capitalize(), "Value": f"{miss_any_geo:,} of {n_proj:,}", "Pct": pct_geo})
            has_sector = sub[
                sub["sector"].notna() & (sub["sector"].astype(str).str.strip() != "") & (sub["sector"].astype(str).str.strip() != "(Blank)")
            ][id_col].nunique()
            pct_sector = (100 * has_sector / n_proj) if n_proj else 0
            rows.append({"Issue": 3, "Metric": "Projects with sector set", "Source": src.capitalize(), "Value": f"{has_sector:,} of {n_proj:,}", "Pct": pct_sector})
        n_proj_all = projects_df[id_col].nunique()
        miss_any_geo_all = projects_df[
            projects_df["city"].fillna("").astype(str).str.strip().isin(("", "(Blank)")) |
            projects_df["state"].fillna("").astype(str).str.strip().isin(("", "(Blank)")) |
            projects_df["country"].fillna("").astype(str).str.strip().isin(("", "(Blank)"))
        ][id_col].nunique()
        pct_geo_all = (100 * miss_any_geo_all / n_proj_all) if n_proj_all else 0
        rows.append({"Issue": 2, "Metric": "Projects missing city/state/country", "Source": "Combined", "Value": f"{miss_any_geo_all:,} of {n_proj_all:,}", "Pct": pct_geo_all})
        has_sector_all = projects_df[
            projects_df["sector"].notna() & (projects_df["sector"].astype(str).str.strip() != "") & (projects_df["sector"].astype(str).str.strip() != "(Blank)")
        ][id_col].nunique()
        pct_sector_all = (100 * has_sector_all / n_proj_all) if n_proj_all else 0
        rows.append({"Issue": 3, "Metric": "Projects with sector set", "Source": "Combined", "Value": f"{has_sector_all:,} of {n_proj_all:,}", "Pct": pct_sector_all})

    for issue_num, metric in [(4, "Consistent cost codes (standardization)"), (5, "Budget details (unit qty/cost per line)")]:
        for src in ["Clarizen", "Ingenious", "Combined"]:
            rows.append({"Issue": issue_num, "Metric": metric, "Source": src, "Value": "—", "Pct": None})

    return pd.DataFrame(rows)


def _render_data_quality():
    """Data Quality tab: DQ metrics by source, missing budget, and missing area sections (no sidebar filters)."""
    # ── Data quality metrics by source (Clarizen, Ingenious, Combined) ─────
    st.subheader("Data quality metrics by source")
    dq_df = _compute_data_quality_metrics_by_source()
    if not dq_df.empty:
        dq_df["Display"] = dq_df.apply(lambda r: f"{r['Value']} ({r['Pct']:.1f}%)" if pd.notna(r.get("Pct")) else r["Value"], axis=1)
        wide = dq_df.pivot_table(index=["Issue", "Metric"], columns="Source", values="Display", aggfunc="first").reset_index()
        for col in ["Clarizen", "Ingenious", "Combined"]:
            if col not in wide.columns:
                wide[col] = "—"
        wide = wide[["Issue", "Metric", "Clarizen", "Ingenious", "Combined"]]
        st.caption("Issues 1–3 from project/summary data; 4–5 require cost code and budget detail data (—). Run data_quality_missing_area_by_source.py for Issue 1 by Clarizen/Ingenious.")
        st.dataframe(wide, use_container_width=True, hide_index=True)
    else:
        st.info("Load projects_closed_usd_with_budget_and_area.csv and/or missing_area_summary.csv to see metrics.")

    st.divider()
    st.subheader("Projects missing a budget by business line")
    mb_df = load_missing_budget()
    if not mb_df.empty:
        total_row = mb_df[mb_df["business_line"] == "(Total)"]
        total_missing = int(total_row["closed_projects_missing_budget"].iloc[0]) if len(total_row) else int(mb_df["closed_projects_missing_budget"].sum())
        st.metric("Closed projects missing budget", f"{int(total_missing):,}")
        mb_display = mb_df[mb_df["business_line"] != "(Total)"].copy()
        if not mb_display.empty:
            mb_display = mb_display.sort_values("closed_projects_missing_budget", ascending=False)
            mb_chart = alt.Chart(mb_display).mark_bar().encode(
                x=alt.X("business_line:N", title="Business line", sort=alt.EncodingSortField("closed_projects_missing_budget", op="sum", order="descending")),
                y=alt.Y("closed_projects_missing_budget:Q", title="Projects missing budget"),
                tooltip=["business_line", alt.Tooltip("closed_projects_missing_budget:Q", format=",")],
            ).properties(height=280)
            st.altair_chart(mb_chart, use_container_width=True)
            mb_sorted = mb_df[mb_df["business_line"] != "(Total)"].sort_values("closed_projects_missing_budget", ascending=False)
            transposed = mb_sorted.set_index("business_line").T
            transposed["(Total)"] = total_missing
            transposed = transposed.applymap(lambda x: f"{int(x):,}" if pd.notna(x) else "")
            st.dataframe(transposed, use_container_width=True, hide_index=True)
    else:
        st.info("Run closed_projects_missing_budget_by_business_line to generate this data.")

    st.divider()
    st.subheader("Project budget and area analysis")
    ma_df = load_missing_area()
    mb_df = load_missing_budget()
    mb_by_source_df = load_missing_budget_by_source()
    if not ma_df.empty and not mb_df.empty:
        d = ma_df.set_index("metric")["value"].to_dict()
        proj_with_budget_any = int(d.get("Distinct projects with budget (any area)", 0))
        proj_missing_area = int(d.get("Distinct projects with budget but MISSING/ZERO area", 0))
        total_missing_budget = int(mb_df[mb_df["business_line"] == "(Total)"]["closed_projects_missing_budget"].iloc[0]) if len(mb_df[mb_df["business_line"] == "(Total)"]) else int(mb_df["closed_projects_missing_budget"].sum())
        total_closed = total_missing_budget + proj_with_budget_any
        pct_missing_budget = (total_missing_budget / total_closed * 100) if total_closed else 0
        pct_missing_area = (proj_missing_area / total_closed * 100) if total_closed else 0
        missing_either = total_missing_budget + proj_missing_area
        pct_missing_either = (missing_either / total_closed * 100) if total_closed else 0
        # Option: Combined vs By source system (Clarizen / Ingenious)
        chart_view = st.radio(
            "Chart view",
            options=["Combined", "By source system (Clarizen / Ingenious)"],
            index=0,
            key="dq_budget_area_chart_view",
            horizontal=True,
        )
        if chart_view == "Combined":
            chart_df = pd.DataFrame({
                "Metric": ["Missing budget", "Missing area", "Missing Both"],
                "Percentage": [round(pct_missing_budget, 1), round(pct_missing_area, 1), round(pct_missing_either, 1)],
            })
            bar_chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X("Percentage:Q", title="% of closed projects", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Metric:N", title="", sort=["Missing budget", "Missing area", "Missing Both"]),
                tooltip=["Metric", alt.Tooltip("Percentage:Q", format=".1f")],
            ).properties(height=220)
            st.altair_chart(bar_chart, use_container_width=True)
            table_df = pd.DataFrame({
                "": ["Amt Missing", "Total Projects"],
                "Missing budget": [f"{total_missing_budget:,}", f"{total_closed:,}"],
                "Missing area": [f"{proj_missing_area:,}", f"{total_closed:,}"],
                "Missing Both": [f"{missing_either:,}", f"{total_closed:,}"],
            })
            st.caption("Numbers used in the bar chart above.")
            st.dataframe(table_df, use_container_width=True, hide_index=True)
        else:
            # By source system: show missing budget by Clarizen / Ingenious
            if not mb_by_source_df.empty and "sourcesystem" in mb_by_source_df.columns:
                src_display = mb_by_source_df.copy()
                src_display["Source"] = src_display["sourcesystem"].astype(str).str.strip().str.capitalize()
                src_display["pct_missing"] = (
                    src_display["closed_projects_missing_budget"] / src_display["total_closed_projects"] * 100
                ).fillna(0).round(1)
                bar_src = alt.Chart(src_display).mark_bar().encode(
                    x=alt.X("Source:N", title="Source system", sort=alt.EncodingSortField("closed_projects_missing_budget", op="sum", order="descending")),
                    y=alt.Y("closed_projects_missing_budget:Q", title="Closed projects missing budget"),
                    tooltip=[
                        "Source",
                        alt.Tooltip("closed_projects_missing_budget:Q", format=","),
                        alt.Tooltip("total_closed_projects:Q", format=","),
                        alt.Tooltip("pct_missing:Q", format=".1f", title="% missing budget"),
                    ],
                ).properties(height=220)
                st.altair_chart(bar_src, use_container_width=True)
                tbl = src_display[["Source", "total_closed_projects", "closed_projects_missing_budget", "pct_missing"]].copy()
                tbl.columns = ["Source", "Total closed", "Missing budget", "% missing"]
                tbl["% missing"] = tbl["% missing"].apply(lambda x: f"{x:.1f}%")
                st.caption("Closed USD projects missing budget by source system.")
                st.dataframe(tbl, use_container_width=True, hide_index=True)
            else:
                st.info("Load closed_projects_missing_budget_by_source.csv (run run_closed_projects_missing_budget_by_source.py) to see by source system.")
        st.caption("Source: missing_area_summary.csv, closed_projects_missing_budget_by_business_line.csv; by source: closed_projects_missing_budget_by_source.csv. Run summary_missing_area_projects.py, run_closed_projects_missing_budget_by_business_line.py, run_closed_projects_missing_budget_by_source.py to refresh.")
    elif not ma_df.empty:
        st.info("Load closed_projects_missing_budget_by_business_line.csv for the full analysis (chart and table).")
        d = ma_df.set_index("metric")["value"].to_dict()
        proj_missing = int(d.get("Distinct projects with budget but MISSING/ZERO area", 0))
        st.metric("Projects with budget but no area", f"{proj_missing:,}")
    elif not mb_df.empty:
        st.info("Load missing_area_summary.csv (run summary_missing_area_projects.py) for the full analysis.")
    else:
        st.info("Add missing_area_summary.csv and closed_projects_missing_budget_by_business_line.csv for this section.")


def _render_missing_budget_tab():
    """Missing Budget tab: heatmap of % missing budget by phase (y) and source (x)."""
    st.subheader("Missing budget by phase and source")
    st.caption("Percentage of projects missing a budget (no generictask with budget/Cost Code Item and amount > 0). Phases: Initiate, Construct, Planning/Design, Closeout, Design, Plan, Closed, Pursuit. Run the SQL and export to data/projects/projects_missing_budget_by_source_all_phases.csv to refresh.")
    df = load_missing_budget_by_source_all_phases()
    if df.empty:
        st.info("No data. Run **projects_missing_budget_by_source_all_phases.sql** and save results as `data/projects/projects_missing_budget_by_source_all_phases.csv` (columns: phasetext, sourcesystem, total_projects, projects_missing_budget, pct_missing_budget).")
        return
    required = {"phasetext", "sourcesystem", "pct_missing_budget"}
    if not required.issubset(df.columns):
        st.warning(f"CSV must have columns: {', '.join(required)}. Found: {', '.join(df.columns)}.")
        return
    # Normalize for display
    df = df.copy()
    df["sourcesystem"] = df["sourcesystem"].astype(str).str.strip().str.capitalize()
    df["phasetext"] = df["phasetext"].astype(str).str.strip()
    df["pct_missing_budget"] = pd.to_numeric(df["pct_missing_budget"], errors="coerce").fillna(0)
    # Phase order for consistent y-axis (match case-insensitively to data)
    phase_order = ["Initiate", "Construct", "Planning/Design", "Closeout", "Design", "Plan", "Closed", "Pursuit"]
    seen = set()
    order = []
    for p in phase_order:
        for v in df["phasetext"].unique():
            if str(v).strip().lower() == p.lower():
                order.append(v)
                seen.add(str(v).strip().lower())
                break
    for v in df["phasetext"].unique():
        if str(v).strip().lower() not in seen:
            order.append(v)
    df["phasetext"] = pd.Categorical(df["phasetext"], categories=order, ordered=True)
    heatmap = alt.Chart(df).mark_rect().encode(
        x=alt.X("sourcesystem:N", title="Source system", sort=["Clarizen", "Ingenious"]),
        y=alt.Y("phasetext:N", title="Phase", sort=order),
        color=alt.Color(
            "pct_missing_budget:Q",
            title="% missing budget",
            scale=alt.Scale(domain=[0, 100], scheme="reds"),
            legend=alt.Legend(format=".0f"),
        ),
        tooltip=[
            alt.Tooltip("phasetext:N", title="Phase"),
            alt.Tooltip("sourcesystem:N", title="Source"),
            alt.Tooltip("pct_missing_budget:Q", format=".0f", title="% missing budget"),
            alt.Tooltip("total_projects:Q", format=",", title="Total projects"),
            alt.Tooltip("projects_missing_budget:Q", format=",", title="Missing budget"),
        ],
    ).properties(height=400, width=280)
    st.altair_chart(heatmap, use_container_width=True)
    st.subheader("Data table")
    display_df = df[["phasetext", "sourcesystem", "total_projects", "projects_missing_budget", "pct_missing_budget"]].copy()
    display_df["pct_missing_budget"] = display_df["pct_missing_budget"].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "")
    display_df.columns = ["Phase", "Source", "Total projects", "Missing budget", "% missing budget"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title="Budget Closed & Summaries", layout="wide")

    # Global navigation at the very top (link-style menu items)
    if "main_tab" not in st.session_state:
        st.session_state.main_tab = "Budget Analysis"
    tab = st.session_state.main_tab

    # Global nav at top: two menu options, no wrap; active has thicker blue underline; grey line tight under nav
    st.markdown("""
        <style>
        section.main .block-container { padding-top: 0.75rem !important; }
        section.main .stButton:nth-of-type(1) button,
        section.main .stButton:nth-of-type(2) button,
        section.main .stButton:nth-of-type(3) button {
            background: transparent !important; color: #31333F !important; border: none !important;
            box-shadow: none !important; font-weight: 500 !important; font-size: 0.95rem !important;
            white-space: nowrap !important;
        }
        section.main .stButton:nth-of-type(1) button:hover,
        section.main .stButton:nth-of-type(2) button:hover,
        section.main .stButton:nth-of-type(3) button:hover { background: rgba(0,0,0,0.04) !important; }
        /* Tighter nav row: less padding so grey line sits close to menu */
        section.main [data-testid="column"]:nth-of-type(1),
        section.main [data-testid="column"]:nth-of-type(2),
        section.main [data-testid="column"]:nth-of-type(3) { padding-bottom: 0.1rem !important; }
        .nav-sep { margin-top: 0.15rem !important; margin-bottom: 0.5rem !important; }
        </style>
    """, unsafe_allow_html=True)
    col_ba, col_dq, col_mb, _ = st.columns([1, 1, 1, 13])
    with col_ba:
        if st.button("Budget Analysis", key="nav_budget_analysis", use_container_width=True, type="tertiary"):
            st.session_state.main_tab = "Budget Analysis"
            st.rerun()
        if tab == "Budget Analysis":
            st.markdown("<div style='height:4px; background:#1E88E5; width:100%; margin-top:-2px;'></div>", unsafe_allow_html=True)
    with col_dq:
        if st.button("Data Quality", key="nav_data_quality", use_container_width=True, type="tertiary"):
            st.session_state.main_tab = "Data Quality"
            st.rerun()
        if tab == "Data Quality":
            st.markdown("<div style='height:4px; background:#1E88E5; width:100%; margin-top:-2px;'></div>", unsafe_allow_html=True)
    with col_mb:
        if st.button("Missing Budget", key="nav_missing_budget", use_container_width=True, type="tertiary"):
            st.session_state.main_tab = "Missing Budget"
            st.rerun()
        if tab == "Missing Budget":
            st.markdown("<div style='height:4px; background:#1E88E5; width:100%; margin-top:-2px;'></div>", unsafe_allow_html=True)
    st.markdown('<hr class="nav-sep" style="margin-top:0.15rem; margin-bottom:0.5rem; border:none; border-top:1px solid rgba(49,51,63,0.2);">', unsafe_allow_html=True)

    st.title("Budget Summary by City/State")

    if tab == "Missing Budget":
        st.sidebar.caption("Missing Budget view — heatmap by phase and source.")
        with st.container():
            _render_missing_budget_tab()
        return

    if tab == "Data Quality":
        st.sidebar.caption("Data Quality view — filters apply only on Budget Analysis.")
        # Data Quality tab: only these sections (no Budget Analysis charts including By Sector)
        with st.container():
            _render_data_quality()
        return

    # ── Budget Analysis tab: project-level dataset only ─────────────────────
    st.caption("Filter by geography (state/city), project type, and sector. Totals by category, area, $/sqft.")

    df = load_projects_budget_area()
    if df.empty:
        st.warning("Project-level file not found: projects_closed_usd_with_budget_and_area.csv. Run run_projects_closed_usd_with_budget_and_area.py first.")
        st.stop()

    project_id_col = "project_id" if "project_id" in df.columns else "sourceprojectid"
    df = df.copy()
    df["taskname"] = df["cost_code_category"] if "cost_code_category" in df.columns else "(Unknown)"
    df["state_display"] = df["state"].fillna("(Blank)").replace("", "(Blank)") if "state" in df.columns else "(Blank)"
    df["city_display"] = df["city"].fillna("(Blank)").replace("", "(Blank)")
    if "sector" in df.columns:
        df["sector_display"] = df["sector"].fillna("(Blank)").replace("", "(Blank)")
    for c in ["area", "total_original_budget", "total_projected_budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Global filter: source system (Clarizen / Ingenious / Both)
    has_sourcesystem = "sourcesystem" in df.columns
    if has_sourcesystem:
        st.sidebar.markdown("**Source system**")
        source_system_choice = st.sidebar.radio(
            "Source system",
            ["Both", "Clarizen", "Ingenious"],
            index=0,
            key="source_system_radio",
            help="Filter all dashboard data by project/cost source system.",
        )
        # When source system changes, reset geo/sector/project type filters so charts get a valid subset
        _select_all = "(Select All)"
        if " _source_system_prev" not in st.session_state:
            st.session_state[" _source_system_prev"] = source_system_choice
        if st.session_state[" _source_system_prev"] != source_system_choice:
            st.session_state[" _source_system_prev"] = source_system_choice
            for key in ("state_widget", "_prev_state", "city_widget", "_prev_city", "sector_widget", "_prev_sector", "project_type_widget", "_prev_project_type"):
                if key in st.session_state:
                    st.session_state[key] = [_select_all]
        if source_system_choice != "Both":
            source_val = source_system_choice.lower().strip()
            df = df[df["sourcesystem"].fillna("").astype(str).str.lower().str.strip() == source_val].copy()
            if df.empty:
                st.warning(f"No data for source system \"{source_system_choice}\". Load projects_closed_usd_with_budget_and_area.csv with that source, or choose Both.")
                st.stop()
        st.sidebar.divider()

    # Global filter: exclude rows with area <= 2 (tiny/placeholder areas)
    if "area" in df.columns:
        before = len(df)
        df = df[(df["area"].isna()) | (df["area"] > 2)].copy()
        if before > len(df):
            st.sidebar.caption(f"Excluded {before - len(df):,} rows with area ≤ 2.")

    has_project_type = "project_type" in df.columns
    has_sector = "sector" in df.columns

    # ── Filters (geographical + project type + sector) ───────────────────────
    _SELECT_ALL = "(Select All)"

    def _make_select_all_callback(widget_key, prev_key):
        def _():
            raw = st.session_state[widget_key]
            specific = [v for v in raw if v != _SELECT_ALL]
            if not raw:
                resolved = [_SELECT_ALL]
            elif _SELECT_ALL in raw and specific:
                resolved = specific
            elif _SELECT_ALL in raw:
                resolved = [_SELECT_ALL]
            else:
                resolved = raw
            st.session_state[widget_key] = resolved
            st.session_state[prev_key] = resolved
        return _

    st.sidebar.subheader("Filters")
    st.sidebar.caption("Select any filter — selections combine with AND. Picking a value removes (Select All).")

    st.sidebar.markdown("**Geographical filters**")
    all_states = ["(Blank)"] + sorted([s for s in df["state_display"].dropna().unique() if s != "(Blank)"])
    state_options = [_SELECT_ALL] + all_states

    if "state_widget" not in st.session_state:
        st.session_state.state_widget = [_SELECT_ALL]
        st.session_state._prev_state = [_SELECT_ALL]
    state_cur = st.session_state.state_widget
    state_clip = [s for s in state_cur if s == _SELECT_ALL or s in all_states] or [_SELECT_ALL]
    if set(state_clip) != set(state_cur):
        st.session_state.state_widget = state_clip
        st.session_state._prev_state = state_clip

    selected_states = st.sidebar.multiselect(
        "State",
        state_options,
        key="state_widget",
        on_change=_make_select_all_callback("state_widget", "_prev_state"),
        help="City list updates to cities in selected state(s).",
    )
    specific_states = [s for s in selected_states if s != _SELECT_ALL]
    states_for_filter = all_states if not specific_states else specific_states

    df_state_filtered = df[df["state_display"].isin(states_for_filter)]
    available_cities = ["(Blank)"] + sorted([c for c in df_state_filtered["city_display"].dropna().unique() if c != "(Blank)"])
    city_options = [_SELECT_ALL] + available_cities

    if "city_widget" not in st.session_state:
        st.session_state.city_widget = [_SELECT_ALL]
        st.session_state._prev_city = [_SELECT_ALL]
    city_cur = st.session_state.city_widget
    city_clip = [c for c in city_cur if c == _SELECT_ALL or c in available_cities] or [_SELECT_ALL]
    if set(city_clip) != set(city_cur):
        st.session_state.city_widget = city_clip
        st.session_state._prev_city = city_clip

    selected_cities = st.sidebar.multiselect(
        "City",
        city_options,
        key="city_widget",
        on_change=_make_select_all_callback("city_widget", "_prev_city"),
        help="Only in selected state(s).",
    )
    specific_cities = [c for c in selected_cities if c != _SELECT_ALL]
    cities_for_filter = available_cities if not specific_cities else specific_cities

    project_types_for_filter = None
    if has_project_type:
        st.sidebar.markdown("**Project type**")
        all_project_types = sorted(df["project_type"].dropna().unique().tolist())
        project_type_options = [_SELECT_ALL] + all_project_types

        def _on_project_type_change():
            raw = st.session_state.project_type_widget
            prev = st.session_state.get("_prev_project_type", [_SELECT_ALL])
            specific = [p for p in raw if p != _SELECT_ALL]
            if not raw:
                resolved = [_SELECT_ALL]
            elif _SELECT_ALL in raw and specific:
                resolved = specific
            elif _SELECT_ALL in raw:
                resolved = [_SELECT_ALL]
            else:
                resolved = raw
            st.session_state.project_type_widget = resolved
            st.session_state._prev_project_type = resolved

        if "project_type_widget" not in st.session_state:
            st.session_state.project_type_widget = [_SELECT_ALL]
            st.session_state._prev_project_type = [_SELECT_ALL]

        selected_project_types = st.sidebar.multiselect(
            "Project type",
            project_type_options,
            key="project_type_widget",
            on_change=_on_project_type_change,
            help="Picking a value removes (Select All). Combines with geographical filters (AND).",
        )
        specific = [p for p in selected_project_types if p != _SELECT_ALL]
        project_types_for_filter = all_project_types if not specific else specific

    sectors_for_filter = None
    if has_sector:
        st.sidebar.markdown("**Sector**")
        all_sectors = sorted(df["sector_display"].dropna().unique().tolist())
        sector_options = [_SELECT_ALL] + all_sectors

        if "sector_widget" not in st.session_state:
            st.session_state.sector_widget = [_SELECT_ALL]
            st.session_state._prev_sector = [_SELECT_ALL]
        sector_cur = st.session_state.sector_widget
        sector_clip = [s for s in sector_cur if s == _SELECT_ALL or s in all_sectors] or [_SELECT_ALL]
        if set(sector_clip) != set(sector_cur):
            st.session_state.sector_widget = sector_clip
            st.session_state._prev_sector = sector_clip

        selected_sectors = st.sidebar.multiselect(
            "Sector",
            sector_options,
            key="sector_widget",
            on_change=_make_select_all_callback("sector_widget", "_prev_sector"),
            help="Filter by sector. Combines with other filters (AND).",
        )
        specific_sectors = [s for s in selected_sectors if s != _SELECT_ALL]
        sectors_for_filter = all_sectors if not specific_sectors else specific_sectors

    exclude_blank = st.sidebar.checkbox(
        "Exclude (Blank) city/state",
        value=False,
        help="Exclude rows with blank city or state from all metrics and charts.",
    )

    filtered = df[df["state_display"].isin(states_for_filter) & df["city_display"].isin(cities_for_filter)]
    if project_types_for_filter is not None:
        filtered = filtered[filtered["project_type"].isin(project_types_for_filter)]
    if sectors_for_filter is not None:
        filtered = filtered[filtered["sector_display"].isin(sectors_for_filter)]
    if exclude_blank:
        filtered = filtered[
            (filtered["city_display"] != "(Blank)") & (filtered["state_display"] != "(Blank)")
        ]

    # KPIs from project-level data (area: distinct value per project_id, then sum across projects)
    total_projects = int(filtered[project_id_col].nunique())
    total_budget = float(filtered["total_original_budget"].sum()) if not filtered.empty else 0.0
    total_proj_budget = float(filtered["total_projected_budget"].sum()) if not filtered.empty else 0.0
    total_area = _area_sum_distinct_per_project(filtered, project_id_col)
    psf = (total_proj_budget / total_area) if total_area and total_area > 0 else None
    filtered_projects = filtered

    if filtered.empty:
        st.info("No rows match the current filters (state, city, project type, sector). Try clearing or changing filters.")
        st.stop()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total original budget", f"${total_budget/1e9:.2f}B" if total_budget >= 1e9 else f"${total_budget/1e6:.2f}M")
    col2.metric("Total projected budget", f"${total_proj_budget/1e9:.2f}B" if total_proj_budget >= 1e9 else f"${total_proj_budget/1e6:.2f}M")
    col3.metric("Total area (sq ft)", f"{total_area/1e6:.2f}M" if total_area >= 1e6 else f"{total_area:,.0f}")
    col4.metric("Project count", f"{total_projects:,.0f}")
    col5.metric("Total Projected Budget/SQFT", f"${psf:,.2f}" if psf is not None else "—")

    # By taskname (category): budget, project count, and area = sum of area of projects that have budget in that category
    st.subheader("Totals by Category")
    by_cat = (
        filtered.groupby("taskname", dropna=False)
        .agg(
            total_original_budget=("total_original_budget", "sum"),
            total_projected_budget=("total_projected_budget", "sum"),
            project_count=(project_id_col, "nunique"),
        )
        .reset_index()
    )
    # Per-category area: sum of (distinct area per project) for projects that have budget in that category
    area_by_cat = filtered.groupby("taskname", dropna=False).apply(
        lambda g: _area_sum_distinct_per_project(g, project_id_col)
    )
    by_cat["area"] = by_cat["taskname"].map(area_by_cat)
    by_cat["psf"] = by_cat.apply(
        lambda r: r["total_projected_budget"] / r["area"] if r["area"] and r["area"] > 0 else None,
        axis=1,
    )
    gt_orig = by_cat["total_original_budget"].sum()
    gt_proj = by_cat["total_projected_budget"].sum()
    gt_psf = (gt_proj / total_area) if total_area and total_area > 0 else None
    display_df = pd.DataFrame({
        "Cost type": list(by_cat["taskname"]) + ["Grand Total"],
        "Total Orig Budget": list(by_cat["total_original_budget"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")) + [f"${gt_orig:,.0f}"],
        "Total Projected Budget": list(by_cat["total_projected_budget"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")) + [f"${gt_proj:,.0f}"],
        "Total Area": list(by_cat["area"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and x else "")) + [f"{total_area:,.0f}"],
        "Project Count": list(by_cat["project_count"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")) + [f"{total_projects:,.0f}"],
        "Total Projected Budget/SQFT": list(by_cat["psf"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) and x is not None else "")) + [f"${gt_psf:,.2f}" if gt_psf is not None else ""],
    })
    # Highlight Grand Total row with light gray (similar to table header)
    styled = display_df.style.apply(
        lambda s: ["background-color: #e8e8e8"] * len(s) if s.name == len(display_df) - 1 else [""] * len(s),
        axis=1,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("Total Area = sum of building area for projects that have budget in that category (each project counted once). $/sqft = category projected budget ÷ category area.")

    # Bar chart by category: side-by-side bars (Original | Projected per category), touching within category, sorted by total original budget descending
    chart_col, _ = st.columns([1, 1])
    with chart_col:
        if by_cat.empty:
            st.info("No category data to chart for the current filters.")
        else:
            by_cat_sorted = by_cat.sort_values("total_original_budget", ascending=False)
            cat_order = by_cat_sorted["taskname"].tolist()
            chart_cat = (
                by_cat_sorted[["taskname", "total_original_budget", "total_projected_budget"]]
                .melt(id_vars="taskname", var_name="budget_type", value_name="value")
                .replace({
                    "total_original_budget": "Total Original Budget",
                    "total_projected_budget": "Total Projected Budget",
                })
            )
            # Numeric x: each category occupies [2*i, 2*i+1]; two bars share that range (touching). Gap between categories.
            def bar_edges(r):
                ci = cat_order.index(r["taskname"])
                start = 2 * ci + (0 if "Original" in r["budget_type"] else 0.5)
                return start, start + 0.5
            chart_cat["x_left"] = chart_cat.apply(lambda r: bar_edges(r)[0], axis=1)
            chart_cat["x_right"] = chart_cat.apply(lambda r: bar_edges(r)[1], axis=1)
            chart_cat["y_baseline"] = 0
            # Axis labels at category centers 0.5, 2.5, 4.5, 6.5 (escape single quotes for Vega)
            axis_vals = [0.5 + 2 * i for i in range(len(cat_order))]
            safe_labels = [str(c).replace("'", "\\'") for c in cat_order]
            label_expr = " : ".join(f"datum.value === {v} ? '{l}'" for v, l in zip(axis_vals, safe_labels)) + " : ''"
            cat_chart = (
                alt.Chart(chart_cat)
                .mark_bar()
                .encode(
                    x=alt.X("x_left:Q", scale=alt.Scale(domain=[-0.25, 2 * len(cat_order)]), title="Category",
                            axis=alt.Axis(values=axis_vals, labelExpr=label_expr, labelAngle=-25)),
                    x2=alt.X2("x_right:Q"),
                    y=alt.Y("value:Q", title="Budget"),
                    y2=alt.Y2("y_baseline:Q"),
                    color=alt.Color("budget_type:N", title="", scale=alt.Scale(range=["#1f77b4", "#ff7f0e"])),
                    tooltip=[
                        "taskname",
                        "budget_type",
                        alt.Tooltip("value:Q", format=",.0f", title="Budget"),
                    ],
                )
                .properties(height=350, width=900)
            )
            st.altair_chart(cat_chart, use_container_width=True)

    # ── Stacked $/SQFT by top 15 cities ─────────────────────────────────────
    st.divider()
    st.subheader("Top Cities by Project Count")
    city_projects = filtered_projects.groupby("city_display")[project_id_col].nunique()
    top_cities = city_projects.nlargest(15).index.tolist()

    default_excluded_cities = [c for c in ["(Blank)"] if c in top_cities]
    excluded_cities = st.multiselect(
        "Exclude cities from chart",
        options=top_cities,
        default=default_excluded_cities,
        help="Remove cities to improve readability (e.g. exclude outliers).",
        key="exclude_cities_chart",
    )
    chart_cities = [c for c in top_cities if c not in excluded_cities]

    city_area = _area_sum_distinct_per_project(
        filtered_projects[filtered_projects["city_display"].isin(chart_cities)],
        project_id_col,
        groupby_col="city_display",
    )
    city_cat = (
        filtered_projects[filtered_projects["city_display"].isin(chart_cities)]
        .groupby(["city_display", "taskname"], dropna=False)["total_projected_budget"]
        .sum()
        .reset_index()
    )
    city_cat = city_cat.merge(city_area.rename("city_area"), left_on="city_display", right_index=True)
    city_cat["psf"] = city_cat["total_projected_budget"] / city_cat["city_area"].replace(0, float("nan"))
    total_psf = (
        city_cat.groupby("city_display")["psf"].sum()
        .sort_values(ascending=False)
    )
    city_order = total_psf.index.tolist()

    if chart_cities and not city_cat.empty:
        city_proj_df = (
            filtered_projects[filtered_projects["city_display"].isin(chart_cities)]
            .groupby("city_display")[project_id_col]
            .nunique()
            .reset_index()
        )
        city_proj_df.columns = ["city_display", "project_count"]

        max_psf = float(city_cat.groupby("city_display")["psf"].sum().max())
        max_proj = float(city_proj_df["project_count"].max())
        if pd.isna(max_psf) or max_psf <= 0:
            max_psf = 1.0
        if pd.isna(max_proj) or max_proj <= 0:
            max_proj = 1.0

        bars = (
            alt.Chart(city_cat)
            .mark_bar()
            .encode(
                x=alt.X("city_display:N", sort=city_order, title="City",
                         scale=alt.Scale(domain=city_order),
                         axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("psf:Q", title="$/SQFT", stack="zero",
                         scale=alt.Scale(domain=[0, max_psf * 1.05])),
                color=alt.Color("taskname:N", title="Category",
                                scale=alt.Scale(
                                    domain=["Construction", "Soft Costs", "FF&E + Millwork"],
                                    range=["#4C78A8", "#F58518", "#54A24B"],
                                )),
                tooltip=[
                    alt.Tooltip("city_display:N", title="City"),
                    alt.Tooltip("taskname:N", title="Category"),
                    alt.Tooltip("psf:Q", title="$/SQFT", format="$,.2f"),
                ],
            )
        )
        points = (
            alt.Chart(city_proj_df)
            .mark_point(filled=True, size=80, color="#E45756")
            .encode(
                x=alt.X("city_display:N", sort=city_order, title=None,
                         scale=alt.Scale(domain=city_order)),
                y=alt.Y("project_count:Q", title="Project count",
                         scale=alt.Scale(domain=[0, max_proj * 1.05]),
                         axis=alt.Axis(orient="right")),
                tooltip=[
                    alt.Tooltip("city_display:N", title="City"),
                    alt.Tooltip("project_count:Q", title="Projects", format=",.0f"),
                ],
            )
        )
        chart = (
            alt.layer(bars, points)
            .resolve_scale(y="independent")
            .properties(height=420, width="container")
        )
        st.altair_chart(chart, use_container_width=True)
    elif not chart_cities:
        st.info("All cities excluded. Clear the exclusion list to see the chart.")
    else:
        st.info("No data for the current filter selection.")

    # ── By Sector (same format as Top Cities) ─────────────────────────────────
    st.subheader("By Sector")
    if has_sector:
        with st.spinner("Building sector data…"):
            sector_area = _area_sum_distinct_per_project(
                filtered_projects, project_id_col, groupby_col="sector_display"
            )
            sector_cat = (
                filtered_projects.groupby(["sector_display", "taskname"], dropna=False)["total_projected_budget"]
                .sum()
                .reset_index()
            )
        # Normalize sector_display for reliable merge (strip / string match)
        sector_cat = sector_cat.copy()
        sector_cat["_sector_key"] = sector_cat["sector_display"].astype(str).str.strip()
        sector_area_ser = sector_area.rename("sector_area")
        sector_area_ser.index = sector_area_ser.index.astype(str).str.strip()
        sector_cat = sector_cat.merge(
            sector_area_ser,
            left_on="_sector_key",
            right_index=True,
            how="left",
        )
        sector_cat.drop(columns=["_sector_key"], inplace=True)
        sector_cat["sector_area"] = sector_cat["sector_area"].fillna(0)
        # Avoid NaN/Inf so Altair draws bars (use 0 when area is 0)
        sector_cat["psf"] = (
            sector_cat["total_projected_budget"] / sector_cat["sector_area"].replace(0, float("nan"))
        ).fillna(0).replace([float("inf"), -float("inf")], 0)
        total_psf_sector = (
            sector_cat.groupby("sector_display")["psf"].sum()
            .sort_values(ascending=False)
        )
        all_sectors = total_psf_sector.index.tolist()

        # Diagnostic: confirm sector data is present
        n_sector_rows = len(filtered_projects)
        n_sectors = len(all_sectors)
        st.caption(f"Sector data: **{n_sectors}** sectors, **{len(sector_cat)}** (sector × category) rows from {n_sector_rows:,} filtered rows.")

        default_excluded_sectors = [s for s in ["(Blank)", "Mixed-use", "Mixed Use"] if s in all_sectors]
        excluded_sectors = st.multiselect(
            "Exclude sectors from chart",
            options=all_sectors,
            default=default_excluded_sectors,
            help="Remove sectors to improve readability (e.g. exclude outliers).",
            key="exclude_sectors_chart",
        )
        chart_sectors = [s for s in all_sectors if s not in excluded_sectors]
        sector_order = chart_sectors
        sector_cat_chart = sector_cat[sector_cat["sector_display"].isin(chart_sectors)]

        if not chart_sectors:
            st.info("All sectors are excluded. Clear one or more sectors from **Exclude sectors from chart** to see the By Sector chart.")
        elif sector_cat_chart.empty:
            st.warning("No (sector × category) rows for the selected sectors. Try including more sectors in the chart.")
        elif chart_sectors and not sector_cat_chart.empty:
            sector_cat = sector_cat_chart
            sector_proj_df = (
                filtered_projects[filtered_projects["sector_display"].isin(chart_sectors)]
                .groupby("sector_display")[project_id_col]
                .nunique()
                .reset_index()
            )
            sector_proj_df.columns = ["sector_display", "project_count"]

            max_psf_s = float(sector_cat.groupby("sector_display")["psf"].sum().max())
            max_proj_s = float(sector_proj_df["project_count"].max())
            if pd.isna(max_proj_s) or max_proj_s <= 0:
                max_proj_s = 1.0
            # When no area by sector (all psf 0), show total projected budget instead so bars are visible
            use_budget_instead = pd.isna(max_psf_s) or max_psf_s <= 0
            if use_budget_instead:
                max_psf_s = 1.0
                sector_cat = sector_cat.copy()
                sector_cat["_chart_y"] = sector_cat["total_projected_budget"]
                y_title = "Total projected budget ($)"
            else:
                sector_cat = sector_cat.copy()
                sector_cat["_chart_y"] = sector_cat["psf"]
                y_title = "$/SQFT"
            y_domain_max = float(sector_cat.groupby("sector_display")["_chart_y"].sum().max()) or 1.0
            if pd.isna(y_domain_max) or y_domain_max <= 0:
                y_domain_max = 1.0

            cat_domain = ["Construction", "Soft Costs", "FF&E + Millwork", "Other"]
            cat_range = ["#4C78A8", "#F58518", "#54A24B", "#BAB0AC"]
            bars_sector = (
                alt.Chart(sector_cat)
                .mark_bar()
                .encode(
                    x=alt.X("sector_display:N", sort=sector_order, title="Sector",
                             scale=alt.Scale(domain=sector_order),
                             axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("_chart_y:Q", title=y_title, stack="zero",
                             scale=alt.Scale(domain=[0, y_domain_max * 1.05])),
                    color=alt.Color("taskname:N", title="Category",
                                    scale=alt.Scale(domain=cat_domain, range=cat_range)),
                    tooltip=[
                        alt.Tooltip("sector_display:N", title="Sector"),
                        alt.Tooltip("taskname:N", title="Category"),
                        alt.Tooltip("_chart_y:Q", title=y_title, format=",.0f" if use_budget_instead else "$,.2f"),
                    ],
                )
            )
            points_sector = (
                alt.Chart(sector_proj_df)
                .mark_point(filled=True, size=80, color="#E45756")
                .encode(
                    x=alt.X("sector_display:N", sort=sector_order, title=None,
                             scale=alt.Scale(domain=sector_order)),
                    y=alt.Y("project_count:Q", title="Project count",
                             scale=alt.Scale(domain=[0, max_proj_s * 1.05]),
                             axis=alt.Axis(orient="right")),
                    tooltip=[
                        alt.Tooltip("sector_display:N", title="Sector"),
                        alt.Tooltip("project_count:Q", title="Projects", format=",.0f"),
                    ],
                )
            )
            chart_sector = (
                alt.layer(bars_sector, points_sector)
                .resolve_scale(y="independent")
                .properties(height=420, width="container")
            )
            try:
                st.altair_chart(chart_sector, use_container_width=True)
            except Exception as e:
                st.error(f"Chart failed to render: {e}")
            if use_budget_instead:
                st.caption("No area by sector for this selection; showing total projected budget instead of $/SQFT.")
    else:
        st.info("Sector data not available for this dataset.")

    st.sidebar.caption("Data: projects_closed_usd_with_budget_and_area.csv (one row per project × category).")


if __name__ == "__main__":
    main()
