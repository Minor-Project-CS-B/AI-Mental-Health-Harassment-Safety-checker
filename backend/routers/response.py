#response.py

"""
routers/response.py
────────────────────
API endpoints for the dynamic AI response generator.

Endpoints:
  POST /response/generate   — generate personalized response after assessment
  GET  /response/history    — get past generated responses for this user
"""

from fastapi import APIRouter, Depends, HTTPException
from database.connection import get_database
from models.schemas import (
    DynamicResponseRequest, DynamicResponseResult, TokenData
)
from utils.security import get_current_user
from services.response_service import generate_dynamic_response
from logger import get_app_logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/response", tags=["Dynamic Response Generator"])
logger = get_app_logger()


@router.post("/generate", response_model=DynamicResponseResult)
async def generate_response(
    payload: DynamicResponseRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Generates a fully personalized AI response based on:
    - User's risk level and track
    - Specific keywords/concern areas detected
    - Their actual assessment answers
    - Recent chat history

    This replaces the hardcoded static response generator.
    Falls back to static suggestions if AI call fails.
    """
    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    logger.info(
        f"Dynamic response requested | user={current_user.user_id} | "
        f"track={payload.track.value} | risk={payload.risk_level.value} | "
        f"score={payload.risk_score}"
    )

    result = await generate_dynamic_response(
        track=payload.track.value,
        risk_level=payload.risk_level.value,
        risk_score=payload.risk_score,
        matched_keywords=payload.matched_keywords or [],
        assessment_answers=payload.assessment_answers or [],
        user_id=current_user.user_id,
        user_name=user["name"],
        db=db,
    )

    # Store generated response in DB for history
    await db["generated_responses"].insert_one({
        "_id":            str(uuid.uuid4()),
        "user_id":        current_user.user_id,
        "track":          payload.track.value,
        "risk_level":     payload.risk_level.value,
        "risk_score":     payload.risk_score,
        "support_message": result.support_message,
        "suggestions":    [{"text": s.text, "category": s.category, "priority": s.priority} for s in result.suggestions],
        "coping_plan":    result.coping_plan,
        "follow_up_tip":  result.follow_up_tip,
        "generated_by":   result.generated_by,
        "created_at":     datetime.utcnow(),
    })

    logger.info(f"Dynamic response generated | user={current_user.user_id} | by={result.generated_by}")
    return result


@router.get("/history")
async def get_response_history(
    limit: int = 5,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Returns past generated responses for this user.
    Useful for the dashboard to show what was recommended previously.
    """
    db = get_database()

    responses = await db["generated_responses"].find(
        {"user_id": current_user.user_id},
        {
            "_id": 1, "track": 1, "risk_level": 1, "risk_score": 1,
            "support_message": 1, "coping_plan": 1, "follow_up_tip": 1,
            "generated_by": 1, "created_at": 1,
        }
    ).sort("created_at", -1).limit(limit).to_list(length=limit)

    for r in responses:
        r["response_id"] = str(r.pop("_id"))
        if "created_at" in r:
            r["created_at"] = r["created_at"].isoformat()

    return {"responses": responses, "count": len(responses)}


@router.get("/latest")
async def get_latest_response(current_user: TokenData = Depends(get_current_user)):
    """
    Returns the most recent generated response for this user.
    Dashboard can call this to show current personalized plan.
    """
    db = get_database()

    response = await db["generated_responses"].find_one(
        {"user_id": current_user.user_id},
        sort=[("created_at", -1)],
    )

    if not response:
        return {"response": None, "message": "No response generated yet. Complete an assessment first."}

    response["response_id"] = str(response.pop("_id"))
    if "created_at" in response:
        response["created_at"] = response["created_at"].isoformat()

    return {"response": response}