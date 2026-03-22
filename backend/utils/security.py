from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database.connection import get_settings
from models.schemas import TokenData
import secrets

# Points to our login endpoint — this is what powers Swagger's Authorize button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ── Magic link token ───────────────────────────────────────────────────────────

def generate_magic_token() -> str:
    return secrets.token_urlsafe(48)


# ── Session JWT ───────────────────────────────────────────────────────────────

def create_session_token(user_id: str, username: str) -> str:
    settings = get_settings()
    payload  = {
        "sub":      user_id,
        "username": username,
        "exp":      datetime.utcnow() + timedelta(minutes=settings.session_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_session_token(token: str) -> Optional[TokenData]:
    settings = get_settings()
    try:
        payload  = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id  = payload.get("sub")
        username = payload.get("username")
        if not user_id:
            return None
        return TokenData(user_id=user_id, username=username)
    except JWTError:
        return None


# ── FastAPI dependency ─────────────────────────────────────────────────────────

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> TokenData:
    """Require a valid session JWT. Raises 401 if missing or invalid."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = decode_session_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data