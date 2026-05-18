"""Example: Run the research chain.

Usage:
    python examples/research_chain.py

Demonstrates a multi-step chain: search → synthesize → summarize.
"""

import asyncio
import os

from dotenv import load_dotenv

from src.agents.base import AgentConfig
from src.chains.research_chain import ResearchChain

load_dotenv()


# Reuse the SimpleAgent from the other example
from examples.simple_agent import SimpleAgent


async def main() -> None:
    config = AgentConfig(
        name="researcher",
        model="gpt-4o",
        system_prompt="You are a research analyst. Provide structured, factual analysis.",
    )

    agent = SimpleAgent(config)
    chain = ResearchChain(agent)

    result = await chain.run({
        "topic": "Recent advances in agentic AI systems",
        "depth": 3,
    })

    print("=== Research Chain Result ===")
    print(result.output)
    print(f"\nSteps completed: {len(result.steps)}")
    for step in result.steps:
        print(f"  - {step['step']}")


if __name__ == "__main__":
    asyncio.run(main())
