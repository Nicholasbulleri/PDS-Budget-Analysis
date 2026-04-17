#!/usr/bin/env python3
"""
Run Clarizen projects area/city/state/country/property analysis.
Scope: phase Closed and In Progress only. Results segmented by phase.
Executes the 3 queries from clarizen_projects_area_city_country_property_analysis.sql.
Outputs: CSV + markdown report (projects missing property, missing area, missing city/state/country).
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
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "analysis", "clarizen_projects_area_city_country_property_analysis.csv")
OUT_REPORT = os.path.join(DATA_DIR, "clarizen_projects_area_city_country_property_analysis_report.md")


def main():
    from edp_connection import execute_query

    report = []
    csv_rows = []

    phase_filter = "AND LOWER(TRIM(COALESCE(p.phasetext, ''))) IN ('closed', 'in progress')"

    # Query 1: Overall counts by phase (Closed, In Progress)
    q1 = f"""
    WITH base AS (
      SELECT
        p.id,
        TRIM(COALESCE(p.phasetext, '')) AS phasetext,
        COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) AS area,
        TRIM(COALESCE(p.city, '')) AS city,
        TRIM(COALESCE(p.state, '')) AS state,
        TRIM(COALESCE(p.country, '')) AS country,
        p.propertyidentifier
      FROM work_dynamics.curated.project p
      WHERE LOWER(TRIM(COALESCE(p.sourcesystem, ''))) = 'clarizen'
        {phase_filter}
    ),
    with_flags AS (
      SELECT
        id,
        phasetext,
        CASE WHEN area IS NULL OR area <= 0 THEN 1 ELSE 0 END AS missing_area,
        CASE WHEN city = '' THEN 1 ELSE 0 END AS missing_city,
        CASE WHEN state = '' THEN 1 ELSE 0 END AS missing_state,
        CASE WHEN country = '' THEN 1 ELSE 0 END AS missing_country,
        CASE WHEN propertyidentifier IS NULL OR TRIM(CAST(propertyidentifier AS STRING)) = '' THEN 1 ELSE 0 END AS missing_property
      FROM base
    )
    SELECT
      phasetext AS phase,
      COUNT(*) AS total_projects,
      SUM(missing_area) AS missing_area,
      SUM(missing_city) AS missing_city,
      SUM(missing_state) AS missing_state,
      SUM(missing_country) AS missing_country,
      SUM(missing_property) AS missing_property
    FROM with_flags
    GROUP BY phasetext
    ORDER BY phasetext
    """
    _, rows1 = execute_query(q1)
    if not rows1:
        print("Query 1 returned no rows.")
        return 1

    report.append("# Clarizen projects: area, city, state, country, property analysis")
    report.append("")
    report.append("**Scope:** Phase = Closed or In Progress only. Results by phase.")
    report.append("")
    report.append("## 1. Overall counts by phase")
    report.append("")
    report.append("| Phase | Total projects | Missing area | Missing city | Missing state | Missing country | Missing property |")
    report.append("|-------|----------------|--------------|--------------|---------------|-----------------|-------------------|")
    total_all = 0
    miss_area_all = miss_city_all = miss_state_all = miss_country_all = miss_prop_all = 0
    for row in rows1:
        phase = row[0] or ""
        tot = int(row[1] or 0)
        ma = int(row[2] or 0)
        mc = int(row[3] or 0)
        ms = int(row[4] or 0)
        mco = int(row[5] or 0)
        mp = int(row[6] or 0)
        total_all += tot
        miss_area_all += ma
        miss_city_all += mc
        miss_state_all += ms
        miss_country_all += mco
        miss_prop_all += mp
        report.append(f"| {phase} | {tot:,} | {ma:,} | {mc:,} | {ms:,} | {mco:,} | {mp:,} |")
        csv_rows.append({
            "section": "overall", "phase": phase, "total_projects": tot,
            "missing_area": ma, "missing_city": mc, "missing_state": ms, "missing_country": mco, "missing_property": mp
        })
    report.append(f"| **Combined** | **{total_all:,}** | **{miss_area_all:,}** | **{miss_city_all:,}** | **{miss_state_all:,}** | **{miss_country_all:,}** | **{miss_prop_all:,}** |")
    report.append("")
    report.append("| Metric (combined) | Count | % of combined total |")
    report.append("|--------------------|-------|---------------------|")
    for label, val in [
        ("Total projects", total_all),
        ("Missing area", miss_area_all),
        ("Missing city", miss_city_all),
        ("Missing state", miss_state_all),
        ("Missing country", miss_country_all),
        ("Missing property", miss_prop_all),
    ]:
        pct = (100 * val / total_all) if total_all else 0
        report.append(f"| {label} | {val:,} | {pct:.1f}% |")
    report.append("")

    # Query 2: By phase and property status
    q2 = f"""
    WITH base AS (
      SELECT
        p.id,
        TRIM(COALESCE(p.phasetext, '')) AS phasetext,
        CASE WHEN COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NULL
              OR COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) <= 0 THEN 1 ELSE 0 END AS missing_area,
        CASE WHEN TRIM(COALESCE(p.city, '')) = '' THEN 1 ELSE 0 END AS missing_city,
        CASE WHEN TRIM(COALESCE(p.state, '')) = '' THEN 1 ELSE 0 END AS missing_state,
        CASE WHEN TRIM(COALESCE(p.country, '')) = '' THEN 1 ELSE 0 END AS missing_country,
        CASE WHEN p.propertyidentifier IS NULL OR TRIM(CAST(p.propertyidentifier AS STRING)) = '' THEN 1 ELSE 0 END AS missing_property
      FROM work_dynamics.curated.project p
      WHERE LOWER(TRIM(COALESCE(p.sourcesystem, ''))) = 'clarizen'
        {phase_filter}
    )
    SELECT
      phasetext AS phase,
      CASE WHEN missing_property = 1 THEN 'Property missing' ELSE 'Property assigned' END AS property_status,
      COUNT(*) AS total_projects,
      SUM(missing_area) AS missing_area,
      SUM(missing_city) AS missing_city,
      SUM(missing_state) AS missing_state,
      SUM(missing_country) AS missing_country
    FROM base
    GROUP BY phasetext, missing_property
    ORDER BY phasetext, missing_property DESC
    """
    _, rows2 = execute_query(q2)
    report.append("## 2. By phase and property status")
    report.append("")
    report.append("When property is **missing** vs **assigned**, by phase: total projects and counts still missing area, city, state, country.")
    report.append("")
    report.append("| Phase | Property status | Total projects | Missing area | Missing city | Missing state | Missing country |")
    report.append("|-------|-----------------|----------------|--------------|--------------|---------------|-----------------|")
    for row in rows2 or []:
        phase, status = row[0] or "", row[1]
        tot = int(row[2] or 0)
        ma, mc, ms, mco = int(row[3] or 0), int(row[4] or 0), int(row[5] or 0), int(row[6] or 0)
        report.append(f"| {phase} | {status} | {tot:,} | {ma:,} | {mc:,} | {ms:,} | {mco:,} |")
        csv_rows.append({
            "section": "by_property", "phase": phase, "property_status": status, "total_projects": tot,
            "missing_area": ma, "missing_city": mc, "missing_state": ms, "missing_country": mco
        })
    report.append("")
    report.append("**Takeaway:** \"Property assigned\" rows show how often area/city/state/country are still missing even when a property is linked (by phase).")
    report.append("")

    # Query 3: Overlap by phase
    q3 = f"""
    WITH base AS (
      SELECT
        p.id,
        TRIM(COALESCE(p.phasetext, '')) AS phasetext,
        CASE WHEN COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NULL
              OR COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) <= 0 THEN 1 ELSE 0 END AS missing_area,
        CASE WHEN TRIM(COALESCE(p.city, '')) = '' THEN 1 ELSE 0 END AS missing_city,
        CASE WHEN p.propertyidentifier IS NULL OR TRIM(CAST(p.propertyidentifier AS STRING)) = '' THEN 1 ELSE 0 END AS missing_property
      FROM work_dynamics.curated.project p
      WHERE LOWER(TRIM(COALESCE(p.sourcesystem, ''))) = 'clarizen'
        {phase_filter}
    )
    SELECT
      phasetext AS phase,
      'Missing area' AS metric,
      SUM(CASE WHEN missing_area = 1 AND missing_property = 1 THEN 1 ELSE 0 END) AS when_property_missing,
      SUM(CASE WHEN missing_area = 1 AND missing_property = 0 THEN 1 ELSE 0 END) AS when_property_assigned
    FROM base
    GROUP BY phasetext
    UNION ALL
    SELECT
      phasetext,
      'Missing city' AS metric,
      SUM(CASE WHEN missing_city = 1 AND missing_property = 1 THEN 1 ELSE 0 END),
      SUM(CASE WHEN missing_city = 1 AND missing_property = 0 THEN 1 ELSE 0 END)
    FROM base
    GROUP BY phasetext
    ORDER BY phase, metric
    """
    _, rows3 = execute_query(q3)
    report.append("## 3. Relationship by phase: missing area/city vs property")
    report.append("")
    report.append("For projects **missing area** or **missing city**, how many have property missing vs property assigned (by phase).")
    report.append("")
    report.append("| Phase | Metric | When property missing | When property assigned |")
    report.append("|-------|--------|------------------------|-------------------------|")
    for row in rows3 or []:
        phase, metric, w_miss, w_ass = row[0] or "", row[1], int(row[2] or 0), int(row[3] or 0)
        report.append(f"| {phase} | {metric} | {w_miss:,} | {w_ass:,} |")
        csv_rows.append({
            "section": "overlap", "phase": phase, "metric": metric,
            "when_property_missing": w_miss, "when_property_assigned": w_ass
        })
    report.append("")
    report.append("**Takeaway:** \"When property assigned\" = area/city still missing despite having a property; gaps to fill from property or elsewhere.")
    report.append("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("Report written to " + OUT_REPORT)

    if csv_rows:
        keys = [
            "section", "phase", "metric", "property_status", "total_projects",
            "missing_area", "missing_city", "missing_state", "missing_country", "missing_property",
            "when_property_missing", "when_property_assigned"
        ]
        with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(csv_rows)
        print("CSV written to " + OUT_CSV)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
