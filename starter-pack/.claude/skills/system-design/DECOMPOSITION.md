# Decomposition Reference

Detailed guide for functional decomposition based on The Method.

## Core Principle

**Functional decomposition** = Breaking the system based on **what it does** (functions/capabilities), not how it does it (implementation details).

This creates stable architecture resistant to implementation changes.

---

## The Decomposition Problem

For any non-trivial system, there are **infinite ways to decompose** it. The challenge is finding the **one correct decomposition** that:

1. Addresses business requirements
2. Minimizes coupling between components
3. Maximizes cohesion within components
4. Remains stable over time

### Cost of Wrong Decomposition
- Exponential rework penalty: O(n²) when starting from wrong decomposition
- Changes cascade across component boundaries
- Technical debt accumulates rapidly
- System becomes unmaintainable

---

## The 3-9 Rule

### Why 3-9?
- Human cognitive limit: 7±2 items in working memory (Miller's Law)
- Below 3: Probably not enough decomposition
- Above 9: Probably too much decomposition

### Application
- Top-level system: 3-9 major components
- Each component: 3-9 sub-components (if needed)
- Recursive application creates hierarchy

### Indicators of Right Granularity
✅ Component has clear, single purpose
✅ Team can understand component's role quickly
✅ Component has 3-9 major operations/interfaces
✅ Testing strategy is straightforward

❌ Component has > 15 public operations
❌ Component name is vague or requires explanation
❌ Multiple teams claim ownership
❌ Frequent cross-component changes

---

## Hierarchical Decomposition

When a component becomes complex:
1. Treat component as a **subsystem**
2. Apply decomposition principles **recursively**
3. Create 3-9 sub-components
4. Maintain clear boundaries at each level

### Example Hierarchy
```
E-commerce System
├── Order Management (component)
│   ├── Order Creation (sub-component)
│   ├── Order Fulfillment (sub-component)
│   └── Order History (sub-component)
├── Inventory Management (component)
├── Payment Processing (component)
└── Customer Management (component)
```

---

## Cohesion and Coupling

### Cohesion (Internal)
**Definition**: Degree to which elements within a component belong together.

**High Cohesion Indicators**:
- All methods/classes work toward same business capability
- Changes to one part rarely require changes to other parts
- Easy to name component with single, clear name

**Low Cohesion Red Flags**:
- Component name requires "and" or "or"
- Internal elements rarely interact
- Difficult to explain purpose in one sentence

### Coupling (External)
**Definition**: Degree of dependency between components.

**Low Coupling Indicators**:
- Components communicate through well-defined interfaces
- Changes in one component rarely affect others
- Components can be tested independently
- Can replace implementation without affecting clients

**High Coupling Red Flags**:
- Components share data structures
- Changes cascade across boundaries
- Circular dependencies
- Components call each other's internal methods

**Goal**: Maximize cohesion, minimize coupling

---

## Decomposition Anti-Patterns

### 1. Layer-Based Decomposition
❌ **Bad Structure**:
```
├── Presentation Layer
├── Business Logic Layer
└── Data Access Layer
```

**Why It Fails**:
- Business changes cut across all layers
- Artificial boundaries
- Forces unnecessary dependencies

**Better Approach**: Decompose by business capabilities first, apply layering within each component.

### 2. God Component
**Problem**: Single component that does everything.

**Symptoms**:
- Hundreds of operations
- Multiple unrelated responsibilities
- Every change touches this component
- Impossible to test in isolation

**Solution**: Apply SRP aggressively.

### 3. Chatty Components
**Problem**: Components making many fine-grained calls to each other.

**Symptoms**:
- Performance issues from communication overhead
- Complex orchestration logic
- Difficult to understand system flow

**Solution**: Rethink boundaries, use coarser operations, consider merging.

### 4. Data-Driven Decomposition
❌ **Bad**:
```
├── CustomerComponent
├── OrderComponent
└── ProductComponent
```

**Why It Fails**:
- Business processes cut across entities
- Creates artificial dependencies
- Violates functional decomposition

**Better**: Decompose by business capabilities that use these entities.

### 5. Ravioli Architecture
**Problem**: Too many small components with complex interconnections.

**Symptoms**:
- Dozens of tiny components
- Components highly interdependent
- Overhead dominates useful work

**Solution**: Consolidate related functionality.

---

## Decomposition Process

### Step 1: Identify Business Capabilities
1. Work with domain experts
2. List major business functions (not technical functions)
3. Group related capabilities
4. Aim for 3-9 top-level capabilities

**Example Business Capabilities**:
- Order Management
- Inventory Management
- Customer Management
- Payment Processing
- Shipping Management

### Step 2: Define Component Boundaries
For each business capability:
1. Define clear **responsibility**: What does it do?
2. Define **interfaces**: How do clients interact?
3. Define **dependencies**: What does it need from others?
4. Verify **SRP**: Does it have one reason to change?

### Step 3: Validate Decomposition
- Can we name each component clearly?
- Are interfaces cohesive and focused?
- Can components be tested independently?
- Would typical business changes stay within component boundaries?
- Do we have 3-9 components?

### Step 4: Iterate and Refine
- Test against real scenarios
- Look for high coupling indicators
- Look for low cohesion indicators
- Adjust boundaries as needed
- Don't gold-plate: good enough is good enough

---

## Testing the Decomposition

### Scenario Walkthrough
Take common business scenarios and trace through components:
1. New customer order
2. Product return
3. Inventory replenishment
4. Customer support inquiry

**Good Decomposition**: Each scenario touches minimal components with clear flow.
**Bad Decomposition**: Scenarios ping-pong between many components.

### Change Impact Analysis
Consider typical changes:
- New payment method
- New shipping carrier
- New product type
- Regulatory requirement change

**Good Decomposition**: Changes localized to 1-2 components.
**Bad Decomposition**: Changes ripple across many components.

---

## Naming Conventions

- Use **business terms**, not technical jargon
- Be specific: "Order Processing" not "Manager"
- Avoid generic suffixes: -Manager, -Handler, -Service, -Helper
- Name should indicate responsibility
- If you need "and" or "or", split the component

---

## Decomposition Checklist

- [ ] Identified 3-9 major business capabilities
- [ ] Named each component clearly with business terms
- [ ] Verified each component has single responsibility
- [ ] Defined interfaces for each component
- [ ] Identified dependencies between components
- [ ] Checked for circular dependencies
- [ ] Validated coupling is minimal
- [ ] Validated cohesion is maximal
- [ ] Walked through 3-5 business scenarios
- [ ] Performed change impact analysis
- [ ] No component has > 15 operations
- [ ] No "God components"
- [ ] No layer-based decomposition at top level
- [ ] Can explain decomposition to team in < 5 minutes
