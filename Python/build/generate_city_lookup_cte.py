#!/usr/bin/env python3
"""
Generate city_lookup CTE from city_to_state_mapping.csv and write a new query file
that uses it (Option B: inline CTE). Run after updating the mapping CSV.

Output: budget_core_query_closed_by_category_with_state_using_mapping.sql
"""

import csv
import os
import re

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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "mappings")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "budget")
MAPPING_CSV = os.path.join(PROJECT_ROOT, "data", "mappings", "city_to_state_mapping.csv")
TEMPLATE_SQL = os.path.join(SQL_DIR, "budget_core_query_closed_by_category_with_state.sql")
OUT_SQL = os.path.join(SQL_DIR, "budget_core_query_closed_by_category_with_state_using_mapping.sql")


def sql_escape(s: str) -> str:
    """Escape single quotes for SQL string literal."""
    return (s or "").replace("'", "''")


def normalize_city(s: str) -> str:
    s = (s or "").strip().rstrip(",\t")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def generate_cte(csv_path: str) -> str:
    """Build WITH city_lookup AS (...) from CSV. Dedupe by city_norm; keep first non-null state."""
    seen_norm = {}
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            city = (row.get("city") or "").strip().strip('"')
            country = (row.get("country") or "").strip()
            state = (row.get("state_abbrev") or "").strip().upper()
            city_norm = normalize_city(city)
            if not city_norm:
                continue
            if city_norm in seen_norm:
                continue
            seen_norm[city_norm] = True
            state_sql = f"'{sql_escape(state)}'" if state else "NULL"
            country_sql = f"'{sql_escape(country)}'" if country else "NULL"
            city_sql = f"'{sql_escape(city_norm)}'"
            rows.append(f"    SELECT {city_sql} AS city_norm, {state_sql} AS state_derived, {country_sql} AS country_derived")
    return "WITH city_lookup AS (\n" + " UNION ALL\n".join(rows) + "\n)"


def main() -> int:
    if not os.path.isfile(MAPPING_CSV):
        print(f"Mapping CSV not found: {MAPPING_CSV}")
        return 1
    if not os.path.isfile(TEMPLATE_SQL):
        print(f"Template SQL not found: {TEMPLATE_SQL}")
        return 1

    cte = generate_cte(MAPPING_CSV)
    with open(TEMPLATE_SQL, "r", encoding="utf-8") as f:
        full = f.read()

    # Replace the city_lookup CTE: from "WITH city_lookup AS (" to "),\n-- US state/territory"
    start_marker = "WITH city_lookup AS ("
    end_marker = "),\n-- US state/territory codes"
    if start_marker not in full or end_marker not in full:
        print("Template SQL does not contain expected city_lookup markers.")
        return 1
    i = full.index(start_marker)
    j = full.index(end_marker, i) + len("),\n")  # skip "),\n" so rest starts with "-- US state..."
    new_sql = full[:i] + cte + ",\n" + full[j:]

    with open(OUT_SQL, "w", encoding="utf-8") as f:
        f.write(new_sql)
    print(f"Wrote {OUT_SQL} (city_lookup CTE from {MAPPING_CSV}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
