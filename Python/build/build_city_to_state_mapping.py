#!/usr/bin/env python3
"""
Build city -> state (abbreviation) mapping for US cities from budget query output.

1. Reads unique (city, country) from the budget CSV where country is United States.
   Use the same CSV that includes both Clarizen and Ingenious (sector + project type)
   so Ingenious cities get state mappings.
2. Resolves state using the USA cities/states reference dataset (grammakov/USA-cities-and-states).
3. Writes city_to_state_mapping.csv (city, country, state_abbrev) for use in the run script.

Run after refreshing budget data; then re-run the budget query script to apply the new mapping.
"""

import csv
import json
import os
import re
import ssl
import urllib.request
from collections import Counter
from typing import Optional

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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "mappings")
BUDGET_DATA = os.path.join(PROJECT_ROOT, "data", "budget")
# Prefer the dashboard CSV (sector + project type) so both Clarizen and Ingenious cities are included
BUDGET_CSV_PREFERRED = os.path.join(
    BUDGET_DATA,
    "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area_with_property_sector_and_project_type.csv",
)
BUDGET_CSV_FALLBACK = os.path.join(BUDGET_DATA, "budget_query_results_curated_closed_by_category_with_state.csv")
OUT_CSV = os.path.join(DATA_DIR, "city_to_state_mapping.csv")
REFERENCE_URL = "https://raw.githubusercontent.com/grammakov/USA-cities-and-states/master/us_cities_states_counties.csv"
REFERENCE_LOCAL = os.path.join(DATA_DIR, "us_cities_states_counties.csv")


def normalize_city(s: str) -> str:
    """Normalize for lookup: strip, remove trailing punctuation, collapse spaces, lowercase."""
    if not s:
        return ""
    s = s.strip().rstrip(",\t")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def load_us_city_to_states(from_path_or_url: Optional[str] = None):
    """
    Load reference CSV: City|State short|State full|County|City alias.
    Returns dict: normalized_city -> set of state abbreviations.
    If from_path_or_url is None: try REFERENCE_LOCAL file, then REFERENCE_URL (with SSL fallback).
    """
    city_states: dict[str, set[str]] = {}
    text = None
    if from_path_or_url:
        if os.path.isfile(from_path_or_url):
            with open(from_path_or_url, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        else:
            try:
                with urllib.request.urlopen(from_path_or_url, timeout=30) as resp:
                    text = resp.read().decode("utf-8", errors="replace")
            except ssl.SSLError:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(from_path_or_url, timeout=30, context=ctx) as resp:
                    text = resp.read().decode("utf-8", errors="replace")
    else:
        if os.path.isfile(REFERENCE_LOCAL):
            with open(REFERENCE_LOCAL, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        if not text:
            try:
                with urllib.request.urlopen(REFERENCE_URL, timeout=30) as resp:
                    text = resp.read().decode("utf-8", errors="replace")
            except (ssl.SSLError, OSError) as e1:
                try:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(REFERENCE_URL, timeout=30, context=ctx) as resp:
                        text = resp.read().decode("utf-8", errors="replace")
                except Exception as e2:
                    raise SystemExit(
                        f"Could not load reference. Save us_cities_states_counties.csv to {DATA_DIR}.\nURL error: {e1}; fallback: {e2}"
                    ) from e2
    if not text:
        raise SystemExit("No reference data loaded.")

    lines = text.splitlines()
    for line in lines[1:]:  # skip header "City|State short|..."
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        city, state_short = parts[0], parts[1]
        if not city or not state_short or len(state_short) != 2:
            continue
        key = normalize_city(city)
        if key not in city_states:
            city_states[key] = set()
        city_states[key].add(state_short.upper())

    return city_states


def extract_unique_us_cities(budget_csv_path: str) -> list[tuple[str, str]]:
    """Return list of (city, country) for rows where country is United States (or US/USA)."""
    us_aliases = {"united states", "us", "usa"}
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    with open(budget_csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            city = (row.get("city") or "").strip()
            country = (row.get("country") or "").strip()
            if not city:
                continue
            if country and country.lower() in us_aliases:
                key = (city, "United States")
                if key not in seen:
                    seen.add(key)
                    out.append(key)
    return out


def get_city_state_from_budget_csv(budget_csv_path: str):
    """Return dict: normalized_city -> most common state_abbrev seen in budget rows (US only)."""
    us_aliases = {"united states", "us", "usa"}
    city_states = {}
    with open(budget_csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            city = (row.get("city") or "").strip()
            country = (row.get("country") or "").strip()
            state = (row.get("state") or "").strip().upper()
            if not city or not state or len(state) != 2:
                continue
            if country and country.lower() in us_aliases:
                key = normalize_city(city)
                if key not in city_states:
                    city_states[key] = Counter()
                city_states.setdefault(key, Counter())[state] += 1
    return {k: v.most_common(1)[0][0] for k, v in city_states.items() if v}


def main() -> int:
    budget_csv = BUDGET_CSV_PREFERRED if os.path.isfile(BUDGET_CSV_PREFERRED) else BUDGET_CSV_FALLBACK
    if not os.path.isfile(budget_csv):
        print(f"Budget CSV not found. Tried: {BUDGET_CSV_PREFERRED!r} and {BUDGET_CSV_FALLBACK!r}")
        return 1
    print(f"Using budget CSV: {os.path.basename(budget_csv)}")

    print("Loading US city -> state reference...")
    city_to_states = load_us_city_to_states()
    print(f"Reference has {len(city_to_states)} unique cities.")

    print("Extracting unique US (city, country) from budget output...")
    unique_us = extract_unique_us_cities(budget_csv)
    print(f"Found {len(unique_us)} unique US city/country pairs.")

    # Prefer state from budget CSV when city appears with a state there (disambiguates multi-state cities)
    budget_city_state = get_city_state_from_budget_csv(budget_csv)
    print(f"Budget CSV has state for {len(budget_city_state)} cities; using to disambiguate when possible.")

    # Build mapping: (original_city, country) -> state_abbrev
    rows_out: list[tuple[str, str, str]] = []
    unmapped: list[str] = []
    ambiguous: list[tuple[str, str]] = []  # (city, states_str)

    for city_orig, country in unique_us:
        key = normalize_city(city_orig)
        states = city_to_states.get(key)
        if not states:
            unmapped.append(city_orig)
            # Use budget's state if we have it even when not in reference (e.g. typos)
            state_abbrev = budget_city_state.get(key, "")
            rows_out.append((city_orig, country, state_abbrev))
            continue
        states_sorted = sorted(states)
        preferred = budget_city_state.get(key)
        if preferred and preferred in states:
            state_abbrev = preferred
        else:
            state_abbrev = states_sorted[0]
        if len(states_sorted) > 1:
            ambiguous.append((city_orig, ",".join(states_sorted)))
        rows_out.append((city_orig, country, state_abbrev))

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "country", "state_abbrev"])
        w.writerows(rows_out)
    print(f"Wrote {OUT_CSV} ({len(rows_out)} rows).")

    out_json = os.path.join(PROJECT_ROOT, "data", "mappings", "city_to_state_mapping.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            [{"city": c, "country": co, "state_abbrev": s} for c, co, s in rows_out],
            f,
            indent=2,
        )
    print(f"Wrote {out_json} (same mapping, for run script).")

    if unmapped:
        print(f"Unmapped US cities (no state): {len(unmapped)}")
        for c in sorted(unmapped)[:25]:
            print(f"  - {c!r}")
        if len(unmapped) > 25:
            print(f"  ... and {len(unmapped) - 25} more")
    if ambiguous:
        print(f"Ambiguous (city in multiple states; used first): {len(ambiguous)}")
        for c, st in sorted(ambiguous)[:15]:
            print(f"  - {c!r} -> {st}")
        if len(ambiguous) > 15:
            print(f"  ... and {len(ambiguous) - 15} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
