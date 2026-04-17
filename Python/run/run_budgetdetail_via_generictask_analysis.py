#!/usr/bin/env python3
"""
Run analysis of budgetdetail-for-project via project -> generictask -> budgetdetail.
Executes summary queries and writes a short report (and optional CSV).
"""
import os
import csv

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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "analysis")
OUT_CSV = os.path.join(DATA_DIR, "budgetdetail_via_generictask_analysis.csv")
OUT_REPORT = os.path.join(DATA_DIR, "budgetdetail_via_generictask_analysis_report.md")


def main():
    from edp_connection import execute_query

    report_lines = [
        "# Budgetdetail-for-Project (via Generictask) – Analysis",
        "",
        "Join path: **project** (workitemidentifier) → **generictask** (projectidentifier) → **budgetdetail** (budgetidentifier).",
        "",
    ]
    csv_rows = []

    # 1) Overall totals
    q1 = """
    SELECT
        COUNT(bd.id) AS total_budgetdetail_rows,
        COUNT(DISTINCT p.id) AS distinct_projects,
        COUNT(DISTINCT gt.id) AS distinct_generictasks,
        COUNT(DISTINCT bd.budgetidentifier) AS distinct_budgets
    FROM work_dynamics.curated.project p
    INNER JOIN work_dynamics.curated.generictask gt
        ON gt.projectidentifier = p.workitemidentifier
    INNER JOIN work_dynamics.curated.budgetdetail bd
        ON bd.budgetidentifier = gt.budgetidentifier
    """
    cols1, rows1 = execute_query(q1)
    if not rows1:
        report_lines.extend([
            "## Result",
            "",
            "**No rows returned** from the join. The link `generictask.budgetidentifier = budgetdetail.budgetidentifier` may not hold in your data (e.g. Clarizen may use a different key, or generictask may not have budgetidentifier populated).",
            "",
        ])
        with open(OUT_REPORT, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print("No rows from join. Report written to " + OUT_REPORT)
        return 0

    r1 = rows1[0]
    total_bd = int(r1[0] or 0)
    distinct_projects = int(r1[1] or 0)
    distinct_gt = int(r1[2] or 0)
    distinct_budgets = int(r1[3] or 0)

    report_lines.extend([
        "## 1. Overall (via this join path)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total budgetdetail rows | {total_bd:,} |",
        f"| Distinct projects | {distinct_projects:,} |",
        f"| Distinct generictasks | {distinct_gt:,} |",
        f"| Distinct budgets (budgetidentifier) | {distinct_budgets:,} |",
        "",
    ])
    csv_rows.append({"section": "overall", "metric": "total_budgetdetail_rows", "value": total_bd})
    csv_rows.append({"section": "overall", "metric": "distinct_projects", "value": distinct_projects})
    csv_rows.append({"section": "overall", "metric": "distinct_generictasks", "value": distinct_gt})
    csv_rows.append({"section": "overall", "metric": "distinct_budgets", "value": distinct_budgets})

    # 2) By project source system
    q2 = """
    SELECT
        p.sourcesystem AS project_sourcesystem,
        COUNT(DISTINCT p.id) AS distinct_projects,
        COUNT(bd.id) AS budgetdetail_rows,
        COUNT(DISTINCT bd.budgetidentifier) AS distinct_budgets
    FROM work_dynamics.curated.project p
    INNER JOIN work_dynamics.curated.generictask gt
        ON gt.projectidentifier = p.workitemidentifier
    INNER JOIN work_dynamics.curated.budgetdetail bd
        ON bd.budgetidentifier = gt.budgetidentifier
    GROUP BY p.sourcesystem
    ORDER BY budgetdetail_rows DESC
    """
    cols2, rows2 = execute_query(q2)
    report_lines.append("## 2. By project source system")
    report_lines.append("")
    report_lines.append("| Project source | Distinct projects | Budgetdetail rows | Distinct budgets |")
    report_lines.append("|----------------|--------------------|-------------------|------------------|")
    for row in rows2 or []:
        report_lines.append(f"| {row[0] or '(NULL)'} | {int(row[1] or 0):,} | {int(row[2] or 0):,} | {int(row[3] or 0):,} |")
        csv_rows.append({"section": "by_project_source", "source": str(row[0] or ""), "distinct_projects": row[1], "budgetdetail_rows": row[2], "distinct_budgets": row[3]})
    report_lines.append("")

    # 3) By budgetdetail source system
    q3 = """
    SELECT
        bd.sourcesystem AS budgetdetail_sourcesystem,
        COUNT(DISTINCT p.id) AS distinct_projects,
        COUNT(bd.id) AS budgetdetail_rows
    FROM work_dynamics.curated.project p
    INNER JOIN work_dynamics.curated.generictask gt
        ON gt.projectidentifier = p.workitemidentifier
    INNER JOIN work_dynamics.curated.budgetdetail bd
        ON bd.budgetidentifier = gt.budgetidentifier
    GROUP BY bd.sourcesystem
    ORDER BY budgetdetail_rows DESC
    """
    cols3, rows3 = execute_query(q3)
    report_lines.append("## 3. By budgetdetail source system")
    report_lines.append("")
    report_lines.append("| Budgetdetail source | Distinct projects | Budgetdetail rows |")
    report_lines.append("|---------------------|--------------------|-------------------|")
    for row in rows3 or []:
        report_lines.append(f"| {row[0] or '(NULL)'} | {int(row[1] or 0):,} | {int(row[2] or 0):,} |")
    report_lines.append("")

    # 4) Distribution of budgetdetail rows per project
    q4 = """
    SELECT bucket, project_count
    FROM (
        SELECT
            CASE
                WHEN cnt BETWEEN 1 AND 5 THEN '1-5'
                WHEN cnt BETWEEN 6 AND 20 THEN '6-20'
                WHEN cnt BETWEEN 21 AND 100 THEN '21-100'
                ELSE '101+'
            END AS bucket,
            COUNT(*) AS project_count
        FROM (
            SELECT p.id, COUNT(bd.id) AS cnt
            FROM work_dynamics.curated.project p
            INNER JOIN work_dynamics.curated.generictask gt
                ON gt.projectidentifier = p.workitemidentifier
            INNER JOIN work_dynamics.curated.budgetdetail bd
                ON bd.budgetidentifier = gt.budgetidentifier
            GROUP BY p.id
        ) per_project
        GROUP BY 1
    ) t
    ORDER BY CASE bucket WHEN '1-5' THEN 1 WHEN '6-20' THEN 2 WHEN '21-100' THEN 3 WHEN '101+' THEN 4 ELSE 5 END
    """
    cols4, rows4 = execute_query(q4)
    report_lines.append("## 4. Budgetdetail rows per project (distribution)")
    report_lines.append("")
    report_lines.append("| Rows per project | Project count |")
    report_lines.append("|------------------|---------------|")
    for row in rows4 or []:
        report_lines.append(f"| {row[0]} | {int(row[1] or 0):,} |")
    report_lines.append("")

    # Interpretation
    report_lines.extend([
        "## 5. Interpretation",
        "",
        "- **If totals are 0**: The join `generictask.budgetidentifier = budgetdetail.budgetidentifier` likely does not match in your schema (e.g. Clarizen uses a different key, or generictask has no budgetidentifier). Consider joining budgetdetail to project directly via `budgetdetail.projectidentifier = project.id` where that is populated (e.g. Ingenious).",
        "- **If only Ingenious has rows**: Consistent with curated findings that Clarizen budgetdetail often has NULL projectidentifier; the generictask→budgetdetail link may exist only for Ingenious.",
        "- **If both sources have rows**: The join path is valid for both; you can use the detail query filtered by project to list all budgetdetail lines for a given project.",
        "",
    ])

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("Report written to " + OUT_REPORT)

    # Write CSV (flat for by_project_source)
    if csv_rows:
        keys = ["section", "metric", "value", "source", "distinct_projects", "budgetdetail_rows", "distinct_budgets"]
        with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(csv_rows)
        print("CSV written to " + OUT_CSV)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
