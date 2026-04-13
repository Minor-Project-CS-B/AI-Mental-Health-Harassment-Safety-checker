#schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# Enums
# ══════════════════════════════════════════════════════════════════════════════

class TrackType(str, Enum):
    mental_health = "mental_health"
    harassment    = "harassment"


class RiskLevel(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"


class MessageRole(str, Enum):
    user      = "user"
    assistant = "assistant"


class ChatInputType(str, Enum):
    image  = "image"
    video  = "video"
    audio  = "audio"
    text  = "text"
    voice = "voice"
    mcq   = "mcq"
    emoji = "emoji"


# ══════════════════════════════════════════════════════════════════════════════
# Auth
# ══════════════════════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    name:     str      = Field(..., min_length=2, max_length=60)
    username: str      = Field(..., min_length=3, max_length=30)
    email:    EmailStr
    password: str      = Field(..., min_length=6)


class MagicLinkRequest(BaseModel):
    """Payload sent when user clicks the email link."""
    token: str


class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class TokenData(BaseModel):
    user_id:  Optional[str] = None
    username: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# User profile (stored in MongoDB)
# ══════════════════════════════════════════════════════════════════════════════

class UserProfile(BaseModel):
    user_id:              str
    name:                 str
    username:             str
    email:                str
    onboarding_complete:  bool       = False
    current_risk_level:   RiskLevel  = RiskLevel.low
    risk_score:           float      = 0.0
    created_at:           datetime   = Field(default_factory=datetime.utcnow)
    last_active:          datetime   = Field(default_factory=datetime.utcnow)


# ══════════════════════════════════════════════════════════════════════════════
# Onboarding assessment
# ══════════════════════════════════════════════════════════════════════════════

class OnboardingAnswer(BaseModel):
    question_id:   str
    question_text: str
    answer:        str
    score:         Optional[int] = None    # 0–4 numeric weight


class OnboardingSubmission(BaseModel):
    answers:   List[OnboardingAnswer]
    free_text: Optional[str] = None


class OnboardingResult(BaseModel):
    profile_summary: str                   # Short AI-derived summary of user state
    follow_up_questions: List[dict]        # Extra questions AI generates if needed
    onboarding_complete: bool = True


# ══════════════════════════════════════════════════════════════════════════════
# Assessment (Mental Health / Harassment track)
# ══════════════════════════════════════════════════════════════════════════════

class AssessmentAnswer(BaseModel):
    question_id:   str
    question_text: str
    answer:        str
    score:         Optional[int] = None


class AssessmentSubmission(BaseModel):
    track:   TrackType
    answers: List[AssessmentAnswer]


class SentimentResult(BaseModel):
    compound: float
    positive: float
    negative: float
    neutral:  float
    label:    str


class KeywordMatch(BaseModel):
    keyword:  str
    category: str
    severity: str


class ResourceItem(BaseModel):
    title:       str
    description: str
    contact:     Optional[str] = None
    url:         Optional[str] = None


class AssessmentResult(BaseModel):
    assessment_id:    str
    track:            TrackType
    risk_level:       RiskLevel
    risk_score:       float
    sentiment:        SentimentResult
    matched_keywords: List[KeywordMatch]
    suggestions:      List[str]
    resources:        List[ResourceItem]
    support_message:  str
    disclaimer:       str = (
        "This tool provides AI-based support suggestions and is not a substitute "
        "for professional medical or legal advice."
    )
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# ══════════════════════════════════════════════════════════════════════════════
# Chat
# ══════════════════════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role:        MessageRole
    content:     str
    input_type:  ChatInputType  = ChatInputType.text
    is_evidence: bool           = False    # User/AI flagged as harassment evidence
    timestamp:   datetime       = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message:    str
    input_type: ChatInputType = ChatInputType.text
    tag_evidence: bool        = False      # User explicitly marks this as evidence


class ChatResponse(BaseModel):
    reply:          str
    input_type:     ChatInputType = ChatInputType.text
    mcq_options:    Optional[List[str]] = None    # If AI wants to offer MCQ choices
    emoji_options:  Optional[List[str]] = None    # If AI wants emoji reaction choices
    risk_updated:   bool  = False                  # True if this chat changed risk level
    new_risk_level: Optional[RiskLevel] = None
    timestamp:      datetime = Field(default_factory=datetime.utcnow)


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════════════════════════════════════════

class DashboardData(BaseModel):
    user_id:             str
    name:                str
    username:            str
    email:               str
    current_risk_level:  RiskLevel
    risk_score:          float
    onboarding_complete: bool
    total_chats:         int
    total_assessments:   int
    last_active:         datetime
    recent_assessments:  List[dict] = []
    risk_history:        List[dict] = []    # Last 7 risk scores over time


# ══════════════════════════════════════════════════════════════════════════════
# Evidence Media
# ══════════════════════════════════════════════════════════════════════════════

class EvidenceAnalysisResult(BaseModel):
    evidence_id:       str
    file_type:         str                    # image / video / audio
    original_filename: str
    ai_analysis:       str                    # What AI found in the media
    risk_indicators:   List[str]              # Specific risk signals detected
    suggested_actions: List[str]              # What user should do with this evidence
    is_harassment_evidence: bool = False      # AI determined this is harassment evidence
    confidence:        str = "medium"         # low / medium / high
    saved_at:          datetime = Field(default_factory=datetime.utcnow)
    disclaimer: str = (
        "This AI analysis is not a legal determination. "
        "Always consult a professional before taking action."
    )


class VoiceTranscriptionResult(BaseModel):
    transcription: str
    language:      str = "en"
    confidence:    str = "high"


# ══════════════════════════════════════════════════════════════════════════════
# Dynamic Assessment (AI + RAG generated questions)
# ══════════════════════════════════════════════════════════════════════════════
 
class DynamicQuestion(BaseModel):
    id:       str
    text:     str
    options:  List[str]
    scores:   List[int]
    emoji:    List[str]
    category: str            # what aspect this question probes
    why:      str            # why AI generated this question (for explainability)
 
 
class DynamicAssessmentSession(BaseModel):
    session_id:   str
    track:        str
    questions:    List[DynamicQuestion]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    based_on_chat: bool = False    # whether chat history was used
 
 
class DynamicAssessmentSubmission(BaseModel):
    session_id: str
    track:      TrackType
    answers:    List[AssessmentAnswer]