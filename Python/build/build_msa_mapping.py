#!/usr/bin/env python3
"""
Build a city -> MSA/Metro mapping for cities in the budget closed dataset.
Saves city_to_msa_mapping.json and applies it to the budget CSV,
writing budget_query_results_*_with_metro.csv and .xlsx.

NOTE: The existing city→state mapping has errors (e.g. Mountain View shows AR
instead of CA). The MSA lookup is primarily by city name to avoid false negatives.
For cities shared across metros (e.g. Richmond), the state is used as tiebreaker.
"""
import csv
import json
import os
import re

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
IN_CSV = os.path.join(
    BUDGET_DATA,
    "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area_with_property_sector.csv",
)
OUT_CSV = os.path.join(BUDGET_DATA, "budget_query_results_curated_closed_by_category_with_metro.csv")
OUT_XLSX = os.path.join(BUDGET_DATA, "budget_query_results_curated_closed_by_category_with_metro.xlsx")
MSA_JSON = os.path.join(DATA_DIR, "city_to_msa_mapping.json")

# ---------------------------------------------------------------------------
# METRO DEFINITIONS
# city name (lower) -> metro label
# For ambiguous cities, also keyed as "city|STATE" (uppercase 2-letter state)
# ---------------------------------------------------------------------------
CITY_TO_METRO = {
    # ── Atlanta ──────────────────────────────────────────────────────────────
    "atlanta": "Atlanta", "alpharetta": "Atlanta", "kennesaw": "Atlanta",
    "duluth": "Atlanta", "marietta": "Atlanta", "roswell": "Atlanta",
    "lawrenceville": "Atlanta", "norcross": "Atlanta", "smyrna": "Atlanta",
    "sandy springs": "Atlanta", "peachtree city": "Atlanta", "cumming": "Atlanta",
    "decatur": "Atlanta", "brookhaven": "Atlanta", "college park": "Atlanta",
    "conyers": "Atlanta", "johns creek": "Atlanta", "woodstock": "Atlanta",
    "newnan": "Atlanta", "fayetteville": "Atlanta", "gainesville": "Atlanta",
    "canton": "Atlanta", "rome": "Atlanta", "buford": "Atlanta",

    # ── Austin ────────────────────────────────────────────────────────────────
    "austin": "Austin", "cedar park": "Austin", "round rock": "Austin",
    "georgetown": "Austin", "pflugerville": "Austin", "kyle": "Austin",
    "buda": "Austin", "san marcos": "Austin", "bastrop": "Austin",
    "leander": "Austin", "hutto": "Austin", "taylor": "Austin",
    "pflugerville": "Austin", "dripping springs": "Austin",

    # ── Baltimore ─────────────────────────────────────────────────────────────
    "baltimore": "Baltimore", "owings mills": "Baltimore",
    "towson": "Baltimore", "bel air": "Baltimore", "catonsville": "Baltimore",
    "essex": "Baltimore", "parkville": "Baltimore", "dundalk": "Baltimore",
    "ellicott city": "Baltimore", "glen burnie": "Baltimore",
    "annapolis junction": "Baltimore", "hanover": "Baltimore",
    "columbia": "Baltimore",   # Columbia MD straddles Balt/DC -- assigned Baltimore

    # ── Boston ────────────────────────────────────────────────────────────────
    "boston": "Boston", "cambridge": "Boston", "waltham": "Boston",
    "quincy": "Boston", "somerville": "Boston", "newton": "Boston",
    "lowell": "Boston", "worcester": "Boston", "brockton": "Boston",
    "brookline": "Boston", "malden": "Boston", "medford": "Boston",
    "framingham": "Boston", "natick": "Boston", "needham": "Boston",
    "andover": "Boston", "burlington": "Boston", "woburn": "Boston",
    "peabody": "Boston", "salem": "Boston", "lynn": "Boston",
    "lexington": "Boston", "concord": "Boston", "wellesley": "Boston",
    "waltham": "Boston", "watertown": "Boston", "dedham": "Boston",
    "westwood": "Boston", "norwood": "Boston", "canton": "Boston",
    "stoughton": "Boston", "braintree": "Boston", "weymouth": "Boston",
    "westborough": "Boston", "marlborough": "Boston",

    # ── Charlotte ─────────────────────────────────────────────────────────────
    "charlotte": "Charlotte", "concord": "Charlotte", "gastonia": "Charlotte",
    "rock hill": "Charlotte", "mooresville": "Charlotte", "huntersville": "Charlotte",
    "cornelius": "Charlotte", "davidson": "Charlotte", "matthews": "Charlotte",
    "mint hill": "Charlotte", "kannapolis": "Charlotte", "statesville": "Charlotte",
    "fort mill": "Charlotte", "indian land": "Charlotte", "ballantyne": "Charlotte",
    "pineville": "Charlotte", "harrisburg": "Charlotte",

    # ── Chicago ───────────────────────────────────────────────────────────────
    "chicago": "Chicago", "naperville": "Chicago", "aurora": "Chicago",
    "schaumburg": "Chicago", "lisle": "Chicago", "barrington": "Chicago",
    "cary": "Chicago", "oak brook": "Chicago", "rosemont": "Chicago",
    "downers grove": "Chicago", "lombard": "Chicago", "elgin": "Chicago",
    "joliet": "Chicago", "evanston": "Chicago", "arlington heights": "Chicago",
    "elk grove village": "Chicago", "buffalo grove": "Chicago",
    "palatine": "Chicago", "gurnee": "Chicago", "northbrook": "Chicago",
    "glen ellyn": "Chicago", "wheaton": "Chicago", "carol stream": "Chicago",
    "bolingbrook": "Chicago", "romeoville": "Chicago", "tinley park": "Chicago",
    "orland park": "Chicago", "oak lawn": "Chicago", "harvey": "Chicago",
    "waukegan": "Chicago", "north chicago": "Chicago", "hoffman estates": "Chicago",
    "des plaines": "Chicago", "mount prospect": "Chicago",
    "rolling meadows": "Chicago", "addison": "Chicago", "itasca": "Chicago",
    "woodridge": "Chicago", "glendale heights": "Chicago",
    "bloomingdale": "Chicago", "roselle": "Chicago", "hanover park": "Chicago",
    "streamwood": "Chicago", "bartlett": "Chicago", "st. charles": "Chicago",
    "saint charles": "Chicago", "batavia": "Chicago", "oswego": "Chicago",
    "plainfield": "Chicago", "shorewood": "Chicago", "lockport": "Chicago",
    "deerfield": "Chicago", "lake forest": "Chicago", "highland park": "Chicago",
    "libertyville": "Chicago", "round lake": "Chicago", "mundelein": "Chicago",
    "park ridge": "Chicago", "niles": "Chicago", "skokie": "Chicago",
    "morton grove": "Chicago", "lincolnwood": "Chicago",
    "chicago heights": "Chicago", "south holland": "Chicago",
    "dolton": "Chicago", "lansing": "Chicago", "calumet city": "Chicago",
    "oak park": "Chicago", "berwyn": "Chicago", "cicero": "Chicago",
    "melrose park": "Chicago", "franklin park": "Chicago",
    "wood dale": "Chicago", "bensenville": "Chicago",

    # ── Cincinnati ────────────────────────────────────────────────────────────
    "cincinnati": "Cincinnati", "mason": "Cincinnati", "fairfield": "Cincinnati",
    "blue ash": "Cincinnati", "kenwood": "Cincinnati", "westchester": "Cincinnati",
    "loveland": "Cincinnati", "milford": "Cincinnati", "florence": "Cincinnati",
    "covington": "Cincinnati", "newport": "Cincinnati", "covington": "Cincinnati",
    "fort mitchell": "Cincinnati", "norwood": "Cincinnati",
    "anderson township": "Cincinnati", "hyde park": "Cincinnati",

    # ── Cleveland ─────────────────────────────────────────────────────────────
    "cleveland": "Cleveland", "akron": "Cleveland", "parma": "Cleveland",
    "strongsville": "Cleveland", "solon": "Cleveland", "beachwood": "Cleveland",
    "westlake": "Cleveland", "north olmsted": "Cleveland",
    "independence": "Cleveland", "bedford": "Cleveland",

    # ── Columbus ──────────────────────────────────────────────────────────────
    "columbus": "Columbus", "dublin": "Columbus", "westerville": "Columbus",
    "hilliard": "Columbus", "grove city": "Columbus", "reynoldsburg": "Columbus",
    "gahanna": "Columbus", "lewis center": "Columbus", "new albany": "Columbus",

    # ── Dallas-Fort Worth ─────────────────────────────────────────────────────
    "dallas": "Dallas-Fort Worth", "fort worth": "Dallas-Fort Worth",
    "arlington": "Dallas-Fort Worth", "plano": "Dallas-Fort Worth",
    "irving": "Dallas-Fort Worth", "richardson": "Dallas-Fort Worth",
    "frisco": "Dallas-Fort Worth", "mckinney": "Dallas-Fort Worth",
    "garland": "Dallas-Fort Worth", "mesquite": "Dallas-Fort Worth",
    "carrollton": "Dallas-Fort Worth", "lewisville": "Dallas-Fort Worth",
    "grand prairie": "Dallas-Fort Worth", "addison": "Dallas-Fort Worth",
    "coppell": "Dallas-Fort Worth", "grapevine": "Dallas-Fort Worth",
    "allen": "Dallas-Fort Worth", "denton": "Dallas-Fort Worth",
    "flower mound": "Dallas-Fort Worth", "euless": "Dallas-Fort Worth",
    "bedford": "Dallas-Fort Worth", "hurst": "Dallas-Fort Worth",
    "north richland hills": "Dallas-Fort Worth", "keller": "Dallas-Fort Worth",
    "southlake": "Dallas-Fort Worth", "colleyville": "Dallas-Fort Worth",
    "mansfield": "Dallas-Fort Worth", "cedar hill": "Dallas-Fort Worth",
    "desoto": "Dallas-Fort Worth", "duncanville": "Dallas-Fort Worth",
    "waxahachie": "Dallas-Fort Worth", "burleson": "Dallas-Fort Worth",
    "prosper": "Dallas-Fort Worth", "the colony": "Dallas-Fort Worth",
    "little elm": "Dallas-Fort Worth", "rockwall": "Dallas-Fort Worth",
    "rowlett": "Dallas-Fort Worth", "wylie": "Dallas-Fort Worth",
    "sachse": "Dallas-Fort Worth", "murphy": "Dallas-Fort Worth",
    "forney": "Dallas-Fort Worth", "azle": "Dallas-Fort Worth",
    "weatherford": "Dallas-Fort Worth",

    # ── Denver ────────────────────────────────────────────────────────────────
    "denver": "Denver", "aurora": "Denver", "lakewood": "Denver",
    "thornton": "Denver", "arvada": "Denver", "westminster": "Denver",
    "englewood": "Denver", "littleton": "Denver", "centennial": "Denver",
    "highlands ranch": "Denver", "castle rock": "Denver",
    "lone tree": "Denver", "parker": "Denver", "commerce city": "Denver",
    "broomfield": "Denver", "boulder": "Denver", "longmont": "Denver",
    "greeley": "Denver", "fort collins": "Denver", "loveland": "Denver",
    "colorado springs": "Colorado Springs",  # separate MSA

    # ── Detroit ───────────────────────────────────────────────────────────────
    "detroit": "Detroit", "warren": "Detroit", "sterling heights": "Detroit",
    "ann arbor": "Detroit", "lansing": "Detroit", "troy": "Detroit",
    "livonia": "Detroit", "dearborn": "Detroit", "westland": "Detroit",
    "southfield": "Detroit", "pontiac": "Detroit", "farmington hills": "Detroit",
    "auburn hills": "Detroit", "rochester hills": "Detroit",
    "royal oak": "Detroit", "novi": "Detroit", "canton": "Detroit",
    "clinton township": "Detroit", "macomb": "Detroit",
    "shelby township": "Detroit", "flint": "Detroit",

    # ── Houston ───────────────────────────────────────────────────────────────
    "houston": "Houston", "katy": "Houston", "sugar land": "Houston",
    "the woodlands": "Houston", "spring": "Houston", "pearland": "Houston",
    "humble": "Houston", "webster": "Houston", "baytown": "Houston",
    "missouri city": "Houston", "pasadena": "Houston",
    "friendswood": "Houston", "league city": "Houston",
    "clear lake": "Houston", "galveston": "Houston", "conroe": "Houston",
    "tomball": "Houston", "cypress": "Houston", "stafford": "Houston",
    "rosenberg": "Houston", "richmond": "Houston",
    "manvel": "Houston", "alvin": "Houston", "deer park": "Houston",
    "la porte": "Houston", "channelview": "Houston",

    # ── Indianapolis ──────────────────────────────────────────────────────────
    "indianapolis": "Indianapolis", "carmel": "Indianapolis",
    "fishers": "Indianapolis", "noblesville": "Indianapolis",
    "greenwood": "Indianapolis", "avon": "Indianapolis",
    "zionsville": "Indianapolis", "plainfield": "Indianapolis",
    "anderson": "Indianapolis",

    # ── Jacksonville ─────────────────────────────────────────────────────────
    "jacksonville": "Jacksonville", "orange park": "Jacksonville",
    "st. augustine": "Jacksonville", "saint augustine": "Jacksonville",
    "fernandina beach": "Jacksonville", "ponte vedra": "Jacksonville",
    "fleming island": "Jacksonville",

    # ── Kansas City ───────────────────────────────────────────────────────────
    "kansas city": "Kansas City", "overland park": "Kansas City",
    "olathe": "Kansas City", "shawnee": "Kansas City",
    "lee's summit": "Kansas City", "independence": "Kansas City",
    "blue springs": "Kansas City", "lenexa": "Kansas City",
    "leawood": "Kansas City", "raytown": "Kansas City",
    "liberty": "Kansas City", "grain valley": "Kansas City",

    # ── Las Vegas ─────────────────────────────────────────────────────────────
    "las vegas": "Las Vegas", "henderson": "Las Vegas",
    "north las vegas": "Las Vegas", "summerlin": "Las Vegas",
    "enterprise": "Las Vegas", "paradise": "Las Vegas",
    "boulder city": "Las Vegas", "laughlin": "Las Vegas",

    # ── Los Angeles ───────────────────────────────────────────────────────────
    "los angeles": "Los Angeles", "beverly hills": "Los Angeles",
    "santa monica": "Los Angeles", "long beach": "Los Angeles",
    "glendale": "Los Angeles", "burbank": "Los Angeles",
    "torrance": "Los Angeles", "compton": "Los Angeles",
    "el segundo": "Los Angeles", "inglewood": "Los Angeles",
    "culver city": "Los Angeles", "thousand oaks": "Los Angeles",
    "newbury park": "Los Angeles", "oxnard": "Los Angeles",
    "ventura": "Los Angeles", "woodland hills": "Los Angeles",
    "pacific palisades": "Los Angeles", "westwood": "Los Angeles",
    "brentwood": "Los Angeles", "west hollywood": "Los Angeles",
    "studio city": "Los Angeles", "encino": "Los Angeles",
    "sherman oaks": "Los Angeles", "van nuys": "Los Angeles",
    "north hollywood": "Los Angeles", "chatsworth": "Los Angeles",
    "canoga park": "Los Angeles", "reseda": "Los Angeles",
    "irvine": "Los Angeles", "anaheim": "Los Angeles",
    "orange": "Los Angeles", "santa ana": "Los Angeles",
    "huntington beach": "Los Angeles", "costa mesa": "Los Angeles",
    "newport beach": "Los Angeles", "yorba linda": "Los Angeles",
    "brea": "Los Angeles", "fullerton": "Los Angeles",
    "pomona": "Los Angeles", "ontario": "Los Angeles",
    "riverside": "Los Angeles", "san bernardino": "Los Angeles",
    "bloomington": "Los Angeles", "lancaster": "Los Angeles",
    "palmdale": "Los Angeles", "santa clarita": "Los Angeles",
    "pasadena": "Los Angeles", "monrovia": "Los Angeles",
    "arcadia": "Los Angeles", "west covina": "Los Angeles",
    "covina": "Los Angeles", "glendora": "Los Angeles",
    "diamond bar": "Los Angeles", "rowland heights": "Los Angeles",
    "El Monte": "Los Angeles", "downey": "Los Angeles",
    "norwalk": "Los Angeles", "cerritos": "Los Angeles",
    "lakewood": "Los Angeles", "hawthorne": "Los Angeles",
    "gardena": "Los Angeles", "carson": "Los Angeles",
    "redondo beach": "Los Angeles", "manhattan beach": "Los Angeles",
    "hermosa beach": "Los Angeles", "el monte": "Los Angeles",
    "chino": "Los Angeles", "chino hills": "Los Angeles",
    "corona": "Los Angeles", "rancho cucamonga": "Los Angeles",
    "ontario": "Los Angeles", "fontana": "Los Angeles",
    "rialto": "Los Angeles", "colton": "Los Angeles",
    "redlands": "Los Angeles", "yucaipa": "Los Angeles",
    "camarillo": "Los Angeles", "simi valley": "Los Angeles",
    "moorpark": "Los Angeles", "westlake village": "Los Angeles",
    "agoura hills": "Los Angeles", "calabasas": "Los Angeles",
    "cypress": "Los Angeles", "la habra": "Los Angeles",
    "la mirada": "Los Angeles", "buena park": "Los Angeles",
    "lakewood": "Los Angeles", "bellflower": "Los Angeles",
    "pico rivera": "Los Angeles", "montebello": "Los Angeles",
    "alhambra": "Los Angeles", "san gabriel": "Los Angeles",
    "temple city": "Los Angeles", "rosemead": "Los Angeles",
    "south pasadena": "Los Angeles", "sierra madre": "Los Angeles",
    "la canada flintridge": "Los Angeles",
    "la crescenta": "Los Angeles", "tarzana": "Los Angeles",
    "westport": "Los Angeles",  # if Westport CA is Ventura County

    # ── Memphis ───────────────────────────────────────────────────────────────
    "memphis": "Memphis", "germantown": "Memphis", "bartlett": "Memphis",
    "collierville": "Memphis", "cordova": "Memphis",
    "olive branch": "Memphis", "southaven": "Memphis",
    "horn lake": "Memphis", "millington": "Memphis",

    # ── Miami ─────────────────────────────────────────────────────────────────
    "miami": "Miami", "fort lauderdale": "Miami", "boca raton": "Miami",
    "west palm beach": "Miami", "hialeah": "Miami",
    "hollywood": "Miami", "pembroke pines": "Miami",
    "coral springs": "Miami", "miramar": "Miami",
    "davie": "Miami", "plantation": "Miami", "sunrise": "Miami",
    "deerfield beach": "Miami", "pompano beach": "Miami",
    "delray beach": "Miami", "boynton beach": "Miami",
    "lake worth": "Miami", "palm beach gardens": "Miami",
    "jupiter": "Miami", "coral gables": "Miami",
    "homestead": "Miami", "north miami": "Miami",
    "miami beach": "Miami", "miami gardens": "Miami",
    "weston": "Miami", "wellington": "Miami", "palm beach": "Miami",
    "aventura": "Miami", "doral": "Miami", "kendall": "Miami",
    "cutler bay": "Miami", "tamarac": "Miami", "margate": "Miami",
    "coconut creek": "Miami", "hallandale beach": "Miami",

    # ── Milwaukee ─────────────────────────────────────────────────────────────
    "milwaukee": "Milwaukee", "brookfield": "Milwaukee",
    "wauwatosa": "Milwaukee", "waukesha": "Milwaukee",
    "west allis": "Milwaukee", "oak creek": "Milwaukee",
    "mequon": "Milwaukee", "new berlin": "Milwaukee",
    "greenfield": "Milwaukee", "franklin": "Milwaukee",

    # ── Minneapolis-St. Paul ──────────────────────────────────────────────────
    "minneapolis": "Minneapolis-St. Paul", "saint paul": "Minneapolis-St. Paul",
    "st. paul": "Minneapolis-St. Paul", "bloomington": "Minneapolis-St. Paul",
    "plymouth": "Minneapolis-St. Paul", "brooklyn park": "Minneapolis-St. Paul",
    "edina": "Minneapolis-St. Paul", "st. louis park": "Minneapolis-St. Paul",
    "maple grove": "Minneapolis-St. Paul", "eagan": "Minneapolis-St. Paul",
    "burnsville": "Minneapolis-St. Paul", "apple valley": "Minneapolis-St. Paul",
    "lakeville": "Minneapolis-St. Paul", "eden prairie": "Minneapolis-St. Paul",
    "minnetonka": "Minneapolis-St. Paul", "coon rapids": "Minneapolis-St. Paul",
    "blaine": "Minneapolis-St. Paul", "roseville": "Minneapolis-St. Paul",
    "shakopee": "Minneapolis-St. Paul", "maplewood": "Minneapolis-St. Paul",
    "woodbury": "Minneapolis-St. Paul", "cottage grove": "Minneapolis-St. Paul",
    "richfield": "Minneapolis-St. Paul", "prior lake": "Minneapolis-St. Paul",
    "chaska": "Minneapolis-St. Paul", "stillwater": "Minneapolis-St. Paul",
    "rogers": "Minneapolis-St. Paul", "inver grove heights": "Minneapolis-St. Paul",
    "andover": "Minneapolis-St. Paul",

    # ── Nashville ─────────────────────────────────────────────────────────────
    "nashville": "Nashville", "brentwood": "Nashville",
    "franklin": "Nashville", "murfreesboro": "Nashville",
    "hendersonville": "Nashville", "smyrna": "Nashville",
    "gallatin": "Nashville", "columbia": "Nashville",
    "la vergne": "Nashville", "spring hill": "Nashville",
    "nolensville": "Nashville", "mt. juliet": "Nashville",
    "mount juliet": "Nashville", "clarksville": "Nashville",

    # ── New Orleans ───────────────────────────────────────────────────────────
    "new orleans": "New Orleans", "metairie": "New Orleans",
    "kenner": "New Orleans", "slidell": "New Orleans",
    "gretna": "New Orleans", "chalmette": "New Orleans",
    "harvey": "New Orleans", "marrero": "New Orleans",
    "baton rouge": "Baton Rouge",

    # ── New York ──────────────────────────────────────────────────────────────
    "new york": "New York", "brooklyn": "New York",
    "queens": "New York", "bronx": "New York",
    "staten island": "New York", "jersey city": "New York",
    "newark": "New York", "hoboken": "New York",
    "stamford": "New York", "bridgeport": "New York",
    "new haven": "New York", "hartford": "New York",
    "yonkers": "New York", "white plains": "New York",
    "mount vernon": "New York", "new rochelle": "New York",
    "hempstead": "New York", "long island city": "New York",
    "garden city": "New York", "mineola": "New York",
    "hicksville": "New York", "westbury": "New York",
    "holtsville": "New York", "islandia": "New York",
    "melville": "New York", "hauppauge": "New York",
    "ronkonkoma": "New York", "binghamton": "New York",
    "poughkeepsie": "New York", "newburgh": "New York",
    "tarrytown": "New York", "white plains": "New York",
    "parsippany": "New York", "morristown": "New York",
    "princeton": "New York", "trenton": "New York",
    "edison": "New York", "new brunswick": "New York",
    "woodbridge": "New York", "elizabeth": "New York",
    "union": "New York", "hackensack": "New York",
    "paramus": "New York", "fort lee": "New York",
    "ridgefield park": "New York", "fairfield": "New York",
    "norfolk": "New York",  # will be overridden by state-specific
    "plainfield": "New York",  # NJ Plainfield → NY metro area

    # ── Oklahoma City ─────────────────────────────────────────────────────────
    "oklahoma city": "Oklahoma City", "norman": "Oklahoma City",
    "edmond": "Oklahoma City", "moore": "Oklahoma City",
    "midwest city": "Oklahoma City", "yukon": "Oklahoma City",
    "mustang": "Oklahoma City", "del city": "Oklahoma City",

    # ── Orlando ───────────────────────────────────────────────────────────────
    "orlando": "Orlando", "kissimmee": "Orlando",
    "sanford": "Orlando", "deltona": "Orlando",
    "daytona beach": "Daytona Beach",
    "lake mary": "Orlando", "altamonte springs": "Orlando",
    "casselberry": "Orlando", "longwood": "Orlando",
    "oviedo": "Orlando", "winter park": "Orlando",
    "maitland": "Orlando", "windermere": "Orlando",
    "ocoee": "Orlando", "apopka": "Orlando",
    "clermont": "Orlando", "ocala": "Ocala",  # separate MSA
    "the villages": "The Villages",

    # ── Philadelphia ─────────────────────────────────────────────────────────
    "philadelphia": "Philadelphia", "wilmington": "Philadelphia",
    "king of prussia": "Philadelphia", "wayne": "Philadelphia",
    "allentown": "Philadelphia", "bethlehem": "Philadelphia",
    "reading": "Philadelphia", "trenton": "Philadelphia",
    "camden": "Philadelphia", "cherry hill": "Philadelphia",
    "mount laurel": "Philadelphia", "moorestown": "Philadelphia",
    "voorhees": "Philadelphia", "marlton": "Philadelphia",
    "west chester": "Philadelphia", "exton": "Philadelphia",
    "malvern": "Philadelphia", "norristown": "Philadelphia",
    "ardmore": "Philadelphia", "bala cynwyd": "Philadelphia",
    "conshohocken": "Philadelphia", "blue bell": "Philadelphia",
    "lansdale": "Philadelphia", "hatboro": "Philadelphia",

    # ── Phoenix ───────────────────────────────────────────────────────────────
    "phoenix": "Phoenix", "scottsdale": "Phoenix", "tempe": "Phoenix",
    "mesa": "Phoenix", "chandler": "Phoenix", "gilbert": "Phoenix",
    "glendale": "Phoenix", "peoria": "Phoenix", "avondale": "Phoenix",
    "goodyear": "Phoenix", "surprise": "Phoenix", "buckeye": "Phoenix",
    "queen creek": "Phoenix", "san tan valley": "Phoenix",
    "maricopa": "Phoenix", "fountain hills": "Phoenix",
    "cave creek": "Phoenix", "carefree": "Phoenix",
    "paradise valley": "Phoenix", "litchfield park": "Phoenix",
    "tolleson": "Phoenix", "el mirage": "Phoenix",
    "youngtown": "Phoenix", "sun city": "Phoenix",
    "sun city west": "Phoenix", "sun lakes": "Phoenix",
    "ahwatukee": "Phoenix", "anthem": "Phoenix", "prescott": "Prescott",
    "tucson": "Tucson",  # separate MSA

    # ── Pittsburgh ────────────────────────────────────────────────────────────
    "pittsburgh": "Pittsburgh", "cranberry township": "Pittsburgh",
    "monroeville": "Pittsburgh", "north hills": "Pittsburgh",
    "bethel park": "Pittsburgh", "robinson township": "Pittsburgh",
    "mcmurray": "Pittsburgh", "mt. lebanon": "Pittsburgh",

    # ── Portland ──────────────────────────────────────────────────────────────
    "portland": "Portland", "beaverton": "Portland",
    "hillsboro": "Portland", "gresham": "Portland",
    "tigard": "Portland", "lake oswego": "Portland",
    "tualatin": "Portland", "wilsonville": "Portland",
    "sherwood": "Portland", "king city": "Portland",
    "vancouver": "Portland",  # Vancouver WA is Portland metro
    "camas": "Portland", "battle ground": "Portland",

    # ── Raleigh-Durham ────────────────────────────────────────────────────────
    "raleigh": "Raleigh-Durham", "durham": "Raleigh-Durham",
    "cary": "Raleigh-Durham", "morrisville": "Raleigh-Durham",
    "chapel hill": "Raleigh-Durham", "apex": "Raleigh-Durham",
    "holly springs": "Raleigh-Durham", "wake forest": "Raleigh-Durham",
    "garner": "Raleigh-Durham", "knightdale": "Raleigh-Durham",
    "research triangle park": "Raleigh-Durham",

    # ── Richmond ─────────────────────────────────────────────────────────────
    "richmond": "Richmond VA",  # default - CA override via state key below
    "glen allen": "Richmond VA", "henrico": "Richmond VA",
    "chesterfield": "Richmond VA", "mechanicsville": "Richmond VA",
    "midlothian": "Richmond VA", "short pump": "Richmond VA",
    "ashland": "Richmond VA",

    # ── Sacramento ────────────────────────────────────────────────────────────
    "sacramento": "Sacramento", "roseville": "Sacramento",
    "folsom": "Sacramento", "elk grove": "Sacramento",
    "rancho cordova": "Sacramento", "citrus heights": "Sacramento",
    "rocklin": "Sacramento", "lincoln": "Sacramento",
    "auburn": "Sacramento", "davis": "Sacramento",
    "woodland": "Sacramento", "vacaville": "Sacramento",
    "fairfield": "Sacramento",

    # ── San Antonio ───────────────────────────────────────────────────────────
    "san antonio": "San Antonio", "new braunfels": "San Antonio",
    "schertz": "San Antonio", "converse": "San Antonio",
    "boerne": "San Antonio", "universal city": "San Antonio",
    "leon valley": "San Antonio", "windcrest": "San Antonio",

    # ── San Diego ─────────────────────────────────────────────────────────────
    "san diego": "San Diego", "chula vista": "San Diego",
    "el cajon": "San Diego", "escondido": "San Diego",
    "oceanside": "San Diego", "carlsbad": "San Diego",
    "vista": "San Diego", "santee": "San Diego",
    "national city": "San Diego", "la mesa": "San Diego",
    "lemon grove": "San Diego", "poway": "San Diego",
    "san marcos": "San Diego", "encinitas": "San Diego",
    "solana beach": "San Diego", "del mar": "San Diego",
    "coronado": "San Diego", "imperial beach": "San Diego",
    "el centro": "El Centro",

    # ── San Francisco Bay Area ────────────────────────────────────────────────
    "san francisco": "San Francisco Bay Area",
    "san jose": "San Francisco Bay Area",
    "oakland": "San Francisco Bay Area",
    "sunnyvale": "San Francisco Bay Area",
    "santa clara": "San Francisco Bay Area",
    "palo alto": "San Francisco Bay Area",
    "mountain view": "San Francisco Bay Area",
    "redwood city": "San Francisco Bay Area",
    "menlo park": "San Francisco Bay Area",
    "fremont": "San Francisco Bay Area",
    "san mateo": "San Francisco Bay Area",
    "hayward": "San Francisco Bay Area",
    "berkeley": "San Francisco Bay Area",
    "walnut creek": "San Francisco Bay Area",
    "pleasanton": "San Francisco Bay Area",
    "south san francisco": "San Francisco Bay Area",
    "milpitas": "San Francisco Bay Area",
    "cupertino": "San Francisco Bay Area",
    "santa cruz": "San Francisco Bay Area",
    "richmond": "San Francisco Bay Area",   # CA override below
    "burlingame": "San Francisco Bay Area",
    "foster city": "San Francisco Bay Area",
    "san rafael": "San Francisco Bay Area",
    "novato": "San Francisco Bay Area",
    "san leandro": "San Francisco Bay Area",
    "union city": "San Francisco Bay Area",
    "newark": "San Francisco Bay Area",  # Newark CA
    "livermore": "San Francisco Bay Area",
    "concord": "San Francisco Bay Area",
    "antioch": "San Francisco Bay Area",
    "pittsburg": "San Francisco Bay Area",
    "brentwood": "San Francisco Bay Area",  # CA Brentwood in East Bay
    "los gatos": "San Francisco Bay Area",
    "campbell": "San Francisco Bay Area",
    "saratoga": "San Francisco Bay Area",
    "morgan hill": "San Francisco Bay Area",
    "gilroy": "San Francisco Bay Area",
    "san bruno": "San Francisco Bay Area",
    "daly city": "San Francisco Bay Area",
    "pacifica": "San Francisco Bay Area",
    "half moon bay": "San Francisco Bay Area",
    "napa": "San Francisco Bay Area",
    "petaluma": "San Francisco Bay Area",
    "santa rosa": "San Francisco Bay Area",
    "rohnert park": "San Francisco Bay Area",
    "middletown": "San Francisco Bay Area",
    "vacaville": "San Francisco Bay Area",
    "benicia": "San Francisco Bay Area",
    "vallejo": "San Francisco Bay Area",
    "emeryville": "San Francisco Bay Area",
    "alameda": "San Francisco Bay Area",
    "redwood shores": "San Francisco Bay Area",
    "foster city": "San Francisco Bay Area",
    "independence": "San Francisco Bay Area",  # CA Independence in East Bay
    "san ramon": "San Francisco Bay Area",
    "danville": "San Francisco Bay Area",
    "alamo": "San Francisco Bay Area",
    "orinda": "San Francisco Bay Area",
    "moraga": "San Francisco Bay Area",

    # ── Seattle ───────────────────────────────────────────────────────────────
    "seattle": "Seattle", "bellevue": "Seattle",
    "kirkland": "Seattle", "redmond": "Seattle",
    "renton": "Seattle", "kent": "Seattle",
    "federal way": "Seattle", "tacoma": "Seattle",
    "lakewood": "Seattle", "puyallup": "Seattle",
    "auburn": "Seattle", "lynnwood": "Seattle",
    "everett": "Seattle", "marysville": "Seattle",
    "bothell": "Seattle", "issaquah": "Seattle",
    "sammamish": "Seattle", "woodinville": "Seattle",
    "shoreline": "Seattle", "mountlake terrace": "Seattle",
    "edmonds": "Seattle", "kenmore": "Seattle",
    "burien": "Seattle", "tukwila": "Seattle",
    "seatac": "Seattle", "des moines": "Seattle",
    "covington": "Seattle", "maple valley": "Seattle",
    "mercer island": "Seattle", "newcastle": "Seattle",
    "north bend": "Seattle", "snoqualmie": "Seattle",
    "duvall": "Seattle", "carnation": "Seattle",
    "monroe": "Seattle", "sultan": "Seattle",

    # ── St. Louis ────────────────────────────────────────────────────────────
    "saint louis": "St. Louis", "st. louis": "St. Louis",
    "chesterfield": "St. Louis", "o'fallon": "St. Louis",
    "st. charles": "St. Louis", "florissant": "St. Louis",
    "ballwin": "St. Louis", "wildwood": "St. Louis",
    "creve coeur": "St. Louis", "maryland heights": "St. Louis",
    "hazelwood": "St. Louis", "fenton": "St. Louis",

    # ── Tampa-St. Petersburg ──────────────────────────────────────────────────
    "tampa": "Tampa-St. Petersburg", "st. petersburg": "Tampa-St. Petersburg",
    "saint petersburg": "Tampa-St. Petersburg",
    "clearwater": "Tampa-St. Petersburg",
    "brandon": "Tampa-St. Petersburg",
    "riverview": "Tampa-St. Petersburg",
    "sarasota": "Tampa-St. Petersburg",  # often grouped
    "bradenton": "Tampa-St. Petersburg",
    "plant city": "Tampa-St. Petersburg",
    "new port richey": "Tampa-St. Petersburg",
    "spring hill": "Tampa-St. Petersburg",
    "wesley chapel": "Tampa-St. Petersburg",
    "zephyrhills": "Tampa-St. Petersburg",
    "land o lakes": "Tampa-St. Petersburg",
    "lutz": "Tampa-St. Petersburg",

    # ── Washington DC ─────────────────────────────────────────────────────────
    "washington": "Washington DC",  # default for this city name
    "reston": "Washington DC", "mclean": "Washington DC",
    "ashburn": "Washington DC", "chantilly": "Washington DC",
    "falls church": "Washington DC", "alexandria": "Washington DC",
    "herndon": "Washington DC", "vienna": "Washington DC",
    "tysons": "Washington DC", "tysons corner": "Washington DC",
    "bethesda": "Washington DC", "gaithersburg": "Washington DC",
    "rockville": "Washington DC", "silver spring": "Washington DC",
    "germantown": "Washington DC", "fairfax": "Washington DC",
    "springfield": "Washington DC",
    "woodbridge": "Washington DC",
    "manassas": "Washington DC", "gainesville": "Washington DC",
    "centreville": "Washington DC", "burke": "Washington DC",
    "lorton": "Washington DC", "fort belvoir": "Washington DC",
    "quantico": "Washington DC", "stafford": "Washington DC",
    "fredericksburg": "Washington DC",
    "annapolis junction": "Washington DC",
    "college park": "Washington DC",  # MD College Park
    "bowie": "Washington DC", "laurel": "Washington DC",
    "greenbelt": "Washington DC", "hyattsville": "Washington DC",
    "lanham": "Washington DC", "upper marlboro": "Washington DC",
    "clinton": "Washington DC",

    # ── Other standalone metros ────────────────────────────────────────────────
    "albuquerque": "Albuquerque",
    "buffalo": "Buffalo",
    "charleston": "Charleston SC",
    "chattanooga": "Chattanooga",
    "des moines": "Des Moines",
    "el paso": "El Paso",
    "fresno": "Fresno",
    "greenville": "Greenville SC",
    "hartford": "Hartford",
    "honolulu": "Honolulu",
    "huntsville": "Huntsville",
    "jackson": "Jackson MS",
    "knoxville": "Knoxville",
    "lexington": "Lexington KY",
    "little rock": "Little Rock",
    "louisville": "Louisville",
    "madison": "Madison WI",
    "modesto": "Modesto",
    "omaha": "Omaha",
    "oxnard": "Los Angeles",  # Ventura County → LA metro
    "pensacola": "Pensacola",
    "reno": "Reno",
    "rochester": "Rochester NY",
    "salt lake city": "Salt Lake City",
    "spokane": "Spokane",
    "springfield": "Springfield MO",
    "stockton": "Stockton",
    "tallahassee": "Tallahassee",
    "tucson": "Tucson",
    "tulsa": "Tulsa",
    "wichita": "Wichita",
    "winston-salem": "Winston-Salem",
    "greensboro": "Greensboro NC",
    "durham": "Raleigh-Durham",  # part of Research Triangle
    "chapel hill": "Raleigh-Durham",
    "fayetteville nc": "Fayetteville NC",
    "savannah": "Savannah",
    "augusta": "Augusta GA",
    "columbia sc": "Columbia SC",
    "boise": "Boise",
    "provo": "Provo",
    "bakersfield": "Bakersfield",
    "el centro": "El Centro",
    "syracuse": "Syracuse",
    "albany": "Albany NY",
    "worcester": "Worcester",
    "springfield ma": "Springfield MA",
    "new haven": "New Haven",
    "bridgeport": "Bridgeport",
    "stamford": "Stamford CT",
    "norfolk": "Virginia Beach-Norfolk",
    "virginia beach": "Virginia Beach-Norfolk",
    "chesapeake": "Virginia Beach-Norfolk",
    "hampton": "Virginia Beach-Norfolk",
    "newport news": "Virginia Beach-Norfolk",
    "suffolk": "Virginia Beach-Norfolk",
}

# ---------------------------------------------------------------------------
# State-specific overrides for ambiguous city names
# key: "city_lower|STATE" (2-letter uppercase)
# ---------------------------------------------------------------------------
STATE_OVERRIDES = {
    # Richmond: CA = Bay Area, VA = Richmond VA
    "richmond|ca": "San Francisco Bay Area",
    "richmond|va": "Richmond VA",
    # Brentwood: CA = Bay Area East Bay, TN = Nashville
    "brentwood|ca": "San Francisco Bay Area",
    "brentwood|tn": "Nashville",
    # Columbia: MD = Baltimore, SC = Columbia SC, MO = Columbia MO
    "columbia|md": "Baltimore",
    "columbia|sc": "Columbia SC",
    "columbia|mo": "Columbia MO",
    # Bloomington: CA = Los Angeles, MN = Minneapolis, IL = Chicago, IN = Indianapolis
    "bloomington|ca": "Los Angeles",
    "bloomington|mn": "Minneapolis-St. Paul",
    "bloomington|il": "Chicago",
    "bloomington|in": "Indianapolis",
    # Aurora: CO = Denver, IL = Chicago
    "aurora|co": "Denver",
    "aurora|il": "Chicago",
    # Canton: GA = Atlanta, OH = Cleveland
    "canton|ga": "Atlanta",
    "canton|oh": "Cleveland",
    # Concord: CA = Bay Area, NC = Charlotte
    "concord|ca": "San Francisco Bay Area",
    "concord|nc": "Charlotte",
    # Vancouver: WA = Portland, BC = Vancouver Canada
    "vancouver|wa": "Portland",
    # Springfield: MO = Springfield MO, VA = Washington DC, MA = Springfield MA
    "springfield|mo": "Springfield MO",
    "springfield|va": "Washington DC",
    "springfield|ma": "Springfield MA",
    "springfield|il": "Springfield IL",
    "springfield|oh": "Springfield OH",
    # Franklin: TN = Nashville, MA = Boston
    "franklin|tn": "Nashville",
    "franklin|ma": "Boston",
    # Washington: DC = Washington DC, PA = Pittsburgh (Washington PA)
    "washington|dc": "Washington DC",
    "washington|pa": "Pittsburgh",
    # Fairfield: CA = Sacramento/Bay Area, CT = New York, NJ = Philadelphia/NY
    "fairfield|ca": "San Francisco Bay Area",
    "fairfield|ct": "New York",
    "fairfield|nj": "New York",
    "fairfield|oh": "Cincinnati",
    # Pasadena: CA = Los Angeles, TX = Houston
    "pasadena|ca": "Los Angeles",
    "pasadena|tx": "Houston",
    # Independence: CA = Bay Area (if small city), MO = Kansas City
    "independence|mo": "Kansas City",
    "independence|ca": "San Francisco Bay Area",
    # Norwood: OH = Cincinnati, MA = Boston
    "norwood|oh": "Cincinnati",
    "norwood|ma": "Boston",
    # Smyrna: GA = Atlanta, TN = Nashville, DE = Philadelphia
    "smyrna|ga": "Atlanta",
    "smyrna|tn": "Nashville",
    "smyrna|de": "Philadelphia",
    # Andover: MA = Boston, MN = Minneapolis
    "andover|ma": "Boston",
    "andover|mn": "Minneapolis-St. Paul",
    # Plainfield: IL = Chicago, NJ = New York, CT = New York
    "plainfield|il": "Chicago",
    "plainfield|nj": "New York",
    "plainfield|ct": "New York",
    # Cary: IL = Chicago, NC = Raleigh-Durham
    "cary|il": "Chicago",
    "cary|nc": "Raleigh-Durham",
    # Newton: MA = Boston, NJ = New York
    "newton|ma": "Boston",
    "newton|nj": "New York",
    # Herndon: VA = Washington DC, KS = (standalone)
    "herndon|va": "Washington DC",
    # Kirkland: WA = Seattle, AZ = Phoenix
    "kirkland|wa": "Seattle",
    "kirkland|az": "Phoenix",
    # Cypress: CA = Los Angeles, TX = Houston
    "cypress|ca": "Los Angeles",
    "cypress|tx": "Houston",
    # Harvey: IL = Chicago, LA = New Orleans
    "harvey|il": "Chicago",
    "harvey|la": "New Orleans",
    # Addison: IL = Chicago, TX = Dallas-Fort Worth
    "addison|il": "Chicago",
    "addison|tx": "Dallas-Fort Worth",
    # Glendale: AZ = Phoenix, CA = Los Angeles
    "glendale|az": "Phoenix",
    "glendale|ca": "Los Angeles",
    # Newark: NJ = New York, CA = Bay Area, DE = Philadelphia
    "newark|nj": "New York",
    "newark|ca": "San Francisco Bay Area",
    "newark|de": "Philadelphia",
    # Bartlett: IL = Chicago, TN = Memphis
    "bartlett|il": "Chicago",
    "bartlett|tn": "Memphis",
    # Chesapeake: VA = Virginia Beach-Norfolk
    "chesapeake|va": "Virginia Beach-Norfolk",
    # Norfolke
    "norfolk|va": "Virginia Beach-Norfolk",
}


def normalize(s):
    if s is None or (isinstance(s, float)):
        return ""
    return re.sub(r'\s+', ' ', str(s).strip().lower())


def lookup_metro(city, state):
    c = normalize(city)
    s = normalize(state).upper()
    if not c:
        return None
    # 1. State-specific override
    key_st = f"{c}|{s}"
    if key_st in STATE_OVERRIDES:
        return STATE_OVERRIDES[key_st]
    # 2. City-only lookup
    if c in CITY_TO_METRO:
        return CITY_TO_METRO[c]
    return None


def build_and_apply():
    import pandas as pd

    # Build full mapping dict and save JSON
    mapping = {}
    for city_key, metro in CITY_TO_METRO.items():
        mapping[city_key] = metro
    for city_state_key, metro in STATE_OVERRIDES.items():
        mapping[city_state_key] = metro

    with open(MSA_JSON, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    print(f"Saved {len(mapping)} entries to {MSA_JSON}")

    # Apply to budget CSV
    df = pd.read_csv(IN_CSV)
    print(f"Loaded {len(df)} rows from budget CSV.")

    df["metro"] = df.apply(
        lambda r: lookup_metro(r.get("city"), r.get("state")), axis=1
    )

    # Coverage stats (US only)
    us_mask = df["country"].str.lower().isin(["united states", "us", "usa"]) | df["country"].isna()
    us = df[us_mask & df["city"].notna()]
    mapped = us[us["metro"].notna()]
    print(f"\n--- Coverage (US rows with city) ---")
    print(f"  Total US rows with city : {len(us):>7,}")
    print(f"  Rows with metro mapped  : {len(mapped):>7,}  ({100*len(mapped)/len(us):.1f}%)")
    print(f"  Project count mapped    : {int(mapped['project_count'].sum()):>7,}")
    print(f"  Project count total     : {int(us['project_count'].sum()):>7,}")

    # Show top unmapped cities
    unmapped = us[us["metro"].isna()].groupby(["city", "state"])["project_count"].sum()
    unmapped = unmapped.sort_values(ascending=False)
    print(f"\nTop 30 unmapped cities:")
    for (city, state), cnt in unmapped.head(30).items():
        print(f"  {city:30s}  {str(state):5s}  {int(cnt):>5}")

    # Metro summary
    print(f"\nTop metros by project count:")
    metro_sum = df[df["metro"].notna()].groupby("metro")["project_count"].sum()
    metro_sum = metro_sum.sort_values(ascending=False)
    for metro, cnt in metro_sum.head(30).items():
        print(f"  {metro:35s}  {int(cnt):>6,}")

    # Write outputs
    df.to_csv(OUT_CSV, index=False)
    print(f"\nWritten to {OUT_CSV}")

    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Closed by Category with Metro"[:31]
        ws.append(list(df.columns))
        for row in df.itertuples(index=False):
            ws.append(list(row))
        wb.save(OUT_XLSX)
    except ImportError:
        df.to_excel(OUT_XLSX, index=False)
    print(f"Written to {OUT_XLSX}")


if __name__ == "__main__":
    build_and_apply()
