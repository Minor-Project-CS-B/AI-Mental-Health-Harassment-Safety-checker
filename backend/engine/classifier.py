from typing import List, Tuple
from models.schemas import AssessmentAnswer, RiskLevel, SentimentResult, KeywordMatch, TrackType
from engine.sentiment import analyze_sentiment, merge_texts
from engine.keywords import detect_keywords, keyword_score

# ── Weights ────────────────────────────────────────────────────────────────────
# Problem: harassment MCQ answers ("Always", "Not safe at all", "Strongly agree")
# are plain English — they fire ZERO keywords and score NEUTRAL in VADER.
# With old weights (S=0.30, K=0.45, Q=0.25), even all-extreme harassment answers
# gave: 0.30*0.5 + 0.45*0.0 + 0.25*1.0 = 0.40 → MEDIUM (just under HIGH at 0.45).
#
# Fix: raise questionnaire weight to 0.45 (it is the most reliable signal for MCQ),
# lower keyword weight to 0.35 (keywords matter but MCQ answers won't trigger them),
# lower sentiment to 0.20 (MCQ options are neutral English, VADER is unreliable here).

W_SENTIMENT     = 0.20
W_KEYWORDS      = 0.35
W_QUESTIONNAIRE = 0.45


def questionnaire_score(answers: List[AssessmentAnswer]) -> float:
    """Average score across all scored answers, normalized to 0.0–1.0."""
    scored = [a for a in answers if a.score is not None]
    if not scored:
        return 0.0
    return min(sum(a.score for a in scored) / (len(scored) * 4.0), 1.0)


def sentiment_to_distress(sentiment: SentimentResult) -> float:
    """Convert VADER compound (-1 to +1) to distress scale (0 to 1)."""
    return round((1.0 - sentiment.compound) / 2.0, 4)


def classify_risk(score: float) -> RiskLevel:
    if score >= 0.50:   # raised from 0.45 so medium band is wider
        return RiskLevel.high
    elif score >= 0.20: # raised from 0.15
        return RiskLevel.medium
    return RiskLevel.low


def _harassment_severity_boost(answers: List[AssessmentAnswer], q_score: float) -> float:
    """
    Track-specific boost for harassment assessments.

    Why needed: harassment questions use MCQ options like:
      "Not safe at all", "Always", "Strongly agree", "Not at all"
    These phrases contain ZERO harassment keywords and score NEUTRAL in VADER.
    So keyword_score = 0 and sentiment_score ≈ 0.5 (neutral).
    Without this boost, even all-extreme answers cap at ~0.40 (MEDIUM).

    Logic:
    - q_score >= 0.75 → user answered "Often/Always" on most questions → +0.25
    - q_score >= 0.50 → user answered "Sometimes/Often" on most questions → +0.12
    """
    if q_score >= 0.75:
        return 0.25
    elif q_score >= 0.50:
        return 0.12
    return 0.0


def run_classification(
    track: TrackType,
    answers: List[AssessmentAnswer],
    free_text: str = None,
) -> Tuple[RiskLevel, float, SentimentResult, List[KeywordMatch]]:

    text       = merge_texts(answers, free_text)
    sentiment  = analyze_sentiment(text)
    kw_matches = detect_keywords(text)

    s_score = sentiment_to_distress(sentiment)
    k_score = keyword_score(kw_matches)
    q_score = questionnaire_score(answers)

    final = (W_SENTIMENT * s_score) + (W_KEYWORDS * k_score) + (W_QUESTIONNAIRE * q_score)

    # ── Harassment-specific boost ──────────────────────────────────────────────
    # Only applied when track is harassment because mental health free-text
    # answers do contain emotional language that VADER/keywords can detect.
    # Harassment MCQ options are clinical/frequency words with no signal.
    if track == TrackType.harassment:
        boost = _harassment_severity_boost(answers, q_score)
        final = final + boost

    final = round(min(final, 1.0), 4)

    # Crisis override — always push to HIGH regardless of score
    if any(m.category == "crisis" for m in kw_matches):
        final = max(final, 0.85)

    return classify_risk(final), final, sentiment, kw_matches


# ── classify_input — lightweight wrapper for chat.py ──────────────────────────

def classify_input(text: str) -> dict:
    """
    Real-time chat message classifier.
    No questionnaire component — only sentiment + keywords.
    """
    if not text or not text.strip():
        return {"risk_score": 0.0, "categories": [], "severity": "none", "is_crisis": False}

    sentiment  = analyze_sentiment(text)
    kw_matches = detect_keywords(text)

    s_score = sentiment_to_distress(sentiment)
    k_score = keyword_score(kw_matches)

    final     = round(min((0.4 * s_score) + (0.6 * k_score), 1.0), 4)
    is_crisis = any(m.category == "crisis" for m in kw_matches)
    if is_crisis:
        final = max(final, 0.85)

    categories = list({m.category for m in kw_matches})
    severity   = "none"
    if kw_matches:
        sev_order = {"severe": 3, "moderate": 2, "mild": 1}
        severity  = max(kw_matches, key=lambda m: sev_order.get(m.severity, 0)).severity

    return {
        "risk_score": final,
        "categories": categories,
        "severity":   severity,
        "is_crisis":  is_crisis,
    }