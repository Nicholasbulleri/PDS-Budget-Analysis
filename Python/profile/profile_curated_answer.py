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
Profile work_dynamics.curated.answer table in EDP Databricks.
Examines structure, row counts, column stats, and sample data.
"""
import sys, os, json

from edp_connection import execute_query

def run(sql, label=None):
    if label:
        print(f"\n{'='*80}\n{label}\n{'='*80}")
    cols, rows = execute_query(sql)
    return cols, rows

def print_table(cols, rows, max_rows=50, max_col_width=80):
    if not rows:
        print("  (no rows)")
        return
    display = rows[:max_rows]
    widths = [len(c) for c in cols]
    for row in display:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], min(len(str(val) if val is not None else "NULL"), max_col_width))
    header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
    print(header)
    print("-" * len(header))
    for row in display:
        line = " | ".join(
            str(v if v is not None else "NULL")[:max_col_width].ljust(widths[i])
            for i, v in enumerate(row)
        )
        print(line)
    if len(rows) > max_rows:
        print(f"  ... ({len(rows)} total rows, showing first {max_rows})")

# ── 1. DESCRIBE TABLE ──
cols, rows = run("DESCRIBE TABLE EXTENDED work_dynamics.curated.answer", "1. TABLE SCHEMA (DESCRIBE TABLE EXTENDED)")
print_table(cols, rows, max_rows=100)

# ── 2. ROW COUNT ──
cols, rows = run("SELECT COUNT(*) AS row_count FROM work_dynamics.curated.answer", "2. TOTAL ROW COUNT")
print_table(cols, rows)

# ── 3. COLUMN NAMES (for dynamic profiling) ──
cols_meta, rows_meta = run("DESCRIBE TABLE work_dynamics.curated.answer")
column_names = [r[0] for r in rows_meta if r[0] and not r[0].startswith("#")]

print(f"\n{'='*80}\n3. COLUMNS FOUND: {len(column_names)}\n{'='*80}")
for c in column_names:
    print(f"  - {c}")

# ── 4. NULL / DISTINCT counts per column ──
parts = []
for c in column_names:
    safe = f"`{c}`"
    parts.append(f"COUNT(*) - COUNT({safe}) AS `{c}_nulls`")
    parts.append(f"COUNT(DISTINCT {safe}) AS `{c}_distinct`")

null_sql = f"SELECT {', '.join(parts)} FROM work_dynamics.curated.answer"
cols_n, rows_n = run(null_sql, "4. NULL & DISTINCT COUNTS PER COLUMN")

total_rows = None
try:
    _, rc = run("SELECT COUNT(*) FROM work_dynamics.curated.answer")
    total_rows = rc[0][0]
except:
    pass

print(f"{'Column':<45} {'Nulls':>12} {'Distinct':>12} {'Null%':>8}")
print("-" * 80)
for i, c in enumerate(column_names):
    nulls = rows_n[0][i * 2]
    distinct = rows_n[0][i * 2 + 1]
    pct = f"{nulls/total_rows*100:.1f}%" if total_rows else "?"
    print(f"{c:<45} {nulls:>12,} {distinct:>12,} {pct:>8}")

# ── 5. SAMPLE DATA ──
cols_s, rows_s = run("SELECT * FROM work_dynamics.curated.answer LIMIT 20", "5. SAMPLE ROWS (LIMIT 20)")
print_table(cols_s, rows_s)

# ── 6. Check for question/answer patterns ──
# Look for columns that might hold questions and answers
q_cols = [c for c in column_names if any(k in c.lower() for k in ("question", "ques", "prompt", "label", "text", "name", "description"))]
a_cols = [c for c in column_names if any(k in c.lower() for k in ("answer", "response", "value", "result"))]

print(f"\n{'='*80}\n6. LIKELY QUESTION COLUMNS: {q_cols}\n   LIKELY ANSWER COLUMNS: {a_cols}\n{'='*80}")

if q_cols:
    for qc in q_cols[:2]:
        print(f"\n  Top 30 distinct values for [{qc}]:")
        c2, r2 = run(f"SELECT `{qc}`, COUNT(*) AS cnt FROM work_dynamics.curated.answer GROUP BY `{qc}` ORDER BY cnt DESC LIMIT 30")
        print_table(c2, r2, max_rows=30)

if a_cols:
    for ac in a_cols[:2]:
        print(f"\n  Top 30 distinct values for [{ac}]:")
        c3, r3 = run(f"SELECT `{ac}`, COUNT(*) AS cnt FROM work_dynamics.curated.answer GROUP BY `{ac}` ORDER BY cnt DESC LIMIT 30")
        print_table(c3, r3, max_rows=30)

# ── 7. Source system breakdown ──
source_cols = [c for c in column_names if any(k in c.lower() for k in ("source", "system", "origin", "provider"))]
if source_cols:
    for sc in source_cols[:2]:
        print(f"\n{'='*80}\n7. SOURCE BREAKDOWN: [{sc}]\n{'='*80}")
        c4, r4 = run(f"SELECT `{sc}`, COUNT(*) AS cnt FROM work_dynamics.curated.answer GROUP BY `{sc}` ORDER BY cnt DESC LIMIT 30")
        print_table(c4, r4, max_rows=30)

# ── 8. Date/time columns ──
date_cols = [c for c in column_names if any(k in c.lower() for k in ("date", "time", "created", "updated", "modified", "timestamp"))]
if date_cols:
    print(f"\n{'='*80}\n8. DATE RANGE CHECK\n{'='*80}")
    for dc in date_cols[:4]:
        try:
            c5, r5 = run(f"SELECT MIN(`{dc}`) AS min_val, MAX(`{dc}`) AS max_val FROM work_dynamics.curated.answer")
            print(f"  {dc}: {r5[0][0]} → {r5[0][1]}")
        except Exception as e:
            print(f"  {dc}: error — {e}")

# ── 9. Incident form / form-type breakdown if applicable ──
form_cols = [c for c in column_names if any(k in c.lower() for k in ("form", "incident", "type", "category", "template"))]
if form_cols:
    for fc in form_cols[:3]:
        print(f"\n{'='*80}\n9. FORM/TYPE BREAKDOWN: [{fc}]\n{'='*80}")
        c6, r6 = run(f"SELECT `{fc}`, COUNT(*) AS cnt FROM work_dynamics.curated.answer GROUP BY `{fc}` ORDER BY cnt DESC LIMIT 40")
        print_table(c6, r6, max_rows=40)

print(f"\n{'='*80}\nPROFILE COMPLETE\n{'='*80}")
