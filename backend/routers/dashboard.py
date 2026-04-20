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

    # Risk score history — last 7 assessments for trend chart
    history_raw = await db["assessment_results"].find(
        {"user_id": current_user.user_id},
        {"risk_score": 1, "analyzed_at": 1, "track": 1},
    ).sort("analyzed_at", -1).limit(7).to_list(length=7)
    history_raw.reverse()

    risk_history = [
        {
            "score": round(r["risk_score"] * 100, 1),  # as percentage 0-100
            "date":  r["analyzed_at"].strftime("%d %b"),
            "track": r.get("track", "mental_health"),
        }
        for r in history_raw
    ]

    # ── Sentiment history from chat messages ───────────────────────────────────
    # Each user chat message has a "sentiment" field (VADER compound, -1 to +1).
    # We fetch the last 10, convert to 0-100 scale for the chart.
    # If no chat data exists yet, returns empty list → frontend shows placeholder.
    sentiment_raw = await db["chat_messages"].find(
        {
            "user_id":   current_user.user_id,
            "role":      "user",
            "sentiment": {"$exists": True, "$ne": None},
        },
        {"sentiment": 1, "timestamp": 1},
    ).sort("timestamp", -1).limit(10).to_list(length=10)
    sentiment_raw.reverse()

    # Convert VADER compound (-1 to 1) → mood score (0 to 100)
    # compound=-1 (very negative) → mood=0, compound=0 (neutral) → mood=50, compound=1 → mood=100
    sentiment_history = [
        {
            "mood":  round(((m["sentiment"] + 1) / 2) * 100, 1),
            "label": "negative" if m["sentiment"] <= -0.05
                     else "positive" if m["sentiment"] >= 0.05
                     else "neutral",
            "time":  m["timestamp"].strftime("%d %b"),
        }
        for m in sentiment_raw
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
        sentiment_history=sentiment_history,
    )