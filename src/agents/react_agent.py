"""ReAct (Reason + Act) agent implementation.

Implements the ReAct loop: the agent reasons about what to do,
selects a tool, observes the result, and repeats until it has
enough information to answer.
"""

import json
import logging
from typing import Any

from src.agents.base import AgentConfig, AgentResponse, BaseAgent
from src.prompts.loader import load_prompt
from src.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """Agent that follows the ReAct reasoning pattern.

    Each iteration:
    1. Thought — reason about the current state
    2. Action — choose a tool and arguments
    3. Observation — execute the tool and observe the result
    4. Repeat or produce a final answer
    """

    def __init__(self, config: AgentConfig, tools: list[BaseTool] | None = None) -> None:
        super().__init__(config, tools)
        self._history: list[dict[str, str]] = []

    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Run the ReAct loop until a final answer or max iterations."""
        system_prompt = load_prompt(
            "react_system",
            tools=self.get_tool_descriptions(),
            system_prompt=self.config.system_prompt,
        )

        self._history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        tool_calls: list[dict[str, Any]] = []

        for iteration in range(1, self.config.max_iterations + 1):
            logger.info("ReAct iteration %d/%d", iteration, self.config.max_iterations)

            # In a real implementation, this calls the LLM API.
            # This scaffold shows the structure — replace with actual API call.
            response_text = await self._call_llm()

            # Check if the response contains a final answer
            if "FINAL ANSWER:" in response_text:
                answer = response_text.split("FINAL ANSWER:")[-1].strip()
                return AgentResponse(
                    output=answer,
                    tool_calls=tool_calls,
                    iterations=iteration,
                )

            # Parse tool call from response
            tool_call = self._parse_tool_call(response_text)
            if tool_call and tool_call["tool"] in self.tools:
                tool = self.tools[tool_call["tool"]]
                result = await tool.execute(**tool_call.get("args", {}))
                tool_calls.append({**tool_call, "result": result})

                self._history.append({"role": "assistant", "content": response_text})
                self._history.append({"role": "user", "content": f"Observation: {result}"})
            else:
                # No valid tool call and no final answer — ask LLM to continue
                self._history.append({"role": "assistant", "content": response_text})
                self._history.append({
                    "role": "user",
                    "content": "Continue reasoning. Use a tool or provide FINAL ANSWER:",
                })

        return AgentResponse(
            output="Max iterations reached without a final answer.",
            tool_calls=tool_calls,
            iterations=self.config.max_iterations,
        )

    async def _call_llm(self) -> str:
        """Call the LLM with the current message history.

        Replace this with your actual LLM client (OpenAI, Anthropic, etc.).
        """
        # Placeholder — integrate your LLM client here
        raise NotImplementedError(
            "Replace _call_llm() with your LLM API integration. "
            "See examples/simple_agent.py for a working example."
        )

    @staticmethod
    def _parse_tool_call(text: str) -> dict[str, Any] | None:
        """Extract a tool call from the LLM response text.

        Expected format in the LLM output:
            ACTION: {"tool": "tool_name", "args": {"key": "value"}}
        """
        if "ACTION:" not in text:
            return None
        try:
            action_str = text.split("ACTION:")[-1].strip()
            return json.loads(action_str)  # type: ignore[no-any-return]
        except (json.JSONDecodeError, IndexError):
            logger.warning("Failed to parse tool call from: %s", text)
            return None
