"""Research chain — search, synthesize, summarize.

A three-step chain that:
1. Searches for information on a topic (via tool-use agent)
2. Synthesizes findings into a structured analysis
3. Produces a final summary

Each step uses Claude's native tool use — no prompt-based
tool selection needed.
"""

import logging
from typing import Any

from anthropic import AsyncAnthropic

from src.agents.base import AgentConfig
from src.agents.tool_use_agent import ToolUseAgent
from src.chains.base import BaseChain, ChainResult
from src.prompts.loader import load_prompt
from src.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class ResearchChain(BaseChain):
    """Three-step research pipeline: search → synthesize → summarize."""

    def __init__(self, client: AsyncAnthropic | None = None) -> None:
        self.client = client or AsyncAnthropic()

    async def run(self, input_data: dict[str, Any]) -> ChainResult:
        """Run the research chain.

        Args:
            input_data: Must contain 'topic' (str). Optional: 'depth' (int, default 3).

        Returns:
            ChainResult with the research summary.
        """
        topic = input_data["topic"]
        depth = input_data.get("depth", 3)
        steps: list[dict[str, Any]] = []

        # Step 1: Search via tool-use agent
        logger.info("Step 1: Searching for '%s'", topic)
        search_agent = ToolUseAgent(
            config=AgentConfig(
                name="searcher",
                system_prompt=f"Search for information about: {topic}. "
                "Use the web_search tool to find relevant results.",
                max_iterations=3,
            ),
            tools=[WebSearchTool()],
            client=self.client,
        )
        search_result = await search_agent.run(f"Find information about: {topic}")
        steps.append({"step": "search", "input": topic, "output": search_result.output})

        # Step 2: Synthesize (direct Claude call, no tools needed)
        logger.info("Step 2: Synthesizing findings")
        system_prompt = load_prompt("system_researcher", depth=depth)
        synthesis_agent = ToolUseAgent(
            config=AgentConfig(
                name="synthesizer",
                system_prompt=system_prompt,
            ),
            client=self.client,
        )
        synthesis = await synthesis_agent.run(
            f"Based on these findings about '{topic}', provide a structured analysis:\n\n"
            f"{search_result.output}"
        )
        steps.append({"step": "synthesize", "output": synthesis.output})

        # Step 3: Summarize
        logger.info("Step 3: Summarizing")
        summary_prompt = load_prompt(
            "summarize", text=synthesis.output, style="concise", max_points=depth
        )
        summary_agent = ToolUseAgent(
            config=AgentConfig(name="summarizer"),
            client=self.client,
        )
        summary = await summary_agent.run(summary_prompt)
        steps.append({"step": "summarize", "output": summary.output})

        return ChainResult(
            output=summary.output,
            steps=steps,
            metadata={"topic": topic, "depth": depth},
        )
