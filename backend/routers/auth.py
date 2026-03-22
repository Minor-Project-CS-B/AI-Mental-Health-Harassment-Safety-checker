from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database.connection import get_database, get_settings
from models.schemas import UserRegister, MagicLinkRequest, Token
from utils.security import generate_magic_token, create_session_token, get_current_user
from services.email_service import send_magic_link_email
from datetime import datetime, timedelta
from logger import get_auth_logger
import bcrypt
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_auth_logger()


# ── Password helpers ───────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── Register ───────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    """
    Step 1 of auth flow.
    Creates the user account and sends a magic login link to their email.
    """
    db       = get_database()
    settings = get_settings()

    if await db["users"].find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    if await db["users"].find_one({"username": payload.username}):
        raise HTTPException(status_code=400, detail="This username is already taken.")

    user_id  = str(uuid.uuid4())
    user_doc = {
        "_id":                 user_id,
        "name":                payload.name,
        "username":            payload.username,
        "email":               payload.email,
        "password_hash":       hash_password(payload.password),
        "onboarding_complete": False,
        "current_risk_level":  "low",
        "risk_score":          0.0,
        "created_at":          datetime.utcnow(),
        "last_active":         datetime.utcnow(),
    }
    await db["users"].insert_one(user_doc)
    logger.info(f"New user registered: username={payload.username} email={payload.email} id={user_id}")

    magic_token = generate_magic_token()
    expires_at  = datetime.utcnow() + timedelta(minutes=settings.magic_link_expire_minutes)

    await db["magic_tokens"].insert_one({
        "_id":        str(uuid.uuid4()),
        "token":      magic_token,
        "user_id":    user_id,
        "used":       False,
        "expires_at": expires_at,
    })

    magic_url = f"{settings.frontend_url}/login?token={magic_token}"
    sent = await send_magic_link_email(to_email=payload.email, name=payload.name, magic_url=magic_url)

    if not sent:
        logger.warning(f"Magic link email failed for user={user_id} email={payload.email}")
        return {"message": "Account created but email delivery failed.", "email_sent": False}

    logger.info(f"Magic link sent successfully to {payload.email}")
    return {
        "message": f"Account created! Check your email at {payload.email} for your login link.",
        "email_sent": True,
    }


# ── Login with username + password (also powers Swagger Authorize button) ──────

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Standard username + password login.
    Also used by Swagger UI's Authorize button — enter username and password there.
    Returns a JWT session token.
    """
    db   = get_database()
    user = await db["users"].find_one({"username": form_data.username})

    if not user:
        # Try by email as well
        user = await db["users"].find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["password_hash"]):
        logger.warning(f"Failed login attempt for username={form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"last_active": datetime.utcnow()}}
    )

    session_token = create_session_token(user_id=user["_id"], username=user["username"])
    logger.info(f"User logged in: username={user['username']} id={user['_id']}")
    return Token(access_token=session_token)


# ── Resend magic link ──────────────────────────────────────────────────────────

@router.post("/request-link")
async def request_magic_link(email: str):
    """Lets an existing user request a new magic link (e.g., link expired)."""
    db       = get_database()
    settings = get_settings()

    user = await db["users"].find_one({"email": email})
    if not user:
        return {"message": "If that email is registered, a login link has been sent."}

    magic_token = generate_magic_token()
    expires_at  = datetime.utcnow() + timedelta(minutes=settings.magic_link_expire_minutes)

    await db["magic_tokens"].insert_one({
        "_id":        str(uuid.uuid4()),
        "token":      magic_token,
        "user_id":    user["_id"],
        "used":       False,
        "expires_at": expires_at,
    })

    magic_url = f"{settings.frontend_url}/login?token={magic_token}"
    await send_magic_link_email(to_email=user["email"], name=user["name"], magic_url=magic_url)
    return {"message": "If that email is registered, a login link has been sent."}


# ── Verify magic link → issue session JWT ─────────────────────────────────────

@router.post("/verify-magic-link", response_model=Token)
async def verify_magic_link(payload: MagicLinkRequest):
    """
    Step 2 of magic link flow.
    Frontend sends the token from the URL → validates it → returns a session JWT.
    """
    db = get_database()

    token_doc = await db["magic_tokens"].find_one({"token": payload.token})

    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired login link.")
    if token_doc.get("used"):
        raise HTTPException(status_code=400, detail="This login link has already been used.")
    if token_doc["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This login link has expired. Please request a new one.")

    await db["magic_tokens"].update_one({"_id": token_doc["_id"]}, {"$set": {"used": True}})

    user = await db["users"].find_one({"_id": token_doc["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"last_active": datetime.utcnow()}})

    session_token = create_session_token(user_id=user["_id"], username=user["username"])
    logger.info(f"Magic link verified. Session created for user={user['_id']} username={user['username']}")
    return Token(access_token=session_token)


# ── Get current user info ──────────────────────────────────────────────────────

@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    """Returns the currently logged-in user's basic info."""
    db   = get_database()
    user = await db["users"].find_one(
        {"_id": current_user.user_id},
        {"password_hash": 0}   # never return password hash
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user["_id"] = str(user["_id"])
    return user