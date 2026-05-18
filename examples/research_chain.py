"""Example: Run the research chain.

Usage:
    python examples/research_chain.py

Requires ANTHROPIC_API_KEY in .env or environment.

Demonstrates a multi-step chain: search → synthesize → summarize.
Each step uses Claude's native tool use.
"""

import asyncio

from dotenv import load_dotenv

from src.chains.research_chain import ResearchChain

load_dotenv()


async def main() -> None:
    chain = ResearchChain()

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
