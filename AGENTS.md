# AGENTS.md — Agentic AI Starter Pack (Claude Native)

## Project Overview

Claude-native prototyping scaffold for agentic AI systems. Uses Anthropic's Messages API with native tool use — no ReAct prompting or OpenAI-style function calling.

## Repository Structure

```
├── src/
│   ├── agents/          # Claude-powered agents (ToolUseAgent)
│   ├── tools/           # Tool implementations with Anthropic input_schema
│   ├── prompts/         # Jinja2 system prompt templates
│   ├── chains/          # Multi-step agent chains and workflows
│   └── evaluation/      # Evaluation and testing utilities
├── configs/             # Agent and model configuration files
├── examples/            # Runnable example scripts
├── tests/               # Unit and integration tests (mocked API)
└── docs/                # Architecture and design docs
```

## Conventions

### Python
- Python 3.11+
- Use type hints on all function signatures
- Docstrings: Google style
- Formatting: `ruff format`
- Linting: `ruff check`

### Claude API Patterns
- Use `anthropic.AsyncAnthropic` client — inject via constructor
- System prompt is a **top-level API parameter**, not a message role
- Tool definitions use `input_schema` (JSON Schema), not `parameters`
- The agentic loop checks `stop_reason`: `tool_use` → execute tools → loop; `end_turn` → return
- Tool results are `tool_result` content blocks in a `user` message
- Extended thinking is available via `thinking` parameter for complex reasoning

### Prompts
- Store system prompt templates in `src/prompts/` as `.j2` files
- Use Jinja2 templating for dynamic context injection
- Each prompt file should have a corresponding `_meta.yaml`
- Tool descriptions are handled by the API — don't inject them into prompts

### Tools
- Each tool is a single Python module in `src/tools/`
- Tools must implement `BaseTool` from `src/tools/base.py`
- Implement `input_schema()` returning JSON Schema for Anthropic's format
- Use `to_anthropic_schema()` to get the full tool definition for the API

### Agents
- Agent configs live in `configs/agents/` as YAML files
- `ToolUseAgent` is the primary agent — uses Claude's native tool use loop
- Inject `AsyncAnthropic` client for testability
- Agent implementations should be stateless

### Chains
- Chains compose agents into multi-step workflows
- Each step creates its own `ToolUseAgent` with appropriate config
- Define chains in `src/chains/` with clear input/output contracts

### Configuration
- Model parameters go in `configs/models/` (includes `thinking.yaml` for extended thinking)
- Never hardcode API keys — use environment variables via `.env`
- Default model: `claude-sonnet-4-20250514`

### Testing
- Tests mirror the `src/` structure under `tests/`
- Mock `AsyncAnthropic` client — tests run without API keys
- Use `pytest` with `asyncio_mode = "auto"`
- Evaluation scripts in `src/evaluation/` for measuring agent quality

### Git
- Commit messages: imperative mood, concise (`Add retrieval tool`, not `Added retrieval tool`)
- One logical change per commit
- Co-author: `Co-authored-by: Ona <no-reply@ona.com>`
