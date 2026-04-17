#!/usr/bin/env python3
"""
Analyze cost code mapping: utilization distribution and tiers for leadership.

Uses construct-only, no-currency mapping: cost_code_master_mapping_construct_only_no_curr.csv
(run run_cost_code_master_mapping_construct_only_no_curr.py first).

- Distribution: histogram of cost codes by distinct_projects (1, 2-5, 6-10, ...).
- Tiers: High (10+ projects), Medium (2-9), Low (1 project).
- Outputs: CSV distributions, tier assignment, summary stats, and a Markdown report.
  Optional: histogram chart (PNG) if matplotlib is available.
"""
import csv
import os
from collections import defaultdict

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
OUT_DISTRIBUTION = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_utilization_distribution_construct_only_no_curr.csv")
OUT_TIERS = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_utilization_tiers_construct_only_no_curr.csv")
OUT_SUMMARY = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_utilization_summary_construct_only_no_curr.csv")
OUT_REPORT = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_utilization_report_construct_only_no_curr.md")


def to_num(s, default=0):
    if s is None or s == "":
        return default
    try:
        return float(str(s).replace(",", ""))
    except (ValueError, TypeError):
        return default


def to_int(s, default=0):
    return int(round(to_num(s, default)))


def project_bucket(projects: int) -> str:
    if projects <= 1:
        return "1"
    if projects <= 5:
        return "2-5"
    if projects <= 10:
        return "6-10"
    if projects <= 25:
        return "11-25"
    if projects <= 50:
        return "26-50"
    if projects <= 100:
        return "51-100"
    return "101+"


def utilization_tier(projects: int) -> str:
    if projects <= 1:
        return "Low (1 project)"
    if projects < 10:
        return "Medium (2-9 projects)"
    return "High (10+ projects)"


BUCKET_ORDER = ["1", "2-5", "6-10", "11-25", "26-50", "51-100", "101+"]


def load_rows(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    if not os.path.isfile(INPUT_CSV):
        print(f"Missing {INPUT_CSV}. Run run_cost_code_master_mapping_construct_only_no_curr.py first.")
        return 1

    rows = load_rows(INPUT_CSV)
    n = len(rows)
    print(f"Loaded {n:,} rows from cost_code_master_mapping_construct_only_no_curr.csv")

    # Normalize and add derived fields
    for r in rows:
        r["_projects"] = to_int(r.get("distinct_projects"), 1)
        r["_budget"] = to_num(r.get("total_original_budget"), 0)
        r["_project_bucket"] = project_bucket(r["_projects"])
        r["_tier"] = utilization_tier(r["_projects"])

    # --- Distribution: count of cost codes by (sourcesystem, currency_bucket, project_bucket) ---
    # currency_bucket may be absent (construct_only_no_curr); use "" then
    dist_counts = defaultdict(int)  # (source, currency, bucket) -> count
    dist_overall = defaultdict(int)  # bucket -> count (overall)
    for r in rows:
        currency = (r.get("currency_bucket") or "").strip() or "all"
        key = (r.get("sourcesystem") or "", currency, r["_project_bucket"])
        dist_counts[key] += 1
        dist_overall[r["_project_bucket"]] += 1

    dist_rows = []
    for (source, currency, bucket), count in sorted(dist_counts.items()):
        total_in_slice = sum(v for (s, cur, b), v in dist_counts.items() if (s, cur) == (source, currency))
        pct = 100.0 * count / total_in_slice if total_in_slice else 0
        dist_rows.append({
            "sourcesystem": source,
            "currency_bucket": currency or "all",
            "project_bucket": bucket,
            "cost_code_count": count,
            "pct_of_source_currency": round(pct, 1),
        })
    # Add overall row (sourcesystem=ALL, currency_bucket=ALL)
    for bucket in BUCKET_ORDER:
        count = dist_overall.get(bucket, 0)
        pct = 100.0 * count / n if n else 0
        dist_rows.append({
            "sourcesystem": "ALL",
            "currency_bucket": "ALL",
            "project_bucket": bucket,
            "cost_code_count": count,
            "pct_of_source_currency": round(pct, 1),
        })

    with open(OUT_DISTRIBUTION, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sourcesystem", "currency_bucket", "project_bucket", "cost_code_count", "pct_of_source_currency"])
        w.writeheader()
        w.writerows(dist_rows)
    print(f"Written {OUT_DISTRIBUTION}")

    # --- Tiers: each cost code row with tier (for filtering / pivot) ---
    tier_rows = []
    for r in rows:
        tier_rows.append({
            "sourcesystem": r.get("sourcesystem", ""),
            "currency_bucket": r.get("currency_bucket", "").strip() or "all",
            "taskname": r.get("taskname", ""),
            "cost_code_category": r.get("cost_code_category", ""),
            "distinct_projects": r["_projects"],
            "task_row_count": to_int(r.get("task_row_count")),
            "total_original_budget": round(r["_budget"], 2),
            "utilization_tier": r["_tier"],
            "project_bucket": r["_project_bucket"],
        })
    with open(OUT_TIERS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "sourcesystem", "currency_bucket", "taskname", "cost_code_category",
            "distinct_projects", "task_row_count", "total_original_budget",
            "utilization_tier", "project_bucket",
        ])
        w.writeheader()
        w.writerows(tier_rows)
    print(f"Written {OUT_TIERS}")

    # --- Summary for leadership: tier counts and high-level stats by source/currency ---
    tier_counts = defaultdict(lambda: defaultdict(int))  # (source, currency) -> {tier: count}
    for r in rows:
        currency = (r.get("currency_bucket") or "").strip() or "all"
        key = (r.get("sourcesystem") or "", currency)
        tier_counts[key][r["_tier"]] += 1
    summary_rows = []
    for (source, currency), tiers in sorted(tier_counts.items()):
        total = sum(tiers.values())
        for tier in ["High (10+ projects)", "Medium (2-9 projects)", "Low (1 project)"]:
            count = tiers.get(tier, 0)
            pct = 100.0 * count / total if total else 0
            summary_rows.append({
                "sourcesystem": source,
                "currency_bucket": currency,
                "utilization_tier": tier,
                "cost_code_count": count,
                "pct": round(pct, 1),
                "total_cost_codes": total,
            })
    # Overall
    overall_tiers = defaultdict(int)
    for r in rows:
        overall_tiers[r["_tier"]] += 1
    for tier in ["High (10+ projects)", "Medium (2-9 projects)", "Low (1 project)"]:
        count = overall_tiers.get(tier, 0)
        summary_rows.append({
            "sourcesystem": "ALL",
            "currency_bucket": "ALL",
            "utilization_tier": tier,
            "cost_code_count": count,
            "pct": round(100.0 * count / n, 1),
            "total_cost_codes": n,
        })
    with open(OUT_SUMMARY, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sourcesystem", "currency_bucket", "utilization_tier", "cost_code_count", "pct", "total_cost_codes"])
        w.writeheader()
        w.writerows(summary_rows)
    print(f"Written {OUT_SUMMARY}")

    # --- Markdown report ---
    low_count = sum(1 for r in rows if r["_tier"] == "Low (1 project)")
    med_count = sum(1 for r in rows if r["_tier"] == "Medium (2-9 projects)")
    high_count = sum(1 for r in rows if r["_tier"] == "High (10+ projects)")
    pct_low = 100.0 * low_count / n
    pct_med = 100.0 * med_count / n
    pct_high = 100.0 * high_count / n

    md = []
    md.append("# Cost Code Utilization Analysis")
    md.append("")
    md.append("Based on **cost_code_master_mapping_construct_only_no_curr.csv** (Construct only, no currency grouping, Clarizen + Ingenious).")
    md.append("")
    md.append("## Executive Summary")
    md.append("")
    md.append(f"- **Total cost code × source combinations:** {n:,}")
    md.append(f"- **Low utilization (1 project):** {low_count:,} ({pct_low:.1f}%) — cost codes used on a single project only.")
    md.append(f"- **Medium utilization (2–9 projects):** {med_count:,} ({pct_med:.1f}%) — used across a few projects.")
    md.append(f"- **High utilization (10+ projects):** {high_count:,} ({pct_high:.1f}%) — widely used; good candidates for standardization.")
    md.append("")
    md.append("## Distribution (Histogram): Cost Codes by Number of Projects")
    md.append("")
    md.append("| Project bucket | # Cost codes | % of total |")
    md.append("|----------------|-------------:|-----------:|")
    for bucket in BUCKET_ORDER:
        c = dist_overall.get(bucket, 0)
        p = 100.0 * c / n if n else 0
        md.append(f"| {bucket} | {c:,} | {p:.1f}% |")
    md.append("")
    md.append("## Utilization Tiers by Source & Currency")
    md.append("")
    md.append("| Source | Currency | Tier | Count | % |")
    md.append("|--------|----------|------|------:|--:|")
    for (source, currency), tiers in sorted(tier_counts.items()):
        total = sum(tiers.values())
        for tier in ["High (10+ projects)", "Medium (2-9 projects)", "Low (1 project)"]:
            count = tiers.get(tier, 0)
            pct = 100.0 * count / total if total else 0
            md.append(f"| {source} | {currency} | {tier} | {count:,} | {pct:.1f}% |")
    md.append("")
    md.append("## Output Files")
    md.append("")
    md.append("- **cost_code_utilization_distribution_construct_only_no_curr.csv** — Histogram: cost code count by project bucket and by source.")
    md.append("- **cost_code_utilization_tiers_construct_only_no_curr.csv** — Every cost code row with utilization_tier and project_bucket.")
    md.append("- **cost_code_utilization_summary_construct_only_no_curr.csv** — Tier counts and percentages by source.")
    md.append("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Written {OUT_REPORT}")

    # --- Optional: histogram chart ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        buckets_ordered = BUCKET_ORDER
        counts = [dist_overall.get(b, 0) for b in buckets_ordered]
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(buckets_ordered, counts, color=["#d62728" if b == "1" else "#ff7f0e" if b in ("2-5", "6-10") else "#2ca02c" for b in buckets_ordered], edgecolor="gray")
        ax.set_xlabel("Number of projects (distinct projects per cost code)")
        ax.set_ylabel("Number of cost codes")
        ax.set_title("Cost Code Utilization (Construct Only, No Currency): Distribution by Distinct Project Count")
        for bar, c in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50, f"{c:,}", ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        chart_path = os.path.join(PROJECT_ROOT, "data", "cost_codes", "cost_code_utilization_histogram_construct_only_no_curr.png")
        plt.savefig(chart_path, dpi=120)
        plt.close()
        print(f"Written {chart_path}")
    except ImportError:
        print("Skipping histogram PNG (matplotlib not installed).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
