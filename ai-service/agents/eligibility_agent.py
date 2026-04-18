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

    # Add None safety checks for when profile_agent fails
    percentile = state.get("percentile")
    category = state.get("category")
    if not percentile or not category:
        state["error"] = "Could not extract profile. Please try again."
        state["ranked_colleges"] = []
        return state

    # Validation
    if not percentile or not category:
        state["error"] = "Percentile and category are required."
        return state

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/ranking/ranked-colleges",
            params={
                "percentile": percentile,
                "category":   category,
                "year":       2024,
                "capRound":   1,
                "priority":   "general"
            },
            timeout=10
        )

        if response.status_code == 200:
            colleges = response.json()

            # Filter by branch preference if student mentioned it
            branches = state.get("branches")
            if branches:
                branches_lower = [b.lower() for b in branches]
                filtered = []
                for c in colleges:
                    branch_name = c.get("branchName", "").lower()
                    if any(b in branch_name for b in branches_lower):
                        filtered.append(c)
                colleges = filtered if filtered else colleges

            # Filter by budget — allow 20% flexibility
            budget = state.get("budget")
            if budget:
                flexible_budget = budget * 1.2  # 20% flexibility
                colleges = [
                    c for c in colleges
                    if c.get("annualFee") is None
                    or c.get("annualFee") <= flexible_budget
                ]

            # Filter by hostel if student needs it
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

    except Exception as e:
        print(f"❌ Eligibility Agent error: {e}")
        state["error"] = "Database connection failed."

    return state