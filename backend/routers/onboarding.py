from fastapi import APIRouter, Depends
from database.connection import get_database
from models.schemas import OnboardingSubmission, OnboardingResult, TokenData
from utils.security import get_current_user
from utils.questions import ONBOARDING_QUESTIONS
from engine.classifier import run_classification
from engine.sentiment import merge_texts
from models.schemas import TrackType
from datetime import datetime

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/questions")
async def get_onboarding_questions(current_user: TokenData = Depends(get_current_user)):
    """Returns the 10 general onboarding questions."""
    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})

    if user and user.get("onboarding_complete"):
        return {"already_complete": True, "message": "Onboarding already completed."}

    return {"questions": ONBOARDING_QUESTIONS}


@router.post("/submit", response_model=OnboardingResult)
async def submit_onboarding(
    payload: OnboardingSubmission,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Process onboarding answers.
    - Runs sentiment + keyword + questionnaire scoring.
    - Sets initial risk level on the user profile.
    - Marks onboarding as complete.
    """
    db = get_database()

    # Determine dominant track from answer to question ob10
    last_answer = payload.answers[-1] if payload.answers else None
    track = TrackType.mental_health
    if last_answer and "harassment" in last_answer.answer.lower():
        track = TrackType.harassment

    # Run initial classification
    risk_level, risk_score, sentiment, kw_matches = run_classification(
        track=track,
        answers=payload.answers,
        free_text=payload.free_text,
    )

    # Build a simple profile summary
    profile_summary = _build_profile_summary(risk_level, sentiment, kw_matches)

    # Update user document
    await db["users"].update_one(
        {"_id": current_user.user_id},
        {
            "$set": {
                "onboarding_complete": True,
                "current_risk_level":  risk_level.value,
                "risk_score":          risk_score,
                "onboarding_track":    track.value,
                "onboarding_at":       datetime.utcnow(),
            }
        },
    )

    # Store onboarding record
    await db["onboarding_results"].insert_one({
        "user_id":        current_user.user_id,
        "risk_level":     risk_level.value,
        "risk_score":     risk_score,
        "sentiment":      sentiment.label,
        "track":          track.value,
        "keyword_count":  len(kw_matches),
        "completed_at":   datetime.utcnow(),
    })

    return OnboardingResult(
        profile_summary=profile_summary,
        follow_up_questions=[],
        onboarding_complete=True,
    )


def _build_profile_summary(risk_level, sentiment, kw_matches) -> str:
    categories = list({m.category for m in kw_matches})

    if risk_level.value == "high":
        return (
            "Your responses suggest you may be going through a significantly difficult time. "
            "AIMHHC will check in with you regularly and make sure you have access to support."
        )
    elif risk_level.value == "medium":
        cat_str = " and ".join(categories[:2]) if categories else "stress"
        return (
            f"It looks like you're dealing with some {cat_str}. "
            "That's completely understandable — AIMHHC is here to support you."
        )
    else:
        return (
            "You seem to be in a relatively good place right now. "
            "AIMHHC will help you stay that way with regular check-ins and resources."
        )