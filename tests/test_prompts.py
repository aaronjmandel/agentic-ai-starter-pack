"""Tests for prompt template loading."""

from src.prompts.loader import load_prompt


class TestPromptLoader:
    def test_load_react_system(self) -> None:
        result = load_prompt(
            "react_system",
            system_prompt="You are a helpful assistant.",
            tools=[
                {"name": "calculator", "description": "Do math"},
                {"name": "search", "description": "Search the web"},
            ],
        )
        assert "You are a helpful assistant." in result
        assert "calculator" in result
        assert "search" in result
        assert "FINAL ANSWER" in result

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
        assert "concise" in result  # default style
