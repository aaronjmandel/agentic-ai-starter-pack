# Agentic AI Starter Pack — Claude Native

A prototyping scaffold for building agentic AI systems with Claude. Uses Anthropic's Messages API with native tool use — no ReAct prompting or function-calling wrappers needed.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Run the example agent
python examples/simple_agent.py

# Run with extended thinking
python examples/thinking_agent.py

# Multi-turn conversation with tools
python examples/multi_turn_chat.py

# Evaluation demo (no API key needed)
python examples/evaluation_demo.py
```

## Project Structure

```
src/
├── agents/        Claude-powered agents with native tool use
├── tools/         Tool implementations with Anthropic input_schema
├── prompts/       Jinja2 system prompt templates
├── chains/        Multi-step workflows composing agents + tools
└── evaluation/    Quality measurement and testing utilities

configs/
├── agents/        Agent configuration (model, tools, system prompt)
└── models/        Model presets (default, precise, creative, thinking)

examples/          Runnable scripts demonstrating each pattern
tests/             Unit and integration tests (with mocked API)
docs/              Architecture notes and design decisions
```

## Key Concepts

### Claude's Agentic Loop
The core pattern (see `src/agents/tool_use_agent.py`):
1. Send messages + tool definitions to Claude
2. Claude responds with text and/or `tool_use` content blocks
3. Execute requested tools, return `tool_result` content blocks
4. Repeat until Claude responds with `end_turn`

No prompt engineering for tool selection — Claude handles it natively.

### Tools
Tools implement `BaseTool` with an `input_schema()` method returning JSON Schema. The schema is passed directly to Claude's `tools` parameter. See `src/tools/base.py`.

### System Prompts
Claude takes the system prompt as a top-level API parameter (not a message role). Jinja2 templates in `src/prompts/` compose system prompts with dynamic context.

### Extended Thinking
Claude can reason internally before responding. Enable via `AgentConfig.thinking`:
```python
config = AgentConfig(
    name="thinker",
    thinking={"type": "enabled", "budget_tokens": 10000},
)
```

### Chains
Chains wire multiple agents into a pipeline. Each step uses Claude's native tool use independently.

### Evaluation
`src/evaluation/` scores agent outputs against expected results. No API key needed.

## Configuration

Model presets in `configs/models/`:
- `default.yaml` — balanced (claude-sonnet-4, temp 0.7)
- `precise.yaml` — deterministic (temp 0)
- `creative.yaml` — exploratory (temp 1.0)
- `thinking.yaml` — extended thinking enabled

API key goes in `.env` — never commit secrets.

## Testing

```bash
pytest tests/ -v
```

Tests mock the Anthropic API — no API key needed to run them.

## License

MIT
