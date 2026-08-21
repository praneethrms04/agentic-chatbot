"""LangGraph state definition for the chat workflow."""

from typing import TypedDict


class ChatState(TypedDict):
    """State flowing through the chat graph."""

    message: str
    response: str
