-- Budget Closed query grouped by 3 categories; EXCLUDES projects with missing/zero area.
-- NEW: For Clarizen projects with null/blank p.sector, derive sector from property table:
--      join project to work_dynamics.curated.property on p.propertyidentifier = pr.id
--      and use pr.generalcontext.propertyuse.usageTypeSourceValue as sector.
-- Output: taskname = category, city, country, sector (project or property-derived), area,
--         total_original_budget, total_projected_budget, project_count.
-- State is applied externally via mapping (see run script).

WITH base AS (
    SELECT
        gt.taskname,
        gt.originalbudgetamount,
        gt.totalprojectedbudgetamount,
        p.id AS project_id,
        p.city,
        p.country,
        COALESCE(
            NULLIF(TRIM(p.sector), ''),
            CASE
                WHEN p.sourcesystem = 'clarizen' AND (p.sector IS NULL OR TRIM(p.sector) = '')
                THEN TRIM(element_at(pr.generalcontext.propertyuse.usageTypeSourceValue, 1))
                ELSE NULL
            END
        ) AS sector,
        COALESCE(NULLIF(p.grossarea, 0), p.usablearea) AS area
    FROM work_dynamics.curated.generictask gt
    INNER JOIN work_dynamics.curated.project p
        ON gt.projectidentifier = p.workitemidentifier
    LEFT JOIN work_dynamics.curated.property pr
        ON pr.id = p.propertyidentifier
    WHERE p.currencytype = 'USD'
      AND p.phasetext = 'Closed'
      AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
      AND gt.originalbudgetamount IS NOT NULL
      AND gt.originalbudgetamount <> 0
      AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL
      AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0
),
with_category AS (
    SELECT
        *,
        CASE
            WHEN LOWER(TRIM(taskname)) RLIKE '^(11|12)[\\s\\-]' THEN 'FF&E + Millwork'
            WHEN LOWER(TRIM(taskname)) RLIKE '^[0-9]{2}[\\s\\-]' THEN 'Construction'
            WHEN LOWER(TRIM(taskname)) RLIKE '^\\s*\\-[\\s]*[0-9]{2}\\s' THEN 'Construction'
            WHEN LOWER(TRIM(taskname)) RLIKE 'div[\\s]*[0-9]+' THEN 'Construction'
            WHEN LOWER(TRIM(taskname)) LIKE '%soft%' AND (LOWER(taskname) LIKE '%contingency%' OR LOWER(taskname) LIKE '%cost%') THEN 'Soft Costs'
            WHEN LOWER(TRIM(taskname)) LIKE '%design%' AND (LOWER(taskname) LIKE '%contingency%' OR LOWER(taskname) LIKE '%allowance%') THEN 'Soft Costs'
            WHEN LOWER(taskname) LIKE '%contingency%' AND (LOWER(taskname) LIKE '%ff&e%' OR LOWER(taskname) LIKE '%furniture%') THEN 'FF&E + Millwork'
            WHEN LOWER(taskname) LIKE '%contingency%' OR LOWER(taskname) LIKE '%allowance%' THEN 'Construction'
            WHEN LOWER(taskname) LIKE '%furniture%' OR LOWER(taskname) LIKE '%millwork%' OR LOWER(taskname) LIKE '%ff&e%' OR LOWER(taskname) LIKE '%ffe%'
                 OR LOWER(taskname) LIKE '%artwork%' OR LOWER(taskname) LIKE '% signage%' OR LOWER(taskname) LIKE '%branding%'
                 OR LOWER(taskname) LIKE '%audio visual%' OR LOWER(taskname) LIKE '%a/v%' OR LOWER(taskname) LIKE '% it %' OR LOWER(taskname) LIKE '% it'
                 OR LOWER(taskname) LIKE '%equipment%' OR LOWER(taskname) LIKE '%appliances%' OR LOWER(taskname) LIKE '%blinds%'
                 OR LOWER(taskname) LIKE '%workstations%' OR LOWER(taskname) LIKE '%seating%' OR LOWER(taskname) LIKE '%carpet%'
                 OR LOWER(taskname) LIKE '%(it)%' OR LOWER(taskname) LIKE '%information technology%'
            THEN 'FF&E + Millwork'
            WHEN LOWER(taskname) LIKE '%architect%' OR LOWER(taskname) LIKE '%designer%' OR LOWER(taskname) LIKE '%engineer%'
                 OR LOWER(taskname) LIKE '%consultant%' OR LOWER(taskname) LIKE '%expeditor%' OR LOWER(taskname) LIKE '%permit%'
                 OR LOWER(taskname) LIKE '% pm fee%' OR LOWER(taskname) LIKE '%jll %' OR LOWER(taskname) LIKE '%project management%'
                 OR LOWER(taskname) LIKE '%inspection%' OR LOWER(taskname) LIKE '%survey%' OR LOWER(taskname) LIKE '%legal%'
                 OR LOWER(taskname) LIKE '%insurance%' OR LOWER(taskname) LIKE '%leed%' OR LOWER(taskname) LIKE '%sustainability%'
                 OR LOWER(taskname) LIKE '%design fee%' OR LOWER(taskname) LIKE '%reimbursable%' OR LOWER(taskname) LIKE '%admin fee%'
                 OR LOWER(taskname) LIKE '%management fee%' OR LOWER(taskname) LIKE '%soft cost%'
            THEN 'Soft Costs'
            WHEN LOWER(taskname) LIKE '%general contractor%' OR LOWER(taskname) LIKE '% gc %' OR LOWER(taskname) LIKE 'gc %' OR LOWER(taskname) LIKE '% gmp %'
                 OR LOWER(taskname) LIKE '%construction %' OR LOWER(taskname) LIKE '%concrete%' OR LOWER(taskname) LIKE '%structural%'
                 OR LOWER(taskname) LIKE '%electrical%' OR LOWER(taskname) LIKE '%plumbing%' OR LOWER(taskname) LIKE '%hvac%'
                 OR LOWER(taskname) LIKE '%demolition%' OR LOWER(taskname) LIKE '%sitework%' OR LOWER(taskname) LIKE '%earthwork%'
                 OR LOWER(taskname) LIKE '%general conditions%' OR LOWER(taskname) LIKE '%drywall%' OR LOWER(taskname) LIKE '%framing%'
                 OR LOWER(taskname) LIKE '%flooring%' OR LOWER(taskname) LIKE '%ceilings%' OR LOWER(taskname) LIKE '%painting%'
                 OR LOWER(taskname) LIKE '%fire protection%' OR LOWER(taskname) LIKE '%fire sprinkler%' OR LOWER(taskname) LIKE '%roofing%'
                 OR LOWER(taskname) LIKE '%facade%' OR LOWER(taskname) LIKE '%cladding%' OR LOWER(taskname) LIKE '%hard cost%'
                 OR LOWER(TRIM(taskname)) LIKE '$%'
                 OR LOWER(TRIM(taskname)) RLIKE '^[0-9]+\\.' OR LOWER(TRIM(taskname)) RLIKE '^[0-9]+\\s+[a-z]'
            THEN 'Construction'
            ELSE NULL
        END AS category
    FROM base
)
SELECT
    w.category AS taskname,
    w.city,
    w.country,
    w.sector,
    SUM(w.area) AS area,
    SUM(w.originalbudgetamount) AS total_original_budget,
    SUM(w.totalprojectedbudgetamount) AS total_projected_budget,
    COUNT(DISTINCT w.project_id) AS project_count
FROM with_category w
WHERE w.category IS NOT NULL
GROUP BY w.category, w.city, w.country, w.sector
ORDER BY w.category, w.city, w.country, w.sector;
