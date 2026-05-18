"""Claude tool-use agent implementing the Anthropic agentic loop.

This is the canonical pattern for building agents with Claude:
1. Send messages with tool definitions to Claude
2. Claude responds with text and/or tool_use content blocks
3. Execute the requested tools
4. Feed tool_result content blocks back to Claude
5. Repeat until Claude responds with end_turn (no more tool calls)

This replaces the ReAct pattern used with OpenAI — Claude handles
tool selection natively via its Messages API, no prompt engineering
for "ACTION:" parsing needed.
"""

import logging
from typing import Any

from anthropic import AsyncAnthropic

from src.agents.base import AgentConfig, AgentResponse, BaseAgent
from src.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolUseAgent(BaseAgent):
    """Agent using Claude's native tool use via the Messages API.

    The agentic loop:
    1. Call Claude with messages + tool definitions
    2. If stop_reason == "tool_use": execute tools, append results, loop
    3. If stop_reason == "end_turn": extract final text response, return
    """

    def __init__(
        self,
        config: AgentConfig,
        tools: list[BaseTool] | None = None,
        client: AsyncAnthropic | None = None,
    ) -> None:
        super().__init__(config, tools)
        self.client = client or AsyncAnthropic()

    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Run the Claude agentic loop until end_turn or max iterations."""
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_input}]
        tool_calls: list[dict[str, Any]] = []
        thinking_text = ""

        # Build API kwargs
        api_kwargs: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": messages,
        }
        if self.config.system_prompt:
            api_kwargs["system"] = self.config.system_prompt
        if self.config.temperature is not None:
            api_kwargs["temperature"] = self.config.temperature
        if self.tools:
            api_kwargs["tools"] = self.get_tool_schemas()
        if self.config.thinking:
            api_kwargs["thinking"] = self.config.thinking

        for iteration in range(1, self.config.max_iterations + 1):
            logger.info("Iteration %d/%d", iteration, self.config.max_iterations)

            response = await self.client.messages.create(**api_kwargs)

            # Collect any thinking blocks (extended thinking feature)
            for block in response.content:
                if block.type == "thinking":
                    thinking_text += block.thinking + "\n"

            # If Claude is done (no tool calls), extract text and return
            if response.stop_reason == "end_turn":
                output = self._extract_text(response.content)
                return AgentResponse(
                    output=output,
                    tool_calls=tool_calls,
                    iterations=iteration,
                    thinking=thinking_text.strip(),
                    usage=self._extract_usage(response),
                )

            # Process tool_use blocks
            if response.stop_reason == "tool_use":
                # Append Claude's response (with tool_use blocks) as assistant turn
                messages.append({"role": "assistant", "content": response.content})

                # Execute each tool and collect results
                tool_results: list[dict[str, Any]] = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue

                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    logger.info("Tool call: %s(%s)", tool_name, tool_input)

                    if tool_name in self.tools:
                        result = await self.tools[tool_name].execute(**tool_input)
                    else:
                        result = f"Error: Unknown tool '{tool_name}'"

                    tool_calls.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result,
                        "tool_use_id": tool_use_id,
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result,
                    })

                # Append tool results as user turn (Anthropic's convention)
                messages.append({"role": "user", "content": tool_results})

                # Update messages in api_kwargs for next iteration
                api_kwargs["messages"] = messages
            else:
                # Unexpected stop reason
                logger.warning("Unexpected stop_reason: %s", response.stop_reason)
                output = self._extract_text(response.content)
                return AgentResponse(
                    output=output,
                    tool_calls=tool_calls,
                    iterations=iteration,
                    thinking=thinking_text.strip(),
                    usage=self._extract_usage(response),
                )

        return AgentResponse(
            output="Max iterations reached without a final answer.",
            tool_calls=tool_calls,
            iterations=self.config.max_iterations,
            thinking=thinking_text.strip(),
        )

    @staticmethod
    def _extract_text(content: list[Any]) -> str:
        """Extract text from Claude's response content blocks."""
        texts = [block.text for block in content if block.type == "text"]
        return "\n".join(texts)

    @staticmethod
    def _extract_usage(response: Any) -> dict[str, int]:
        """Extract token usage from the API response."""
        if hasattr(response, "usage"):
            return {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        return {}
