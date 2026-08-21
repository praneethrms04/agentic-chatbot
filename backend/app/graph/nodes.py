"""Chatbot node for the LangGraph workflow."""

from app.graph.state import ChatState
from app.llm.model import get_llm


def chatbot_node(state: ChatState) -> ChatState:
    """Send the user message to Gemini and store the reply in state."""
    llm = get_llm()
    ai_message = llm.invoke(state["message"])
    # .text normalizes both plain-string and multi-block content to a string.
    return {"response": ai_message.text}
