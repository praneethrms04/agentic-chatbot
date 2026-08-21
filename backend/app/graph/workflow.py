"""LangGraph workflow assembly: START -> chatbot -> END."""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes import chatbot_node
from app.graph.persistence import checkpoint_store
from app.graph.state import ChatState


def build_graph(checkpointer=None) -> CompiledStateGraph:
    """Build and compile the chat graph, optionally with persistence."""
    graph = StateGraph(ChatState)
    graph.add_node("chatbot", chatbot_node)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)
    return graph.compile(checkpointer=checkpointer)


_chat_graph: CompiledStateGraph | None = None


async def init_chat_graph() -> None:
    """Compile the graph with the SQLite checkpointer (called at app startup)."""
    global _chat_graph
    if _chat_graph is None:
        saver = await checkpoint_store.start()
        _chat_graph = build_graph(checkpointer=saver)


async def shutdown_chat_graph() -> None:
    """Release the checkpointer connection (called at app shutdown)."""
    global _chat_graph
    await checkpoint_store.stop()
    _chat_graph = None


def get_chat_graph() -> CompiledStateGraph:
    """Return the compiled graph initialized by the app lifespan."""
    if _chat_graph is None:
        raise RuntimeError(
            "Chat graph is not initialized. The application lifespan must run first."
        )
    return _chat_graph
