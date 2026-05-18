"""Base chain interface for multi-step workflows."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChainResult:
    """Result from a chain execution."""

    output: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseChain(ABC):
    """Abstract base for multi-step agent chains.

    A chain composes multiple agents and/or tools into a pipeline.
    Each step's output feeds into the next step's input.
    """

    @abstractmethod
    async def run(self, input_data: dict[str, Any]) -> ChainResult:
        """Execute the chain.

        Args:
            input_data: Input dict with chain-specific keys.

        Returns:
            ChainResult with the final output and step-by-step trace.
        """
        ...
