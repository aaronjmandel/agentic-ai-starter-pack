"""Web search tool stub.

Replace the execute() method with a real search API integration
(e.g., Tavily, SerpAPI, Brave Search).
"""

from typing import Any

from src.tools.base import BaseTool


class WebSearchTool(BaseTool):
    """Search the web for information. Returns a summary of top results."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for a query. Returns summaries of top results. Input: 'query' string."

    async def execute(self, **kwargs: Any) -> str:
        query = kwargs.get("query", "")
        if not query:
            return "Error: No query provided."

        # Stub — replace with actual search API call
        return (
            f"[Search stub] Results for '{query}':\n"
            "1. Example result — replace this with a real search API integration.\n"
            "   See docs/integrations.md for setup instructions."
        )

    def _parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                }
            },
            "required": ["query"],
        }
