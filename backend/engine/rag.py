"""
engine/rag.py — Lightweight RAG for AIMHHC
==========================================

Architecture:
  - Knowledge base = curated mental health + harassment safety documents
  - Embeddings = sentence-transformers (all-MiniLM-L6-v2) — fast, small, good
  - Retrieval = cosine similarity via scikit-learn (no external vector DB needed)
  - Output = top-K relevant chunks injected into system prompt

Flow in chat pipeline:
  User message
      ↓
  classify_input()  →  risk_score + categories
      ↓
  retrieve_context()  →  relevant knowledge chunks
      ↓
  get_ai_reply()  →  Gemini with enriched system prompt
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional

# ── Lazy-load sentence-transformers so startup is fast ────────────────────────
_model = None

def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError as e:
            raise ImportError("sentence_transformers is required but not installed. Please run: pip install sentence-transformers") from e
    return _model


# ── Knowledge Base ─────────────────────────────────────────────────────────────
# Each entry: {"text": "...", "category": "...", "tags": [...]}
# Categories match classifier output: depression, anxiety, crisis,
# harassment_verbal, harassment_physical, harassment_online,
# threat, manipulation, coercion, workplace_stress, academic_stress

KNOWLEDGE_BASE = [

    # ── CRISIS / SELF-HARM ─────────────────────────────────────────────────────
    {
        "text": "If someone is experiencing suicidal thoughts or self-harm urges, immediate help is available. In India: iCall 9152987821, Vandrevala Foundation 1860-2662-345, Emergency 112. Encourage them to reach out to a trusted person right now.",
        "category": "crisis",
        "tags": ["suicidal", "self-harm", "emergency", "helpline"],
    },
    {
        "text": "Crisis grounding technique: Ask the person to name 5 things they can see, 4 they can touch, 3 they can hear, 2 they can smell, 1 they can taste. This brings attention back to the present moment and can reduce immediate distress.",
        "category": "crisis",
        "tags": ["grounding", "coping", "immediate-help"],
    },
    {
        "text": "When someone expresses hopelessness, validate their pain without minimizing it. Say: 'What you are feeling sounds incredibly heavy. You don't have to carry this alone.' Then guide them to professional support immediately.",
        "category": "crisis",
        "tags": ["hopelessness", "validation", "support"],
    },

    # ── DEPRESSION ─────────────────────────────────────────────────────────────
    {
        "text": "Depression is not a character flaw or weakness. It is a recognized mental health condition that responds well to treatment. Common symptoms include persistent sadness, loss of interest, fatigue, sleep changes, and difficulty concentrating.",
        "category": "depression",
        "tags": ["depression", "symptoms", "awareness"],
    },
    {
        "text": "Behavioral Activation is a proven technique for depression: start with one tiny enjoyable activity per day — even 10 minutes. Small actions rebuild motivation over time. Examples: a short walk, calling a friend, listening to music.",
        "category": "depression",
        "tags": ["coping", "behavioral-activation", "technique"],
    },
    {
        "text": "For persistent low mood: maintain a consistent sleep schedule, expose yourself to natural light in the morning, eat regular meals, and limit alcohol. These basic habits significantly affect mood regulation.",
        "category": "depression",
        "tags": ["lifestyle", "self-care", "mood"],
    },
    {
        "text": "In India, mental health support resources include: iCall (TISS) 9152987821, Vandrevala Foundation 1860-2662-345, NIMHANS 080-46110007, Snehi 044-24640050. Many offer free, confidential counseling.",
        "category": "depression",
        "tags": ["helpline", "india", "counseling"],
    },
    {
        "text": "Udaasi aur akela feel karna bohot mushkil hota hai. Ye feelings real hain aur inhe samjha ja sakta hai. Agar aap bahut zyada akela ya hopeless feel kar rahe ho, please kisi trusted insaan se baat karo ya iCall 9152987821 pe call karo.",
        "category": "depression",
        "tags": ["hindi", "hinglish", "depression", "helpline"],
    },

    # ── ANXIETY ────────────────────────────────────────────────────────────────
    {
        "text": "Box breathing technique for anxiety: Inhale for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat 4 times. This activates the parasympathetic nervous system and reduces the fight-or-flight response within minutes.",
        "category": "anxiety",
        "tags": ["breathing", "technique", "immediate-relief", "anxiety"],
    },
    {
        "text": "Anxiety often comes from catastrophic thinking — imagining worst-case scenarios. Challenge anxious thoughts by asking: What is the actual evidence for this fear? What would I tell a friend in this situation? What is most likely to happen?",
        "category": "anxiety",
        "tags": ["cbt", "cognitive", "anxiety", "technique"],
    },
    {
        "text": "For exam and academic stress: break study sessions into 25-minute focused blocks (Pomodoro technique), take 5-minute breaks, avoid all-night studying as it impairs memory consolidation. Reach out to your institution's counselor if stress feels unmanageable.",
        "category": "academic_stress",
        "tags": ["study", "academic", "students", "technique"],
    },
    {
        "text": "Workplace burnout signs: emotional exhaustion, cynicism about work, reduced productivity, physical symptoms like headaches. Steps: talk to a trusted colleague or HR, set clear boundaries on work hours, take your entitled leave, seek counseling if needed.",
        "category": "workplace_stress",
        "tags": ["burnout", "workplace", "boundaries"],
    },

    # ── HARASSMENT — VERBAL / EMOTIONAL ───────────────────────────────────────
    {
        "text": "Verbal and emotional harassment includes: repeated insults, public humiliation, threats, intimidation, and belittling. It is not normal and not your fault. Document every incident with date, time, location, and any witnesses.",
        "category": "harassment_verbal",
        "tags": ["verbal", "emotional-abuse", "documentation"],
    },
    {
        "text": "If you are experiencing workplace or institutional harassment, you have rights. Report to: internal complaints committee (ICC), your college's anti-harassment cell, or the National Commission for Women (NCW) helpline 7827170170.",
        "category": "harassment_verbal",
        "tags": ["workplace", "legal", "reporting", "india"],
    },
    {
        "text": "Gaslighting is a form of emotional manipulation where someone makes you doubt your own memory or perception. Signs: feeling confused after conversations, apologizing frequently without reason, second-guessing yourself. Trust your instincts — your feelings are valid.",
        "category": "manipulation",
        "tags": ["gaslighting", "manipulation", "awareness"],
    },

    # ── HARASSMENT — PHYSICAL ──────────────────────────────────────────────────
    {
        "text": "If you have experienced physical assault or inappropriate touching: move to safety immediately, call Emergency 112, preserve any physical evidence, document injuries with photos, and report to the nearest police station. You do not have to face this alone.",
        "category": "harassment_physical",
        "tags": ["physical", "assault", "emergency", "legal"],
    },
    {
        "text": "Physical harassment in educational institutions can be reported to: the college's Internal Complaints Committee, UGC Anti-Ragging Helpline 1800-180-5522, or police via FIR. Keep records of every incident.",
        "category": "harassment_physical",
        "tags": ["college", "institution", "reporting", "ugc"],
    },

    # ── HARASSMENT — ONLINE / CYBER ────────────────────────────────────────────
    {
        "text": "Cyberbullying and online harassment response steps: (1) Do not respond to the harasser. (2) Screenshot and save all evidence before blocking. (3) Block and report on the platform. (4) Report to cybercrime.gov.in or call 1930. (5) Tell a trusted adult.",
        "category": "harassment_online",
        "tags": ["cyberbullying", "online", "steps", "evidence"],
    },
    {
        "text": "If someone is threatening to leak your private images or videos (non-consensual intimate image abuse): do not pay any demands. Report immediately to cybercrime.gov.in (1930) and the National Commission for Women 7827170170. Legal action is available under IT Act Section 67.",
        "category": "harassment_online",
        "tags": ["image-leak", "sextortion", "legal", "cyber"],
    },
    {
        "text": "Stalking — online or offline — is a criminal offence in India under IPC Section 354D. Evidence to collect: screenshots of messages, call logs, witness names, dates and locations of incidents. Report to local police or cybercrime portal.",
        "category": "harassment_online",
        "tags": ["stalking", "legal", "evidence", "india"],
    },

    # ── THREATS / BLACKMAIL / COERCION ────────────────────────────────────────
    {
        "text": "If someone is blackmailing or threatening you: do not give in to demands (it usually escalates). Save all evidence (screenshots, messages). Report to cybercrime.gov.in or call 1930. In urgent situations call Emergency 112.",
        "category": "threat",
        "tags": ["blackmail", "threat", "emergency", "steps"],
    },
    {
        "text": "Coercion — being forced or pressured into doing something against your will — is a form of abuse. You are not responsible for what happened under coercion. Legal support: nearest police station, State Legal Aid Services, or NCW helpline 7827170170.",
        "category": "coercion",
        "tags": ["coercion", "legal", "support", "rights"],
    },

    # ── GENERAL SAFETY / SELF-CARE ─────────────────────────────────────────────
    {
        "text": "Safety planning when feeling unsafe: identify 2-3 trusted people you can call, save emergency numbers on your phone, identify safe physical spaces near you, have a go-bag ready if needed. Share your plan with someone you trust.",
        "category": "crisis",
        "tags": ["safety-plan", "prevention", "preparation"],
    },
    {
        "text": "Talking to someone about mental health or harassment does not make you weak — it takes courage. Professional counselors are bound by confidentiality. Your information will not be shared without your consent except in cases of immediate danger to life.",
        "category": "depression",
        "tags": ["stigma", "counseling", "confidentiality", "encouragement"],
    },
]

# ── Pre-compute embeddings at module load ──────────────────────────────────────
_kb_texts: List[str] = [entry["text"] for entry in KNOWLEDGE_BASE]
_kb_embeddings: Optional[np.ndarray] = None


def _get_kb_embeddings() -> np.ndarray:
    global _kb_embeddings
    if _kb_embeddings is None:
        model = _get_model()
        _kb_embeddings = model.encode(_kb_texts, convert_to_numpy=True)
    return _kb_embeddings


# ── Retriever ──────────────────────────────────────────────────────────────────

def retrieve_context(
    query: str,
    categories: List[str] = None,
    top_k: int = 3,
    min_score: float = 0.30,
) -> str:
    """
    Retrieve top-K relevant knowledge chunks for a user query.

    Args:
        query:      User's message text
        categories: Detected categories from classify_input() — used to boost relevant docs
        top_k:      Max number of chunks to return
        min_score:  Minimum cosine similarity threshold

    Returns:
        Formatted string ready to inject into system prompt.
        Empty string if nothing relevant found.
    """
    if not query or not query.strip():
        return ""

    model = _get_model()
    kb_embs = _get_kb_embeddings()

    query_emb = model.encode([query], convert_to_numpy=True)
    scores = cosine_similarity(query_emb, kb_embs)[0]

    # Category boost — if classifier detected a category, boost matching docs
    if categories:
        for i, entry in enumerate(KNOWLEDGE_BASE):
            if entry["category"] in categories:
                scores[i] = min(scores[i] + 0.15, 1.0)

    # Get top-K above threshold
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    selected = [
        KNOWLEDGE_BASE[idx]["text"]
        for idx, score in ranked[:top_k]
        if score >= min_score
    ]

    if not selected:
        return ""

    context = "\n\n---\n\n".join(selected)
    return (
        "\n\nRELEVANT KNOWLEDGE (use this to inform your response — do not quote directly):\n"
        + context
    )


def retrieve_crisis_context() -> str:
    """Always return crisis resources — called when mode == CRISIS."""
    crisis_docs = [
        entry["text"]
        for entry in KNOWLEDGE_BASE
        if entry["category"] == "crisis"
    ]
    return (
        "\n\nCRISIS RESOURCES (must reference these in your response):\n"
        + "\n\n".join(crisis_docs)
    )