#assessment.py

from fastapi import APIRouter, Depends, HTTPException
from database.connection import get_database
from models.schemas import (
    DynamicAssessmentSubmission, AssessmentResult,
    TrackType, TokenData, DynamicAssessmentSession,
)
from utils.security import get_current_user
from engine.classifier import run_classification
from services.response_service import generate_response
from services.assessment_service import generate_dynamic_questions
from logger import get_assessment_logger
from services.response_service import generate_dynamic_response
from datetime import datetime
import uuid

router = APIRouter(prefix="/assessment", tags=["Assessment"])
logger = get_assessment_logger()


# ── Generate dynamic questions (AI + RAG + chat history) ──────────────────────

@router.get("/generate/{track}", response_model=DynamicAssessmentSession)
async def generate_assessment(
    track: TrackType,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Generates a FRESH set of 10 AI + RAG personalized questions every time.

    Steps:
    1. Fetch user profile + current risk level
    2. Fetch recent chat history (last 20 messages)
    3. Pass both to GPT with RAG question bank as context
    4. Return 10 unique, personalized questions with options/scores/emojis
    """
    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Fetch recent chat history for RAG context
    chat_messages = await db["chat_messages"].find(
        {"user_id": current_user.user_id, "role": "user"},
        {"_id": 0, "role": 1, "content": 1, "timestamp": 1},
    ).sort("timestamp", -1).limit(20).to_list(length=20)
    chat_messages.reverse()

    logger.info(
        f"Generating assessment | user={current_user.user_id} | "
        f"track={track.value} | chat_msgs={len(chat_messages)}"
    )

    result = await generate_dynamic_questions(
        track=track.value,
        chat_messages=chat_messages,
        user_name=user["name"],
        user_risk_level=user.get("current_risk_level", "low"),
    )

    # Store the generated session so we can validate on submit
    await db["assessment_sessions"].insert_one({
        "_id":           result["session_id"],
        "user_id":       current_user.user_id,
        "track":         track.value,
        "questions":     result["questions"],
        "based_on_chat": result["based_on_chat"],
        "generated_at":  datetime.utcnow(),
        "submitted":     False,
    })

    return DynamicAssessmentSession(
        session_id=result["session_id"],
        track=track.value,
        questions=result["questions"],
        based_on_chat=result["based_on_chat"],
    )


# ── Submit answers → local ML analysis → risk result ──────────────────────────

@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(
    payload: DynamicAssessmentSubmission,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Accepts answers for a dynamic assessment session.
    Runs local ML pipeline (VADER + keywords + questionnaire score).
    Updates user risk level with blended score.
    """
    db = get_database()

    # Validate session belongs to this user
    session = await db["assessment_sessions"].find_one({
        "_id":     payload.session_id,
        "user_id": current_user.user_id,
    })
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found.")
    if session.get("submitted"):
        raise HTTPException(status_code=400, detail="This assessment has already been submitted.")

    # Build combined text from answers for NLP analysis
    combined_text = " ".join([a.answer for a in payload.answers if a.answer])

    # Run local ML classification
    risk_level, risk_score, sentiment, kw_matches = run_classification(
        track=payload.track,
        answers=payload.answers,
        free_text=combined_text,
    )

    response_data  = generate_response(risk_level=risk_level, track=payload.track)
    assessment_id  = str(uuid.uuid4())

    logger.info(
        f"Assessment submitted | user={current_user.user_id} | "
        f"track={payload.track.value} | risk={risk_level.value} | score={risk_score}"
    )

    # Mark session as submitted
    await db["assessment_sessions"].update_one(
        {"_id": payload.session_id},
        {"$set": {"submitted": True, "submitted_at": datetime.utcnow()}}
    )

    # Store result
    await db["assessment_results"].insert_one({
        "_id":             assessment_id,
        "user_id":         current_user.user_id,
        "session_id":      payload.session_id,
        "track":           payload.track.value,
        "risk_level":      risk_level.value,
        "risk_score":      risk_score,
        "sentiment_label": sentiment.label,
        "keyword_count":   len(kw_matches),
        "keyword_cats":    list({m.category for m in kw_matches}),
        "based_on_chat":   session.get("based_on_chat", False),
        "analyzed_at":     datetime.utcnow(),
    })

    # Blend with existing risk score (60% new, 40% old)
    user      = await db["users"].find_one({"_id": current_user.user_id})
    old_score = user.get("risk_score", 0.0) if user else 0.0
    blended   = round(0.6 * risk_score + 0.4 * old_score, 4)

    await db["users"].update_one(
        {"_id": current_user.user_id},
        {"$set": {
            "risk_score":          blended,
            "current_risk_level":  risk_level.value,
            "last_active":         datetime.utcnow(),
        }},
    )

    # ── Generate personalized AI response in background ──────────────────────
    try:
        answer_texts     = [a.answer for a in payload.answers if a.answer]
        keyword_cats     = list({m.category for m in kw_matches})
        dynamic_response = await generate_dynamic_response(
            track=payload.track.value,
            risk_level=risk_level.value,
            risk_score=risk_score,
            matched_keywords=keyword_cats,
            assessment_answers=answer_texts,
            user_id=current_user.user_id,
            user_name=user["name"] if user else "User",
            db=db,
        )
        final_suggestions   = [s.text for s in dynamic_response.suggestions]
        final_resources     = dynamic_response.resources
        final_message       = dynamic_response.support_message
        logger.info(f"Dynamic response generated by={dynamic_response.generated_by}")
    except Exception as e:
        logger.warning(f"Dynamic response failed, using static: {e}")
        final_suggestions = response_data["suggestions"]
        final_resources   = response_data["resources"]
        final_message     = response_data["support_message"]

    return AssessmentResult(
        assessment_id=assessment_id,
        track=payload.track,
        risk_level=risk_level,
        risk_score=risk_score,
        sentiment=sentiment,
        matched_keywords=kw_matches,
        suggestions=final_suggestions,
        resources=final_resources,
        support_message=final_message,
    )


# ── History ────────────────────────────────────────────────────────────────────

@router.get("/history")
async def get_assessment_history(
    limit: int = 10,
    current_user: TokenData = Depends(get_current_user),
):
    """Returns past assessment results for the current user."""
    db = get_database()

    results = await db["assessment_results"].find(
        {"user_id": current_user.user_id},
        {"_id": 1, "track": 1, "risk_level": 1, "risk_score": 1,
         "sentiment_label": 1, "based_on_chat": 1, "analyzed_at": 1},
    ).sort("analyzed_at", -1).limit(limit).to_list(length=limit)

    for r in results:
        r["assessment_id"] = str(r.pop("_id"))

    return {"history": results, "count": len(results)}