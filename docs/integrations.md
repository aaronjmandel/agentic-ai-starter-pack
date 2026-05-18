# Integrations

## LLM Providers

### OpenAI
Set `OPENAI_API_KEY` in `.env`. See `examples/simple_agent.py`.

### Anthropic
Set `ANTHROPIC_API_KEY` in `.env`. Override `_call_llm()` using the `anthropic` package:

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()
message = await client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=self._history,
)
```

### Local Models (Ollama, vLLM)
Point the OpenAI client at a local endpoint:

```python
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="unused")
```

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
