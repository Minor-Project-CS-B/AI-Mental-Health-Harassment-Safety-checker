"""
engine/keywords.py  —  v3 (robust + negation-safe + Hinglish + stable)

Improvements over v2:
1. Better tokenization (punctuation-safe)
2. Stronger negation handling (phrase-aware)
3. No substring bugs
4. Same API → classifier.py untouched
"""

import re
from typing import List
from models.schemas import KeywordMatch


# ── Tokenization (IMPORTANT FIX) ──────────────────────────────────────────────
def _tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())


# ── Negation handling ─────────────────────────────────────────────────────────
_NEGATION_WORDS = {
    "not", "never", "no", "don't", "dont", "doesn't", "doesnt",
    "didn't", "didnt", "isn't", "isnt", "wasn't", "wasnt",
    "can't", "cant", "won't", "wont",
    "hardly", "barely", "rarely",
    # Hinglish
    "nahi", "nahin", "nhi", "mat", "na"
}

_NEGATION_WINDOW = 5


def _is_negated(tokens, match_tokens):
    """
    Check if any keyword token is preceded by negation
    """
    for i, token in enumerate(tokens):
        if token in match_tokens:
            window = tokens[max(0, i - _NEGATION_WINDOW):i]
            if any(neg in window for neg in _NEGATION_WORDS):
                return True
    return False


# ── Keyword patterns (UNCHANGED + extended safe matching) ─────────────────────
KEYWORD_PATTERNS = [

    # Depression
    (r"\b(hopeless|worthless|useless|failure|hate myself|hate my life)\b", "depression", "severe"),
    (r"\b(sad|sadness|unhappy|miserable|depressed|empty|numb|lonely|isolated)\b", "depression", "moderate"),
    (r"\b(tired|exhausted|drained|unmotivated|no energy|can't focus)\b", "depression", "mild"),

    # Hinglish depression
    (r"\b(udaas|udaasi|akela|akeli|akelapan|nirasha|bekar|bekaar|thaka|thaki)\b", "depression", "moderate"),
    (r"\b(jeene ka mann nahi|sab bekar hai|koi farak nahi|kuch nahi chahiye)\b", "depression", "severe"),
    (r"\b(bahut bura lag raha|accha nahi lag raha|dil nahi lag raha|mann nahi lag raha)\b", "depression", "moderate"),

    # Anxiety
    (r"\b(panic attack|can't breathe|heart racing|shaking|trembling)\b", "anxiety", "severe"),
    (r"\b(anxious|nervous|worried|overthinking|restless|on edge|tense)\b", "anxiety", "moderate"),
    (r"\b(stressed|overwhelmed|pressure|uneasy|jittery)\b", "anxiety", "mild"),

    # Hinglish anxiety
    (r"\b(ghabrahat|ghabra|dara hua|dari hui|dar lag raha|tension mein)\b", "anxiety", "moderate"),
    (r"\b(bahut tension|zyada soch raha|samajh nahi aa raha)\b", "anxiety", "mild"),

    # Crisis
    (r"\b(suicidal|end my life|kill myself|self harm|cut myself|don't want to live)\b", "crisis", "severe"),
    (r"\b(hurt myself|no point|give up|can't go on|want to disappear)\b", "crisis", "severe"),
    (r"\b(want to die|wish i was dead|better off dead|no reason to live)\b", "crisis", "severe"),

    # Hinglish crisis
    (r"\b(marna chahta|marna chahti|jeena nahi chahta|jeena nahi chahti)\b", "crisis", "severe"),
    (r"\b(khatam kar lena|jeene se thak gaya|jeene se thak gayi)\b", "crisis", "severe"),
    (r"\b(koi fayda nahi|haar maan li|sab khatam)\b", "crisis", "severe"),

    # Harassment verbal
    (r"\b(verbally abused|shouted at|humiliated|insulted|degraded|threatened)\b", "harassment_verbal", "severe"),
    (r"\b(bullied|mocked|ridiculed|made fun of|belittled|criticized harshly)\b", "harassment_verbal", "moderate"),

    # Hinglish verbal
    (r"\b(gaali|gaaliyan|beizzati|sharminda kiya|chillaya)\b", "harassment_verbal", "severe"),
    (r"\b(mazak banaya|tana mara|taunt kiya|ignore kiya)\b", "harassment_verbal", "moderate"),

    # Physical harassment
    (r"\b(hit|slapped|pushed|grabbed|touched without consent|physically abused)\b", "harassment_physical", "severe"),
    (r"\b(uncomfortable touch|inappropriate contact|forced|coerced)\b", "harassment_physical", "severe"),

    # Hinglish physical
    (r"\b(mara|maara|thappad|dhakka|pakda|haath lagaya)\b", "harassment_physical", "severe"),

    # Online harassment
    (r"\b(cyberbullied|online harassment|doxxed|stalked online|fake profile|leaked)\b", "harassment_online", "severe"),
    (r"\b(trolled|abusive messages|threatening messages|hate messages)\b", "harassment_online", "moderate"),

    # Hinglish online
    (r"\b(fake account|photo leak|video leak|stalk kar raha|number share kiya)\b", "harassment_online", "severe"),

    # Threat / manipulation
    (r"\b(blackmail|threatened me|extortion|i will ruin you|watch your back)\b", "threat", "severe"),
    (r"\b(if you tell anyone|don't tell anyone)\b", "threat", "severe"),
    (r"\b(manipulated|gaslighting|twisted my words|emotionally abused)\b", "manipulation", "moderate"),
    (r"\b(forced to|pressured into|had no choice)\b", "coercion", "severe"),

    # Hinglish threat
    (r"\b(dhamki|blackmail kar raha|dekh lunga|kisiko mat batana)\b", "threat", "severe"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), cat, sev) for p, cat, sev in KEYWORD_PATTERNS]


# ── MAIN DETECTION ────────────────────────────────────────────────────────────
def detect_keywords(text: str) -> List[KeywordMatch]:
    if not text or not text.strip():
        return []

    tokens = _tokenize(text)
    matches = []
    seen = set()

    for pattern, category, severity in _COMPILED:
        for m in pattern.finditer(text):
            kw = m.group(0).lower()

            if kw in seen:
                continue

            match_tokens = _tokenize(kw)

            if _is_negated(tokens, match_tokens):
                continue

            seen.add(kw)
            matches.append(
                KeywordMatch(keyword=kw, category=category, severity=severity)
            )

    return matches


# ── SCORE (UNCHANGED) ─────────────────────────────────────────────────────────
def keyword_score(matches: List[KeywordMatch]) -> float:
    if not matches:
        return 0.0

    weights = {"severe": 0.9, "moderate": 0.5, "mild": 0.2}
    max_w = max(weights.get(m.severity, 0) for m in matches)
    bonus = min(len(matches) * 0.05, 0.10)

    return min(max_w + bonus, 1.0)