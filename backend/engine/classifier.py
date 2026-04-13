from typing import List, Tuple
from models.schemas import AssessmentAnswer, RiskLevel, SentimentResult, KeywordMatch, TrackType
from engine.sentiment import analyze_sentiment, merge_texts
from engine.keywords import detect_keywords, keyword_score

# Weights
W_SENTIMENT    = 0.30
W_KEYWORDS     = 0.45
W_QUESTIONNAIRE = 0.25


def questionnaire_score(answers: List[AssessmentAnswer]) -> float:
    scored = [a for a in answers if a.score is not None]
    if not scored:
        return 0.0
    return min(sum(a.score for a in scored) / (len(scored) * 4.0), 1.0)


def sentiment_to_distress(sentiment: SentimentResult) -> float:
    # compound: -1 (very negative) → 1 (positive); invert to distress scale
    return round((1.0 - sentiment.compound) / 2.0, 4)


def classify_risk(score: float) -> RiskLevel:
    if score >= 0.45:
        return RiskLevel.high
    elif score >= 0.15:
        return RiskLevel.medium
    return RiskLevel.low


def run_classification(
    track: TrackType,
    answers: List[AssessmentAnswer],
    free_text: str = None,
) -> Tuple[RiskLevel, float, SentimentResult, List[KeywordMatch]]:

    text         = merge_texts(answers, free_text)
    sentiment    = analyze_sentiment(text)
    kw_matches   = detect_keywords(text)

    s_score = sentiment_to_distress(sentiment)
    k_score = keyword_score(kw_matches)
    q_score = questionnaire_score(answers)

    final = (W_SENTIMENT * s_score) + (W_KEYWORDS * k_score) + (W_QUESTIONNAIRE * q_score)
    final = round(min(final, 1.0), 4)

    # Crisis override — always push to high
    if any(m.category == "crisis" for m in kw_matches):
        final = max(final, 0.85)

    return classify_risk(final), final, sentiment, kw_matches