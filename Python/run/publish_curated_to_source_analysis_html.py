"""
Embed curated PM dense CSV + sector×type (with area) CSV into reports/ds_pds_source_system_analysis.html.

Dense CSV: run python3 Python/run/run_closed_closeout_good_data_segments.py
Sector×type CSV: run python3 Python/run/run_sector_project_type_area_rank.py (optional; empty embed if missing)
Canonical sector embed JSON: run python3 Python/run/run_source_analysis_canonical_embed.py (optional; spendData + sector matrices)
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
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
CSV_PATH = PROJECT_ROOT / "data" / "closeout" / "closed_closeout_good_data_dense_cells.csv"
SECTOR_TYPE_AREA_CSV = PROJECT_ROOT / "data" / "sector" / "sector_project_type_with_area_top.csv"
CANONICAL_EMBED_JSON = PROJECT_ROOT / "data" / "analysis" / "source_analysis_canonical_embed.json"
HTML_PATH = reports_dir() / "ds_pds_source_system_analysis.html"
BLOCK_START = "/* CURATED_GOOD_DATA_BLOCK_START */"
BLOCK_END = "/* CURATED_GOOD_DATA_BLOCK_END */"
SECTOR_AREA_BLOCK_START = "/* SECTOR_TYPE_AREA_BLOCK_START */"
SECTOR_AREA_BLOCK_END = "/* SECTOR_TYPE_AREA_BLOCK_END */"
CANONICAL_BLOCK_START = "/* SOURCE_ANALYSIS_CANONICAL_BLOCK_START */"
CANONICAL_BLOCK_END = "/* SOURCE_ANALYSIS_CANONICAL_BLOCK_END */"
LEGACY_MARKER = "/* __CURATED_GOOD_DATA_DATA__ */"

# Curated CSV rows = sector×type×metro with COUNT(*) >= 25 (see sql/closed_closeout_good_data_by_segment.sql HAVING).
# Sector×type+area CSV: all sector×type pairs per source (sql/closed_closeout_sector_project_type_with_area_frag.sql).

def load_csv_rows():
    import csv

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_payload(rows):
    projects_in_cells = sum(int(float(r.get("project_count") or 0)) for r in rows)

    dense_rows = []
    for r in rows:
        dense_rows.append(
            {
                "sector": r.get("sector", ""),
                "project_type": r.get("project_type", ""),
                "metro": r.get("metro", ""),
                "project_count": int(float(r.get("project_count") or 0)),
            }
        )

    sector_rollup = defaultdict(int)
    for r in rows:
        s = r.get("sector", "")
        sector_rollup[s] += int(float(r.get("project_count") or 0))
    curated_sector_rollup = dict(sorted(sector_rollup.items(), key=lambda x: (-x[1], x[0])))

    sectors = sorted(sector_rollup.keys())
    meta = {
        "denseRowCount": len(rows),
        "projectsInDenseCells": projects_in_cells,
        "sectorCount": len(sectors),
    }

    return {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "meta": meta,
        "sectorRollup": curated_sector_rollup,
        "denseRows": dense_rows,
    }


def to_js_injection(payload):
    meta = json.dumps(payload["meta"], separators=(",", ":"))
    rollup = json.dumps(payload["sectorRollup"], separators=(",", ":"))
    dense = json.dumps(payload["denseRows"], separators=(",", ":"))
    gen = json.dumps(payload["generatedAt"])
    inner = f"""const curatedGeneratedAt = {gen};
const curatedMeta = {meta};
const curatedSectorRollup = {rollup};
const curatedDenseRows = {dense};"""
    return f"{BLOCK_START}\n{inner}\n{BLOCK_END}"


def load_sector_type_area_rows():
    import csv

    if not SECTOR_TYPE_AREA_CSV.is_file():
        return [], None
    with open(SECTOR_TYPE_AREA_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return rows, gen


def build_sector_type_area_payload(csv_rows, generated_at):
    cl, ig, ts = [], [], []
    for r in csv_rows:
        src = (r.get("source_system") or "").strip().lower()
        item = {
            "sector": r.get("sector", ""),
            "project_type": r.get("project_type", ""),
            "project_count": int(float(r.get("project_count") or 0)),
        }
        if src == "clarizen":
            cl.append(item)
        elif src == "ingenious":
            ig.append(item)
        elif src == "tetrisoft":
            ts.append(item)
    return {
        "generatedAt": generated_at if csv_rows else None,
        "cl": cl,
        "ig": ig,
        "ts": ts,
    }


def to_sector_area_js_injection(payload):
    gen = json.dumps(payload["generatedAt"])
    cl = json.dumps(payload["cl"], separators=(",", ":"))
    ig = json.dumps(payload["ig"], separators=(",", ":"))
    ts = json.dumps(payload.get("ts") or [], separators=(",", ":"))
    inner = f"""const sectorTypeAreaGeneratedAt = {gen};
const sectorTypeAreaCl = {cl};
const sectorTypeAreaIg = {ig};
const sectorTypeAreaTs = {ts};"""
    return f"{SECTOR_AREA_BLOCK_START}\n{inner}\n{SECTOR_AREA_BLOCK_END}"


def load_canonical_embed_payload():
    if not CANONICAL_EMBED_JSON.is_file():
        return None
    with open(CANONICAL_EMBED_JSON, encoding="utf-8") as f:
        return json.load(f)


def to_canonical_js_injection(payload):
    gen = json.dumps(payload.get("generatedAt", ""))
    sd = json.dumps(payload["spendData"], separators=(",", ":"))
    kd = json.dumps(payload.get("kpiData") or {}, separators=(",", ":"))
    scl = json.dumps(payload.get("sectorCl") or {}, separators=(",", ":"))
    sig = json.dumps(payload.get("sectorIg") or {}, separators=(",", ":"))
    sts = json.dumps(payload.get("sectorTs") or {}, separators=(",", ":"))
    sscl = json.dumps(payload.get("sectorSpendCl") or {}, separators=(",", ":"))
    ssig = json.dumps(payload.get("sectorSpendIg") or {}, separators=(",", ":"))
    ssts = json.dumps(payload.get("sectorSpendTs") or {}, separators=(",", ":"))
    pcl = json.dumps(payload.get("ptypeCl") or {}, separators=(",", ":"))
    pig = json.dumps(payload.get("ptypeIg") or {}, separators=(",", ":"))
    pts = json.dumps(payload.get("ptypeTs") or {}, separators=(",", ":"))
    sacl = json.dumps(payload.get("sectorAreaCl") or {}, separators=(",", ":"))
    saig = json.dumps(payload.get("sectorAreaIg") or {}, separators=(",", ":"))
    sats = json.dumps(payload.get("sectorAreaTs") or {}, separators=(",", ":"))
    pacl = json.dumps(payload.get("ptypeAreaCl") or {}, separators=(",", ":"))
    paig = json.dumps(payload.get("ptypeAreaIg") or {}, separators=(",", ":"))
    pats = json.dumps(payload.get("ptypeAreaTs") or {}, separators=(",", ":"))
    pscl = json.dumps(payload.get("ptypeSpendCl") or {}, separators=(",", ":"))
    psig = json.dumps(payload.get("ptypeSpendIg") or {}, separators=(",", ":"))
    psts = json.dumps(payload.get("ptypeSpendTs") or {}, separators=(",", ":"))
    inner = f"""const sourceAnalysisCanonicalGeneratedAt = {gen};
const spendData = {sd};
const kpiData = {kd};
const sectorCl = {scl};
const sectorIg = {sig};
const sectorTs = {sts};
const sectorAreaCl = {sacl};
const sectorAreaIg = {saig};
const sectorAreaTs = {sats};
const sectorSpendCl = {sscl};
const sectorSpendIg = {ssig};
const sectorSpendTs = {ssts};
const ptypeCl = {pcl};
const ptypeIg = {pig};
const ptypeTs = {pts};
const ptypeAreaCl = {pacl};
const ptypeAreaIg = {paig};
const ptypeAreaTs = {pats};
const ptypeSpendCl = {pscl};
const ptypeSpendIg = {psig};
const ptypeSpendTs = {psts};"""
    return f"{CANONICAL_BLOCK_START}\n{inner}\n{CANONICAL_BLOCK_END}"


def main():
    if not CSV_PATH.is_file():
        print(f"Missing {CSV_PATH}; run run_closed_closeout_good_data_segments.py first.", file=sys.stderr)
        sys.exit(1)

    rows = load_csv_rows()
    payload = build_payload(rows)
    injection = to_js_injection(payload)

    html = HTML_PATH.read_text(encoding="utf-8")
    wrapped = injection

    if BLOCK_START in html and BLOCK_END in html:
        pattern = re.escape(BLOCK_START) + r"[\s\S]*?" + re.escape(BLOCK_END)
        html_new, n = re.subn(pattern, wrapped, html, count=1)
        if n != 1:
            print("Failed to replace curated data block", file=sys.stderr)
            sys.exit(1)
    elif LEGACY_MARKER in html:
        html_new = html.replace(LEGACY_MARKER, wrapped, 1)
    else:
        print(
            f"Neither {BLOCK_START!r}…{BLOCK_END!r} nor {LEGACY_MARKER!r} found in {HTML_PATH}",
            file=sys.stderr,
        )
        sys.exit(1)

    st_rows, st_gen = load_sector_type_area_rows()
    st_payload = build_sector_type_area_payload(st_rows, st_gen)
    st_wrapped = to_sector_area_js_injection(st_payload)
    if SECTOR_AREA_BLOCK_START in html_new and SECTOR_AREA_BLOCK_END in html_new:
        pat2 = re.escape(SECTOR_AREA_BLOCK_START) + r"[\s\S]*?" + re.escape(SECTOR_AREA_BLOCK_END)
        html_new, n2 = re.subn(pat2, st_wrapped, html_new, count=1)
        if n2 != 1:
            print("Failed to replace sector×type area block", file=sys.stderr)
            sys.exit(1)

    canon = load_canonical_embed_payload()
    canon_applied = False
    if canon and CANONICAL_BLOCK_START in html_new and CANONICAL_BLOCK_END in html_new:
        cwrap = to_canonical_js_injection(canon)
        patc = re.escape(CANONICAL_BLOCK_START) + r"[\s\S]*?" + re.escape(CANONICAL_BLOCK_END)
        html_new, nc = re.subn(patc, cwrap, html_new, count=1)
        if nc != 1:
            print("Failed to replace canonical source-analysis block", file=sys.stderr)
            sys.exit(1)
        canon_applied = True

    HTML_PATH.write_text(html_new, encoding="utf-8")
    msg = (
        f"Updated {HTML_PATH} ({len(rows):,} combinations ≥25, "
        f"{payload['meta']['projectsInDenseCells']:,} projects, {payload['meta']['sectorCount']} sectors)"
    )
    if SECTOR_TYPE_AREA_CSV.is_file():
        msg += f"; sector×type w/ area: {len(st_rows)} rows"
    if canon_applied:
        msg += "; canonical sector embed refreshed"
    print(msg)


if __name__ == "__main__":
    main()
