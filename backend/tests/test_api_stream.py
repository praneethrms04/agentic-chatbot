"""API-level tests for the SSE streaming endpoint (LLM mocked, temp SQLite DB)."""

import json

from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.core.config import settings
from app.main import app


def parse_sse_frames(body: str) -> list[dict]:
    """Extract the JSON payload of every `data:` frame in an SSE body."""
    events = []
    for line in body.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line.removeprefix("data: ")))
    return events


def test_chat_stream_emits_tokens_then_done(monkeypatch, tmp_path):
    # FakeListChatModel streams its canned response one character per token,
    # exercising the real token-by-token path without any API key or network.
    monkeypatch.setattr(
        "app.graph.nodes.get_llm",
        lambda: FakeListChatModel(responses=["hello there"]),
    )
    monkeypatch.setattr(
        settings, "CHECKPOINT_DB_PATH", str(tmp_path / "checkpoints.sqlite3")
    )

    with TestClient(app) as client:
        with client.stream(
            "POST",
            "/api/chat/stream",
            json={"message": "Hi", "thread_id": "s1"},
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            body = "".join(response.iter_text())

        events = parse_sse_frames(body)

        # Tokens first, exactly one terminal event last.
        types = [event["type"] for event in events]
        assert types[-1] == "done"
        assert types.count("done") == 1
        assert "error" not in types

        # Concatenated tokens must equal the full reply reported by "done".
        tokens = [event["content"] for event in events if event["type"] == "token"]
        assert "".join(tokens) == events[-1]["response"]

        # The streamed turn must also be persisted for the thread.
        history = client.get("/api/chat/s1/history").json()
        turns = [(m["role"], m["content"]) for m in history["messages"]]
        assert turns[-2:] == [("user", "Hi"), ("assistant", "hello there")]
