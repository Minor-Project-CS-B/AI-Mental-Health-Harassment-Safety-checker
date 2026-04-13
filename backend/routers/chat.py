#chat.py

import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database.connection import get_database
from models.schemas import (
    ChatRequest, ChatResponse, ChatMessage, MessageRole,
    TokenData, EvidenceAnalysisResult, VoiceTranscriptionResult
)
from utils.security import get_current_user
from services.chat_service import (
    get_ai_reply, get_opening_message,
    analyze_evidence_image, analyze_evidence_video,
    transcribe_voice,  # ✅ FIX: yeh pehle missing tha
)
from engine.sentiment import analyze_sentiment
from engine.keywords import detect_keywords, keyword_score
from engine.classifier import classify_risk
from logger import get_chat_logger
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_chat_logger()

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/quicktime", "video/webm", "video/x-msvideo"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp4", "audio/wav", "audio/webm", "audio/x-m4a", "audio/ogg", "audio/mp3", "audio/m4a"}
MAX_FILE_SIZE_MB    = 25


# ── Opening message ────────────────────────────────────────────────────────────

@router.get("/start")
async def start_chat(current_user: TokenData = Depends(get_current_user)):
    message = await get_opening_message()
    return {"role": "assistant", "content": message, "timestamp": datetime.utcnow().isoformat()}


# ── Feature 1 + 2: Text chat (with AI-driven MCQ / emoji options) ─────────────

@router.post("/message", response_model=ChatResponse)
async def send_message(
    payload: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
):
    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Load last 20 messages for context
    raw_history = await db["chat_messages"].find(
        {"user_id": current_user.user_id},
        {"_id": 0, "role": 1, "content": 1}
    ).sort("timestamp", -1).limit(20).to_list(length=20)
    raw_history.reverse()

    history = [ChatMessage(role=MessageRole(m["role"]), content=m["content"]) for m in raw_history]

    risk_context = (
        f"Current risk level: {user.get('current_risk_level', 'low')}. "
        f"Risk score: {user.get('risk_score', 0.0):.2f}."
    )

    logger.info(f"Chat message | user={current_user.user_id} | type={payload.input_type.value}")

    ai_result = await get_ai_reply(
        history=history,
        new_user_message=payload.message,
        user_name=user["name"],
        risk_context=risk_context,
    )

    # ── Passive risk analysis ──────────────────────────────────────────────────
    sentiment    = analyze_sentiment(payload.message)
    kw_matches   = detect_keywords(payload.message)
    k_score      = keyword_score(kw_matches)
    risk_updated = False
    new_risk     = None

    if k_score >= 0.5 or sentiment.compound <= -0.5:
        old_score = user.get("risk_score", 0.0)
        blended   = round(0.3 * k_score + 0.7 * old_score, 4)
        new_risk  = classify_risk(blended)
        if new_risk.value != user.get("current_risk_level", "low"):
            await db["users"].update_one(
                {"_id": current_user.user_id},
                {"$set": {"risk_score": blended, "current_risk_level": new_risk.value}},
            )
            risk_updated = True
            logger.warning(f"Risk updated via chat | user={current_user.user_id} | {user.get('current_risk_level')} -> {new_risk.value}")

    # ── Store user message ─────────────────────────────────────────────────────
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

    # ── Store AI reply ─────────────────────────────────────────────────────────
    await db["chat_messages"].insert_one({
        "_id":       str(uuid.uuid4()),
        "user_id":   current_user.user_id,
        "role":      "assistant",
        "content":   ai_result["reply"],
        "input_type": "text",
        "timestamp": datetime.utcnow(),
    })

    await db["users"].update_one({"_id": current_user.user_id}, {"$set": {"last_active": datetime.utcnow()}})

    return ChatResponse(
        reply=ai_result["reply"],
        mcq_options=ai_result.get("mcq_options"),
        emoji_options=ai_result.get("emoji_options"),
        risk_updated=risk_updated,
        new_risk_level=new_risk,
    )


# ── Feature 3a: Upload image evidence ─────────────────────────────────────────

@router.post("/upload-evidence/image", response_model=EvidenceAnalysisResult)
async def upload_image_evidence(
    file:    UploadFile = File(...),
    context: str        = Form(default=""),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Upload an image as harassment/safety evidence.
    GPT-4o Vision analyzes it and returns risk indicators and suggested actions.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: JPEG, PNG, WebP, GIF. Got: {file.content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB.")

    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    logger.info(f"Image evidence upload | user={current_user.user_id} | file={file.filename}")

    analysis = await analyze_evidence_image(
        image_bytes=contents,
        filename=file.filename,
        user_name=user["name"],
        context=context or None,
    )

    evidence_id = str(uuid.uuid4())

    # Store evidence record in MongoDB
    await db["evidence_files"].insert_one({
        "_id":                  evidence_id,
        "user_id":              current_user.user_id,
        "file_type":            "image",
        "original_filename":    file.filename,
        "content_type":         file.content_type,
        "ai_analysis":          analysis.get("ai_analysis", ""),
        "risk_indicators":      analysis.get("risk_indicators", []),
        "is_harassment_evidence": analysis.get("is_harassment_evidence", False),
        "confidence":           analysis.get("confidence", "medium"),
        "suggested_actions":    analysis.get("suggested_actions", []),
        "uploaded_at":          datetime.utcnow(),
    })

    # Also save as a chat message so it appears in chat history
    await db["chat_messages"].insert_one({
        "_id":         str(uuid.uuid4()),
        "user_id":     current_user.user_id,
        "role":        "user",
        "content":     f"[Image uploaded as evidence: {file.filename}] {context}".strip(),
        "input_type":  "image",
        "is_evidence": True,
        "timestamp":   datetime.utcnow(),
    })

    # Store AI analysis reply in chat
    await db["chat_messages"].insert_one({
        "_id":       str(uuid.uuid4()),
        "user_id":   current_user.user_id,
        "role":      "assistant",
        "content":   f"I have analyzed the image. {analysis.get('ai_analysis', '')}",
        "input_type": "text",
        "timestamp": datetime.utcnow(),
    })

    return EvidenceAnalysisResult(
        evidence_id=evidence_id,
        file_type="image",
        original_filename=file.filename,
        ai_analysis=analysis.get("ai_analysis", ""),
        risk_indicators=analysis.get("risk_indicators", []),
        suggested_actions=analysis.get("suggested_actions", []),
        is_harassment_evidence=analysis.get("is_harassment_evidence", False),
        confidence=analysis.get("confidence", "medium"),
    )


# ── Feature 3b: Upload video evidence ─────────────────────────────────────────

@router.post("/upload-evidence/video", response_model=EvidenceAnalysisResult)
async def upload_video_evidence(
    file:    UploadFile = File(...),
    context: str        = Form(default=""),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Upload a video as harassment/safety evidence.
    AI provides guidance on preservation and next steps.
    """
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: MP4, MOV, WebM, AVI. Got: {file.content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB.")

    db   = get_database()
    user = await db["users"].find_one({"_id": current_user.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    logger.info(f"Video evidence upload | user={current_user.user_id} | file={file.filename}")

    analysis = await analyze_evidence_video(
        video_bytes=contents,
        filename=file.filename,
        user_name=user["name"],
        context=context or None,
    )

    evidence_id = str(uuid.uuid4())

    await db["evidence_files"].insert_one({
        "_id":                  evidence_id,
        "user_id":              current_user.user_id,
        "file_type":            "video",
        "original_filename":    file.filename,
        "content_type":         file.content_type,
        "ai_analysis":          analysis.get("ai_analysis", ""),
        "risk_indicators":      analysis.get("risk_indicators", []),
        "is_harassment_evidence": analysis.get("is_harassment_evidence", False),
        "confidence":           analysis.get("confidence", "medium"),
        "suggested_actions":    analysis.get("suggested_actions", []),
        "uploaded_at":          datetime.utcnow(),
    })

    await db["chat_messages"].insert_one({
        "_id":         str(uuid.uuid4()),
        "user_id":     current_user.user_id,
        "role":        "user",
        "content":     f"[Video uploaded as evidence: {file.filename}] {context}".strip(),
        "input_type":  "video",
        "is_evidence": True,
        "timestamp":   datetime.utcnow(),
    })

    await db["chat_messages"].insert_one({
        "_id":       str(uuid.uuid4()),
        "user_id":   current_user.user_id,
        "role":      "assistant",
        "content":   f"I have received your video. {analysis.get('ai_analysis', '')}",
        "input_type": "text",
        "timestamp": datetime.utcnow(),
    })

    return EvidenceAnalysisResult(
        evidence_id=evidence_id,
        file_type="video",
        original_filename=file.filename,
        ai_analysis=analysis.get("ai_analysis", ""),
        risk_indicators=analysis.get("risk_indicators", []),
        suggested_actions=analysis.get("suggested_actions", []),
        is_harassment_evidence=analysis.get("is_harassment_evidence", False),
        confidence=analysis.get("confidence", "medium"),
    )


# ── History and evidence ───────────────────────────────────────────────────────

@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    current_user: TokenData = Depends(get_current_user),
):
    db       = get_database()
    messages = await db["chat_messages"].find(
        {"user_id": current_user.user_id},
        {"_id": 0, "role": 1, "content": 1, "input_type": 1, "is_evidence": 1, "timestamp": 1},
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)
    messages.reverse()
    return {"messages": messages}


@router.get("/evidence")
async def get_evidence(current_user: TokenData = Depends(get_current_user)):
    """Returns all uploaded evidence files and their AI analysis for this user."""
    db       = get_database()
    evidence = await db["evidence_files"].find(
        {"user_id": current_user.user_id},
        {"_id": 1, "file_type": 1, "original_filename": 1, "ai_analysis": 1,
         "risk_indicators": 1, "is_harassment_evidence": 1, "suggested_actions": 1,
         "confidence": 1, "uploaded_at": 1},
    ).sort("uploaded_at", -1).to_list(length=100)

    for e in evidence:
        e["evidence_id"] = str(e.pop("_id"))

    return {"evidence": evidence, "count": len(evidence)}


# ── Feature 4: Voice/mic to text ──────────────────────────────────────────────

@router.post("/voice-to-text", response_model=VoiceTranscriptionResult)
async def voice_to_text(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Upload a voice recording. Gemini transcribes it to text.
    Accepts audio/webm, audio/webm;codecs=opus, and all common audio formats.
    Frontend should send the transcription as a regular /chat/message.
    """
    # Normalize content type — browser sends "audio/webm;codecs=opus" etc.
    raw_content_type  = file.content_type or ""
    base_content_type = raw_content_type.split(";")[0].strip().lower()

    if base_content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Allowed: MP3, MP4, WAV, WebM, M4A, OGG. Got: {raw_content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB.")

    logger.info(f"Voice transcription | user={current_user.user_id} | file={file.filename} | type={base_content_type}")

    result = await transcribe_voice(
        audio_bytes=contents,
        filename=file.filename,
        mime_type=base_content_type,
    )

    if not result.get("transcription"):
        error_detail = result.get("error", "Could not transcribe audio.")
        raise HTTPException(status_code=422, detail=f"Transcription failed: {error_detail}. Please try again or use text input.")

    return VoiceTranscriptionResult(
        transcription=result["transcription"],
        language=result.get("language", "en"),
        confidence=result.get("confidence", "high"),
    )