"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Load backend/.env (paths are resolved relative to the backend folder).
load_dotenv(os.path.join(BACKEND_DIR, ".env"))


class Settings:
    """Central place for all environment-driven settings."""

    APP_NAME: str = "Agentic Chatbot API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-3.6-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

    # Persistence (SQLite checkpoint database for LangGraph threads)
    CHECKPOINT_DB_PATH: str = os.getenv(
        "CHECKPOINT_DB_PATH",
        os.path.join(BACKEND_DIR, "data", "checkpoints.sqlite3"),
    )

    # CORS (comma-separated list of allowed browser origins)
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]


settings = Settings()
