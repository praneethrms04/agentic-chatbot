"""Chat services.

Business logic layer for the chat feature. Routes stay thin (HTTP concerns
only) and delegate here; everything that knows about LangGraph, threads, or
streaming events lives in this package.
"""

from collections.abc import AsyncIterator

from pydantic import BaseModel

from app.graph.workflow import get_chat_graph
from app.schemas.chat import DoneEvent, ErrorEvent, TokenEvent


def _thread_config(thread_id: str) -> dict:
    """LangGraph config scoping persistence to one conversation thread."""
    return {"configurable": {"thread_id": thread_id}}


async def run_chat(thread_id: str, message: str) -> dict:
    """Run the whole workflow once and return the final graph state."""
    result = await get_chat_graph().ainvoke({"message": message}, config=_thread_config(thread_id))
    return result


async def stream_chat_events(
    thread_id: str, message: str
) -> AsyncIterator[BaseModel]:
    """Stream the assistant reply as a sequence of typed events.

    Yields in order:
      TokenEvent* -> (DoneEvent | ErrorEvent)

    Implementation notes:
      - stream_mode="messages" emits every LLM token the instant the model
        produces it (LangGraph taps the model's callbacks inside each node).
      - stream_mode="values" emits the full state after each graph step; we
        keep only the last one to read back the authoritative final response.
      - Combining both modes makes astream yield `(mode, payload)` tuples.
    """
    collected_chunks: list[str] = []
    final_response = ""

    try:
        async for mode, payload in get_chat_graph().astream(
            {"message": message},
            config=_thread_config(thread_id),
            stream_mode=["messages", "values"],
        ):
            if mode == "messages":
                # payload is (message_chunk, metadata); we only need the text.
                chunk, _metadata = payload
                text = getattr(chunk, "text", "")
                if text:
                    collected_chunks.append(text)
                    yield TokenEvent(content=text)
            elif mode == "values":
                # Full state snapshot after a step finished.
                final_response = payload.get("response", "")

        # Prefer the state-backed response; fall back to what we streamed
        # (covers models that do not support token streaming at all).
        yield DoneEvent(response=final_response or "".join(collected_chunks))
    except Exception as exc:  # noqa: BLE001 - any failure must reach the browser
        # Emit a terminal error event so clients can stop waiting gracefully.
        yield ErrorEvent(message=str(exc))
