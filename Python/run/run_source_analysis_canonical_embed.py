"""
Refresh canonical-sector aggregates for reports/ds_pds_source_system_analysis.html (spend bands + sector tabs).

Uses sql/sector_mapping_cte_generated.sql + sql/metro_lookup_cte_generated.sql +
sql/source_analysis_canonical_embed_frag.sql (same sector mapping as unified segment queries).

Sources: Clarizen (ADW) + Ingenious from work_dynamics.curated.project;
Tetrisoft from edp_sourcesystem.tetris (projects with POs + area > 0).

Writes data/source_analysis_canonical_embed.json and runs publish_curated_to_source_analysis_html.py.
"""
import json
import subprocess
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
from repo_paths import repo_root

PROJECT_ROOT = repo_root()
MAPPING_FILE = PROJECT_ROOT / "sql" / "sector" / "sector_mapping_cte_generated.sql"
METRO_FILE = PROJECT_ROOT / "sql" / "sector" / "metro_lookup_cte_generated.sql"
FRAG_FILE = PROJECT_ROOT / "sql" / "sector" / "source_analysis_canonical_embed_frag.sql"
OUT_JSON = PROJECT_ROOT / "data" / "analysis" / "source_analysis_canonical_embed.json"

ALL_BAND_KEYS = [
    "0 - No Budget",
    "1 - <$50K",
    "2 - $50K-$250K",
    "3 - $250K-$500K",
    "4 - $500K-$1M",
    "5 - $1M-$5M",
    "6 - $5M+",
]
BAND_KEYS_BUDGET = [k for k in ALL_BAND_KEYS if k != "0 - No Budget"]

SOURCES = ("clarizen", "ingenious", "tetrisoft")


def strip_leading_comment(text: str) -> str:
    t = text.strip()
    if t.startswith("--"):
        nl = t.find("\n")
        if nl != -1:
            t = t[nl + 1 :].lstrip()
    return t


def build_sql() -> str:
    mapping = strip_leading_comment(MAPPING_FILE.read_text(encoding="utf-8")).strip()
    metro = strip_leading_comment(METRO_FILE.read_text(encoding="utf-8")).strip().rstrip(",")
    frag = FRAG_FILE.read_text(encoding="utf-8").strip().rstrip(";")
    return f"WITH\n{mapping}\n{metro},\n{frag}"


def row_int(v):
    if v is None:
        return 0
    return int(v)


def empty_spend():
    return {k: 0 for k in ALL_BAND_KEYS}


def empty_band_matrix():
    return defaultdict(lambda: {k: 0 for k in BAND_KEYS_BUDGET})


def build_payload(rows, columns):
    idx = {c.lower(): i for i, c in enumerate(columns)}
    rk = idx["result_kind"]
    src = idx["source_system"]
    sec = idx["sector"]
    band = idx["spend_band"]
    cnt = idx["cnt"]
    cwa = idx.get("cnt_with_area")

    spend_data = {s: empty_spend() for s in SOURCES}
    kpi_data = {s: {"median_spend": 0, "p90_spend": 0, "total_projects": 0, "with_budget": 0, "with_area": 0} for s in SOURCES}
    sector_cl, sector_ig, sector_ts = {}, {}, {}
    sector_area_cl, sector_area_ig, sector_area_ts = {}, {}, {}
    ptype_cl, ptype_ig, ptype_ts = {}, {}, {}
    ptype_area_cl, ptype_area_ig, ptype_area_ts = {}, {}, {}
    mat_cl = empty_band_matrix()
    mat_ig = empty_band_matrix()
    mat_ts = empty_band_matrix()
    pspend_cl = empty_band_matrix()
    pspend_ig = empty_band_matrix()
    pspend_ts = empty_band_matrix()

    def sector_dict(source):
        if source == "clarizen":
            return sector_cl
        if source == "ingenious":
            return sector_ig
        return sector_ts

    def sector_area_dict(source):
        if source == "clarizen":
            return sector_area_cl
        if source == "ingenious":
            return sector_area_ig
        return sector_area_ts

    def ptype_dict(source):
        if source == "clarizen":
            return ptype_cl
        if source == "ingenious":
            return ptype_ig
        return ptype_ts

    def ptype_area_dict(source):
        if source == "clarizen":
            return ptype_area_cl
        if source == "ingenious":
            return ptype_area_ig
        return ptype_area_ts

    def sector_mat(source):
        if source == "clarizen":
            return mat_cl
        if source == "ingenious":
            return mat_ig
        return mat_ts

    def ptype_spend_mat(source):
        if source == "clarizen":
            return pspend_cl
        if source == "ingenious":
            return pspend_ig
        return pspend_ts

    for row in rows:
        kind = row_int(row[rk])
        source = (row[src] or "").strip().lower()
        if source not in SOURCES:
            continue
        c = row_int(row[cnt])
        wa = row_int(row[cwa]) if cwa is not None else 0
        if kind == 1:
            sector_name = row[sec]
            if sector_name is None:
                continue
            s = str(sector_name).strip()
            sd = sector_dict(source)
            sad = sector_area_dict(source)
            sd[s] = sd.get(s, 0) + c
            sad[s] = sad.get(s, 0) + wa
            kpi_data[source]["with_area"] = kpi_data[source]["with_area"] + wa
        elif kind == 2:
            sector_name = row[sec]
            b = row[band]
            if sector_name is None or b is None:
                continue
            s = str(sector_name).strip()
            b = str(b).strip()
            if b not in BAND_KEYS_BUDGET:
                continue
            m = sector_mat(source)
            m[s][b] = m[s][b] + c
        elif kind == 3:
            b = row[band]
            if b is None:
                continue
            b = str(b).strip()
            if b in spend_data[source]:
                spend_data[source][b] = spend_data[source][b] + c
        elif kind == 4:
            ptype_name = row[sec]
            if ptype_name is None:
                continue
            t = str(ptype_name).strip()
            pd = ptype_dict(source)
            pad = ptype_area_dict(source)
            pd[t] = pd.get(t, 0) + c
            pad[t] = pad.get(t, 0) + wa
        elif kind == 5:
            ptype_name = row[sec]
            b = row[band]
            if ptype_name is None or b is None:
                continue
            t = str(ptype_name).strip()
            b = str(b).strip()
            if b not in BAND_KEYS_BUDGET:
                continue
            m = ptype_spend_mat(source)
            m[t][b] = m[t][b] + c
        elif kind == 6:
            kpi_data[source]["median_spend"] = c
            kpi_data[source]["p90_spend"] = wa
        elif kind == 7:
            kpi_data[source]["total_projects"] = c
            kpi_data[source]["with_budget"] = wa

    def finalize_matrix(m):
        out = {}
        for name, bands in m.items():
            d = dict(bands)
            d["total"] = sum(d[k] for k in BAND_KEYS_BUDGET)
            out[name] = d
        return out

    return {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "spendData": spend_data,
        "kpiData": kpi_data,
        "sectorCl": sector_cl,
        "sectorIg": sector_ig,
        "sectorTs": sector_ts,
        "sectorAreaCl": sector_area_cl,
        "sectorAreaIg": sector_area_ig,
        "sectorAreaTs": sector_area_ts,
        "sectorSpendCl": finalize_matrix(mat_cl),
        "sectorSpendIg": finalize_matrix(mat_ig),
        "sectorSpendTs": finalize_matrix(mat_ts),
        "ptypeCl": ptype_cl,
        "ptypeIg": ptype_ig,
        "ptypeTs": ptype_ts,
        "ptypeAreaCl": ptype_area_cl,
        "ptypeAreaIg": ptype_area_ig,
        "ptypeAreaTs": ptype_area_ts,
        "ptypeSpendCl": finalize_matrix(pspend_cl),
        "ptypeSpendIg": finalize_matrix(pspend_ig),
        "ptypeSpendTs": finalize_matrix(pspend_ts),
    }


def main():
    for f in (MAPPING_FILE, METRO_FILE, FRAG_FILE):
        if not f.is_file():
            print(f"Missing {f}", file=sys.stderr)
            sys.exit(1)

    from edp_connection import connect_databricks

    sql = build_sql()
    print(f"Built SQL ({len(sql):,} chars)")

    conn = connect_databricks()
    cur = conn.cursor()
    print("Executing canonical embed query...")
    cur.execute(sql)
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    print(f"Fetched {len(rows):,} rows")

    payload = build_payload(rows, columns)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")

    pub = PROJECT_ROOT / "Python" / "run" / "publish_curated_to_source_analysis_html.py"
    r = subprocess.run([sys.executable, str(pub)], cwd=str(PROJECT_ROOT))
    if r.returncode != 0:
        sys.exit(r.returncode)
    print("Published HTML updates.")


if __name__ == "__main__":
    main()
