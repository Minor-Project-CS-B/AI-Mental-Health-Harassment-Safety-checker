import re
from typing import List
from models.schemas import KeywordMatch

KEYWORD_PATTERNS = [
    # Depression / Hopelessness
    (r"\b(hopeless|worthless|useless|failure|hate myself|hate my life)\b",              "depression",           "severe"),
    (r"\b(sad|unhappy|miserable|depressed|empty|numb|lonely|isolated)\b",               "depression",           "moderate"),
    (r"\b(tired|exhausted|drained|unmotivated|no energy|can't focus)\b",                "depression",           "mild"),
    # Anxiety / Panic
    (r"\b(panic attack|can't breathe|heart racing|shaking|trembling)\b",                "anxiety",              "severe"),
    (r"\b(anxious|nervous|worried|overthinking|restless|on edge|tense)\b",              "anxiety",              "moderate"),
    (r"\b(stressed|overwhelmed|pressure|uneasy|jittery)\b",                             "anxiety",              "mild"),
    # Crisis / Self-harm
    (r"\b(suicidal|end my life|kill myself|self harm|cut myself|don't want to live)\b", "crisis",               "severe"),
    (r"\b(hurt myself|no point|give up|can't go on|want to disappear)\b",               "crisis",               "severe"),
    # Harassment – verbal
    (r"\b(verbally abused|shouted at|humiliated|insulted|degraded|threatened)\b",       "harassment_verbal",    "severe"),
    (r"\b(bullied|mocked|ridiculed|made fun of|belittled|criticized harshly)\b",        "harassment_verbal",    "moderate"),
    # Harassment – physical
    (r"\b(hit|slapped|pushed|grabbed|touched without consent|physically abused)\b",     "harassment_physical",  "severe"),
    (r"\b(uncomfortable touch|inappropriate contact|forced|coerced)\b",                 "harassment_physical",  "severe"),
    # Harassment – online / cyber
    (r"\b(cyberbullied|online harassment|doxxed|stalked online|fake profile|leaked)\b", "harassment_online",    "severe"),
    (r"\b(trolled|abusive messages|threatening messages|hate messages|spam)\b",         "harassment_online",    "moderate"),
    # Workplace / academic
    (r"\b(work pressure|deadline|overloaded|burnout|toxic workplace|unfair treatment)\b","workplace_stress",    "moderate"),
    (r"\b(exam stress|academic pressure|failing|low grades|assignment)\b",              "academic_stress",      "mild"),
]

_COMPILED = [
    (re.compile(p, re.IGNORECASE), cat, sev)
    for p, cat, sev in KEYWORD_PATTERNS
]


def detect_keywords(text: str) -> List[KeywordMatch]:
    if not text or not text.strip():
        return []

    matches, seen = [], set()
    for pattern, category, severity in _COMPILED:
        for m in pattern.finditer(text):
            kw = m.group(0).lower()
            if kw not in seen:
                seen.add(kw)
                matches.append(KeywordMatch(keyword=kw, category=category, severity=severity))
    return matches


def keyword_score(matches: List[KeywordMatch]) -> float:
    if not matches:
        return 0.0
    weights = {"severe": 0.9, "moderate": 0.5, "mild": 0.2}
    max_w   = max(weights.get(m.severity, 0) for m in matches)
    bonus   = min(len(matches) * 0.05, 0.10)
    return min(max_w + bonus, 1.0)