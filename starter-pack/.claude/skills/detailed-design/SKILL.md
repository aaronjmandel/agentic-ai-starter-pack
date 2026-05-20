---
name: detailed-design
description: Use this skill when designing service contracts, interfaces, method signatures, DTOs, or API shapes after system architecture is defined. Triggers include requests to design an interface, define a contract, create method signatures, design DTOs/request/response objects, review API design, apply Interface Segregation, design for evolvability, or handle error responses in contracts. Also use when the user mentions "contract-first design", "client-centric interfaces", "result objects", "parameter objects", or asks how to structure method parameters and return types. Make sure to use this skill whenever the user is working on the shape of an API or interface — even if they frame it as "what should this method look like", "how should I return errors", or "should I use exceptions or result types" rather than explicitly saying "detailed design". This skill bridges system design (architecture) and implementation (coding).
---

# Detailed Design Skill

Design service contracts, interfaces, method signatures, and DTOs — the bridge between system architecture and implementation.

## Core Philosophy

**Contract-First**: Design the interface BEFORE implementing the service. This forces thinking about client needs, reveals design issues early, and creates stable boundaries.

**Client-Centric**: Design from the client's perspective, not the service's implementation. Ask: "What does the client want to accomplish?"

---

## Quick Reference: Contract Design Rules

| Rule | Bad | Good |
|------|-----|------|
| ≤ 3-4 parameters | `PlaceOrder(int, string, string, int, decimal, ...)` | `PlaceOrder(OrderRequest request)` |
| Domain types, not primitives | `ProcessPayment(int orderId, decimal amount, string currency)` | `ProcessPayment(OrderId orderId, Money amount)` |
| Return domain objects | `DataTable GetOrders(int customerId)` | `IEnumerable<Order> GetOrders(int customerId)` |
| Result objects for failures | `bool ProcessPayment(...)` | `PaymentResult ProcessPayment(...)` |
| Intention-revealing names | `void Execute(OrderData data)` | `OrderResult PlaceOrder(OrderRequest request)` |
| ≤ 10 methods per interface | One big interface | Split by role: Commands / Queries / Reporting / Admin |
| Commands vs Queries (CQS) | Method changes state AND returns data | Commands return void/result; Queries have no side effects |

---

## Design Process

Follow this sequence. Each step has a dedicated reference file with full patterns, examples, and anti-patterns.

### Step 1: Design from Client's Perspective

Start every interface design by asking:
1. What does the client want to accomplish?
2. What information does the client have?
3. What information does the client need back?
4. What is the most natural way for them to use this?

Design interfaces that mirror business tasks, not database tables or internal implementation.

### Step 2: Design Method Signatures

Keep parameters low (≤ 3-4), use parameter objects for complex requests, use meaningful domain types over primitives, return result objects for operations that can fail.

Read `SIGNATURES.md` for parameter patterns (parameter objects, fluent builders, value objects, options pattern), return type patterns (result objects, pagination, async+cancellation), naming conventions (intention-revealing names, command/query verb patterns), and anti-patterns (boolean parameters, out/ref parameters).

### Step 3: Get Operation Granularity Right

One operation per business task from the client's perspective. The client should accomplish a business task with one or two calls, not ten. Avoid both chatty interfaces (too fine-grained, requiring many calls) and god methods (too coarse, doing everything in one call).

### Step 4: Apply Interface Segregation

Split large interfaces into smaller, role-specific interfaces. Common splits: Commands vs Queries vs Reporting vs Admin. Clients should depend only on methods they use.

### Step 5: Design DTOs

Simple data holders (no business logic), serializable, flat structure (avoid deep nesting), separate from domain model. Use distinct DTO categories: request, response, result, search/filter, summary.

Read `DTOS.md` for the 5 DTO categories, naming convention table, design patterns (immutable DTOs, builders, projections), mapping strategies (manual, extension methods), and anti-patterns (anemic domain disguised as DTOs, one-DTO-for-everything).

### Step 6: Design Error Handling

Use result objects for expected business failures (payment declined, invalid input). Reserve exceptions for truly exceptional conditions (database down, programming errors). Include typed error codes so clients can handle specific failure cases.

Read `ERRORS.md` for result object patterns (generic, domain-specific, validation), error code design (enums, naming conventions), client-side handling patterns (switch, fluent matching), exception guidelines, HTTP/REST mapping, and anti-patterns.

### Step 7: Design for Evolution

Add, don't modify or remove. Use optional parameters for new features. Design DTOs for extension — adding properties is safe; removing or changing types is breaking.

Read `EVOLUTION.md` for the breaking vs non-breaking change matrix, DTO evolution patterns, enum evolution (safe vs unsafe), API versioning strategies (URL path, query param, header), semantic versioning rules, and migration strategies (parallel operation, strangler fig).

---

## Red Flags

Stop and reconsider if:
- Method has > 4 parameters
- Method name is generic (Process, Execute, Handle, Get, Set)
- Method both changes state AND returns data (violates CQS)
- Interface has > 10 methods
- Returning DataTable, DataSet, XmlDocument, SqlDataReader
- DTOs have business logic
- Exposing domain model directly in contract
- Using exceptions for expected business failures
- Not documenting pre/post-conditions

---

## Reference Files

| File | When to read |
|------|-------------|
| `SIGNATURES.md` | Designing method parameters, return types, naming conventions |
| `DTOS.md` | Designing data transfer objects, naming patterns, mapping strategies |
| `ERRORS.md` | Choosing error handling strategy, designing result objects, HTTP mapping |
| `EVOLUTION.md` | Planning for backward compatibility, versioning APIs, migration |
| `EXAMPLES.md` | Complete service contract examples (payment, inventory, customer, orders) |

---

## Related Skills

**Order of Activities**:
1. **system-design** → Decomposition, Structure, Composition
2. **detailed-design-v2** → Contract factoring, data contract factoring, interaction patterns (if using The IDesign Method)
3. **detailed-design** → Individual interface quality: signatures, DTOs, error handling, evolution (this skill)
4. **Implementation** → Coding to contracts

- **system-design**: Prerequisite. Provides the components, layers, and composition plan that this skill designs contracts for.
- **detailed-design-v2**: Complementary. If building a service-oriented system with The IDesign Method, use v2 first for contract topology (facets, namespace-separated DTOs, manager patterns, BFF), then this skill for per-interface refinement. This skill covers error handling depth, evolution strategies, and universal rules (parameter counts, CQS, result objects) that v2 assumes but does not repeat.
