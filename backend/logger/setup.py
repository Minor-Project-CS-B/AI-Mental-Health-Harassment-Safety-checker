"""
logger/setup.py
───────────────
Central logging configuration for AIMHHC backend.
Creates separate log files per category with daily rotation.

Log files created inside /logs/:
    app.log       — general application events
    auth.log      — register, login, magic link events
    chat.log      — chat messages and AI responses
    assessment.log — assessment submissions and results
    error.log     — ALL errors across the entire app (aggregated)
    access.log    — every HTTP request/response
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# ── Log directory ──────────────────────────────────────────────────────────────
# Creates /logs/ folder next to /backend/ at runtime if it doesn't exist
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Format ─────────────────────────────────────────────────────────────────────
LOG_FORMAT     = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT    = "%Y-%m-%d %H:%M:%S"
ROTATE_WHEN    = "midnight"      # New file every day
BACKUP_COUNT   = 14              # Keep last 14 days of logs


def _make_handler(filename: str, level: int = logging.DEBUG) -> TimedRotatingFileHandler:
    """Creates a daily-rotating file handler for the given log file."""
    handler = TimedRotatingFileHandler(
        filename=LOG_DIR / filename,
        when=ROTATE_WHEN,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return handler


def _make_console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    """Console handler — shows INFO and above in terminal."""
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return handler


# ── Error handler (shared across all loggers) ──────────────────────────────────
_error_handler = _make_handler("error.log", level=logging.ERROR)


def get_logger(name: str, filename: str) -> logging.Logger:
    """
    Returns a named logger that writes to:
      - its own dedicated log file (all levels)
      - error.log (ERROR and above only)
      - console (INFO and above)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured — avoid duplicate handlers

    logger.setLevel(logging.DEBUG)
    logger.addHandler(_make_handler(filename))
    logger.addHandler(_error_handler)
    logger.addHandler(_make_console_handler())
    logger.propagate = False

    return logger


# ── Pre-built loggers (import these directly in routers/services) ──────────────

def get_app_logger()        -> logging.Logger: return get_logger("app",        "app.log")
def get_auth_logger()       -> logging.Logger: return get_logger("auth",       "auth.log")
def get_chat_logger()       -> logging.Logger: return get_logger("chat",       "chat.log")
def get_assessment_logger() -> logging.Logger: return get_logger("assessment", "assessment.log")
def get_access_logger()     -> logging.Logger: return get_logger("access",     "access.log")


# ── Uvicorn log capture (pipe uvicorn's own logs into our files) ───────────────

def configure_uvicorn_logging():
    """
    Redirects uvicorn's access and error logs into our log files
    so everything is in one place.
    Call this once from main.py lifespan startup.
    """
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(uvicorn_logger_name)
        uv_logger.handlers.clear()
        uv_logger.addHandler(_make_handler("app.log"))
        uv_logger.addHandler(_error_handler)
        uv_logger.addHandler(_make_console_handler())
        uv_logger.propagate = False