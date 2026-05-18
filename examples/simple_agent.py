"""Example: Run a simple ReAct agent with tools.

Usage:
    python examples/simple_agent.py

Requires OPENAI_API_KEY in .env or environment.
"""

import asyncio
import os

from dotenv import load_dotenv

from src.agents.base import AgentConfig
from src.agents.react_agent import ReActAgent
from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool

load_dotenv()


class SimpleAgent(ReActAgent):
    """ReAct agent wired to OpenAI's chat completions API."""

    async def _call_llm(self) -> str:
        """Call OpenAI with the current message history."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=self.config.model,
            messages=self._history,  # type: ignore[arg-type]
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.choices[0].message.content or ""


async def main() -> None:
    config = AgentConfig(
        name="simple-agent",
        model="gpt-4o",
        system_prompt="You are a helpful assistant that can search the web and do math.",
    )

    tools = [WebSearchTool(), CalculatorTool()]
    agent = SimpleAgent(config, tools)

    question = "What is 42 * 17 + 3?"
    print(f"Question: {question}")

    result = await agent.run(question)
    print(f"Answer: {result.output}")
    print(f"Iterations: {result.iterations}")
    print(f"Tool calls: {len(result.tool_calls)}")


if __name__ == "__main__":
    asyncio.run(main())
