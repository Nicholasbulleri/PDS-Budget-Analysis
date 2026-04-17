#!/usr/bin/env python3
"""
Create unified benchmarking project list.

Merges two data sources into one Excel file using the Global CM Benchmarking
column structure as the canonical schema:
  1. Global CM Benchmarking - Project Info Sheet (manual XLS from regional teams)
  2. JLL internal project data from Databricks (dim_project_budget_benchmarking_filtered)

Hard costs are derived from generictask cost codes categorized as 'Construction'
or 'FF&E + Millwork' using projectedtotalcommitmentsamount.

Output: data/unified_benchmarking_project_list.xlsx
"""

import os
import re
import json
import sys
from datetime import datetime, date
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

from edp_connection import execute_query
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
XLS_INPUT = '/Users/nicholas.bulleri/Documents/Cost Management/Global CM Benchmarking - Project Info Sheet.xlsx'
SQL_INPUT = os.path.join(PROJECT_ROOT, 'sql', 'dim', 'dim_project_budget_benchmarking_filtered.sql')
OUTPUT = os.path.join(PROJECT_ROOT, 'data', 'dim', 'unified_benchmarking_project_list.xlsx')
SKIP_SHEETS = {'Template', 'Input Count', 'Asset List (Do not Edit)', '4.01 Data Centers'}

SQFT_TO_SQM = 0.092903
SQM_TO_SQFT = 10.7639
HARD_COST_USD_MINIMUM = 1_000_000
GEOCODE_CACHE = os.path.join(PROJECT_ROOT, 'data', 'mappings', 'geocode_cache.json')
GEOCODE_PRECISE_CACHE = os.path.join(PROJECT_ROOT, 'data', 'mappings', 'geocode_precise_cache.json')

# FX rates to USD (must match fx_rates CTE in benchmarking_unified_project_list.sql)
FX_TO_USD = {
    'AED': 0.27229408, 'ARS': 0.00068859, 'AUD': 0.70038851, 'BBD': 0.50000000,
    'BDT': 0.00815251, 'BGN': 0.58718010, 'BHD': 2.65957447, 'BND': 0.77948398,
    'BRL': 0.18991653, 'CAD': 0.72901919, 'CHF': 1.26534228, 'CLP': 0.00109429,
    'CNY': 0.14471684, 'COP': 0.00027088, 'CRC': 0.00212273, 'CZK': 0.04673519,
    'DKK': 0.15326575, 'EGP': 0.01904505, 'EUR': 1.14332231, 'FJD': 0.45100669,
    'GBP': 1.32389134, 'GHS': 0.09225582, 'GTQ': 0.13055730, 'HKD': 0.12774276,
    'HRK': 0.15174560, 'HUF': 0.00290904, 'IDR': 0.00005902, 'ILS': 0.31851759,
    'INR': 0.01078697, 'JOD': 1.41043724, 'JPY': 0.00626734, 'KES': 0.00774292,
    'KRW': 0.00066779, 'KWD': 3.26030256, 'KZT': 0.00204218, 'LKR': 0.00321668,
    'MAD': 0.10606175, 'MOP': 0.12402210, 'MUR': 0.02151465, 'MXN': 0.05586126,
    'MYR': 0.25392144, 'NGN': 0.00072230, 'NOK': 0.10233719, 'NZD': 0.57964899,
    'OMR': 2.60080053, 'PEN': 0.29039807, 'PGK': 0.23031954, 'PHP': 0.01672203,
    'PKR': 0.00358148, 'PLN': 0.26755917, 'PYG': 0.00015388, 'QAR': 0.27472527,
    'RON': 0.22515063, 'RSD': 0.00975580, 'RUB': 0.01247975, 'SAR': 0.26666667,
    'SEK': 0.10579981, 'SGD': 0.77948216, 'THB': 0.03088110, 'TND': 0.33970588,
    'TOP': 0.42321056, 'TRY': 0.02260965, 'TWD': 0.03113850, 'UAH': 0.02267583,
    'USD': 1.00000000, 'UYU': 0.02489600, 'VND': 0.00003823, 'VUV': 0.00840350,
    'WST': 0.36821969, 'XPF': 0.00958106, 'ZAR': 0.05920445,
}

# Country normalization — XLS values are the standard.
# Maps common variants (full names, ISO-2 codes, abbreviations) to the XLS canonical form.
COUNTRY_NORMALIZE = {
    # XLS standard forms
    'united states': 'USA', 'us': 'USA', 'usa': 'USA',
    'united kingdom': 'UK', 'gb': 'UK', 'uk': 'UK', 'great britain': 'UK', 'england': 'UK',
    'united arab emirates': 'UAE', 'ae': 'UAE', 'uae': 'UAE',
    'saudi arabia': 'KSA', 'sa': 'KSA', 'ksa': 'KSA',
    'india': 'India', 'in': 'India',
    'singapore': 'Singapore', 'sg': 'Singapore',
    'spain': 'Spain', 'es': 'Spain',
    'france': 'France', 'fr': 'France',
    'greece': 'Greece', 'gr': 'Greece',
    'germany': 'Germany', 'de': 'Germany',
    'italy': 'Italy', 'it': 'Italy',
    'portugal': 'Portugal', 'pt': 'Portugal',
    'ireland': 'Ireland', 'ie': 'Ireland',
    'israel': 'Israel', 'il': 'Israel',
    'norway': 'Norway', 'no': 'Norway',
    'sweden': 'Sweden', 'se': 'Sweden',
    # Common SQL variants not in XLS — normalize to full name
    'canada': 'Canada', 'ca': 'Canada',
    'australia': 'Australia', 'au': 'Australia',
    'china': 'China', 'cn': 'China',
    'japan': 'Japan', 'jp': 'Japan',
    'south korea': 'South Korea', 'kr': 'South Korea', 'korea': 'South Korea',
    'hong kong': 'Hong Kong', 'hk': 'Hong Kong',
    'mexico': 'Mexico', 'mx': 'Mexico',
    'brazil': 'Brazil', 'br': 'Brazil',
    'argentina': 'Argentina', 'ar': 'Argentina',
    'colombia': 'Colombia', 'co': 'Colombia',
    'chile': 'Chile', 'cl': 'Chile',
    'peru': 'Peru', 'pe': 'Peru',
    'costa rica': 'Costa Rica', 'cr': 'Costa Rica',
    'guatemala': 'Guatemala', 'gt': 'Guatemala',
    'el salvador': 'El Salvador', 'sv': 'El Salvador',
    'panama': 'Panama', 'pa': 'Panama',
    'uruguay': 'Uruguay', 'uy': 'Uruguay',
    'paraguay': 'Paraguay', 'py': 'Paraguay',
    'puerto rico': 'Puerto Rico', 'pr': 'Puerto Rico',
    'poland': 'Poland', 'pl': 'Poland',
    'finland': 'Finland', 'fi': 'Finland',
    'belgium': 'Belgium', 'be': 'Belgium',
    'netherlands': 'Netherlands', 'nl': 'Netherlands',
    'malaysia': 'Malaysia', 'my': 'Malaysia',
    'new zealand': 'New Zealand', 'nz': 'New Zealand',
    'papua new guinea': 'Papua New Guinea', 'pg': 'Papua New Guinea',
    'fiji': 'Fiji', 'fj': 'Fiji',
    'armenia': 'Armenia', 'am': 'Armenia',
}

WORKING_DAYS_PER_MONTH = 21.74


def normalize_country(value):
    """Normalize country name to canonical form using XLS as the standard."""
    if not value or not str(value).strip():
        return value
    raw = str(value).strip()
    key = raw.lower()
    if key in COUNTRY_NORMALIZE:
        return COUNTRY_NORMALIZE[key]
    # Already a clean full name not in the map — return as-is
    return raw


def load_geocode_caches():
    """Load both city-level and precise geocode caches."""
    city_cache = {}
    precise_cache = {}
    if os.path.exists(GEOCODE_CACHE):
        with open(GEOCODE_CACHE) as f:
            city_cache = json.load(f)
    if os.path.exists(GEOCODE_PRECISE_CACHE):
        with open(GEOCODE_PRECISE_CACHE) as f:
            precise_cache = json.load(f)
    return city_cache, precise_cache


def _extract_scope_location(scope):
    """Extract the most specific location reference from scope text."""
    if not scope or scope.strip() in ('', 'None'):
        return None
    candidates = []
    addr = re.search(
        r'(\d+\s+[\w\s]+(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Way|Lane|Ln|Place|Pl|Parkway|Pkwy)(?:\s*,\s*[\w\s]+)?)',
        scope, re.IGNORECASE)
    if addr:
        txt = addr.group(1).strip()
        if 5 < len(txt) < 80:
            candidates.append((0, txt))
    addr_match = re.search(r'(?:site\s*)?address\s*[:=]\s*([\w\s,.\-]+?)(?:\s*➢|\s*$|\n)', scope, re.IGNORECASE)
    if addr_match:
        txt = addr_match.group(1).strip()[:80]
        if len(txt) > 5:
            candidates.append((1, txt))
    named = re.findall(
        r'((?:[A-Z][\w\'-]*\s+){0,3}(?:Science\s+Park|Tech\s+Park|Business\s+Park|Industrial\s+Park|IT\s+Park|Campus|Tower|Centre|Center|Plaza|Mall|World\s+Trade)(?:\s+\d+)?)',
        scope)
    for n in named:
        n = n.strip()
        if 5 < len(n) < 60:
            candidates.append((2, n))
    at_match = re.search(
        r'\bat\s+([\w\s\'-]+(?:Park|Campus|Tower|Center|Centre|Plaza|Building|Complex|Square|Place|Point|Court|House|Hall|Village|City)[\w\s,]*)',
        scope, re.IGNORECASE)
    if at_match:
        txt = at_match.group(1).strip()[:60]
        if len(txt) > 5:
            candidates.append((3, txt))
    loc_match = re.search(
        r'located\s+(?:at|in|on)\s+([\w\s,.\'-]+?)(?:\.\s|\s*,\s*(?:the|which|having|with|comprising|a\s))',
        scope, re.IGNORECASE)
    if loc_match:
        txt = loc_match.group(1).strip()[:60]
        if len(txt) > 5:
            candidates.append((4, txt))
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1] if candidates else None


def _extract_name_location(pname):
    """Extract building/venue from project name."""
    if not pname:
        return None
    addr = re.search(r'(\d+\s+[\w\s]+(?:St|Street|Rd|Road|Ave|Avenue|Blvd|Dr|Drive|Way))\b', pname, re.IGNORECASE)
    if addr:
        return addr.group(1).strip()
    venue = re.search(r'([\w\s\'-]+(?:Park|Campus|Tower|Center|Centre|Plaza|Building|Complex|Square))', pname, re.IGNORECASE)
    if venue:
        txt = venue.group(1).strip()
        if len(txt) > 5:
            return txt
    return None


def geocode_lookup_tiered(city_cache, precise_cache, city, country, project_name=None, scope=None):
    """Tiered GPS lookup: scope location -> project name -> city + country."""
    city_s = str(city or '').strip()
    country_s = str(country or '').strip()

    # Tier 1: scope-extracted location
    scope_loc = _extract_scope_location(scope)
    if scope_loc:
        q = f"{scope_loc}, {city_s}, {country_s}" if city_s else f"{scope_loc}, {country_s}"
        result = precise_cache.get(q)
        if result and isinstance(result, dict):
            return f"{result['lat']}, {result['lng']}"

    # Tier 2: project name location
    name_loc = _extract_name_location(project_name)
    if name_loc:
        q = f"{name_loc}, {city_s}, {country_s}" if city_s else f"{name_loc}, {country_s}"
        result = precise_cache.get(q)
        if result and isinstance(result, dict):
            return f"{result['lat']}, {result['lng']}"

    # Tier 3: city + country fallback
    if city_s or country_s:
        q = f"{city_s}, {country_s}" if city_s and country_s else city_s or country_s
        result = city_cache.get(q)
        if result and isinstance(result, dict):
            return f"{result['lat']}, {result['lng']}"

    return None


# --- Unified output column definitions ---
# First group: standard XLS columns; second group: supplementary SQL-only columns.
UNIFIED_COLUMNS = [
    'Data Source Origin',
    'Custom ID',
    'Data Inserted by whom',
    'Ingenious Build Generated ID',
    'Data Source',
    'Project Name',
    'Project Type',
    'Asset Type or Industry / Sector',
    'Country',
    'City or Location',
    'Project GPS Coordinates',
    'Approximate Building Age',
    'Building Height',
    'Project Cost Document Type',
    'Project Cost Document WBS Format',
    'Project Cost Document file name',
    'Date of Pricing or Contract Commencement Date',
    'Base Currency',
    'Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)',
    'Committed Hard Costs (USD)',
    'Cost Breakdown: Preliminaries / General Requirements / Bonds & Insurance',
    'Cost Breakdown: Civil / Structural / Architectural',
    'Cost Breakdown: MEP / IT / AV / Security',
    'Cost Breakdown: FF&E / OS&E / Furniture',
    'Cost Breakdown: Other Hard Costs (unclassified lump sums)',
    'Construction Cost Per m²',
    'Construction Cost Per sqft',
    'Procurement Type',
    'Project Construction Schedule Duration (months)',
    'Project Construction Schedule file name',
    'Client',
    'Lead Architect',
    'Lead Engineer',
    'Main Contractor',
    'Number of basement levels',
    'Number of above ground levels',
    'Total number of Levels',
    'Built Up Area (BUA) in m²',
    'Gross Area m² (GIA or GFA)',
    'Gross Area sqft',
    'Rentable Area m²',
    'Net to Gross Floorplate Efficiency %',
    'Wall to Floor Ratio',
    'Sustainability Rating',
    'Project Risk Register file name',
    'Project Specification file name',
    'Project Scope / Supplementary information',
    'Supporting Documents file names',
    'JLL Contract Document (scope and fees) file name',
    'Reviewed and relocated to "Approved Folder" by',
    'Date approved',
    # --- Supplementary SQL-only columns ---
    'Source System',
    'Phase',
    'Status',
    'Project Sub Type',
    'State / Province',
    'Metro',
    'Unit of Measure (raw)',
    'Area (raw, as stored)',
    'Original Budget (all cost codes, local)',
    'Original Budget (USD)',
    'Current Budget (local)',
    'Total Anticipated Cost (all cost codes)',
    'Total Anticipated Cost (USD)',
    'Variance to Budget',
    'Construction Costs (category subtotal)',
    'Soft Costs (category subtotal)',
    'Total All Costs',
    'Hard Costs Original Budget',
    'Project Create Date',
    'Start Date',
    'Due Date',
    'Year-Month',
    'Year-Quarter',
    'Tags',
    'JLL Role',
    'Business Line',
    'Cost Code Line Item Count',
    'Cost Codes List',
    'Work Item Identifier',
    'Source Project Identifier',
    'Project Document URL',
    'Source System Project URL',
]

LAST_XLS_COL_INDEX = UNIFIED_COLUMNS.index('Date approved')

# Category classification logic (from APP_budget_closed_by_category)
CATEGORY_CASE_SQL = """
    CASE
      WHEN LOWER(TRIM(g.taskname)) RLIKE '^(11|12)[\\\\s\\\\-]' THEN 'FF&E + Millwork'
      WHEN LOWER(TRIM(g.taskname)) RLIKE '^[0-9]{2}[\\\\s\\\\-]' THEN 'Construction'
      WHEN LOWER(TRIM(g.taskname)) RLIKE '^\\\\s*\\\\-[\\\\s]*[0-9]{2}\\\\s' THEN 'Construction'
      WHEN LOWER(TRIM(g.taskname)) RLIKE 'div[\\\\s]*[0-9]+' THEN 'Construction'
      WHEN LOWER(TRIM(g.taskname)) LIKE '%soft%' AND (LOWER(g.taskname) LIKE '%contingency%' OR LOWER(g.taskname) LIKE '%cost%') THEN 'Soft Costs'
      WHEN LOWER(TRIM(g.taskname)) LIKE '%design%' AND (LOWER(g.taskname) LIKE '%contingency%' OR LOWER(g.taskname) LIKE '%allowance%') THEN 'Soft Costs'
      WHEN LOWER(g.taskname) LIKE '%contingency%' AND (LOWER(g.taskname) LIKE '%ff&e%' OR LOWER(g.taskname) LIKE '%furniture%') THEN 'FF&E + Millwork'
      WHEN LOWER(g.taskname) LIKE '%contingency%' OR LOWER(g.taskname) LIKE '%allowance%' THEN 'Construction'
      WHEN LOWER(g.taskname) LIKE '%furniture%' OR LOWER(g.taskname) LIKE '%millwork%' OR LOWER(g.taskname) LIKE '%ff&e%' OR LOWER(g.taskname) LIKE '%ffe%'
           OR LOWER(g.taskname) LIKE '%artwork%' OR LOWER(g.taskname) LIKE '% signage%' OR LOWER(g.taskname) LIKE '%branding%'
           OR LOWER(g.taskname) LIKE '%audio visual%' OR LOWER(g.taskname) LIKE '%audio-visual%' OR LOWER(g.taskname) LIKE '%audio/visual%'
           OR LOWER(g.taskname) LIKE '%a/v%' OR LOWER(g.taskname) LIKE '% it %' OR LOWER(g.taskname) LIKE '% it'
           OR LOWER(g.taskname) LIKE '%equipment%' OR LOWER(g.taskname) LIKE '%appliances%' OR LOWER(g.taskname) LIKE '%blinds%'
           OR LOWER(g.taskname) LIKE '%workstations%' OR LOWER(g.taskname) LIKE '%seating%' OR LOWER(g.taskname) LIKE '%carpet%'
           OR LOWER(g.taskname) LIKE '%(it)%' OR LOWER(g.taskname) LIKE '%information technology%'
           OR LOWER(g.taskname) LIKE '%tech/comm%' OR LOWER(g.taskname) LIKE '%technology%' OR LOWER(g.taskname) LIKE '%data cabling%'
           OR LOWER(g.taskname) LIKE '%voice/data%' OR LOWER(g.taskname) LIKE '%signage%' OR LOWER(g.taskname) LIKE '%graphics%'
           OR LOWER(g.taskname) LIKE '%security monitoring%' OR LOWER(g.taskname) LIKE '%furnishings%'
           OR (LOWER(g.taskname) LIKE 'moving%' OR LOWER(g.taskname) LIKE '% moving %') OR LOWER(g.taskname) LIKE '%it server%' OR LOWER(g.taskname) LIKE '%it hardware%'
           OR LOWER(g.taskname) LIKE '%telecom%' OR LOWER(g.taskname) LIKE '%cabling%' OR LOWER(g.taskname) LIKE '%atm%'
      THEN 'FF&E + Millwork'
      WHEN LOWER(g.taskname) LIKE '%architect%' OR LOWER(g.taskname) LIKE '%designer%' OR LOWER(g.taskname) LIKE '%engineer%'
           OR LOWER(g.taskname) LIKE '%consultant%' OR LOWER(g.taskname) LIKE '%expeditor%' OR LOWER(g.taskname) LIKE '%permit%'
           OR LOWER(g.taskname) LIKE '% pm fee%' OR LOWER(g.taskname) LIKE '%jll %' OR LOWER(g.taskname) LIKE '%project management%'
           OR LOWER(g.taskname) LIKE '%inspection%' OR LOWER(g.taskname) LIKE '%survey%' OR LOWER(g.taskname) LIKE '%legal%'
           OR LOWER(g.taskname) LIKE '%insurance%' OR LOWER(g.taskname) LIKE '%leed%' OR LOWER(g.taskname) LIKE '%sustainability%'
           OR LOWER(g.taskname) LIKE '%design fee%' OR LOWER(g.taskname) LIKE '%reimbursable%' OR LOWER(g.taskname) LIKE '%admin fee%'
           OR LOWER(g.taskname) LIKE '%management fee%' OR LOWER(g.taskname) LIKE '%soft cost%'
           OR LOWER(g.taskname) LIKE '%fee-%' OR LOWER(g.taskname) LIKE '%fee -%' OR LOWER(g.taskname) LIKE 'fee%' OR LOWER(g.taskname) LIKE '% fees%'
           OR LOWER(g.taskname) LIKE '%development fee%' OR LOWER(g.taskname) LIKE '%developer cost%'
           OR LOWER(g.taskname) LIKE '%leasing commission%' OR LOWER(g.taskname) LIKE '%leasing- commission%'
           OR LOWER(g.taskname) LIKE '%professional fee%' OR LOWER(g.taskname) LIKE '%pm fee%' OR LOWER(g.taskname) LIKE '%pm fees%'
           OR LOWER(g.taskname) LIKE '%tax (%' OR LOWER(g.taskname) LIKE '%sales tax%' OR LOWER(g.taskname) LIKE '%vat (%'
           OR LOWER(g.taskname) LIKE '%overhead allocation%' OR LOWER(g.taskname) LIKE '%marketing%'
           OR LOWER(g.taskname) LIKE '%test fit%' OR LOWER(g.taskname) = 'jll'
           OR LOWER(g.taskname) LIKE '%move & storage%' OR LOWER(g.taskname) LIKE '%move and storage%'
           OR LOWER(g.taskname) LIKE '%additional forecasted fee%jll%' OR LOWER(g.taskname) LIKE '%additional forecasted fee jll%'
           OR LOWER(g.taskname) LIKE '%40101000-design-eng-mgmt%' OR (LOWER(g.taskname) LIKE '%40101000%' AND (LOWER(g.taskname) LIKE '%design%' OR LOWER(g.taskname) LIKE '%eng%' OR LOWER(g.taskname) LIKE '%mgmt%'))
      THEN 'Soft Costs'
      WHEN LOWER(g.taskname) LIKE '%general contractor%' OR LOWER(g.taskname) LIKE '% gc %' OR LOWER(g.taskname) LIKE 'gc %' OR LOWER(g.taskname) LIKE '% gmp %'
           OR LOWER(g.taskname) LIKE '%construction%' OR LOWER(g.taskname) LIKE '%concrete%' OR LOWER(g.taskname) LIKE '%structural%'
           OR LOWER(g.taskname) LIKE '%electrical%' OR LOWER(g.taskname) LIKE '%plumbing%' OR LOWER(g.taskname) LIKE '%hvac%'
           OR LOWER(g.taskname) LIKE '%demolition%' OR LOWER(g.taskname) LIKE '%sitework%' OR LOWER(g.taskname) LIKE '%earthwork%'
           OR LOWER(g.taskname) LIKE '%general conditions%' OR LOWER(g.taskname) LIKE '%drywall%' OR LOWER(g.taskname) LIKE '%framing%'
           OR LOWER(g.taskname) LIKE '%flooring%' OR LOWER(g.taskname) LIKE '%ceilings%' OR LOWER(g.taskname) LIKE '%painting%'
           OR LOWER(g.taskname) LIKE '%fire protection%' OR LOWER(g.taskname) LIKE '%fire sprinkler%' OR LOWER(g.taskname) LIKE '%roofing%'
           OR LOWER(g.taskname) LIKE '%facade%' OR LOWER(g.taskname) LIKE '%cladding%' OR LOWER(g.taskname) LIKE '%hard cost%'
           OR LOWER(TRIM(g.taskname)) LIKE '$%'
           OR LOWER(TRIM(g.taskname)) RLIKE '^[0-9]+\\\\.' OR LOWER(TRIM(g.taskname)) RLIKE '^[0-9]+\\\\s+[a-z]'
           OR LOWER(g.taskname) LIKE 'land %' OR LOWER(g.taskname) LIKE '% land %' OR LOWER(g.taskname) LIKE '%land acquisition%'
           OR LOWER(g.taskname) LIKE '%land develop%' OR LOWER(g.taskname) LIKE '%land cost%' OR LOWER(g.taskname) LIKE '%purchase land%'
           OR LOWER(g.taskname) = 'land'
           OR LOWER(g.taskname) LIKE '%conveying%' OR LOWER(g.taskname) LIKE '%elevator%'
           OR LOWER(g.taskname) LIKE '%gen requirement%' OR LOWER(g.taskname) LIKE '%gen cond%' OR LOWER(g.taskname) LIKE '%general requirement%'
           OR LOWER(g.taskname) LIKE '%leasehold improvement%' OR LOWER(g.taskname) LIKE '%tenant improvement%'
           OR LOWER(g.taskname) LIKE '%main contractor%' OR LOWER(g.taskname) LIKE '%main contract%'
           OR LOWER(g.taskname) LIKE '%mechanical%' OR LOWER(g.taskname) LIKE '%interior work%' OR LOWER(g.taskname) LIKE '%exterior work%'
           OR LOWER(g.taskname) LIKE '%external work%' OR LOWER(g.taskname) LIKE '%civil%' OR LOWER(g.taskname) LIKE '%site infrastructure%'
           OR LOWER(g.taskname) LIKE '%base building%' OR LOWER(g.taskname) LIKE '%parking%' OR LOWER(g.taskname) LIKE '%finishes%'
           OR LOWER(g.taskname) LIKE '%partition%' OR LOWER(g.taskname) LIKE '%metals%'
           OR LOWER(g.taskname) LIKE '%contigenc%' OR LOWER(g.taskname) LIKE '%contingenc%'
           OR LOWER(g.taskname) LIKE '%building improvement%' OR LOWER(g.taskname) LIKE '%site improvement%'
           OR LOWER(g.taskname) LIKE '%landscap%' OR LOWER(g.taskname) LIKE '%decommission%'
           OR LOWER(g.taskname) LIKE '%design/build%' OR LOWER(g.taskname) LIKE '%peb%'
           OR LOWER(g.taskname) LIKE '%contractor''s fee%' OR LOWER(g.taskname) LIKE '%contractors fee%'
           OR LOWER(g.taskname) LIKE '%security%'
           OR LOWER(g.taskname) LIKE '%woods%' OR LOWER(g.taskname) LIKE '%plastics%'
           OR LOWER(g.taskname) LIKE '%interior%'
           OR LOWER(g.taskname) LIKE '%condo%' OR LOWER(g.taskname) LIKE '%lobby buildout%'
      THEN 'Construction'
      WHEN LOWER(g.taskname) LIKE '%furn%' OR LOWER(g.taskname) LIKE '%equip%' THEN 'FF&E + Millwork'
      ELSE 'Other'
    END"""


def is_sqm(uom):
    """Determine if unit of measure is square meters."""
    if not uom:
        return False
    u = str(uom).lower().strip()
    return any(k in u for k in ('sqm', 'sq m', 'square m', 'meter', 'metre', 'm2', 'm²'))


def convert_to_usd(amount, currency_code):
    """Convert a local-currency amount to USD. Returns None if conversion not possible."""
    if amount is None:
        return None
    try:
        amt = float(amount)
    except (ValueError, TypeError):
        return None
    if not currency_code:
        return amt  # assume USD if no currency
    code = str(currency_code).strip().upper()
    if code == 'USD' or code == '':
        return amt
    rate = FX_TO_USD.get(code)
    if rate is None:
        return None
    return round(amt * rate, 2)


def build_modified_sql():
    """Read the base SQL and inject hard-cost categorization, property data,
    cost sub-breakdowns, main contractor, and unit of measure."""
    with open(SQL_INPUT) as f:
        sql = f.read()

    # 1. Replace cost_code_summary CTE with cost_code_detail + hard_cost_summary
    #    (includes sub-category breakdowns) + property_gps + main_contractor CTEs
    old_ccs = (
        "cost_code_summary AS (\n"
        "  SELECT\n"
        "    g.projectidentifier,\n"
        "    COUNT(*) AS cost_code_line_item_count,\n"
        "    ARRAY_JOIN(COLLECT_SET(g.taskname), '; ') AS cost_codes_list,\n"
        "    SUM(g.originalbudgetamount) AS gt_original_budget,\n"
        "    SUM(g.totalapprovedbudgetamount) AS gt_current_budget,\n"
        "    SUM(g.projectedtotalcommitmentsamount) AS gt_total_anticipated_cost\n"
        "  FROM work_dynamics.curated.generictask g\n"
        "  WHERE g.taskname IS NOT NULL\n"
        "    AND TRIM(g.taskname) <> ''\n"
        "    AND g.originalbudgetamount IS NOT NULL\n"
        "    AND g.originalbudgetamount > 0\n"
        "  GROUP BY g.projectidentifier\n"
        "),"
    )

    new_ccs = f"""cost_code_categorized AS (
  SELECT
    g.projectidentifier,
    g.taskname,
    g.originalbudgetamount,
    g.totalapprovedbudgetamount,
    g.projectedtotalcommitmentsamount,
{CATEGORY_CASE_SQL} AS category
  FROM work_dynamics.curated.generictask g
  WHERE g.taskname IS NOT NULL
    AND TRIM(g.taskname) <> ''
    AND g.originalbudgetamount IS NOT NULL
    AND g.originalbudgetamount > 0
),
cost_code_detail AS (
  SELECT cc.*,
    CASE
      WHEN cc.category = 'FF&E + Millwork' THEN 'FF&E'
      WHEN cc.category <> 'Construction' THEN NULL
      WHEN (
        LOWER(TRIM(cc.taskname)) RLIKE '^01[\\\\s\\\\-]'
        OR LOWER(cc.taskname) LIKE '%general conditions%'
        OR LOWER(cc.taskname) LIKE '%general requirement%'
        OR LOWER(cc.taskname) LIKE '%gen requirement%'
        OR LOWER(cc.taskname) LIKE '%gen cond%'
        OR LOWER(cc.taskname) LIKE '%bond%'
        OR LOWER(cc.taskname) LIKE '%insurance%'
        OR LOWER(cc.taskname) LIKE '%preliminary%'
        OR LOWER(cc.taskname) LIKE '%preliminaries%'
      ) THEN 'Preliminaries'
      WHEN (
        LOWER(TRIM(cc.taskname)) RLIKE '^(2[1-8])[\\\\s\\\\-]'
        OR LOWER(cc.taskname) LIKE '%mechanical%'
        OR LOWER(cc.taskname) LIKE '%electrical%'
        OR LOWER(cc.taskname) LIKE '%plumbing%'
        OR LOWER(cc.taskname) LIKE '%hvac%'
        OR LOWER(cc.taskname) LIKE '%fire protection%'
        OR LOWER(cc.taskname) LIKE '%fire sprinkler%'
        OR LOWER(cc.taskname) LIKE '%mep%'
        OR LOWER(cc.taskname) LIKE '%security%'
        OR LOWER(cc.taskname) LIKE '%audio visual%'
        OR LOWER(cc.taskname) LIKE '%audio-visual%'
        OR LOWER(cc.taskname) LIKE '%technology%'
        OR LOWER(cc.taskname) LIKE '%data cabling%'
        OR LOWER(cc.taskname) LIKE '%telecom%'
      ) THEN 'MEP'
      WHEN (
        LOWER(TRIM(cc.taskname)) RLIKE '^(0[2-9]|10)[\\\\s\\\\-]'
        OR LOWER(cc.taskname) LIKE '%concrete%'
        OR LOWER(cc.taskname) LIKE '%structural%'
        OR LOWER(cc.taskname) LIKE '%civil%'
        OR LOWER(cc.taskname) LIKE '%masonry%'
        OR LOWER(cc.taskname) LIKE '%metals%'
        OR LOWER(cc.taskname) LIKE '%finishes%'
        OR LOWER(cc.taskname) LIKE '%drywall%'
        OR LOWER(cc.taskname) LIKE '%framing%'
        OR LOWER(cc.taskname) LIKE '%flooring%'
        OR LOWER(cc.taskname) LIKE '%ceilings%'
        OR LOWER(cc.taskname) LIKE '%painting%'
        OR LOWER(cc.taskname) LIKE '%facade%'
        OR LOWER(cc.taskname) LIKE '%cladding%'
        OR LOWER(cc.taskname) LIKE '%roofing%'
        OR LOWER(cc.taskname) LIKE '%partition%'
        OR LOWER(cc.taskname) LIKE '%demolition%'
        OR LOWER(cc.taskname) LIKE '%sitework%'
        OR LOWER(cc.taskname) LIKE '%earthwork%'
        OR LOWER(cc.taskname) LIKE '%landscap%'
        OR LOWER(cc.taskname) LIKE '%interior%'
      ) THEN 'Civil/Structural/Architectural'
      ELSE 'Other Hard Costs'
    END AS sub_category
  FROM cost_code_categorized cc
),
hard_cost_summary AS (
  SELECT
    projectidentifier,
    COUNT(*) AS cost_code_line_item_count,
    ARRAY_JOIN(COLLECT_SET(taskname), '; ') AS cost_codes_list,
    SUM(originalbudgetamount) AS gt_original_budget,
    SUM(totalapprovedbudgetamount) AS gt_current_budget,
    SUM(projectedtotalcommitmentsamount) AS gt_total_anticipated_cost,
    SUM(CASE WHEN category IN ('Construction', 'FF&E + Millwork') THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS total_hard_costs,
    SUM(CASE WHEN category = 'Construction' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS construction_costs,
    SUM(CASE WHEN category = 'Soft Costs' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS soft_costs,
    SUM(COALESCE(projectedtotalcommitmentsamount, 0)) AS total_all_costs,
    SUM(CASE WHEN category IN ('Construction', 'FF&E + Millwork') THEN COALESCE(originalbudgetamount, 0) ELSE 0 END) AS hard_costs_original_budget,
    SUM(CASE WHEN sub_category = 'Preliminaries' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS prelims_costs,
    SUM(CASE WHEN sub_category = 'Civil/Structural/Architectural' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS civil_struct_arch_costs,
    SUM(CASE WHEN sub_category = 'MEP' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS mep_it_av_costs,
    SUM(CASE WHEN sub_category = 'FF&E' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS ffe_costs,
    SUM(CASE WHEN sub_category = 'Other Hard Costs' THEN COALESCE(projectedtotalcommitmentsamount, 0) ELSE 0 END) AS other_hard_costs
  FROM cost_code_detail
  GROUP BY projectidentifier
),
property_gps AS (
  SELECT
    prop.id AS property_id,
    prop.addresses[0].addressGeolocation.geoLatitude AS gps_lat,
    prop.addresses[0].addressGeolocation.geoLongitude AS gps_lng
  FROM work_dynamics.curated.property prop
  WHERE prop.addresses IS NOT NULL AND SIZE(prop.addresses) > 0
),
main_contractor AS (
  SELECT workitemidentifier, commitmentname AS main_contractor_name
  FROM (
    SELECT c.workitemidentifier, c.commitmentname,
      ROW_NUMBER() OVER (PARTITION BY c.workitemidentifier ORDER BY COALESCE(c.approvedamount, 0) DESC) AS rn
    FROM work_dynamics.curated.commitment c
    WHERE c.commitmentname IS NOT NULL AND c.commitmentname <> ''
      AND LOWER(c.commitmentname) NOT LIKE '%jll%'
      AND LOWER(c.commitmentname) NOT LIKE '%historical%'
      AND COALESCE(c.approvedamount, 0) > 0
  )
  WHERE rn = 1
),"""

    sql = sql.replace(old_ccs, new_ccs)

    # 2. Add unitofmeasure + additional fields to base CTE
    sql = sql.replace(
        "    p.tags\n  FROM work_dynamics.curated.project p",
        "    p.tags,\n"
        "    LOWER(TRIM(COALESCE(CAST(p.unitofmeasure AS STRING), ''))) AS unit_of_measure,\n"
        "    p.rentablearea,\n"
        "    p.grossarea AS project_gross_area,\n"
        "    COALESCE(p.sustainabilitycertificationtext, '') AS sustainability_cert,\n"
        "    p.propertyidentifier,\n"
        "    p.projecturl\n"
        "  FROM work_dynamics.curated.project p"
    )

    # 3. Replace cost_code_summary alias with hard_cost_summary
    sql = sql.replace('cost_code_summary ccs', 'hard_cost_summary hcs')
    sql = sql.replace('ccs.', 'hcs.')

    # 4. Add new computed columns before FROM base b
    old_from = "    hcs.cost_codes_list\n  FROM base b"
    new_cols = """    hcs.cost_codes_list,
    COALESCE(hcs.total_hard_costs, 0) AS total_hard_costs,
    COALESCE(hcs.construction_costs, 0) AS construction_costs,
    COALESCE(hcs.ffe_costs, 0) AS ffe_costs,
    COALESCE(hcs.soft_costs, 0) AS soft_costs,
    COALESCE(hcs.total_all_costs, 0) AS total_all_costs,
    COALESCE(hcs.hard_costs_original_budget, 0) AS hard_costs_original_budget,
    COALESCE(hcs.prelims_costs, 0) AS prelims_costs,
    COALESCE(hcs.civil_struct_arch_costs, 0) AS civil_struct_arch_costs,
    COALESCE(hcs.mep_it_av_costs, 0) AS mep_it_av_costs,
    COALESCE(hcs.other_hard_costs, 0) AS other_hard_costs,
    b.unit_of_measure,
    CASE
      WHEN b.unit_of_measure IN ('sqm', 'sm', 'm2', 'square meters', 'square metres')
        OR b.unit_of_measure LIKE '%meter%' OR b.unit_of_measure LIKE '%metre%'
      THEN b.area
      ELSE b.area * 0.092903
    END AS area_sqm,
    CASE
      WHEN b.unit_of_measure IN ('sqm', 'sm', 'm2', 'square meters', 'square metres')
        OR b.unit_of_measure LIKE '%meter%' OR b.unit_of_measure LIKE '%metre%'
      THEN b.area * 10.7639
      ELSE b.area
    END AS area_sqft,
    CASE WHEN b.area > 0 AND COALESCE(hcs.total_hard_costs, 0) > 0 THEN
      COALESCE(hcs.total_hard_costs, 0) / NULLIF(
        CASE WHEN b.unit_of_measure IN ('sqm', 'sm', 'm2', 'square meters', 'square metres')
          OR b.unit_of_measure LIKE '%meter%' OR b.unit_of_measure LIKE '%metre%'
        THEN b.area ELSE b.area * 0.092903 END, 0)
      ELSE NULL END AS cost_per_sqm,
    CASE WHEN b.area > 0 AND COALESCE(hcs.total_hard_costs, 0) > 0 THEN
      COALESCE(hcs.total_hard_costs, 0) / NULLIF(
        CASE WHEN b.unit_of_measure IN ('sqm', 'sm', 'm2', 'square meters', 'square metres')
          OR b.unit_of_measure LIKE '%meter%' OR b.unit_of_measure LIKE '%metre%'
        THEN b.area * 10.7639 ELSE b.area END, 0)
      ELSE NULL END AS cost_per_sqft,
    CASE
      WHEN b.currency_code = 'USD' OR b.currency_code = '' OR b.currency_code IS NULL
        THEN COALESCE(hcs.total_hard_costs, 0)
      ELSE ROUND(COALESCE(hcs.total_hard_costs, 0) * COALESCE(fx.exchangerate, 0), 2)
    END AS total_hard_costs_usd,
    CASE WHEN pg.gps_lat IS NOT NULL AND pg.gps_lng IS NOT NULL
      THEN CONCAT(CAST(pg.gps_lat AS STRING), ', ', CAST(pg.gps_lng AS STRING))
      ELSE NULL
    END AS gps_coordinates,
    b.sustainability_cert,
    CASE
      WHEN b.rentablearea IS NOT NULL AND b.rentablearea > 0 THEN
        CASE WHEN b.unit_of_measure IN ('sqm', 'sm', 'm2', 'square meters', 'square metres')
          OR b.unit_of_measure LIKE '%meter%' OR b.unit_of_measure LIKE '%metre%'
        THEN b.rentablearea ELSE b.rentablearea * 0.092903 END
      ELSE NULL
    END AS rentable_area_sqm,
    CASE
      WHEN b.project_gross_area IS NOT NULL AND b.project_gross_area > 0 THEN
        CASE WHEN b.unit_of_measure IN ('sqm', 'sm', 'm2', 'square meters', 'square metres')
          OR b.unit_of_measure LIKE '%meter%' OR b.unit_of_measure LIKE '%metre%'
        THEN b.project_gross_area ELSE b.project_gross_area * 0.092903 END
      ELSE NULL
    END AS bua_sqm,
    CASE WHEN b.rentablearea > 0 AND b.project_gross_area > 0
      THEN b.rentablearea / b.project_gross_area
      ELSE NULL
    END AS net_to_gross_pct,
    mc.main_contractor_name,
    b.projecturl
  FROM base b"""
    sql = sql.replace(old_from, new_cols)

    # 5. Add new JOINs (property_gps and main_contractor)
    sql = sql.replace(
        "  LEFT JOIN fx_rates fx\n    ON fx.sourcecurrencycode = b.currency_code\n)",
        "  LEFT JOIN fx_rates fx\n    ON fx.sourcecurrencycode = b.currency_code\n"
        "  LEFT JOIN property_gps pg\n    ON pg.property_id = b.propertyidentifier\n"
        "  LEFT JOIN main_contractor mc\n    ON mc.workitemidentifier = b.workitemidentifier\n)"
    )

    return sql


def run_databricks_query(sql):
    """Execute the modified SQL against Databricks and return (columns, rows)."""
    print(f"Executing query ({len(sql):,} chars) against Databricks...")
    columns, rows = execute_query(sql)
    print(f"  Returned {len(rows):,} rows, {len(columns)} columns")
    return columns, rows


def read_xls_data():
    """Read all project data from the Global CM Benchmarking spreadsheet."""
    print(f"Reading XLS: {XLS_INPUT}")
    wb = openpyxl.load_workbook(XLS_INPUT, read_only=True, data_only=True)
    projects = []

    for sheet_name in wb.sheetnames:
        if sheet_name in SKIP_SHEETS:
            continue

        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 4:
            continue

        country_label = sheet_name.split(' ', 1)[1] if ' ' in sheet_name else sheet_name
        data_rows = rows[3:]

        for row in data_rows:
            custom_id = row[0] if len(row) > 0 else None
            project_name = row[4] if len(row) > 4 else None
            if not custom_id or str(custom_id).strip() == '':
                continue
            if not project_name or str(project_name).strip() == '':
                continue

            def safe(idx):
                return row[idx] if len(row) > idx else None

            projects.append({
                'sheet': sheet_name,
                'country_label': country_label,
                'custom_id': safe(0),
                'data_inserted_by': safe(1),
                'ingenious_id': safe(2),
                'data_source_name': safe(3),
                'project_name': safe(4),
                'project_type': safe(5),
                'sector': safe(6),
                'country': safe(7),
                'city': safe(8),
                'gps': safe(9),
                'building_age': safe(10),
                'building_height': safe(11),
                'cost_doc_type': safe(12),
                'cost_doc_wbs': safe(13),
                'cost_doc_filename': safe(14),
                'date_of_pricing': safe(15),
                'currency': safe(16),
                'hard_costs': safe(17),
                'breakdown_prelims': safe(18),
                'breakdown_civil': safe(19),
                'breakdown_mep': safe(20),
                'breakdown_ffe': safe(21),
                'cost_per_sqm': safe(22),
                'procurement_type': safe(23),
                'schedule_duration': safe(24),
                'schedule_filename': safe(25),
                'client': safe(26),
                'lead_architect': safe(27),
                'lead_engineer': safe(28),
                'main_contractor': safe(29),
                'basement_levels': safe(30),
                'above_ground_levels': safe(31),
                'total_levels': safe(32),
                'bua_sqm': safe(33),
                'gross_area_sqm': safe(34),
                'rentable_area_sqm': safe(35),
                'net_to_gross': safe(36),
                'wall_to_floor': safe(37),
                'sustainability': safe(38),
                'risk_register': safe(39),
                'specification': safe(40),
                'project_scope': safe(41),
                'supporting_docs': safe(42),
                'jll_contract': safe(43),
                'reviewed_by': safe(44),
                'date_approved': safe(45),
            })

    wb.close()
    print(f"  Read {len(projects)} projects from {len([s for s in wb.sheetnames if s not in SKIP_SHEETS])} country sheets")
    return projects


def _col(name):
    """Return the index of a column name in UNIFIED_COLUMNS."""
    return UNIFIED_COLUMNS.index(name)


def map_xls_to_unified_row(p):
    """Map an XLS project dict to a unified output row."""
    gross_sqm = p.get('gross_area_sqm')
    gross_sqft = None
    cost_per_sqft = None
    if gross_sqm is not None:
        try:
            gross_sqft = float(gross_sqm) * SQM_TO_SQFT
        except (ValueError, TypeError):
            pass
    if p.get('cost_per_sqm') is not None:
        try:
            cost_per_sqft = float(p['cost_per_sqm']) / SQM_TO_SQFT
        except (ValueError, TypeError):
            pass

    hc_usd = convert_to_usd(p.get('hard_costs'), p.get('currency'))

    row = [None] * len(UNIFIED_COLUMNS)
    row[_col('Data Source Origin')] = f"XLS - {p['country_label']}"
    row[_col('Custom ID')] = p['custom_id']
    row[_col('Data Inserted by whom')] = p['data_inserted_by']
    row[_col('Ingenious Build Generated ID')] = p['ingenious_id']
    row[_col('Data Source')] = p['data_source_name']
    row[_col('Project Name')] = p['project_name']
    row[_col('Project Type')] = p['project_type']
    row[_col('Asset Type or Industry / Sector')] = p['sector']
    row[_col('Country')] = normalize_country(p['country'])
    row[_col('City or Location')] = p['city']
    row[_col('Project GPS Coordinates')] = p['gps']
    pt = str(p.get('project_type') or '').strip().lower()
    if 'new' in pt and ('build' in pt or 'construction' in pt):
        row[_col('Approximate Building Age')] = 'New Build'
    else:
        row[_col('Approximate Building Age')] = p['building_age']
    row[_col('Building Height')] = p['building_height']
    row[_col('Project Cost Document Type')] = p['cost_doc_type']
    row[_col('Project Cost Document WBS Format')] = p['cost_doc_wbs']
    row[_col('Project Cost Document file name')] = p['cost_doc_filename']
    row[_col('Date of Pricing or Contract Commencement Date')] = p['date_of_pricing']
    row[_col('Base Currency')] = p['currency']
    row[_col('Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)')] = p['hard_costs']
    row[_col('Committed Hard Costs (USD)')] = hc_usd
    row[_col('Cost Breakdown: Preliminaries / General Requirements / Bonds & Insurance')] = p['breakdown_prelims']
    row[_col('Cost Breakdown: Civil / Structural / Architectural')] = p['breakdown_civil']
    row[_col('Cost Breakdown: MEP / IT / AV / Security')] = p['breakdown_mep']
    row[_col('Cost Breakdown: FF&E / OS&E / Furniture')] = p['breakdown_ffe']
    row[_col('Construction Cost Per m²')] = p['cost_per_sqm']
    row[_col('Construction Cost Per sqft')] = cost_per_sqft
    row[_col('Procurement Type')] = p['procurement_type']
    row[_col('Project Construction Schedule Duration (months)')] = p['schedule_duration']
    row[_col('Project Construction Schedule file name')] = p['schedule_filename']
    row[_col('Client')] = p['client']
    row[_col('Lead Architect')] = p['lead_architect']
    row[_col('Lead Engineer')] = p['lead_engineer']
    row[_col('Main Contractor')] = p['main_contractor']
    row[_col('Number of basement levels')] = p['basement_levels']
    row[_col('Number of above ground levels')] = p['above_ground_levels']
    row[_col('Total number of Levels')] = p['total_levels']
    row[_col('Built Up Area (BUA) in m²')] = p['bua_sqm']
    row[_col('Gross Area m² (GIA or GFA)')] = p['gross_area_sqm']
    row[_col('Gross Area sqft')] = gross_sqft
    row[_col('Rentable Area m²')] = p['rentable_area_sqm']
    row[_col('Net to Gross Floorplate Efficiency %')] = p['net_to_gross']
    row[_col('Wall to Floor Ratio')] = p['wall_to_floor']
    row[_col('Sustainability Rating')] = p['sustainability']
    row[_col('Project Risk Register file name')] = p['risk_register']
    row[_col('Project Specification file name')] = p['specification']
    row[_col('Project Scope / Supplementary information')] = p['project_scope']
    row[_col('Supporting Documents file names')] = p['supporting_docs']
    row[_col('JLL Contract Document (scope and fees) file name')] = p['jll_contract']
    row[_col('Reviewed and relocated to "Approved Folder" by')] = p['reviewed_by']
    row[_col('Date approved')] = p['date_approved']
    return row


def map_sql_to_unified_row(sql_col_map, r):
    """Map a SQL result row to a unified output row."""
    def g(col):
        idx = sql_col_map.get(col)
        if idx is None:
            return None
        return r[idx]

    row = [None] * len(UNIFIED_COLUMNS)

    src = g('sourcesystem') or ''
    row[_col('Data Source Origin')] = f"Databricks - {src.title()}"
    row[_col('Custom ID')] = g('sourceprojectidentifier')
    row[_col('Ingenious Build Generated ID')] = g('workitemidentifier')
    row[_col('Data Source')] = src.title() if src else None
    row[_col('Project Name')] = g('projectname')
    row[_col('Project Type')] = g('project_type')
    row[_col('Asset Type or Industry / Sector')] = g('sector')
    row[_col('Country')] = normalize_country(g('country'))
    row[_col('City or Location')] = g('city')

    sql_pt = str(g('project_type') or '').strip().lower()
    if 'new' in sql_pt and ('build' in sql_pt or 'construction' in sql_pt):
        row[_col('Approximate Building Age')] = 'New Build'

    date_val = g('startdatetime')
    if date_val is None:
        date_val = g('project_create_date')
    row[_col('Date of Pricing or Contract Commencement Date')] = date_val
    row[_col('Base Currency')] = g('currency_code')
    row[_col('Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)')] = g('total_hard_costs')
    row[_col('Committed Hard Costs (USD)')] = g('total_hard_costs_usd')
    row[_col('Cost Breakdown: Preliminaries / General Requirements / Bonds & Insurance')] = g('prelims_costs')
    row[_col('Cost Breakdown: Civil / Structural / Architectural')] = g('civil_struct_arch_costs')
    row[_col('Cost Breakdown: MEP / IT / AV / Security')] = g('mep_it_av_costs')
    row[_col('Cost Breakdown: FF&E / OS&E / Furniture')] = g('ffe_costs')
    row[_col('Cost Breakdown: Other Hard Costs (unclassified lump sums)')] = g('other_hard_costs')
    row[_col('Construction Cost Per m²')] = g('cost_per_sqm')
    row[_col('Construction Cost Per sqft')] = g('cost_per_sqft')
    duration_raw = g('duration')
    if duration_raw is not None:
        try:
            duration_months = round(float(duration_raw) / WORKING_DAYS_PER_MONTH, 1)
        except (ValueError, TypeError):
            duration_months = duration_raw
    else:
        duration_months = None
    row[_col('Project Construction Schedule Duration (months)')] = duration_months
    row[_col('Client')] = g('client_name')
    row[_col('Main Contractor')] = g('main_contractor_name')
    row[_col('Built Up Area (BUA) in m²')] = g('bua_sqm')
    row[_col('Gross Area m² (GIA or GFA)')] = g('area_sqm')
    row[_col('Gross Area sqft')] = g('area_sqft')
    row[_col('Rentable Area m²')] = g('rentable_area_sqm')
    row[_col('Net to Gross Floorplate Efficiency %')] = g('net_to_gross_pct')
    row[_col('Project GPS Coordinates')] = g('gps_coordinates')

    sustainability_raw = g('sustainability_cert')
    if sustainability_raw and sustainability_raw.strip() and sustainability_raw.strip() != '[]':
        val = sustainability_raw.strip()
        if val.startswith('[') and val.endswith(']'):
            try:
                import json
                items = json.loads(val)
                val = ', '.join(str(i) for i in items)
            except Exception:
                val = val.strip('[]"')
        row[_col('Sustainability Rating')] = val

    row[_col('Project Scope / Supplementary information')] = g('description')

    # --- Supplementary SQL-only columns ---
    row[_col('Source System')] = g('sourcesystem')
    row[_col('Phase')] = g('phase')
    row[_col('Status')] = g('status')
    row[_col('Project Sub Type')] = g('project_sub_type')
    row[_col('State / Province')] = g('state')
    row[_col('Metro')] = g('metro')
    row[_col('Unit of Measure (raw)')] = g('unit_of_measure')
    row[_col('Area (raw, as stored)')] = g('area')
    row[_col('Original Budget (all cost codes, local)')] = g('original_budget')
    row[_col('Original Budget (USD)')] = g('original_budget_usd')
    row[_col('Current Budget (local)')] = g('current_budget')
    row[_col('Total Anticipated Cost (all cost codes)')] = g('total_anticipated_cost')
    row[_col('Total Anticipated Cost (USD)')] = g('total_anticipated_cost_usd')
    row[_col('Variance to Budget')] = g('variance_to_budget')
    row[_col('Construction Costs (category subtotal)')] = g('construction_costs')
    row[_col('Soft Costs (category subtotal)')] = g('soft_costs')
    row[_col('Total All Costs')] = g('total_all_costs')
    row[_col('Hard Costs Original Budget')] = g('hard_costs_original_budget')
    row[_col('Project Create Date')] = g('project_create_date')
    row[_col('Start Date')] = g('startdatetime')
    row[_col('Due Date')] = g('duedatetime')
    row[_col('Year-Month')] = g('year_month')
    row[_col('Year-Quarter')] = g('year_quarter')
    row[_col('Tags')] = g('tags')
    row[_col('JLL Role')] = g('jll_role')
    row[_col('Business Line')] = g('business_line')
    row[_col('Cost Code Line Item Count')] = g('cost_code_line_item_count')
    row[_col('Cost Codes List')] = g('cost_codes_list')
    row[_col('Work Item Identifier')] = g('workitemidentifier')
    row[_col('Source Project Identifier')] = g('sourceprojectidentifier')
    row[_col('Project Document URL')] = g('projectdocumenturltext')
    row[_col('Source System Project URL')] = g('projecturl')
    return row


def create_unified_excel(xls_rows, sql_rows, output_path):
    """Create the unified Excel workbook."""
    wb = openpyxl.Workbook()

    # --- Sheet 1: Unified Projects ---
    ws = wb.active
    ws.title = "Unified Projects"

    # Styles
    header_font = Font(bold=True, size=10)
    data_font = Font(size=10)
    header_fill_xls = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
    header_fill_supp = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    xls_row_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    sql_row_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9'),
    )

    # Column format classification
    CURRENCY_COLS = {
        'Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)',
        'Committed Hard Costs (USD)',
        'Cost Breakdown: Preliminaries / General Requirements / Bonds & Insurance',
        'Cost Breakdown: Civil / Structural / Architectural',
        'Cost Breakdown: MEP / IT / AV / Security',
        'Cost Breakdown: FF&E / OS&E / Furniture',
        'Cost Breakdown: Other Hard Costs (unclassified lump sums)',
        'Original Budget (all cost codes, local)',
        'Original Budget (USD)',
        'Current Budget (local)',
        'Total Anticipated Cost (all cost codes)',
        'Total Anticipated Cost (USD)',
        'Variance to Budget',
        'Construction Costs (category subtotal)',
        'Soft Costs (category subtotal)',
        'Total All Costs',
        'Hard Costs Original Budget',
    }
    RATE_COLS = {
        'Construction Cost Per m²',
        'Construction Cost Per sqft',
    }
    DATE_COLS = {
        'Date of Pricing or Contract Commencement Date',
        'Date approved',
        'Project Create Date',
        'Start Date',
        'Due Date',
    }
    NUMBER_COLS = {
        'Number of basement levels',
        'Number of above ground levels',
        'Total number of Levels',
        'Cost Code Line Item Count',
    }
    AREA_COLS = {
        'Built Up Area (BUA) in m²',
        'Gross Area m² (GIA or GFA)',
        'Gross Area sqft',
        'Rentable Area m²',
        'Area (raw, as stored)',
    }
    PCT_COLS = {
        'Net to Gross Floorplate Efficiency %',
        'Wall to Floor Ratio',
    }

    FMT_CURRENCY = '#,##0'
    FMT_RATE = '#,##0.00'
    FMT_DATE = 'YYYY-MM-DD'
    FMT_NUMBER = '#,##0'
    FMT_AREA = '#,##0'
    FMT_PCT = '0%'

    col_formats = {}
    for i, name in enumerate(UNIFIED_COLUMNS):
        col_1based = i + 1
        if name in CURRENCY_COLS:
            col_formats[col_1based] = FMT_CURRENCY
        elif name in RATE_COLS:
            col_formats[col_1based] = FMT_RATE
        elif name in DATE_COLS:
            col_formats[col_1based] = FMT_DATE
        elif name in NUMBER_COLS:
            col_formats[col_1based] = FMT_NUMBER
        elif name in AREA_COLS:
            col_formats[col_1based] = FMT_AREA
        elif name in PCT_COLS:
            col_formats[col_1based] = FMT_PCT

    for col_idx, col_name in enumerate(UNIFIED_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        cell.border = thin_border
        if col_idx <= LAST_XLS_COL_INDEX + 1:
            cell.fill = header_fill_xls
        else:
            cell.fill = header_fill_supp

    all_rows = xls_rows + sql_rows
    for row_idx, data_row in enumerate(all_rows, 2):
        is_xls = row_idx - 2 < len(xls_rows)
        for col_idx, value in enumerate(data_row, 1):
            # Strip timezone from datetimes
            if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                value = value.replace(tzinfo=None)
            # For date columns, strip time component if it's a datetime with midnight time
            fmt = col_formats.get(col_idx)
            if fmt == FMT_DATE and hasattr(value, 'date') and callable(value.date):
                value = value.date()
            # For currency/number columns, ensure numeric (skip non-numeric strings)
            if fmt in (FMT_CURRENCY, FMT_RATE, FMT_AREA, FMT_NUMBER) and isinstance(value, str):
                try:
                    value = float(value.replace(',', '').replace('$', ''))
                except (ValueError, TypeError):
                    pass

            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = data_font
            cell.border = thin_border
            if fmt and not isinstance(value, str):
                cell.number_format = fmt

        origin_cell = ws.cell(row=row_idx, column=1)
        origin_cell.fill = xls_row_fill if is_xls else sql_row_fill

    # Column widths by type
    col_widths = {}
    for i, name in enumerate(UNIFIED_COLUMNS):
        col_letter = get_column_letter(i + 1)
        if name in CURRENCY_COLS:
            col_widths[col_letter] = 22
        elif name in RATE_COLS:
            col_widths[col_letter] = 18
        elif name in DATE_COLS:
            col_widths[col_letter] = 14
        elif name in AREA_COLS:
            col_widths[col_letter] = 16
        elif name in ('Project Name', 'Project Scope / Supplementary information', 'Cost Codes List'):
            col_widths[col_letter] = 40
        elif name in ('Data Source Origin', 'Country', 'City or Location', 'Client',
                       'Asset Type or Industry / Sector', 'Project Type'):
            col_widths[col_letter] = 24
        elif name in ('Custom ID', 'Ingenious Build Generated ID', 'Work Item Identifier',
                       'Source Project Identifier', 'Project Document URL',
                       'Source System Project URL'):
            col_widths[col_letter] = 28
        else:
            col_widths[col_letter] = 18

    for letter, width in col_widths.items():
        ws.column_dimensions[letter].width = width

    ws.auto_filter.ref = f"A1:{get_column_letter(len(UNIFIED_COLUMNS))}1"
    ws.freeze_panes = "B2"

    # --- Sheet 2: Column Mapping & Gaps ---
    ws2 = wb.create_sheet("Column Mapping & Gaps")
    mapping_headers = [
        'Unified Column Name', 'Column #', 'Standard XLS Column?',
        'Available from XLS Spreadsheet?', 'Available from Databricks SQL?',
        'SQL Source Field', 'Gap Notes'
    ]
    for col_idx, h in enumerate(mapping_headers, 1):
        cell = ws2.cell(row=1, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill_xls

    xls_available = {
        'Data Source Origin', 'Custom ID', 'Data Inserted by whom',
        'Ingenious Build Generated ID', 'Data Source', 'Project Name',
        'Project Type', 'Asset Type or Industry / Sector', 'Country',
        'City or Location', 'Project GPS Coordinates', 'Approximate Building Age',
        'Building Height', 'Project Cost Document Type', 'Project Cost Document WBS Format',
        'Project Cost Document file name',
        'Date of Pricing or Contract Commencement Date', 'Base Currency',
        'Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)',
        'Committed Hard Costs (USD)',
        'Cost Breakdown: Preliminaries / General Requirements / Bonds & Insurance',
        'Cost Breakdown: Civil / Structural / Architectural',
        'Cost Breakdown: MEP / IT / AV / Security',
        'Cost Breakdown: FF&E / OS&E / Furniture',
        'Cost Breakdown: Other Hard Costs (unclassified lump sums)',
        'Construction Cost Per m²', 'Construction Cost Per sqft',
        'Procurement Type', 'Project Construction Schedule Duration (months)',
        'Project Construction Schedule file name',
        'Client', 'Lead Architect', 'Lead Engineer', 'Main Contractor',
        'Number of basement levels', 'Number of above ground levels',
        'Total number of Levels', 'Built Up Area (BUA) in m²',
        'Gross Area m² (GIA or GFA)', 'Gross Area sqft', 'Rentable Area m²',
        'Net to Gross Floorplate Efficiency %', 'Wall to Floor Ratio',
        'Sustainability Rating', 'Project Risk Register file name',
        'Project Specification file name',
        'Project Scope / Supplementary information',
        'Supporting Documents file names',
        'JLL Contract Document (scope and fees) file name',
        'Reviewed and relocated to "Approved Folder" by', 'Date approved',
    }

    sql_field_map = {
        'Data Source Origin': ('sourcesystem', ''),
        'Custom ID': ('sourceprojectidentifier', ''),
        'Ingenious Build Generated ID': ('workitemidentifier', ''),
        'Data Source': ('sourcesystem', ''),
        'Project Name': ('projectname', ''),
        'Project Type': ('project_type', ''),
        'Asset Type or Industry / Sector': ('sector', ''),
        'Country': ('country', ''),
        'City or Location': ('city', ''),
        'Project GPS Coordinates': ('gps_coordinates', 'From property.addresses[0].addressGeolocation (lat/lng); ~42% fill rate'),
        'Date of Pricing or Contract Commencement Date': ('startdatetime / project_create_date', 'Uses startdatetime; falls back to project_create_date if null'),
        'Base Currency': ('currency_code', ''),
        'Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)': ('total_hard_costs', 'Sum of projectedtotalcommitmentsamount for Construction + FF&E cost codes, in project base currency'),
        'Committed Hard Costs (USD)': ('total_hard_costs_usd', 'Hard costs converted to USD using FX rates'),
        'Cost Breakdown: Preliminaries / General Requirements / Bonds & Insurance': ('prelims_costs', 'Derived from cost code taskname patterns (CSI Div 01, gen conditions, bonds, insurance)'),
        'Cost Breakdown: Civil / Structural / Architectural': ('civil_struct_arch_costs', 'Derived from cost code taskname patterns (CSI Divs 02-10, concrete, structural, finishes, etc.)'),
        'Cost Breakdown: MEP / IT / AV / Security': ('mep_it_av_costs', 'Derived from cost code taskname patterns (CSI Divs 21-28, mechanical, electrical, plumbing, etc.)'),
        'Cost Breakdown: FF&E / OS&E / Furniture': ('ffe_costs', 'FF&E + Millwork category subtotal'),
        'Cost Breakdown: Other Hard Costs (unclassified lump sums)': ('other_hard_costs', 'Hard costs not classifiable into Prelims/Civil-Struct-Arch/MEP/FF&E; typically generic lump-sum line items (e.g. "Construction", "General Construction")'),
        'Construction Cost Per m²': ('cost_per_sqm', 'Derived: total_hard_costs / area_sqm'),
        'Construction Cost Per sqft': ('cost_per_sqft', 'Derived: total_hard_costs / area_sqft'),
        'Project Construction Schedule Duration (months)': ('duration', 'Converted from working days to months (÷ 21.74)'),
        'Client': ('client_name', ''),
        'Main Contractor': ('main_contractor_name', 'Largest non-JLL commitment by approved amount; heuristic - review recommended'),
        'Built Up Area (BUA) in m²': ('bua_sqm', 'From project.grossarea, converted to m² using unitofmeasure'),
        'Gross Area m² (GIA or GFA)': ('area_sqm', 'Converted from raw area using unitofmeasure'),
        'Gross Area sqft': ('area_sqft', 'Converted from raw area using unitofmeasure'),
        'Rentable Area m²': ('rentable_area_sqm', 'From project.rentablearea, converted to m² using unitofmeasure'),
        'Net to Gross Floorplate Efficiency %': ('net_to_gross_pct', 'Derived: rentablearea / grossarea (where both > 0)'),
        'Sustainability Rating': ('sustainability_cert', 'From project.sustainabilitycertificationtext; ~3.5% fill rate'),
        'Project Scope / Supplementary information': ('description', ''),
    }

    sql_only_always = set(UNIFIED_COLUMNS[LAST_XLS_COL_INDEX + 1:])

    missing_fill = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")

    for i, col_name in enumerate(UNIFIED_COLUMNS):
        row_num = i + 2
        is_standard = (i <= LAST_XLS_COL_INDEX)
        from_xls = 'Yes' if col_name in xls_available else 'No'
        sql_info = sql_field_map.get(col_name)
        from_sql = 'Yes' if (sql_info or col_name in sql_only_always) else 'No'
        sql_field = sql_info[0] if sql_info else (col_name if col_name in sql_only_always else '')
        gap_note = ''
        if sql_info:
            gap_note = sql_info[1]
        elif is_standard and not sql_info and col_name not in sql_only_always and col_name != 'Data Source Origin':
            gap_note = 'NOT AVAILABLE in Databricks dataset'

        ws2.cell(row=row_num, column=1, value=col_name)
        ws2.cell(row=row_num, column=2, value=i + 1)
        ws2.cell(row=row_num, column=3, value='Yes' if is_standard else 'Supplementary')
        ws2.cell(row=row_num, column=4, value=from_xls)
        ws2.cell(row=row_num, column=5, value=from_sql)
        ws2.cell(row=row_num, column=6, value=sql_field)
        ws2.cell(row=row_num, column=7, value=gap_note)

        if 'NOT AVAILABLE' in gap_note:
            for c in range(1, 8):
                ws2.cell(row=row_num, column=c).fill = missing_fill

    for col_idx in range(1, 8):
        ws2.column_dimensions[get_column_letter(col_idx)].width = 25
    ws2.column_dimensions['A'].width = 55
    ws2.column_dimensions['G'].width = 60
    ws2.auto_filter.ref = "A1:G1"
    ws2.freeze_panes = "A2"

    # --- Sheet 3: Summary ---
    ws3 = wb.create_sheet("Summary")
    ws3.cell(row=1, column=1, value="Unified Benchmarking Summary").font = Font(bold=True, size=14)
    ws3.cell(row=2, column=1, value=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    summary_data = [
        ('', ''),
        ('Total Projects', len(xls_rows) + len(sql_rows)),
        ('  XLS (Global CM Benchmarking sheet)', len(xls_rows)),
        ('  Databricks (dim_project_budget_benchmarking_filtered)', len(sql_rows)),
        ('', ''),
        ('Total Unified Columns', len(UNIFIED_COLUMNS)),
        ('  Standard XLS Columns', LAST_XLS_COL_INDEX + 1),
        ('  Supplementary SQL Columns', len(UNIFIED_COLUMNS) - LAST_XLS_COL_INDEX - 1),
    ]
    for i, (label, val) in enumerate(summary_data, 4):
        ws3.cell(row=i, column=1, value=label).font = Font(bold=label and not label.startswith(' '))
        ws3.cell(row=i, column=2, value=val)
    ws3.column_dimensions['A'].width = 55
    ws3.column_dimensions['B'].width = 15

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"\nSaved unified workbook: {output_path}")
    print(f"  Sheet 'Unified Projects': {len(xls_rows) + len(sql_rows)} rows x {len(UNIFIED_COLUMNS)} columns")
    print(f"  Sheet 'Column Mapping & Gaps': documents all field mappings and missing fields")
    print(f"  Sheet 'Summary': high-level counts")


def filter_by_hard_costs_usd(rows, source_label):
    """Filter rows to only include projects with hard costs > $1M USD."""
    hc_usd_col = _col('Committed Hard Costs (USD)')
    hc_local_col = _col('Committed Hard Costs in Base Currency (Construction + FF&E, excl VAT/Taxes)')
    currency_col = _col('Base Currency')

    kept = []
    skipped_below = 0
    skipped_no_data = 0

    for row in rows:
        hc_usd = row[hc_usd_col]
        if hc_usd is None:
            hc_usd = convert_to_usd(row[hc_local_col], row[currency_col])
        if hc_usd is None:
            skipped_no_data += 1
            continue
        try:
            if float(hc_usd) > HARD_COST_USD_MINIMUM:
                kept.append(row)
            else:
                skipped_below += 1
        except (ValueError, TypeError):
            skipped_no_data += 1

    print(f"  {source_label}: {len(kept)} kept, {skipped_below} below ${HARD_COST_USD_MINIMUM:,.0f} USD, {skipped_no_data} missing hard cost data")
    return kept


def main():
    print("=" * 80)
    print("UNIFIED BENCHMARKING PROJECT LIST BUILDER")
    print(f"Filter: Hard Costs (USD) > ${HARD_COST_USD_MINIMUM:,.0f}")
    print("=" * 80)

    # Step 1: Read XLS
    xls_projects = read_xls_data()
    xls_rows = [map_xls_to_unified_row(p) for p in xls_projects]
    print(f"  Mapped {len(xls_rows)} XLS projects to unified schema")

    # Step 2: Build and run modified SQL
    sql = build_modified_sql()
    sql_columns, sql_data = run_databricks_query(sql)
    sql_col_map = {name: idx for idx, name in enumerate(sql_columns)}
    sql_rows = [map_sql_to_unified_row(sql_col_map, r) for r in sql_data]
    print(f"  Mapped {len(sql_rows)} Databricks projects to unified schema")

    # Step 3: Filter both sources — hard costs converted to USD must exceed $1M
    print(f"\nApplying hard costs filter (> ${HARD_COST_USD_MINIMUM:,.0f} USD)...")
    xls_rows = filter_by_hard_costs_usd(xls_rows, "XLS")
    sql_rows = filter_by_hard_costs_usd(sql_rows, "Databricks")

    # Step 4: Fill missing GPS coordinates from geocode caches (tiered)
    city_cache, precise_cache = load_geocode_caches()
    if city_cache or precise_cache:
        gps_col = _col('Project GPS Coordinates')
        country_col = _col('Country')
        city_col = _col('City or Location')
        name_col = _col('Project Name')
        scope_col = _col('Project Scope / Supplementary information')
        filled_precise = 0
        filled_city = 0
        for row in xls_rows + sql_rows:
            gps_val = row[gps_col]
            if not gps_val or not str(gps_val).strip() or str(gps_val).strip() == '0':
                old_gps = None
                coords = geocode_lookup_tiered(
                    city_cache, precise_cache,
                    row[city_col], row[country_col],
                    row[name_col], row[scope_col])
                if coords:
                    row[gps_col] = coords
                    filled_city += 1
            else:
                # Already has GPS (from EDP or XLS), but try to upgrade precision
                coords = geocode_lookup_tiered(
                    {}, precise_cache,
                    row[city_col], row[country_col],
                    row[name_col], row[scope_col])
                if coords and coords != row[gps_col]:
                    row[gps_col] = coords
                    filled_precise += 1
        print(f"\nGPS enrichment: filled {filled_city} missing, upgraded {filled_precise} to building-level precision")
        print(f"  ({len(city_cache)} city-level + {len(precise_cache)} precise cached locations)")

    # Step 4b: Extract sustainability certifications from scope
    sust_col = _col('Sustainability Rating')
    scope_col = _col('Project Scope / Supplementary information')
    sust_re = re.compile(r'(LEED|IGBC|BREEAM|Green\s*Star|WELL\s+(?:Certified|Gold|Platinum|Silver)|NABERS)', re.IGNORECASE)
    sust_filled = 0
    for row in xls_rows + sql_rows:
        sust_val = row[sust_col]
        if sust_val and str(sust_val).strip():
            continue
        scope_text = str(row[scope_col] or '').strip()
        if scope_text:
            matches = sust_re.findall(scope_text)
            if matches:
                row[sust_col] = ', '.join(sorted(set(m.strip() for m in matches)))
                sust_filled += 1
    if sust_filled:
        print(f"Sustainability enrichment: filled {sust_filled} from scope text")

    # Step 5: Create unified Excel
    create_unified_excel(xls_rows, sql_rows, OUTPUT)


if __name__ == '__main__':
    main()
