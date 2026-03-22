from models.schemas import RiskLevel, TrackType, ResourceItem

# ── Support messages ───────────────────────────────────────────────────────────

MESSAGES = {
    RiskLevel.low: {
        TrackType.mental_health: "You're doing well for checking in with yourself. Small daily habits make a big difference.",
        TrackType.harassment:    "You seem safe right now. Stay aware of your surroundings and trust your instincts.",
    },
    RiskLevel.medium: {
        TrackType.mental_health: "It sounds like you're going through a tough time. You're not alone — support is available. Please consider talking to someone you trust.",
        TrackType.harassment:    "What you're experiencing sounds difficult and unfair. You deserve to feel safe. Consider speaking to a trusted person or authority.",
    },
    RiskLevel.high: {
        TrackType.mental_health: "We're genuinely concerned about your wellbeing right now. Please reach out to a mental health professional or helpline immediately. You matter and help is available right now.",
        TrackType.harassment:    "Your safety is the top priority. If you are in immediate danger, please contact emergency services (112). You are not alone — help is here.",
    },
}

# ── Suggestions ───────────────────────────────────────────────────────────────

SUGGESTIONS = {
    RiskLevel.low: {
        TrackType.mental_health: [
            "Practice 5 minutes of deep breathing daily (inhale 4s, hold 4s, exhale 4s).",
            "Keep a short gratitude journal — write 3 positive things each evening.",
            "Stay physically active: even a 20-minute walk improves mood significantly.",
            "Maintain a consistent sleep schedule for better emotional balance.",
            "Reach out to a friend or family member you haven't spoken to in a while.",
        ],
        TrackType.harassment: [
            "Be aware of your surroundings, especially in unfamiliar or isolated places.",
            "Save emergency contacts on your phone for quick access.",
            "Trust your instincts — if something feels wrong, move to a safer space.",
            "Talk to a trusted friend or family member about your experiences.",
        ],
    },
    RiskLevel.medium: {
        TrackType.mental_health: [
            "Try CBT journaling: write down a negative thought, then challenge it with evidence.",
            "Reach out to a counselor, mentor, or campus/workplace wellness program.",
            "Use grounding: name 5 things you see, 4 you can touch, 3 you hear.",
            "Limit social media if it's increasing your anxiety or feelings of inadequacy.",
            "Schedule one small enjoyable activity each day — even 10 minutes of a hobby helps.",
        ],
        TrackType.harassment: [
            "Document every incident: date, time, location, what happened, any witnesses.",
            "Speak to a trusted authority figure (teacher, HR, campus coordinator).",
            "Avoid being alone with the person causing harm if possible.",
            "Block the person on all digital platforms if harassment is online.",
            "Seek support from a counselor or peer support group.",
        ],
    },
    RiskLevel.high: {
        TrackType.mental_health: [
            "Please contact a mental health helpline immediately — see the resources below.",
            "Tell a trusted person how you're feeling right now — do not be alone.",
            "If you are in immediate danger to yourself, go to the nearest hospital emergency.",
            "Avoid alcohol and substances, which can intensify distress.",
        ],
        TrackType.harassment: [
            "If you are in immediate physical danger, call 112 (India emergency) now.",
            "Move to a safe location as soon as possible.",
            "Preserve all evidence: screenshots, messages — do not delete anything.",
            "File a complaint at the nearest police station or online at cybercrime.gov.in.",
        ],
    },
}

# ── Resources ──────────────────────────────────────────────────────────────────

RESOURCES = {
    RiskLevel.low: [
        ResourceItem(title="Vandrevala Foundation", description="24/7 mental health helpline.", contact="1860-2662-345"),
        ResourceItem(title="Mindfulness India", description="Free guided meditation and breathing exercises.", url="https://www.artofliving.org/in-en/meditation"),
    ],
    RiskLevel.medium: [
        ResourceItem(title="iCall – TISS", description="Psychosocial helpline for students and professionals.", contact="9152987821", url="https://icallhelpline.org"),
        ResourceItem(title="Vandrevala Foundation", description="24/7 mental health helpline.", contact="1860-2662-345"),
        ResourceItem(title="NIMHANS", description="National Institute of Mental Health helpline.", contact="080-46110007"),
        ResourceItem(title="Women Helpline", description="National helpline for women in distress.", contact="181"),
    ],
    RiskLevel.high: [
        ResourceItem(title="Emergency Services", description="Call immediately if you are in danger.", contact="112"),
        ResourceItem(title="iCall – TISS", description="Psychosocial helpline for students and professionals.", contact="9152987821", url="https://icallhelpline.org"),
        ResourceItem(title="Vandrevala Foundation", description="24/7 mental health helpline.", contact="1860-2662-345"),
        ResourceItem(title="Women Helpline", description="National helpline for women in distress.", contact="181"),
        ResourceItem(title="Cyber Crime Reporting", description="Report online harassment and cyberbullying.", url="https://cybercrime.gov.in"),
        ResourceItem(title="NIMHANS", description="National Institute of Mental Health helpline.", contact="080-46110007"),
    ],
}


def generate_response(risk_level: RiskLevel, track: TrackType) -> dict:
    return {
        "suggestions":     SUGGESTIONS[risk_level][track],
        "resources":       RESOURCES[risk_level],
        "support_message": MESSAGES[risk_level][track],
    }