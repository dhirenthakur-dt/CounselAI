import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


def document_agent(state: dict) -> dict:
    """
    Agent 4: Fetches document checklist for
    student category from Spring Boot API.
    """

    category = state.get("category", "GOPENS")

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/documents/checklist",
            params={"category": category},
            timeout=10
        )

        if response.status_code == 200:
            state["documents"] = response.json()
            print(f"✅ Document Agent fetched checklist for {category}")
        else:
            state["documents"] = {"error": "Could not fetch documents"}

    except Exception as e:
        print(f"❌ Document Agent error: {e}")
        state["documents"] = {"error": "Document service unavailable"}

    return state