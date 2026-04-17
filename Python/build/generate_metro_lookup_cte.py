#!/usr/bin/env python3
"""
Generate metro_lookup CTE from data/city_to_msa_mapping.json for use in Spark/Athena SQL.
Output: CTE with (city_norm, state_code, metro). state_code is NULL for city-only keys;
for "city|state" keys, state_code is the 2-letter uppercase state (tiebreaker for ambiguous cities).
Join: prefer (city_norm, state_code) match, then (city_norm, NULL).
Regenerate after updating city_to_msa_mapping.json (e.g. via Python/build/build_msa_mapping.py).
"""
import json
import os
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
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "sector")
MSA_JSON = os.path.join(PROJECT_ROOT, "data", "mappings", "city_to_msa_mapping.json")
OUT_SQL = os.path.join(SQL_DIR, "metro_lookup_cte_generated.sql")


def sql_escape(s: str) -> str:
    return (s or "").replace("'", "''")


def main():
    if not os.path.isfile(MSA_JSON):
        print("-- ERROR: city_to_msa_mapping.json not found at", MSA_JSON)
        return 1
    with open(MSA_JSON, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    rows = []
    for key, metro in mapping.items():
        key = (key or "").strip()
        if not key:
            continue
        metro = (metro or "").strip().replace("'", "''")
        if "|" in key:
            city_norm, state_code = key.split("|", 1)
            city_norm = city_norm.strip().lower()
            state_code = state_code.strip().upper()[:2]
            if not city_norm:
                continue
            rows.append((city_norm, state_code, metro))
        else:
            city_norm = key.strip().lower()
            if not city_norm:
                continue
            rows.append((city_norm, None, metro))

    # Dedupe: (city_norm, state_code) -> metro; keep state-specific and city-only
    seen = set()
    unique = []
    for city_norm, state_code, metro in rows:
        k = (city_norm, state_code)
        if k in seen:
            continue
        seen.add(k)
        unique.append((city_norm, state_code, metro))

    def row_sql(r):
        city_norm, state_code, metro = r
        state_sql = f"'{sql_escape(state_code)}'" if state_code else "NULL"
        return f"  ('{sql_escape(city_norm)}', {state_sql}, '{sql_escape(metro)}')"

    lines = [row_sql(r) for r in unique]
    cte = "metro_lookup AS (\n  SELECT city_norm, state_code, metro FROM (\n    VALUES\n" + ",\n".join(lines) + "\n  ) AS t(city_norm, state_code, metro)\n)"
    print("-- Metro lookup CTE from city_to_msa_mapping.json. Regenerate: python3 Python/build/generate_metro_lookup_cte.py")
    print(cte)
    os.makedirs(SQL_DIR, exist_ok=True)
    with open(OUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- From city_to_msa_mapping.json. Regenerate: python3 Python/build/generate_metro_lookup_cte.py\n")
        f.write(cte)
    print(f"\nWrote {OUT_SQL}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
