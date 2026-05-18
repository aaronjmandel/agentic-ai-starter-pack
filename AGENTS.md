# AGENTS.md — Agentic AI Starter Pack

## Project Overview

This is a prototyping starter pack for building agentic AI systems. It provides scaffolding for prompt templates, tool definitions, agent chains, and evaluation harnesses.

## Repository Structure

```
├── src/
│   ├── agents/          # Agent definitions and orchestration
│   ├── tools/           # Tool implementations agents can invoke
│   ├── prompts/         # Prompt templates (Jinja2 format)
│   ├── chains/          # Multi-step agent chains and workflows
│   └── evaluation/      # Evaluation and testing utilities
├── configs/             # Agent and model configuration files
├── examples/            # Runnable example scripts
├── tests/               # Unit and integration tests
└── docs/                # Architecture and design docs
```

## Conventions

### Python
- Python 3.11+
- Use type hints on all function signatures
- Docstrings: Google style
- Formatting: `ruff format`
- Linting: `ruff check`

### Prompts
- Store prompt templates in `src/prompts/` as `.j2` files
- Use Jinja2 templating for variable substitution
- Each prompt file should have a corresponding `_meta.yaml` describing its purpose and required variables

### Tools
- Each tool is a single Python module in `src/tools/`
- Tools must implement the `BaseTool` interface from `src/tools/base.py`
- Tool docstrings are used as the tool description passed to the LLM — keep them precise

### Agents
- Agent configs live in `configs/agents/` as YAML files
- Agent implementations in `src/agents/` should be stateless where possible
- Use dependency injection for LLM clients and tool registries

### Chains
- Chains compose agents and tools into multi-step workflows
- Define chains in `src/chains/` with clear input/output contracts
- Each chain should be independently testable

### Configuration
- Model parameters (temperature, max_tokens, etc.) go in `configs/models/`
- Never hardcode API keys — use environment variables via `.env`
- Default config values should be sensible for prototyping (e.g., temperature=0.7)

### Testing
- Tests mirror the `src/` structure under `tests/`
- Use `pytest` with fixtures for LLM mocking
- Evaluation scripts in `src/evaluation/` for measuring agent quality

### Git
- Commit messages: imperative mood, concise (`Add retrieval tool`, not `Added retrieval tool`)
- One logical change per commit
- Co-author: `Co-authored-by: Ona <no-reply@ona.com>`
