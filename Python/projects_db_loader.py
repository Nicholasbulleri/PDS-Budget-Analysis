"""
Load budget data from SQLite for dashboard use.

Tables (join on city, state, country, sector, project_type):
  - project_level_budgets: one row per project
  - cost_category_level_budgets: one row per (category, city, state, country, sector, project_type)

Usage:
  df = load_project_level_budgets()
  df = load_cost_category_level_budgets()
  df = load_projects_filtered_by_category(state=["CA"], taskname="Construction")
"""
import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

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
DB_PATH = os.path.join(PROJECT_ROOT, "projects_closed.db")
PROJECTS_CSV_FALLBACK = os.path.join(DATA_DIR, "projects_closed_usd_with_budget_and_area.csv")

JOIN_KEYS = ["city", "state", "country", "sector", "project_type"]


def load_project_level_budgets():
    """Load project-level budgets from SQLite if available, else CSV."""
    if os.path.isfile(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql("SELECT * FROM project_level_budgets", conn)
    elif os.path.isfile(PROJECTS_CSV_FALLBACK):
        df = pd.read_csv(PROJECTS_CSV_FALLBACK)
    else:
        return pd.DataFrame()

    for c in ["area", "total_original_budget", "total_projected_budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_cost_category_level_budgets():
    """Load cost category-level budgets from SQLite (Construction, Soft Costs, FF&E + Millwork)."""
    if not os.path.isfile(DB_PATH):
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM cost_category_level_budgets", conn)
    for c in ["area", "total_original_budget", "total_projected_budget", "project_count"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_projects_filtered_by_category(state=None, city=None, sector=None, project_type=None, taskname=None):
    """
    Load projects filtered by cost category selections.
    Joins project_level_budgets to cost_category_level_budgets on shared attributes.
    Pass lists for multi-select (e.g. state=["CA","NY"]).
    """
    if not os.path.isfile(DB_PATH):
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        sql = """
            SELECT DISTINCT p.*
            FROM project_level_budgets p
            INNER JOIN cost_category_level_budgets c
              ON p.city = c.city AND p.state = c.state AND p.country = c.country
              AND COALESCE(p.sector, '') = COALESCE(c.sector, '')
              AND COALESCE(p.project_type, '') = COALESCE(c.project_type, '')
              AND COALESCE(p.cost_code_category, '') = COALESCE(c.taskname, '')
            WHERE 1=1
        """
        params = []
        if state:
            states = state if isinstance(state, (list, tuple)) else [state]
            placeholders = ",".join("?" * len(states))
            sql += f" AND p.state IN ({placeholders})"
            params.extend(states)
        if city:
            cities = city if isinstance(city, (list, tuple)) else [city]
            placeholders = ",".join("?" * len(cities))
            sql += f" AND p.city IN ({placeholders})"
            params.extend(cities)
        if sector:
            sectors = sector if isinstance(sector, (list, tuple)) else [sector]
            placeholders = ",".join("?" * len(sectors))
            sql += f" AND COALESCE(p.sector, '') IN ({placeholders})"
            params.extend(sectors)
        if project_type:
            types = project_type if isinstance(project_type, (list, tuple)) else [project_type]
            placeholders = ",".join("?" * len(types))
            sql += f" AND COALESCE(p.project_type, '') IN ({placeholders})"
            params.extend(types)
        if taskname:
            cats = taskname if isinstance(taskname, (list, tuple)) else [taskname]
            placeholders = ",".join("?" * len(cats))
            sql += f" AND c.taskname IN ({placeholders})"
            params.extend(cats)
        df = pd.read_sql(sql, conn, params=params if params else None)
    for c in ["area", "total_original_budget", "total_projected_budget"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# Alias for backward compatibility
load_projects = load_project_level_budgets
