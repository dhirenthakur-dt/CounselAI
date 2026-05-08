import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

# Branch keyword mapping
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

# Category seat type mapping
CATEGORY_MAP = {
    "GOPENS": ["GOPENS", "GOPENH", "GOPENO"],
    "GOBCS":  ["GOBCS",  "GOBCH",  "GOBCO"],
    "GSCS":   ["GSCS",   "GSCH",   "GSCO"],
    "GSTS":   ["GSTS",   "GSTH",   "GSTO"],
    "EWS":    ["EWS"],
    "TFWS":   ["TFWS"],
}


def eligibility_agent(state: dict) -> dict:
    """
    Agent 2: Calls Java Spring Boot API to find
    eligible colleges based on student profile.
    Checks all seat types (State + Home + Other University).
    """

    percentile = state.get("percentile")
    category   = state.get("category")

    if not percentile or not category:
        state["error"] = "Could not extract profile. Please try again."
        state["ranked_colleges"] = []
        return state

    try:
        # Get all seat type categories for this student
        categories_to_check = CATEGORY_MAP.get(category, [category])

        all_colleges = []
        seen_keys    = set()

        # Query each category separately and combine
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
                        key = (
                            college.get("collegeId"),
                            college.get("branchName")
                        )
                        if key not in seen_keys:
                            seen_keys.add(key)
                            all_colleges.append(college)
            except Exception as cat_error:
                print(f"⚠️  Category {cat} query failed: {cat_error}")
                continue

        colleges = all_colleges
        print(f"📊 Total before filters: {len(colleges)} colleges")

        # ── Filter by branch preference ──────────────────────────
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
                if any(
                    kw in c.get("branchName", "").lower()
                    for kw in keywords
                )
            ]
            # If filter removes everything keep all
            colleges = filtered if filtered else colleges
            print(f"📊 After branch filter: {len(colleges)} colleges")

        # ── Filter by budget with 20% flexibility ────────────────
        budget = state.get("budget")
        if budget:
            flexible_budget = budget * 1.2
            colleges = [
                c for c in colleges
                if c.get("annualFee") is None
                or c.get("annualFee") <= flexible_budget
            ]
            print(f"📊 After budget filter: {len(colleges)} colleges")

        # ── Filter by hostel ──────────────────────────────────────
        hostel_needed = state.get("hostel_needed")
        if hostel_needed:
            has_hostel = [
                c for c in colleges
                if c.get("hostelAvailable") is True
            ]
            # Only apply if some colleges have hostel data
            # Otherwise keep all (hostel data may be missing)
            if has_hostel:
                colleges = has_hostel
            print(f"📊 After hostel filter: {len(colleges)} colleges")

        state["ranked_colleges"] = colleges
        print(f"✅ Eligibility Agent found: {len(colleges)} colleges")

    except Exception as e:
        print(f"❌ Eligibility Agent error: {e}")
        state["error"] = "Database connection failed."
        state["ranked_colleges"] = []

    return state