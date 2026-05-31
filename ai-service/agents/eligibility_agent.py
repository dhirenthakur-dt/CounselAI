import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

# ─────────────────────────────────────────────
# Branch keyword mapping
# ─────────────────────────────────────────────
BRANCH_KEYWORDS = {
    "cs":    ["computer science", "computer engineering", "cse"],
    "it":    ["information technology"],
    "aiml":  ["artificial intelligence", "machine learning"],
    "extc":  ["electronics", "telecommunication"],
    "mech":  ["mechanical"],
    "civil": ["civil"],
    "elec":  ["electrical"],
    "ds":    ["data science"],
}

# ─────────────────────────────────────────────
# Category seat type mapping
# ─────────────────────────────────────────────
CATEGORY_MAP = {
    "GOPENS": ["GOPENS", "GOPENH", "GOPENO"],
    "GOBCS":  ["GOBCS",  "GOBCH",  "GOBCO"],
    "GSCS":   ["GSCS",   "GSCH",   "GSCO"],
    "GSTS":   ["GSTS",   "GSTH",   "GSTO"],
    "EWS":    ["EWS"],
    "TFWS":   ["TFWS"],
}

# ─────────────────────────────────────────────
# City / Taluka → District mapping
# Students often type city names not district
# ─────────────────────────────────────────────
CITY_TO_DISTRICT = {
    # Dhule district
    "shirpur":      "dhule",
    "dhule":        "dhule",
    "sakri":        "dhule",
    "sindkheda":    "dhule",
    # Nashik district
    "nashik":       "nashik",
    "malegaon":     "nashik",
    "igatpuri":     "nashik",
    "trimbakeshwar":"nashik",
    "sinnar":       "nashik",
    "chandwad":     "nashik",
    "niphad":       "nashik",
    "deola":        "nashik",
    # Pune district
    "pune":         "pune",
    "pimpri":       "pune",
    "chinchwad":    "pune",
    "baramati":     "pune",
    "junnar":       "pune",
    "indapur":      "pune",
    "bhor":         "pune",
    "haveli":       "pune",
    "narhe":        "pune",
    "hadapsar":     "pune",
    "ambegaon":     "pune",
    "khed":         "pune",
    # Mumbai
    "mumbai":       "mumbai",
    "andheri":      "mumbai",
    "borivali":     "mumbai",
    "chembur":      "mumbai",
    "dadar":        "mumbai",
    "bandra":       "mumbai",
    # Thane
    "thane":        "thane",
    "kalyan":       "thane",
    "dombivli":     "thane",
    "ulhasnagar":   "thane",
    "ambernath":    "thane",
    "badlapur":     "thane",
    "bhiwandi":     "thane",
    "shahapur":     "thane",
    # Nagpur
    "nagpur":       "nagpur",
    "wardha":       "wardha",
    "yavatmal":     "yavatmal",
    "wani":         "yavatmal",
    "pusad":        "yavatmal",
    # Aurangabad (Sambhajinagar)
    "aurangabad":   "aurangabad",
    "sambhajinagar":"aurangabad",
    "jalna":        "jalna",
    "paithan":      "aurangabad",
    # Amravati
    "amravati":     "amravati",
    "achalpur":     "amravati",
    "badnera":      "amravati",
    # Kolhapur
    "kolhapur":     "kolhapur",
    "ichalkaranji": "kolhapur",
    "hatkanangale": "kolhapur",
    "kagal":        "kolhapur",
    # Sangli
    "sangli":       "sangli",
    "miraj":        "sangli",
    "ashta":        "sangli",
    # Solapur
    "solapur":      "solapur",
    "barshi":       "solapur",
    "akkalkot":     "solapur",
    # Nandurbar
    "nandurbar":    "nandurbar",
    "shahada":      "nandurbar",
    "taloda":       "nandurbar",
    # Jalgaon
    "jalgaon":      "jalgaon",
    "bhusawal":     "jalgaon",
    "pachora":      "jalgaon",
    "amalner":      "jalgaon",
    "chalisgaon":   "jalgaon",
    "chopda":       "jalgaon",
    # Akola
    "akola":        "akola",
    "washim":       "washim",
    "buldhana":     "buldhana",
    "shegaon":      "buldhana",
    "mehkar":       "buldhana",
    # Latur
    "latur":        "latur",
    "osmanabad":    "osmanabad",
    "nanded":       "nanded",
    "hingoli":      "hingoli",
    "parbhani":     "parbhani",
    "selu":         "parbhani",
    # Ahmednagar
    "ahmednagar":   "ahmednagar",
    "rahuri":       "ahmednagar",
    "kopargaon":    "ahmednagar",
    "shrirampur":   "ahmednagar",
    "sangamner":    "ahmednagar",
    # Satara
    "satara":       "satara",
    "karad":        "satara",
    "phaltan":      "satara",
    # Ratnagiri
    "ratnagiri":    "ratnagiri",
    "chiplun":      "ratnagiri",
    "khed":         "ratnagiri",
    # Palghar
    "palghar":      "palghar",
    "vasai":        "palghar",
    "virar":        "palghar",
    "boisar":       "palghar",
    "dahanu":       "palghar",
    # Raigad
    "raigad":       "raigad",
    "panvel":       "raigad",
    "alibag":       "raigad",
    "pen":          "raigad",
    "karjat":       "raigad",
    # Navi Mumbai
    "navi mumbai":  "thane",
    "vashi":        "thane",
    "nerul":        "thane",
    "belapur":      "thane",
    "kharghar":     "thane",
    # Chandrapur
    "chandrapur":   "chandrapur",
    "gadchiroli":   "gadchiroli",
    "gondia":       "gondia",
    "bhandara":     "bhandara",
    # Beed
    "beed":         "beed",
    "ambajogai":    "beed",
    # Sindhudurg
    "sindhudurg":   "sindhudurg",
    "kudal":        "sindhudurg",
    "sawantwadi":   "sindhudurg",
}

# ─────────────────────────────────────────────
# District → nearby districts (priority order)
# ─────────────────────────────────────────────
NEARBY_DISTRICTS = {
    "nashik":       ["nashik", "dhule", "pune", "ahmednagar", "aurangabad", "jalgaon", "nandurbar"],
    "dhule":        ["dhule", "nashik", "nandurbar", "jalgaon", "ahmednagar"],
    "pune":         ["pune", "mumbai", "satara", "ahmednagar", "solapur", "kolhapur", "nashik"],
    "mumbai":       ["mumbai", "thane", "palghar", "raigad", "pune"],
    "thane":        ["thane", "mumbai", "palghar", "raigad", "nashik"],
    "nagpur":       ["nagpur", "wardha", "amravati", "yavatmal", "chandrapur", "bhandara", "gondia"],
    "aurangabad":   ["aurangabad", "jalna", "beed", "osmanabad", "nanded", "parbhani", "nashik"],
    "amravati":     ["amravati", "nagpur", "wardha", "yavatmal", "akola", "buldhana", "washim"],
    "solapur":      ["solapur", "pune", "satara", "osmanabad", "latur", "ahmednagar"],
    "kolhapur":     ["kolhapur", "sangli", "satara", "pune", "ratnagiri", "sindhudurg"],
    "sangli":       ["sangli", "kolhapur", "satara", "pune", "solapur"],
    "satara":       ["satara", "pune", "kolhapur", "sangli", "solapur"],
    "jalgaon":      ["jalgaon", "nashik", "dhule", "nandurbar", "aurangabad", "buldhana"],
    "latur":        ["latur", "osmanabad", "solapur", "nanded", "beed"],
    "nanded":       ["nanded", "latur", "aurangabad", "osmanabad", "parbhani", "hingoli"],
    "ahmednagar":   ["ahmednagar", "pune", "nashik", "aurangabad", "beed", "solapur"],
    "akola":        ["akola", "amravati", "buldhana", "washim", "yavatmal"],
    "buldhana":     ["buldhana", "akola", "jalgaon", "amravati", "washim"],
    "yavatmal":     ["yavatmal", "amravati", "nanded", "nagpur", "wardha", "washim"],
    "wardha":       ["wardha", "nagpur", "amravati", "yavatmal", "chandrapur"],
    "chandrapur":   ["chandrapur", "nagpur", "wardha", "yavatmal", "gadchiroli"],
    "ratnagiri":    ["ratnagiri", "sindhudurg", "kolhapur", "satara", "raigad"],
    "sindhudurg":   ["sindhudurg", "ratnagiri", "kolhapur"],
    "raigad":       ["raigad", "mumbai", "pune", "thane", "ratnagiri"],
    "palghar":      ["palghar", "thane", "mumbai", "nashik"],
    "nandurbar":    ["nandurbar", "dhule", "jalgaon", "nashik"],
    "beed":         ["beed", "aurangabad", "ahmednagar", "osmanabad", "latur"],
    "osmanabad":    ["osmanabad", "latur", "solapur", "beed", "nanded"],
    "parbhani":     ["parbhani", "nanded", "aurangabad", "hingoli", "latur"],
    "hingoli":      ["hingoli", "nanded", "parbhani", "aurangabad", "washim"],
    "washim":       ["washim", "akola", "amravati", "yavatmal", "buldhana", "hingoli"],
    "jalna":        ["jalna", "aurangabad", "beed", "parbhani"],
    "gondia":       ["gondia", "nagpur", "bhandara", "gadchiroli"],
    "bhandara":     ["bhandara", "nagpur", "gondia", "chandrapur"],
    "gadchiroli":   ["gadchiroli", "chandrapur", "nagpur", "yavatmal"],
}

MIN_RESULTS = 10


def resolve_district(user_input):
    """
    Convert city/taluka name to district name.
    Also handles misspellings with partial match.
    Returns (district_name, search_terms)
    """
    inp = user_input.lower().strip()

    # Direct city match
    if inp in CITY_TO_DISTRICT:
        district = CITY_TO_DISTRICT[inp]
        # Return both city name and district name as search terms
        return district, [inp, district]

    # Direct district match
    if inp in NEARBY_DISTRICTS:
        return inp, [inp]

    # Partial match in city map
    for city, district in CITY_TO_DISTRICT.items():
        if city in inp or inp in city:
            return district, [city, district, inp]

    # Partial match in district map
    for dist in NEARBY_DISTRICTS:
        if dist in inp or inp in dist:
            return dist, [dist, inp]

    # No match — use as-is
    return inp, [inp]


def eligibility_agent(state: dict) -> dict:
    """
    Agent 2: Finds eligible colleges based on student profile.
    - Checks all seat types (State + Home + Other University)
    - Filters by branch, budget, hostel
    - Prioritizes colleges by city/district proximity
    - Handles city names like Shirpur, Ichalkaranji etc.
    """

    percentile = state.get("percentile")
    category   = state.get("category")

    if not percentile or not category:
        state["error"] = "Could not extract profile. Please try again."
        state["ranked_colleges"] = []
        return state

    try:
        categories_to_check = CATEGORY_MAP.get(category, [category])
        all_colleges = []
        seen_keys    = set()

        # ── Fetch from all seat type categories ──────────────────
        for cat in categories_to_check:
            try:
                resp = requests.get(
                    f"{BACKEND_URL}/api/ranking/ranked-colleges",
                    params={
                        "percentile": percentile,
                        "category":   cat,
                        "year":       2024,
                        "capRound":   1,
                        "priority":   "general"
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    for college in resp.json():
                        key = (college.get("collegeId"), college.get("branchName"))
                        if key not in seen_keys:
                            seen_keys.add(key)
                            all_colleges.append(college)
            except Exception as cat_error:
                print(f"Warning: Category {cat} failed: {cat_error}")

        colleges = all_colleges
        print(f"Total before filters: {len(colleges)}")

        # ── Branch filter ─────────────────────────────────────────
        branches = state.get("branches")
        if branches:
            keywords = []
            for b in branches:
                b_lower = b.lower()
                if b_lower in BRANCH_KEYWORDS:
                    keywords.extend(BRANCH_KEYWORDS[b_lower])
                else:
                    keywords.append(b_lower)
            filtered = [
                c for c in colleges
                if any(kw in c.get("branchName", "").lower() for kw in keywords)
            ]
            if filtered:
                colleges = filtered
            print(f"After branch filter: {len(colleges)}")

        # ── Budget filter ─────────────────────────────────────────
        budget = state.get("budget")
        if budget:
            flexible_budget = budget * 1.2
            colleges = [
                c for c in colleges
                if c.get("annualFee") is None or c.get("annualFee") <= flexible_budget
            ]
            print(f"After budget filter: {len(colleges)}")

        # ── Hostel filter ─────────────────────────────────────────
        hostel_needed = state.get("hostel_needed")
        if hostel_needed:
            hostel_colleges = [c for c in colleges if c.get("hostelAvailable") is True]
            if hostel_colleges:
                colleges = hostel_colleges
            print(f"After hostel filter: {len(colleges)}")

        # ── District/City priority filter ─────────────────────────
        preferred_location = state.get("district")

        if preferred_location and colleges:

            # Resolve city → district + get all search terms
            district, search_terms = resolve_district(preferred_location)

            # Get nearby districts
            nearby_list = NEARBY_DISTRICTS.get(district, [district])

            # All terms to check for "same location"
            # Includes city name + district name
            same_terms = search_terms + [district]

            print(f"Location: '{preferred_location}' -> district: '{district}'")
            print(f"Search terms: {same_terms}")
            print(f"Nearby: {nearby_list[:4]}")

            same_location   = []
            nearby_colleges = []
            other_colleges  = []

            for c in colleges:
                college_name     = (c.get("collegeName") or "").lower()
                college_district = (c.get("district") or "").lower()
                location_text    = college_name + " " + college_district

                # Priority 1 — Same city OR same district
                if any(term in location_text for term in same_terms):
                    same_location.append(c)

                # Priority 2 — Nearby districts
                elif any(d in location_text for d in nearby_list[1:]):
                    nearby_colleges.append(c)

                # Priority 3 — Rest of Maharashtra
                else:
                    other_colleges.append(c)

            print(f"Same location ({preferred_location}): {len(same_location)}")
            print(f"Nearby districts: {len(nearby_colleges)}")
            print(f"Rest Maharashtra: {len(other_colleges)}")

            final = []
            final.extend(same_location)
            if len(final) < MIN_RESULTS:
                final.extend(nearby_colleges)
            if len(final) < MIN_RESULTS:
                final.extend(other_colleges)

            colleges = final

        # ── Final result ──────────────────────────────────────────
        state["ranked_colleges"] = colleges
        print(f"Final colleges: {len(colleges)}")

    except Exception as e:
        print(f"Eligibility Agent error: {e}")
        import traceback
        traceback.print_exc()
        state["error"] = "Database connection failed."
        state["ranked_colleges"] = []

    return state