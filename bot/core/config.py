"""
Bot service configuration using pydantic-settings.
All environment variables are loaded here.
"""

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Bot service configuration."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # WhatsApp & Meta
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    WHATSAPP_APP_SECRET: str = os.getenv("WHATSAPP_APP_SECRET", "")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Bot Identity
    BOT_NAME: str = os.getenv("BOT_NAME", "GiBi")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
