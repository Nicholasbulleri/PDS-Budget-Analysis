#!/usr/bin/env python3
"""
Projects with/without sector by source system (Clarizen, Ingenious).
Population: Closed USD, with budget in generictask (no area requirement).
  Sector = p.sector; for Clarizen when null/blank, from property usageTypeSourceValue.
Outputs: CSV + markdown report with count and % of total per source (with sector / without sector).
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))
except (ImportError, PermissionError, FileNotFoundError):
    pass

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
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "projects")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "projects")
SQL_FILE = os.path.join(SQL_DIR, "projects_sector_availability_by_source.sql")
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "projects", "projects_sector_availability_by_source.csv")
OUT_REPORT = os.path.join(DATA_DIR, "projects_sector_availability_by_source_report.md")


def main():
    from edp_connection import execute_query

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        query = f.read().strip()

    print("Running projects sector availability by source (same logic as sector mapping script)...")
    columns, rows = execute_query(query)
    if not rows:
        print("No rows returned.")
        return 1

    # Build per-source totals and rows with pct
    by_source = {}  # source -> { "With sector": count, "Without sector": count }
    report_rows = []
    for row in rows:
        source = (row[0] or "").strip()
        status = (row[1] or "").strip()
        count = int(row[2] or 0)
        if source not in by_source:
            by_source[source] = {"With sector": 0, "Without sector": 0}
        by_source[source][status] = count
        report_rows.append({"sourcesystem": source, "sector_status": status, "project_count": count})

    # Add total and pct per source to each row
    for r in report_rows:
        src = r["sourcesystem"]
        total = by_source[src]["With sector"] + by_source[src]["Without sector"]
        r["total_projects"] = total
        r["pct_of_total"] = round((100 * r["project_count"] / total), 1) if total else 0

    # Write CSV
    import csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sourcesystem", "sector_status", "project_count", "total_projects", "pct_of_total"])
        w.writeheader()
        w.writerows(report_rows)
    print("CSV written to " + OUT_CSV)

    # Markdown report
    lines = [
        "# Projects with/without sector by source system",
        "",
        "**Population:** Closed USD, with budget in generictask (no area requirement).",
        "**Sector:** From `p.sector`; for Clarizen when null/blank, derived from property `usageTypeSourceValue`.",
        "",
        "## Count and % of total by source",
        "",
    ]
    for src in sorted(by_source.keys()):
        with_count = by_source[src]["With sector"]
        without_count = by_source[src]["Without sector"]
        total = with_count + without_count
        pct_with = (100 * with_count / total) if total else 0
        pct_without = (100 * without_count / total) if total else 0
        lines.append(f"### {src.capitalize()}")
        lines.append("")
        lines.append(f"| Sector status   | Count   | % of total |")
        lines.append(f"|-----------------|--------|------------|")
        lines.append(f"| With sector     | {with_count:,} | {pct_with:.1f}% |")
        lines.append(f"| Without sector  | {without_count:,} | {pct_without:.1f}% |")
        lines.append(f"| **Total**       | **{total:,}** | 100% |")
        lines.append("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Report written to " + OUT_REPORT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
