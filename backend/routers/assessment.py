from fastapi import APIRouter, Depends
from database.connection import get_database
from models.schemas import (
    AssessmentSubmission, AssessmentResult, TrackType, TokenData
)
from utils.security import get_current_user
from engine.classifier import run_classification
from engine.response_generator import generate_response
from logger import get_assessment_logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/assessment", tags=["Assessment"])
logger = get_assessment_logger()

# ── Question Banks ─────────────────────────────────────────────────────────────

MENTAL_HEALTH_QUESTIONS = [
    {"id": "mh1",  "text": "How often have you felt hopeless or helpless in the past 2 weeks?",
     "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0,1,2,3,4],
     "emoji": ["😊","🙂","😐","😟","😢"]},
    {"id": "mh2",  "text": "How would you describe your energy levels lately?",
     "options": ["Very high", "Moderate", "Low", "Very low", "Completely drained"], "scores": [0,1,2,3,4],
     "emoji": ["⚡","🙂","😐","😔","😩"]},
    {"id": "mh3",  "text": "How often do you feel anxious or worried without a clear reason?",
     "options": ["Never", "Rarely", "Sometimes", "Often", "Almost always"], "scores": [0,1,2,3,4],
     "emoji": ["😊","🙂","😐","😰","😱"]},
    {"id": "mh4",  "text": "How well have you been sleeping recently?",
     "options": ["Very well", "Mostly fine", "Disturbed", "Poorly", "Hardly at all"], "scores": [0,1,2,3,4],
     "emoji": ["😴","🙂","😐","😔","😩"]},
    {"id": "mh5",  "text": "Have you lost interest in activities you used to enjoy?",
     "options": ["Not at all", "Slightly", "Moderately", "Mostly", "Completely"], "scores": [0,1,2,3,4],
     "emoji": ["😊","🙂","😐","😟","😢"]},
    {"id": "mh6",  "text": "How often do you feel overwhelmed by everyday tasks?",
     "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0,1,2,3,4],
     "emoji": ["😊","🙂","😐","😟","😩"]},
    {"id": "mh7",  "text": "How well are you able to concentrate on work or studies?",
     "options": ["Very well", "Mostly fine", "Somewhat difficult", "Very difficult", "Cannot focus at all"],
     "scores": [0,1,2,3,4], "emoji": ["🧠","🙂","😐","😟","😩"]},
    {"id": "mh8",  "text": "Do you feel connected to and supported by people around you?",
     "options": ["Very connected", "Mostly yes", "Somewhat", "Not really", "Completely isolated"],
     "scores": [0,1,2,3,4], "emoji": ["🤗","🙂","😐","😔","😞"]},
    {"id": "mh9",  "text": "How often have you had thoughts of harming yourself?",
     "options": ["Never", "A fleeting thought", "Occasionally", "Often", "Very frequently"],
     "scores": [0,1,2,3,4], "emoji": ["😊","🙂","😐","😟","🚨"]},
    {"id": "mh10", "text": "Overall, how would you rate your mental health right now?",
     "options": ["Excellent", "Good", "Fair", "Poor", "Very poor"], "scores": [0,1,2,3,4],
     "emoji": ["😊","🙂","😐","😔","😢"]},
]

HARASSMENT_QUESTIONS = [
    {"id": "hr1",  "text": "Have you experienced verbal abuse, insults, or humiliation recently?",
     "options": ["Never", "Once", "Sometimes", "Regularly", "Very frequently"], "scores": [0,1,2,3,4],
     "emoji": ["😊","😐","😟","😠","😡"]},
    {"id": "hr2",  "text": "Have you received threatening or abusive messages online?",
     "options": ["Never", "Once", "A few times", "Often", "Constantly"], "scores": [0,1,2,3,4],
     "emoji": ["😊","😐","😟","😨","🚨"]},
    {"id": "hr3",  "text": "Have you felt physically unsafe or threatened by someone?",
     "options": ["Never", "Once", "Sometimes", "Often", "Always"], "scores": [0,1,2,3,4],
     "emoji": ["😊","😐","😟","😨","😱"]},
    {"id": "hr4",  "text": "Has anyone shared private information or images of you without consent?",
     "options": ["No", "I'm not sure", "Yes, once", "Yes, multiple times", "Yes, it's ongoing"],
     "scores": [0,1,2,3,4], "emoji": ["😊","😐","😟","😠","🚨"]},
    {"id": "hr5",  "text": "Have you been followed, watched, or stalked (online or offline)?",
     "options": ["Never", "I'm unsure", "Once", "Sometimes", "Frequently"], "scores": [0,1,2,3,4],
     "emoji": ["😊","😐","😟","😨","😱"]},
    {"id": "hr6",  "text": "Have you been discriminated against or treated unfairly at your institution?",
     "options": ["Never", "Rarely", "Sometimes", "Often", "Very frequently"], "scores": [0,1,2,3,4],
     "emoji": ["😊","🙂","😐","😟","😠"]},
    {"id": "hr7",  "text": "Do you feel you can report harassment to someone in authority?",
     "options": ["Yes, easily", "Probably yes", "Unsure", "Probably not", "Definitely not"],
     "scores": [0,1,2,3,4], "emoji": ["😊","🙂","😐","😟","😔"]},
    {"id": "hr8",  "text": "Has the harassment affected your daily routine or sense of safety?",
     "options": ["Not at all", "Slightly", "Moderately", "Significantly", "Completely"],
     "scores": [0,1,2,3,4], "emoji": ["😊","🙂","😐","😟","😢"]},
    {"id": "hr9",  "text": "Have you lost sleep or experienced anxiety because of the situation?",
     "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0,1,2,3,4],
     "emoji": ["😴","🙂","😐","😰","😱"]},
    {"id": "hr10", "text": "Do you currently feel safe where you are right now?",
     "options": ["Yes, completely safe", "Mostly safe", "Somewhat unsafe", "Quite unsafe", "Not safe at all"],
     "scores": [0,1,2,3,4], "emoji": ["😊","🙂","😐","😟","🚨"]},
]


@router.get("/questions/{track}")
async def get_questions(
    track: TrackType,
    current_user: TokenData = Depends(get_current_user),
):
    questions = (
        MENTAL_HEALTH_QUESTIONS if track == TrackType.mental_health else HARASSMENT_QUESTIONS
    )
    return {"track": track, "questions": questions}


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(
    payload: AssessmentSubmission,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Run local ML analysis on assessment answers.
    Updates the user's risk level and stores the result.
    """
    db = get_database()

    risk_level, risk_score, sentiment, kw_matches = run_classification(
        track=payload.track,
        answers=payload.answers,
    )

    response_data  = generate_response(risk_level=risk_level, track=payload.track)
    assessment_id  = str(uuid.uuid4())

    logger.info(f"Assessment submitted | user={current_user.user_id} | track={payload.track.value} | risk={risk_level.value} | score={risk_score}")

    # Store result
    await db["assessment_results"].insert_one({
        "_id":             assessment_id,
        "user_id":         current_user.user_id,
        "track":           payload.track.value,
        "risk_level":      risk_level.value,
        "risk_score":      risk_score,
        "sentiment_label": sentiment.label,
        "keyword_count":   len(kw_matches),
        "keyword_cats":    list({m.category for m in kw_matches}),
        "analyzed_at":     datetime.utcnow(),
    })

    # Update user risk level (weighted: 60% latest assessment, 40% existing)
    user = await db["users"].find_one({"_id": current_user.user_id})
    old_score   = user.get("risk_score", 0.0) if user else 0.0
    blended     = round(0.6 * risk_score + 0.4 * old_score, 4)

    await db["users"].update_one(
        {"_id": current_user.user_id},
        {"$set": {"risk_score": blended, "current_risk_level": risk_level.value, "last_active": datetime.utcnow()}},
    )

    return AssessmentResult(
        assessment_id=assessment_id,
        track=payload.track,
        risk_level=risk_level,
        risk_score=risk_score,
        sentiment=sentiment,
        matched_keywords=kw_matches,
        suggestions=response_data["suggestions"],
        resources=response_data["resources"],
        support_message=response_data["support_message"],
    )