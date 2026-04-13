#assessment_service.py

"""
services/assessment_service.py
──────────────────────────────
RAG + GPT dynamic assessment question generator.

Flow:
  1. Load static question bank for the selected track (RAG knowledge base)
  2. Fetch user's recent chat history (if any)
  3. Build a rich prompt combining both sources
  4. Ask GPT to generate 10 personalized, context-aware questions
  5. Return structured DynamicQuestion list

Every call generates a FRESH set — never the same questions twice.
"""

import json
import uuid
from typing import List, Optional
from google import genai
from google.genai import types
from database.connection import get_settings

# ── Static question banks (RAG knowledge base) ─────────────────────────────────
# These are the reference questions the AI uses to understand scope and format.
# It does NOT reuse them verbatim — it generates NEW ones inspired by these.

MENTAL_HEALTH_RAG_BASE = [
    {"text": "How often have you felt hopeless or helpless in the past 2 weeks?",  "category": "hopelessness"},
    {"text": "How would you describe your energy levels lately?",                   "category": "energy"},
    {"text": "How often do you feel anxious or worried without a clear reason?",    "category": "anxiety"},
    {"text": "How well have you been sleeping recently?",                           "category": "sleep"},
    {"text": "Have you lost interest in activities you used to enjoy?",             "category": "anhedonia"},
    {"text": "How often do you feel overwhelmed by everyday tasks?",                "category": "overwhelm"},
    {"text": "How well are you able to concentrate on work or studies?",            "category": "concentration"},
    {"text": "Do you feel connected to and supported by people around you?",        "category": "social_support"},
    {"text": "How often have you had thoughts of harming yourself?",                "category": "self_harm"},
    {"text": "Overall, how would you rate your mental health right now?",           "category": "overall"},
    {"text": "How often do you feel lonely or isolated from others?",               "category": "loneliness"},
    {"text": "Have you noticed changes in your appetite recently?",                 "category": "appetite"},
    {"text": "How often do you experience physical symptoms like headaches or stomachaches due to stress?", "category": "physical_stress"},
    {"text": "Do you find it hard to make decisions or think clearly?",             "category": "cognitive"},
    {"text": "How often do you feel irritable or angry without strong reason?",     "category": "irritability"},
]

HARASSMENT_RAG_BASE = [
    {"text": "Have you experienced verbal abuse, insults, or humiliation recently?",          "category": "verbal_harassment"},
    {"text": "Have you received threatening or abusive messages online?",                     "category": "cyber_harassment"},
    {"text": "Have you felt physically unsafe or threatened by someone?",                     "category": "physical_safety"},
    {"text": "Has anyone shared private information or images of you without consent?",       "category": "privacy_violation"},
    {"text": "Have you been followed, watched, or stalked online or offline?",                "category": "stalking"},
    {"text": "Have you been discriminated against or treated unfairly at your institution?",  "category": "discrimination"},
    {"text": "Do you feel you can report harassment to someone in authority?",                "category": "reporting_access"},
    {"text": "Has the harassment affected your daily routine or sense of safety?",            "category": "daily_impact"},
    {"text": "Have you lost sleep or experienced anxiety because of the situation?",          "category": "psychological_impact"},
    {"text": "Do you currently feel safe where you are right now?",                           "category": "current_safety"},
    {"text": "Has someone pressured you into something you were uncomfortable with?",         "category": "coercion"},
    {"text": "Have you felt forced to change your behavior to avoid a harasser?",             "category": "behavior_change"},
    {"text": "Has a person in authority misused their power over you?",                       "category": "power_abuse"},
    {"text": "Have you experienced harassment based on your gender, religion, or identity?",  "category": "identity_based"},
    {"text": "Do you have a trusted person you can talk to about what is happening?",         "category": "support_access"},
]

OPTION_TEMPLATES = {
    "frequency":  (["Never", "Rarely", "Sometimes", "Often", "Always"],           [0,1,2,3,4], ["😊","🙂","😐","😟","😢"]),
    "intensity":  (["Not at all", "Slightly", "Moderately", "Significantly", "Severely"], [0,1,2,3,4], ["😊","🙂","😐","😟","😱"]),
    "safety":     (["Very safe", "Mostly safe", "Somewhat unsafe", "Quite unsafe", "Not safe at all"], [0,1,2,3,4], ["😊","🙂","😐","😟","🚨"]),
    "agreement":  (["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"], [0,1,2,3,4], ["😊","🙂","😐","😟","😢"]),
    "wellbeing":  (["Excellent", "Good", "Fair", "Poor", "Very poor"],             [0,1,2,3,4], ["😊","🙂","😐","😔","😢"]),
    "support":    (["Very supported", "Mostly yes", "Somewhat", "Not really", "Not at all"], [0,1,2,3,4], ["🤗","🙂","😐","😔","😞"]),
}

EMOJI_OPTION_CATEGORIES = {
    "safety": "safety", "current_safety": "safety", "physical_safety": "safety",
    "overall": "wellbeing", "social_support": "support", "reporting_access": "support", "support_access": "support",
    "hopelessness": "intensity", "anhedonia": "intensity", "self_harm": "intensity",
    "physical_stress": "intensity", "privacy_violation": "intensity", "coercion": "intensity",
    "power_abuse": "intensity", "identity_based": "intensity",
}


def _get_option_template(category: str) -> tuple:
    key = EMOJI_OPTION_CATEGORIES.get(category, "frequency")
    return OPTION_TEMPLATES[key]


def _format_chat_summary(chat_messages: list) -> str:
    """Convert recent chat messages into a concise summary for the prompt."""
    if not chat_messages:
        return "No prior chat history available."

    summary_lines = []
    for msg in chat_messages[-15:]:    # last 15 messages
        role    = "User" if msg.get("role") == "user" else "AI"
        content = msg.get("content", "")[:200]    # truncate long messages
        if content and not content.startswith("["):    # skip file upload markers
            summary_lines.append(f"{role}: {content}")

    return "\n".join(summary_lines) if summary_lines else "No meaningful chat history found."


async def generate_dynamic_questions(
    track: str,
    chat_messages: list,
    user_name: str,
    user_risk_level: str = "low",
) -> dict:
    """
    Core RAG + GPT function.
    Returns a dict with session_id, questions list, and metadata.
    """
    settings = get_settings()
    client   = genai.Client(api_key=settings.gemini_api_key)

    # ── Step 1: Select RAG base ────────────────────────────────────────────────
    rag_base   = MENTAL_HEALTH_RAG_BASE if track == "mental_health" else HARASSMENT_RAG_BASE
    track_name = "Mental Health" if track == "mental_health" else "Harassment & Safety"

    # Format RAG base as reference
    rag_text = "\n".join([f"- [{q['category']}] {q['text']}" for q in rag_base])

    # ── Step 2: Format chat context ───────────────────────────────────────────
    chat_summary    = _format_chat_summary(chat_messages)
    has_chat        = bool(chat_messages)

    # ── Step 3: Build prompt ──────────────────────────────────────────────────
    system_prompt = """You are an expert clinical psychologist and assessment designer specializing in mental health and harassment safety screening.

Your task is to generate 10 personalized assessment questions for a user.

Rules:
- Generate EXACTLY 10 questions
- Each question must be unique and different from all others
- Questions must be sensitive, non-judgmental, and easy to understand
- Base questions on the user's chat history if available — make them contextually relevant
- Use the reference question bank for inspiration on categories and scope, but DO NOT copy them verbatim
- Generate FRESH, PERSONALIZED questions every time
- Vary the question angles — don't ask the same thing twice in different words
- Each question needs a category label and a brief reason why you generated it
- Don't take only the question bank questions make new and different questions 
- Very question should be unique and different from last assessments question 

Respond ONLY with valid JSON in this exact format:
{
  "questions": [
    {
      "id": "q1",
      "text": "question text here",
      "category": "category_name",
      "why": "one sentence explaining why this question was generated"
    },
    ...10 questions total
  ]
}"""

    user_prompt = f"""Generate 10 personalized {track_name} assessment questions for {user_name}.

Current risk level: {user_risk_level}

Reference question bank (for scope and category inspiration — do NOT copy verbatim):
{rag_text}

Recent conversation history with the user:
{chat_summary}

{"IMPORTANT: The chat history reveals specific concerns — tailor some questions to probe those areas more deeply." if has_chat else "No chat history available — generate general but thoughtful questions covering all key categories."}

Generate 10 fresh, personalized questions now."""

    # ── Step 4: Call GPT ──────────────────────────────────────────────────────
    combined_prompt = system_prompt + "\n\n" + user_prompt

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[types.Content(role="user", parts=[types.Part(text=combined_prompt)])],
        config=types.GenerateContentConfig(
            max_output_tokens=1500,
            temperature=0.85,
        ),
    )

    # ── Step 5: Parse and structure ───────────────────────────────────────────
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    try:
        raw       = json.loads(raw_text)
        questions = raw.get("questions", [])
    except Exception:
        questions = []

    # Validate we got 10 questions, pad with fallbacks if needed
    if len(questions) < 10:
        fallbacks = rag_base[len(questions):]
        for i, fb in enumerate(fallbacks[:10 - len(questions)]):
            questions.append({
                "id":       f"fb{i+1}",
                "text":     fb["text"],
                "category": fb["category"],
                "why":      "Fallback question from reference bank.",
            })

    # Attach options/scores/emojis to each question
    dynamic_questions = []
    for i, q in enumerate(questions[:10]):
        category          = q.get("category", "frequency")
        options, scores, emojis = _get_option_template(category)
        dynamic_questions.append({
            "id":       q.get("id", f"q{i+1}"),
            "text":     q.get("text", ""),
            "options":  options,
            "scores":   scores,
            "emoji":    emojis,
            "category": category,
            "why":      q.get("why", ""),
        })

    session_id = str(uuid.uuid4())

    return {
        "session_id":    session_id,
        "track":         track,
        "questions":     dynamic_questions,
        "based_on_chat": has_chat,
    }