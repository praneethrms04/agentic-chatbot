"""LangGraph workflow assembly: START -> chatbot -> END."""

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import chatbot_node
from app.graph.state import ChatState


def build_graph():
    """Build and compile the chat graph."""
    graph = StateGraph(ChatState)
    graph.add_node("chatbot", chatbot_node)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)
    return graph.compile()


# Compiled graph used by the API layer.
chat_graph = build_graph()
