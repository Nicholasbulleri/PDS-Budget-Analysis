#!/usr/bin/env python3
"""
Build taskname -> category mapping for budget rollups.
Categories:
  a) FF&E + Millwork: Furniture, finishings, equipment, millwork, decorative materials,
     IT/security integrator, POS, storage shelving, owner-supplied items.
  b) Soft Costs: Designer, architect, engineers, expeditor, PM, special inspections, landmark consultant.
  c) Construction: General contractor / construction trade costs.
"""
import csv
import json
import re

FFE_KEYWORDS = [
    "furniture", "furnishings", "ff&e", "ffe", "millwork", "casework", "cased goods",
    "art", "artwork", "accessories", "appliances", "decorative", "blinds", "window treatment",
    "window covering", "it equipment", "it hardware", "av equipment", "audio visual", "a/v",
    "security equipment", "cameras", "access control", "pos ", "storage shelving", "lockers",
    "signage", "branding", "mobiliario", "seating", "workstations", "chairs", "desk", "tables",
    "carpet", "carpets", "reused furniture", "new furniture", "loose furniture", "ancillary furniture",
    "interior signage", "artwork/", "art & ", "general ff&e", "specialty ffe", "equipment ",
    "av ", "av-", "av consultant", "low voltage", "data cabling", "voice and data", "cabling",
    "printers", "monitors", "network equipment", "waps", "wireless", "telecom", "technology ",
    "food service equipment", "kitchen ", "appliancies", "accesories", "interior design",
    "ff&e interior", "move ", "relocation", "decom", "decommission", "moving", "mover",
    "furniture budget", "furniture allowance", "furniture specification", "furniture planning",
    "henricksen", "office furniture", "conference room", "pantry", "pantry area",
    "building standard blinds", "interior landscaping", "plants", "plantings", "art program",
    "graphics", "wayfinding", "digital displays", "lunch room displays", "reception logo",
    "suite signage", "keying", "decor", "soft decoration", "upholstery",
    "medical equipment purchases", "lab equipment", "o&m equipment", "refrigeration",
    "balers", "scales", "storage ", "shelving", "uline", "lab storage",
    "lighting fixtures", "lighting fixture", "4th floor lighting", "5th floor lighting",
    "lobby lighting", "rigging", "chair", "conference plaques", "cupper sculpture",
    "badge swipe", "camera for ", "cameras/", "das system", "cell phones", "central register",
    "playtest", "streaming studio", "audio & video", "audio/visual", "audio & video |",
    "county it", "cat 6a", "circuit order", "data a/v", "internet of things", "it budget",
    "it/av", "live cams", "video", "audio", "artwork/accessories", "signage", "printers",
    "meeting rooms seats", "workstations-staff", "seats - staff", "cabines",
    "electrodomésticos", "accesorios", "aparatos", "iluminação", "comunicação visual",
]
FFE_EXACT = [
    "equipment", "furniture", "millwork", "art", "artwork", "appliances", "accessories",
    "branding", "signage", "it ", "av ", "security", "cabling", "move", "relocation",
    "decom", "blinds", "seating", "workstations", "carpet", "mobiliario", "diseño",
]
SOFT_KEYWORDS = [
    "architect", "designer", "design ", "engineer", "expeditor", "expediter", "permit",
    "project management", " pm ", "pm fee", "pm fees", "jll ", "jll fee", "jll admin",
    "consultant", "inspection", "survey", "legal", "insurance", "leed", "sustainability",
    "acoustical", "acoustic ", "a/e", "arch/mep", "mep design", "mep consultant", "mep fee",
    "structural eng", "civil eng", "electrical eng", "mechanical eng", "design fees",
    "reimbursable", "reimbursables", "design development", "schematic design", "programming",
    "space planning", "test fit", "visioning", "permitting", "filing fee", "building permit",
    "plan check", "code consultant", "ada consultant", "accessibility consultant",
    "facade consultant", "façade consultant", "landmark", "special inspections", "tas ",
    "commissioning", "building envelope", "envelope evaluation", "geotech", "geotechnical",
    "environmental ", "phase 1", "phase 2", "esa ", "due diligence", "appraisal", "title",
    "legal fee", "management fee", "admin fee", "administration", "gerencia", "gerenciadora",
    "dirección de obra", "dro ", "construction consultant", "design and professional",
    "design services", "professional consultants", "consultores", "diseñadores", "arquitectura",
    "budgetary estimating", "cost consulting", "pds ", "contract management", "owner's rep",
    "landlord pm", "landlord management", "ll management", "cm fee", "principal pm",
    "design contingency", "soft cost contingency", "soft cost %",
    "architectural design", "architectural services", "architectural consultant",
    "interior design ", "interior consultant", "design architect", "landscape architect",
    "landscape consultant", "kitchen consultant", "theater consultant", "multimedia consultant",
    "add service", "additional services", "add services", "basic services", "bid phase",
    "bidding ", "ao bidding", "asr ", "lionakis", "proposal", "amendment ", "amend #",
    "sd-dd", "cd-co", "reimbursable", "con fees", "admin. fee", "annual fee", "development fee",
    "advance payment", "gestorías", "dri ", "dri determination", "dri review", "as-built documentation",
    "accessibility certification", "deign management", "disbursement", "expensas",
    "civil - ", "civil streetlight", "civil technical", "code/comment review", "core drill review",
    "dependencias gubernamentales", "development of regional impact",
]
CONSTRUCTION_KEYWORDS = [
    "general contractor", "gc ", " gc", "gc-", "gmp", "construction ", "construct",
    "concrete", "structural ", "steel", "metals", "masonry", "drywall", "framing",
    "carpentry", "mechanical install", "electrical ", "plumbing", "hvac",
    "mep ", "fire protection", "fire sprinkler", "fire alarm", "demolition", "sitework",
    "earthwork", "excavation", "general conditions", "general requirements", "contingency",
    "hard cost", "hard costs", "construction cost", "construction budget", "construction contingency",
    "roofing", "facade", "facade", "envelope", "glazing", "cladding", "waterproofing",
    "flooring", "flooring ", "ceilings", "walls", "paint", "painting", "finishes",
    "div 2", "div 3", "div 5", "div 6", "div 7", "div 8", "div 9", "div 10", "div 15", "div 16", "div 22", "div 23", "div 26", "div 27", "div 28",
    "construccion", "construcción", "contratistas", "preliminar", "civil works",
    "reinforcement", "shuttering", "pile ", "dewatering", "site work", "utilities",
    "storm water", "stormwater", "irrigation", "landscaping", "exterior improvement",
    "temporary construction", "scaffolding", "builder", "contractor ", "subcontract",
    "base contract", "construction admin", "construction doc", "cd architectural",
    "dd architectural", "sd architectural", "fit out", "fitout", "tenant improvement",
    "ti construction", "interior construction", "leasehold improvement", "base building",
    "north building ", "south building ", "off site ", "on site ", "precon", "pre-con",
    "ocip", "subguard", "sdi", "b&o tax", "state tax", "sales tax", " gr's",
    " general conditions", "contingency - gc", "construction contingency", "gc fee",
    "gmp contract", "construction - ", "contruction", "builders risk",
    "doors frame", "doors, frame", "door replacement", "doors frames", "glass ", "almuminum and glass",
    "boiler replacement", "chilled water", "domestic water", "compressed air", "control room",
    "cleaning ", "cleaning services", "cleaning & protection", "caulking", "column gurd",
    "ceiling tile replacement", "cathodic protection", "change orders", "contract documents",
    "contingencia", "contingecncy", "bms", "bms -", "controls", "bas ", "chlorination",
    "building ", "building sign", "building electrical", "building fees",
    "cableado", "canteen", "carpentry", "carpet", "vct", "base", "carpets and vinyl",
    "circuit", "city intake", "column ", "commercial hose", "commercial ilt",
    "commissioining", "communications", "concept plans", "conceptual ",
    "detectores", "smoke detectors", "dewatering", "dredging", "dredging design",
    "earthwork", "electrical", "elevator", "equipment connections", "equipment electric",
    "existing conditions", "exterior ", "facade", "fire ", "flash ", "floor leveling",
    "floor prep", "floor preparation", "food grade", "frp", "gate ", "granite ",
    "gypsum", "hvac ", "hvac system", "hvac relocate", "insulation", "k-13", "kerb stone",
    "labor ", "laying cost", "land cost", "land/building", "laying cost", "marble work",
    "material ", "metal doors", "metal works", "misc metals", "mockup", "movable partitions",
    "paver work", "pile work", "pipe ", "piping", "plumbing", "plaster", "process ",
    "public area construction", "public row", "rough carpentry", "roofing", "saw cutting",
    "scaffolding", "scrubber", "shoring", "shuttering", "sprinkler", "staircase ",
    "stone ", "supply & fixing", "supply of ", "terracota", "tile cost", "tile ",
    "temporary ", "tents ", "thermal & moisture", "topografía", "trailers",
    "upvc work", "vinyl flooring", "waterproofing", "wood flooring", "wood works",
    "acoustic ceilings", "acoustical ceiling", "walls and ceilings", "coats ", "primer",
    "putty", "emulsion", "acp cladding", "alta tecnología", "ar condicionado", "arquit",
    "boc", "bocw", "bldg #", "boulder ", "brownfield", "cbpmesp", "cd electrical",
    "cd mechanical", "cd structural", "chilled water", "column ", "con fees",
    "contruction", "decom -", "decommission", "demolition", "deterra", "dewate",
    "elect ", "electrical", "elev ", "esd flooring", "estrutura", "excavation",
    "expansion", "exterior", "field ", "final cleaning", "fireproofing", "floor ",
    "foundation", "fundação", "gases e ar", "hidrosanitário", "impermeabilização",
    "instalación", "instalação", "levelling", "mass timber", "mechanical instalation",
    "nurse call", "on site utilities", "off site ", "openings", "pavimentação",
    "paisagismo", "percantege", "pier and infrastructure", "pile work", "projeto ",
    "regularização", "reinforcement", "rink & plant", "rolling shutter", "roof ",
    "sanitary", "sewer", "site ", "sprinkler", "structural ", "subsurface ",
    "tráfego", "trafego", "tráfego/logistica", "vegetation", "vertical transport",
    "water ", "weep ", "white wash", "window ", "wire ", "wiring",
]
# Soft overrides: task names that are clearly soft (design/PM/permitting) but might match construction
SOFT_OVERRIDES = [
    "architect", "design", "engineer", "consultant", "permit", "expeditor", "survey",
    "inspection", "management", "jll", "reimbursable", "fee", "insurance", "legal",
]
# Construction overrides for ambiguous (e.g. "Design" as phase vs design fees - we map "Design" to Soft)
# FFE overrides
FFE_OVERRIDES = ["furniture", "ff&e", "millwork", "art", "av ", "it ", "signage", "move", "relocation"]


def normalize(s):
    return (s or "").strip().lower()


def match_keywords(text, keywords):
    t = normalize(text)
    for k in keywords:
        if k in t:
            return True
    return False


def match_regex(text, patterns):
    t = normalize(text)
    for p in patterns:
        if re.search(p, t):
            return True
    return False


def categorize(taskname):
    t = normalize(taskname)
    if not t or t in ("a", "i", "u", "1"):
        return "Uncategorized"

    # 0) CSI division format: 11 (Equipment) and 12 (Furnishings) -> FF&E; rest -> Construction
    if re.search(r"^(11|12)\s*-\s*", t):
        return "FF&E + Millwork"
    if re.search(r"^\d{2}\s*-\s*", t) or re.search(r"\bdiv\s*\d+", t):
        return "Construction"
    # CSI-style with leading dash (e.g. "- 08 33 23 - INTERIOR COILING FIRE DOORS") -> Construction
    if re.search(r"^\s*-\s*\d{2}\s", t):
        return "Construction"

    # Percentage and contingency line items
    if t.startswith("%"):
        if "soft" in t:
            return "Soft Costs"
        return "Construction"
    if "contingency" in t:
        if "soft" in t or "design" in t:
            return "Soft Costs"
        if "ff&e" in t or "furniture" in t:
            return "FF&E + Millwork"
        return "Construction"
    if "allowance" in t:
        if "design" in t or "interior signage" in t:
            return "Soft Costs"
        if "furniture" in t or "ff&e" in t:
            return "FF&E + Millwork"
        return "Construction"

    # 1) FF&E + Millwork (check so "Furniture" doesn't get Construction)
    if match_keywords(taskname, FFE_KEYWORDS):
        return "FF&E + Millwork"
    if any(t == x or t.startswith(x) or (x in t and len(x) > 3) for x in FFE_EXACT):
        if "construction" in t and "furniture" not in t and "equipment" not in t:
            pass
        else:
            return "FF&E + Millwork"

    # 2) Soft Costs
    if match_keywords(taskname, SOFT_KEYWORDS):
        return "Soft Costs"
    if re.search(r"^(architect|design|engineering|a/e|mep design|design services)\b", t):
        return "Soft Costs"
    if re.search(r"\b(architect|designer|engineer|consultant|expeditor|permit|pm fee|jll)\b", t):
        return "Soft Costs"

    # 3) Construction
    if match_keywords(taskname, CONSTRUCTION_KEYWORDS):
        return "Construction"

    # Phase names
    if re.search(r"phase\s*[0-9]+", t) and "construction" not in t and "design" in t:
        return "Soft Costs"

    # "X% of Soft Cost" / "of Hard Cost" etc.
    if "of soft cost" in t or "of soft costs" in t or "per lease" in t:
        return "Soft Costs"
    if "of hard cost" in t or "of total project costs" in t:
        return "Construction"

    # Dollar amount / cost line (e.g. "$100,000.00") -> Construction
    if t.startswith("$"):
        return "Construction"
    # Numeric CSI-style with period (e.g. "08.7100 Doors / Frames") -> Construction
    if re.search(r"^\d+\.\d+", t):
        return "Construction"
    # Leading digits + space (e.g. "1 General Requirement", "10 Specialties") -> Construction
    if re.search(r"^\d+\s+\w", t):
        return "Construction"
    # (IT) / Information Technology -> FF&E
    if "(it)" in t or "information technology" in t:
        return "FF&E + Millwork"

    # Fallbacks
    if re.search(r"(fee|fees|mark-up|overall|increase|annual fee|administrat|admin\.? fee)\b", t):
        return "Soft Costs"
    if re.search(r"\b(gc|general contractor|general contradtor)\b", t) or t in ("building", "general"):
        return "Construction"
    if t in ("av", "it", "data") or "avi-spl" in t:
        return "FF&E + Millwork"
    if re.search(r"\b(asr|dd mechanical|dd structural|cdm)\b", t) or "civil" in t or "structural" in t or "mechanical" in t:
        if "contractor" in t or "install" in t:
            return "Construction"
        return "Soft Costs"
    if re.search(r"\b(electric|electrical|plumbing|hvac|heating|gas)\b", t):
        return "Construction"
    if "soft cost" in t or "general soft" in t:
        return "Soft Costs"
    if re.search(r"\b(assessment|survey|testing|inspection|due diligence|environmental|esa)\b", t):
        return "Soft Costs"
    if re.search(r"\b(compressor|pump|boiler|chiller|equipment)\b", t) and "furniture" not in t:
        return "Construction"
    if re.search(r"\b(additional|alternate|allowance|contingency|imprevistos)\b", t):
        return "Construction"
    if "furntiure" in t:
        return "FF&E + Millwork"

    return "Uncategorized"


def main():
    with open("INGENIOUS_BUDGETS_PROJECT_LEVEL.json") as f:
        data = json.load(f)
    items = data.get("budget_breakdown_by_item", [])
    tasknames = sorted(set(x.get("budgetitemdescription", "") for x in items))

    mapping = {}
    by_cat = {"FF&E + Millwork": [], "Soft Costs": [], "Construction": [], "Uncategorized": []}
    for name in tasknames:
        cat = categorize(name)
        mapping[name] = cat
        by_cat[cat].append(name)

    out = {
        "description": "Task name to budget category mapping for commercial real estate project/construction management",
        "categories": {
            "FF&E + Millwork": "Furniture, finishings, equipment and millwork; decorative materials; IT/security integrator; POS; storage shelving; owner-supplied items",
            "Soft Costs": "Designer, architect, engineers, expeditor, project management, special inspections, landmark consultant",
            "Construction": "General contractor and construction trade costs",
        },
        "taskname_to_category": mapping,
    }
    with open("budget_taskname_category_mapping.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # CSV for SQL/reporting (taskname,category)
    with open("budget_taskname_category_mapping.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["taskname", "category"])
        for name in tasknames:
            w.writerow([name, mapping[name]])

    summary = []
    for cat in ["FF&E + Millwork", "Soft Costs", "Construction", "Uncategorized"]:
        summary.append(f"## {cat}: {len(by_cat[cat])} task names")
    with open("budget_mapping_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n\n")
        f.write("--- Uncategorized (review these) ---\n")
        for n in by_cat["Uncategorized"][:200]:
            f.write(n + "\n")
        if len(by_cat["Uncategorized"]) > 200:
            f.write(f"... and {len(by_cat['Uncategorized']) - 200} more\n")

    print("Mapping written to budget_taskname_category_mapping.json and .csv")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
