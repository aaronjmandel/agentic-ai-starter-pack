"""Base agent interface for Claude-powered agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.tools.base import BaseTool


@dataclass
class AgentConfig:
    """Configuration for an agent instance.

    Maps directly to Anthropic Messages API parameters.
    """

    name: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float | None = None  # None = use API default
    system_prompt: str = ""
    max_iterations: int = 10
    thinking: dict[str, Any] | None = None  # Extended thinking config


@dataclass
class AgentResponse:
    """Structured response from an agent run."""

    output: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    thinking: str = ""  # Extended thinking output, if enabled
    usage: dict[str, int] = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for Claude-powered agents.

    Subclasses implement `run()` with their specific agentic strategy.
    The system prompt is passed as a top-level parameter to the Messages
    API (not as a message role).
    """

    def __init__(self, config: AgentConfig, tools: list[BaseTool] | None = None) -> None:
        self.config = config
        self.tools = {tool.name: tool for tool in (tools or [])}

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool definitions in Anthropic's Messages API format."""
        return [tool.to_anthropic_schema() for tool in self.tools.values()]

    @abstractmethod
    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Execute the agent on the given input.

        Args:
            user_input: The user's query or instruction.
            context: Optional context dict passed through the agent run.

        Returns:
            AgentResponse with the final output and metadata.
        """
        ...
