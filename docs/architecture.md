# Architecture

## Overview

```
┌─────────────┐     ┌──────────┐     ┌───────────┐
│   Chains     │────▶│  Agents  │────▶│   Tools   │
│ (workflows)  │     │ (ReAct)  │     │ (actions) │
└─────────────┘     └──────────┘     └───────────┘
       │                  │                 │
       ▼                  ▼                 ▼
┌─────────────┐     ┌──────────┐     ┌───────────┐
│   Configs    │     │ Prompts  │     │ Evaluation│
│   (YAML)     │     │ (Jinja2) │     │ (scoring) │
└─────────────┘     └──────────┘     └───────────┘
```

## Data Flow

1. **User input** enters through a chain or directly to an agent
2. **Agent** loads its system prompt from a Jinja2 template, injecting tool descriptions
3. **LLM** receives the prompt and either produces a final answer or requests a tool call
4. **Tool** executes and returns an observation string
5. **Agent** feeds the observation back to the LLM (ReAct loop)
6. **Chain** passes output between steps until the pipeline completes
7. **Evaluation** scores the final output against expected results

## Extension Points

- **New tools**: Implement `BaseTool` in `src/tools/`
- **New agents**: Subclass `BaseAgent` in `src/agents/` (e.g., plan-and-execute, tree-of-thought)
- **New chains**: Subclass `BaseChain` in `src/chains/`
- **New prompts**: Add `.j2` + `_meta.yaml` in `src/prompts/templates/`
- **New metrics**: Add functions to `src/evaluation/scorer.py`

## LLM Integration

The starter pack is LLM-agnostic. The `BaseAgent._call_llm()` method is the integration point.
See `examples/simple_agent.py` for an OpenAI implementation. Swap in Anthropic, local models,
or any other provider by overriding this method.
