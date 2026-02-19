-- Budget Closed by category + state (derived from city only) + country derived when missing.
-- State: ONLY from city lookup (US state code). Do not use project.state - that is phase/status (Active, Cancelled, etc.).
-- Country: when missing, derived from city lookup or from state (US state codes -> United States).
-- Uncategorized tasks excluded. Same category logic as budget_core_query_closed_by_category.sql.
--
-- This version uses the full city->state mapping (inline CTE generated from city_to_state_mapping.csv).
-- To refresh: run generate_city_lookup_cte.py after updating the mapping CSV.

-- City -> (state, country) lookup. Normalized city = LOWER(TRIM(city)).
WITH city_lookup AS (
    SELECT 'albuquerque' AS city_norm, 'NM' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arlington' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'austin' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'abbeville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aberdeen' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aberdeen proving ground' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'abilene' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'abingdon' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'acton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'acushnet' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'addison' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'adel' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'adelanto' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'agoura' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'agoura hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aiea' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aiken' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alamo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'albany' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'albion' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alexandria' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alhambra' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aliso viejo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'allen' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'allentown' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'allison park' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alpharetta' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alta loma' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'altadena' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'altamont' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'altamonte springs' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'altoona' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alvin' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'amesbury' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'amherst' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'amherst, ny' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'anacortes' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'anaheim' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'anchorage' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'anderson' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'andover' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ann arbor' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'annandale' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'annapolis' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'annapolis junction' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'apex' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'apollo beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'apopka' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'apple valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'appleton' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aptos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arcadia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ardmore' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arlington heights' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'armonk' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arnold' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arroyo grande' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arvada' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arvin' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ashburn' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'asheboro' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'asheville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ashland' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aspen' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'astoria' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'atlanta' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'attleboro' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'auberry' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'auburn' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'auburndale' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'augusta' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aurora' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'avalon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aventura' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'avon' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'avon park' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'avondale' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'avondale estates' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ayer' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'baltimore' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'baileys xrds' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bainbridge island' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bakersfield' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bal harbour' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'balch springs' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'baldwin' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'baldwin park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ballwin' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'banks' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'banning' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'barrington' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'barstow' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bastrop' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'batavia' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'baton rouge' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bay shore' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bayside' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beaufort' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beaumont' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beaver dam' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beavercreek' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beaverton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beckley' AS city_norm, 'WV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bedford' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bel air' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bell' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bellaire' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belleville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bellevue' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bellflower' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bellmore' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belmont' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beloit' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belton' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beltsville' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bend' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'benicia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bensenville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bentonville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'berkeley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'berlin' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'berryville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'berwyn' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bessemer' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bethesda' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bethlehem' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bettendorf' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beverly' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'beverly hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'billerica' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'billings' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bingham farms' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'birmingham' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bishop' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bismarck' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blacksburg' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blaine' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blairsville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bloomingdale' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bloomington' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blue ash' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blue bell' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blue springs' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bluefield' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bluffton' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'blythe' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boca raton' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bogalusa' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bohemia' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boiling springs' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boise' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bolingbrook' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bonita springs' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boone' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boonton' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bossier city' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boston' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bothell' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boulder' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boulder city' AS city_norm, 'NV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bowie' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bowling green' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boyertown' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'boynton beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bozeman' AS city_norm, 'MT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bradenton' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'braintree' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brandon' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'branford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brawley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brea' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brentwood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brevard' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brick' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bridgehampton' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bridgeville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bridgewater' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brighton' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bristow' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brockton' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bronx' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bronxville' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brookfield' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brookhaven' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brookline' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brooklyn' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brooklyn center' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brooklyn park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'broomfield' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brownsville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brunswick' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bryn mawr' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'buena park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'buffalo' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'buffalo grove' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'buford' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bunkie' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burbank' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burlingame' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burlington' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burney' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burnsville' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burr ridge' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'burtonsville' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'butler' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'canoga park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'colorado springs' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'columbus' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'caldwell' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'caledonia' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'calexico' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'california' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'callahan' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'calumet city' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'camarillo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cambridge' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'camp hill' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'camp springs' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'campbell' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'canby' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'candor' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cape canaveral' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cape coral' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'capistrano beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'capitola' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carle place' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carlsbad' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carlstadt' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carmel' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carol stream' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carolina beach' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carpentersville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carpinteria' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carrabelle' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carrollton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carson' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carson city' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cartersville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cary' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cashiers' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'casper' AS city_norm, 'WY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'castle hayne' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'castle rock' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'castro valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cathedral city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cedar grove' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cedar hill' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cedar park' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cedar rapids' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cedarburg' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cedarhurst' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'celebration' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'centennial' AS city_norm, 'WY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'center harbor or moultenboro' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'centerville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ceres' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cerritos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chalmette' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chambersburg' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chamblee' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'champlin' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chandler' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chanhassen' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'channahon' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chantilly' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chapel hill' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chapin' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'charles town' AS city_norm, 'WV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'charleston' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'charlestown' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'charlotte' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'charlottesville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chatsworth' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chattanooga' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cheektowaga' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chelmsford' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chelsea' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cheraw' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cherry hill' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chesapeake' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chester' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chester, va 23836' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chesterfield' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chestnut hill' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chevy chase' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cheyenne' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chicago' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chicago heights' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chicago ridge' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chicopee' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chilton' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chino' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chippewa falls' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'christiansburg' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chubbuck' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chula vista' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cincinnati' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cinnaminson' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'city of industry' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clackamas' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'claremont' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clark' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clarksburg' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clarksville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clayton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clearfield' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clearwater' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clemson' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clermont' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cleveland' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clifton' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clifton park' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clinton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clintwood' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clovis' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clyde' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coachella' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cockeysville' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cocoa' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cocoa beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coconut creek' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coconut grove' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coeur d alene' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'college park' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'college station' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'collinsville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'columbia' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'commack' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'commerce' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'compton' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'concord' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'connellsville' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'connersville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'conshohocken' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'conyers' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cookeville' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coon rapids' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cooper city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coppell' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coral gables' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coral springs' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coralville' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cordova' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cornelius' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corona' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corona del mar' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'coronado' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corpus christi' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corte madera' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corvallis' AS city_norm, 'MT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corydon' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'costa mesa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cottonwood heights' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'country club hills' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'covina' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'covington' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cranberry' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cranberry township' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crane' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cranston' AS city_norm, 'RI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crawfordville' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cresskill' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crestwood' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crete' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'creve coeur' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cross lanes' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crystal' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crystal lake' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crystal river' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cudahy' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'culpeper' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'culver city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cumberland' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cumming' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cupertino' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'curtis bay' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cut off' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cypress' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dallas' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dacula' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'daggett' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dahlonega' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dalton' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'daly city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dana point' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'danbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'danbury, ct' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dania beach' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'danvers' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'danville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'davenport' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'davidson' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'davis' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dawsonville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dayton' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'daytona beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'de pere' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'decatur' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dededo' AS city_norm, 'GU' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dedham' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'deer park' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'deer valley' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'deerfield beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'del mar' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'delafield' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'deland' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'delray beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'denham springs' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'denver' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'derby' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'derwood' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'des moines' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'des plaines' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'desoto' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'destrehan' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'detroit' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'devens' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dewitt' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'diamond bar' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dobbs ferry' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dobson' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'doral' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dorchester' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'douglasville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dover' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'downers grove' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'downey' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dracut' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'draper' AS city_norm, 'SD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'drexel hill' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dry ridge' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'duarte' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dublin' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ducor' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'duluth' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'duncan' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dundalk' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dunn' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dunnellon' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'durham' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'duvall' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eagan' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eagle' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'earth city' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'easley' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east boston' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east brunswick' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east hartford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east lansing' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east meadow' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east palo alto' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east pittsburgh' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east point' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east syracuse' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'easton' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eastvale' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eau claire' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eden prairie' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edgard' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edgewood' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edina' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edison' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edmond' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edmonds' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'egg harbor township' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'el cajon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'el centro' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'el dorado hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'el paso' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'el segundo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eldersburg' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elgin' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elizabeth' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elizabeth city' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elk grove' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elk grove village' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elk river' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elkridge' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elkton' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ellenton' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ellenwood' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ellicott city' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ellisville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elmhurst' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'emeryville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'emmaus' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'encinitas' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'encino' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'endicott' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'enfield' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'englewood' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'enterprise' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'erie' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'erlanger' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'escondido' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'essex junction' AS city_norm, 'VT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'etters' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eugene' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'euless' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'evans' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'evanston' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'everett' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ewing' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'excelsior' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'excelsior springs' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'exton' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairfax' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairfield' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairhaven' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairhope' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairmont' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairport' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fairview heights' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fall river' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'falls church' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fargo' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'farmers branch' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'farmingdale' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'farmington' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fayetteville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'federal way' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fenton' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fernandina beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fillmore' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fishkill' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fishsersville' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fitchburg' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'flagler beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'flagstaff' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'flint' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'florence' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'florham park' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'florissant' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'flower mound' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'flushing' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'folsom' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fontana' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'foothill ranch' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'forest' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'forest lake' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'forest park' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'forestdale' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'forestville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort bragg' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort collins' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort lauderdale' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort lee' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort mill' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort myers' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort smith' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort walton beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort worth' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'foster city' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fountain hills' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fountain valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'foxborough' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'framingham' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'frankfort' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'franklin' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'franklin lakes' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'franklin park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'franklinville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'frederick' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fredericksburg' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fredericktown' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fremont' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fresh meadows' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fresno' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'friendswood' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'frisco' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'frontenac' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fruitland park' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ft lauderdale' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ft worth' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fullerton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fulton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fuquay varina' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gainesville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gaithersburg' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gallatin' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'galt' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'galveston' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gambrills' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'garden city' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'garden city park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'garden grove' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gardena' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'garland' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'garner' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gastonia' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'geneva' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'georgetown' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'germantown' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gilbert' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gilroy' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glastonbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glen allen' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glen burnie' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glen cove' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glen mills' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glen oaks' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glendale' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glendora' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glenview' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gold river' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'golden' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'golden valley' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'goldenrod' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'goldsboro' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'goleta' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gonzales' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'goodlettsville' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'goodyear' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'granada hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'granby' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grand junction' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grand prairie' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grand rapids' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grand terrace' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grandview' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grapevine' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grass valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grayslake' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'great neck' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greeley' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'green bay' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenbelt' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greencastle' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greendale' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenfield' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenlawn' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greensboro' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greensburg' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenwich' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenwood' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenwood village' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greer' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gridley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'griffin' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'groveland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'groveport' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grover beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'guerneville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gulf breeze' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gulfport' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'houston' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hacienda heights' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hackensack' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hagerstown' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hailey' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'haines city' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'halethorpe' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'half moon bay' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'halifax' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hallandale' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hallandale beach' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hamilton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hamlet' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hammond' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hampton' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hanahan' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hanford' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hanover' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hanover park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harker heights' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harlingen' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harmans' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harrisburg' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harrison' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hartford' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hartland' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hartsville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harvey' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hato rey' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hattiesburg' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hauppauge' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'haverhill' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hawaiian gardens' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hayward' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hazelwood' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'healdsburg' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hebron' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'helena' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hemet' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hempstead' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'henderson' AS city_norm, 'NV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hendersonville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'henrico' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hermitage' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'herndon' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hershey' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hesperia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hewlett' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hialeah' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hialeah gardens' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hiawatha' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hickory' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hickory hills' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hicksville' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'high point' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'highland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'highland park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'highlands' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'highlands ranch' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hilliard' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hillsboro' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hillsville' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hilo' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hilton head island' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hingham' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hinsdale' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hiram' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hixson' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hoboken' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hodges' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hoffman estates' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holbrook' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holden' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holladay' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hollister' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holly springs' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hollywood' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holmdel' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holt' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'holtsville' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'homestead' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'homewood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'honolulu' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hoover' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hopatcong' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hopkins' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'horsham' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hot springs' AS city_norm, 'MT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'houma' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'howard beach' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'howell' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'humble' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hunker' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hunt valley' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hunt vally' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntersville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntington' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntington beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntington park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntington station' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntley' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'huntsville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hurricane' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hyattsville' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'idaho falls' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'idyllwild' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'immokalee' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'independence' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indian land' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indian trail' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indian wells' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indiana' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indianapolis' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indianland' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'indio' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ingleside' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'inglewood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'inglis' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'inman' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'intercession city' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'inverness' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'inyokern' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'irmo' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'irvine' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'irving' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'irwindale' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'iselin' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'islip' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'issaquah' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'itasca' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jacksonville' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jackson' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jackson heights' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jamaica' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'janesville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jefferson city' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jeffersonville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jennings' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jericho' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jersey city' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'johns creek' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'johns island' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'johnston' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'johnstown' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'joliet' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jonesville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'juncos' AS city_norm, 'PR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'juneau' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jupiter' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kansas city' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'katy' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'keams canyon' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kennebunk' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kenner' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kennesaw' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kennewick' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kenosha' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kensington' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kent' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kernersville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ketchum' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'key largo' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kill devil hills' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'killeen' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'king' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'king of prussia' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kings mountain' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kingstree' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kingwood' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kinston' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kirkland' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kissimmee' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'knoxville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kokomo' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kyle' AS city_norm, 'SD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los angeles' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la canada flintridge' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la crescenta' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la crosse' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la grange' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la habra' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la jolla' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la mesa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la mirada' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la palma' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la puente' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la quinta' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la verne' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laplace' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'labadieville' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ladera ranch' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ladson' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lafayette' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laguna beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laguna hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laguna niguel' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake arrowhead' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake buena vista' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake charles' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake elmo' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake elsinore' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake forest' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake grove' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake havasu city' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake isabella' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake jackson' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake mary' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake oswego' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake park' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake placid' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake providence' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake stevens' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake success' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake wales' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake worth' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake wylie' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake zurich' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakeland' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakeside' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakeville' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakewood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakewood ranch' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakewoood' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lambertville' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lancaster' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'langhorne' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lanham' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lansing' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laredo' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'largo' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'larkspur' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'las cruces' AS city_norm, 'NM' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'las vegas' AS city_norm, 'NV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'latham' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lathrop' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lauderdale lakes' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lauderhill' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laurel' AS city_norm, 'DE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'laurens' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lavonia' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lawndale' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lawrence' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lawrenceville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lawton' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'layton' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'league city' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leawood' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lebanon' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leeds' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lees summit' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leesburg' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lehi' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lehigh acres' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leland' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lemon grove' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lenexa' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lenoir' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leominster' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leonardtown' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'letrobe' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'levittown' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lewisville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lexington' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'liberty' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'liberty twp' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lihue' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lilburn' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lima' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lincoln' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lincoln city' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lincolnshire' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lincolnton' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lincolnwood' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'linden' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lindenhurst' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lino lakes' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'linthicum' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lisle' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'litchfield park' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lithia' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lithonia' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'little falls' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'little river' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'little rock' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'little silver' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'littleton' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'live oak' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'livermore' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'liverpool' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'livingston' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lodi' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'logan' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loganville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loma linda' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lombard' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'london' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lone tree' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'long beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'longboat key' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'longmont' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'longwood' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loris' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lorton' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los alamitos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los altos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los banos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los gatos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loudon' AS city_norm, 'NH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'louisburg' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'louisville' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loveland' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lowell' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lubbock' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lugoff' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'luling' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lumberton' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lutz' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lynbrook' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lynchburg' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lynn' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lynnfield' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lynnwood' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'miami beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mableton' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'machesney park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'madera' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'madison' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'madisonville' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mahwah' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maiden' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maitland' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'malden' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'malvern' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mammoth lakes' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manalapan' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manassas' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manchester' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mandeville' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manhattan beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manning' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manomet' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mansfield' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manteca' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maple grove' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maple valley' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maplewood' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marathon' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'margate' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marianna' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maricopa' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marietta' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marina' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marina del rey' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marion' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marksville' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marlborough' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marlton' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marrero' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marshall' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marshfield' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marshville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'martinez' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'martinsburg' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'martinsville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marysville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mashpee' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mason' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'massapequa park' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'matawan' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'matteson' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'matthews' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mattituck' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mattoon' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maxton' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mayville' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maywood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mc lean' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mcdonough' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mchenry' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mckinney' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mclean' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mebane' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mechanicsburg' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mechanicsville' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'media' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'melbourne' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'melrose' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'melville' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'memphis' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'menands' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'menifee' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'menlo park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'menomonee falls' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'menomonie' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mequon' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mercer island' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'meriden' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'meridian' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'merritt island' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mesa' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mesquite' AS city_norm, 'NM' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'metairie' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'methuen' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'miami' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'miami shores' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'miamisburg' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'middle river' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'middle village' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'middletown' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'midlothian' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'milford' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mill creek' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mill valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'millbrae' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'milpitas' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'milton' AS city_norm, 'DE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'milwaukee' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'milwaukie' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'minden' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'minenapolis' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'minneapolis' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'minnetonka' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'miramar' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mission' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mission viejo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'missoula' AS city_norm, 'MT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mobile' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mocksville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'modesto' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monarch mill' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monroe' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monroeville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monrovia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'montclair' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'montebello' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monterey park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'montgomery' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monticello' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'montrose' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monument' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moon township' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mooresville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moreno valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morgan hill' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morganton' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morgantown' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morris plains' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morristown' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morrisville' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'morton grove' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moscow' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moultonborough' AS city_norm, 'NH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mound' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moundsville' AS city_norm, 'WV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount dora' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount gilead' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount holly' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount juliet' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount pleasant' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount prospect' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mountain home' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mountain view' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mountville' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mt laurel' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mt pleasant' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mt. pleasant' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mukilteo' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mullins' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'multi' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'muncie' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'munster' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'murfreesboro' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'murphy' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'murrells inlet' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'murrieta' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'myerstown' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'myrtle beach' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new york' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nanuet' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'napa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'naperville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'naples' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'napoleonville' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'narragansett' AS city_norm, 'RI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nashua' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nashville' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'neenah' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'neptune beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'neptune city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'netcong' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new bedford' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new berlin' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new bern' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new braunfels' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new britain' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new castle' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new freedom' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new hartford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new hill' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new hyde park' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new iberia' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new lenox' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new london' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new orleans' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new port richey' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new smyrna beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new stanton' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new york city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newark' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newberry' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newbury park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newburyport' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newhall' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newington' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newport' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newport beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newport news' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newton grove' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newtonville' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'niles' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'noblesville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nocona' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norcross' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norfolk' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norman' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north adams' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north bend' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north bethesda' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north charleston' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north grafton' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north haven' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north highlands' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north hollywood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north kansas city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north las vegas' AS city_norm, 'NV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north little rock' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north miami beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north myrtle beach' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north palm beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north plainfield' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north tonawanda' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north wilkesboro' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'northborough' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'northbrook' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'northford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'northlake' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'northridge' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norwalk' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norwell' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norwood' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'novato' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'novi' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nutley' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'o fallon' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oakland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'omaha' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'owings mills' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oak brook' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oak lawn' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oak ridge' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oakboro' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oakhurst' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oakland park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oakton' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ocala' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ocean city' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oceanside' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ocoee' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'odessa' AS city_norm, 'DE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ogden' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ojai' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'okeechobee' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oklahoma city' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'olathe' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oldsmar' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oley' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'olive branch' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'olivette' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'olney' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'olympia' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'onalaska' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'onley' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ontario' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'opa locka' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oradell' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orange' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orange city' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orange park' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orangeburg' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oregon city' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oreland' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orem' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orland park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orlando' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ormond beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oshkosh' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ossining' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oswego' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ottumwa' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'overland park' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oviedo' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'owensboro' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oxford' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oxnard' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oyster bay' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'perris' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pittsburgh' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pacific palisades' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pacifica' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pahrump' AS city_norm, 'NV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palatine' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palisades park' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm beach gardens' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm city' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm desert' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm harbor' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm springs' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palmdale' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palmetto' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palo alto' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palos heights' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palos hills' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'panama city' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paoli' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paradise' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paramount' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paramus' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'park ridge' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'parker' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'parkersburg' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'parrish' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'parsippany' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pasadena' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paso robles' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'patchogue' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paterson' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'peabody' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'peachtree city' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pearland' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pell city' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pembroke' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pembroke pines' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pendleton' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'penn wynne' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pennsauken township' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pensacola' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'peoria' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'perrine' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'perry' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'perth amboy' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'petaluma' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'phenix city' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'philadelphia' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'phoenix' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pico rivera' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'piedmont' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pierre part' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pilot point' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pine brook' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pinecrest' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pinellas park' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'piscataway' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pittsboro' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pittsford' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'placentia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'placerville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plainfield' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plainsboro' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plainview' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plainville' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plano' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plant city' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plantation' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pleasant hill' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pleasant prairie' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pleasanton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plymouth' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pomona' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pompano beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pompton lakes' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ponte vedra beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pooler' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port arthur' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port charlotte' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port chester' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port hueneme' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port orange' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port orchard' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port richey' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port saint joe' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port saint lucie' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'port washington' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'portage' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'porterville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'portland' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'portsmouth' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'post falls' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'potomac' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'poughkeepsie' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'poulsbo' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'poway' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'prairie village' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'prairieville' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'prescott valley' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'price' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'princeton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'prior lake' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'providence' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'provo' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pueblo' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'punta gorda' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'purchase' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'puyallup' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'queen creek' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'queens' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'queens village' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'quincy' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'quinton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'raceland' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'raleigh' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho cordova' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho cucamonga' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho mirage' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho santa margarita' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'randolph' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rapid city' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'raynham' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'raytown' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reading' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'redding' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'redlands' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'redmond' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'redondo beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'redwood city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reedsburg' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rego park' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rehoboth beach' AS city_norm, 'DE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reidsville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reno' AS city_norm, 'NV' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'renton' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reseda' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reston' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rhinelander' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rialto' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rice lake' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'richardson' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'richfield' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'richland' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'richmond' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'richmond heights' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ridgecrest' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ridgeway' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ridgewood' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rim forest' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rio rancho' AS city_norm, 'NM' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'riverdale' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'riverhead' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'riverside' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'riverton' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'riverview' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roanoke' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'robbinsville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rochester' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rock hill' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rockford' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rockingham' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rocklin' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rockville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rockwall' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rocky mount' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rogers' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rohnert park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rolla' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rolling hills estates' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rolling meadows' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'romeoville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'romoland' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ronkonkoma' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rose hill' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roseburg' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roseland' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roselle' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rosemead' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rosemont' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rosenberg' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roseville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roslyn' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roslyn heights' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roswell' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'round rock' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rowland heights' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rowlett' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roxboro' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'roxbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'royal oak' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ruffs dale' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rumson' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rural hall' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ruskin' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rutherford' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rye' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rye brook' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint louis' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'salt lake city' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'secaucus' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sacramento' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint augustine' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint charles' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint cloud' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint helena' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint johns' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint joseph' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint leo' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint paul' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint peters' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint petersburg' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'salem' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'salinas' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'salisbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sammamish' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san angelo' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san antonio' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san bernardino' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san bruno' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san clemente' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san diego' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san dimas' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san fernando' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san francisco' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san gabriel' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san jose' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san juan capistrano' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san leandro' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san luis obispo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san marcos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san marino' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san mateo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san rafael' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san ramon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san ysidro' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sand city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sandwich' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sandy' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sandy springs' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sanford' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sanger' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa ana' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa barbara' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa clara' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa clarita' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa cruz' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa fe' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa fe springs' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa maria' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa monica' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa paula' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa rosa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santee' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sarasota' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saratoga' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saratoga springs' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sausalito' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'savannah' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'scarborough' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'scarsdale' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'schaumburg' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'schenectady' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'schriever' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'schuylkill haven' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'scotch plains' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'scottsdale' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sea ranch lakes' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sea tac' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seabrook' AS city_norm, 'NH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seal beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seaside' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seattle' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sebastian' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sebastopol' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sebring' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sedona' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seffner' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seguin' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seminole' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'senatobia' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seneca' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seven hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sewickley' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seymour' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shafter' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shakopee' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shalimar' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shamokin' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sharonville' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shaver lake' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shawano' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shawnee' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sheboygan' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shelby' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shelton' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sheridan' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sherman oaks' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shirley' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shreveport' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shrewsbury' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sierra madre' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sierra vista' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'signal hill' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'silver spring' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'simi valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'simpsonville' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sioux city' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sioux falls' AS city_norm, 'SD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'skokie' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'slidell' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'smokey point' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'smyrna' AS city_norm, 'DE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'snellville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'snohomish' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'snoqualmie' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'socorro' AS city_norm, 'NM' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'solana beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'soledad' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'solon' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'somerset' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'somerville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south amboy' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south daytona' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south jordan' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south lake tahoe' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south pasadena' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south richmond hill' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south san francisco' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south windsor' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south yarmouth' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'southampton' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'southborough' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'southern pines' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'southlake' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sparks' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spartanburg' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'speonk' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spindale' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spokane' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spokane valley' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spring' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spring hill' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spring lake' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spring valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'springboro' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'springfield' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'springfield township' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'springville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spruce pine' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st helens' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st louis' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st paul' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st petersburg' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. augustine' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. bernard' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. cloud' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. louis' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. paul' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. petersburg' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stafford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stamford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stamford, ct' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stanton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'star' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'staten island' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'statesville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'staunton' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sterling' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stillwater' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stockbridge' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stockton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stone mountain' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stratham' AS city_norm, 'NH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'strathmore' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'streamwood' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stuart' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'studio city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stuyvesant' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'succasunna' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sugar land' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sullivan' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sulphur' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'summerfield' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'summerland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'summerville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'summit' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sumter' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sun city' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sun city center' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sun valley' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sunland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sunnyside' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sunnyvale' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sunrise' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sunset hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'superior' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'supply' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'surprise' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sussex' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sutton' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'suwanee' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'swampscott' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'swansea' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sylmar' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sylvania' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'syracuse' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tbd' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tacoma' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'taft' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tahoe city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'takoma park' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tallahassee' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tallulah' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tamarac' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tampa' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tarpon springs' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tarrytown' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tarzana' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'taunton' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tavernier' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'telluride' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'temecula' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tempe' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'temple' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'temple city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'temple terrace' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tenafly' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tequesta' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'terre haute' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'terrell' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tewksbury' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'texarkana' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'texas city' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'the villages' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'the woodlands' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'thibodaux' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'thomasville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'thornton' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'thousand oaks' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'thousand palms' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tigard' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tijuana' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'timonium' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tipton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'titusville' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tolland' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tolleson' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'toluca lake' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tomball' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'topsfield' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'torrance' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'totowa' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'towson' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tracy' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'trenton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'troutman' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'troy' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'trumbull' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tualatin' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tuckasegee' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tucker' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tucson' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tulare' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tulsa' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'turlock' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tustin' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tyler' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tysons' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'umatilla' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'union' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'union city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'uniondale' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'uniontown' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'upland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'urbandale' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'uxbridge' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'virginia beach' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vacaville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'valdosta' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'valencia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vallejo' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'valley city' AS city_norm, 'ND' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'valley springs' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'van nuys' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vancouver' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'venice' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ventura' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vernon' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vernon hills' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vero beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vestavia hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'victorville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vienna' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'villa park' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vineyard haven' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'visalia' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vista' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'void' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'voorhees township' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wabash' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waco' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wade' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waipahu' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wake forest' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wakefield' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waldorf' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'walker' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'walled lake' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wallingford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'walnut creek' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'walnut park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waltham' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wantagh' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warner robins' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warren' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warrendale' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warwick' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wasco' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'washington' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'washington d.c' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'washington d.c.' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'washington dc' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waterford' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'watertown' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waukegan' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wausau' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wauwatosa' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wayne' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waynesboro' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waynesville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wayzata' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'webster' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'weeki wachee' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wellesley' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wellesley hills' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wellington' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wentzville' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west bend' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west caldwell' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west chester' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west conshohocken' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west covina' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west des moines' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west hartford' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west hempstead' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west hollywood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west islip' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west jordan' AS city_norm, 'UT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west lafayette' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west linn' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west los angeles' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west melbourne' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west new york' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west orange' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west palm beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west roxbury' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west sacramento' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west saint paul' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west valley city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westborough' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westbury' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westchester' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'western springs' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westfield' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westford' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westlake' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westlake village' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westminster' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westmont' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'weston' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westport' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westwego' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westwood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wethersfield' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wheat ridge' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wheatland' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wheaton' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wheeling' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'white bear lake' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'white plains' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'white water' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitefish bay' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitestone' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whiteville' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whiting' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitinsville' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitman' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitmire' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitsett' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whittier' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wichita' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wildomar' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wildwood' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wilkes-barre' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'williamsburg' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'williamston' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'willingboro' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'williston park' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'willowbrook' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wilmette' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wilmington' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wilson' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wilton' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winchester' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winchester (earlstown)' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winder' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'windham' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'windsor mill' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winnetka' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winooski' AS city_norm, 'VT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winston salem' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winston-salem' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winter garden' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winter park' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winter springs' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winterville' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wofford heights' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodbridge' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodcliff lake' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodinville' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodland hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodland park' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodridge' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodruff' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodstock' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'worcester' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'worchester' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'worthington' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wyckoff' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yakima' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yardley' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yoakum' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yorba linda' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'york' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yuba city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yucaipa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yucca valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yukon' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'zebulon' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'zephyrhills' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'aguadilla' AS city_norm, 'PR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alameda' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alamogordo' AS city_norm, 'NM' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'albuquerue' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'algonquin' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'allendale' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alma' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'anaheim hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'antioch' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'arden hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'asbury park' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'auburn hills' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'babcock ranch' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ballston' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'baytown' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bedminster' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bee cave' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belcrest' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belleair bluffs' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bellingham' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belmar' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'belvedere tiburon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bensalem' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'berkeley heights' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bethedsa' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bloomfield' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bonita' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bonney lake' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brandywine' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bremen' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'broadview' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bushnell' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'calabasas' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'camden' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cameron park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cannonsburg' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'canton' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cape elizabeth' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carlisle' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'catonsville' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'champaign' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'champions gate' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chatham' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chesterbrook' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chico' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'chino hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'citrus heights' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clarendon hills' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clarkston' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'clearwater beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cliffside park' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cloquet' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'closter' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cohasset' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'colmar manor' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'colonia' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'commerce twp' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'conifer' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'conroe' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'corinth' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cranberry twp' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crestview' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crosslake' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crowley' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'deerfield' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'defuniak springs' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'delavan' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'denton' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'denville' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'depere' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'derry' AS city_norm, 'NH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'des peres' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'destin' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'detriot' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'doylestown' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dunedin' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dunwoody' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'duxbury' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eagle river' AS city_norm, 'AK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east greenwich' AS city_norm, 'RI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east hampton' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east lyme' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east orange' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east rutherford' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'east windsor' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'edinburg' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'el monte' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'elizabethville' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'englewood cliffs' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ephrata' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'evergreen' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fair lawn' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fair oaks' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fallbrook' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'falmouth' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'festus' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'forest hills' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fox lake' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fox point' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fox river grove' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'freehold' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'freeport' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ft mitchell' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ft wayne' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ft. worth' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'garwood' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glencoe' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glendale heights' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'glenside' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gloucester' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'green valley' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'greenbrae' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gretna' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grosse pointe farms' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gurnee' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hackettstown' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hamden' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hammonton' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hasbrouck heights' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'havertown' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hazlet' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'heath' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hercules' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'homosassa' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hudson' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'industry' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'inwood' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'iron river' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'irwin' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jurupa valley' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'joelton' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jonestown' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kahului' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kailua-kona' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kapolei' AS city_norm, 'HI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'katonah' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kerman' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'key biscayne' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'la place' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lacey' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake saint louis' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakeway' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'land o'' lakes' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'landing' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'liberty lake' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'libertyville' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lockport' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'londonderry' AS city_norm, 'NH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'long island city' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'longmeadow' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'longview' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lookout mountain' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lutherville timonium' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lyndhurst' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lynwood' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'macomb twp' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'macon' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'malibu' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'manhasset' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marblehead' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'maryland heights' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'massapequa' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'massillon' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mcallen' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'medfield' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mendham' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'merced' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'merrill' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'midland' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'midvale' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'minong' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monterey' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moorestown' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moorpark' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount laurel' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mount vernon' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mt. laurel' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'murray' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mystic' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nazareth' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'needham' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new albany' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new holland' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newnan' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newton center' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'niceville' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norco' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north arlington' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north haledon' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north huntingdon' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north kingstown' AS city_norm, 'RI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north oaks' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nottingham' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oakbrook terrace' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ocean' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'okahumpka' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'okemos' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'old bridge' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'old greenwich' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orinda' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oro valley' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oroville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm bay' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palm coast' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palos verdes estate' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'panama city beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'panorama city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'park city' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pelham' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pharr' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pittsburg' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'plymouth meeting' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'portola valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pottsville' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'prescott' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'prosper' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'quakertown' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'quarryville' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rtp' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'racine' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'radnor' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ramona' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho bernardo' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho santa fe' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'randallstown' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'red bank' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rincon' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ringwood' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ripon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rockaway' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rocky hill' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'round lake heights' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saco' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san carlos' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san juan' AS city_norm, 'PR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'san pedro' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'santa rosa beach' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'savage' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'schererville' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'schnecksville' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'scituate' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'selma' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'severna park' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sharon' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sheboygan falls' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shoreline' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'siler city' AS city_norm, 'NC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'silverdale' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'simsbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sisters' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'somers' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sonoma' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south easton' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south jacksonville' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south milwaukee' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south ogden' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'southfield' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spooner' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'spring grove' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st louis park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st pete beach' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. armands or longboat key?' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. charles' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stanwood' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'state college' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stevens point' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stevensville' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stirling' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stratford' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'street' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sudbury' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'suffield' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'suffolk' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sun city west' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'surfside beach' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'thomson' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'toms river' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'topanga' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'towaco' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'troy hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'truckee' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tukwila' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'universal city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'upper marlboro' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vail' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'various' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'village of oak creek' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waconia' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wallington' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wappingers falls' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warner robbins' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warrenville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warrington' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'washington crossing' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'washington, dc' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'watsonville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waxahachie' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'weaverville' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west allis' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'west grove' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westerville' AS city_norm, 'NE' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wharton' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitehall' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wilsonville' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winter haven' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wixom' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'woodland' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wyomissing' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'yorktown heights' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'acworth' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'alburquerque' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'amarillo' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'american canyon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'anthem' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'antigo' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'apache junction' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'atascadero' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'atco' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'athens' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'attica' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'austell' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'azusa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'battle ground' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bayonet point' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bell gardens' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'benton' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'biloxi' AS city_norm, 'MS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bremerton' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'bristol' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'brooksville' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'buckeye' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cabazon' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'calimesa' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cambria' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cape girardeau' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'carnation' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'casa grande' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'casco' AS city_norm, 'ME' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'castaic' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'cayce' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'century city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'colfax' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'colonie' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'colton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'crestview hills' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'davie' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'desert hot springs' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'dyess afb' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'estero' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'eustis' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'evergreen park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'exeter' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'felton' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'finksburg' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fort stockton' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'fowler' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'ft. lauderdale' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gig harbor' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'grafton' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'gustine' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hales corners' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'happy valley' AS city_norm, 'OR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'harbor city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hawthorne' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hazlewood' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hermosa beach' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hickory creek' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hillsdale' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hillside' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'homer glen' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hortonville' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'hurst' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jessup' AS city_norm, 'MD' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'jonesboro' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'kenmore' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'key west' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'king george' AS city_norm, 'VA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lake in the hills' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lakeside park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'landover' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'las vgas' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'leitchfield' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'lindsay' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'linwood' AS city_norm, 'KS' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'livonia' AS city_norm, 'LA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loogootee' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'loomis' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'los osos' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'madison heights' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marana' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'marcus hook' AS city_norm, 'PA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'medley' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'miami springs' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mira loma' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mission hills' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'missouri city' AS city_norm, 'MO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'monroe township' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moonachie' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'moraga' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mosinee' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mountain lakes' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'multiple projects' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'mundelein' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'muscatine' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'n salt lake city' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nw' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nampa' AS city_norm, 'ID' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'navarre' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'nevada city' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new buffalo' AS city_norm, 'MI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new caney' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'new holstein' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'newtown' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'niagara falls' AS city_norm, 'NY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'norridge' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north carolina' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north fort myers' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north miami' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'north richland hills' AS city_norm, 'TX' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oak harbor' AS city_norm, 'OH' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oak park heights' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'oconto falls' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'old lyme' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orangevale' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'orleans' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palatka' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'palos verdes estates' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'paradise valley' AS city_norm, 'AZ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pasco' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pawleys island' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'peshtigo' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pikeville' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pine bluff' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pine castle' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pine valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pinole' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'playa vista' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'pleasant grove' AS city_norm, 'AL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'quil ceda village' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rancho mission viejo' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'red bluff' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'reedley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rensselaer' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'richland center' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rockledge' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'rome' AS city_norm, 'GA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'se washington' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint louis park' AS city_norm, 'MN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'saint pete beach' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'scotts valley' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'seatac' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sedro woolley' AS city_norm, 'WA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shavano park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shelbyville' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shenandoah' AS city_norm, 'IA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shepherdsville' AS city_norm, 'KY' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sherwood' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'shorewood' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'signal mountain' AS city_norm, 'TN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'snohomish county' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'sonora' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'south gate' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'southbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'st. louis park' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stoneham' AS city_norm, 'CO' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'stow' AS city_norm, 'MA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tinley park' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'topeka' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'travelers rest' AS city_norm, 'SC' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'tupelo' AS city_norm, 'AR' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'union gap' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'victoria' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vincennes' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'vineland' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'voorhees' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waldwick' AS city_norm, 'NJ' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wall township' AS city_norm, NULL AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'walnut' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'warrensburg' AS city_norm, 'IL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waterbury' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'waukesha' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wautoma' AS city_norm, 'WI' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wesley chapel' AS city_norm, 'FL' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'westbrook' AS city_norm, 'CT' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'whitestown' AS city_norm, 'IN' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'windsor' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'winters' AS city_norm, 'CA' AS state_derived, 'United States' AS country_derived UNION ALL
    SELECT 'wynnewood' AS city_norm, 'OK' AS state_derived, 'United States' AS country_derived
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
