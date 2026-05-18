"""Base tool interface that all tools must implement."""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base for agent tools.

    The `name` and `description` are passed to the LLM so it knows
    what the tool does and when to use it. Keep descriptions precise
    and action-oriented.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for the tool (e.g., 'web_search')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description of what the tool does. Sent to the LLM."""
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Run the tool with the given arguments and return a string result.

        Args:
            **kwargs: Tool-specific arguments.

        Returns:
            String result to be fed back to the agent as an observation.
        """
        ...

    def to_schema(self) -> dict[str, Any]:
        """Return a JSON-schema-style description for function calling APIs."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._parameters_schema(),
            },
        }

    def _parameters_schema(self) -> dict[str, Any]:
        """Override to provide parameter schema for function calling.

        Default returns an empty object schema.
        """
        return {"type": "object", "properties": {}, "required": []}
