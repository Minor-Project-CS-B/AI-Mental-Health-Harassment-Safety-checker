#setup.py

"""
logger/setup.py
Central logging configuration for SafeSpace backend.
Uses WatchedFileHandler on Linux, plain FileHandler on Windows
to avoid the WinError 32 file-locking issue with TimedRotatingFileHandler.
"""

import logging
import os
import platform
from pathlib import Path

LOG_DIR    = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
IS_WINDOWS  = platform.system() == "Windows"


def _make_handler(filename: str, level: int = logging.DEBUG) -> logging.Handler:
    """
    On Windows: use plain FileHandler (avoids WinError 32 file-locking bug
    with TimedRotatingFileHandler when uvicorn spawns subprocesses).
    On Linux/Mac: use TimedRotatingFileHandler with daily rotation.
    """
    filepath = LOG_DIR / filename

    if IS_WINDOWS:
        handler = logging.FileHandler(filepath, encoding="utf-8", delay=True)
    else:
        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(
            filename=filepath,
            when="midnight",
            backupCount=14,
            encoding="utf-8",
            delay=True,
        )

    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return handler


def _make_console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return handler


_error_handler = _make_handler("error.log", level=logging.ERROR)


def get_logger(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_make_handler(filename))
    logger.addHandler(_error_handler)
    logger.addHandler(_make_console_handler())
    logger.propagate = False
    return logger


def get_app_logger()        -> logging.Logger: return get_logger("app",        "app.log")
def get_auth_logger()       -> logging.Logger: return get_logger("auth",       "auth.log")
def get_chat_logger()       -> logging.Logger: return get_logger("chat",       "chat.log")
def get_assessment_logger() -> logging.Logger: return get_logger("assessment", "assessment.log")
def get_access_logger()     -> logging.Logger: return get_logger("access",     "access.log")


def configure_uvicorn_logging():
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv = logging.getLogger(name)
        uv.handlers.clear()
        uv.addHandler(_make_handler("app.log"))
        uv.addHandler(_error_handler)
        uv.addHandler(_make_console_handler())
        uv.propagate = False