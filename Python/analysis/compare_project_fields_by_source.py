#!/usr/bin/env python3
"""
Compare project table fields across source systems using the profile CSV.
- Identifies fields that are never used (0% complete in every source).
- For each field: best/worst source by completeness, spread, and which sources populate it.
Input: data/project_table_data_profile_by_source.csv (from profile_project_table_by_source.py)
Output: data/project_field_comparison_by_source.csv, markdown/project_field_comparison_by_source.md
"""

import csv
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
INPUT_CSV = PROJECT_ROOT / "data" / "profiling" / "project_table_data_profile_by_source.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "profiling" / "project_field_comparison_by_source.csv"
OUTPUT_MD = PROJECT_ROOT / "markdown" / "project_field_comparison_by_source.md"


def load_profile_csv(path: Path):
    """Load profile CSV; return list of dicts, and set of source systems seen."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    sources = sorted({r["source_system"] for r in rows if r.get("source_system") and r["source_system"] not in ("_error",)})
    return rows, sources


def build_column_stats(rows, sources):
    """
    For each column: data_type, is_id, and per-source pct_complete / non_null_count / row_count.
    Return: dict column_name -> { data_type, is_id_or_reference, sources: { src -> { pct, non_null, row_count } } }
    """
    by_col = defaultdict(lambda: {"data_type": "", "is_id_or_reference": "", "sources": {}})
    for r in rows:
        col = r.get("column_name", "").strip()
        if not col:
            continue
        by_col[col]["data_type"] = r.get("data_type", "")
        by_col[col]["is_id_or_reference"] = r.get("is_id_or_reference", "")
        src = (r.get("source_system") or "").strip() or "(blank)"
        if src == "_error":
            continue
        try:
            pct = float(r.get("pct_complete") or 0)
        except (TypeError, ValueError):
            pct = 0
        try:
            non_null = int(r.get("non_null_count") or 0)
        except (TypeError, ValueError):
            non_null = 0
        try:
            row_count = int(r.get("row_count") or 0)
        except (TypeError, ValueError):
            row_count = 0
        by_col[col]["sources"][src] = {"pct_complete": pct, "non_null_count": non_null, "row_count": row_count}
    return dict(by_col), sources


def analyze_column(column_name, meta, sources):
    """
    Return dict: never_used, best_source, best_pct, worst_source, worst_pct, spread,
                 sources_with_data (count), source_pcts (for reporting).
    """
    src_data = meta.get("sources", {})
    pcts = [(src, src_data.get(src, {}).get("pct_complete", 0)) for src in sources]
    pcts = [(s, p) for s, p in pcts if p is not None]
    if not pcts:
        return {
            "column_name": column_name,
            "data_type": meta.get("data_type", ""),
            "is_id_or_reference": meta.get("is_id_or_reference", ""),
            "never_used": True,
            "best_source": "",
            "best_pct": 0,
            "worst_source": "",
            "worst_pct": 0,
            "spread": 0,
            "sources_with_data": 0,
            "source_pcts": {},
        }
    best = max(pcts, key=lambda x: x[1])
    worst = min(pcts, key=lambda x: x[1])
    sources_with_data = sum(1 for _, p in pcts if p > 0)
    never_used = sources_with_data == 0
    return {
        "column_name": column_name,
        "data_type": meta.get("data_type", ""),
        "is_id_or_reference": meta.get("is_id_or_reference", ""),
        "never_used": never_used,
        "best_source": best[0],
        "best_pct": best[1],
        "worst_source": worst[0],
        "worst_pct": worst[1],
        "spread": round(best[1] - worst[1], 1),
        "sources_with_data": sources_with_data,
        "source_pcts": dict(meta.get("sources", {})),
    }


def run_comparison(input_path: Path):
    rows, sources = load_profile_csv(input_path)
    if not rows:
        return [], [], []
    by_col, sources = build_column_stats(rows, sources)
    comparison = []
    for col_name in sorted(by_col.keys()):
        stats = analyze_column(col_name, by_col[col_name], sources)
        comparison.append(stats)
    never_used = [c for c in comparison if c["never_used"]]
    used_by_some = [c for c in comparison if not c["never_used"]]
    return comparison, never_used, used_by_some, sources


def write_comparison_csv(comparison, path: Path, sources: list):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "column_name", "data_type", "is_id_or_reference",
        "never_used", "best_source", "best_pct", "worst_source", "worst_pct", "spread", "sources_with_data"
    ]
    # Add one column per source for pct_complete
    for s in sources:
        fieldnames.append(f"pct_{s}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for c in comparison:
            row = {k: c.get(k, "") for k in fieldnames if k in c and not k.startswith("pct_")}
            for s in sources:
                val = c.get("source_pcts", {}).get(s, {})
                pct = val.get("pct_complete", "") if isinstance(val, dict) else ""
                row[f"pct_{s}"] = pct
            w.writerow(row)
    print(f"Wrote {path}")


def write_comparison_markdown(never_used, used_by_some, sources, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project table: field comparison by source system",
        "",
        "Derived from `data/project_table_data_profile_by_source.csv`.",
        "",
        "## 1. Fields never used (0% complete in every source)",
        "",
    ]
    if never_used:
        lines.append(f"**{len(never_used)}** columns have no non-null values in any source system:")
        lines.append("")
        lines.append("| Column | Data type | ID/Reference |")
        lines.append("|--------|-----------|--------------|")
        for c in never_used:
            id_ref = "Yes" if c.get("is_id_or_reference") == "Y" else ""
            lines.append(f"| {c['column_name']} | {c['data_type']} | {id_ref} |")
    else:
        lines.append("No columns are unused in all sources.")
    lines.extend([
        "",
        "---",
        "",
        "## 2. Completeness comparison (fields used by at least one source)",
        "",
        "For each column: best and worst source by % complete, and spread (best − worst).",
        "",
    ])
    # Summary table: column | type | best_source | best_pct | worst_source | worst_pct | spread | sources_with_data
    lines.append("| Column | Type | Best source | Best % | Worst source | Worst % | Spread | # Sources with data |")
    lines.append("|--------|------|-------------|--------|--------------|---------|--------|---------------------|")
    for c in used_by_some:
        lines.append(
            f"| {c['column_name']} | {c['data_type']} | {c['best_source']} | {c['best_pct']}% | "
            f"{c['worst_source']} | {c['worst_pct']}% | {c['spread']} | {c['sources_with_data']} |"
        )
    lines.extend([
        "",
        "---",
        "",
        "## 3. Per-source completeness (top columns by spread)",
        "",
        "Columns with the largest gap between best- and worst-performing source (often source-specific fields).",
        "",
    ])
    by_spread = sorted(used_by_some, key=lambda x: -x["spread"])
    for c in by_spread[:30]:
        pcts = c.get("source_pcts", {})
        parts = [f"**{c['column_name']}** (spread {c['spread']}%):"]
        for s in sources:
            p = pcts.get(s, {}).get("pct_complete", 0)
            parts.append(f" {s}={p}%")
        lines.append("".join(parts))
        lines.append("")
    lines.extend([
        "---",
        "",
        "## 4. Which source leads most often",
        "",
    ])
    lead_count = defaultdict(int)
    for c in used_by_some:
        lead_count[c["best_source"]] += 1
    lines.append("| Source | # columns where this source has highest completeness |")
    lines.append("|--------|--------------------------------------------------------|")
    for src in sources:
        lines.append(f"| {src} | {lead_count[src]} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")


def main():
    if not INPUT_CSV.exists():
        print(f"Input not found: {INPUT_CSV}")
        print("Run Python/profile/profile_project_table_by_source.py first to generate the profile CSV.")
        return 1
    print(f"Reading {INPUT_CSV}...")
    comparison, never_used, used_by_some, sources = run_comparison(INPUT_CSV)
    print(f"Columns: {len(comparison)} total, {len(never_used)} never used, {len(used_by_some)} used by at least one source")
    print(f"Sources: {', '.join(sources)}")
    write_comparison_csv(comparison, OUTPUT_CSV, sources)
    write_comparison_markdown(never_used, used_by_some, sources, OUTPUT_MD)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
