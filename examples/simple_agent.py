"""Example: Run a Claude tool-use agent.

Usage:
    python examples/simple_agent.py

Requires ANTHROPIC_API_KEY in .env or environment.

Demonstrates Claude's native agentic loop:
- Define tools with input_schema
- Claude decides when and how to call them
- Tool results are fed back as tool_result content blocks
- Loop continues until Claude responds with end_turn
"""

import asyncio

from dotenv import load_dotenv

from src.agents.base import AgentConfig
from src.agents.tool_use_agent import ToolUseAgent
from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool

load_dotenv()


async def main() -> None:
    config = AgentConfig(
        name="simple-agent",
        system_prompt="You are a helpful assistant that can search the web and do math.",
    )

    tools = [WebSearchTool(), CalculatorTool()]
    agent = ToolUseAgent(config, tools)

    question = "What is 42 * 17 + 3?"
    print(f"Question: {question}")

    result = await agent.run(question)
    print(f"Answer: {result.output}")
    print(f"Iterations: {result.iterations}")
    print(f"Tool calls: {len(result.tool_calls)}")
    if result.usage:
        print(f"Tokens: {result.usage}")


if __name__ == "__main__":
    asyncio.run(main())
