import os
import json
import traceback
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def profile_agent(state: dict) -> dict:
    """
    Agent 1: Reads student message and extracts
    structured profile data using Gemini AI.
    """

    user_message = state.get("user_message", "")

    prompt = f"""
You are an expert admission counsellor for Maharashtra engineering colleges.

A student has typed the following message:
"{user_message}"

Extract the following information from this message.
If any field is not mentioned, set it to null.

Return ONLY a valid JSON object with these exact fields:
{{
    "percentile": <number or null>,
    "category": <one of: GOPENS, GOBCS, GSCS, GSTS, EWS, or null>,
    "district": <district name in Maharashtra or null>,
    "branches": <list of branch codes like ["CS","IT","AIML"] or null>,
    "budget": <annual fee in rupees as number or null>,
    "hostel_needed": <true or false or null>
}}

Category mapping rules:
- General / Open / No category → GOPENS
- OBC / Other Backward Class → GOBCS  
- SC / Scheduled Caste → GSCS
- ST / Scheduled Tribe → GSTS
- EWS / Economically Weaker → EWS

Branch code mapping:
- Computer / CS / Computer Engineering → CS
- IT / Information Technology → IT
- AI / AIML / Artificial Intelligence → AIML
- EXTC / Electronics → EXTC
- Mechanical → MECH
- Civil → CIVIL

Return ONLY the JSON. No explanation. No markdown.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=prompt
        )
        raw = response.text.strip()

        # Clean up if Gemini adds markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        profile = json.loads(raw)

        # Update state with extracted profile
        state["percentile"]    = profile.get("percentile")
        state["category"]      = profile.get("category")
        state["district"]      = profile.get("district")
        state["branches"]      = profile.get("branches")
        state["budget"]        = profile.get("budget")
        state["hostel_needed"] = profile.get("hostel_needed")

        print(f"[OK] Profile Agent extracted: {profile}")

    except Exception as e:
        print(f"[ERROR] Profile Agent error: {e}")
        print(traceback.format_exc())
        state["error"] = f"Could not understand your message. Please try again."

    return state