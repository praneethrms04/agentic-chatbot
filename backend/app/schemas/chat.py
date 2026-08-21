"""Pydantic schemas for the chat API."""

from typing import Literal

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
    """Outgoing assistant reply (non-streaming endpoint)."""

    response: str


class ChatMessage(BaseModel):
    """A single persisted conversation turn."""

    role: str
    content: str


class HistoryResponse(BaseModel):
    """Persisted conversation turns for one thread."""

    thread_id: str
    messages: list[ChatMessage]


# --- Streaming events (Server-Sent Events payloads for POST /api/chat/stream) ---
#
# The stream always ends with exactly one terminal event:
#   - "done"  on success (carries the full assembled reply), or
#   - "error" on failure.


class TokenEvent(BaseModel):
    """One incremental chunk of the assistant reply as it is generated."""

    type: Literal["token"] = "token"
    content: str


class DoneEvent(BaseModel):
    """Terminal success event carrying the complete assistant reply."""

    type: Literal["done"] = "done"
    response: str


class ErrorEvent(BaseModel):
    """Terminal failure event; the human-readable error message."""

    type: Literal["error"] = "error"
    message: str
