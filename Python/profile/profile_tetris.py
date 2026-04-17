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
Tetris (TetriSoft) Source System Profiling
Discovers tables in edp_sourcesystem.tetris, profiles schemas,
row counts, nullability, and budget/cost-related data.
"""
import sys
import os
import json
from datetime import datetime


from edp_connection import execute_query

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CATALOG = "edp_sourcesystem"
SCHEMA = "tetris"


def run(query, label=""):
    if label:
        print(f"\n--- {label} ---")
    cols, rows = execute_query(query)
    if label:
        print(f"  {len(rows)} rows returned, columns: {cols}")
    return cols, rows


def step1_discover_tables():
    print("=" * 70)
    print("STEP 1: Discover tables in edp_sourcesystem.tetris")
    print("=" * 70)
    cols, rows = run(f"SHOW TABLES IN {CATALOG}.{SCHEMA}", "SHOW TABLES")
    tables = []
    for r in rows:
        tname = r[1] if len(r) > 1 else r[0]
        tables.append(tname)
        print(f"  Table: {tname}")
    return tables


def step2_describe_tables(tables):
    print("\n" + "=" * 70)
    print("STEP 2: Schema details for each table")
    print("=" * 70)
    schemas = {}
    for t in tables:
        cols, rows = run(f"DESCRIBE TABLE {CATALOG}.{SCHEMA}.{t}", f"DESCRIBE {t}")
        col_defs = []
        for r in rows:
            cname, ctype = r[0], r[1]
            if cname.startswith("#") or cname.strip() == "":
                break
            col_defs.append({"name": cname, "type": ctype, "comment": r[2] if len(r) > 2 else ""})
        schemas[t] = col_defs
        for c in col_defs:
            print(f"    {c['name']:40s}  {c['type']}")
    return schemas


def step3_row_counts(tables):
    print("\n" + "=" * 70)
    print("STEP 3: Row counts")
    print("=" * 70)
    counts = {}
    for t in tables:
        cols, rows = run(f"SELECT COUNT(*) AS cnt FROM {CATALOG}.{SCHEMA}.{t}", f"COUNT {t}")
        cnt = rows[0][0] if rows else 0
        counts[t] = cnt
        print(f"  {t}: {cnt:,} rows")
    return counts


def step4_null_profile(tables, schemas):
    print("\n" + "=" * 70)
    print("STEP 4: Null / completeness profile per table")
    print("=" * 70)
    null_profiles = {}
    for t in tables:
        col_defs = schemas[t]
        if not col_defs:
            continue
        exprs = []
        for c in col_defs:
            cn = c["name"]
            exprs.append(f"SUM(CASE WHEN `{cn}` IS NULL THEN 1 ELSE 0 END) AS `null_{cn}`")
            exprs.append(f"COUNT(DISTINCT `{cn}`) AS `dist_{cn}`")
        exprs.append("COUNT(*) AS total_rows")
        q = f"SELECT {', '.join(exprs)} FROM {CATALOG}.{SCHEMA}.{t}"
        cols, rows = run(q, f"NULLS {t}")
        if not rows:
            continue
        row = rows[0]
        total = row[-1]
        profile = []
        idx = 0
        for c in col_defs:
            null_ct = row[idx]
            dist_ct = row[idx + 1]
            pct_null = round(100 * null_ct / total, 1) if total else 0
            profile.append({
                "column": c["name"],
                "type": c["type"],
                "null_count": null_ct,
                "null_pct": pct_null,
                "distinct_count": dist_ct,
                "total_rows": total,
            })
            idx += 2
        null_profiles[t] = profile
        print(f"\n  Table: {t} ({total:,} rows)")
        print(f"  {'Column':40s} {'Type':15s} {'Nulls':>8s} {'Null%':>7s} {'Distinct':>10s}")
        print(f"  {'-'*40} {'-'*15} {'-'*8} {'-'*7} {'-'*10}")
        for p in profile:
            print(f"  {p['column']:40s} {p['type']:15s} {p['null_count']:>8,} {p['null_pct']:>6.1f}% {p['distinct_count']:>10,}")
    return null_profiles


def step5_sample_rows(tables):
    print("\n" + "=" * 70)
    print("STEP 5: Sample rows (first 3) per table")
    print("=" * 70)
    samples = {}
    for t in tables:
        cols, rows = run(f"SELECT * FROM {CATALOG}.{SCHEMA}.{t} LIMIT 3", f"SAMPLE {t}")
        samples[t] = {"columns": cols, "rows": [list(r) for r in rows]}
        for i, r in enumerate(rows):
            print(f"  Row {i+1}: {dict(zip(cols, r))}")
    return samples


def save_results(tables, schemas, counts, null_profiles, samples):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = {
        "generated": ts,
        "catalog": CATALOG,
        "schema": SCHEMA,
        "tables": tables,
        "row_counts": counts,
        "schemas": schemas,
        "null_profiles": null_profiles,
    }
    path = os.path.join(OUTPUT_DIR, "tetris_profile.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nProfile saved to {path}")


if __name__ == "__main__":
    tables = step1_discover_tables()
    schemas = step2_describe_tables(tables)
    counts = step3_row_counts(tables)
    null_profiles = step4_null_profile(tables, schemas)
    samples = step5_sample_rows(tables)
    save_results(tables, schemas, counts, null_profiles, samples)
    print("\n✓ Tetris profiling complete!")
