"""
Build all sector × project_type pairs per source: closed/closeout, positive area,
and budget/cost-code lines (originalbudgetamount). Composes mapping CTE + frag SQL.
Writes data/sector_project_type_with_area_top.csv and refreshes embed in reports/ds_pds_source_system_analysis.html.
"""
import csv
import subprocess
import sys
from pathlib import Path

for _p in Path(__file__).resolve().parents:
    if (_p / "repo_paths.py").is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break
else:
    raise RuntimeError("Not inside project Python tree")
from repo_paths import repo_root, reports_dir

PROJECT_ROOT = repo_root()
MAPPING_FILE = PROJECT_ROOT / "sql" / "sector" / "sector_mapping_cte_generated.sql"
FRAG_FILE = PROJECT_ROOT / "sql" / "sector" / "closed_closeout_sector_project_type_with_area_frag.sql"
OUTPUT_CSV = PROJECT_ROOT / "data" / "sector" / "sector_project_type_with_area_top.csv"


def build_sql() -> str:
    mapping = MAPPING_FILE.read_text(encoding="utf-8").strip()
    if mapping.startswith("--"):
        first_nl = mapping.find("\n")
        if first_nl != -1:
            mapping = mapping[first_nl + 1 :].lstrip()
    frag = FRAG_FILE.read_text(encoding="utf-8").strip().rstrip(";")
    return f"WITH\n{mapping}\n{frag}"


def main():
    if not MAPPING_FILE.is_file():
        print(f"Missing {MAPPING_FILE}; run Python/build/generate_sector_mapping_sql.py if needed.", file=sys.stderr)
        sys.exit(1)
    if not FRAG_FILE.is_file():
        print(f"Missing {FRAG_FILE}", file=sys.stderr)
        sys.exit(1)

    from edp_connection import connect_databricks

    sql = build_sql()
    print(f"Built SQL ({len(sql):,} chars)")

    print("Connecting to Databricks...")
    conn = connect_databricks()
    cursor = conn.cursor()
    print("Executing query...")
    cursor.execute(sql)
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    print(f"Fetched {len(rows):,} rows")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(rows)
    print(f"Wrote {OUTPUT_CSV}")

    pub = PROJECT_ROOT / "Python" / "run" / "publish_curated_to_source_analysis_html.py"
    r = subprocess.run([sys.executable, str(pub)], cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        print(f"publish_curated_to_source_analysis_html.py exited {r.returncode}", file=sys.stderr)
        sys.exit(r.returncode)
    print(f"Updated embed in {reports_dir() / 'ds_pds_source_system_analysis.html'}")


if __name__ == "__main__":
    main()
