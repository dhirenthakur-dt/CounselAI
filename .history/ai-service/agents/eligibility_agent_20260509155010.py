import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

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

CATEGORY_MAP = {
    "GOPENS": ["GOPENS", "GOPENH", "GOPENO"],
    "GOBCS":  ["GOBCS",  "GOBCH",  "GOBCO"],
    "GSCS":   ["GSCS",   "GSCH",   "GSCO"],
    "GSTS":   ["GSTS",   "GSTH",   "GSTO"],
    "EWS":    ["EWS"],
    "TFWS":   ["TFWS"],
}

NEARBY_DISTRICTS = {
    "nashik":       ["nashik", "pune", "ahmednagar", "aurangabad", "jalgaon", "dhule"],
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
    "dhule":        ["dhule", "nashik", "jalgaon", "nandurbar","Shirpur"],
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


def eligibility_agent(state: dict) -> dict:
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

        # Branch filter
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

        # Budget filter
        budget = state.get("budget")
        if budget:
            flexible_budget = budget * 1.2
            colleges = [
                c for c in colleges
                if c.get("annualFee") is None or c.get("annualFee") <= flexible_budget
            ]
            print(f"After budget filter: {len(colleges)}")

        # Hostel filter
        hostel_needed = state.get("hostel_needed")
        if hostel_needed:
            hostel_colleges = [c for c in colleges if c.get("hostelAvailable") is True]
            if hostel_colleges:
                colleges = hostel_colleges
            print(f"After hostel filter: {len(colleges)}")

        # District priority filter
        preferred_district = state.get("district")
        if preferred_district and colleges:
            district_lower = preferred_district.lower().strip()

            nearby_list = NEARBY_DISTRICTS.get(district_lower)

            if not nearby_list:
                for key in NEARBY_DISTRICTS:
                    if key in district_lower or district_lower in key:
                        nearby_list = NEARBY_DISTRICTS[key]
                        break

            if not nearby_list:
                nearby_list = [district_lower]

            same_district   = []
            nearby_colleges = []
            other_colleges  = []

            for c in colleges:
                college_name     = (c.get("collegeName") or "").lower()
                college_district = (c.get("district") or "").lower()
                location_text    = college_name + " " + college_district

                if nearby_list[0] in location_text:
                    same_district.append(c)
                elif any(d in location_text for d in nearby_list[1:]):
                    nearby_colleges.append(c)
                else:
                    other_colleges.append(c)

            print(f"Same district ({nearby_list[0]}): {len(same_district)}")
            print(f"Nearby districts: {len(nearby_colleges)}")
            print(f"Rest Maharashtra: {len(other_colleges)}")

            final = []
            final.extend(same_district)
            if len(final) < MIN_RESULTS:
                final.extend(nearby_colleges)
            if len(final) < MIN_RESULTS:
                final.extend(other_colleges)

            colleges = final

        state["ranked_colleges"] = colleges
        print(f"Final colleges: {len(colleges)}")

    except Exception as e:
        print(f"Eligibility Agent error: {e}")
        import traceback
        traceback.print_exc()
        state["error"] = "Database connection failed."
        state["ranked_colleges"] = []

    return state