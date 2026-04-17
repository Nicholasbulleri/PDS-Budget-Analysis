#!/usr/bin/env python3
"""
Analyze cost_code_master_mapping output to identify the most relevant cost codes per source system.

Uses construct-only, no-currency mapping: cost_code_master_mapping_construct_only_no_curr.csv
(run run_cost_code_master_mapping_construct_only_no_curr.py first).

- By budget: for each source, which cost codes account for the most budget (and how many cover 80%/90%/95%).
- By usage: which cost codes appear most often (task_row_count as proxy for projects/lines).
- Summary: how many unique cost codes are "really used" (meaningful budget or usage).
"""

import csv
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cost_codes")
INPUT_CSV = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_master_mapping_construct_only_no_curr.csv")
OUT_SUMMARY_CSV = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_relevance_summary_construct_only_no_curr.csv")
OUT_TOP_BUDGET_CSV = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_top_by_budget_by_source_construct_only_no_curr.csv")
OUT_TOP_USAGE_CSV = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_top_by_usage_by_source_construct_only_no_curr.csv")
OUT_DETAIL_CSV = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_relevance_detail_construct_only_no_curr.csv")
TOP_N = 50  # top N cost codes per source by budget and by usage


def load_data(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r)


def to_num(s: str, default=0):
    if s is None or s == "":
        return default
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return default


def main():
    if not os.path.isfile(INPUT_CSV):
        print(f"Missing {INPUT_CSV}. Run run_cost_code_master_mapping_construct_only_no_curr.py first.")
        return 1

    rows = load_data(INPUT_CSV)
    print(f"Loaded {len(rows)} rows from cost_code_master_mapping_construct_only_no_curr.csv")

    # Aggregate per (sourcesystem, taskname): sum budget and task_row_count; keep first category
    by_source_task: Dict[Tuple[str, str], dict] = defaultdict(lambda: {
        "total_original_budget": 0.0,
        "total_task_row_count": 0,
        "cost_code_category": None,
        "currencies": set(),
    })
    for r in rows:
        src = (r.get("sourcesystem") or "").strip()
        task = (r.get("taskname") or "").strip()
        key = (src, task)
        by_source_task[key]["total_original_budget"] += to_num(r.get("total_original_budget"))
        by_source_task[key]["total_task_row_count"] += int(to_num(r.get("task_row_count"), 0))
        if by_source_task[key]["cost_code_category"] is None:
            by_source_task[key]["cost_code_category"] = (r.get("cost_code_category") or "").strip()
        # Support both currency_bucket (grouped) and no-currency (construct_only_no_curr) CSVs
        curr = (r.get("currency_bucket") or r.get("currency") or "").strip()
        by_source_task[key]["currencies"].add(curr if curr else "all")

    # Build per-source lists (taskname, budget, task_row_count, category)
    by_source: Dict[str, List[dict]] = defaultdict(list)
    for (src, task), v in by_source_task.items():
        by_source[src].append({
            "taskname": task,
            "total_original_budget": v["total_original_budget"],
            "total_task_row_count": v["total_task_row_count"],
            "cost_code_category": v["cost_code_category"] or "",
            "currencies": ";".join(sorted(v["currencies"])),
        })

    summary_rows = []
    detail_rows = []
    top_budget_rows = []
    top_usage_rows = []

    for source in sorted(by_source.keys()):
        items = by_source[source]
        total_budget = sum(x["total_original_budget"] for x in items)
        total_task_rows = sum(x["total_task_row_count"] for x in items)
        n_codes = len(items)

        # Sort by budget descending for cumulative %
        by_budget = sorted(items, key=lambda x: x["total_original_budget"], reverse=True)
        cum = 0.0
        n_80 = n_90 = n_95 = None
        for i, x in enumerate(by_budget):
            cum += x["total_original_budget"]
            pct = (cum / total_budget * 100) if total_budget else 0
            if n_80 is None and pct >= 80:
                n_80 = i + 1
            if n_90 is None and pct >= 90:
                n_90 = i + 1
            if n_95 is None and pct >= 95:
                n_95 = i + 1

        summary_rows.append({
            "sourcesystem": source,
            "unique_cost_codes": n_codes,
            "total_original_budget": round(total_budget, 2),
            "total_task_row_count": total_task_rows,
            "n_codes_80pct_budget": n_80 or n_codes,
            "n_codes_90pct_budget": n_90 or n_codes,
            "n_codes_95pct_budget": n_95 or n_codes,
        })

        # Detail: each cost code with rank by budget and by usage
        by_usage = sorted(items, key=lambda x: x["total_task_row_count"], reverse=True)
        budget_rank = {x["taskname"]: i + 1 for i, x in enumerate(by_budget)}
        usage_rank = {x["taskname"]: i + 1 for i, x in enumerate(by_usage)}
        cum_budget = 0.0
        for x in by_budget:
            cum_budget += x["total_original_budget"]
            pct_cum = (cum_budget / total_budget * 100) if total_budget else 0
            detail_rows.append({
                "sourcesystem": source,
                "taskname": x["taskname"],
                "cost_code_category": x["cost_code_category"],
                "total_original_budget": x["total_original_budget"],
                "total_task_row_count": x["total_task_row_count"],
                "currencies": x["currencies"],
                "rank_by_budget": budget_rank[x["taskname"]],
                "rank_by_usage": usage_rank[x["taskname"]],
                "cumulative_pct_budget": round(pct_cum, 2),
            })

        for i, x in enumerate(by_budget[:TOP_N]):
            top_budget_rows.append({
                "sourcesystem": source,
                "rank": i + 1,
                "taskname": x["taskname"],
                "cost_code_category": x["cost_code_category"],
                "total_original_budget": x["total_original_budget"],
                "total_task_row_count": x["total_task_row_count"],
                "pct_of_source_budget": round(x["total_original_budget"] / total_budget * 100, 2) if total_budget else 0,
            })
        for i, x in enumerate(by_usage[:TOP_N]):
            top_usage_rows.append({
                "sourcesystem": source,
                "rank": i + 1,
                "taskname": x["taskname"],
                "cost_code_category": x["cost_code_category"],
                "total_task_row_count": x["total_task_row_count"],
                "total_original_budget": x["total_original_budget"],
                "pct_of_source_usage": round(x["total_task_row_count"] / total_task_rows * 100, 2) if total_task_rows else 0,
            })

    # Write CSVs
    def write_csv(path: str, rows: List[dict], fieldnames: Optional[List[str]] = None):
        if not rows:
            return
        fn = fieldnames or list(rows[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"Written {len(rows)} rows to {path}")

    write_csv(OUT_SUMMARY_CSV, summary_rows)
    write_csv(OUT_TOP_BUDGET_CSV, top_budget_rows)
    write_csv(OUT_TOP_USAGE_CSV, top_usage_rows)
    write_csv(OUT_DETAIL_CSV, detail_rows)

    # Optional: single Excel with multiple sheets
    out_xlsx = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_relevance_analysis_construct_only_no_curr.xlsx")
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Summary"
        for c, col in enumerate(summary_rows[0].keys(), 1):
            ws.cell(row=1, column=c, value=col)
        for r, row in enumerate(summary_rows, 2):
            for c, val in enumerate(row.values(), 1):
                ws.cell(row=r, column=c, value=val)
        for sheet_name, sheet_rows, key in [
            ("Top by budget", top_budget_rows, list(top_budget_rows[0].keys()) if top_budget_rows else []),
            ("Top by usage", top_usage_rows, list(top_usage_rows[0].keys()) if top_usage_rows else []),
        ]:
            s = wb.create_sheet(sheet_name[:31])
            for c, col in enumerate(key, 1):
                s.cell(row=1, column=c, value=col)
            for r, row in enumerate(sheet_rows, 2):
                for c, col in enumerate(key, 1):
                    s.cell(row=r, column=c, value=row.get(col))
        wb.save(out_xlsx)
        print(f"Excel: {out_xlsx}")
    except Exception as e:
        pass  # CSV is enough if openpyxl fails

    # Console summary
    print("\n--- Summary by source system ---")
    for r in summary_rows:
        print(f"\n{r['sourcesystem']}:")
        print(f"  Unique cost codes (taskname): {r['unique_cost_codes']}")
        print(f"  Total original budget (local currencies): {r['total_original_budget']:,.0f}")
        print(f"  Total task rows (usage): {r['total_task_row_count']:,}")
        print(f"  Cost codes that account for 80% of budget: {r['n_codes_80pct_budget']} ({100*r['n_codes_80pct_budget']/r['unique_cost_codes']:.1f}% of codes)")
        print(f"  Cost codes that account for 90% of budget: {r['n_codes_90pct_budget']}")
        print(f"  Cost codes that account for 95% of budget: {r['n_codes_95pct_budget']}")

    total_records = len(rows)
    total_unique_codes = len(by_source_task)
    print(f"\n--- Overall ---")
    print(f"Input records (source + currency + taskname + category): {total_records:,}")
    print(f"Unique cost codes across all sources (source + taskname): {total_unique_codes:,}")

    # "Really used" summary
    n_80_clarizen = next((r["n_codes_80pct_budget"] for r in summary_rows if r["sourcesystem"] == "clarizen"), 0)
    n_80_ingenious = next((r["n_codes_80pct_budget"] for r in summary_rows if r["sourcesystem"] == "ingenious"), 0)
    print(f"\n--- Most relevant cost codes (budget significance) ---")
    print(f"To cover 80% of budget: Clarizen uses {n_80_clarizen} cost codes (of {next(r['unique_cost_codes'] for r in summary_rows if r['sourcesystem']=='clarizen')}); Ingenious uses {n_80_ingenious} (of {next(r['unique_cost_codes'] for r in summary_rows if r['sourcesystem']=='ingenious')}).")
    print(f"So out of ~18.6k unique (source+taskname) records, only ~{n_80_clarizen + n_80_ingenious} codes drive 80% of budget in each system; the rest are long-tail.")
    print(f"\nOutputs (construct only, no currency):")
    print(f"  Summary: {OUT_SUMMARY_CSV}")
    print(f"  Top by budget (top {TOP_N} per source): {OUT_TOP_BUDGET_CSV}")
    print(f"  Top by usage (top {TOP_N} per source): {OUT_TOP_USAGE_CSV}")
    print(f"  Full detail (ranks + cumulative %): {OUT_DETAIL_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
