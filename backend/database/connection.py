#connection.py


from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from functools import lru_cache

import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    mongo_uri: str = os.getenv("MONGO_URI")
    db_name: str = os.getenv("DB_NAME")

    secret_key: str = os.getenv("SECRET_KEY")
    magic_link_expire_minutes: int = 30
    session_expire_minutes: int = 1440

    gmail_user: str = os.getenv("GMAIL_USER")
    gmail_app_password: str = os.getenv("GMAIL_APP_PASSWORD")

    frontend_url: str = os.getenv("FRONTEND_URL")
    app_name: str = os.getenv("APP_NAME")

    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str = os.getenv("google_api_key")

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
    database = db.client[settings.db_name]

    # ── Indexes ────────────────────────────────────────────────────────────────
    await database["users"].create_index("email", unique=True)
    await database["users"].create_index("username", unique=True)
    await database["magic_tokens"].create_index("token", unique=True)
    await database["magic_tokens"].create_index(
        "expires_at", expireAfterSeconds=0  # TTL index — MongoDB auto-deletes expired tokens
    )
    await database["chat_messages"].create_index("user_id")
    await database["analysis_results"].create_index("user_id")
    print(f"[DB] Connected → {settings.db_name}")


async def close_db():
    if db.client:
        db.client.close()
        print("[DB] Connection closed.")


def get_database():
    settings = get_settings()
    return db.client[settings.db_name]