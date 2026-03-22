from fastapi import APIRouter, Depends
from database.connection import get_database
from models.schemas import ChatRequest, ChatResponse, ChatMessage, MessageRole, TokenData
from utils.security import get_current_user
from services.chat_service import get_ai_reply, get_opening_message
from engine.sentiment import analyze_sentiment
from engine.keywords import detect_keywords, keyword_score
from engine.classifier import classify_risk
from logger import get_chat_logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_chat_logger()


@router.get("/start")
async def start_chat(current_user: TokenData = Depends(get_current_user)):
    """
    Returns the AI's opening message for a new chat session.
    Call this when the user opens the chat page.
    """
    message = await get_opening_message()
    return {
        "role":      "assistant",
        "content":   message,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/message", response_model=ChatResponse)
async def send_message(
    payload: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """
    Main chat endpoint.
    - Stores user message
    - Gets AI reply from Claude
    - Runs background sentiment/keyword analysis on user message
    - Updates risk level if signals are significant
    - Stores assistant reply
    """
    db = get_database()

    # Fetch user info + recent chat history (last 20 messages for context)
    user = await db["users"].find_one({"_id": current_user.user_id})
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found.")

    # Load recent history for Claude context
    raw_history = await db["chat_messages"].find(
        {"user_id": current_user.user_id},
        {"_id": 0, "role": 1, "content": 1, "input_type": 1}
    ).sort("timestamp", -1).limit(20).to_list(length=20)
    raw_history.reverse()  # Chronological order

    history = [
        ChatMessage(
            role=MessageRole(m["role"]),
            content=m["content"],
        )
        for m in raw_history
    ]

    # Build risk context for Claude (not shown to user)
    risk_context = (
        f"Current risk level: {user.get('current_risk_level', 'low')}. "
        f"Risk score: {user.get('risk_score', 0.0):.2f}."
    )

    logger.info(f"Chat message | user={current_user.user_id} | input_type={payload.input_type.value} | evidence={payload.tag_evidence}")

    # Get AI reply
    ai_result = await get_ai_reply(
        history=history,
        new_user_message=payload.message,
        user_name=user["name"],
        risk_context=risk_context,
    )

    # ── Passive risk analysis on user message ──────────────────────────────────
    sentiment   = analyze_sentiment(payload.message)
    kw_matches  = detect_keywords(payload.message)
    k_score     = keyword_score(kw_matches)
    risk_updated = False
    new_risk     = None

    # Only update risk if there are strong signals (avoid noise from casual chat)
    if k_score >= 0.5 or sentiment.compound <= -0.5:
        old_score = user.get("risk_score", 0.0)
        # Blend: chat contributes less weight than a full assessment
        blended   = round(0.3 * k_score + 0.7 * old_score, 4)
        new_risk  = classify_risk(blended)

        if new_risk.value != user.get("current_risk_level", "low"):
            await db["users"].update_one(
                {"_id": current_user.user_id},
                {"$set": {"risk_score": blended, "current_risk_level": new_risk.value}},
            )
            risk_updated = True
            logger.warning(f"Risk updated via chat | user={current_user.user_id} | {user.get('current_risk_level')} → {new_risk.value} | score={blended}")

    # ── Persist user message ───────────────────────────────────────────────────
    await db["chat_messages"].insert_one({
        "_id":         str(uuid.uuid4()),
        "user_id":     current_user.user_id,
        "role":        "user",
        "content":     payload.message,
        "input_type":  payload.input_type.value,
        "is_evidence": payload.tag_evidence,
        "sentiment":   sentiment.compound,
        "timestamp":   datetime.utcnow(),
    })

    # ── Persist AI reply ───────────────────────────────────────────────────────
    await db["chat_messages"].insert_one({
        "_id":       str(uuid.uuid4()),
        "user_id":   current_user.user_id,
        "role":      "assistant",
        "content":   ai_result["reply"],
        "input_type": "text",
        "timestamp": datetime.utcnow(),
    })

    # Update last_active
    await db["users"].update_one(
        {"_id": current_user.user_id},
        {"$set": {"last_active": datetime.utcnow()}}
    )

    return ChatResponse(
        reply=ai_result["reply"],
        mcq_options=ai_result.get("mcq_options"),
        emoji_options=ai_result.get("emoji_options"),
        risk_updated=risk_updated,
        new_risk_level=new_risk,
    )


@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    current_user: TokenData = Depends(get_current_user),
):
    """Returns recent chat messages for the current user."""
    db = get_database()

    messages = await db["chat_messages"].find(
        {"user_id": current_user.user_id},
        {"_id": 0, "role": 1, "content": 1, "input_type": 1, "is_evidence": 1, "timestamp": 1},
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)

    messages.reverse()
    return {"messages": messages}


@router.get("/evidence")
async def get_evidence_messages(current_user: TokenData = Depends(get_current_user)):
    """Returns all messages the user has flagged as harassment evidence."""
    db = get_database()

    evidence = await db["chat_messages"].find(
        {"user_id": current_user.user_id, "is_evidence": True},
        {"_id": 0, "role": 1, "content": 1, "timestamp": 1},
    ).sort("timestamp", 1).to_list(length=200)

    return {"evidence": evidence, "count": len(evidence)}