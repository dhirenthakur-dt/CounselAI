import os
import time
import logging
import traceback
from dotenv import load_dotenv
from google import genai
from google.api_core.exceptions import ResourceExhausted, NotFound

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required")

client = genai.Client(api_key=api_key)

# Updated with working model names based on test_gemini.py results
MODELS_TO_TRY = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds


def generate_with_retry(prompt, model_name='gemini-2.0-flash-lite', max_retries=MAX_RETRIES):
    """Generate content with exponential backoff retry logic for rate limits only."""
    last_error = None

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} to generate content with model {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            # Check if response has text
            if not response.text or len(response.text.strip()) == 0:
                raise ValueError("Empty response from Gemini API")

            return response.text.strip()

        except ResourceExhausted as e:
            last_error = e
            logger.warning(f"Rate limit (ResourceExhausted) on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                delay = INITIAL_RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.info(f"Rate limit detected, retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            else:
                raise

        except NotFound as e:
            # Model not found - don't retry, this is a configuration issue
            logger.error(f"Model not found (404): {e}")
            raise

        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed with unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(INITIAL_RETRY_DELAY)
                continue
            else:
                raise

    raise last_error if last_error else Exception("Unknown error in retry loop")


def strategy_agent(state: dict) -> dict:
    """
    Agent 3: Uses Gemini to generate CAP Round
    strategy based on ranked colleges.
    """

    colleges = state.get("ranked_colleges", [])
    percentile = state.get("percentile")
    category = state.get("category")

    if not colleges:
        state["strategy"] = "No eligible colleges found for your profile."
        logger.warning("No colleges provided to strategy agent")
        return state

    # Build college summary for Gemini (limit to 8 colleges to control prompt length)
    college_summary = ""
    for i, c in enumerate(colleges[:8], 1):
        college_summary += f"""{i}. {c.get('collegeName')}
   Branch: {c.get('branchName')}
   Chance: {c.get('chance')}
   Safety Margin: {c.get('safetyMargin')}
   Score: {c.get('totalScore')}
   Fee: Rs {c.get('annualFee')}
   Hostel: {c.get('hostelAvailable')}
"""

    prompt = f"""You are an expert MHT-CET admission counsellor for Maharashtra engineering colleges.

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
No bullet points inside advice. Write in paragraph style.
Maximum 200 words total.
"""

    logger.info(f"Strategy Agent: Processing {len(colleges)} college(s)")
    logger.info(f"Prompt length: {len(prompt)} characters")

    try:
        # Generate with retry using primary model
        strategy_text = generate_with_retry(prompt, model_name='gemini-2.0-flash-lite')

        state["strategy"] = strategy_text
        logger.info("Strategy Agent generated advice successfully")
        print(f"[OK] Strategy generated ({len(strategy_text)} characters)")

    except ResourceExhausted as e:
        error_msg = f"Gemini API rate limit exceeded: {e}"
        logger.error(error_msg)
        print(f"[ERROR] {error_msg}")
        state["strategy"] = "API quota exceeded. Please try again later."
        state["error"] = error_msg

    except NotFound as e:
        error_msg = f"Gemini model not found: {e}"
        logger.error(error_msg)
        print(f"[ERROR] {error_msg}")
        state["strategy"] = "AI model unavailable. Please contact support."
        state["error"] = error_msg

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Strategy Agent failed:\n{error_details}")
        print(f"[ERROR] Strategy generation failed: {e}")
        state["strategy"] = "Strategy generation failed. Please check your colleges manually."
        state["error"] = str(e)

    return state
