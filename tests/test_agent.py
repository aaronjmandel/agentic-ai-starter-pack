"""Tests for the ToolUseAgent with mocked Claude API."""

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.base import AgentConfig
from src.agents.tool_use_agent import ToolUseAgent
from src.tools.calculator import CalculatorTool


@dataclass
class MockTextBlock:
    type: str = "text"
    text: str = ""


@dataclass
class MockToolUseBlock:
    type: str = "tool_use"
    name: str = ""
    input: dict = None  # type: ignore[assignment]
    id: str = "tool_123"

    def __post_init__(self) -> None:
        if self.input is None:
            self.input = {}


@dataclass
class MockUsage:
    input_tokens: int = 100
    output_tokens: int = 50


@dataclass
class MockResponse:
    content: list[Any]
    stop_reason: str
    usage: MockUsage = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.usage is None:
            self.usage = MockUsage()


class TestToolUseAgent:
    async def test_simple_text_response(self) -> None:
        """Agent returns text when Claude responds with end_turn."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=MockResponse(
                content=[MockTextBlock(text="The answer is 42.")],
                stop_reason="end_turn",
            )
        )

        agent = ToolUseAgent(
            config=AgentConfig(name="test"),
            client=mock_client,
        )
        result = await agent.run("What is the meaning of life?")

        assert result.output == "The answer is 42."
        assert result.iterations == 1
        assert result.tool_calls == []

    async def test_tool_use_loop(self) -> None:
        """Agent executes tools and feeds results back to Claude."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()

        # First call: Claude requests calculator tool
        # Second call: Claude responds with final answer
        mock_client.messages.create = AsyncMock(
            side_effect=[
                MockResponse(
                    content=[
                        MockTextBlock(text="Let me calculate that."),
                        MockToolUseBlock(
                            name="calculator",
                            input={"expression": "2 + 3"},
                            id="tool_abc",
                        ),
                    ],
                    stop_reason="tool_use",
                ),
                MockResponse(
                    content=[MockTextBlock(text="The result is 5.0.")],
                    stop_reason="end_turn",
                ),
            ]
        )

        agent = ToolUseAgent(
            config=AgentConfig(name="test"),
            tools=[CalculatorTool()],
            client=mock_client,
        )
        result = await agent.run("What is 2 + 3?")

        assert result.output == "The result is 5.0."
        assert result.iterations == 2
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["tool"] == "calculator"
        assert result.tool_calls[0]["result"] == "5.0"

    async def test_max_iterations(self) -> None:
        """Agent stops after max_iterations even if Claude keeps calling tools."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()

        # Always return tool_use — agent should stop at max_iterations
        mock_client.messages.create = AsyncMock(
            return_value=MockResponse(
                content=[
                    MockToolUseBlock(
                        name="calculator",
                        input={"expression": "1+1"},
                        id="tool_loop",
                    ),
                ],
                stop_reason="tool_use",
            )
        )

        agent = ToolUseAgent(
            config=AgentConfig(name="test", max_iterations=3),
            tools=[CalculatorTool()],
            client=mock_client,
        )
        result = await agent.run("Loop forever")

        assert "Max iterations" in result.output
        assert result.iterations == 3

    async def test_unknown_tool(self) -> None:
        """Agent handles unknown tool names gracefully."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            side_effect=[
                MockResponse(
                    content=[
                        MockToolUseBlock(
                            name="nonexistent_tool",
                            input={},
                            id="tool_bad",
                        ),
                    ],
                    stop_reason="tool_use",
                ),
                MockResponse(
                    content=[MockTextBlock(text="I couldn't use that tool.")],
                    stop_reason="end_turn",
                ),
            ]
        )

        agent = ToolUseAgent(
            config=AgentConfig(name="test"),
            client=mock_client,
        )
        result = await agent.run("Use a fake tool")

        assert len(result.tool_calls) == 1
        assert "Error: Unknown tool" in result.tool_calls[0]["result"]

    async def test_system_prompt_passed(self) -> None:
        """System prompt is passed as top-level API parameter."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=MockResponse(
                content=[MockTextBlock(text="OK")],
                stop_reason="end_turn",
            )
        )

        agent = ToolUseAgent(
            config=AgentConfig(name="test", system_prompt="You are a pirate."),
            client=mock_client,
        )
        await agent.run("Hello")

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["system"] == "You are a pirate."

    async def test_usage_tracking(self) -> None:
        """Token usage is captured from the API response."""
        mock_client = MagicMock()
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=MockResponse(
                content=[MockTextBlock(text="Done")],
                stop_reason="end_turn",
                usage=MockUsage(input_tokens=200, output_tokens=75),
            )
        )

        agent = ToolUseAgent(
            config=AgentConfig(name="test"),
            client=mock_client,
        )
        result = await agent.run("Test")

        assert result.usage["input_tokens"] == 200
        assert result.usage["output_tokens"] == 75
