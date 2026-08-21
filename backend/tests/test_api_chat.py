"""API-level tests: chat persistence via lifespan + SQLite checkpointer."""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

from test_graph import FakeLLM


def test_chat_and_history_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr("app.graph.nodes.get_llm", lambda: FakeLLM())
    monkeypatch.setattr(
        settings, "CHECKPOINT_DB_PATH", str(tmp_path / "checkpoints.sqlite3")
    )

    with TestClient(app) as client:
        first = client.post("/api/chat", json={"message": "Hi", "thread_id": "t1"})
        assert first.status_code == 200
        assert first.json() == {"response": "echo: Hi"}

        second = client.post("/api/chat", json={"message": "Bye", "thread_id": "t1"})
        assert second.json()["response"] == "echo: Bye"

        history = client.get("/api/chat/t1/history")
        assert history.status_code == 200
        body = history.json()
        assert body["thread_id"] == "t1"
        assert [(m["role"], m["content"]) for m in body["messages"]] == [
            ("user", "Hi"),
            ("assistant", "echo: Hi"),
            ("user", "Bye"),
            ("assistant", "echo: Bye"),
        ]

        empty = client.get("/api/chat/t2/history")
        assert empty.status_code == 200
        assert empty.json()["messages"] == []
