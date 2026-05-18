"""Base tool interface for Claude's native tool use.

Tools are defined using Anthropic's tool schema format with `input_schema`
(JSON Schema). The schema is passed directly to Claude's `tools` parameter
in the Messages API.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base for agent tools.

    Subclasses define `name`, `description`, and `input_schema` which are
    sent to Claude as-is. The `execute()` method runs when Claude emits
    a `tool_use` content block.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for the tool (e.g., 'web_search')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description of what the tool does. Sent directly to Claude."""
        ...

    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for the tool's input parameters.

        Returns a dict matching Anthropic's `input_schema` format:
        {"type": "object", "properties": {...}, "required": [...]}
        """
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Run the tool with the given arguments and return a string result.

        Args:
            **kwargs: Tool-specific arguments matching the input_schema.

        Returns:
            String result fed back to Claude as a tool_result content block.
        """
        ...

    def to_anthropic_schema(self) -> dict[str, Any]:
        """Return the tool definition in Anthropic's Messages API format.

        This dict is passed directly to the `tools` parameter of
        `client.messages.create()`.
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema(),
        }
