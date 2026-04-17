#!/usr/bin/env python3
"""
Load budget data into SQLite for dashboard use.

Tables (join on city, state, country, sector, project_type):
  - project_level_budgets: from projects query (sector mapped to canonical for join)
  - cost_category_level_budgets: from budget core query (sector + project type)

Run after:
  1. python3 run_projects_closed_usd_with_budget_and_area.py
  2. python3 run_budget_query_closed_by_category_with_state_using_mapping_exclude_missing_area_with_property_sector_and_project_type.py
"""
import json
import os
import sqlite3

import pandas as pd

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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "projects")
PROJECTS_CSV = os.path.join(PROJECT_ROOT, "data", "projects", "projects_closed_usd_with_budget_and_area.csv")
BUDGET_CSV = os.path.join(
    PROJECT_ROOT,
    "data",
    "budget",
    "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area_with_property_sector_and_project_type.csv",
)
SECTOR_MAPPING_FILE = os.path.join(PROJECT_ROOT, "data", "sector", "sector_mapping.json")
DB_PATH = os.path.join(PROJECT_ROOT, "projects_closed.db")

CANONICAL_SECTOR_ORDER = [
    "Office", "Retail", "Industrial and Logistics", "Data Center", "Hotels/Hospitality",
    "Residential", "Education", "Mixed-use", "Infrastructure/Energy", "Special Purpose Facility",
]
DEFAULT_SECTOR = "Special Purpose Facility"


def load_sector_mapping():
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


def main():
    conn = sqlite3.connect(DB_PATH)
    loaded = 0

    # Load project_level_budgets
    if not os.path.isfile(PROJECTS_CSV):
        print(f"CSV not found: {PROJECTS_CSV}")
        print("Run first: python3 run_projects_closed_usd_with_budget_and_area.py")
    else:
        df = pd.read_csv(PROJECTS_CSV)
        for c in ["area", "total_original_budget", "total_projected_budget"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        # Map sector to canonical (same as budget query) for join compatibility
        sector_lookup = load_sector_mapping()
        if sector_lookup and "sector" in df.columns:
            def map_sector(s):
                if pd.isna(s) or not str(s).strip():
                    return None
                v = str(s).strip()
                return sector_lookup.get(v) or sector_lookup.get(v.lower()) or DEFAULT_SECTOR
            df["sector"] = df["sector"].apply(map_sector)
        df.to_sql("project_level_budgets", conn, if_exists="replace", index=False)
        print(f"Loaded {len(df)} rows into project_level_budgets")
        print("  Columns:", ", ".join(df.columns.tolist()))
        if sector_lookup:
            print("  Sector mapped to canonical for join with cost_category_level_budgets")
        loaded += 1

    # Load cost_category_level_budgets
    if not os.path.isfile(BUDGET_CSV):
        print(f"\nCSV not found: {BUDGET_CSV}")
        print("Run: python3 run_budget_query_closed_by_category_with_state_using_mapping_exclude_missing_area_with_property_sector_and_project_type.py")
    else:
        df = pd.read_csv(BUDGET_CSV)
        for c in ["area", "total_original_budget", "total_projected_budget", "project_count"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df.to_sql("cost_category_level_budgets", conn, if_exists="replace", index=False)
        print(f"\nLoaded {len(df)} rows into cost_category_level_budgets")
        print("  Columns:", ", ".join(df.columns.tolist()))
        loaded += 1

    conn.close()

    if loaded > 0:
        print("\nJoin keys: city, state, country, sector, project_type, cost_code_category=taskname")
        print("Example: SELECT p.* FROM project_level_budgets p")
        print("  INNER JOIN cost_category_level_budgets c ON p.city=c.city AND p.state=c.state")
        print("    AND p.country=c.country AND p.sector=c.sector AND p.project_type=c.project_type")
        print("    AND p.cost_code_category=c.taskname")
        print("  WHERE c.taskname = 'Construction' AND c.state IN ('CA','NY')")
    return 0 if loaded > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
