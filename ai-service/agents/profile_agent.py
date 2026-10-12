import os
import json
import traceback
import re
from dotenv import load_dotenv
from groq import Groq
from agents.eligibility_agent import CITY_TO_DISTRICT, NEARBY_DISTRICTS

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=0)

# Primary and fallback models for Groq
GROQ_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]


def detect_query_language(message: str) -> str:
    """Detect if student query is in Hinglish (Hindi/Marathi in Roman script) or English."""
    hinglish_markers = [
        "hai", "mai", "me", "se", "hu", "hoon", "batao", "bataiye", "chahiye",
        "mila", "milega", "mil", "aaya", "kya", "kaise", "mera", "meri", "mere",
        "mujhe", "bhai", "hoga", "hogi", "konsa", "kaunsa", "kitna", "kitne",
        "wale", "wali", "karna", "lena", "admission", "chalega", "sath"
    ]
    msg_words = re.findall(r'\b[a-zA-Z]+\b', message.lower())
    match_count = sum(1 for w in msg_words if w in hinglish_markers)
    return "hinglish" if match_count >= 1 else "english"


def parse_profile_from_message(message: str) -> dict:
    """Hardened regex & heuristic parser for profile data when AI is unavailable."""
    profile = {
        "percentile": None,
        "category": None,
        "district": None,
        "branches": None,
        "budget": None,
        "hostel_needed": None,
        "query_language": detect_query_language(message)
    }

    msg_lower = message.lower()

    # 1. Extract percentile (handles: "97 percentile", "97.5 %ile", "97%", "97 pr", "97 mila", "score 97")
    pct_match = re.search(r'(\d{1,2}(?:\.\d+)?)\s*(?:percentile|%ile|%|pr|marks|mila|aaya|score|point)', msg_lower)
    if not pct_match:
        pct_match = re.search(r'(?:score|marks|percentile|cet\s*me|cet\s*mai)\s*(?:is|hai|of|me|mai)?\s*(\d{1,2}(?:\.\d+)?)', msg_lower)
    if pct_match:
        val = float(pct_match.group(1))
        if 0.0 <= val <= 100.0:
            profile["percentile"] = val

    # 2. Extract category with word boundaries (avoids 'st' matching 'best'/'hostel' and 'sc' matching 'science'/'score')
    if re.search(r'\b(obc|gobcs)\b', msg_lower):
        profile["category"] = "GOBCS"
    elif re.search(r'\b(ews)\b', msg_lower):
        profile["category"] = "EWS"
    elif re.search(r'\b(sc|gscs)\b', msg_lower) and not re.search(r'\b(score|science|scheme)\b', msg_lower):
        profile["category"] = "GSCS"
    elif re.search(r'\b(st|gsts)\b', msg_lower) and not re.search(r'\b(best|hostel|first|last|list|state)\b', msg_lower):
        profile["category"] = "GSTS"
    elif re.search(r'\b(open|general|gopens|gen)\b', msg_lower):
        profile["category"] = "GOPENS"
    else:
        profile["category"] = "GOPENS"

    # 3. Extract district
    districts = [
        "Mumbai", "Pune", "Nashik", "Nagpur", "Thane", "Aurangabad", "Solapur", "Kolhapur",
        "Sangli", "Satara", "Ahmednagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana",
        "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Latur",
        "Nanded", "Nandurbar", "Osmanabad", "Parbhani", "Raigad", "Ratnagiri", "Sindhudurg",
        "Wardha", "Washim", "Yavatmal"
    ]
    for district in districts:
        if re.search(r'\b' + re.escape(district.lower()) + r'\b', msg_lower):
            profile["district"] = district
            break

    # 4. Extract branches with word boundaries (strict: avoids 'ai' matching 'hai'/'mai'/'chahiye')
    branches = []
    if re.search(r'\b(cs|cse|computer|comp)\b', msg_lower):
        branches.append("CS")
    if re.search(r'\b(it|information\s*tech|information\s*technology)\b', msg_lower):
        branches.append("IT")
    if re.search(r'\b(aiml|ai\s*ml|artificial\s*intelligence|machine\s*learning)\b', msg_lower) or re.search(r'\bai\s*(?:branch|engineering|course)\b', msg_lower):
        branches.append("AIML")
    if re.search(r'\b(extc|entc|e&tc|electronics)\b', msg_lower):
        branches.append("EXTC")
    if re.search(r'\b(mech|mechanical)\b', msg_lower):
        branches.append("MECH")
    if re.search(r'\b(civil)\b', msg_lower):
        branches.append("CIVIL")
    if branches:
        profile["branches"] = branches

    # 5. Extract budget (handles: "budget 1 lakh", "fees 1.5 lac", "80k fees", "budget 150000")
    budget_match = re.search(r'(?:budget|fees?|fee)\s*(?:hai|me|tak|of|is)?\s*(?:rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(lakh|lac|k)?', msg_lower)
    if budget_match:
        val = float(budget_match.group(1))
        unit = (budget_match.group(2) or "").lower()
        if "lakh" in unit or "lac" in unit:
            profile["budget"] = int(val * 100000)
        elif "k" in unit:
            profile["budget"] = int(val * 1000)
        elif val <= 50:  # e.g., "budget 1" or "budget 2" implies lakh
            profile["budget"] = int(val * 100000)
        else:
            profile["budget"] = int(val)

    # 6. Extract hostel (handles: "hostel chahiye", "bina hostel ke", "hostel needed")
    if re.search(r'\b(no\s*hostel|hostel\s*nahi|hostel\s*not\s*needed|without\s*hostel)\b', msg_lower):
        profile["hostel_needed"] = False
    elif re.search(r'\b(hostel|need\s*hostel|hostel\s*chahiye|hostel\s*hona|hostel\s*required)\b', msg_lower):
        profile["hostel_needed"] = True

    return profile


def verify_district(user_message: str, llm_district: str) -> str:
    """
    Scan the original user message for known city/taluka names
    from CITY_TO_DISTRICT mapping. If found, return the city name
    so resolve_district() in eligibility_agent can map it correctly.
    """
    msg_lower = user_message.lower()

    # Sort by length descending so "navi mumbai" matches before "mumbai"
    sorted_cities = sorted(CITY_TO_DISTRICT.keys(), key=len, reverse=True)

    for city in sorted_cities:
        if re.search(r'\b' + re.escape(city) + r'\b', msg_lower):
            print(f"[OK] verify_district: Found city '{city}' in message, mapped to district '{CITY_TO_DISTRICT[city]}'")
            return city

    for dist in NEARBY_DISTRICTS:
        if re.search(r'\b' + re.escape(dist) + r'\b', msg_lower):
            print(f"[OK] verify_district: Found district '{dist}' in message")
            return dist

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
    
    # Normalize district
    if profile.get("district") and user_message:
        profile["district"] = verify_district(user_message, profile["district"])
    elif user_message:
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

    if not profile.get("query_language") and user_message:
        profile["query_language"] = detect_query_language(user_message)
    
    return profile


def profile_agent(state: dict) -> dict:
    """
    Agent 1: Reads student message (English or Hinglish) and extracts
    structured profile data using Groq AI with reliable fallback.
    """

    user_message = state.get("user_message", "")

    prompt = f"""You are an expert admission counsellor for Maharashtra engineering colleges (MHT-CET / CAP rounds).
Students communicate in English or Hinglish (Hindi / Marathi written in Roman script, e.g. 'mujhe cet mai 97 percentile hai', 'mera score 94.5 aaya', 'CS branch chahiye', 'pune me best college').

Student Message:
"{user_message}"

Extract the following information from this message.
If any field is not mentioned, set it to null.

Return ONLY a valid JSON object with these exact fields:
{{
    "percentile": <float number or null>,
    "category": <one of: GOPENS, GOBCS, GSCS, GSTS, EWS, or null>,
    "district": <the exact city or location text the student mentioned, or null>,
    "branches": <list of branch codes like ["CS","IT","AIML"] or null>,
    "budget": <annual fee in rupees as number or null>,
    "hostel_needed": <true or false or null>,
    "query_language": <"hinglish" or "english">
}}

Rules:
1. Category mapping:
   - General / Open / "open se hu" / "general category" / "khula pravarg" → GOPENS
   - OBC / "obc se hu" / "obc category" → GOBCS
   - SC / "sc category" → GSCS
   - ST / "st category" → GSTS
   - EWS / "ews category" / "ews certificate hai" → EWS
   - If not mentioned → GOPENS

2. Percentile:
   - Extract numbers from "97 percentile", "94.5 mila hai", "score 92", "88 aaya". Must be between 0 and 100.

3. District:
   - Return the EXACT city/town name the student typed (e.g. Pune, Mumbai, Nashik, Shirpur, Kalyan).
   - Do NOT convert city names to parent district names.

4. Branches:
   - CS / Computer / CSE → CS
   - IT / Information Technology → IT
   - AI / AIML / Artificial Intelligence → AIML
   - EXTC / Electronics / ENTC / E&TC → EXTC
   - Mechanical → MECH
   - Civil → CIVIL
   - CRITICAL: Do NOT confuse Hindi words like 'hai', 'mai', 'chahiye' with 'AI'! Only assign 'AIML' if the student specifically asks for AI/AIML.

5. Budget:
   - "1 lakh" → 100000, "1.5 lakh" → 150000, "80k" → 80000.

6. query_language:
   - Set to "hinglish" if the message uses Romanized Hindi/Marathi words like 'hai', 'mai', 'se', 'hu', 'chahiye', 'batao', 'kya', 'mera', 'mujhe'.
   - Otherwise "english".

Return ONLY raw JSON without markdown or backticks."""

    parsed_successfully = False
    for model_name in GROQ_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

            profile = json.loads(raw)
            profile = normalize_profile(profile, user_message)

            if profile.get("percentile") is not None:
                state["percentile"] = profile.get("percentile")
            if profile.get("category") is not None:
                state["category"] = profile.get("category")
            if profile.get("district") is not None:
                state["district"] = profile.get("district")
            if profile.get("branches") is not None:
                state["branches"] = profile.get("branches")
            if profile.get("budget") is not None:
                state["budget"] = profile.get("budget")
            if profile.get("hostel_needed") is not None:
                state["hostel_needed"] = profile.get("hostel_needed")
            if profile.get("query_language") is not None:
                state["query_language"] = profile.get("query_language")

            print(f"[OK] Profile Agent ({model_name}) extracted: {profile}")
            parsed_successfully = True
            break

        except Exception as e:
            print(f"[WARN] Profile Agent model {model_name} failed: {e}")
            continue

    if not parsed_successfully:
        print("[WARN] LLM models failed, parsing profile manually with regex")
        profile = parse_profile_from_message(user_message)
        profile = normalize_profile(profile, user_message)
        if profile.get("percentile") is not None:
            state["percentile"] = profile.get("percentile")
        if profile.get("category") is not None:
            state["category"] = profile.get("category")
        if profile.get("district") is not None:
            state["district"] = profile.get("district")
        if profile.get("branches") is not None:
            state["branches"] = profile.get("branches")
        if profile.get("budget") is not None:
            state["budget"] = profile.get("budget")
        if profile.get("hostel_needed") is not None:
            state["hostel_needed"] = profile.get("hostel_needed")
        if profile.get("query_language") is not None:
            state["query_language"] = profile.get("query_language")
        print(f"[OK] Profile Agent parsed manually: {profile}")

    # Fallback in case LLM succeeded but missed required fields
    if state.get("percentile") is None or state.get("category") is None:
        print("[WARN] Required fields missing, attempting manual parse")
        profile = parse_profile_from_message(user_message)
        profile = normalize_profile(profile, user_message)
        if profile.get("percentile") is not None and state.get("percentile") is None:
            state["percentile"] = profile.get("percentile")
        if profile.get("category") is not None and state.get("category") is None:
            state["category"] = profile.get("category")
        if profile.get("district") is not None and not state.get("district"):
            state["district"] = profile.get("district")
        if profile.get("branches") is not None and not state.get("branches"):
            state["branches"] = profile.get("branches")
        if profile.get("query_language") is not None and not state.get("query_language"):
            state["query_language"] = profile.get("query_language")
        
        # If still none, set error
        if state.get("percentile") is None or state.get("category") is None:
            state["error"] = "Could not understand your message. Please provide your percentile and category."

    return state