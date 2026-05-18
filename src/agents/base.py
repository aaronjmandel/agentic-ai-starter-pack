"""Base agent interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.tools.base import BaseTool


@dataclass
class AgentConfig:
    """Configuration for an agent instance."""

    name: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""
    max_iterations: int = 10


@dataclass
class AgentResponse:
    """Structured response from an agent run."""

    output: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for all agents.

    Subclasses implement `run()` with their specific reasoning strategy
    (ReAct, chain-of-thought, plan-and-execute, etc.).
    """

    def __init__(self, config: AgentConfig, tools: list[BaseTool] | None = None) -> None:
        self.config = config
        self.tools = {tool.name: tool for tool in (tools or [])}

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

    def get_tool_descriptions(self) -> list[dict[str, str]]:
        """Return tool descriptions formatted for the LLM."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]
