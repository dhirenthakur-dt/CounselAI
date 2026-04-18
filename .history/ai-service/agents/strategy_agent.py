import os
import time
import logging
import traceback
from dotenv import load_dotenv
from google import genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS_TO_TRY = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]

MAX_RETRIES = 3


def generate_with_retry(prompt, model_name="gemini-2.0-flash-lite"):
    """Generate with exponential backoff retry."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response.text and len(response.text.strip()) > 0:
                return response.text.strip()
            raise ValueError("Empty response from Gemini")

        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    raise Exception("All retry attempts failed")


def strategy_agent(state: dict) -> dict:
    """
    Agent 3: Uses Gemini to generate CAP Round
    strategy based on ranked colleges.
    """

    colleges   = state.get("ranked_colleges") or []
    percentile = state.get("percentile")
    category   = state.get("category")

    if not colleges:
        state["strategy"] = "No eligible colleges found for your profile."
        logger.warning("No colleges provided to strategy agent")
        return state

    # Build college summary
    college_summary = ""
    for i, c in enumerate(colleges[:8], 1):
        college_summary += f"""
{i}. {c.get('collegeName')}
   Branch: {c.get('branchName')}
   Chance: {c.get('chance')}
   Safety Margin: {c.get('safetyMargin')}
   Score: {c.get('totalScore')}
   Fee: Rs {c.get('annualFee')}
   Hostel: {c.get('hostelAvailable')}
"""

    prompt = f"""
You are an expert MHT-CET admission counsellor for Maharashtra engineering colleges.

Student Profile:
- Percentile: {percentile}
- Category: {category}

Eligible colleges ranked by score:
{college_summary}

Give a clear CAP Round strategy in simple English. Include:

1. REACH colleges (Choice 1-2): Colleges where chance is LOW or borderline
2. TARGET colleges (Choice 3-6): Colleges where chance is MEDIUM or HIGH
3. SAFETY colleges (Choice 7-10): Colleges where safety margin is very high

4. ROUND 1 ADVICE: Should student lock seat in Round 1 or wait for Round 2?
   Rule: If top target college has HIGH chance → lock in Round 1
   Rule: If top target college has MEDIUM chance → wait for Round 2

5. ONE important tip specific to this student

Keep it SHORT and CLEAR. Use simple words.
Maximum 200 words total.
"""

    try:
        strategy_text = generate_with_retry(
            prompt, model_name="gemini-2.0-flash-lite"
        )
        state["strategy"] = strategy_text
        print(f"✅ Strategy Agent generated advice")

    except Exception as e:
        logger.error(f"Strategy Agent failed: {e}")
        state["strategy"] = "Strategy generation failed. Please check your colleges manually."

    return state