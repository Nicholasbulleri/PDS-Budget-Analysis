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
Search all OVal tables for a specific client (Warner Bros) and summarize their data.
"""
import sys, os

from edp_connection import execute_query

CATALOG = "work_dynamics"
SCHEMA = "curated"
FQN = lambda t: f"{CATALOG}.{SCHEMA}.{t}"

SEARCH = "Warner"

def run(label, query):
    print(f"\n{'─' * 80}")
    print(f"  {label}")
    print(f"{'─' * 80}")
    cols, rows = execute_query(query)
    print(f"  → {len(rows)} rows returned")
    if not rows:
        return cols, rows
    # print column headers
    widths = [max(len(str(c)), max(len(str(r[i])) for r in rows[:50])) for i, c in enumerate(cols)]
    widths = [min(w, 50) for w in widths]
    header = " | ".join(f"{c:{w}s}" for c, w in zip(cols, widths))
    print(f"  {header}")
    print(f"  {'-' * len(header)}")
    for row in rows[:50]:
        vals = " | ".join(f"{str(v)[:50]:{w}s}" for v, w in zip(row, widths))
        print(f"  {vals}")
    if len(rows) > 50:
        print(f"  ... ({len(rows) - 50} more rows)")
    return cols, rows

# 1. Parent Companies
run("PARENT COMPANIES matching Warner Bros", f"""
SELECT ParentCompanyId, ParentCompanyName, MDMCompanyCode, IndustryType,
       IndustryTypeMastered, IsActive, DefaultL5Code
FROM {FQN('oval_vwparentcompanies')}
WHERE UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
ORDER BY ParentCompanyName
""")

# 2. Companies (child entities)
run("COMPANIES (child entities) matching Warner Bros", f"""
SELECT CompanyId, CompanyName, ParentCompanyId, CRMCompanyId, ClientId,
       IndustryType, Country, City, IsClient, IsActive
FROM {FQN('oval_vwcompanies')}
WHERE UPPER(CompanyName) LIKE '%{SEARCH.upper()}%'
   OR ParentCompanyId IN (
       SELECT ParentCompanyId FROM {FQN('oval_vwparentcompanies')}
       WHERE UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
   )
ORDER BY CompanyName
""")

# 3. Requests
run("REQUESTS (projects/bids) for Warner Bros", f"""
SELECT RequestId, RequestNo, RequestType, Status, StageStatus, Stage,
       Hub, Country, PL, LocalClientEntityName, ParentCompanyName,
       ProjectName, AssetType, ServiceType, SubServiceType, ProjectType,
       JobSiteLocation, Currency,
       ReportedRevenueUSD, FeeRevenueUSD, PbAGMTargetUSD,
       ProjectStartDate, ProjectCompletionDate, ClosedOn,
       WinProbability, LostReason
FROM {FQN('oval_vwrequests')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
   OR CompanyId IN (
       SELECT CompanyId FROM {FQN('oval_vwcompanies')}
       WHERE UPPER(CompanyName) LIKE '%{SEARCH.upper()}%'
          OR ParentCompanyId IN (
              SELECT ParentCompanyId FROM {FQN('oval_vwparentcompanies')}
              WHERE UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
          )
   )
ORDER BY RequestNo
""")

# 4. ClientPlus
run("CLIENTPLUS (flattened view) for Warner Bros", f"""
SELECT OValID, ProjectName, LocalClientEntityName, ParentCompanyName,
       Country, Status, ServiceType, SubServiceType, ProjectType,
       AssetType, IndustryType, Currency,
       EstGAAPRevenue, EstFeeRevenue, ActualGAAPRevenue, ActualFeeRevenue,
       ProjectStartDate, ProjectCompletionDate, ClosedOn,
       WinProbability, LostReason, JobSiteLocation
FROM {FQN('oval_clientplus')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
ORDER BY OValID
""")

# 5. Variations
run("VARIATIONS (change orders) for Warner Bros requests", f"""
SELECT v.VariationId, v.VariationNo, v.RequestId, v.RequestType,
       v.Status, v.StageStatus, v.LocalClientEntityName, v.ParentCompanyName,
       v.ProjectName, v.Country, v.Hub,
       v.ServiceType, v.SubServiceType, v.ProjectType,
       v.ReportedRevenueUSD, v.FeeRevenueUSD, v.PbAGMTargetUSD,
       v.Currency, v.ClosedOn
FROM {FQN('oval_vwvariations')} v
WHERE UPPER(v.LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(v.ParentCompanyName) LIKE '%{SEARCH.upper()}%'
   OR v.RequestId IN (
       SELECT RequestId FROM {FQN('oval_vwrequests')}
       WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
          OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
   )
ORDER BY v.VariationNo
""")

# 6. Summary statistics
print(f"\n{'=' * 80}")
print(f"  AGGREGATE SUMMARY — Warner Bros across OVal")
print(f"{'=' * 80}")

run("Requests by Status", f"""
SELECT Status, COUNT(*) AS cnt,
       SUM(CAST(FeeRevenueUSD AS DOUBLE)) AS total_fee_revenue_usd,
       SUM(CAST(ReportedRevenueUSD AS DOUBLE)) AS total_reported_revenue_usd,
       SUM(CAST(PbAGMTargetUSD AS DOUBLE)) AS total_pbagm_usd
FROM {FQN('oval_vwrequests')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
GROUP BY Status ORDER BY cnt DESC
""")

run("Requests by Country / Hub", f"""
SELECT Hub, Country, COUNT(*) AS cnt,
       SUM(CAST(FeeRevenueUSD AS DOUBLE)) AS total_fee_revenue_usd
FROM {FQN('oval_vwrequests')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
GROUP BY Hub, Country ORDER BY cnt DESC
""")

run("Requests by ServiceType / SubServiceType", f"""
SELECT ServiceType, SubServiceType, COUNT(*) AS cnt,
       SUM(CAST(FeeRevenueUSD AS DOUBLE)) AS total_fee_revenue_usd
FROM {FQN('oval_vwrequests')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
GROUP BY ServiceType, SubServiceType ORDER BY cnt DESC
""")

run("Requests by ProjectType / AssetType", f"""
SELECT ProjectType, AssetType, COUNT(*) AS cnt
FROM {FQN('oval_vwrequests')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
GROUP BY ProjectType, AssetType ORDER BY cnt DESC
""")

run("Timeline — earliest and latest activity", f"""
SELECT
  MIN(ProjectStartDate) AS earliest_project_start,
  MAX(ProjectCompletionDate) AS latest_project_completion,
  MIN(Stage1_CreatedOn) AS first_request_created,
  MAX(ModifiedOn) AS last_modified,
  COUNT(DISTINCT RequestId) AS total_requests
FROM {FQN('oval_vwrequests')}
WHERE UPPER(LocalClientEntityName) LIKE '%{SEARCH.upper()}%'
   OR UPPER(ParentCompanyName) LIKE '%{SEARCH.upper()}%'
""")

print("\nDone.")
