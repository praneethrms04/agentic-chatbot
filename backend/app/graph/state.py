"""LangGraph state definition for the chat workflow."""

import operator
from typing import Annotated, TypedDict


class ChatState(TypedDict):
    """State flowing through the chat graph."""

    message: str
    response: str
    # Accumulated conversation turns; the checkpointer persists this per thread.
    history: Annotated[list[dict], operator.add]
