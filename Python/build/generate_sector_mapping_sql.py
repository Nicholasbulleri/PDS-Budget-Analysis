#!/usr/bin/env python3
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

"""Generate sector_mapping CTE SQL from data/sector_mapping.json for use in Spark/Athena SQL.
Output: a single CTE named sector_mapping with columns (raw_lower, canonical_sector).
Match logic: case-insensitive by storing raw values lowercased; unmapped -> 'Special Purpose Facility'.
"""
import json
import os

SECTOR_MAPPING_FILE = os.path.join(PROJECT_ROOT, "data", "sector", "sector_mapping.json")


def main():
    if not os.path.isfile(SECTOR_MAPPING_FILE):
        print("-- ERROR: sector_mapping.json not found at", SECTOR_MAPPING_FILE)
        return
    with open(SECTOR_MAPPING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for canon, raw_list in data.items():
        if canon.startswith("_") or not isinstance(raw_list, list):
            continue
        for raw in raw_list:
            s = (raw or "").strip()
            if s:
                raw_lower = s.lower()
                rows.append((raw_lower, canon))
    # Dedupe by raw_lower (first occurrence wins, which matches Python dict behavior)
    seen = set()
    unique = []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            unique.append(r)
    def sql_row(r):
        # Escape single quote for SQL: ' -> ''
        raw_sql = "'" + r[0].replace("'", "''") + "'"
        canon_sql = "'" + (r[1].replace("'", "''")) + "'"
        return "  (" + raw_sql + ", " + canon_sql + ")"
    values_lines = ",\n".join(sql_row(r) for r in unique)
    print("-- Sector mapping CTE: raw_lower (lowercase trimmed) -> canonical_sector. From sector_mapping.json.")
    print("sector_mapping AS (")
    print("  SELECT raw_lower, canonical_sector FROM (")
    print("    VALUES")
    print(values_lines)
    print("  ) AS t(raw_lower, canonical_sector)")
    print("),")


if __name__ == "__main__":
    main()
