-- Budget Closed by category + state (derived from city only) + country derived when missing.
-- State: ONLY from city lookup (US state code). Do not use project.state - that is phase/status (Active, Cancelled, etc.).
-- Country: when missing, derived from city lookup or from state (US state codes -> United States).
-- Uncategorized tasks excluded. Same category logic as budget_core_query_closed_by_category.sql.

-- City -> (state, country) lookup. Normalized city = LOWER(TRIM(city)).
-- US cities (state + country United States); add more rows as needed.
WITH city_lookup AS (
    SELECT 'new york' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los angeles', 'CA', 'United States' UNION ALL SELECT 'chicago', 'IL', 'United States' UNION ALL
    SELECT 'houston', 'TX', 'United States' UNION ALL SELECT 'phoenix', 'AZ', 'United States' UNION ALL
    SELECT 'philadelphia', 'PA', 'United States' UNION ALL SELECT 'san antonio', 'TX', 'United States' UNION ALL
    SELECT 'san diego', 'CA', 'United States' UNION ALL SELECT 'dallas', 'TX', 'United States' UNION ALL
    SELECT 'san jose', 'CA', 'United States' UNION ALL SELECT 'austin', 'TX', 'United States' UNION ALL
    SELECT 'jacksonville', 'FL', 'United States' UNION ALL SELECT 'fort worth', 'TX', 'United States' UNION ALL
    SELECT 'columbus', 'OH', 'United States' UNION ALL SELECT 'charlotte', 'NC', 'United States' UNION ALL
    SELECT 'san francisco', 'CA', 'United States' UNION ALL SELECT 'indianapolis', 'IN', 'United States' UNION ALL
    SELECT 'seattle', 'WA', 'United States' UNION ALL SELECT 'denver', 'CO', 'United States' UNION ALL
    SELECT 'boston', 'MA', 'United States' UNION ALL SELECT 'nashville', 'TN', 'United States' UNION ALL
    SELECT 'detroit', 'MI', 'United States' UNION ALL SELECT 'portland', 'OR', 'United States' UNION ALL
    SELECT 'las vegas', 'NV', 'United States' UNION ALL SELECT 'memphis', 'TN', 'United States' UNION ALL
    SELECT 'louisville', 'KY', 'United States' UNION ALL SELECT 'baltimore', 'MD', 'United States' UNION ALL
    SELECT 'milwaukee', 'WI', 'United States' UNION ALL SELECT 'albuquerque', 'NM', 'United States' UNION ALL
    SELECT 'tucson', 'AZ', 'United States' UNION ALL SELECT 'fresno', 'CA', 'United States' UNION ALL
    SELECT 'mesa', 'AZ', 'United States' UNION ALL SELECT 'sacramento', 'CA', 'United States' UNION ALL
    SELECT 'atlanta', 'GA', 'United States' UNION ALL SELECT 'kansas city', 'MO', 'United States' UNION ALL
    SELECT 'colorado springs', 'CO', 'United States' UNION ALL SELECT 'raleigh', 'NC', 'United States' UNION ALL
    SELECT 'miami', 'FL', 'United States' UNION ALL SELECT 'long beach', 'CA', 'United States' UNION ALL
    SELECT 'virginia beach', 'VA', 'United States' UNION ALL SELECT 'omaha', 'NE', 'United States' UNION ALL
    SELECT 'oakland', 'CA', 'United States' UNION ALL SELECT 'minneapolis', 'MN', 'United States' UNION ALL
    SELECT 'tulsa', 'OK', 'United States' UNION ALL SELECT 'tampa', 'FL', 'United States' UNION ALL
    SELECT 'arlington', 'TX', 'United States' UNION ALL SELECT 'new orleans', 'LA', 'United States' UNION ALL
    SELECT 'wichita', 'KS', 'United States' UNION ALL SELECT 'cleveland', 'OH', 'United States' UNION ALL
    SELECT 'bakersfield', 'CA', 'United States' UNION ALL SELECT 'aurora', 'CO', 'United States' UNION ALL
    SELECT 'honolulu', 'HI', 'United States' UNION ALL SELECT 'anaheim', 'CA', 'United States' UNION ALL
    SELECT 'salt lake city', 'UT', 'United States' UNION ALL SELECT 'arlington', 'VA', 'United States' UNION ALL
    SELECT 'st. louis', 'MO', 'United States' UNION ALL SELECT 'st louis', 'MO', 'United States' UNION ALL
    SELECT 'pittsburgh', 'PA', 'United States' UNION ALL SELECT 'cincinnati', 'OH', 'United States' UNION ALL
    SELECT 'lexington', 'KY', 'United States' UNION ALL SELECT 'anchorage', 'AK', 'United States' UNION ALL
    SELECT 'stockton', 'CA', 'United States' UNION ALL SELECT 'henderson', 'NV', 'United States' UNION ALL
    SELECT 'newark', 'NJ', 'United States' UNION ALL SELECT 'orlando', 'FL', 'United States' UNION ALL
    SELECT 'london', NULL, 'United Kingdom' UNION ALL SELECT 'toronto', NULL, 'Canada' UNION ALL
    SELECT 'vancouver', NULL, 'Canada' UNION ALL SELECT 'montreal', NULL, 'Canada' UNION ALL
    SELECT 'mexico city', NULL, 'Mexico' UNION ALL SELECT 'sydney', NULL, 'Australia' UNION ALL
    SELECT 'singapore', NULL, 'Singapore' UNION ALL SELECT 'dublin', NULL, 'Ireland'
),
-- US state/territory codes -> United States (for deriving country when state present but country missing)
us_states AS (
    SELECT 'AL' AS state_code UNION ALL SELECT 'AK' UNION ALL SELECT 'AZ' UNION ALL SELECT 'AR' UNION ALL SELECT 'CA' UNION ALL
    SELECT 'CO' UNION ALL SELECT 'CT' UNION ALL SELECT 'DE' UNION ALL SELECT 'FL' UNION ALL SELECT 'GA' UNION ALL
    SELECT 'HI' UNION ALL SELECT 'ID' UNION ALL SELECT 'IL' UNION ALL SELECT 'IN' UNION ALL SELECT 'IA' UNION ALL
    SELECT 'KS' UNION ALL SELECT 'KY' UNION ALL SELECT 'LA' UNION ALL SELECT 'ME' UNION ALL SELECT 'MD' UNION ALL
    SELECT 'MA' UNION ALL SELECT 'MI' UNION ALL SELECT 'MN' UNION ALL SELECT 'MS' UNION ALL SELECT 'MO' UNION ALL
    SELECT 'MT' UNION ALL SELECT 'NE' UNION ALL SELECT 'NV' UNION ALL SELECT 'NH' UNION ALL SELECT 'NJ' UNION ALL
    SELECT 'NM' UNION ALL SELECT 'NY' UNION ALL SELECT 'NC' UNION ALL SELECT 'ND' UNION ALL SELECT 'OH' UNION ALL
    SELECT 'OK' UNION ALL SELECT 'OR' UNION ALL SELECT 'PA' UNION ALL SELECT 'RI' UNION ALL SELECT 'SC' UNION ALL
    SELECT 'SD' UNION ALL SELECT 'TN' UNION ALL SELECT 'TX' UNION ALL SELECT 'UT' UNION ALL SELECT 'VT' UNION ALL
    SELECT 'VA' UNION ALL SELECT 'WA' UNION ALL SELECT 'WV' UNION ALL SELECT 'WI' UNION ALL SELECT 'WY' UNION ALL
    SELECT 'DC'
),
base AS (
    SELECT
        gt.taskname,
        gt.originalbudgetamount,
        gt.totalprojectedbudgetamount,
        p.id AS project_id,
        TRIM(p.city) AS city,
        TRIM(p.country) AS country_raw,
        TRIM(p.state) AS state_raw,
        TRIM(p.worklocationstateprov) AS worklocationstateprov,
        TRIM(p.worklocationcountry) AS worklocationcountry,
        TRIM(p.projectcountry) AS projectcountry,
        p.sector,
        COALESCE(NULLIF(p.grossarea, 0), p.usablearea) AS area,
        LOWER(TRIM(p.city)) AS city_norm
    FROM work_dynamics.curated.generictask gt
    INNER JOIN work_dynamics.curated.project p
        ON gt.projectidentifier = p.workitemidentifier
    WHERE p.currencytype = 'USD'
      AND p.phasetext = 'Closed'
      AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
      AND gt.originalbudgetamount IS NOT NULL
      AND gt.originalbudgetamount <> 0
),
base_with_location AS (
    SELECT
        b.*,
        -- State: ONLY from city lookup (geographic). Do not use project.state (that is phase/status: Active, Cancelled, etc.)
        cl.state_derived AS state,
        -- Country: use raw when present; when missing, from city lookup or from state (US state -> United States)
        COALESCE(
            NULLIF(b.country_raw, ''),
            b.worklocationcountry,
            b.projectcountry,
            cl.country_derived,
            CASE WHEN us.state_code IS NOT NULL THEN 'United States' ELSE NULL END
        ) AS country
    FROM base b
    LEFT JOIN city_lookup cl ON cl.city_norm = b.city_norm
    LEFT JOIN us_states us ON us.state_code = UPPER(TRIM(cl.state_derived))
),
with_category AS (
    SELECT
        taskname,
        originalbudgetamount,
        totalprojectedbudgetamount,
        project_id,
        city,
        state,
        country,
        sector,
        area,
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
    FROM base_with_location
)
SELECT
    w.category AS taskname,
    w.city,
    w.state,
    w.country,
    w.sector,
    SUM(w.area) AS area,
    SUM(w.originalbudgetamount) AS total_original_budget,
    SUM(w.totalprojectedbudgetamount) AS total_projected_budget,
    COUNT(DISTINCT w.project_id) AS project_count
FROM with_category w
WHERE w.category IS NOT NULL
GROUP BY w.category, w.city, w.state, w.country, w.sector
ORDER BY w.category, w.city, w.state, w.country, w.sector;
