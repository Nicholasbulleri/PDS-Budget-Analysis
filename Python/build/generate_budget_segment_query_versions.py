#!/usr/bin/env python3
"""
Generate 8 versions of projects_budget_count_and_avg_line_items query:
 1. by_src_sector_type_metro (existing file - most detailed, no trend)
 2. by_src_sector_type
 3. by_src_sector
 4. by_src_type
 5. by_src_sector_type_metro_trend (with year_month; no cost code columns)
 6. by_src_sector_type_trend
 7. by_src_sector_trend
 8. by_src_type_trend

Run from project root. Reads sql/projects_budget_count_and_avg_line_items.sql
and writes sql/projects_budget_segment_by_<suffix>.sql for versions 2-8.
"""
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
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "budget")
SOURCE_SQL = os.path.join(SQL_DIR, "projects_budget_count_and_avg_line_items.sql")

# Segment column sets: (select_columns, group_by_columns, order_by_columns)
# We use placeholder tokens to replace in the SQL.
SEGMENTS = {
    "by_src_sector_type_metro": {
        "select_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type,\n  c.metro",
        "blp_select": "c.sourcesystem,\n    c.sector,\n    c.project_type,\n    c.metro",
        "blp_group": "p.id, c.sourcesystem, c.sector, c.project_type, c.metro",
        "ccu_group": "c.sourcesystem, c.sector, c.project_type, c.metro",
        "partition": "sourcesystem, sector, project_type, metro",
        "join_blp": "AND blp.metro = c.metro",
        "join_cc": "AND cc.metro = c.metro",
        "join_tc": "AND tc.metro = c.metro",
        "join_oc": "AND oc.metro = c.metro",
        "group_by_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type,\n  c.metro",
        "order_by": "c.sourcesystem, c.sector, c.project_type, c.metro",
        "trend": False,
    },
    "by_src_sector_type": {
        "select_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type",
        "blp_select": "c.sourcesystem,\n    c.sector,\n    c.project_type",
        "blp_group": "p.id, c.sourcesystem, c.sector, c.project_type",
        "ccu_group": "c.sourcesystem, c.sector, c.project_type",
        "partition": "sourcesystem, sector, project_type",
        "join_blp": "",
        "join_cc": "",
        "join_tc": "",
        "join_oc": "",
        "group_by_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type",
        "order_by": "c.sourcesystem, c.sector, c.project_type",
        "trend": False,
    },
    "by_src_sector": {
        "select_segment": "c.sourcesystem,\n  c.sector",
        "blp_select": "c.sourcesystem,\n    c.sector",
        "blp_group": "p.id, c.sourcesystem, c.sector",
        "ccu_group": "c.sourcesystem, c.sector",
        "partition": "sourcesystem, sector",
        "join_blp": "",
        "join_cc": "",
        "join_tc": "",
        "join_oc": "",
        "group_by_segment": "c.sourcesystem,\n  c.sector",
        "order_by": "c.sourcesystem, c.sector",
        "trend": False,
    },
    "by_src_type": {
        "select_segment": "c.sourcesystem,\n  c.project_type",
        "blp_select": "c.sourcesystem,\n    c.project_type",
        "blp_group": "p.id, c.sourcesystem, c.project_type",
        "ccu_group": "c.sourcesystem, c.project_type",
        "partition": "sourcesystem, project_type",
        "join_blp": "",
        "join_cc": "",
        "join_tc": "",
        "join_oc": "",
        "group_by_segment": "c.sourcesystem,\n  c.project_type",
        "order_by": "c.sourcesystem, c.project_type",
        "trend": False,
    },
    "by_src_sector_type_metro_trend": {
        "select_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type,\n  c.metro,\n  c.year_month",
        "blp_select": "c.sourcesystem,\n    c.sector,\n    c.project_type,\n    c.metro,\n    c.year_month",
        "blp_group": "p.id, c.sourcesystem, c.sector, c.project_type, c.metro, c.year_month",
        "partition": "sourcesystem, sector, project_type, metro, year_month",
        "join_blp": "AND blp.metro = c.metro\n  AND blp.year_month = c.year_month",
        "group_by_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type,\n  c.metro,\n  c.year_month",
        "order_by": "c.sourcesystem, c.sector, c.project_type, c.metro, c.year_month DESC",
        "trend": True,
    },
    "by_src_sector_type_trend": {
        "select_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type,\n  c.year_month",
        "blp_select": "c.sourcesystem,\n    c.sector,\n    c.project_type,\n    c.year_month",
        "blp_group": "p.id, c.sourcesystem, c.sector, c.project_type, c.year_month",
        "partition": "sourcesystem, sector, project_type, year_month",
        "join_blp": "AND blp.year_month = c.year_month",
        "group_by_segment": "c.sourcesystem,\n  c.sector,\n  c.project_type,\n  c.year_month",
        "order_by": "c.sourcesystem, c.sector, c.project_type, c.year_month DESC",
        "trend": True,
    },
    "by_src_sector_trend": {
        "select_segment": "c.sourcesystem,\n  c.sector,\n  c.year_month",
        "blp_select": "c.sourcesystem,\n    c.sector,\n    c.year_month",
        "blp_group": "p.id, c.sourcesystem, c.sector, c.year_month",
        "partition": "sourcesystem, sector, year_month",
        "join_blp": "AND blp.year_month = c.year_month",
        "group_by_segment": "c.sourcesystem,\n  c.sector,\n  c.year_month",
        "order_by": "c.sourcesystem, c.sector, c.year_month DESC",
        "trend": True,
    },
    "by_src_type_trend": {
        "select_segment": "c.sourcesystem,\n  c.project_type,\n  c.year_month",
        "blp_select": "c.sourcesystem,\n    c.project_type,\n    c.year_month",
        "blp_group": "p.id, c.sourcesystem, c.project_type, c.year_month",
        "partition": "sourcesystem, project_type, year_month",
        "join_blp": "AND blp.year_month = c.year_month",
        "group_by_segment": "c.sourcesystem,\n  c.project_type,\n  c.year_month",
        "order_by": "c.sourcesystem, c.project_type, c.year_month DESC",
        "trend": True,
    },
}


def main():
    with open(SOURCE_SQL, "r", encoding="utf-8") as f:
        sql = f.read()

    # Version 1 is the source file; we generate 2-8
    for suffix, cfg in SEGMENTS.items():
        if suffix == "by_src_sector_type_metro":
            continue
        out_sql = sql

        trend = cfg.get("trend", False)

        # Replace header (version and description)
        version_num = {"by_src_sector_type": 2, "by_src_sector": 3, "by_src_type": 4,
                      "by_src_sector_type_metro_trend": 5, "by_src_sector_type_trend": 6,
                      "by_src_sector_trend": 7, "by_src_type_trend": 8}[suffix]
        group_desc = suffix.replace("_", " ").replace("trend", "(with year_month for trend; no cost code columns)")
        out_sql = re.sub(
            r"-- VERSION 1/8: by_src_sector_type_metro \(most detailed; no trend\)\.",
            f"-- VERSION {version_num}/8: {suffix}.",
            out_sql,
            count=1,
        )

        if trend:
            # Add year_month to base subquery (inner SELECT)
            out_sql = re.sub(
                r"(FROM work_dynamics\.curated\.project p\s+LEFT JOIN work_dynamics\.curated\.property pr ON pr\.id = p\.propertyidentifier\s+WHERE LOWER\(TRIM\(COALESCE\(p\.phasetext, ''\)\)\)) IN \('closed', 'closeout'\))",
                r"DATE_FORMAT(p.sourcecreateddatetime, 'yyyy-MM') AS year_month,\n      \\1",
                out_sql,
                count=1,
            )
            # Fix the replacement - we need to add year_month to the SELECT list before FROM
            out_sql = re.sub(
                r"(p\.propertyidentifier,\s+COALESCE\(NULLIF\(p\.grossarea, 0\), NULLIF\(p\.usablearea, 0\), NULLIF\(p\.rentablearea, 0\)\) AS area)\s+FROM work_dynamics\.curated\.project p",
                r"\\1,\n      DATE_FORMAT(p.sourcecreateddatetime, 'yyyy-MM') AS year_month\n    FROM work_dynamics.curated.project p",
                out_sql,
                count=1,
            )
            # Add year_month to projects_in_scope SELECT
            out_sql = re.sub(
                r"(CASE WHEN base\.area IS NULL OR base\.area <= 0 THEN 1 ELSE 0 END AS missing_area)\s+FROM \(\s+SELECT",
                r"\\1,\n    base.year_month\n  FROM (\n    SELECT",
                out_sql,
                count=1,
            )
            # Add year_month to base columns (inner) - we already added it above
            # Remove the cost code CTEs (from cost_code_usage to closing of segment_cost_code_counts)
            start_marker = "-- Cost code (taskname) usage per segment"
            end_marker = "GROUP BY sourcesystem, sector, project_type, metro\n)"
            idx = out_sql.find(start_marker)
            if idx != -1:
                comma_before = out_sql.rfind(",", 0, idx)
                idx3 = out_sql.find(end_marker, idx)
                if idx3 != -1:
                    end_idx = idx3 + len(end_marker) + 1  # +1 for closing paren
                    out_sql = out_sql[:comma_before] + "\n" + out_sql[end_idx:]

            # Remove cost code columns and joins from final SELECT
            out_sql = re.sub(
                r",\s*COALESCE\(cc\.distinct_cost_codes, 0\) AS distinct_cost_codes_in_segment,\s*COALESCE\(tc\.top_cost_codes_list, ''\) AS top_10_cost_codes,\s*COALESCE\(oc\.overlapping_cost_codes, ''\) AS overlapping_cost_codes_used_in_2plus_projects",
                "",
                out_sql,
            )
            out_sql = re.sub(
                r"LEFT JOIN segment_cost_code_counts cc[\s\S]*?AND oc\.metro = c\.metro\s*",
                "",
                out_sql,
            )
            out_sql = re.sub(
                r"LEFT JOIN segment_top_codes tc[\s\S]*?AND tc\.metro = c\.metro\s*",
                "",
                out_sql,
            )
            out_sql = re.sub(
                r"LEFT JOIN segment_overlapping_codes oc[\s\S]*?AND oc\.metro = c\.metro\s*",
                "",
                out_sql,
            )
            out_sql = re.sub(
                r",\s*cc\.distinct_cost_codes,\s*tc\.top_cost_codes_list,\s*oc\.overlapping_cost_codes",
                "",
                out_sql,
            )

        # Segment column replacements (for both trend and non-trend)
        # Final SELECT segment columns
        out_sql = re.sub(
            r"c\.sourcesystem,\s*c\.sector,\s*c\.project_type,\s*c\.metro",
            cfg["select_segment"].replace("\n", "\n  "),
            out_sql,
            count=1,
        )
        # budget_line_items_per_project SELECT and GROUP BY
        out_sql = re.sub(
            r"c\.sourcesystem,\s*c\.sector,\s*c\.project_type,\s*c\.metro,\s*COUNT\(\*\) AS gt_line_item_count",
            cfg["blp_select"] + ",\n    COUNT(*) AS gt_line_item_count",
            out_sql,
        )
        out_sql = re.sub(
            r"GROUP BY p\.id, c\.sourcesystem, c\.sector, c\.project_type, c\.metro",
            "GROUP BY " + cfg["blp_group"],
            out_sql,
        )

        if not trend:
            # cost_code_usage
            out_sql = re.sub(
                r"c\.sourcesystem,\s*c\.sector,\s*c\.project_type,\s*c\.metro,\s*TRIM\(COALESCE",
                cfg["blp_select"].replace("c.\n", "c.") + ",\n    TRIM(COALESCE",
                out_sql,
            )
            out_sql = re.sub(
                r"GROUP BY c\.sourcesystem, c\.sector, c\.project_type, c\.metro, TRIM\(COALESCE\(CAST\(gt\.taskname AS STRING\), ''\)\)",
                "GROUP BY " + cfg["ccu_group"] + ", TRIM(COALESCE(CAST(gt.taskname AS STRING), ''))",
                out_sql,
            )
            # cost_code_ranked PARTITION BY
            out_sql = re.sub(
                r"PARTITION BY sourcesystem, sector, project_type, metro ORDER BY",
                f"PARTITION BY {cfg['partition']} ORDER BY",
                out_sql,
            )
            # segment_top_codes, segment_overlapping_codes, segment_cost_code_counts - replace sourcesystem, sector, project_type, metro with the segment list
            seg_list = cfg["partition"].replace(", ", ", ")
            for cte in ["segment_top_codes", "segment_overlapping_codes", "segment_cost_code_counts"]:
                out_sql = re.sub(
                    r"(SELECT\s+)sourcesystem,\s*sector,\s*project_type,\s*metro",
                    r"\1" + seg_list.replace(",", ",\n    "),
                    out_sql,
                    count=1,
                )
                out_sql = re.sub(
                    r"GROUP BY sourcesystem, sector, project_type, metro",
                    "GROUP BY " + seg_list,
                    out_sql,
                    count=1,
                )
            # JOIN conditions
            if cfg["join_blp"]:
                out_sql = re.sub(r"AND blp\.metro = c\.metro", cfg["join_blp"], out_sql)
            else:
                out_sql = re.sub(r"\s*AND blp\.metro = c\.metro", "", out_sql)
            out_sql = re.sub(r"\s*AND cc\.metro = c\.metro", "\n  " + cfg["join_cc"] if cfg["join_cc"] else "", out_sql)
            out_sql = re.sub(r"\s*AND tc\.metro = c\.metro", "\n  " + cfg["join_tc"] if cfg["join_tc"] else "", out_sql)
            out_sql = re.sub(r"\s*AND oc\.metro = c\.metro", "\n  " + cfg["join_oc"] if cfg["join_oc"] else "", out_sql)
            # GROUP BY and ORDER BY in final SELECT
            out_sql = re.sub(
                r"c\.sourcesystem,\s*c\.sector,\s*c\.project_type,\s*c\.metro,\s*cc\.distinct_cost_codes",
                cfg["group_by_segment"] + ",\n  cc.distinct_cost_codes",
                out_sql,
            )
            out_sql = re.sub(
                r"ORDER BY c\.sourcesystem, c\.sector, c\.project_type, c\.metro;",
                "ORDER BY " + cfg["order_by"] + ";",
                out_sql,
            )
        else:
            # Trend: blp join may have year_month
            out_sql = re.sub(r"AND blp\.metro = c\.metro", cfg["join_blp"], out_sql)
            out_sql = re.sub(
                r"GROUP BY\s+c\.sourcesystem,\s*c\.sector,\s*c\.project_type,\s*c\.metro,\s*cc\.distinct_cost_codes",
                "GROUP BY\n  " + cfg["group_by_segment"],
                out_sql,
            )
            out_sql = re.sub(
                r"ORDER BY c\.sourcesystem, c\.sector, c\.project_type, c\.metro;",
                "ORDER BY " + cfg["order_by"] + ";",
                out_sql,
            )

        out_path = os.path.join(SQL_DIR, f"projects_budget_segment_{suffix}.sql")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out_sql)
        print(f"Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
