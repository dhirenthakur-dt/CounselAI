import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"), max_retries=0)
GROQ_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]


def response_agent(state: dict) -> dict:
    """
    Agent 5: Combines all agent outputs into
    one clean, adaptive final response for the student.
    Responds in Hinglish if student typed Hinglish, or English if typed English.
    """

    colleges       = state.get("ranked_colleges") or []
    strategy       = state.get("strategy") or "No strategy available."
    documents      = state.get("documents") or {}
    percentile     = state.get("percentile") or "Unknown"
    category       = state.get("category") or "Unknown"
    query_language = state.get("query_language") or "english"

    # Build college text
    top_colleges = ""
    for i, c in enumerate(colleges[:5], 1):
        chance = c.get("chance", "MEDIUM")
        emoji = "🟢" if chance == "HIGH" else "🟡" if chance == "MEDIUM" else "🔴"
        top_colleges += (
            f"{i}. {c.get('collegeName')} — "
            f"{c.get('branchName')} {emoji} ({chance} Chance)\n"
            f"   Annual Fee: Rs {c.get('annualFee')} | "
            f"Cutoff Score: {c.get('totalScore')}\n"
        )

    warnings     = documents.get("warnings", [])
    warning_text = "\n".join(warnings) if warnings else "No critical warnings."

    if query_language == "hinglish":
        prompt = f"""
You are CounselAI, an expert admission counsellor for Maharashtra engineering colleges (MHT-CET).
The student asked in Hinglish (Romanized Hindi).

Student Profile: {percentile} percentile, {category} category

Top Recommended Colleges:
{top_colleges}

CAP Round Strategy:
{strategy}

Document Warnings:
{warning_text}

Generate a friendly, reassuring, and motivating response in natural, conversational Hinglish (Hindi written in Roman script with English technical terms):
1. A warm opening acknowledging their {percentile} percentile (e.g. 'Badhai ho! {percentile} percentile bohot accha score hai...')
2. Top recommended colleges list with their chance level
3. CAP Round strategy in 2-3 clear actionable lines (which round to lock seat)
4. Document reminder in Hinglish (e.g., Non-Creamy Layer, Caste Validity, EWS certificate)
5. Encouraging closing line

Keep college and branch names in exact English. Use clean markdown formatting (bold, bullet points). Maximum 300 words.
"""
    else:
        prompt = f"""
You are CounselAI, an expert admission counsellor for Maharashtra engineering colleges (MHT-CET).

Student Profile: {percentile} percentile, {category} category

Top Recommended Colleges:
{top_colleges}

CAP Round Strategy:
{strategy}

Document Warnings:
{warning_text}

Write a complete, helpful response in simple, clear English:
1. A short encouraging opening line
2. Top recommended colleges with chance level
3. The CAP Round strategy in 3-4 lines
4. Important document warnings if any
5. A short encouraging closing line

Keep it friendly, structured, and easy to read with markdown. Maximum 300 words.
"""

    generated = False
    for model_name in GROQ_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600
            )
            state["final_response"] = response.choices[0].message.content.strip()
            print(f"[OK] Response Agent ({model_name}) generated final response in {query_language}")
            generated = True
            break
        except Exception as e:
            print(f"[WARN] Response Agent model {model_name} failed: {e}")
            continue

    if not generated:
        if query_language == "hinglish":
            state["final_response"] = (
                f"Aapke {percentile} percentile ({category}) ke liye top colleges ye hain:\n\n"
                f"{top_colleges}\n"
                f"**Strategy:** {strategy}\n\n"
                f"**Documents Alert:** {warning_text}"
            )
        else:
            state["final_response"] = (
                f"Here are your top colleges for "
                f"{percentile} percentile ({category}):\n\n"
                f"{top_colleges}\n"
                f"**Strategy:** {strategy}\n\n"
                f"**Documents Alert:** {warning_text}"
            )

    return state