from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from agents.pipeline import pipeline
from agents.profile_agent import profile_agent, client
from agents.live_search_agent import search_college_live

app = FastAPI(title="CounselAI - AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StudentMessage(BaseModel):
    message: str


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
        "messages":        [],
        "error":           None
    }
    result = profile_agent(state)
    return {
        "percentile":    result.get("percentile"),
        "category":      result.get("category"),
        "district":      result.get("district"),
        "branches":      result.get("branches"),
        "budget":        result.get("budget"),
        "hostel_needed": result.get("hostel_needed"),
        "error":         result.get("error")
    }


@app.post("/counsel")
def counsel_student(body: StudentMessage):
    initial_state = {
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
            "percentile":    result.get("percentile"),
            "category":      result.get("category"),
            "district":      result.get("district"),
            "branches":      result.get("branches"),
            "budget":        result.get("budget"),
            "hostel_needed": result.get("hostel_needed"),
        },
        "colleges":  result.get("ranked_colleges", [])[:10],
        "strategy":  result.get("strategy"),
        "documents": result.get("documents"),
        "error":     result.get("error")
    }


@app.post("/college/live-details")
def get_live_college_details(body: CollegeSearchRequest):
    return search_college_live(body.college_name)


@app.post("/follow-up")
def follow_up_question(body: FollowUpMessage):
    """Answers follow-up questions based on previous counseling context."""
    
    # Format the previous colleges into a readable string
    colleges_text = ""
    for i, c in enumerate(body.previous_colleges):
        colleges_text += f"{i+1}. {c.get('collegeName')} ({c.get('branchName')}) - Chance: {c.get('chance')}, Safety Margin: {c.get('safetyMargin')}%\n"
        
    profile = body.previous_profile
    profile_text = f"Percentile: {profile.get('percentile')}, Category: {profile.get('category')}, Location: {profile.get('district')}"

    prompt = f"""
You are an expert admission counsellor for Maharashtra engineering colleges.
The user has asked a follow-up question regarding their previous counseling results.

User Profile: {profile_text}

Previously Recommended Colleges:
{colleges_text}

User's Follow-up Question: "{body.message}"

Answer the user's question directly, concisely, and helpfully using ONLY the context provided above. 
Do not make up information. If the question is about a specific college from the list, reference its chance level or safety margin.
Use a friendly, encouraging tone. Format with basic markdown if helpful (bold, bullet points).
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
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
        return {
            "response": "I'm having trouble answering that follow-up right now. Could you try asking again?",
            "profile": body.previous_profile,
            "colleges": body.previous_colleges,
            "error": str(e)
        }
