import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


def eligibility_agent(state: dict) -> dict:
    """
    Agent 2: Calls Java Spring Boot API to find
    eligible colleges based on student profile.
    """

    percentile = state.get("percentile")
    category   = state.get("category")

    if not percentile or not category:
        state["error"] = "Could not extract profile. Please try again."
        state["ranked_colleges"] = []
        return state

    try:
        # Map student category to all seat types
        category_map = {
            "GOPENS": ["GOPENS", "GOPENH", "GOPENO"],
            "GOBCS":  ["GOBCS",  "GOBCH",  "GOBCO"],
            "GSCS":   ["GSCS",   "GSCH",   "GSCO"],
            "GSTS":   ["GSTS",   "GSTH",   "GSTO"],
            "EWS":    ["EWS"],
            "TFWS":   ["TFWS"],
        }
        categories_to_check = category_map.get(category, [category])

        all_colleges = []
        seen_ids = set()

        for cat in categories_to_check:
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
                    key = (college.get("collegeId"), college.get("branchName"))
                    if key not in seen_ids:
                        seen_ids.add(key)
                        all_colleges.append(college)

        colleges = all_colleges

        # Filter by branch preference
        branches = state.get("branches")
        if branches:
            branches_lower = [b.lower() for b in branches]
            filtered = [
                c for c in colleges
                if any(b in c.get("branchName", "").lower()
                       for b in branches_lower)
            ]
            colleges = filtered if filtered else colleges

        # Filter by budget with 20% flexibility
        budget = state.get("budget")
        if budget:
            flexible_budget = budget * 1.2
            colleges = [
                c for c in colleges
                if c.get("annualFee") is None
                or c.get("annualFee") <= flexible_budget
            ]

        # Filter by hostel
        hostel_needed = state.get("hostel_needed")
        if hostel_needed:
            colleges = [
                c for c in colleges
                if c.get("hostelAvailable") is True
            ]

        state["ranked_colleges"] = colleges
        print(f"✅ Eligibility Agent found: {len(colleges)} colleges")

        else:
            state["error"] = "Could not fetch colleges from database."
            state["ranked_colleges"] = []

    except Exception as e:
        print(f"❌ Eligibility Agent error: {e}")
        state["error"] = "Database connection failed."
        state["ranked_colleges"] = []

    return state