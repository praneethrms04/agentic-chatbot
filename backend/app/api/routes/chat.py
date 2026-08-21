"""Chat API routes."""

from fastapi import APIRouter

from app.graph.workflow import chat_graph
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Run the LangGraph chat workflow and return the assistant reply."""
    result = await chat_graph.ainvoke({"message": request.message})
    return ChatResponse(response=result["response"])
