-- Core budget query (Closed phase): cost code / task × city, country, sector
-- Source: Work Dynamics curated (generictask + project)
-- Filters: USD, Closed phase; budget rows (see note on task types), non-zero original budget
-- Use: Aggregate area, original budget, projected budget, and project count by cost/task and location/sector
--
-- Note: For Closed, most budget data is in generictask as 'Cost Code Item', not 'budget'.
-- Including both so coverage matches ~55K Closed USD projects (vs 115 with 'budget' only).

SELECT
    gt.costcode,
    gt.taskname,
    p.city,
    p.country,
    p.sector,
    SUM(COALESCE(NULLIF(p.grossarea, 0), p.usablearea)) AS area,
    SUM(gt.originalbudgetamount) AS total_original_budget,
    SUM(gt.totalprojectedbudgetamount) AS total_projected_budget,
    COUNT(p.id) AS project_count
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
WHERE p.currencytype = 'USD'
  AND p.phasetext = 'Closed'
  AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
  AND gt.originalbudgetamount IS NOT NULL
  AND gt.originalbudgetamount <> 0
  -- AND p.sourceprojectid = 'JLL2P25000031'  -- optional: single project
GROUP BY gt.costcode, gt.taskname, p.city, p.country, p.sector;
