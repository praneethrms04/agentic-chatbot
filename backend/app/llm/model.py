"""Google Gemini model factory."""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    """Return a configured Gemini chat model instance."""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to backend/.env (see .env.example)."
        )
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=settings.GEMINI_TEMPERATURE,
    )
