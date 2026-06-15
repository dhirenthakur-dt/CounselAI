import os
import json
import traceback
import re
from dotenv import load_dotenv
from groq import Groq
from agents.eligibility_agent import CITY_TO_DISTRICT, NEARBY_DISTRICTS

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
    if 'extc' in message.lower() or 'electronics' in message.lower() or 'entc' in message.lower():
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


def verify_district(user_message: str, llm_district: str) -> str:
    """
    Scan the original user message for known city/taluka names
    from CITY_TO_DISTRICT mapping. If found, return the city name
    so resolve_district() in eligibility_agent can map it correctly.
    This prevents LLM from misinterpreting cities like Shirpur → Nandurbar.
    """
    msg_lower = user_message.lower()

    # Sort by length descending so "navi mumbai" matches before "mumbai"
    sorted_cities = sorted(CITY_TO_DISTRICT.keys(), key=len, reverse=True)

    for city in sorted_cities:
        # Use word boundary check to avoid partial matches
        # e.g., "pune" should not match inside "impune"
        if re.search(r'\b' + re.escape(city) + r'\b', msg_lower):
            print(f"[OK] verify_district: Found city '{city}' in message, mapped to district '{CITY_TO_DISTRICT[city]}'")
            return city  # Return city name; resolve_district() will handle mapping

    # Also check direct district names from NEARBY_DISTRICTS
    for dist in NEARBY_DISTRICTS:
        if re.search(r'\b' + re.escape(dist) + r'\b', msg_lower):
            print(f"[OK] verify_district: Found district '{dist}' in message")
            return dist

    # Fallback to what the LLM extracted
    return llm_district


def normalize_profile(profile: dict, user_message: str = "") -> dict:
    """Normalize all profile fields to standard format."""
    
    # Normalize category
    if profile.get("category"):
        cat = profile["category"].upper().strip()
        category_map = {
            "OBC": "GOBCS", "GOBCS": "GOBCS",
            "OPEN": "GOPENS", "GENERAL": "GOPENS", 
            "GEN": "GOPENS", "GOPENS": "GOPENS",
            "SC": "GSCS", "GSCS": "GSCS",
            "ST": "GSTS", "GSTS": "GSTS",
            "EWS": "EWS",
        }
        profile["category"] = category_map.get(cat, cat)
    
    # Normalize district — verify against user message to fix LLM errors
    if profile.get("district") and user_message:
        profile["district"] = verify_district(user_message, profile["district"])
    elif user_message:
        # Even if LLM returned null for district, try to detect from message
        detected = verify_district(user_message, None)
        if detected:
            profile["district"] = detected
    
    if profile.get("district"):
        profile["district"] = profile["district"].strip().title()
    
    # Normalize branches (uppercase)
    if profile.get("branches"):
        branch_map = {
            "ENTC": "EXTC", "E&TC": "EXTC", "ETC": "EXTC",
            "ELECTRONICS": "EXTC", "ELECTRONICS AND TC": "EXTC",
            "CS": "CS", "CSE": "CS", "COMPUTER": "CS",
            "IT": "IT", "INFORMATION TECHNOLOGY": "IT",
            "AIML": "AIML", "AI": "AIML", "ML": "AIML",
            "MECH": "MECH", "MECHANICAL": "MECH",
            "CIVIL": "CIVIL",
            "ELEC": "ELEC", "ELECTRICAL": "ELEC",
            "DS": "DS", "DATA SCIENCE": "DS",
        }
        normalized = []
        for b in profile["branches"]:
            b_upper = b.upper().strip()
            normalized.append(branch_map.get(b_upper, b_upper))
        profile["branches"] = normalized
    
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
    "district": <the exact city or location text the student mentioned, or null>,
    "branches": <list of branch codes like ["CS","IT","AIML"] or null>,
    "budget": <annual fee in rupees as number or null>,
    "hostel_needed": <true or false or null>
}}

IMPORTANT for district field:
- Return the EXACT location/city/town name the student typed
- Do NOT convert city names to parent district names
- Example: if student says "Shirpur" return "Shirpur", NOT "Dhule"
- Example: if student says "Kalyan" return "Kalyan", NOT "Thane"

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
- EXTC / Electronics / ENTC / E&TC → EXTC
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
        profile = normalize_profile(profile, user_message)

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
            profile = normalize_profile(profile, user_message)
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