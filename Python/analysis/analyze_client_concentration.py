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

import csv
from collections import Counter
from pathlib import Path

DATA_FILE = PROJECT_ROOT / "data" / "dim" / "dim_project_budget_automation.csv"
OUT_FILE = PROJECT_ROOT / "markdown" / "client_concentration_fitout_newbuild.md"

TARGET_PHASES = {"closed", "closeout", "construct", "construction"}
US_COUNTRIES = {"united states", "us", "usa", "united states of america", "puerto rico", ""}

BANDS = [
    ("$1M-$5M",  1_000_000,  5_000_000),
    ("$5M-$10M", 5_000_000, 10_000_000),
    ("$10M+",   10_000_000, 100_000_000),
]


def get_band(amt):
    for label, lo, hi in BANDS:
        if lo < amt <= hi:
            return label
    return None


def analyze_type(rows, target_type):
    filtered = []
    for r in rows:
        phase = r.get("phase", "").strip().lower()
        if phase not in TARGET_PHASES:
            continue
        ptype = r.get("project_type", "").strip()
        if ptype != target_type:
            continue
        budget_usd = float(r.get("original_budget_usd") or 0)
        if budget_usd <= 1_000_000 or budget_usd > 100_000_000:
            continue
        currency = r.get("currency_code", "").strip().upper()
        country = r.get("country", "").strip().lower()
        if currency == "USD" and country not in US_COUNTRIES:
            continue
        client = r.get("client_name", "").strip() or "(Unknown)"
        band = get_band(budget_usd)
        if band is None:
            continue
        filtered.append({
            "client": client, "band": band, "budget_usd": budget_usd,
            "cc_count": int(r.get("cost_code_line_item_count") or 0),
        })

    total = len(filtered)
    client_counts = Counter(p["client"] for p in filtered)
    total_clients = len(client_counts)

    top_5_total = sum(c for _, c in client_counts.most_common(5))
    top_10_total = sum(c for _, c in client_counts.most_common(10))
    top_20_total = sum(c for _, c in client_counts.most_common(20))

    md = []
    md.append(f"## {target_type} — Client Concentration ({total:,} projects > $1M)")
    md.append("")
    md.append(f"**Overall**: {total:,} projects across **{total_clients:,} unique clients**")
    md.append("")
    md.append(f"- Top 5 clients: {top_5_total:,} projects ({100*top_5_total/total:.1f}%)")
    md.append(f"- Top 10 clients: {top_10_total:,} projects ({100*top_10_total/total:.1f}%)")
    md.append(f"- Top 20 clients: {top_20_total:,} projects ({100*top_20_total/total:.1f}%)")
    md.append("")

    # Client size distribution
    bucket_defs = [
        ("1 project", lambda c: c == 1),
        ("2-5 projects", lambda c: 2 <= c <= 5),
        ("6-10 projects", lambda c: 6 <= c <= 10),
        ("11-25 projects", lambda c: 11 <= c <= 25),
        ("26-50 projects", lambda c: 26 <= c <= 50),
        ("51-100 projects", lambda c: 51 <= c <= 100),
        ("100+ projects", lambda c: c > 100),
    ]

    md.append("**Client size distribution:**")
    md.append("")
    md.append("| Client Size | # Clients | % of Clients | # Projects | % of Projects |")
    md.append("|-------------|-----------|-------------|------------|---------------|")
    for label, pred in bucket_defs:
        matching = [(cl, cnt) for cl, cnt in client_counts.items() if pred(cnt)]
        if not matching:
            continue
        n_clients = len(matching)
        n_projects = sum(cnt for _, cnt in matching)
        md.append(
            f"| {label} | {n_clients:,} | {100*n_clients/total_clients:.1f}% "
            f"| {n_projects:,} | {100*n_projects/total:.1f}% |"
        )
    md.append("")

    # Top 15 clients
    md.append("**Top 15 clients:**")
    md.append("")
    md.append("| Rank | Client | Projects | % of Total | Avg Budget (USD) | Avg CCs |")
    md.append("|------|--------|----------|-----------|------------------|---------|")
    for rank, (client, cnt) in enumerate(client_counts.most_common(15), 1):
        cp = [p for p in filtered if p["client"] == client]
        avg_budget = sum(p["budget_usd"] for p in cp) / len(cp)
        avg_cc = sum(p["cc_count"] for p in cp) / len(cp)
        pct = 100 * cnt / total
        if avg_budget >= 1_000_000:
            budget_str = f"${avg_budget/1_000_000:.1f}M"
        else:
            budget_str = f"${avg_budget/1_000:,.0f}K"
        md.append(f"| {rank} | {client[:50]} | {cnt:,} | {pct:.1f}% | {budget_str} | {avg_cc:.1f} |")
    md.append("")

    # By band — top 5 clients per band
    for label, _, _ in BANDS:
        band_projects = [p for p in filtered if p["band"] == label]
        if len(band_projects) < 20:
            continue
        band_clients = Counter(p["client"] for p in band_projects)
        n_band = len(band_projects)
        n_band_clients = len(band_clients)
        top5 = band_clients.most_common(5)
        top5_total = sum(c for _, c in top5)

        md.append(f"### {label} ({n_band:,} projects, {n_band_clients:,} clients)")
        md.append("")
        md.append(f"- Top 5 clients hold **{100*top5_total/n_band:.1f}%** of projects")
        md.append("")
        md.append("| Rank | Client | Projects | % of Band |")
        md.append("|------|--------|----------|-----------|")
        for rank, (client, cnt) in enumerate(top5, 1):
            md.append(f"| {rank} | {client[:50]} | {cnt:,} | {100*cnt/n_band:.1f}% |")
        md.append("")

    # HHI
    shares = [cnt / total for cnt in client_counts.values()]
    hhi = sum(s ** 2 for s in shares)
    n = len(shares)
    hhi_norm = (hhi - 1 / n) / (1 - 1 / n) if n > 1 else 1.0

    md.append("### Concentration metrics")
    md.append("")
    md.append(f"- **HHI (Herfindahl-Hirschman Index)**: {hhi:.4f} (0 = perfectly dispersed, 1 = single client)")
    md.append(f"- **Normalized HHI**: {hhi_norm:.4f}")
    if hhi < 0.01:
        md.append("- Interpretation: **Highly dispersed** — no single client dominates")
    elif hhi < 0.05:
        md.append("- Interpretation: **Moderately dispersed** — some concentration but broad client base")
    elif hhi < 0.15:
        md.append("- Interpretation: **Moderately concentrated** — a few clients hold significant share")
    else:
        md.append("- Interpretation: **Highly concentrated** — dominated by a small number of clients")
    md.append("")

    return md


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    lines = ["# Client Concentration Analysis — Fitout & New Build (>$1M)", ""]
    lines.extend(analyze_type(rows, "Fitout"))
    lines.append("---")
    lines.append("")
    lines.extend(analyze_type(rows, "New Build"))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
