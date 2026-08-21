"""Tests for the LangGraph chat workflow (LLM is mocked, no API key needed)."""

from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph.workflow import build_graph


class FakeMessage:
    """Mimics the LangChain AIMessage interface used by the node."""

    def __init__(self, text: str) -> None:
        self.text = text


class FakeLLM:
    """Deterministic stand-in for the Gemini model."""

    def invoke(self, prompt: str) -> FakeMessage:
        # Reply to the most recent user turn in the rendered transcript.
        user_lines = [line for line in prompt.splitlines() if line.startswith("User: ")]
        last_message = user_lines[-1].removeprefix("User: ")
        return FakeMessage(f"echo: {last_message}")


def test_graph_invokes_and_populates_response(monkeypatch):
    # Patch the LLM factory so the test runs without an API key or network.
    monkeypatch.setattr("app.graph.nodes.get_llm", lambda: FakeLLM())

    graph = build_graph()
    result = graph.invoke({"message": "Hello"})

    assert result["response"] == "echo: Hello"


def test_history_accumulates_across_invocations(monkeypatch, tmp_path):
    monkeypatch.setattr("app.graph.nodes.get_llm", lambda: FakeLLM())

    with SqliteSaver.from_conn_string(str(tmp_path / "checkpoints.sqlite3")) as saver:
        graph = build_graph(checkpointer=saver)
        config = {"configurable": {"thread_id": "t1"}}

        graph.invoke({"message": "Hello"}, config=config)
        graph.invoke({"message": "Again"}, config=config)

        state = graph.get_state(config)
        turns = [(turn["role"], turn["content"]) for turn in state.values["history"]]
        assert turns == [
            ("user", "Hello"),
            ("assistant", "echo: Hello"),
            ("user", "Again"),
            ("assistant", "echo: Again"),
        ]


def test_threads_are_isolated(monkeypatch, tmp_path):
    monkeypatch.setattr("app.graph.nodes.get_llm", lambda: FakeLLM())

    with SqliteSaver.from_conn_string(str(tmp_path / "checkpoints.sqlite3")) as saver:
        graph = build_graph(checkpointer=saver)
        thread_a = {"configurable": {"thread_id": "a"}}
        thread_b = {"configurable": {"thread_id": "b"}}

        graph.invoke({"message": "Hello"}, config=thread_a)
        state_b = graph.get_state(thread_b)

        assert state_b.values.get("history", []) == []
