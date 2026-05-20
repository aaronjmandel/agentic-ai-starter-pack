---
description: Structural requirements for execution plans — enforces tiered architecture and IDesign layering
paths:
  - "Design/exec-plans/**/*.md"
---

# Tiered Architecture Requirements for Execution Plans

Every exec-plan that introduces components must demonstrate architectural compliance. These rules enforce disciplined layering so that agents produce structurally sound plans, not just feature checklists.

## Application Layers

All components must map to one of these architectural layers. [REPLACE layer names and responsibilities to match your architecture — the principles (direction, separation, purity) are universal.]

| Layer | Directory | Responsibility | Rules |
|-------|-----------|---------------|-------|
| **Manager** | `manager/` | Orchestration, workflow | Stateless mediators. No business logic. Delegates to engines. |
| **Engine** | `engine/` | Business logic | Pure functions: `(data, rules) → results`. No I/O. No DA calls. |
| **Data Access** | `data_access/` | Data retrieval/persistence | Database queries, API calls, file I/O. No business logic. |
| **Utility** | `utility/` | Cross-cutting services | Logging, audit, sync, notifications. Domain-adjacent, not business logic. |
| **Infrastructure** | `infrastructure/` | Framework plumbing | DI container, composition roots, provisional mocks. |
| **Contracts** | `contracts/` | Interfaces & shared types | Protocols, DTOs, error hierarchies. Zero intra-project imports. |

## Layer Dependency Direction (top → bottom only)

```
manager/        → contracts/, infrastructure/  (resolves deps via DI)
engine/         → contracts/  (receives data, returns results)
data_access/    → contracts/, utility/
utility/        → contracts/
infrastructure/ → contracts/  (except composition root, which wires all layers)
contracts/      → (leaf — zero intra-project imports, only stdlib/third-party)
```

**Forbidden:** `engine/` → `data_access/`, `data_access/` → `engine/`, `engine/` → `manager/`, any layer → `manager/` (except Client).

## IDesign Structural Checklist

Before marking an exec-plan as ready for the tester, verify all principles:

1. **DIP Compliance** — `contracts/` contains all interfaces (Protocols/interfaces) and shared types, separate from implementations
2. **No Upward Dependencies** — imports follow the layer dependency direction above
3. **Import Discipline** — include at least one acceptance criterion (AC) that enforces import rules via an automated test
4. **Component-Scoped Subdirectories** — each layer uses `{layer}/{component}/` pattern (e.g., `engine/pricing/`, not flat files at the layer root)
5. **Interface Separation** — interfaces live in `contracts/`, never co-located with implementations in the same file
6. **Shared Types at Boundary** — types used by multiple layers live in `contracts/`, not inside any single layer
7. **Error Consolidation** — all error hierarchies in `contracts/errors` (or per-component), not scattered across layers
8. **Pure Engine** — engine components have no I/O, no DA calls. Include this in the component table
9. **Single Composition Root** — dependencies wired in one place (e.g., DI container), not scattered across modules
10. **Component-Scoped Tests** — test directories mirror source components: `tests/{tier}/{component}/`

## Test Structure

Tests must mirror the source component structure:

```
tests/
├── unit/                    # Pure logic tests (no runtime deps)
│   ├── pricing/             # Tests for engine/pricing/
│   └── validation/          # Tests for engine/validation/
├── component/               # Isolated tests needing runtime deps
│   ├── data_store/          # Tests with mocked database
│   └── api_client/          # Tests with HTTP mocks
└── integration/             # Cross-component or real infrastructure
    └── order_manager/       # Full chain tests
```

### Test Tiers

| Tier | Directory | What it tests | Runtime deps |
|------|-----------|---------------|-------------|
| **Unit** | `tests/unit/` | Pure logic, types, contracts | None |
| **Component** | `tests/component/` | Single component with test doubles | Varies |
| **Integration** | `tests/integration/` | Cross-component flows or real infra | Multiple |

## Exec-Plan Template Requirements

Every exec-plan must include these sections:

- `## Goal` — one sentence describing the outcome
- `## Acceptance Criteria` — testable behaviors in `- [ ] **AC-N:**` format
- `## Completion Criteria` — what must be true to mark the plan Completed
- At least one fenced code block containing a directory tree with layer annotations
- A section documenting import/dependency direction rules for the components being added

## Do

- Map every component to exactly one layer
- Place interfaces in `contracts/`, separate from implementations
- Use component-scoped subdirectories: `{layer}/{component}/`
- Describe engine components as pure (no I/O) in the component table
- Wire dependencies in a single composition root
- Group test files by component: `tests/{tier}/{component}/`
- Include acceptance criteria that enforce import discipline
- Include a fenced code block file tree showing directory structure with layer annotations

## Don't

- Co-locate an interface and its implementation in the same file
- Place interface definitions inside an implementation layer
- Allow imports against the dependency direction (e.g., `engine/` → `data_access/`)
- Place types used by multiple layers inside a single layer's directory
- Scatter error classes across multiple layers
- Give engine components I/O responsibilities
- Put business logic in `data_access/` or `manager/`
- Wire dependencies in multiple places
- Skip the file tree — structural compliance cannot be verified without one
- Place test files for different components in the same flat directory
