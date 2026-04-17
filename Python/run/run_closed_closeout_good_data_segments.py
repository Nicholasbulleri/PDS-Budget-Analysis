"""
Run sql/closed_closeout_good_data_by_segment.sql: cells with area + budget/cost-code lines,
>= min threshold projects per sector × project type × metro (see SQL HAVING).
Writes CSV + standalone HTML in reports/ + embeds into reports/ds_pds_source_system_analysis.html via publish script.
"""
import csv
import html
import subprocess
import sys
from collections import defaultdict
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
SQL_FILE = PROJECT_ROOT / "sql" / "segments" / "closed_closeout_good_data_by_segment.sql"
OUTPUT_CSV = PROJECT_ROOT / "data" / "closeout" / "closed_closeout_good_data_dense_cells.csv"
OUTPUT_HTML = reports_dir() / "closed_closeout_good_data_matrix.html"


def _int_cell(row, key):
    v = row.get(key)
    if v is None or v == "":
        return 0
    return int(float(v))


def write_dense_html(csv_path: Path, out_html: Path, min_cell: int = 25) -> None:
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total_projects = sum(_int_cell(r, "project_count") for r in rows)
    sector_totals = defaultdict(int)
    for row in rows:
        sector_totals[row.get("sector") or ""] += _int_cell(row, "project_count")
    sectors_sorted = sorted(sector_totals.keys(), key=lambda x: (-sector_totals[x], x))

    def esc(s):
        return html.escape(str(s) if s is not None else "")

    max_cell = max((c for r in rows for c in [_int_cell(r, "project_count")]), default=1)
    max_sec = max(sector_totals.values(), default=1)

    parts = [
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>",
        "<title>Closed / closeout — dense segments (area + budget)</title>",
        "<style>",
        ":root { --bg:#0b0e13; --surface:#12161e; --border:#252b38; --text:#dfe5f0; --muted:#7c859a; --accent:#56d48e; }",
        "body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; line-height: 1.5; }",
        "h1 { font-size: 1.35rem; font-weight: 600; margin: 0 0 8px; }",
        "p.sub { color: var(--muted); font-size: 0.88rem; margin: 0 0 24px; max-width: 920px; }",
        "h2 { font-size: 1.05rem; margin: 28px 0 12px; }",
        ".card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; overflow-x: auto; margin-bottom: 24px; }",
        "table { border-collapse: collapse; font-size: 0.82rem; width: 100%; }",
        "th, td { border-bottom: 1px solid var(--border); padding: 8px 10px; text-align: right; }",
        "th:nth-child(-n+4), td:nth-child(-n+4) { text-align: left; }",
        "th { color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.68rem; }",
        "tr:hover td { background: rgba(86,212,142,0.04); }",
        ".num { font-variant-numeric: tabular-nums; }",
        "</style></head><body>",
        "<h1>Dense segments (normalization-ready)</h1>",
        f"<p class='sub'>Closed / closeout curated projects with <strong>positive area</strong> and <strong>budget/cost-code lines</strong>. "
        f"One row per sector × project type × metro with <strong>≥ {min_cell}</strong> projects. "
        f"Ordered by project count descending. "
        f"CSV: <code>data/closed_closeout_good_data_dense_cells.csv</code>. Rows: <strong>{len(rows):,}</strong>, "
        f"projects in table: <strong>{total_projects:,}</strong>.</p>",
        "<div class='card'><h2>By sector, project type, metro</h2><table><thead><tr>"
        "<th>#</th><th>Sector</th><th>Project type</th><th>Metro</th><th>Projects</th></tr></thead><tbody>",
    ]
    for i, row in enumerate(rows):
        cnt = _int_cell(row, "project_count")
        t = max_cell > 0 and (cnt / max_cell) ** 0.45 or 0
        alpha = 0.08 + 0.38 * t
        parts.append("<tr>")
        parts.append(f"<td class='num' style='color:var(--muted)'>{i + 1}</td>")
        parts.append(f"<td>{esc(row.get('sector'))}</td>")
        parts.append(f"<td>{esc(row.get('project_type'))}</td>")
        parts.append(f"<td>{esc(row.get('metro'))}</td>")
        parts.append(
            f"<td class='num' style='background:rgba(86,212,142,{alpha:.3f})'>{cnt:,}</td>"
        )
        parts.append("</tr>")
    parts.append("</tbody></table></div>")

    parts.append("<div class='card'><h2>Sector totals (curated slice)</h2><table><thead><tr><th>Sector</th><th>Projects</th></tr></thead><tbody>")
    for s in sectors_sorted:
        if not s:
            continue
        v = sector_totals[s]
        t = max_sec > 0 and (v / max_sec) ** 0.45 or 0
        alpha = 0.08 + 0.35 * t
        parts.append(
            f"<tr><td>{esc(s)}</td><td class='num' style='background:rgba(86,212,142,{alpha:.3f})'>{v:,}</td></tr>"
        )
    parts.append("</tbody></table></div></body></html>")
    out_html.write_text("".join(parts), encoding="utf-8")


def main():
    from edp_connection import connect_databricks

    sql = SQL_FILE.read_text(encoding="utf-8").strip().rstrip(";")
    print(f"Loaded SQL ({len(sql):,} chars)")

    print("Connecting to Databricks...")
    conn = connect_databricks()
    cursor = conn.cursor()

    print("Executing query (may take several minutes)...")
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    print(f"Fetched {len(rows):,} rows, {len(columns)} columns")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columns)
        for row in rows:
            w.writerow(row)
    print(f"Wrote {OUTPUT_CSV}")

    write_dense_html(OUTPUT_CSV, OUTPUT_HTML)
    print(f"Wrote {OUTPUT_HTML}")

    pub = PROJECT_ROOT / "Python" / "run" / "publish_curated_to_source_analysis_html.py"
    r = subprocess.run([sys.executable, str(pub)], cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        print(f"publish_curated_to_source_analysis_html.py exited {r.returncode}")
    else:
        print(f"Embedded curated data into {reports_dir() / 'ds_pds_source_system_analysis.html'}")


if __name__ == "__main__":
    main()
