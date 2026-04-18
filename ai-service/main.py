from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.pipeline import pipeline

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
    return {"status": "CounselAI AI Service running"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-service"}


@app.post("/extract-profile")
def extract_profile(body: StudentMessage):
    """
    Profile extraction endpoint. Takes student message →
    runs profile agent only → returns extracted profile data.
    """

    # Initial state for profile extraction only
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

    # Run only the profile agent
    from agents.profile_agent import profile_agent
    result = profile_agent(initial_state)

    # Return clean profile response
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
    """
    Main endpoint. Takes student message →
    runs all 5 agents → returns complete response.
    """

    # Initial state
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

    # Run pipeline
    try:
        result = pipeline.invoke(initial_state)
    except Exception as e:
        return {
            "response": "Service temporarily unavailable. Please try again in 1 minute.",
            "profile": {},
            "colleges": [],
            "strategy": None,
            "documents": None,
            "error": str(e)
        }

    # Return clean response
    return {
        "response":    result.get("final_response"),
        "profile": {
            "percentile":    result.get("percentile"),
            "category":      result.get("category"),
            "district":      result.get("district"),
            "branches":      result.get("branches"),
            "budget":        result.get("budget"),
            "hostel_needed": result.get("hostel_needed"),
        },
        "colleges":   result.get("ranked_colleges", [])[:5],
        "strategy":   result.get("strategy"),
        "documents":  result.get("documents"),
        "error":      result.get("error")
    }