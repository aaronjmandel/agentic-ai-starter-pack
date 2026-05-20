"""Example: Multi-turn conversation with tool use.

Usage:
    python examples/multi_turn_chat.py

Requires ANTHROPIC_API_KEY in .env or environment.

Shows how to maintain conversation history across multiple turns
while giving Claude access to tools. Each turn builds on the
previous context.
"""

import asyncio

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool

load_dotenv()


async def main() -> None:
    client = AsyncAnthropic()
    tools = [CalculatorTool(), WebSearchTool()]
    tool_map = {t.name: t for t in tools}
    tool_schemas = [t.to_anthropic_schema() for t in tools]

    messages: list[dict] = []
    system = "You are a helpful assistant with access to a calculator and web search."

    queries = [
        "What is 2**10?",
        "Now multiply that result by 3.",
        "Search the web for 'Claude AI tool use' and summarize what you find.",
    ]

    for query in queries:
        print(f"\n{'='*50}")
        print(f"User: {query}")

        messages.append({"role": "user", "content": query})

        # Agentic loop for this turn
        while True:
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system,
                tools=tool_schemas,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                # Extract and display text
                messages.append({"role": "assistant", "content": response.content})
                for block in response.content:
                    if block.type == "text":
                        print(f"Claude: {block.text}")
                break

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    print(f"  [Tool: {block.name}({block.input})]")
                    result = await tool_map[block.name].execute(**block.input)
                    print(f"  [Result: {result}]")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

                messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    asyncio.run(main())
