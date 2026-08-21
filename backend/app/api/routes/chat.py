"""Chat API routes."""

from fastapi import APIRouter

from app.graph.workflow import get_chat_graph
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    HistoryResponse,
)

router = APIRouter(prefix="/api", tags=["chat"])


def _thread_config(thread_id: str) -> dict:
    """LangGraph config scoping persistence to one conversation thread."""
    return {"configurable": {"thread_id": thread_id}}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Run the LangGraph chat workflow and return the assistant reply."""
    result = await get_chat_graph().ainvoke(
        {"message": request.message},
        config=_thread_config(request.thread_id),
    )
    return ChatResponse(response=result["response"])


@router.get("/chat/{thread_id}/history", response_model=HistoryResponse)
async def chat_history(thread_id: str) -> HistoryResponse:
    """Return the persisted conversation turns for a thread."""
    snapshot = await get_chat_graph().aget_state(_thread_config(thread_id))
    history: list[dict] = snapshot.values.get("history", []) if snapshot.values else []
    return HistoryResponse(
        thread_id=thread_id,
        messages=[ChatMessage(**turn) for turn in history],
    )
