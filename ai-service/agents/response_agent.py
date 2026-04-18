import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def response_agent(state: dict) -> dict:
    """
    Agent 5: Combines all agent outputs into
    one clean final response for the student.
    """

    # Add None safety checks
    colleges  = state.get("ranked_colleges") or []
    strategy  = state.get("strategy") or "No strategy available."
    documents = state.get("documents") or {}
    percentile = state.get("percentile") or "Unknown"
    category   = state.get("category") or "Unknown"

    # Build top colleges text
    top_colleges = ""
    for i, c in enumerate(colleges[:5], 1):
        chance_emoji = "🟢" if c.get("chance") == "HIGH" else \
                       "🟡" if c.get("chance") == "MEDIUM" else "🔴"
        top_colleges += f"{i}. {c.get('collegeName')} — {c.get('branchName')} {chance_emoji}\n"
        top_colleges += f"   Fee: Rs {c.get('annualFee')} | Score: {c.get('totalScore')}\n"

    # Build document warnings text
    warnings = documents.get("warnings", [])
    warning_text = "\n".join(warnings) if warnings else "No critical warnings."

    prompt = f"""
Create a friendly, helpful response for an MHT-CET student.

Student: {percentile} percentile, {category} category

Top Colleges Found:
{top_colleges}

CAP Round Strategy:
{strategy}

Document Warnings:
{warning_text}

Write a complete response that includes:
1. A short encouraging opening line
2. Their top 5 colleges with chance level
3. The CAP Round strategy in 3-4 lines
4. Important document warning if any
5. A short encouraging closing line

Use simple English. Be friendly like a helpful senior student.
Use emojis sparingly. Maximum 300 words.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=prompt
        )
        state["final_response"] = response.text.strip()
        print("✅ Response Agent generated final response")

    except Exception as e:
        print(f"❌ Response Agent error: {e}")
        # Fallback plain response
        state["final_response"] = f"""
Here are your top colleges for {percentile} percentile ({category}):

{top_colleges}

Strategy: {strategy}

Documents warning: {warning_text}
"""

    return state