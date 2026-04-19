# chat_service.py — v4 (Groq LLM)

import json
from groq import Groq
from typing import List, Optional
from database.connection import get_settings
from models.schemas import ChatMessage, MessageRole
from engine.rag import retrieve_context, retrieve_crisis_context

SYSTEM_PROMPT = """You are a calm, caring support companion inside AIMHHC — an AI mental health and harassment safety checker app.

RESPONSE FLOW — always follow this order:
1. ACKNOWLEDGE the emotion first (1 sentence — mirror what the user feels)
2. VALIDATE — normalise the feeling (1 sentence — "That makes sense", "Anyone would feel that way")
3. GENTLY EXPLORE or SUGGEST — one open question OR one small action (1-2 sentences)
4. POINT TO REAL SUPPORT — for anything medium/serious, end with a human resource

CRISIS PROTOCOL — HIGHEST PRIORITY:
If the user says ANYTHING resembling: "want to die", "kill myself", "end my life", "suicidal", "marna chahta/chahti", "jeena nahi chahta/chahti", "khatam kar lena", "hurt myself", "self harm" — your VERY FIRST LINE must be:
"Please reach out right now: iCall 9152987821 | Emergency 112 | Vandrevala Foundation 1860-2662-345"
Then acknowledge, then support. Never skip the helplines for crisis signals.

HARASSMENT PROTOCOL:
If user describes physical danger, threats, blackmail, or stalking:
- Validate their safety concern immediately
- Provide: Emergency 112 | Women Helpline 181 | Cyber Crime cybercrime.gov.in
- Encourage evidence preservation (screenshots, dates, witnesses)

TONE RULES:
- Warm but grounded — like a wise peer, not a therapist
- Never diagnose, prescribe, or give medical/legal advice
- Keep responses concise: 2-4 sentences unless crisis
- Never ask more than one question per message
- Do NOT say "I am always here for you" — creates dependency
- Never be dramatic or over-emotional — steady presence only

MCQ FORMAT (use when helpful):
Write a lead-in sentence, then:
1. Option one
2. Option two
3. Option three

EMOJI OPTIONS FORMAT (for mood check-ins):
EMOJI_OPTIONS: 😊 Good, 😐 Okay, 😔 Not great, 😢 Really struggling

This app is not a substitute for professional medical or legal advice."""

OPENING_MESSAGE = "Hey, how are you doing today? Anything on your mind you would like to talk about?"


def _get_client():
    settings = get_settings()
    return Groq(api_key=settings.groq_api_key)


def _build_history(history: List[ChatMessage]) -> List[dict]:
    contents = []
    for msg in history:
        role = "assistant" if msg.role == MessageRole.assistant else "user"
        contents.append({"role": role, "content": msg.content})
    return contents


def _build_system(
    user_name: str,
    risk_context: Optional[str] = None,
    user_profile: Optional[dict] = None,
    rag_context: str = "",
    mode: str = "NORMAL",
) -> str:
    system = SYSTEM_PROMPT

    if user_profile:
        profile_lines = []
        if user_profile.get("age"):
            profile_lines.append(f"Age: {user_profile['age']}")
        if user_profile.get("gender"):
            profile_lines.append(f"Gender: {user_profile['gender']}")
        if user_profile.get("concern"):
            profile_lines.append(f"Primary concern: {user_profile['concern']}")
        if user_profile.get("track"):
            profile_lines.append(f"Assessment track: {user_profile['track']}")
        if user_profile.get("last_risk_level"):
            profile_lines.append(f"Last risk level: {user_profile['last_risk_level']}")
        if user_profile.get("assessment_summary"):
            profile_lines.append(f"Assessment notes: {user_profile['assessment_summary']}")
        if profile_lines:
            system += "\n\nUSER CONTEXT (use naturally, do not reveal directly):\n"
            system += "\n".join(profile_lines)

    if rag_context:
        system += rag_context

    if mode == "CRISIS":
        system += """

IMPORTANT — CRISIS MODE:
- User may be in serious emotional distress or danger.
- Lead with helplines immediately.
- Be warm, steady, and non-judgmental.
- Do not minimise or dismiss what they are feeling.
- Guide them toward real human support right now.
"""
    elif mode == "SUPPORT":
        system += """

IMPORTANT — SUPPORT MODE:
- User is emotionally vulnerable.
- Be empathetic and validating — avoid generic advice.
- Keep response human, warm, and personal.
"""
    else:
        system += "\n\nIMPORTANT: Maintain a friendly and supportive tone."

    if risk_context:
        system += f"\n\nCurrent session risk: {risk_context}"

    system += f"\n\nUser's name: {user_name}. Use naturally, not every message."
    return system


def _parse_reply(reply_text: str) -> dict:
    mcq_options   = None
    emoji_options = None
    lines         = reply_text.split("\n")
    clean_lines   = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("EMOJI_OPTIONS:"):
            raw = stripped.replace("EMOJI_OPTIONS:", "").strip()
            emoji_options = [o.strip() for o in raw.split(",") if o.strip()]
        else:
            clean_lines.append(line)

    reply_text   = "\n".join(clean_lines).strip()
    lines        = reply_text.split("\n")
    option_lines = [
        l.strip() for l in lines
        if l.strip() and len(l.strip()) > 2
        and l.strip()[0].isdigit() and l.strip()[1] in ".)"
    ]

    if len(option_lines) >= 2:
        mcq_options = [
            l.split(None, 1)[1].strip() if len(l.split(None, 1)) > 1 else l
            for l in option_lines
        ]
        non_option = [l for l in lines if l.strip() not in option_lines]
        reply_text = "\n".join(non_option).strip()

    check_in = ["how are you", "how do you feel", "how is your mood", "feeling today", "how have you been"]
    if not mcq_options and not emoji_options and any(t in reply_text.lower() for t in check_in):
        emoji_options = ["😊 Good", "😐 Okay", "😔 Not great", "😢 Really struggling"]

    return {"reply": reply_text, "mcq_options": mcq_options, "emoji_options": emoji_options}


# ── Main chat ──────────────────────────────────────────────────────────────────

async def get_ai_reply(
    history: List[ChatMessage],
    new_user_message: str,
    user_name: str,
    risk_context: Optional[str] = None,
    user_profile: Optional[dict] = None,
    mode: str = "NORMAL",
    categories: Optional[List[str]] = None,
) -> dict:

    # RAG retrieval
    if mode == "CRISIS":
        rag_context = retrieve_crisis_context()
    else:
        rag_context = retrieve_context(
            query=new_user_message,
            categories=categories or [],
            top_k=3,
            min_score=0.30,
        )

    system = _build_system(
        user_name=user_name,
        risk_context=risk_context,
        user_profile=user_profile,
        rag_context=rag_context,
        mode=mode,
    )

    messages = [{"role": "system", "content": system}]
    messages += _build_history(history)
    messages.append({"role": "user", "content": new_user_message})

    try:
        client   = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=450,
            temperature=0.7,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            text = "I'm here with you. Do you want to share a bit more about what's going on?"
    except Exception as e:
        import traceback
        print(f"GROQ ERROR: {e}")
        traceback.print_exc()
        text = "I'm having a small technical issue right now, but I'm here to listen. Can you tell me more?"

    return _parse_reply(text)


# ── Image evidence ─────────────────────────────────────────────────────────────

async def analyze_evidence_image(
    image_bytes: bytes,
    filename: str,
    user_name: str,
    context: Optional[str] = None,
) -> dict:
    """Groq does not support vision — return guidance to describe in chat."""
    return {
        "description": f"Image '{filename}' received.",
        "risk_indicators": [],
        "is_harassment_evidence": False,
        "confidence": "low",
        "suggested_actions": [
            "Please describe what this image shows in the chat.",
            "Include: who is in the image, what is happening, and when it was taken.",
            "If this is evidence of harassment, save the original file safely.",
        ],
        "ai_analysis": (
            f"Image '{filename}' has been received. "
            "Please describe its contents in the chat so I can help you better."
        ),
    }


# ── Video evidence ─────────────────────────────────────────────────────────────

async def analyze_evidence_video(
    video_bytes: bytes,
    filename: str,
    user_name: str,
    context: Optional[str] = None,
) -> dict:
    return {
        "description": f"Video '{filename}' has been securely received and stored.",
        "risk_indicators": [],
        "is_harassment_evidence": False,
        "confidence": "low",
        "suggested_actions": [
            "Your video has been stored as evidence. Do not delete the original.",
            "Please describe in the chat what this video shows and when it was recorded.",
            "Note the date, time, location, and names of anyone involved.",
            "If you are in immediate danger, call Emergency: 112",
        ],
        "ai_analysis": (
            f"Video file '{filename}' has been securely saved. "
            "Please describe what the video contains in the chat."
        ),
    }


# ── Voice transcription ────────────────────────────────────────────────────────

async def transcribe_voice(audio_bytes: bytes, filename: str, mime_type: str = "audio/webm") -> dict:
    """Use Groq Whisper for transcription — excellent and free."""
    try:
        client = _get_client()
        # Groq supports Whisper via audio transcription endpoint
        transcription = client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
            response_format="text",
        )
        text = transcription if isinstance(transcription, str) else transcription.text
        return {"transcription": text.strip(), "language": "en", "confidence": "high"}
    except Exception as e:
        print(f"GROQ WHISPER ERROR: {e}")
        return {"transcription": "", "language": "en", "confidence": "low", "error": str(e)}


async def get_opening_message() -> str:
    return OPENING_MESSAGE