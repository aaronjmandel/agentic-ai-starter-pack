# Golden Principles

Rules that agents MUST follow. Violations should be caught in review or by path-scoped rules. These are non-negotiable — if a principle needs to change, update this document first and get human approval.

---

## Architecture

### 1. Tiered layer discipline
Client → Manager → Engine → Data Access → Resource.
- **No upward calls:** Data Access never calls Engines or Managers. Engines never call Managers.
- **No layer skipping:** Clients call Managers, not Engines or Data Access directly.
- **Managers orchestrate:** they coordinate calls to Engines, Data Access, and Utilities. No business logic in Managers.
- **Managers are stateless mediators** — orchestration only.
- **Contracts are leaves:** `contracts/` imports nothing from the project. All interfaces, types, and DTOs live here.
- **Utility is cross-cutting:** audit, sync, notifications. Not business logic, not framework plumbing.
- **Infrastructure is framework plumbing:** DI container, composition roots, provisional mocks. Not domain logic.

### 2. Engine purity
Engines are pure functions: `(data, rules) → results`. They never perform I/O, maintain state, or call Data Access. All inputs are passed as parameters by the orchestrating Manager.

> **Why:** Pure engines are trivially testable (no mocks needed), deployment-neutral (same logic runs anywhere), and naturally parallelizable. If your engine needs data, the Manager resolves it and passes it in.

### 3. Single composition root
All dependency wiring happens in one place (`infrastructure/`). Components never construct their own dependencies. Managers resolve dependencies via DI, not by importing concrete implementations.

### 4. Manager-to-Manager is async only
Managers never call each other synchronously. Cross-manager coordination uses events, message queues, or async patterns. This prevents hidden coupling and cascading failures.

### 5. Two data paths
- **Command path** (mutations): Client → Manager → Engine → DA → Resource
- **Query path** (read-only): Reporting/analytics tools may query the data store directly

Reporting and analytics may bypass the command path when they only need read access.

[REPLACE — if your system has a single data path or additional paths (e.g., event sourcing, CQRS), document them here.]

---

## Data Handling

### 6. Validate at boundaries
Parse and validate data at ingestion points: API inputs, file uploads, user form submissions, external system responses. Internal code trusts typed interfaces — no redundant validation in inner layers.

### 7. Typed over stringly
Prefer typed objects, interfaces, and enums over raw strings or unstructured dictionaries.
- Domain statuses are enums or union types, not strings.
- Configuration values use typed structures, not raw JSON/dict access.
- Entity references use typed IDs, not bare strings.

[REPLACE — add project-specific typing rules. For example: "Object Types use the canonical names: `Order`, `Customer`, `Product`." or "Rule conditions use typed column operations, not raw SQL strings."]

### 8. Domain invariants are explicit
[REPLACE — document your domain-specific invariants that must be enforced everywhere. Examples:]

- Valid entity statuses: list them exhaustively. If a workflow needs a new status, update this document first.
- Valid state transitions: document the state machine. Only these transitions are allowed.
- Required fields: list fields that must never be null in production data.
- Business rules: reference the canonical rule catalog if one exists.

> **Template:**
> The only valid [ENTITY] statuses are:
> `Status1` · `Status2` · `Status3` · ...
> No others. If a workflow needs a new status, update this document and the architecture docs first.

---

## Code Quality

### 9. Test-first development (TDD)
Tests define the contract before implementation begins. The tester agent writes failing tests from the exec-plan's acceptance criteria, then the implementer writes code to make those tests pass. Every new business logic function gets a test.

**Exceptions:** UI layout/styling and spike/prototype code (must be explicitly marked as `[SPIKE]` in the exec-plan). These still need tests added before merging to main.

### 10. Data-driven tests
Use fixture files (JSON, YAML, CSV) for test data, not inline hardcoded values. Keep golden outputs for regression comparison. Test data lives in a dedicated directory (e.g., `tests/fixtures/`, `tests/test_data/`), not scattered across test files.

### 11. No dead code
Remove unused imports, functions, and files. Don't comment-out code "for later." Don't leave backward-compatibility shims for removed features.

### 12. Shared utilities over hand-rolled helpers
Reuse existing shared packages, modules, and utilities before writing new helpers. Centralizing invariants (validation, formatting, status mappings) in one place prevents drift across agents and sessions. If a helper is needed by two or more modules, promote it to the shared location. Don't duplicate logic that already exists in a typed SDK or shared package.

### 13. Minimal change
Implement the minimum needed for the current task. No speculative features, no preemptive abstractions. Three similar lines is better than a premature helper function. Don't add features, refactor code, or make "improvements" beyond what was asked.

---

## Documentation

### 14. Design before code
Architecture decisions go into `Design/` docs before implementation begins. If the change touches component boundaries, interfaces, or data contracts, write or update the design doc first.

### 15. Decisions in repo
If a decision was made in Slack, a meeting, or a review session, capture it in the relevant design doc or execution plan. **If it's not in the repo, it doesn't exist for agents.**

### 16. Index stays current
`Design/index.md` must reflect the actual files in `Design/`. When adding, renaming, or archiving a design doc, update the index in the same commit.

---

## Frontend

[REPLACE — remove this section if your project has no frontend, or adapt to your UI framework.]

### 17. Feature module isolation
Each feature owns its own components, hooks, stores, and types under its feature directory. Features never import from other features — shared code lives in a dedicated shared directory.

### 18. Server state vs client state
Use a server-state library (e.g., TanStack Query, SWR, Apollo) for API/server state. Use a client-state library (e.g., Zustand, Jotai, Redux) only for client-side UI state (selections, theme, filters). Never duplicate server state in client stores.

### 19. Shared components first
Use existing shared components before creating new ones. If a component is used by two or more features, promote it to the shared directory.

---

## Cross-Language Contracts

[REPLACE — remove this section if your project uses a single language. If you have multi-language components, adapt the rules below.]

### 20. Multi-language components conform to shared contracts
When a component has implementations in multiple languages (e.g., Python + TypeScript, Java + Go), all shared DTOs, enums, and result types must conform to a shared contract definition (e.g., JSON Schema, Protocol Buffers, OpenAPI spec).

**Rules:**
- When adding a field or enum value, update the shared contract **first**, then update all language implementations.
- All implementations must include contract tests that validate serialized output against the contract and verify enum completeness.
- Never rename a field in one language without updating the contract and all other languages.

[REPLACE — list your shared contract files and which components are multi-language.]
