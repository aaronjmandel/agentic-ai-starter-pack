"""Example: Claude agent with extended thinking.

Usage:
    python examples/thinking_agent.py

Requires ANTHROPIC_API_KEY in .env or environment.

Extended thinking lets Claude reason internally before responding.
The thinking output is captured separately from the final answer,
useful for debugging and understanding the agent's reasoning process.
"""

import asyncio

from dotenv import load_dotenv

from src.agents.base import AgentConfig
from src.agents.tool_use_agent import ToolUseAgent
from src.tools.calculator import CalculatorTool

load_dotenv()


async def main() -> None:
    config = AgentConfig(
        name="thinking-agent",
        max_tokens=16000,
        system_prompt="You are a precise analyst. Show your reasoning clearly.",
        thinking={"type": "enabled", "budget_tokens": 10000},
    )

    agent = ToolUseAgent(config, tools=[CalculatorTool()])

    question = (
        "A store has a 20% off sale. If an item originally costs $85 and "
        "there's an additional 10% member discount applied after the sale "
        "discount, what's the final price? Use the calculator to verify."
    )
    print(f"Question: {question}\n")

    result = await agent.run(question)

    if result.thinking:
        print("=== Claude's Thinking ===")
        print(result.thinking)
        print()

    print("=== Final Answer ===")
    print(result.output)
    print(f"\nIterations: {result.iterations}")
    print(f"Tool calls: {len(result.tool_calls)}")
    for tc in result.tool_calls:
        print(f"  {tc['tool']}({tc['input']}) → {tc['result']}")


if __name__ == "__main__":
    asyncio.run(main())
