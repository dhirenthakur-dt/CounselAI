import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def response_agent(state: dict) -> dict:
    """
    Agent 5: Combines all agent outputs into
    one clean final response for the student.
    """

    colleges   = state.get("ranked_colleges") or []
    strategy   = state.get("strategy") or "No strategy available."
    documents  = state.get("documents") or {}
    percentile = state.get("percentile") or "Unknown"
    category   = state.get("category") or "Unknown"

    # Build college text
    top_colleges = ""
    for i, c in enumerate(colleges[:5], 1):
        emoji = "🟢" if c.get("chance") == "HIGH" else \
                "🟡" if c.get("chance") == "MEDIUM" else "🔴"
        top_colleges += (
            f"{i}. {c.get('collegeName')} — "
            f"{c.get('branchName')} {emoji}\n"
            f"   Fee: Rs {c.get('annualFee')} | "
            f"Score: {c.get('totalScore')}\n"
        )

    warnings     = documents.get("warnings", [])
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
2. Their top colleges with chance level
3. The CAP Round strategy in 3-4 lines
4. Important document warning if any
5. A short encouraging closing line

Use simple English. Be friendly. Maximum 300 words.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600
        )
        state["final_response"] = response.choices[0].message.content.strip()
        print("✅ Response Agent generated final response")

    except Exception as e:
        print(f"❌ Response Agent error: {e}")
        state["final_response"] = (
            f"Here are your top colleges for "
            f"{percentile} percentile ({category}):\n\n"
            f"{top_colleges}\n"
            f"Strategy: {strategy}\n"
            f"Documents warning: {warning_text}"
        )

    return state