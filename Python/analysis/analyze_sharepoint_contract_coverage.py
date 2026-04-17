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

"""
SharePoint Contract & Cost Document Coverage Analysis
=====================================================
Loads SharePoint metadata exports (3 batches) using streaming openpyxl,
classifies documents into contract/cost categories, calculates per-project
coverage ratios, and cross-references against the
dim_project_budget_benchmarking_filtered project list from Databricks.
"""

import os
import sys
import re
import json
import collections
from datetime import datetime
from pathlib import Path
from typing import Optional

import openpyxl
import pandas as pd

BATCH_FILES = [
    os.path.expanduser("~/Downloads/SharePoint_MetaData_Export_batch1.xlsx"),
    os.path.expanduser("~/Downloads/SharePoint_MetaData_Export_batch2.xlsx"),
    os.path.expanduser("~/Downloads/SharePoint_MetaData_Export_batch3.xlsx"),
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Document classification
# ---------------------------------------------------------------------------
CATEGORIES = collections.OrderedDict([
    ("Contract / Agreement", [
        r'\bcontract', r'\bagreement\b', r'\bsubcontract', r'\bvendor.contract',
        r'\bmsa\b', r'\bmaster.service', r'\bwork.?order\b', r'\bletter.of.intent\b',
        r'\bloi\b', r'\bstipulated\b', r'\bnot.to.exceed\b', r'\bnte\b',
    ]),
    ("Bill of Quantities / BOQ", [
        r'\bboq\b', r'\bbill.*(of|s).*quantit', r'\bschedule.of.(value|rate)',
        r'\bsov\b', r'\bpric(e|ing).schedule', r'\bunit.pric(e|ing)',
        r'\brate.schedule',
    ]),
    ("Cost / Budget Document", [
        r'\bcost.(plan|report|estimate|summary|breakdown|analysis|model)',
        r'\bbudget\b', r'\bgmp\b', r'\bguaranteed.maximum',
        r'\bcost.manag', r'\bcost.control', r'\bcost.track',
        r'\bestimate\b', r'\bcost.data', r'\blump.sum',
    ]),
    ("Change Order / Variation", [
        r'\bchange.order', r'\bvariation\b', r'\bpco\b', r'\bcor\b',
        r'\bcontingency.(draw|log)', r'\bamendment\b',
    ]),
    ("Bid / Tender / Proposal", [
        r'\bbid\b', r'\btender\b', r'\bproposal\b', r'\brfp\b', r'\brfq\b',
        r'\bquot(e|ation)\b', r'\bbid.tab', r'\bbid.analysis',
        r'\blevel(l)?ing\b', r'\baward\b',
    ]),
    ("Procurement", [
        r'\bprocurement\b', r'\bpurchase.order\b',
    ]),
    ("Invoice / Payment", [
        r'\binvoice\b', r'\bpayment\b', r'\bpay.app', r'\brequisition\b',
        r'\bsworn\b', r'\bdraw.request', r'\bprogress.claim',
        r'\bapplication.for.payment',
    ]),
])

COST_CONTRACT_CATS = {
    "Contract / Agreement",
    "Bill of Quantities / BOQ",
    "Cost / Budget Document",
    "Change Order / Variation",
    "Bid / Tender / Proposal",
}

_compiled = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
    for cat, pats in CATEGORIES.items()
}


def classify(text: str) -> Optional[str]:
    for cat, pats in _compiled.items():
        for pat in pats:
            if pat.search(text):
                return cat
    return None


# ---------------------------------------------------------------------------
# Streaming load + classify
# ---------------------------------------------------------------------------
COL_MAP = {
    "ProjectURL": 0, "ProjectID": 1, "DocumentName": 2, "DocumentType": 3,
    "IsFolder": 4, "DocumentURL": 5, "UploadedBy": 6, "UploadDate": 7,
    "EditedBy": 8, "EditedDate": 9, "PMTags": 10, "ClientTags": 11, "FileRef": 12,
}


def stream_and_classify():
    """Stream all batches, classify files, accumulate per-project stats."""

    per_project = collections.defaultdict(lambda: {
        "total_files": 0,
        "total_folders": 0,
        "categories": collections.Counter(),
        "classified_file_count": 0,
    })

    classified_samples = []
    total_rows = 0

    for batch_idx, path in enumerate(BATCH_FILES, 1):
        print(f"Streaming batch {batch_idx}: {os.path.basename(path)} ...", flush=True)
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb["Sheet1"]
        row_count = 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            row_count += 1
            project_id = str(row[1] or "").strip()
            doc_name = str(row[2] or "")
            is_folder = row[4]
            file_ref = str(row[12] or "")

            if not project_id:
                continue

            proj = per_project[project_id]

            if is_folder:
                proj["total_folders"] += 1
                continue

            proj["total_files"] += 1
            search_text = f"{doc_name} {file_ref}"
            cat = classify(search_text)

            if cat:
                proj["categories"][cat] += 1
                proj["classified_file_count"] += 1
                if len(classified_samples) < 200_000:
                    classified_samples.append({
                        "ProjectID": project_id,
                        "DocumentName": doc_name,
                        "FileRef": file_ref,
                        "Category": cat,
                        "DocumentType": str(row[3] or ""),
                        "Batch": batch_idx,
                    })

            if row_count % 200_000 == 0:
                print(f"  ... processed {row_count:,} rows", flush=True)

        wb.close()
        total_rows += row_count
        print(f"  Batch {batch_idx} done: {row_count:,} rows", flush=True)

    print(f"\nTotal rows processed: {total_rows:,}")
    print(f"Unique projects: {len(per_project):,}")
    return per_project, classified_samples


# ---------------------------------------------------------------------------
# Build project summary DataFrame
# ---------------------------------------------------------------------------
def build_summary(per_project: dict) -> pd.DataFrame:
    rows = []
    for pid, data in per_project.items():
        cats = data["categories"]
        row = {
            "ProjectID": pid,
            "total_files": data["total_files"],
            "total_folders": data["total_folders"],
            "classified_file_count": data["classified_file_count"],
            "contract_agreement": cats.get("Contract / Agreement", 0),
            "boq": cats.get("Bill of Quantities / BOQ", 0),
            "cost_budget": cats.get("Cost / Budget Document", 0),
            "change_order": cats.get("Change Order / Variation", 0),
            "bid_tender_proposal": cats.get("Bid / Tender / Proposal", 0),
            "procurement": cats.get("Procurement", 0),
            "invoice_payment": cats.get("Invoice / Payment", 0),
        }
        row["cost_contract_files"] = (
            row["contract_agreement"] + row["boq"] + row["cost_budget"]
            + row["change_order"] + row["bid_tender_proposal"]
        )
        row["cost_contract_ratio"] = round(
            row["cost_contract_files"] / max(row["total_files"], 1), 4
        )
        row["has_contract"] = row["contract_agreement"] > 0
        row["has_boq"] = row["boq"] > 0
        row["has_cost_budget"] = row["cost_budget"] > 0
        row["has_change_order"] = row["change_order"] > 0
        row["has_bid_tender"] = row["bid_tender_proposal"] > 0

        row["category_breadth"] = sum([
            row["has_contract"], row["has_boq"], row["has_cost_budget"],
            row["has_change_order"], row["has_bid_tender"],
        ])
        row["category_breadth_pct"] = round(row["category_breadth"] / 5, 2)
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("cost_contract_files", ascending=False)
    return df


# ---------------------------------------------------------------------------
# Cross-reference with Databricks benchmarking project list
# ---------------------------------------------------------------------------
def _extract_sp_project_id(url: str) -> Optional[str]:
    """Extract the SharePoint project folder ID from a projectdocumenturltext URL."""
    if not url or not isinstance(url, str):
        return None
    url = url.split("?")[0].rstrip("/")
    parts = [p for p in url.split("/") if p]
    try:
        idx_teams = [i for i, p in enumerate(parts) if p.lower() == "teams"]
        if idx_teams:
            after_teams = idx_teams[-1] + 1
            if after_teams + 1 < len(parts):
                candidate = parts[after_teams + 1]
                if not candidate.lower().startswith("forms"):
                    return candidate
    except (IndexError, ValueError):
        pass
    return None


def _normalize_id(val: str) -> str:
    """Strip hyphens and whitespace for ID comparison.
    Clarizen sourceprojectidentifier uses P-XXXXXXX; SharePoint uses PXXXXXXX.
    """
    return str(val).replace("-", "").strip()


def cross_reference(summary: pd.DataFrame) -> pd.DataFrame:
    sql_path = Path(__file__).resolve().parents[2] / "sql" / "dim" / "dim_project_budget_benchmarking_filtered.sql"
    if not sql_path.exists():
        print(f"\n[WARN] SQL file not found: {sql_path}")
        return summary

    print("\nConnecting to Databricks for benchmarking project list ...", flush=True)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from edp_connection import execute_query
    except ImportError:
        print("[WARN] edp_connection not available – skipping cross-reference.")
        return summary

    query = sql_path.read_text()
    columns, rows = execute_query(query)
    bench = pd.DataFrame(rows, columns=columns)
    print(f"  Benchmarking query returned {len(bench):,} projects", flush=True)

    sp_set = set(summary["ProjectID"].astype(str).str.strip())

    # Strategy 1: normalize sourceprojectidentifier (strip hyphens)
    # Clarizen: P-4287884 → P4287884 = SharePoint ProjectID
    match_map = {}  # SP ProjectID → bench row index list
    if "sourceprojectidentifier" in bench.columns:
        bench["_norm_spid"] = bench["sourceprojectidentifier"].astype(str).apply(_normalize_id)
        for idx, row in bench.iterrows():
            norm = row["_norm_spid"]
            if norm in sp_set:
                match_map[norm] = idx

    # Strategy 2: sourceprojectid / projectsourceid directly
    for col in ["projectsourceid", "sourceprojectid"]:
        if col in bench.columns:
            for idx, row in bench.iterrows():
                val = str(row[col]).strip()
                if val in sp_set and val not in match_map:
                    match_map[val] = idx

    # Strategy 3: extract from projectdocumenturltext (fallback for Ingenious)
    if "projectdocumenturltext" in bench.columns:
        bench["_url_sp_id"] = bench["projectdocumenturltext"].apply(_extract_sp_project_id)
        for idx, row in bench.iterrows():
            url_id = row.get("_url_sp_id")
            if url_id and url_id in sp_set and url_id not in match_map:
                match_map[url_id] = idx

    matched_sp_ids = set(match_map.keys())
    matched_bench_indices = set(match_map.values())

    print(f"  Match strategy results:", flush=True)
    print(f"    Matched SharePoint projects:     {len(matched_sp_ids)}", flush=True)
    print(f"    Matched benchmarking rows:       {len(matched_bench_indices)}", flush=True)
    print(f"    Benchmarking NOT in SP export:   {len(bench) - len(matched_bench_indices)}", flush=True)

    summary["in_benchmarking_list"] = summary["ProjectID"].isin(matched_sp_ids)

    # Build bench lookup for merge
    keep_cols = [
        "project_id", "projectname", "phase", "sourcesystem",
        "project_type", "sector", "area", "original_budget_usd",
        "total_anticipated_cost_usd", "country", "city", "client_name",
        "sourceprojectidentifier", "projectsourceid",
    ]
    keep_cols = [c for c in keep_cols if c in bench.columns]

    merge_rows = []
    for sp_id, bench_idx in match_map.items():
        row_data = {"ProjectID": sp_id}
        for c in keep_cols:
            row_data[c] = bench.at[bench_idx, c]
        merge_rows.append(row_data)

    if merge_rows:
        bench_sub = pd.DataFrame(merge_rows).drop_duplicates(subset=["ProjectID"])
        merged = summary.merge(bench_sub, on="ProjectID", how="left")
    else:
        merged = summary

    return merged


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def print_report(summary: pd.DataFrame):
    n = len(summary)
    total_files = int(summary["total_files"].sum())

    print("\n" + "=" * 80)
    print("  SHAREPOINT CONTRACT & COST DOCUMENT COVERAGE REPORT")
    print("=" * 80)
    print(f"\n  Total projects:          {n:,}")
    print(f"  Total files (non-folder): {total_files:,}")

    for col, label in [
        ("has_contract", "Contract / Agreement"),
        ("has_boq", "Bill of Quantities / BOQ"),
        ("has_cost_budget", "Cost / Budget Document"),
        ("has_change_order", "Change Order / Variation"),
        ("has_bid_tender", "Bid / Tender / Proposal"),
    ]:
        cnt = int(summary[col].sum())
        print(f"  {label:40s}: {cnt:4d} / {n} ({cnt/n*100:5.1f}%)")

    any_cost = int((summary["cost_contract_files"] > 0).sum())
    print(f"\n  Projects with ANY contract/cost docs: {any_cost:4d} / {n} ({any_cost/n*100:.1f}%)")
    print(f"  Average category breadth (0-1):       {summary['category_breadth_pct'].mean():.2f}")

    if "in_benchmarking_list" in summary.columns:
        b = summary[summary["in_benchmarking_list"]]
        nb = len(b)
        if nb > 0:
            bw = int((b["cost_contract_files"] > 0).sum())
            print(f"\n  --- Benchmarking Cross-Reference ---")
            print(f"  Benchmarking projects matched in SP:  {nb:4d}")
            print(f"  Matched + have contract/cost docs:    {bw:4d} / {nb} ({bw/nb*100:.1f}%)")
            print(f"    w/ Contract / Agreement:            {int(b['has_contract'].sum()):4d}")
            print(f"    w/ BOQ:                             {int(b['has_boq'].sum()):4d}")
            print(f"    w/ Cost / Budget doc:               {int(b['has_cost_budget'].sum()):4d}")
            print(f"    w/ Change Order / Variation:         {int(b['has_change_order'].sum()):4d}")
            print(f"    w/ Bid / Tender / Proposal:         {int(b['has_bid_tender'].sum()):4d}")
            print(f"  Avg category breadth (benchmarking):  {b['category_breadth_pct'].mean():.2f}")

            no_docs = b[b["cost_contract_files"] == 0]
            if len(no_docs) > 0:
                print(f"\n  Benchmarking projects with NO contract/cost docs ({len(no_docs)}):")
                for _, r in no_docs.head(15).iterrows():
                    pname = r.get("projectname", "")
                    if isinstance(pname, str) and len(pname) > 50:
                        pname = pname[:47] + "..."
                    print(f"    {r['ProjectID']:12s}  {pname}")
                if len(no_docs) > 15:
                    print(f"    ... and {len(no_docs) - 15} more")

    print("\n" + "=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    per_project, classified_samples = stream_and_classify()
    summary = build_summary(per_project)

    cat_totals = collections.Counter()
    for data in per_project.values():
        cat_totals.update(data["categories"])
    print("\nCategory distribution (files):")
    for cat, cnt in cat_totals.most_common():
        print(f"  {cat:40s} {cnt:>10,}")

    summary = cross_reference(summary)
    print_report(summary)

    out_xlsx = OUTPUT_DIR / "sharepoint_project_contract_coverage.xlsx"
    print(f"\nSaving project summary → {out_xlsx}", flush=True)
    summary.to_excel(out_xlsx, index=False)

    if classified_samples:
        out_detail = OUTPUT_DIR / "sharepoint_classified_documents.xlsx"
        print(f"Saving classified doc samples ({len(classified_samples):,}) → {out_detail}", flush=True)
        pd.DataFrame(classified_samples).to_excel(out_detail, index=False)

    out_json = OUTPUT_DIR / "sharepoint_coverage_summary.json"
    j = {
        "generated_at": datetime.now().isoformat(),
        "total_projects": len(summary),
        "total_files": int(summary["total_files"].sum()),
        "category_coverage": {},
    }
    for cat_key, col in [
        ("contract_agreement", "contract_agreement"),
        ("boq", "boq"),
        ("cost_budget", "cost_budget"),
        ("change_order", "change_order"),
        ("bid_tender_proposal", "bid_tender_proposal"),
        ("procurement", "procurement"),
        ("invoice_payment", "invoice_payment"),
    ]:
        cnt = int((summary[col] > 0).sum())
        j["category_coverage"][cat_key] = {
            "projects_with_docs": cnt,
            "pct": round(cnt / max(len(summary), 1) * 100, 1),
        }
    if "in_benchmarking_list" in summary.columns:
        b = summary[summary["in_benchmarking_list"]]
        j["benchmarking"] = {
            "matched": len(b),
            "with_cost_contract": int((b["cost_contract_files"] > 0).sum()),
        }
    with open(out_json, "w") as f:
        json.dump(j, f, indent=2)
    print(f"Saving JSON summary → {out_json}")
    print("\nDone.")


if __name__ == "__main__":
    main()
