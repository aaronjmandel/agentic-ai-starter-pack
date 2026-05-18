---
name: system-design
description: Use this skill when planning new system architectures, validating system design ideas, decomposing systems into components, or applying The Method's principles to enterprise software design. Triggers include requests to design a system, review an architecture, decompose a monolith, identify components, apply SOLID principles at the architectural level, validate design decisions, or create layered architectures. Also use when the user asks about system structure, component boundaries, dependency management, composition patterns, or how many services/components they need. If the user mentions "The Method", "Righting Software", functional decomposition, or volatility-based design, use this skill. Make sure to use this skill whenever the user discusses breaking down a system, wants to validate whether their architecture is sound, mentions separating concerns at the system level, or asks about dependency injection and composition roots — even if they don't explicitly say "system design" or "architecture".
---

# System Design Skill

Design, validate, and reason about enterprise software system architectures using The Method from "Righting Software" by Juval Lowy.

## Core Philosophy

**For beginner architects, there are many options. For master architects, there are only a few good options — typically only one correct choice.**

The software industry is saturated with patterns and methodologies. Most design options are incorrect or suboptimal. This skill helps identify the correct approaches quickly.

## The Method Overview

**The Method = System Design + Project Design**

This skill focuses on **System Design**: breaking down a large system into small, modular components with clear roles, semantics, and interactions.

### Time Guidelines
- **System Design**: 3-5 days (not weeks or months)
- **Validation**: Within 1 week of project start
- Quick decisions prevent analysis-paralysis and gold-plating

---

## Design Process

Follow this sequence. Each step has a dedicated reference file with full detail, examples, and anti-patterns.

### Step 1: Functional Decomposition

Decompose by **what the system does** (business capabilities), NOT by how it does it (technical layers). Apply the 3-9 Rule: always aim for 3-9 components at each level. Below 3 means not enough decomposition; above 9 means too much or needs sub-decomposition.

Read `DECOMPOSITION.md` for the full decomposition process, the 3-9 Rule rationale (rooted in Miller's Law), hierarchical decomposition, cohesion/coupling analysis, and anti-patterns (God Component, Ravioli Architecture, data-driven decomposition).

### Step 2: Apply SOLID at Component Level

| Principle | Test |
|-----------|------|
| **SRP** | If you need "and" or "or" to describe it, split it |
| **OCP** | Can new features be added without changing existing code? |
| **LSP** | Can you swap implementations without breaking the system? |
| **ISP** | Do clients depend only on operations they actually use? |
| **DIP** | Does Business Layer define interfaces that Resource Access implements? |

For how SOLID maps to layers, see `STRUCTURE.md`.

### Step 3: Define Layered Structure

The four-layer architecture:

```
Client Layer          (Presentation/UI)
Business Layer        (Domain Logic)
Resource Access Layer (Infrastructure)
Resources             (External Systems)
```

**Critical rule**: Dependencies flow DOWNWARD only. Never skip layers. Never have upward or circular dependencies. Business Layer defines interfaces; Resource Access implements them.

Read `STRUCTURE.md` for layer-specific rules (what belongs in each layer and what doesn't), dependency inversion through interfaces, testing strategies per layer, and anti-patterns (Smart UI, Anemic Domain, Business Logic in Database, Layer Skipping).

### Step 4: Apply Composition

Constructor injection for 95% of dependencies. Single composition root at application entry. Components never call IoC containers or use Service Locator.

Read `COMPOSITION.md` for DI patterns (constructor, property, method injection), lifetime management (transient, singleton, scoped), composition root design, and anti-patterns (Service Locator, ambient context, static dependencies).

### Step 5: Validate the Design

Trace 3-5 business scenarios through the components. Perform change impact analysis — consider typical changes (new payment method, new product type) and verify they stay localized to 1-2 components.

Read `CHECKLIST.md` for the full validation checklist and red flag summary.

---

## Red Flags

Stop and reconsider if:
- Component name uses "and" or "or" (violates SRP)
- Component has >15 public operations
- Cannot explain component in one sentence
- Decomposition based on technical layers at top level
- Components create dependencies with `new` keyword
- More than 4-5 constructor parameters (SRP violation)
- Circular dependencies between components
- Multiple composition roots

---

## Reference Files

| File | When to read |
|------|-------------|
| `DECOMPOSITION.md` | Starting decomposition, unsure about component boundaries, need anti-pattern guidance |
| `STRUCTURE.md` | Defining layers, resolving dependency direction questions, layer-specific rules |
| `COMPOSITION.md` | Setting up DI, choosing lifetimes, designing composition root |
| `EXAMPLE.md` | Want a complete worked example (online banking system end-to-end) |
| `CHECKLIST.md` | Validating a completed design, final review before implementation |

---

## Related Skills

After system design is complete (components identified, layers defined, composition planned), proceed to detailed design:

- **detailed-design-v2**: Use for IDesign Method-specific contract factoring, data contract factoring, manager-as-mediator patterns, BFF design, and workflow managers. Start here when designing the contract topology for a system designed with The Method.
- **detailed-design**: Use for universal interface quality — parameter design, result objects, error handling patterns, CQS, evolution/versioning strategies. Apply as a refinement pass on individual interfaces after contract factoring.

When both detailed design skills are relevant, apply v2 first (structural decisions), then v1 (quality refinement per interface).
