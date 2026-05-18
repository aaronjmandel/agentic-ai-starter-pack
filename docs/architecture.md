# Architecture

## Overview

Built on Claude's native Messages API with tool use — no prompt-based
tool selection or ReAct parsing needed.

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│   Chains     │────▶│ ToolUseAgent │────▶│   Tools   │
│ (workflows)  │     │  (agentic    │     │ (actions) │
│              │     │   loop)      │     │           │
└─────────────┘     └──────────────┘     └───────────┘
       │                  │                     │
       ▼                  ▼                     ▼
┌─────────────┐     ┌──────────┐         ┌───────────┐
│   Configs    │     │ System   │         │ Evaluation│
│   (YAML)     │     │ Prompts  │         │ (scoring) │
└─────────────┘     └──────────┘         └───────────┘
```

## Claude's Agentic Loop

The core pattern (implemented in `ToolUseAgent`):

```
User input
    │
    ▼
┌─────────────────────────────────┐
│  client.messages.create(        │
│    model=...,                   │
│    system=...,        ◄── top-level param, not a message
│    tools=[...],       ◄── Anthropic tool schemas
│    messages=[...],              │
│  )                              │
└─────────────┬───────────────────┘
              │
              ▼
     ┌─────────────────┐
     │  stop_reason?    │
     └────┬────────┬────┘
          │        │
    end_turn    tool_use
          │        │
          ▼        ▼
      Return   Execute tool(s)
      text     Append tool_result
               content blocks
               Loop back ↑
```

Key differences from OpenAI-style agents:
- **No ReAct prompting** — Claude decides tool use natively
- **System prompt is a top-level parameter**, not a message role
- **Tool results use content blocks** (`tool_result` type), not string injection
- **Extended thinking** available for complex reasoning (Claude-specific)
- **Tool schemas use `input_schema`**, not `parameters`

## Extension Points

- **New tools**: Implement `BaseTool` in `src/tools/` with `input_schema()`
- **New agents**: Subclass `BaseAgent` in `src/agents/`
- **New chains**: Subclass `BaseChain` in `src/chains/`
- **New prompts**: Add `.j2` + `_meta.yaml` in `src/prompts/templates/`
- **New metrics**: Add functions to `src/evaluation/scorer.py`
