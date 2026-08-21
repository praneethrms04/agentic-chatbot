"""Server-Sent Events (SSE) helpers.

SSE is a simple HTTP streaming protocol where the server pushes frames of
the form `data: <payload>\n\n` over a long-lived `text/event-stream`
response. Browsers (or fetch-based readers) can consume these incrementally,
which is how we stream LLM tokens to the frontend.
"""

import json
from collections.abc import AsyncIterator

from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Standard SSE frame terminator: one blank line.
SSE_DELIMITER = "\n\n"


def format_sse_frame(payload: BaseModel | dict) -> str:
    """Serialize a single event object into an SSE frame (`data: <json>\n\n`)."""
    data = (
        payload.model_dump_json()
        if isinstance(payload, BaseModel)
        else json.dumps(payload)
    )
    return f"data: {data}{SSE_DELIMITER}"


def sse_response(events: AsyncIterator[BaseModel]) -> StreamingResponse:
    """Wrap an async generator of Pydantic events into an SSE StreamingResponse.

    Headers explained:
      - Cache-Control: no-cache   -> proxies/browsers must not buffer the body.
      - Connection: keep-alive    -> keep the HTTP connection open while streaming.
      - X-Accel-Buffering: no     -> tells nginx (if deployed behind it) to
                                     disable response buffering for this route.
    """

    async def _stream() -> AsyncIterator[str]:
        async for event in events:
            yield format_sse_frame(event)

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
