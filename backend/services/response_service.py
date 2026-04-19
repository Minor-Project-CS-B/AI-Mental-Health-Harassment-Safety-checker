#response_service.py

"""
services/response_service.py
─────────────────────────────
AI-powered dynamic response generator using Groq (llama-3.3-70b-versatile).

Generates personalized:
  - Support message referencing user's actual situation
  - 5 prioritized suggestions tailored to their specific answers
  - A 3-step coping plan for TODAY
  - One concrete follow-up action right now

Falls back to static response_generator.py if Groq call fails.
"""

import json
from groq import Groq
from typing import List, Optional
from database.connection import get_settings
from engine.response_generator import generate_response
from models.schemas import (
    RiskLevel, TrackType, ResourceItem,
    PersonalizedSuggestion, DynamicResponseResult
)


# ── Static helplines — NEVER AI-generated, always reliable ────────────────────

STATIC_RESOURCES = {
    RiskLevel.low: [
        ResourceItem(title="Vandrevala Foundation",  description="24/7 mental health helpline.", contact="1860-2662-345"),
        ResourceItem(title="Mindfulness India",      description="Free guided meditation.", url="https://www.artofliving.org/in-en/meditation"),
    ],
    RiskLevel.medium: [
        ResourceItem(title="iCall – TISS",           description="Psychosocial helpline for students and professionals.", contact="9152987821", url="https://icallhelpline.org"),
        ResourceItem(title="Vandrevala Foundation",  description="24/7 mental health helpline.", contact="1860-2662-345"),
        ResourceItem(title="NIMHANS",                description="National Institute of Mental Health helpline.", contact="080-46110007"),
        ResourceItem(title="Women Helpline",         description="National helpline for women in distress.", contact="181"),
    ],
    RiskLevel.high: [
        ResourceItem(title="Emergency Services",     description="Call immediately if you are in danger.", contact="112"),
        ResourceItem(title="iCall – TISS",           description="Psychosocial helpline for students.", contact="9152987821", url="https://icallhelpline.org"),
        ResourceItem(title="Vandrevala Foundation",  description="24/7 mental health helpline.", contact="1860-2662-345"),
        ResourceItem(title="Women Helpline",         description="National helpline for women in distress.", contact="181"),
        ResourceItem(title="Cyber Crime Reporting",  description="Report online harassment.", url="https://cybercrime.gov.in"),
    ],
}


def _build_prompt(
    track: str,
    risk_level: str,
    risk_score: float,
    matched_keywords: List[str],
    assessment_answers: List[str],
    chat_summary: str,
    user_name: str,
) -> str:
    track_label = "Mental Health" if track == "mental_health" else "Harassment & Safety"
    keyword_str = ", ".join(matched_keywords) if matched_keywords else "none detected"
    answers_str = "\n".join([f"- {a}" for a in assessment_answers[:8]]) if assessment_answers else "No answers provided."

    return f"""You are a compassionate mental health and safety support AI for AIMHHC app.

User: {user_name}
Track: {track_label}
Risk Level: {risk_level.upper()} (score: {round(risk_score * 100)}%)
Detected concern areas: {keyword_str}

Their assessment answers:
{answers_str}

Recent chat context: {chat_summary}

Generate a deeply personalized response. Do NOT give generic advice. Reference their specific concerns.

Respond ONLY in valid JSON with no markdown, no code fences, no extra text:
{{
  "support_message": "Warm 2-3 sentence message addressing their actual situation. Reference their specific keywords/answers.",
  "suggestions": [
    {{"text": "Specific actionable suggestion directly related to their answers", "category": "category_name", "priority": 1}},
    {{"text": "Specific actionable suggestion 2", "category": "category_name", "priority": 2}},
    {{"text": "Specific actionable suggestion 3", "category": "category_name", "priority": 3}},
    {{"text": "Specific actionable suggestion 4", "category": "category_name", "priority": 4}},
    {{"text": "Specific actionable suggestion 5", "category": "category_name", "priority": 5}}
  ],
  "coping_plan": "Step 1: [action]. Step 2: [action]. Step 3: [action].",
  "follow_up_tip": "ONE specific thing they can do in the next 30 minutes."
}}

Rules:
- If risk is HIGH, first suggestion must be about contacting a professional or helpline
- coping_plan must be realistic for a student/young professional in India
- follow_up_tip must be doable RIGHT NOW
- Max 2 sentences per suggestion
- Warm, non-clinical, non-judgmental tone"""


async def generate_dynamic_response(
    track: str,
    risk_level: str,
    risk_score: float,
    matched_keywords: List[str],
    assessment_answers: List[str],
    user_id: str,
    user_name: str,
    db,
) -> DynamicResponseResult:
    """
    Generates personalized AI response using Groq.
    Falls back to static generator on any error.
    """
    settings = get_settings()
    client   = Groq(api_key=settings.groq_api_key)

    # ── Fetch recent chat for context ──────────────────────────────────────────
    try:
        recent_chats = await db["chat_messages"].find(
            {"user_id": user_id, "role": "user"},
            {"content": 1, "_id": 0}
        ).sort("timestamp", -1).limit(10).to_list(length=10)

        chat_texts   = [m["content"] for m in recent_chats if not m["content"].startswith("[")]
        chat_summary = " | ".join(chat_texts[:5]) if chat_texts else "No recent chat history."
    except Exception:
        chat_summary = "No recent chat history."

    prompt = _build_prompt(
        track=track,
        risk_level=risk_level,
        risk_score=risk_score,
        matched_keywords=matched_keywords,
        assessment_answers=assessment_answers,
        chat_summary=chat_summary,
        user_name=user_name,
    )

    # ── Call Groq ──────────────────────────────────────────────────────────────
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate mental health support AI. Always respond with valid JSON only. No markdown, no code fences, no explanations outside the JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_tokens=1000,
        )

        raw = completion.choices[0].message.content.strip()

        # Strip any accidental code fences
        if raw.startswith("```"):
            parts = raw.split("```")
            raw   = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        suggestions = []
        for s in data.get("suggestions", []):
            suggestions.append(PersonalizedSuggestion(
                text=s.get("text", ""),
                category=s.get("category", "general"),
                priority=int(s.get("priority", 5)),
            ))
        suggestions.sort(key=lambda x: x.priority)

        rl        = RiskLevel(risk_level)
        resources = STATIC_RESOURCES.get(rl, STATIC_RESOURCES[RiskLevel.medium])

        return DynamicResponseResult(
            support_message=data.get("support_message", ""),
            suggestions=suggestions,
            resources=resources,
            coping_plan=data.get("coping_plan", ""),
            follow_up_tip=data.get("follow_up_tip", ""),
            generated_by="ai",
        )

    except Exception as e:
        print(f"[ResponseService] Groq failed, using static fallback: {e}")

        rl     = RiskLevel(risk_level)
        tt     = TrackType(track)
        static = generate_response(risk_level=rl, track=tt)

        return DynamicResponseResult(
            support_message=static["support_message"],
            suggestions=[
                PersonalizedSuggestion(text=s, category="general", priority=i + 1)
                for i, s in enumerate(static["suggestions"])
            ],
            resources=static["resources"],
            coping_plan="Step 1: Take a few deep breaths and ground yourself. Step 2: Reach out to one trusted person today. Step 3: Pick one suggestion above and act on it.",
            follow_up_tip="Write down one thing that's bothering you most right now.",
            generated_by="static",
        )