from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from agents.pipeline import pipeline
from agents.profile_agent import profile_agent, client, detect_query_language
from agents.live_search_agent import search_college_live

GROQ_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]

app = FastAPI(title="CounselAI - AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StudentMessage(BaseModel):
    message: str
    previous_profile: Optional[Dict[str, Any]] = None
    previous_colleges: Optional[List[Dict[str, Any]]] = None


class CollegeSearchRequest(BaseModel):
    college_name: str
    college_id: int


class FollowUpMessage(BaseModel):
    message: str
    previous_profile: Dict[str, Any]
    previous_colleges: List[Dict[str, Any]]


@app.get("/")
def root():
    return {"status": "CounselAI AI Service running", "version": "1.0"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-service", "port": 8001}


@app.post("/extract-profile")
def extract_profile(body: StudentMessage):
    state = {
        "user_message":    body.message,
        "percentile":      None,
        "category":        None,
        "district":        None,
        "branches":        None,
        "budget":          None,
        "hostel_needed":   None,
        "ranked_colleges": None,
        "strategy":        None,
        "documents":       None,
        "final_response":  None,
        "query_language":  None,
        "messages":        [],
        "error":           None
    }
    result = profile_agent(state)
    return {
        "percentile":     result.get("percentile"),
        "category":       result.get("category"),
        "district":       result.get("district"),
        "branches":       result.get("branches"),
        "budget":         result.get("budget"),
        "hostel_needed":  result.get("hostel_needed"),
        "query_language": result.get("query_language"),
        "error":          result.get("error")
    }


@app.post("/counsel")
def counsel_student(body: StudentMessage):
    prev_prof = body.previous_profile or {}
    
    initial_state = {
        "user_message":    body.message,
        "percentile":      prev_prof.get("percentile"),
        "category":        prev_prof.get("category"),
        "district":        prev_prof.get("district"),
        "branches":        prev_prof.get("branches"),
        "budget":          prev_prof.get("budget"),
        "hostel_needed":   prev_prof.get("hostel_needed"),
        "ranked_colleges": body.previous_colleges,
        "strategy":        None,
        "documents":       None,
        "final_response":  None,
        "query_language":  prev_prof.get("query_language"),
        "messages":        [],
        "error":           None
    }

    try:
        result = pipeline.invoke(initial_state)
    except Exception as e:
        return {
            "response": "Service temporarily unavailable. Please try again in 1 minute.",
            "profile":  {},
            "colleges": [],
            "strategy": None,
            "documents": None,
            "error":    str(e)
        }

    return {
        "response":  result.get("error") if result.get("error") else result.get("final_response"),
        "profile": {
            "percentile":     result.get("percentile"),
            "category":       result.get("category"),
            "district":       result.get("district"),
            "branches":       result.get("branches"),
            "budget":         result.get("budget"),
            "hostel_needed":  result.get("hostel_needed"),
            "query_language": result.get("query_language"),
        },
        "colleges":  result.get("ranked_colleges", [])[:10] if result.get("ranked_colleges") else [],
        "strategy":  result.get("strategy"),
        "documents": result.get("documents"),
        "error":     result.get("error")
    }


@app.post("/college/live-details")
def get_live_college_details(body: CollegeSearchRequest):
    return search_college_live(body.college_name)


@app.post("/follow-up")
def follow_up_question(body: FollowUpMessage):
    """Answers follow-up questions based on previous counseling context in Hinglish or English."""
    
    # Format the previous colleges into a readable string
    colleges_text = ""
    for i, c in enumerate(body.previous_colleges or []):
        colleges_text += f"{i+1}. {c.get('collegeName')} ({c.get('branchName')}) - Chance: {c.get('chance')}, Safety Margin: {c.get('safetyMargin')}%\n"
        
    profile = body.previous_profile or {}
    profile_text = f"Percentile: {profile.get('percentile')}, Category: {profile.get('category')}, Location: {profile.get('district')}"

    is_hinglish = detect_query_language(body.message) == "hinglish" or profile.get("query_language") == "hinglish"
    lang_inst = "Respond in natural, conversational Hinglish (Hindi in Roman script with English technical terms)." if is_hinglish else "Respond in clear, friendly English."

    prompt = f"""
You are an expert admission counsellor for Maharashtra engineering colleges (MHT-CET).
The user has asked a follow-up question regarding their previous counseling results.

User Profile: {profile_text}

Previously Recommended Colleges:
{colleges_text}

User's Follow-up Question: "{body.message}"

Language Instruction: {lang_inst}
Answer the user's question directly, concisely, and helpfully using the context provided above.
If the question is about a specific college from the list, reference its chance level or safety margin.
Use a friendly, encouraging tone. Format with basic markdown if helpful (bold, bullet points). Maximum 200 words.
"""

    for model_name in GROQ_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600
            )
            answer = response.choices[0].message.content.strip()
            return {
                "response": answer,
                "profile": body.previous_profile,
                "colleges": body.previous_colleges,
                "strategy": None,
                "documents": None,
                "error": None
            }
        except Exception as e:
            print(f"[WARN] Follow-up model {model_name} failed: {e}")
            continue

    return {
        "response": "I'm having trouble answering that follow-up right now. Could you please try again?",
        "profile": body.previous_profile,
        "colleges": body.previous_colleges,
        "error": "LLM error"
    }