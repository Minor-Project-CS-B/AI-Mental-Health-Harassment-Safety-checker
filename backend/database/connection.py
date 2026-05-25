from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    mongo_uri:    str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name:      str = os.getenv("DB_NAME", "mental_health_checker")

    secret_key:                str = os.getenv("SECRET_KEY", "change-this")
    magic_link_expire_minutes: int = 30
    session_expire_minutes:    int = 1440

    gmail_user:         str = os.getenv("GMAIL_USER", "")
    gmail_app_password: str = os.getenv("GMAIL_APP_PASSWORD", "")

    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    app_name:     str = os.getenv("APP_NAME", "AIMHHC")

    groq_api_key:      str = os.getenv("GROQ_API_KEY", "")

    # Google OAuth2
    google_client_id:  str = os.getenv("GOOGLE_CLIENT_ID", "")

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings():
    return Settings()


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def connect_db():
    settings = get_settings()
    db.client = AsyncIOMotorClient(settings.mongo_uri)
    database  = db.client[settings.db_name]

    await database["users"].create_index("email",     unique=True)
    await database["users"].create_index("username",  unique=True)
    await database["users"].create_index("google_id", sparse=True)  # for Google login lookup
    await database["magic_tokens"].create_index("token", unique=True)
    await database["magic_tokens"].create_index("expires_at", expireAfterSeconds=0)
    await database["chat_messages"].create_index("user_id")
    await database["email_otps"].create_index("email")
    await database["email_otps"].create_index("expires_at", expireAfterSeconds=0)
    await database["assessment_results"].create_index("user_id")
    await database["assessment_sessions"].create_index("user_id")
    await database["generated_responses"].create_index("user_id")
    print(f"[DB] Connected → {settings.db_name}")


async def close_db():
    if db.client:
        db.client.close()
        print("[DB] Connection closed.")


def get_database():
    settings = get_settings()
    return db.client[settings.db_name]