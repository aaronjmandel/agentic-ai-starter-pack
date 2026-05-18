"""Research chain — search, synthesize, summarize.

A three-step chain that:
1. Searches for information on a topic
2. Synthesizes findings into a structured analysis
3. Produces a final summary
"""

import logging
from typing import Any

from src.agents.base import AgentConfig, BaseAgent
from src.chains.base import BaseChain, ChainResult
from src.prompts.loader import load_prompt
from src.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class ResearchChain(BaseChain):
    """Three-step research pipeline: search → synthesize → summarize."""

    def __init__(self, agent: BaseAgent) -> None:
        self.agent = agent
        self.search_tool = WebSearchTool()

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

        # Step 1: Search
        logger.info("Step 1: Searching for '%s'", topic)
        search_results = await self.search_tool.execute(query=topic)
        steps.append({"step": "search", "input": topic, "output": search_results})

        # Step 2: Synthesize (via agent)
        logger.info("Step 2: Synthesizing findings")
        synthesis_prompt = (
            f"Based on these search results about '{topic}', provide a structured analysis:\n\n"
            f"{search_results}\n\n"
            f"Cover up to {depth} key aspects."
        )
        synthesis = await self.agent.run(synthesis_prompt)
        steps.append({"step": "synthesize", "input": synthesis_prompt, "output": synthesis.output})

        # Step 3: Summarize
        logger.info("Step 3: Summarizing")
        summary_prompt = load_prompt(
            "summarize",
            text=synthesis.output,
            style="concise",
            max_points=depth,
        )
        summary = await self.agent.run(summary_prompt)
        steps.append({"step": "summarize", "input": summary_prompt, "output": summary.output})

        return ChainResult(
            output=summary.output,
            steps=steps,
            metadata={"topic": topic, "depth": depth},
        )
