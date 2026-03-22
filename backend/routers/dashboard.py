from fastapi import APIRouter, Depends
from database.connection import get_database
from models.schemas import DashboardData, RiskLevel, TokenData
from utils.security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardData)
async def get_dashboard(current_user: TokenData = Depends(get_current_user)):
    """Returns all dashboard data for the logged-in user."""
    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})

    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found.")

    # Counts
    total_chats = await db["chat_messages"].count_documents(
        {"user_id": current_user.user_id, "role": "user"}
    )
    total_assessments = await db["assessment_results"].count_documents(
        {"user_id": current_user.user_id}
    )

    # Recent assessments (last 5)
    recent_raw = await db["assessment_results"].find(
        {"user_id": current_user.user_id},
        {"_id": 1, "track": 1, "risk_level": 1, "risk_score": 1, "analyzed_at": 1},
    ).sort("analyzed_at", -1).limit(5).to_list(length=5)

    recent_assessments = [
        {
            "id":          str(r["_id"]),
            "track":       r["track"],
            "risk_level":  r["risk_level"],
            "risk_score":  r["risk_score"],
            "analyzed_at": r["analyzed_at"].isoformat(),
        }
        for r in recent_raw
    ]

    # Risk history (last 7 assessments for trend chart)
    history_raw = await db["assessment_results"].find(
        {"user_id": current_user.user_id},
        {"risk_score": 1, "analyzed_at": 1},
    ).sort("analyzed_at", -1).limit(7).to_list(length=7)
    history_raw.reverse()

    risk_history = [
        {"score": r["risk_score"], "date": r["analyzed_at"].isoformat()}
        for r in history_raw
    ]

    return DashboardData(
        user_id=str(user["_id"]),
        name=user["name"],
        username=user["username"],
        email=user["email"],
        current_risk_level=RiskLevel(user.get("current_risk_level", "low")),
        risk_score=user.get("risk_score", 0.0),
        onboarding_complete=user.get("onboarding_complete", False),
        total_chats=total_chats,
        total_assessments=total_assessments,
        last_active=user.get("last_active", datetime.utcnow()),
        recent_assessments=recent_assessments,
        risk_history=risk_history,
    )