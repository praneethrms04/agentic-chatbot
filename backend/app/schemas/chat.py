"""Pydantic schemas for the chat API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message."""

    message: str = Field(..., min_length=1, description="The user's message.")
    thread_id: str = Field(
        default="default",
        min_length=1,
        description="Conversation thread used for persistence.",
    )


class ChatResponse(BaseModel):
    """Outgoing assistant reply."""

    response: str


class ChatMessage(BaseModel):
    """A single persisted conversation turn."""

    role: str
    content: str


class HistoryResponse(BaseModel):
    """Persisted conversation turns for one thread."""

    thread_id: str
    messages: list[ChatMessage]
