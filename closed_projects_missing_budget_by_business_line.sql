-- Closed USD projects missing budgets in generictask (gt), by business line.
--
-- "Missing budget" = no gt row with a positive budget. Specifically:
--   - Project has NO matching generictask rows (budget or Cost Code Item), OR
--   - All matching gt rows have originalbudgetamount IS NULL or = 0.
-- So we require at least one gt row with internaltasktypetext IN ('budget','Cost Code Item')
-- and originalbudgetamount > 0 for the project to count as "has budget".
--
-- Business line from project.jllbusinessline (same as used in sector analysis).
-- Results grouped by business line to compare which lines skip budget creation more.

WITH closed_usd AS (
  SELECT
    p.id,
    p.workitemidentifier,
    COALESCE(NULLIF(TRIM(p.jllbusinessline), ''), '(No business line)') AS business_line
  FROM work_dynamics.curated.project p
  WHERE p.currencytype = 'USD'
    AND p.phasetext = 'Closed'
),
projects_with_budget AS (
  SELECT DISTINCT p.id AS project_id
  FROM work_dynamics.curated.generictask gt
  INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
  WHERE p.currencytype = 'USD'
    AND p.phasetext = 'Closed'
    AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
    AND gt.originalbudgetamount IS NOT NULL
    AND gt.originalbudgetamount <> 0
)
SELECT
  c.business_line,
  COUNT(DISTINCT c.id) AS closed_projects_missing_budget
FROM closed_usd c
LEFT JOIN projects_with_budget w ON w.project_id = c.id
WHERE w.project_id IS NULL
GROUP BY c.business_line

UNION ALL

SELECT
  '(Total)' AS business_line,
  COUNT(DISTINCT c.id) AS closed_projects_missing_budget
FROM closed_usd c
LEFT JOIN projects_with_budget w ON w.project_id = c.id
WHERE w.project_id IS NULL

ORDER BY CASE WHEN business_line = '(Total)' THEN 1 ELSE 0 END, closed_projects_missing_budget DESC;

-- Summary: total closed USD projects and how many are missing budget (for % calculation).
-- Run separately if you only need the summary:
/*
WITH closed_usd AS (
  SELECT p.id
  FROM work_dynamics.curated.project p
  WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
),
projects_with_budget AS (
  SELECT DISTINCT p.id AS project_id
  FROM work_dynamics.curated.generictask gt
  INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
  WHERE p.currencytype = 'USD'
    AND p.phasetext = 'Closed'
    AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
    AND gt.originalbudgetamount IS NOT NULL
    AND gt.originalbudgetamount <> 0
)
SELECT
  (SELECT COUNT(*) FROM closed_usd) AS total_closed_usd_projects,
  (SELECT COUNT(*) FROM closed_usd c LEFT JOIN projects_with_budget w ON w.project_id = c.id WHERE w.project_id IS NULL) AS closed_projects_missing_budget;
*/
