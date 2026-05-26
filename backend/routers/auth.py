from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database.connection import get_database, get_settings
from models.schemas import UserRegister, MagicLinkRequest, Token, SendOTPRequest, VerifyOTPRequest, GoogleAuthRequest, GoogleAuthResponse, GoogleProfileComplete
from utils.security import generate_magic_token, create_session_token, get_current_user
from services.email_service import send_magic_link_email, send_otp_email
from utils.email_validator import validate_email_fully
import random
import string
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


# ── Google token verification ─────────────────────────────────────────────────

def verify_google_token(credential: str) -> dict:
    """
    Verifies the JWT credential sent by Google Identity Services.
    Returns decoded payload: {sub, email, name, picture}
    Raises HTTPException if token is invalid or expired.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        settings = get_settings()
        payload  = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.google_client_id,
        )
        return payload
    except Exception as e:
        logger.warning(f"Google token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token. Please try signing in again."
        )


# ── Register ───────────────────────────────────────────────────────────────────

# ── OTP helpers ───────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Generates a 6-digit numeric OTP."""
    return ''.join(random.choices(string.digits, k=6))


# ── Send OTP — Step 1 of registration ─────────────────────────────────────────

@router.post("/send-otp", status_code=200)
async def send_otp(payload: SendOTPRequest):
    """
    Called when user submits the registration form.
    Validates email (disposable check + MX records) BEFORE creating any account.
    If valid, sends OTP. Frontend shows OTP input box.
    """
    db = get_database()

    # ── Layer 1: Email validation (disposable + MX) ────────────────────────────
    validation = await validate_email_fully(payload.email)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["reason"])

    # ── Check duplicates early ─────────────────────────────────────────────────
    if await db["users"].find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    if await db["users"].find_one({"username": payload.username}):
        raise HTTPException(status_code=400, detail="This username is already taken.")

    # ── Generate and store OTP ─────────────────────────────────────────────────
    otp        = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Overwrite any existing OTP for this email (user may be retrying)
    await db["email_otps"].delete_many({"email": payload.email})
    await db["email_otps"].insert_one({
        "_id":        str(uuid.uuid4()),
        "email":      payload.email,
        "otp":        otp,
        "used":       False,
        "expires_at": expires_at,
        "created_at": datetime.utcnow(),
    })

    # ── Send OTP email ─────────────────────────────────────────────────────────
    sent = await send_otp_email(to_email=payload.email, name=payload.name, otp=otp)
    if not sent:
        raise HTTPException(status_code=500, detail="Could not send verification email. Please try again.")

    logger.info(f"OTP sent to {payload.email}")
    return {"message": f"Verification code sent to {payload.email}. Please check your inbox."}


# ── Verify OTP + Create Account — Step 2 of registration ──────────────────────

@router.post("/verify-otp", status_code=status.HTTP_201_CREATED)
async def verify_otp_and_register(payload: VerifyOTPRequest):
    """
    Called when user submits the 6-digit OTP.
    Verifies OTP → creates account → sends magic login link.
    """
    db       = get_database()
    settings = get_settings()

    # ── Find OTP record ────────────────────────────────────────────────────────
    otp_doc = await db["email_otps"].find_one({"email": payload.email})

    if not otp_doc:
        raise HTTPException(status_code=400, detail="No verification code found. Please restart registration.")

    if otp_doc.get("used"):
        raise HTTPException(status_code=400, detail="This verification code has already been used.")

    if otp_doc["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")

    if otp_doc["otp"] != payload.otp.strip():
        raise HTTPException(status_code=400, detail="Incorrect verification code. Please check and try again.")

    # ── Mark OTP as used ──────────────────────────────────────────────────────
    await db["email_otps"].update_one({"_id": otp_doc["_id"]}, {"$set": {"used": True}})

    # ── Final duplicate checks ─────────────────────────────────────────────────
    if await db["users"].find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    if await db["users"].find_one({"username": payload.username}):
        raise HTTPException(status_code=400, detail="This username is already taken.")

    # ── Create user account ────────────────────────────────────────────────────
    user_id  = str(uuid.uuid4())
    user_doc = {
        "_id":                 user_id,
        "name":                payload.name,
        "username":            payload.username,
        "email":               payload.email,
        "password_hash":       hash_password(payload.password),
        "email_verified":      True,
        "google_id":           None,
        "auth_method":         "manual",
        "onboarding_complete": False,
        "current_risk_level":  "low",
        "risk_score":          0.0,
        "created_at":          datetime.utcnow(),
        "last_active":         datetime.utcnow(),
    }
    await db["users"].insert_one(user_doc)
    logger.info(f"Verified registration: username={payload.username} email={payload.email}")

    # ── Send magic login link ──────────────────────────────────────────────────
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
    await send_magic_link_email(to_email=payload.email, name=payload.name, magic_url=magic_url)

    return {
        "message":    "Email verified! Your account is created. Check your email for the login link.",
        "email_sent": True,
    }


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


# ── Google Auth — Login or detect new user ─────────────────────────────────────
 
@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(payload: GoogleAuthRequest):
    """
    Called after user clicks 'Continue with Google' on Login OR Register page.
 
    Two outcomes:
    1. Existing user (google_id found OR email found) → issue JWT → status="logged_in"
    2. New user → status="needs_profile" → frontend redirects to /complete-profile
       where user sets username + password. Email and name are pre-filled from Google.
    """
    db = get_database()
 
    google_data = verify_google_token(payload.credential)
 
    google_id = google_data["sub"]           # unique Google user ID
    email     = google_data["email"]
    name      = google_data.get("name", "")
    avatar    = google_data.get("picture", None)
 
    # ── Case 1: User already linked by google_id ──────────────────────────────
    user = await db["users"].find_one({"google_id": google_id})
 
    # ── Case 2: User registered manually with same email ─────────────────────
    if not user:
        user = await db["users"].find_one({"email": email})
        if user:
            # Link their Google ID so future Google logins work instantly
            await db["users"].update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "google_id":  google_id,
                    "avatar":     avatar,
                    "last_active": datetime.utcnow(),
                }}
            )
            logger.info(f"Google linked to existing manual account: {email}")
 
    if user:
        # Returning user — issue session token
        await db["users"].update_one({"_id": user["_id"]}, {"$set": {"last_active": datetime.utcnow()}})
        session_token = create_session_token(user_id=user["_id"], username=user["username"])
        logger.info(f"Google login success: {email}")
        return GoogleAuthResponse(
            status="logged_in",
            access_token=session_token,
        )
 
    # ── Case 3: Brand new user — needs to complete profile ────────────────────
    logger.info(f"New Google user needs profile completion: {email}")
    return GoogleAuthResponse(
        status="needs_profile",
        google_id=google_id,
        email=email,
        name=name,
    )
 
 
# ── Complete Google Profile — called from CompleteProfile page ─────────────────
 
@router.post("/google/complete-profile", response_model=Token)
async def google_complete_profile(payload: GoogleProfileComplete):
    """
    New Google users submit username + password to complete registration.
    Email and name already came from Google in the previous step.
    """
    db = get_database()
 
    # Double-check: google_id not already registered
    if await db["users"].find_one({"google_id": payload.google_id}):
        raise HTTPException(status_code=400, detail="This Google account is already registered. Please log in.")
 
    if await db["users"].find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
 
    if await db["users"].find_one({"username": payload.username}):
        raise HTTPException(status_code=400, detail="This username is already taken. Please choose another.")
 
    user_id  = str(uuid.uuid4())
    user_doc = {
        "_id":                 user_id,
        "name":                payload.name,
        "username":            payload.username,
        "email":               payload.email,
        "password_hash":       hash_password(payload.password),
        "google_id":           payload.google_id,
        "auth_method":         "google",
        "onboarding_complete": False,
        "current_risk_level":  "low",
        "risk_score":          0.0,
        "created_at":          datetime.utcnow(),
        "last_active":         datetime.utcnow(),
    }
    await db["users"].insert_one(user_doc)
    logger.info(f"Google profile completed: username={payload.username} email={payload.email}")
 
    session_token = create_session_token(user_id=user_id, username=payload.username)
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