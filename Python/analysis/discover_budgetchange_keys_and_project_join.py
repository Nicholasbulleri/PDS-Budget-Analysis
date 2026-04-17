#!/usr/bin/env python3
"""Discover keys in work_dynamics.curated.budgetchange and how it links to project.
Run against EDP (python3 Python/analysis/discover_budgetchange_keys_and_project_join.py).
No changes to EDP; read-only discovery queries."""
import os
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

# Load .env and apply SSL bypass before any Azure/EDP imports (so browser auth can work)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except (ImportError, PermissionError, FileNotFoundError):
    pass
if os.getenv("EDP_SSL_VERIFY", "true").lower() in ("false", "0", "no"):
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

def main():
    try:
        from edp_connection import execute_query
    except ImportError:
        print("Run from project root so edp_connection is on path, or: python3 -c \"import sys; sys.path.insert(0, 'Python'); from edp_connection import execute_query\"")
        sys.exit(1)

    catalog_schema = "work_dynamics.curated"
    budgetchange_table = f"{catalog_schema}.budgetchange"
    project_table = f"{catalog_schema}.project"

    print("=" * 60)
    print("1) Columns in curated.budgetchange")
    print("=" * 60)
    bc_column_names = []
    # Try DESCRIBE first (works with full table name in Databricks)
    try:
        q_desc = f"DESCRIBE TABLE {budgetchange_table}"
        cols, rows = execute_query(q_desc)
        if rows:
            for r in rows:
                if len(r) >= 2 and r[0] is not None and str(r[0]).strip() and not str(r[0]).startswith("#"):
                    print(f"  {r[0]}\t{r[1]}")
                    bc_column_names.append(str(r[0]).strip().lower())
    except Exception as e1:
        print(f"  DESCRIBE failed: {e1}")
    if not bc_column_names:
        # Fallback: information_schema (Unity Catalog)
        q_columns_bc = """
        SELECT column_name, data_type
        FROM system.information_schema.columns
        WHERE LOWER(table_name) = 'budgetchange'
        AND (LOWER(table_schema) = 'curated' OR LOWER(table_catalog) = 'work_dynamics')
        ORDER BY ordinal_position
        """
        try:
            cols, rows = execute_query(q_columns_bc)
            if rows:
                for r in rows:
                    print(f"  {r[0]}\t{r[1]}")
                    bc_column_names.append(str(r[0]).lower())
        except Exception as e2:
            print(f"  information_schema failed: {e2}")

    print()
    print("2) Columns in curated.project (key columns only)")
    print("=" * 60)
    q_columns_p = f"""
    SELECT column_name, data_type
    FROM system.information_schema.columns
    WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'project'
    AND LOWER(column_name) IN ('id', 'workitemidentifier', 'projectidentifier', 'sourcesystem')
    ORDER BY ordinal_position
    """
    try:
        cols, rows = execute_query(q_columns_p)
        for r in (rows or []):
            print(f"  {r[0]}\t{r[1]}")
    except Exception as e:
        print(f"  Error: {e}")

    print()
    print("3) Sample row from budgetchange (to see key values)")
    print("=" * 60)
    try:
        cols, rows = execute_query(f"SELECT * FROM {budgetchange_table} LIMIT 1")
        if rows and cols:
            for c, v in zip(cols, rows[0]):
                print(f"  {c}: {v}")
        else:
            print("  No rows or no columns returned.")
    except Exception as e:
        print(f"  Error: {e}")

    # 4) Try joins: project links in this repo use project.id and project.workitemidentifier;
    #    generictask uses gt.projectidentifier = p.workitemidentifier; budgetdetail uses bd.projectidentifier = p.id (Ingenious).
    print()
    print("4) Testing join: budgetchange -> project (candidate keys)")
    print("=" * 60)

    join_candidates = [
        ("bc.projectidentifier = p.id", "budgetchange.projectidentifier = project.id"),
        ("bc.projectidentifier = p.workitemidentifier", "budgetchange.projectidentifier = project.workitemidentifier"),
        ("bc.workitemidentifier = p.workitemidentifier", "budgetchange.workitemidentifier = project.workitemidentifier"),
        ("bc.projectid = p.id", "budgetchange.projectid = project.id"),
        ("bc.project_id = p.id", "budgetchange.project_id = project.id"),
        ("bc.projectidentifier = p.workitemidentifier", "budgetchange.projectidentifier = project.workitemidentifier"),
    ]

    for join_condition, label in join_candidates:
        # Parse left side column (e.g. bc.projectidentifier -> projectidentifier)
        left_col = join_condition.split("=")[0].strip().split(".")[-1].lower()
        if bc_column_names and left_col not in bc_column_names:
            continue
        try:
            q = f"""
            SELECT COUNT(*) AS cnt
            FROM {budgetchange_table} bc
            INNER JOIN {project_table} p ON {join_condition}
            """
            cols, rows = execute_query(q)
            cnt = rows[0][0] if rows else 0
            print(f"  {label}")
            print(f"    -> Matched rows: {cnt}")
        except Exception as e:
            print(f"  {label}")
            print(f"    -> Error: {e}")

    # 5) If budgetchange has budgetidentifier, try project -> generictask -> budgetchange (like budgetdetail)
    if bc_column_names and "budgetidentifier" in bc_column_names:
        print()
        print("5) Join via generictask: project -> generictask -> budgetchange (budgetidentifier)")
        print("=" * 60)
        try:
            q = f"""
            SELECT COUNT(*) AS cnt
            FROM {catalog_schema}.project p
            INNER JOIN {catalog_schema}.generictask gt ON gt.projectidentifier = p.workitemidentifier
            INNER JOIN {budgetchange_table} bc ON bc.budgetidentifier = gt.budgetidentifier
            """
            cols, rows = execute_query(q)
            cnt = rows[0][0] if rows else 0
            print(f"  project (workitemidentifier) -> generictask (projectidentifier) -> budgetchange (budgetidentifier)")
            print(f"    -> Matched rows: {cnt}")
        except Exception as e:
            print(f"  Error: {e}")

    print()
    print("Done. Use the join that returns non-zero matched rows to link budgetchange to project.")

if __name__ == "__main__":
    main()
