---
name: detailed-design-v2
description: Use this skill for detailed design of service-oriented systems following The IDesign Method. Triggers include requests to factor service contracts, design interfaces between managers/engines/access components, create polymorphic DTOs, design data contracts per volatility area, apply context-driven resolution, design BFF controllers, create workflow managers, or design call chains for use cases. Also use when the user mentions "contract factoring", "data contract factoring", "facets", "multifaceted service", "manager as mediator", "compositional design", "volatility-based DTOs", "polymorphic criteria", "use case factory", "BFF pattern", "out-of-band context", "proxy pattern", or asks how to structure contracts in a layered service-oriented architecture. Make sure to use this skill whenever the user is designing how services interact in a layered architecture — even if they phrase it as "how should my manager call the engine", "should each client get its own API", or "how do I pass context between services" rather than using formal IDesign terminology. This skill extends system design into the exact shape of contracts, DTOs, and interaction patterns between architectural components.
---

# Detailed Design v2 Skill

Detailed design of service contracts, data contracts, and interaction patterns for service-oriented systems following The IDesign Method. This skill bridges system design (architecture) and implementation.

## When to Use This Skill

Use this skill when:
- Factoring service contracts (interfaces) for managers, engines, or access components
- Designing data contracts (DTOs) per volatility area with namespace separation
- Applying polymorphic DTO strategies with context-driven resolution
- Designing manager services as mediators with call chains
- Creating BFF (Backend for Frontend) controller patterns
- Designing workflow managers and step-based orchestration
- Applying the proxy pattern for service boundaries
- Working with out-of-band context (headers, claims, origination)
- Designing common engines (Validation, Transformation, Filtering, Formatting)
- Reviewing contracts against IDesign Method principles

**Prerequisites**: System design should be complete — components identified (managers, engines, access, resources), layers defined, composition planned. This skill focuses on the **exact shape of interfaces, DTOs, and interaction patterns**.

---

## Core Philosophy

### The IDesign Method Perspective on Detailed Design

Detailed design focuses on the **arrows between the blocks** on the architecture diagram. After system design gives you the components, detailed design answers:
- What are the **service contracts** (interfaces/facets) each component exposes?
- What are the **data contracts** (DTOs) flowing between components?
- How does **context** (origination, security, workflow state) flow through the system?
- How are **use cases** mapped to operations on service contracts?

### Guiding Principles

1. **Use-Case Driven**: Every operation exists only in the context of a use case. Call chains are abstractions for groups of related use cases.
2. **Domain Informed, Context Relative**: Design is informed by the domain but shaped by the specific context (Online vs Restaurant, Patient vs Doctor).
3. **Volatility-Based Separation**: Factor contracts and DTOs along volatility boundaries. Things that change together stay together; things that change independently are separated.
4. **Program Against Abstractions**: Always code against interfaces, never concretions. Consumers program against service contracts.
5. **Compositional Over Hierarchical**: Prefer compositional relationships between facets. Hierarchical relationships are reserved for genuine logical hierarchies (e.g., IoT device trees).

---

## Quick Reference: Key Concepts

| Concept | Definition |
|---------|-----------|
| **Facet** | An interface on a service. A service is multifaceted (implements multiple interfaces). |
| **Service Contract** | The interface defining behavioral operations a service exposes. |
| **Data Contract** | The DTO classes that carry data across service boundaries. |
| **Contract Factoring** | Splitting a large interface into cohesive facets by behavioral concern. |
| **Call Chain** | Abstract representation of a set of related use cases flowing through managers → engines → access. |
| **Context** | The originating system/client of the request. Impacts decision-making, especially at the Manager level. |
| **Origination Context** | Out-of-band metadata (headers) identifying request origin, security claims, workflow state. |
| **BFF** | Backend For Frontend — a boundary tailored to a specific client type (web, mobile, IVR). |

---

## Design Process

### Step 1: Capture Behavior (Before Data)
Start with behavior, then data. Identify the use cases each component must support. Create abstract call chains representing groups of related use cases.

### Step 2: Factor Service Contracts
Split interfaces by behavioral concern. Ensure cohesion — everything inside curly braces for an interface must relate to its name. See `CONTRACT-FACTORING.md`.

### Step 3: Factor Data Contracts
Create autonomous DTOs per facet. Use namespaces to separate by volatility area. Apply polymorphism for context-driven variability. See `DATA-CONTRACTS.md`.

### Step 4: Design Interaction Patterns
Define how managers mediate between engines and access. Design context flow, proxy resolution, and response handling. See `LAYERED-PATTERNS.md`.

### Step 5: Design Boundaries
Design BFF controllers, gateway authentication, and API surface. Choose controller implementation strategy. See `CONTEXT-AND-BFF.md`.

### Step 6: Map Use Cases to Call Chains
Map business use cases to operations, design workflow managers for flow-oriented use cases. See `WORKFLOW-AND-CALLCHAINS.md`.

---

## Reference Files

| File | When to read |
|------|-------------|
| `CONTRACT-FACTORING.md` | Splitting interfaces by behavioral concern, compositional vs hierarchical style, anti-patterns |
| `DATA-CONTRACTS.md` | Autonomous DTOs per facet, namespace separation, polymorphic DTOs, the 7 DTO rules |
| `LAYERED-PATTERNS.md` | Manager as mediator, UseCaseFactory, context-driven resolution, proxy pattern, engine patterns |
| `CONTEXT-AND-BFF.md` | BFF per client type, controller implementations, out-of-band context, gateway and security |
| `WORKFLOW-AND-CALLCHAINS.md` | Workflow managers, call chains, use case mapping, common engines, messaging patterns |
| `EXAMPLES.md` | Complete worked examples (food ordering, vet clinic, production pipeline) with code and tests |

---

## Red Flags

Stop and reconsider if:
- A single canonical DTO is used across all facets of a service
- An interface mixes operations from unrelated behavioral concepts (low cohesion)
- Business logic leaks into the controller/API layer
- Context (origin, security) is embedded in method signatures instead of headers
- Manager has private helper methods (extract to engines or helpers)
- Service has class-level state (services should be stateless)
- Dependencies are resolved in the constructor when runtime context is needed
- DTO hierarchies create coupling between independently volatile areas
- One endpoint serves all client types (missing BFF separation)
- Operations are named by implementation rather than use case

---

## Contract Design Checklist

- [ ] Service contracts factored by behavioral cohesion (not one interface per operation)
- [ ] Data contracts factored autonomously per facet with namespace separation
- [ ] Polymorphic DTOs used for context-driven variability (criteria, responses)
- [ ] Manager operations named by call chain / use case (chunky, not chatty)
- [ ] Manager has no private helper methods — logic delegated to engines
- [ ] Context flows out-of-band via headers, not in method signatures
- [ ] Services are stateless — no class-level variables
- [ ] Proxy pattern used at service boundaries (treat local as remote)
- [ ] Compositional style preferred between facets (not hierarchical)
- [ ] Each facet raised as endpoint for independent deployment
- [ ] Response wrappers with error codes used for third-party / cross-boundary calls
- [ ] Constructors validate required DTOs — no invalid objects
- [ ] Every layer has its own request/response DTOs for highly volatile use cases
- [ ] Each service is an independent unit of scale

---

## Related Skills

**Order of Activities**:
1. **system-design** → Decomposition, Structure, Composition
2. **detailed-design-v2** → Contract factoring, data contract factoring, interaction patterns (this skill)
3. **detailed-design** → Per-interface quality refinement: parameter design, result objects, error handling, CQS, evolution/versioning
4. **Implementation** → Coding to contracts, framework integration

- **system-design**: Prerequisite. This skill assumes components, layers, and composition are already defined.
- **detailed-design**: Complementary. After v2 establishes the contract topology, use detailed-design for individual interface refinement. It covers error handling patterns, evolution/versioning strategies, pagination, async conventions, and universal contract quality rules that this skill does not repeat.
