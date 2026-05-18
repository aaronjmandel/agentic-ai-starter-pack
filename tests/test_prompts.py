"""Tests for prompt template loading."""

from src.prompts.loader import load_prompt


class TestPromptLoader:
    def test_load_system_researcher(self) -> None:
        result = load_prompt("system_researcher", domain="AI safety", depth=5)
        assert "AI safety" in result
        assert "5" in result

    def test_load_system_researcher_defaults(self) -> None:
        result = load_prompt("system_researcher")
        assert "research assistant" in result
        assert "3" in result  # default depth

    def test_load_summarize(self) -> None:
        result = load_prompt(
            "summarize",
            text="Some long text to summarize.",
            style="brief",
            max_points=3,
        )
        assert "Some long text to summarize." in result
        assert "brief" in result
        assert "3" in result

    def test_summarize_defaults(self) -> None:
        result = load_prompt("summarize", text="Test text.")
        assert "concise" in result
