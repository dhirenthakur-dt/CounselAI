import os
import json
import traceback
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def parse_profile_from_message(message: str) -> dict:
    """Simple parser for profile data when AI quota is exceeded."""
    profile = {
        "percentile": None,
        "category": None,
        "district": None,
        "branches": None,
        "budget": None,
        "hostel_needed": None
    }

    # Extract percentile
    percentile_match = re.search(r'(\d+(?:\.\d+)?)\s*percentile', message, re.IGNORECASE)
    if percentile_match:
        profile["percentile"] = float(percentile_match.group(1))

    # Extract category
    if 'obc' in message.lower():
        profile["category"] = "GOBCS"
    elif 'sc' in message.lower():
        profile["category"] = "GSCS"
    elif 'st' in message.lower():
        profile["category"] = "GSTS"
    elif 'ews' in message.lower():
        profile["category"] = "EWS"
    else:
        profile["category"] = "GOPENS"  # default

    # Extract district
    districts = ["Mumbai", "Pune", "Nashik", "Nagpur", "Thane", "Aurangabad", "Solapur", "Kolhapur", "Sangli", "Satara", "Ahmednagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Latur", "Nanded", "Nandurbar", "Osmanabad", "Parbhani", "Raigad", "Ratnagiri", "Sindhudurg", "Wardha", "Washim", "Yavatmal"]
    for district in districts:
        if district.lower() in message.lower():
            profile["district"] = district
            break

    # Extract branches
    branches = []
    if 'cs' in message.lower() or 'computer' in message.lower():
        branches.append("CS")
    if 'it' in message.lower() or 'information' in message.lower():
        branches.append("IT")
    if 'ai' in message.lower() or 'aiml' in message.lower():
        branches.append("AIML")
    if 'extc' in message.lower() or 'electronics' in message.lower():
        branches.append("EXTC")
    if 'mech' in message.lower() or 'mechanical' in message.lower():
        branches.append("MECH")
    if 'civil' in message.lower():
        branches.append("CIVIL")
    if branches:
        profile["branches"] = branches

    # Extract budget
    budget_match = re.search(r'budget\s*(\d+)', message, re.IGNORECASE)
    if budget_match:
        profile["budget"] = int(budget_match.group(1))

    # Extract hostel
    if 'hostel' in message.lower() or 'need hostel' in message.lower():
        profile["hostel_needed"] = True
    elif 'no hostel' in message.lower():
        profile["hostel_needed"] = False

    return profile


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
- General / Open / No category mentioned → GOPENS
- OBC / Other Backward Class → GOBCS
- SC / Scheduled Caste → GSCS
- ST / Scheduled Tribe → GSTS
- EWS / Economically Weaker Section → EWS

Branch code mapping:
- Computer / CS / Computer Engineering → CS
- IT / Information Technology → IT
- AI / AIML / Artificial Intelligence → AIML
- EXTC / Electronics → EXTC
- Mechanical → MECH
- Civil → CIVIL

Return ONLY the JSON. No explanation. No markdown. No backticks.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        raw = response.choices[0].message.content.strip()

        profile = json.loads(raw)

        state["percentile"]    = profile.get("percentile")
        state["category"]      = profile.get("category")
        state["district"]      = profile.get("district")
        state["branches"]      = profile.get("branches")
        state["budget"]        = profile.get("budget")
        state["hostel_needed"] = profile.get("hostel_needed")

        print(f"[OK] Profile Agent extracted: {profile}")

    except Exception as e:
        print(f"[ERROR] Profile Agent error: {e}")
        # Check if it's a quota exceeded error
        if "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
            # Fallback to parsing the message manually
            print("[WARN] Quota exceeded, parsing profile manually")
            profile = parse_profile_from_message(user_message)
            state["percentile"]    = profile.get("percentile")
            state["category"]      = profile.get("category")
            state["district"]      = profile.get("district")
            state["branches"]      = profile.get("branches")
            state["budget"]        = profile.get("budget")
            state["hostel_needed"] = profile.get("hostel_needed")
            print(f"[OK] Profile Agent parsed manually: {profile}")
        else:
            state["error"] = "Could not understand your message. Please try again."

    return state