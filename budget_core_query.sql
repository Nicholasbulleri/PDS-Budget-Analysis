-- Core budget query: cost code / task × city, country, sector
-- Source: Work Dynamics curated (generictask + project)
-- Filters: USD, Construct phase, budget tasks, non-zero original budget
-- Use: Aggregate area, original budget, projected budget, and project count by cost/task and location/sector

SELECT DISTINCT
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
  AND p.phasetext = 'Construct'
  AND gt.internaltasktypetext = 'budget'
  AND gt.originalbudgetamount <> 0
  -- AND p.sourceprojectid = 'JLL2P25000031'  -- optional: single project
GROUP BY gt.costcode, gt.taskname, p.city, p.country, p.sector;
