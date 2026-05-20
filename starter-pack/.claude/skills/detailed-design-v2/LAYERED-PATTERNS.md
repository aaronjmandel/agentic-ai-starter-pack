# Layered Interaction Patterns

Manager as mediator, engines, access layer patterns, context-driven resolution, and the proxy pattern for service boundaries.

---

## Manager as Mediator

The Manager is the **Mediator pattern** from GoF. It coordinates between engines and access components to fulfill use cases. It is the entry point for business operations.

### Manager Rules

1. **Stateless**: No class-level variables. In service orientation, state should be resolved at runtime.
2. **No private helper methods**: A manager service should contain only service operations. Any helper logic belongs in engines or dedicated helper classes.
3. **Operations named by call chain**: Each operation on a manager represents a call chain—a business use case.
4. **Chunky operations**: Only what the business needs. Not fine-grained find-and-filter operations, but meaningful business operations (Search, Place, Confirm).
5. **Each service is an independent unit of scale**: Managers can be scaled independently.

### Manager Structure

```csharp
// Manager implements multiple facets — one per context/volatility area
[ApplicationManifest("IDesign.Microservice.Sales", "SalesManager")]
public partial class SalesManager : ServiceBase
{
    // No class-level state!
    // No private helpers!
    // Only constructors and service operations
    public SalesManager(StatelessServiceContext context) : base(context)
    { }
}

// Online context facet — in partial class
public partial class SalesManager : ISalesManager // Online.ISalesManager
{
    async Task<FindResponseBase> ISalesManager.SearchAsync(FindCriteriaBase criteria)
    {
        OriginationContext origination = Origination;
        MyContext context = MyContext;

        // Delegate to strategy — "Look Ma, no switch!"
        return await UseCaseFactory.CallAsync<FindCriteriaBase, FindResponseBase>(
            this, criteria);
    }
}

// Restaurant context facet — same service, different facet
public partial class SalesManager : Restaurant.ISalesManager
{
    async Task<FindResponseBase> Restaurant.ISalesManager.SearchAsync(FindCriteriaBase criteria)
    {
        OriginationContext origination = Origination;
        MyContext context = MyContext;

        return await UseCaseFactory.CallAsync<FindCriteriaBase, FindResponseBase>(
            this, criteria);
    }
}
```

### Key Insight: Partial Classes for Facets

Use partial classes to organize facet implementations. Each file contains one facet's implementation, keeping the codebase manageable while the service class implements all facets.

---

## Context-Driven Resolution

Context is the originating system of the request. It impacts decision making at every layer, but is **most relevant at the Manager level**. Engines are segregated by subsystem but try to remain context-neutral to promote reuse.

### Resolving at Runtime, Not in Constructor

You need to be able to dynamically resolve the instance within the service operation—not in the constructor. Greedy constructors that require many dependencies cause testing problems and couple the service to all its possible dependencies at creation time.

```csharp
❌ BAD: Constructor-time resolution of all possible dependencies
public class SalesManager
{
    private readonly IOnlineEngine _onlineEngine;
    private readonly IRestaurantEngine _restaurantEngine;
    // Greedy — gets everything whether it needs it or not

    public SalesManager(IOnlineEngine online, IRestaurantEngine restaurant)
    {
        _onlineEngine = online;
        _restaurantEngine = restaurant;
    }
}

✅ GOOD: Runtime resolution based on context
public class SalesManager : ServiceBase
{
    async Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria)
    {
        // Resolve at runtime based on the DTO type (polymorphic strategy)
        return await UseCaseFactory.CallAsync<FindCriteriaBase, FindResponseBase>(
            this, criteria);
    }
}
```

### The UseCaseFactory Pattern

A reflection-based or IoC-based strategy that routes to the correct use case implementation based on the DTO's namespace. This eliminates switch statements and enables the system to evolve by adding new DTO types and use case classes.

```csharp
static class UseCaseFactory
{
    static Type Resolve(string classNamespace)
    {
        // Convention: Replace "Interface" with "Service" and append ".UseCases"
        string typeName = classNamespace.Replace("Interface", "Service") + ".UseCases";
        Type implementationType = Assembly.GetExecutingAssembly().GetType(typeName);
        Debug.Assert(implementationType != null, "You did not follow the rules...");
        return implementationType;
    }

    // DTO-driven strategy: namespace convention between Interface and Service
    public static Task<R> CallAsync<C, R>(
        StatelessService service,
        C criteria,
        [CallerMemberName] string name = null)
        where C : FindCriteriaBase
        where R : FindResponseBase
    {
        Type useCases = Resolve(criteria.GetType().Namespace);
        object instance = Activator.CreateInstance(useCases, service);
        MethodInfo method = useCases.GetMethod(name, new Type[] { criteria.GetType() });
        Task<R> response = method.Invoke(instance, new object[] { criteria }) as Task<R>;
        return response;
    }
}
```

### Use Case Classes

Use case implementations are **not services**—they are helper classes that contain the actual orchestration logic. Optionally apply interface and detailed design to these as well for consistency.

```csharp
namespace IDesign.Manager.Sales.Service.Online
{
    // Not a service — a use case orchestrator
    public class UseCases
    {
        ServiceBase Service { get; set; }

        public UseCases(ServiceBase service) { Service = service; }

        // Overloaded by criteria type — strategy selects correct one
        public async Task<FindResponseBase> SearchAsync(ItemCriteria criteria)
        {
            OriginationContext origination = Service.Origination;
            MyContext context = Service.MyContext;

            IRestaurantAccess proxy = Proxy.ForComponent<IRestaurantAccess>(Service);
            await proxy.FilterAsync();
            return new FindResponse();
        }

        public async Task<FindResponseBase> SearchAsync(RestaurantCriteria criteria)
        {
            IRestaurantAccess proxy = Proxy.ForComponent<IRestaurantAccess>(Service);
            await proxy.FilterAsync();
            return new FindResponse();
        }
    }
}
```

---

## The Proxy Pattern

Use the proxy pattern so that even if an object is local, you treat it as if it's remote. This enables the underlying service mesh or transport to be changed without modifying business code.

```csharp
// Always obtain dependencies through proxy factory — never new
IRestaurantAccess proxy = Proxy.ForComponent<IRestaurantAccess>(Service);
await proxy.FilterAsync();

// Proxy abstracts whether the service is:
// - In-process (for development/testing)
// - On the same machine via named pipes
// - Remote via HTTP/gRPC
// - In a service mesh
```

**Historical value**: This pattern has carried codebases forward through technology evolutions—from C++/COM through WCF through Service Fabric through Kubernetes/DAPR.

### Dependency Inversion at Service Boundary

Dependency Inversion is applied at the logic layer—not in the WebAPI controller. The controller merely packages headers and delegates to the manager.

```csharp
// Controller is thin — just packages request and calls manager
[ApiController]
public class OrdersController : ControllerBase
{
    public async Task<IActionResult> Search([FromBody] FindCriteriaBase criteria)
    {
        // Extract headers, package into context
        // Call manager through proxy
        var manager = ProxyFactory.Create<ISalesManager>();
        var result = await manager.SearchAsync(criteria);
        return Ok(result);
    }
}
```

---

## Engine Patterns

Engines contain reusable business logic that is shared across contexts and use cases.

### Common Engines

| Engine | Responsibility |
|--------|---------------|
| **Validation** | Business logic validations (not format validation—that's at the boundary) |
| **Transformation** | Transforming one DTO shape to another; mapping values to properties based on business rules |
| **Filtering** | Logic for notifications, feed content, which items to include/exclude |
| **Formatting** | In the context of notifications—template selection, value substitution, template filling |
| **Ordering** | Sales-specific matching and ordering logic |
| **Pricing** | Rule-based pricing calculations |

### Engine Design Principles

- Engines promote **reuse** across contexts—try not to diverge by context at the engine level
- If context forces divergence, create separate facets on the engine
- Strategy pattern within engines for different algorithms (e.g., matching strategies)

```csharp
[ServiceContract]
public interface IOrderingEngine
{
    [OperationContract]
    Task<MatchResult> MatchAsync(MatchCriteria criteria);
}

// Strategy within the engine handles different matching algorithms
// Without a switch — polymorphic criteria drives resolution
public class OrderingEngine : IOrderingEngine
{
    public async Task<MatchResult> MatchAsync(MatchCriteria criteria)
    {
        // The criteria type (or a strategy field within it)
        // determines which matching algorithm to use
        var strategy = ResolveStrategy(criteria);
        return await strategy.ExecuteAsync(criteria);
    }
}
```

---

## Access Layer Patterns

### FindItem Variability

The `FindItem` pattern at the access layer should support variability on three dimensions:
1. **Filter** — what criteria to use
2. **Data Contract** — what shape of data to return
3. **DTO** — what response structure

```csharp
[ServiceContract]
public interface IRestaurantAccess
{
    [OperationContract]
    Task<IEnumerable<T>> FindAsync<T>(FilterCriteria filter) where T : class;
}
```

### Strategy at Data Access Layer

Use strategy pattern at the data access layer based on polymorphic DTOs. For example, if a `RestaurantContext` criteria comes in, it resolves to a different data query strategy than an `OnlineContext` criteria.

---

## Service Statelessness

Services should be **stateless**—no class-level variables that hold state between calls.

```csharp
❌ BAD: Stateful service
public class SalesManager
{
    private List<Order> _pendingOrders = new();  // State!
    private Customer _currentCustomer;            // State!
}

✅ GOOD: Stateless service
public class SalesManager : ServiceBase
{
    // Only service infrastructure (ServiceBase context)
    // No business state
    public SalesManager(StatelessServiceContext context) : base(context) { }
}
```

**Why stateless?**
- Enables independent scaling (any instance can handle any request)
- No session affinity required
- Simpler to test
- No concurrency issues with shared state

---

## Interaction Patterns Checklist

- [ ] Manager implements Mediator pattern — coordinates, does not contain logic
- [ ] Manager has no class-level state (stateless)
- [ ] Manager has no private helper methods — logic in engines/helpers
- [ ] Manager operations are chunky and named by use case / call chain
- [ ] Context-driven resolution happens at runtime, not in constructor
- [ ] UseCaseFactory or equivalent strategy eliminates switch statements
- [ ] Proxy pattern used for all inter-service communication
- [ ] Engines promote reuse — context-neutral where possible
- [ ] Access layer supports variability on filter, data contract, and DTO
- [ ] System concerns flow via ServiceBase context, not method parameters
