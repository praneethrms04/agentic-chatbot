"""Pydantic schemas for the chat API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message."""

    message: str = Field(..., min_length=1, description="The user's message.")


class ChatResponse(BaseModel):
    """Outgoing assistant reply."""

    response: str
