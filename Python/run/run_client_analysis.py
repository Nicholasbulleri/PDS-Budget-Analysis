#!/usr/bin/env python3
"""
Analyze client names and IDs in the project table.
Source systems: Ingenious, Clarizen, FinancialForce, PeopleSoft (excludes Pega).
Columns used: clientname, ovcid (client ID), sourcesystem, and any other client fields found.
Writes results to client_analysis.csv and client_analysis.xlsx.
"""
import csv
import os

try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "analysis")
OUT_CSV  = os.path.join(PROJECT_ROOT, "data", "analysis", "client_analysis.csv")
OUT_XLSX = os.path.join(PROJECT_ROOT, "data", "analysis", "client_analysis.xlsx")

# Unique client list from companyclient master table
# ovc_id = OneView Client ID (the canonical client identifier across JLL systems)
CLIENT_QUERY = """
SELECT
    cc.sourcesystem,
    cc.ovc_id,
    cc.companyclientname                AS client_name,
    cc.sourcecompanyclientidentifier    AS source_client_id,
    cc.statusofclientdescription        AS client_status,
    cc.jllregionname                    AS jll_region,
    COUNT(DISTINCT p.workitemidentifier) AS project_count
FROM work_dynamics.curated.companyclient cc
LEFT JOIN work_dynamics.curated.project p
    ON p.companyidentifier = cc.id
WHERE LOWER(cc.sourcesystem) IN ('ingenious', 'clarizen', 'financialforce', 'peoplesoft')
  AND (cc.is_deleted IS NULL OR cc.is_deleted = 'false')
GROUP BY
    cc.sourcesystem,
    cc.ovc_id,
    cc.companyclientname,
    cc.sourcecompanyclientidentifier,
    cc.statusofclientdescription,
    cc.jllregionname
ORDER BY
    cc.sourcesystem,
    cc.companyclientname NULLS LAST
"""

# Summary counts by source system
SUMMARY_QUERY = """
SELECT
    cc.sourcesystem,
    COUNT(DISTINCT cc.ovc_id)              AS unique_ovc_ids,
    COUNT(DISTINCT cc.companyclientname)   AS unique_client_names,
    COUNT(DISTINCT cc.id)                  AS total_client_records,
    COUNT(DISTINCT p.workitemidentifier)   AS total_linked_projects
FROM work_dynamics.curated.companyclient cc
LEFT JOIN work_dynamics.curated.project p
    ON p.companyidentifier = cc.id
WHERE LOWER(cc.sourcesystem) IN ('ingenious', 'clarizen', 'financialforce', 'peoplesoft')
  AND (cc.is_deleted IS NULL OR cc.is_deleted = 'false')
GROUP BY cc.sourcesystem
ORDER BY total_client_records DESC
"""


def run_query(execute_query, label, sql):
    print(f"\n--- {label} ---")
    cols, rows = execute_query(sql)
    for r in rows:
        print("  " + "  |  ".join(str(v) for v in r))
    return cols, rows


def main():
    from edp_connection import execute_query

    # Summary
    run_query(execute_query, "Summary by source system", SUMMARY_QUERY)

    # Full unique client list
    print("\nRunning full unique client list from companyclient master table...")
    cols, rows = execute_query(CLIENT_QUERY)
    print(f"Retrieved {len(rows)} unique clients.")

    # Write CSV
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    print(f"Written to {OUT_CSV}")

    # Write Excel with two sheets: full list + summary
    try:
        from openpyxl import Workbook
        wb = Workbook()

        # Sheet 1: full client list
        ws1 = wb.active
        ws1.title = "Clients"
        for ci, col in enumerate(cols, 1):
            ws1.cell(row=1, column=ci, value=col)
        for ri, row in enumerate(rows, 2):
            for ci, val in enumerate(row, 1):
                ws1.cell(row=ri, column=ci, value=val)

        # Sheet 2: summary
        ws2 = wb.create_sheet("Summary")
        s_cols, s_rows = execute_query(SUMMARY_QUERY)
        for ci, col in enumerate(s_cols, 1):
            ws2.cell(row=1, column=ci, value=col)
        for ri, row in enumerate(s_rows, 2):
            for ci, val in enumerate(row, 1):
                ws2.cell(row=ri, column=ci, value=val)

        wb.save(OUT_XLSX)
        print(f"Written to {OUT_XLSX}")
    except ImportError:
        import pandas as pd
        df = pd.DataFrame(rows, columns=cols)
        df.to_excel(OUT_XLSX, index=False, sheet_name="Clients")
        print(f"Written to {OUT_XLSX} (via pandas)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
