#!/usr/bin/env python3
"""
Budget band analysis: closed/closeout/construct projects.
Segments projects into 6 budget bands by original_budget_usd.
Reports project count by band + project_type, and avg cost codes per band.
Excludes: USD projects outside the US, projects > $100M (outlier data), $0 budget.
"""

import csv
import sys
from pathlib import Path
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
INPUT_CSV = PROJECT_ROOT / "data" / "dim" / "dim_project_budget_automation.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "budget" / "budget_band_analysis.csv"
OUTPUT_MD = PROJECT_ROOT / "markdown" / "budget_band_analysis.md"

TARGET_PHASES = {"closed", "closeout", "construct", "construction"}
US_COUNTRIES = {"united states", "us", "usa", "united states of america", "puerto rico", ""}
OUTLIER_CEILING = 100_000_000  # $100M

BANDS = [
    ("$0–$50K",          0,          50_000),
    ("$50K–$250K",  50_000,         250_000),
    ("$250K–$1M",  250_000,       1_000_000),
    ("$1M–$5M",  1_000_000,       5_000_000),
    ("$5M–$10M", 5_000_000,      10_000_000),
    ("$10M+",   10_000_000, OUTLIER_CEILING),
]


def get_band(amount):
    for label, lo, hi in BANDS:
        if lo < amount <= hi:
            return label
    if amount <= 0:
        return None
    return BANDS[-1][0]


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def filter_rows(rows):
    kept, excluded_phase, excluded_usd_non_us, excluded_outlier, excluded_zero = [], 0, 0, 0, 0
    for r in rows:
        phase = r.get("phase", "").strip().lower()
        if phase not in TARGET_PHASES:
            excluded_phase += 1
            continue
        budget_usd = float(r.get("original_budget_usd") or 0)
        if budget_usd <= 0:
            excluded_zero += 1
            continue
        if budget_usd > OUTLIER_CEILING:
            excluded_outlier += 1
            continue
        currency = r.get("currency_code", "").strip().upper()
        country = r.get("country", "").strip().lower()
        if currency == "USD" and country not in US_COUNTRIES:
            excluded_usd_non_us += 1
            continue
        kept.append(r)
    return kept, excluded_phase, excluded_usd_non_us, excluded_outlier, excluded_zero


def analyze(rows):
    band_type_counts = defaultdict(lambda: defaultdict(int))
    band_cc_totals = defaultdict(lambda: {"count": 0, "cc_sum": 0})
    band_budget_totals = defaultdict(lambda: {"count": 0, "budget_sum": 0.0})

    for r in rows:
        budget_usd = float(r.get("original_budget_usd") or 0)
        band = get_band(budget_usd)
        if band is None:
            continue
        ptype = r.get("project_type", "(Unspecified)").strip() or "(Unspecified)"
        cc_count = int(r.get("cost_code_line_item_count") or 0)

        band_type_counts[band][ptype] += 1
        band_cc_totals[band]["count"] += 1
        band_cc_totals[band]["cc_sum"] += cc_count
        band_budget_totals[band]["count"] += 1
        band_budget_totals[band]["budget_sum"] += budget_usd

    return band_type_counts, band_cc_totals, band_budget_totals


def write_outputs(rows, band_type_counts, band_cc_totals, band_budget_totals,
                  excluded_phase, excluded_usd_non_us, excluded_outlier, excluded_zero):
    band_order = [b[0] for b in BANDS]
    all_types = sorted({t for band in band_type_counts.values() for t in band})

    # CSV: band, project_type, project_count, avg_cost_codes, avg_budget_usd
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["budget_band", "project_type", "project_count", "avg_cost_codes", "avg_budget_usd"])
        for band in band_order:
            for ptype in all_types:
                cnt = band_type_counts[band].get(ptype, 0)
                if cnt > 0:
                    w.writerow([band, ptype, cnt, "", ""])
            # Band totals
            info = band_cc_totals[band]
            binfo = band_budget_totals[band]
            avg_cc = round(info["cc_sum"] / info["count"], 1) if info["count"] else 0
            avg_bud = round(binfo["budget_sum"] / binfo["count"], 0) if binfo["count"] else 0
            w.writerow([band, "_TOTAL", info["count"], avg_cc, avg_bud])
    print(f"Wrote {OUTPUT_CSV}")

    # Markdown
    lines = [
        "# Budget band analysis: closed/closeout/construct projects",
        "",
        "## Filters applied",
        "",
        f"- Phases: {', '.join(sorted(TARGET_PHASES))}",
        f"- Excluded: USD projects outside the US ({excluded_usd_non_us:,})",
        f"- Excluded: projects > ${OUTLIER_CEILING/1e6:.0f}M (outlier/bad data) ({excluded_outlier:,})",
        f"- Excluded: projects with $0 budget ({excluded_zero:,})",
        f"- Excluded: other phases ({excluded_phase:,})",
        f"- **Included: {len(rows):,} projects**",
        "",
        "---",
        "",
        "## 1. Summary by budget band",
        "",
        "| Budget Band | Projects | Avg Budget (USD) | Avg Cost Codes |",
        "|-------------|----------|------------------|----------------|",
    ]
    for band in band_order:
        info = band_cc_totals[band]
        binfo = band_budget_totals[band]
        cnt = info["count"]
        avg_cc = round(info["cc_sum"] / cnt, 1) if cnt else 0
        avg_bud = round(binfo["budget_sum"] / cnt, 0) if cnt else 0
        lines.append(f"| {band} | {cnt:,} | ${avg_bud:,.0f} | {avg_cc} |")
    total_projects = sum(band_cc_totals[b]["count"] for b in band_order)
    total_cc = sum(band_cc_totals[b]["cc_sum"] for b in band_order)
    total_bud = sum(band_budget_totals[b]["budget_sum"] for b in band_order)
    lines.append(f"| **Total** | **{total_projects:,}** | **${total_bud/total_projects:,.0f}** | **{total_cc/total_projects:.1f}** |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Project count by band and project type",
        "",
    ])
    header = "| Project Type | " + " | ".join(band_order) + " | Total |"
    sep = "|" + "|".join(["---"] * (len(band_order) + 2)) + "|"
    lines.append(header)
    lines.append(sep)
    for ptype in all_types:
        cells = []
        row_total = 0
        for band in band_order:
            c = band_type_counts[band].get(ptype, 0)
            cells.append(f"{c:,}" if c > 0 else "—")
            row_total += c
        lines.append(f"| {ptype} | " + " | ".join(cells) + f" | {row_total:,} |")
    # Column totals
    col_totals = []
    for band in band_order:
        col_totals.append(f"{band_cc_totals[band]['count']:,}")
    lines.append(f"| **Total** | " + " | ".join(col_totals) + f" | **{total_projects:,}** |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Average cost codes per project by band and project type",
        "",
    ])
    # Compute avg cc per band+type
    band_type_cc = defaultdict(lambda: defaultdict(lambda: {"count": 0, "cc_sum": 0}))
    for r in rows:
        budget_usd = float(r.get("original_budget_usd") or 0)
        band = get_band(budget_usd)
        if band is None:
            continue
        ptype = r.get("project_type", "(Unspecified)").strip() or "(Unspecified)"
        cc = int(r.get("cost_code_line_item_count") or 0)
        band_type_cc[band][ptype]["count"] += 1
        band_type_cc[band][ptype]["cc_sum"] += cc

    header2 = "| Project Type | " + " | ".join(band_order) + " |"
    lines.append(header2)
    lines.append(sep)
    for ptype in all_types:
        cells = []
        for band in band_order:
            info = band_type_cc[band][ptype]
            if info["count"] > 0:
                cells.append(f"{info['cc_sum']/info['count']:.1f}")
            else:
                cells.append("—")
        lines.append(f"| {ptype} | " + " | ".join(cells) + " |")

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {OUTPUT_MD}")


def main():
    if not INPUT_CSV.exists():
        print(f"Input not found: {INPUT_CSV}")
        return 1
    all_rows = load_data(INPUT_CSV)
    print(f"Loaded {len(all_rows):,} rows from {INPUT_CSV.name}")

    rows, ex_phase, ex_usd, ex_outlier, ex_zero = filter_rows(all_rows)
    print(f"After filtering: {len(rows):,} projects")
    print(f"  Excluded - wrong phase: {ex_phase:,}")
    print(f"  Excluded - USD non-US: {ex_usd:,}")
    print(f"  Excluded - outlier >$100M: {ex_outlier:,}")
    print(f"  Excluded - $0 budget: {ex_zero:,}")

    band_type_counts, band_cc_totals, band_budget_totals = analyze(rows)
    write_outputs(rows, band_type_counts, band_cc_totals, band_budget_totals,
                  ex_phase, ex_usd, ex_outlier, ex_zero)
    return 0


if __name__ == "__main__":
    sys.exit(main())
