# Integrations

## Claude Models

Set `ANTHROPIC_API_KEY` in `.env`. The starter pack defaults to `claude-sonnet-4-20250514`.

Available model configs in `configs/models/`:
- `default.yaml` — balanced (temperature 0.7)
- `precise.yaml` — deterministic (temperature 0)
- `creative.yaml` — exploratory (temperature 1.0)
- `thinking.yaml` — extended thinking enabled (budget: 10k tokens)

## Extended Thinking

Claude can reason internally before responding. Enable via config:

```python
config = AgentConfig(
    name="thinker",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
)
```

The thinking output is captured in `AgentResponse.thinking` for debugging.

## Search APIs

Replace `WebSearchTool.execute()` with your preferred search provider:

- **Tavily**: `pip install tavily-python` — purpose-built for AI agents
- **SerpAPI**: `pip install google-search-results`
- **Brave Search**: Direct HTTP API via `httpx`

## Vector Stores (for RAG)

Not included in the starter pack, but easy to add:

1. Create a `VectorStoreTool` implementing `BaseTool`
2. Use `chromadb`, `qdrant-client`, or `pinecone-client`
3. Register it in your agent config
