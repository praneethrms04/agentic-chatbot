"""Chat API routes.

Thin HTTP layer only: validate input, delegate to the service layer, and
shape the HTTP response. All business logic lives in app/services/.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.sse import sse_response
from app.graph.workflow import get_chat_graph
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    HistoryResponse,
)
from app.services import chat_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Run the LangGraph chat workflow and return the assistant reply in one body."""
    result = await chat_service.run_chat(request.thread_id, request.message)
    return ChatResponse(response=result["response"])


@router.post(
    "/chat/stream",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream the assistant reply token-by-token using Server-Sent Events (SSE).

    Event frames: TokenEvent* -> DoneEvent | ErrorEvent  (see app/schemas/chat.py).
    """
    return sse_response(
        chat_service.stream_chat_events(request.thread_id, request.message)
    )


@router.get("/chat/{thread_id}/history", response_model=HistoryResponse)
async def chat_history(thread_id: str) -> HistoryResponse:
    """Return the persisted conversation turns for a thread."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await get_chat_graph().aget_state(config)
    history: list[dict] = snapshot.values.get("history", []) if snapshot.values else []
    return HistoryResponse(
        thread_id=thread_id,
        messages=[ChatMessage(**turn) for turn in history],
    )
