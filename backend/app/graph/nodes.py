"""Chatbot node for the LangGraph workflow."""

from app.graph.state import ChatState
from app.llm.model import get_llm


def _build_prompt(history: list[dict], message: str) -> str:
    """Render prior turns plus the new message into a single prompt."""
    lines = [
        f"{'User' if turn['role'] == 'user' else 'Assistant'}: {turn['content']}"
        for turn in history
    ]
    lines.append(f"User: {message}")
    lines.append("Assistant:")
    return "\n".join(lines)


def chatbot_node(state: ChatState) -> ChatState:
    """Send the conversation to Gemini and store the reply in state."""
    llm = get_llm()
    history = state.get("history", [])
    ai_message = llm.invoke(_build_prompt(history, state["message"]))
    # .text normalizes both plain-string and multi-block content to a string.
    reply = ai_message.text
    return {
        "response": reply,
        "history": [
            {"role": "user", "content": state["message"]},
            {"role": "assistant", "content": reply},
        ],
    }
