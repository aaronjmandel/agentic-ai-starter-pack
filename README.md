# Agentic AI Starter Pack

A prototyping scaffold for building agentic AI systems with LLMs. Provides ready-to-use patterns for agents, tools, prompt templates, multi-step chains, and evaluation.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run the example agent
python examples/simple_agent.py

# Run the example chain
python examples/research_chain.py
```

## Project Structure

```
src/
├── agents/        Agent definitions and orchestration
├── tools/         Tool implementations (search, calculator, etc.)
├── prompts/       Jinja2 prompt templates with metadata
├── chains/        Multi-step workflows composing agents + tools
└── evaluation/    Quality measurement and testing utilities

configs/
├── agents/        Agent configuration (which model, tools, system prompt)
└── models/        Model parameter presets (temperature, tokens, etc.)

examples/          Runnable scripts demonstrating each component
tests/             Unit and integration tests
docs/              Architecture notes and design decisions
```

## Key Concepts

### Agents
An agent wraps an LLM with a system prompt and a set of tools. See `src/agents/base.py` for the interface and `configs/agents/` for configuration.

### Tools
Tools are functions the agent can call. Each tool implements `BaseTool` and provides a name, description, and `execute()` method. The description is passed directly to the LLM, so clarity matters.

### Prompts
Prompt templates use Jinja2 syntax and live in `src/prompts/`. Each template has a companion `_meta.yaml` file listing required variables and usage notes.

### Chains
Chains wire multiple agents and tools into a pipeline. Define input/output contracts so each step is independently testable.

### Evaluation
Use `src/evaluation/` to measure agent output quality. Includes a basic scoring framework and example metrics.

## Configuration

All configuration uses YAML files in `configs/`. Model parameters, agent definitions, and tool registries are separated so you can mix and match.

Environment variables (API keys, endpoints) go in `.env` — never commit secrets.

## Testing

```bash
pytest tests/ -v
```

## License

MIT
