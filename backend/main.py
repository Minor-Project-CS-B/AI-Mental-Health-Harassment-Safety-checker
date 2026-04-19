#main.py
#main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from database.connection import connect_db, close_db, get_settings
from routers import auth, onboarding, assessment, chat, dashboard, Help, response
from logger.setup import configure_uvicorn_logging, get_app_logger
from logger.middleware import AccessLogMiddleware

app_logger = get_app_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_uvicorn_logging()
    app_logger.info("AIMHHC backend starting up...")
    await connect_db()
    app_logger.info("Database connected. Server ready.")
    yield
    app_logger.info("AIMHHC backend shutting down...")
    await close_db()


settings = get_settings()

app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        "AI-powered Mental Health and Harassment Safety Checker.\n\n"
        "**How to authorize in Swagger:**\n"
        "1. Register via `POST /auth/register`\n"
        "2. Click the **Authorize** 🔒 button at the top\n"
        "3. Enter your **username** and **password** → click Login\n"
        "4. All protected endpoints will now work automatically.\n\n"
        "_This tool provides support suggestions and is NOT a substitute for professional medical or legal advice._"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(AccessLogMiddleware)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(assessment.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(Help.router)
app.include_router(response.router)


# ── Custom OpenAPI schema — enables Swagger Authorize button ───────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add OAuth2 password flow so Swagger shows the Authorize button
    schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type":  "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes":   {}
                }
            }
        }
    }

    # Apply security globally to all endpoints
    for path in schema.get("paths", {}).values():
        for method in path.values():
            method.setdefault("security", [{"OAuth2PasswordBearer": []}])

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status":     "running",
        "app":        settings.app_name,
        "version":    "2.0.0",
        "disclaimer": "This tool provides AI-based support suggestions and is not a substitute for professional medical or legal advice.",
        "docs":       "http://127.0.0.1:8000/docs",
    }

    
print(settings.gemini_api_key)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}