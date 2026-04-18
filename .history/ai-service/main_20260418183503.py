from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.pipeline import pipeline
from agents.profile_agent import profile_agent

app = FastAPI(title="CounselAI - AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StudentMessage(BaseModel):
    message: str


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
        "response":  result.get("final_response"),
        "profile": {
            "percentile":    result.get("percentile"),
            "category":      result.get("category"),
            "district":      result.get("district"),
            "branches":      result.get("branches"),
            "budget":        result.get("budget"),
            "hostel_needed": result.get("hostel_needed"),
        },
        "colleges":  result.get("ranked_colleges", [])[:5],
        "strategy":  result.get("strategy"),
        "documents": result.get("documents"),
        "error":     result.get("error")
    }