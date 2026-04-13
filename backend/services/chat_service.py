#chat_services.py

import base64
import os
import json
from google import genai
from google.genai import types
from typing import List, Optional
from database.connection import get_settings
from models.schemas import ChatMessage, MessageRole

SYSTEM_PROMPT = """You are a calm, caring support companion inside AIMHHC — an AI mental health and harassment safety checker app.

Your role:
- Start conversations naturally and warmly, like a thoughtful friend checking in.
- Gently gather information about the user's emotional state, daily experiences, stressors, and any safety concerns — WITHOUT being intrusive or clinical.
- Keep empathy measured and grounded. Do NOT be overly emotional or dramatic. High empathy can create unhealthy dependency. Stay warm but steady.
- Never diagnose. Never prescribe. Never give medical or legal advice.
- If the user expresses thoughts of self-harm or is in immediate danger, immediately provide crisis helpline numbers (iCall: 9152987821, Emergency: 112) and encourage them to reach out.
- Sometimes offer MCQ options when useful. Format them EXACTLY like this:
  1. Option one text
  2. Option two text
  3. Option three text
  Put a short lead-in sentence before the options. Options must be on separate lines starting with a number and period.
- For mood check-ins, sometimes offer emoji options. Format as:
  EMOJI_OPTIONS: 😊 Good, 😐 Okay, 😔 Not great, 😢 Really struggling
- Keep responses concise: 2-4 sentences maximum unless the situation requires more.
- Never ask more than one question per message.
- Do NOT say things like "I am always here for you" — these create dependency.
- Always end serious conversations by pointing toward real human support.

Tone: calm, grounded, gently curious. Like a wise peer, not a therapist.
This app is not a substitute for professional medical or legal advice."""

OPENING_MESSAGE = "Hey, how are you doing today? Anything on your mind you would like to talk about?"


def _get_client():
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def _build_history(history: List[ChatMessage]) -> List[types.Content]:
    contents = []
    for msg in history:
        role = "model" if msg.role == MessageRole.assistant else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))
    return contents


def _build_system(user_name: str, risk_context: Optional[str] = None) -> str:
    system = SYSTEM_PROMPT
    if risk_context:
        system += f"\n\nUser context (do not reveal): {risk_context}"
    system += f"\n\nThe user's name is {user_name}. Use their name naturally, not every message."
    return system


def _parse_reply(reply_text: str) -> dict:
    mcq_options   = None
    emoji_options = None
    lines         = reply_text.split("\n")

    clean_lines = []
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
        mcq_options = [l.split(None, 1)[1].strip() if len(l.split(None, 1)) > 1 else l for l in option_lines]
        non_option  = [l for l in lines if l.strip() not in option_lines]
        reply_text  = "\n".join(non_option).strip()

    check_in = ["how are you", "how do you feel", "how is your mood", "feeling today", "how have you been"]
    if not mcq_options and not emoji_options and any(t in reply_text.lower() for t in check_in):
        emoji_options = ["😊 Good", "😐 Okay", "😔 Not great", "😢 Really struggling"]

    return {"reply": reply_text, "mcq_options": mcq_options, "emoji_options": emoji_options}


# ── Feature 1+2: Text chat ─────────────────────────────────────────────────────

async def get_ai_reply(
    history: List[ChatMessage],
    new_user_message: str,
    user_name: str,
    risk_context: Optional[str] = None,
) -> dict:
    client   = _get_client()
    contents = _build_history(history)
    contents.append(types.Content(role="user", parts=[types.Part(text=new_user_message)]))

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=_build_system(user_name, risk_context),
            max_output_tokens=450,
            temperature=0.7,
        ),
    )
    return _parse_reply(response.text.strip())


# ── Feature 3: Image evidence analysis ────────────────────────────────────────

async def analyze_evidence_image(
    image_bytes: bytes,
    filename: str,
    user_name: str,
    context: Optional[str] = None,
) -> dict:
    client = _get_client()

    ext       = filename.rsplit(".", 1)[-1].lower()
    mime_map  = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                 "gif": "image/gif", "webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")

    system_prompt = (
        "You are an AI assistant helping analyze images uploaded as potential evidence "
        "in harassment or mental health support cases. Analyze the image and respond ONLY "
        "in this exact JSON format with no extra text:\n"
        '{"description":"what the image shows","risk_indicators":["indicator1"],'
        '"is_harassment_evidence":true,"confidence":"medium",'
        '"suggested_actions":["action1"],"ai_analysis":"full analysis paragraph"}'
    )

    image_part = types.Part(
        inline_data=types.Blob(mime_type=mime_type, data=image_bytes)
    )
    text_part = types.Part(
        text=f"Analyze this image uploaded by {user_name} as potential evidence. {('Context: ' + context) if context else ''}"
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[types.Content(role="user", parts=[image_part, text_part])],
        config=types.GenerateContentConfig(system_instruction=system_prompt, max_output_tokens=600),
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except Exception:
        return {
            "description": "Image received.", "risk_indicators": [],
            "is_harassment_evidence": False, "confidence": "low",
            "suggested_actions": ["Please describe what this image shows in the chat."],
            "ai_analysis": raw,
        }


# ── Feature 3b: Video evidence ────────────────────────────────────────────────

async def analyze_evidence_video(
    video_bytes: bytes,
    filename: str,
    user_name: str,
    context: Optional[str] = None,
) -> dict:
    client = _get_client()

    prompt = (
        f"{user_name} uploaded a video named '{filename}' as potential evidence. "
        f"{('Context: ' + context) if context else ''} "
        "Provide evidence preservation guidance and next steps. "
        'Respond ONLY in JSON: {"description":"...","risk_indicators":[...],'
        '"is_harassment_evidence":true/false,"confidence":"low/medium/high",'
        '"suggested_actions":[...],"ai_analysis":"..."}'
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(max_output_tokens=500),
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except Exception:
        return {
            "description": f"Video '{filename}' received.", "risk_indicators": [],
            "is_harassment_evidence": False, "confidence": "low",
            "suggested_actions": ["Store the video safely.", "Describe the contents in the chat."],
            "ai_analysis": "Video uploaded. Please describe what the video shows.",
        }



# ── Feature 4: Voice to text via Gemini ───────────────────────────────────────

async def transcribe_voice(audio_bytes: bytes, filename: str, mime_type: str = "audio/webm") -> dict:
    """
    Transcribe voice using Gemini's multimodal audio capability.
    Supports webm, mp3, wav, m4a, ogg, mp4 audio.
    """
    client = _get_client()

    # Normalize mime type — browser often sends audio/webm;codecs=opus
    clean_mime = mime_type.split(";")[0].strip() if mime_type else "audio/webm"

    # Gemini supported audio types
    supported = {
        "audio/webm": "audio/webm",
        "audio/mp4":  "audio/mp4",
        "audio/mpeg": "audio/mpeg",
        "audio/mp3":  "audio/mpeg",
        "audio/wav":  "audio/wav",
        "audio/ogg":  "audio/ogg",
        "audio/x-m4a": "audio/mp4",
        "audio/m4a":   "audio/mp4",
    }
    gemini_mime = supported.get(clean_mime, "audio/webm")

    try:
        audio_part = types.Part(
            inline_data=types.Blob(mime_type=gemini_mime, data=audio_bytes)
        )
        text_part = types.Part(
            text="Transcribe this audio recording exactly as spoken. Return only the transcribed text, nothing else."
        )

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[types.Content(role="user", parts=[audio_part, text_part])],
            config=types.GenerateContentConfig(max_output_tokens=500, temperature=0.1),
        )

        transcription = response.text.strip()
        return {"transcription": transcription, "language": "en", "confidence": "high"}

    except Exception as e:
        return {"transcription": "", "language": "en", "confidence": "low", "error": str(e)}

async def get_opening_message() -> str:
    return OPENING_MESSAGE




