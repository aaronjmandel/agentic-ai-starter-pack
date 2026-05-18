# System Design Validation Checklists

Comprehensive checklists for validating system designs at each stage.

---

## Quick Validation (5 Minutes)

Use this for rapid assessment:

- [ ] Do I have 3-9 top-level components?
- [ ] Can I name each component in 1-3 words?
- [ ] Can I explain each component's purpose in one sentence?
- [ ] Do dependencies flow downward only?
- [ ] Can I test Business Layer with mocks?

**If any "No"**: Stop and address before proceeding.

---

## Decomposition Checklist

### Component Count
- [ ] 3-9 top-level components
- [ ] Each complex component has 3-9 sub-components (if decomposed)
- [ ] No single "God" component doing everything
- [ ] No explosion of tiny components (ravioli)

### Component Definition
- [ ] Each component has a clear, single purpose
- [ ] Component names use business terms (not technical jargon)
- [ ] No component names use "and" or "or"
- [ ] No generic suffixes: Manager, Handler, Helper, Utils
- [ ] Can explain each component to non-technical stakeholder

### Single Responsibility
- [ ] Each component has one reason to change
- [ ] No component has > 15 public operations
- [ ] Changes to one business area affect only one component
- [ ] Each component owned by single team

### Cohesion
- [ ] All parts of each component work toward same goal
- [ ] Internal elements interact frequently
- [ ] Easy to understand what belongs in each component

### Coupling
- [ ] Components communicate through defined interfaces
- [ ] No shared data structures between components
- [ ] No circular dependencies
- [ ] Can test each component independently
- [ ] Can replace implementation without affecting clients

---

## Structure Checklist

### Layer Definition
- [ ] Four layers identified: Client, Business, Resource Access, Resources
- [ ] Each layer has clear, distinct responsibility
- [ ] All components assigned to exactly one layer
- [ ] Layer boundaries are clearly documented

### Client Layer
- [ ] Contains only presentation logic
- [ ] No business rules or calculations
- [ ] No direct database access
- [ ] Delegates to Business Layer for all logic
- [ ] Validates only format/required fields (not business rules)

### Business Layer
- [ ] Contains all business logic and rules
- [ ] No SQL, HTTP, file I/O (technology-agnostic)
- [ ] No UI formatting or rendering
- [ ] Defines interfaces for what it needs from lower layers
- [ ] Pure enough to test with mocks

### Resource Access Layer
- [ ] Contains only technical operations
- [ ] No business rules or decisions
- [ ] Implements interfaces defined by Business Layer
- [ ] Handles all external system communication

### Dependency Direction
- [ ] Dependencies flow downward only (Client → Business → Resource Access)
- [ ] No upward dependencies (Resource Access → Business)
- [ ] No layer skipping (Client → Resource Access)
- [ ] No circular dependencies between layers

### Dependency Inversion
- [ ] Business Layer defines interfaces
- [ ] Resource Access Layer implements interfaces
- [ ] Business Layer doesn't reference Resource Access assembly
- [ ] Only Composition Root references both layers

---

## Composition Checklist

### Dependency Injection
- [ ] All components use constructor injection for required dependencies
- [ ] Dependencies declared explicitly in constructor signature
- [ ] No `new` keyword for creating dependencies in components
- [ ] No static methods for dependencies
- [ ] Dependencies validated (null check) in constructor

### Composition Root
- [ ] Single composition root at application entry
- [ ] All wiring happens in composition root
- [ ] Components NEVER call IoC container
- [ ] No Service Locator pattern in components
- [ ] Can resolve all root components from container

### Lifetimes
- [ ] Transient for lightweight, stateless objects
- [ ] Singleton for expensive, thread-safe, stateless objects
- [ ] Scoped for per-request objects (database contexts)
- [ ] Lifetimes explicitly configured

### Interface Design
- [ ] Small, focused interfaces (Interface Segregation)
- [ ] Clients depend only on operations they use
- [ ] No "fat" interfaces with dozens of methods
- [ ] Clear contract for each interface

### Dependency Count
- [ ] No component has more than 4-5 constructor parameters
- [ ] If more dependencies needed, consider splitting component
- [ ] Dependencies make sense together (related purpose)

### Avoiding Anti-Patterns
- [ ] No `new` keyword for dependencies
- [ ] No static dependencies
- [ ] No Service Locator calls in components
- [ ] No ambient context / global state
- [ ] No circular dependencies

---

## Scenario Validation Checklist

### Scenario Selection
- [ ] Identified 3-5 common business scenarios
- [ ] Scenarios cover main user journeys
- [ ] Scenarios include edge cases
- [ ] Scenarios span multiple components

### Scenario Walkthrough
For each scenario:
- [ ] Traced complete flow through components
- [ ] Each step clearly belongs to one component
- [ ] No unnecessary back-and-forth between components
- [ ] Clear orchestration point
- [ ] All business logic in Business Layer
- [ ] Client Layer only handles presentation

### Good Scenario Flow Indicators
- [ ] Scenario touches 2-4 components (not 1, not 10)
- [ ] Clear entry point
- [ ] Linear or tree-like flow (not tangled web)
- [ ] Each component adds clear value
- [ ] No component is just pass-through

---

## Change Impact Validation Checklist

### Change Selection
- [ ] Identified 3-5 typical changes
- [ ] Changes represent common evolution patterns
- [ ] Mix of feature additions and modifications
- [ ] Include regulatory/compliance type changes

### Impact Analysis
For each change:
- [ ] Identified which components affected
- [ ] Changes localized to 1-2 components
- [ ] No ripple effects across many components
- [ ] Interface contracts remain stable
- [ ] Tests for unaffected components still pass

### Good Change Isolation Indicators
- [ ] New feature = new code (not modifying existing)
- [ ] Bug fix = isolated to one component
- [ ] Technology swap = only Resource Access changes
- [ ] UI redesign = only Client Layer changes
- [ ] New business rule = only Business Layer changes

---

## Testing Validation Checklist

### Testability
- [ ] Business Layer can be tested with mocked dependencies
- [ ] Can inject mocks via constructor
- [ ] No hidden dependencies (static, global)
- [ ] Clear inputs and outputs for each operation
- [ ] No side effects that prevent isolation

### Test Coverage Plan
- [ ] Unit tests planned for Business Layer
- [ ] Integration tests planned for Resource Access Layer
- [ ] UI/acceptance tests planned for Client Layer
- [ ] Test strategy matches layer responsibilities

### Test Independence
- [ ] Tests can run in any order
- [ ] Tests don't depend on external systems
- [ ] Tests don't depend on other tests
- [ ] Can run tests in parallel

---

## Documentation Checklist

### Component Documentation
- [ ] Each component has one-sentence purpose
- [ ] Responsibilities listed for each component
- [ ] Interfaces documented
- [ ] Dependencies documented

### Visual Documentation
- [ ] Component diagram created
- [ ] Layer diagram created
- [ ] Dependency arrows shown
- [ ] Kept simple (no UML complexity)

### Decision Documentation
- [ ] Key design decisions recorded
- [ ] Rationale documented for each decision
- [ ] Alternatives considered noted
- [ ] Trade-offs acknowledged

---

## Final Sign-Off Checklist

Before development starts:

### Completeness
- [ ] All business capabilities represented
- [ ] All external integrations identified
- [ ] All cross-cutting concerns addressed
- [ ] All layers defined and populated

### Quality
- [ ] Passed all checklist sections above
- [ ] Reviewed by peer architect
- [ ] Scenarios validated with stakeholders
- [ ] Change impact acceptable

### Timeline
- [ ] Design completed in 3-5 days
- [ ] Validation completed within first week
- [ ] Team briefed and understands design
- [ ] Ready for detailed design/implementation

### Confidence
- [ ] Would you stake your reputation on this design?
- [ ] Would you want to maintain this system?
- [ ] Would new team members understand it quickly?
- [ ] Will it survive likely business changes?

---

## Red Flag Summary

Stop and reconsider if ANY of these are true:

### Decomposition Red Flags
🚨 Fewer than 3 or more than 9 top-level components
🚨 Component name uses "and" or "or"
🚨 Component has > 15 public operations
🚨 Cannot explain component in one sentence
🚨 Decomposition based on technical layers

### Structure Red Flags
🚨 Business logic in Client Layer
🚨 Business logic in Resource Access Layer or database
🚨 SQL/HTTP in Business Layer
🚨 Upward or circular dependencies
🚨 Layer skipping

### Composition Red Flags
🚨 `new` keyword for dependencies
🚨 Service Locator pattern
🚨 More than 5 constructor parameters
🚨 Circular dependencies
🚨 Multiple composition roots

### Validation Red Flags
🚨 Scenarios touch > 5 components
🚨 Changes ripple across many components
🚨 Cannot test Business Layer with mocks
🚨 Design took more than 2 weeks
🚨 Cannot explain design in 5 minutes
