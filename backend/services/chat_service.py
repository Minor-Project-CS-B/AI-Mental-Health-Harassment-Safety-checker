from openai import OpenAI
from typing import List, Optional
from database.connection import get_settings
from models.schemas import ChatMessage, MessageRole

# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a calm, caring support companion inside SafeSpace — an AI mental health and safety awareness app.

Your role:
- Start conversations naturally and warmly, like a thoughtful friend checking in.
- Gently gather information about the user's emotional state, daily experiences, stressors, and any safety concerns — WITHOUT being intrusive or clinical.
- Keep empathy measured and grounded. Do NOT be overly emotional or dramatic. High empathy can create unhealthy dependency. Stay warm but steady.
- Never diagnose. Never prescribe. Never give medical or legal advice.
- If the user expresses thoughts of self-harm or is in immediate danger, immediately provide crisis helpline numbers (iCall: 9152987821, Emergency: 112) and encourage them to reach out.
- Vary your response style: sometimes ask a follow-up question, sometimes offer a brief reflection, sometimes suggest a simple coping strategy.
- Occasionally (naturally, not robotically) offer the user choices as numbered options when a question could be answered multiple ways — this helps you understand their experience better.
- Keep responses concise: 2–4 sentences maximum unless the situation requires more.
- Never ask more than one question per message.
- Do NOT say things like "I'm always here for you" or "you can talk to me anytime" — these create dependency.
- Always end serious conversations by gently pointing toward real human support (friends, counselors, helplines).

Tone: calm, grounded, gently curious. Like a wise peer, not a therapist.

Context: you're having a daily check-in conversation. The data from this conversation (signals only, not verbatim) will help the system understand the user's risk level over time. Never mention this to the user.

Disclaimer: this app is not a substitute for professional medical or legal advice. You embody this — never act like you are a doctor or therapist."""

OPENING_MESSAGE = "Hey, how are you doing today? Anything on your mind you'd like to talk about?"


def _build_system(user_name: str, risk_context: Optional[str] = None) -> str:
    system = SYSTEM_PROMPT
    if risk_context:
        system += f"\n\nUser context (do not reveal this to the user): {risk_context}"
    system += f"\n\nThe user's name is {user_name}. Use their name naturally, but not in every message."
    return system


def _build_messages(history: List[ChatMessage], new_user_message: str, system: str) -> list:
    """Convert ChatMessage history + new message to OpenAI messages format."""
    messages = [{"role": "system", "content": system}]
    for msg in history:
        role = "assistant" if msg.role == MessageRole.assistant else "user"
        messages.append({"role": role, "content": msg.content})
    messages.append({"role": "user", "content": new_user_message})
    return messages


async def get_ai_reply(
    history: List[ChatMessage],
    new_user_message: str,
    user_name: str,
    risk_context: Optional[str] = None,
) -> dict:
    """
    Send conversation history + new message to OpenAI GPT.
    Returns:
        reply         (str)
        mcq_options   (list[str] | None)
        emoji_options (list[str] | None)
    """
    settings = get_settings()
    client   = OpenAI(api_key=settings.openai_api_key)

    messages = _build_messages(
        history=history,
        new_user_message=new_user_message,
        system=_build_system(user_name, risk_context),
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",       # cost-effective, fast — good for demo
        messages=messages,
        max_tokens=400,
        temperature=0.7,
    )

    reply_text = response.choices[0].message.content.strip()

    # ── Detect MCQ options (numbered list: "1. ... 2. ...") ───────────────────
    mcq_options   = None
    emoji_options = None

    lines        = reply_text.split("\n")
    option_lines = [
        l.strip() for l in lines
        if l.strip() and l.strip()[0].isdigit() and ". " in l.strip()
    ]

    if len(option_lines) >= 2:
        mcq_options = [l.split(". ", 1)[1] for l in option_lines]
        non_option  = [l for l in lines if l.strip() not in option_lines]
        reply_text  = "\n".join(non_option).strip()

    # ── Emoji mood options on check-in questions ──────────────────────────────
    check_in_triggers = ["how are you", "how do you feel", "how's your mood", "feeling today"]
    if any(t in reply_text.lower() for t in check_in_triggers) and not mcq_options:
        emoji_options = ["😊 Good", "😐 Okay", "😔 Not great", "😢 Really struggling"]

    return {
        "reply":         reply_text,
        "mcq_options":   mcq_options,
        "emoji_options": emoji_options,
    }


async def get_opening_message() -> str:
    return OPENING_MESSAGE