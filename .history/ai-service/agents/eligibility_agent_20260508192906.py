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
# District Priority Mapping
# ─────────────────────────────────────────────
DISTRICT_PRIORITY = {
    "nashik": [
        "nashik",
        "pune",
        "ahmednagar",
        "aurangabad"
    ],

    "pune": [
        "pune",
        "mumbai",
        "satara",
        "ahmednagar"
    ],

    "mumbai": [
        "mumbai",
        "thane",
        "navi mumbai",
        "pune"
    ],
}

# Minimum colleges before fallback
MIN_RESULTS = 15


def eligibility_agent(state: dict) -> dict:
    """
    Agent 2: Finds eligible colleges based on profile.
    Supports:
    - Category seat type matching
    - Branch filtering
    - Budget filtering
    - Hostel filtering
    - District priority ranking
    """

    percentile = state.get("percentile")
    category   = state.get("category")

    if not percentile or not category:
        state["error"] = "Could not extract profile."
        state["ranked_colleges"] = []
        return state

    try:
        categories_to_check = CATEGORY_MAP.get(category, [category])

        all_colleges = []
        seen_keys = set()

        # ─────────────────────────────────────
        # Fetch colleges from backend
        # ─────────────────────────────────────
        for cat in categories_to_check:

            try:
                resp = requests.get(
                    f"{BACKEND_URL}/api/ranking/ranked-colleges",
                    params={
                        "percentile": percentile,
                        "category": cat,
                        "year": 2024,
                        "capRound": 1,
                        "priority": "general"
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
                print(f"⚠️ Category {cat} failed: {cat_error}")

        colleges = all_colleges

        print(f"📊 Total before filters: {len(colleges)}")

        # ─────────────────────────────────────
        # Branch filter
        # ─────────────────────────────────────
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

            if filtered:
                colleges = filtered

            print(f"📊 After branch filter: {len(colleges)}")

        # ─────────────────────────────────────
        # Budget filter
        # ─────────────────────────────────────
        budget = state.get("budget")

        if budget:

            flexible_budget = budget * 1.2

            colleges = [
                c for c in colleges
                if c.get("annualFee") is None
                or c.get("annualFee") <= flexible_budget
            ]

            print(f"📊 After budget filter: {len(colleges)}")

        # ─────────────────────────────────────
        # Hostel filter
        # ─────────────────────────────────────
        hostel_needed = state.get("hostel_needed")

        if hostel_needed:

            hostel_colleges = [
                c for c in colleges
                if c.get("hostelAvailable") is True
            ]

            if hostel_colleges:
                colleges = hostel_colleges

            print(f"📊 After hostel filter: {len(colleges)}")

        # ─────────────────────────────────────
        # DISTRICT PRIORITY FILTER
        # ─────────────────────────────────────
        preferred_district = state.get("district")

        if preferred_district:

            district_lower = preferred_district.lower()

            priority_list = DISTRICT_PRIORITY.get(
                district_lower,
                [district_lower]
            )

            same_district = []
            nearby_districts = []
            others = []

            for c in colleges:

                location = (
                    c.get("district", "") or
                    c.get("city", "") or
                    ""
                ).lower()

                # Priority 1 → Same district
                if priority_list[0] in location:
                    same_district.append(c)

                # Priority 2 → Nearby districts
                elif any(
                    d in location
                    for d in priority_list[1:]
                ):
                    nearby_districts.append(c)

                # Priority 3 → Rest of Maharashtra
                else:
                    others.append(c)

            final_ranked = []

            # Same district first
            final_ranked.extend(same_district)

            # Add nearby if not enough
            if len(final_ranked) < MIN_RESULTS:
                final_ranked.extend(nearby_districts)

            # Add remaining Maharashtra colleges
            if len(final_ranked) < MIN_RESULTS:
                final_ranked.extend(others)

            colleges = final_ranked

            print(f"📍 District priority applied:")
            print(f"   Same district: {len(same_district)}")
            print(f"   Nearby: {len(nearby_districts)}")
            print(f"   Others: {len(others)}")

        # ─────────────────────────────────────
        # Final result
        # ─────────────────────────────────────
        state["ranked_colleges"] = colleges

        print(f"✅ Final colleges: {len(colleges)}")

    except Exception as e:

        print(f"❌ Eligibility Agent error: {e}")

        state["error"] = "Database connection failed."
        state["ranked_colleges"] = []

    return state