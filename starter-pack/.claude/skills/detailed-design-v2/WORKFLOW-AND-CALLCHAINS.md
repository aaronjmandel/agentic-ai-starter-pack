# Workflow Managers and Call Chains

Use case driven design, call chain abstraction, workflow managers for step-based orchestration, and common engine patterns.

---

## Use Case Driven Design

**Good design is: Domain informed, context relative, and use case driven.**

Every operation on a service contract exists only in the context of a use case. The design process starts from use cases, not from data models or technical capabilities.

### Software Requirements Specification (SRS)

The SRS should have two sections:
1. **Behavior side**: Required runtime behaviors of the system
2. **Use case definitions**: What the system must do for each actor/scenario

A **behavior** is an operation that supports a use case. You need to be able to articulate the business rules in derived behavior documentation so that the business can verify you understand the rules.

---

## Call Chains

An **abstract call chain** represents a set of related use cases. It traces the flow from manager through engines to access components. For each permutation of the call chain, you create a sequence diagram.

### Call Chain as Abstraction

```
Use Cases:
  "Online user searches by item"       ─┐
  "Online user searches by restaurant"  ─┼─→ SearchAsync call chain
  "Restaurant user searches by date"    ─┘

Call Chain:
  Client → BFF → Controller → Manager.SearchAsync()
                                  → ValidationEngine.ConfirmAsync()
                                  → OrderingEngine.MatchAsync()
                                  → RestaurantAccess.FilterAsync()
                                  → PricingEngine.CalculateAsync()
```

**Key insight**: The method call chain is an abstraction for a GROUP of use cases. Different use cases follow the same chain but with different DTOs (polymorphic criteria), which the strategy resolves.

### Naming Operations by Call Chain

At the manager level, operations are named by their call chain. The operation name reflects the business task, not the implementation steps.

```csharp
✅ GOOD: Named by business task
interface ISalesManager
{
    Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria);
    Task<OrderResponse> PlaceOrderAsync(OrderRequest request);
    Task<ConfirmationResponse> ConfirmAsync(ConfirmationRequest request);
}

❌ BAD: Named by implementation step
interface ISalesManager
{
    Task ValidateAndFilterAsync(FilterCriteria criteria);
    Task MatchAndPriceAsync(MatchRequest request);
    Task SaveAndNotifyAsync(SaveRequest request);
}
```

---

## Workflow Manager Pattern

A Workflow Manager is a type of manager that orchestrates a sequence of steps. It drives a flow through subsystems in a defined order.

### When to Use Workflow Manager

Use a workflow manager when:
- There is a defined sequence of steps (harvest → process → evaluate → verify → notify)
- The flow has defined activation and completion states
- Steps may have timeouts and compensation logic
- Different installations or configurations may have different workflows

**Not everything is a flow!** When the UI doesn't need flow-type sequencing, an operations-based approach is more appropriate.

### Workflow Structure

```csharp
// Step definition
class Step
{
    public string Name { get; set; }
    public Type Subsystem { get; set; }   // Which manager/engine handles this step
    public TimeSpan Timeout { get; set; }
}

// Workflow is a named sequence of steps
class Workflow
{
    public string Name { get; set; }
    public IEnumerable<Step> Steps { get; set; }
}

// Example: Production workflow
var productionWorkflow = new Workflow
{
    Name = "Production",
    Steps = new Step[]
    {
        new Step { Name = "Harvest",  Subsystem = typeof(IFeedManager),         Timeout = TimeSpan.FromMinutes(30) },
        new Step { Name = "Process",  Subsystem = typeof(IProcessingManager),   Timeout = TimeSpan.FromMinutes(30) },
        new Step { Name = "Evaluate", Subsystem = typeof(IControlManager),      Timeout = TimeSpan.FromMinutes(30) },
        new Step { Name = "Verify",   Subsystem = typeof(IControlManager),      Timeout = TimeSpan.FromMinutes(30) },
        new Step { Name = "Notify",   Subsystem = typeof(INotificationManager), Timeout = TimeSpan.FromMinutes(30) }
    }
};
```

### Workflow Manager Implementation

```csharp
// Workflow manager facets — segregate execution and admin capabilities
[ServiceContract]
public interface IRunAdminManager
{
    [OperationContract]
    void Start(string installationId);

    [OperationContract]
    void Suspend(string installationId, TimeSpan span);

    [OperationContract]
    void Abort(string installationId);

    [OperationContract]
    void Watch(string installationId);
}

// The workflow manager still honors volatilities even when combined
[ServiceBehavior]
public class WorkflowManager :
    ITradingWorkflowManager,
    IAdministrationWorkflowManager,
    IMarketWorkflowManager
{
    // Single deployable unit but facets maintain volatility boundaries
}
```

### Transition Logic

The workflow manager maintains state about the current step and transitions to the next step upon completion. It uses the proxy pattern to reflectively invoke the appropriate subsystem.

```csharp
void Transition()
{
    Step next = FindNextStep(currentContext);

    if (next == null)
    {
        // Workflow complete — perform completion activities
        return;
    }

    // Activate the next step
    RunHelper.Activate(next.Name);

    // Reflectively call the proxy for the next subsystem
    var proxy = ProxyFactory.Create(next.Subsystem);
    proxy.InvokeMethod(next.Name);
}
```

---

## System-Level Flows vs UI Flows

System-level flows (e.g., data processing pipelines) require different treatment from UI flows:
- System flows use `ICommand` and `IObservable` patterns
- UI flows use workflow-driven frontend with sequence configuration

### Marker Interfaces for Messaging Patterns

```csharp
// These are marker interfaces — empty by definition
// Used for clarity in the framework, a notation agreement
public interface IEvent { }
public interface IObservable { }
public interface ICommand { }
```

### Messaging Patterns

| Pattern | Description | Visual |
|---------|-------------|--------|
| **Request-Response** | Synchronous call-and-return | Solid line |
| **Eventing** | Fire-and-forget notification | Dashed black (disconnected, durable) |
| **Request-Eventual-Response** | Async with callback | Dashed grey (transient, both sides up) |

**Note**: Even with a message bus, there can be timeouts. Client code should compensate for this.

### Push API Pattern

For real-time updates (SignalR/WebSockets):
1. Client connects to Push API
2. Push API caches the connection context ID
3. Client adds this context ID to request headers
4. Backend publishes updates to Push API which pushes to the correct client

---

## Common Engine Patterns

### Validation Engine

Business logic validations—not format validation (that's at the API boundary).

```csharp
[ServiceContract]
public interface IValidationEngine
{
    [OperationContract]
    Task<ValidationResult> ConfirmRequestAsync(BusinessRequest request);

    [OperationContract]
    Task<ValidationResult> ValidateBusinessRulesAsync(RulesCriteria criteria);
}
```

### Transformation Engine

Transforms one DTO shape to another. Determines what values go into properties based on business rules.

```csharp
[ServiceContract]
public interface ITransformationEngine
{
    [OperationContract]
    Task<TargetDto> TransformAsync(SourceDto source, TransformContext context);
}
```

**Note**: Reshaping may be done by the manager directly for simple cases, or by calling the transformation engine for complex rule-based mappings. Encapsulate mapper frameworks within the transformation engine.

### Filtering Engine

Used by Notification and Feed volatility areas. Contains logic for what to include, what types of notifications to send.

```csharp
[ServiceContract]
public interface IFilteringEngine
{
    [OperationContract]
    Task<FilteredResult<T>> ApplyAsync<T>(IEnumerable<T> items, FilterCriteria criteria);
}
```

### Formatting Engine

In the context of notifications—template selection, value substitution, filling templates based on business logic.

```csharp
[ServiceContract]
public interface IFormattingEngine
{
    [OperationContract]
    Task<FormattedMessage> FormatAsync(NotificationData data, TemplateSelection selection);
}
```

### Pricing Engine

Typically a rule set. Calculates prices based on configurable business rules.

```csharp
[ServiceContract]
public interface IPricingEngine
{
    [OperationContract]
    Task<PriceResult> CalculateAsync(PriceCriteria criteria);
}
```

---

## Capturing Detailed Design Requirements

### Template for Use Case Capture

When starting detailed design, especially with junior teams, have a template to capture details consistently:

| Question | Answer |
|----------|--------|
| **How** are you capturing? | Interview + FRL (Functional Requirements List) document |
| **What** are you capturing? | UI capabilities, workflows, use cases, business rules |
| **When** in the plan? | Upfront, before coding begins |
| **How much detail?** | Greenfield = lots of detail; Brownfield = confirm facts + look for deltas |
| **Who to interview?** | UX/UI designers, Product Owner, BSA, domain experts |

### Brownfield (Existing System) Focus

- Confirm existing facts
- Look for significant deltas: new workflows, new use cases, new technology, new resources
- Ask: "What is changing? What is staying the same?"

### Greenfield Focus

- Walk through user interactions
- Identify all inputs and outputs
- Define MVP with core use cases
- Plan for future preferences and features

---

## Workflow and Call Chain Checklist

- [ ] Use cases identified and grouped into call chains
- [ ] Each manager operation named by its call chain / business task
- [ ] Polymorphic criteria used to handle use case variations within a call chain
- [ ] Workflow manager used only for genuine sequential flows
- [ ] Workflow steps have defined timeouts and subsystem assignments
- [ ] Execution and admin facets separated on workflow managers
- [ ] Marker interfaces (IEvent, IObservable, ICommand) used for messaging clarity
- [ ] Common engines identified (Validation, Transformation, Filtering, Formatting, Pricing)
- [ ] System-level flows use ICommand/IObservable, not UI workflow patterns
- [ ] Requirements captured with consistent template (how, what, when, how much, who)
