"""Tests for the LangGraph chat workflow (LLM is mocked, no API key needed)."""

from app.graph.workflow import build_graph


class FakeMessage:
    """Mimics the LangChain AIMessage interface used by the node."""

    def __init__(self, text: str) -> None:
        self.text = text


class FakeLLM:
    """Deterministic stand-in for the Gemini model."""

    def invoke(self, prompt: str) -> FakeMessage:
        return FakeMessage(f"echo: {prompt}")


def test_graph_invokes_and_populates_response(monkeypatch):
    # Patch the LLM factory so the test runs without an API key or network.
    monkeypatch.setattr("app.graph.nodes.get_llm", lambda: FakeLLM())

    graph = build_graph()
    result = graph.invoke({"message": "Hello"})

    assert result["response"] == "echo: Hello"
