import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from models.schemas import SentimentResult

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> SentimentResult:
    if not text or not text.strip():
        return SentimentResult(compound=0.0, positive=0.0, negative=0.0, neutral=1.0, label="neutral")

    scores  = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return SentimentResult(
        compound=round(compound, 4),
        positive=round(scores["pos"], 4),
        negative=round(scores["neg"], 4),
        neutral=round(scores["neu"],  4),
        label=label,
    )


def merge_texts(answers: list, free_text: str = None) -> str:
    parts = [a.answer for a in answers if a.answer]
    if free_text:
        parts.append(free_text)
    return " ".join(parts)