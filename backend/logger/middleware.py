"""
logger/middleware.py
────────────────────
FastAPI middleware that logs every incoming request and outgoing response
into access.log. Captures method, path, status code, and response time.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from logger.setup import get_access_logger

access_logger = get_access_logger()


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        # ── Log incoming request ───────────────────────────────────────────────
        client_ip = request.client.host if request.client else "unknown"
        access_logger.info(
            f"→ {request.method} {request.url.path} "
            f"| client={client_ip}"
        )

        # ── Process request ────────────────────────────────────────────────────
        try:
            response   = await call_next(request)
            duration   = round((time.perf_counter() - start_time) * 1000, 2)
            status     = response.status_code

            log_fn = access_logger.warning if status >= 400 else access_logger.info
            log_fn(
                f"← {request.method} {request.url.path} "
                f"| status={status} | {duration}ms"
            )
            return response

        except Exception as exc:
            duration = round((time.perf_counter() - start_time) * 1000, 2)
            access_logger.error(
                f"✗ {request.method} {request.url.path} "
                f"| UNHANDLED ERROR: {exc} | {duration}ms"
            )
            raise