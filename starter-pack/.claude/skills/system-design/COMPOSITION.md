# Composition Reference

Detailed guide for component composition and dependency injection based on The Method.

## Core Concept

**Composition over Inheritance**: Build components by combining smaller, focused components through delegation, not inheritance hierarchies.

---

## Why Composition Over Inheritance?

### Problems with Inheritance
- ❌ Creates **tight coupling** between parent and child
- ❌ Leads to **deep hierarchies** (fragile base class problem)
- ❌ Forces **compile-time decisions**
- ❌ Violates **SRP** (child inherits all parent responsibilities)
- ❌ Creates **rigidity**

### Benefits of Composition
- ✅ **Loose coupling** through interfaces
- ✅ **Flexible assembly** at runtime
- ✅ **Single Responsibility** per component
- ✅ **Testability** through mocking
- ✅ **Runtime flexibility**

---

## Dependency Injection (DI)

### Definition
A component receives its dependencies from an external source rather than creating them itself.

### Without DI (Bad)
```csharp
❌ Component Creates Dependencies:
public class OrderProcessor
{
    private readonly SqlOrderRepository _repository;
    
    public OrderProcessor()
    {
        _repository = new SqlOrderRepository();  // Tight coupling!
    }
}
```

**Problems**:
- Tightly coupled to concrete class
- Cannot swap implementations
- Cannot test with mocks
- Violates Dependency Inversion Principle

### With DI (Good)
```csharp
✅ Dependencies Injected:
public class OrderProcessor
{
    private readonly IOrderRepository _repository;
    
    public OrderProcessor(IOrderRepository repository)
    {
        _repository = repository;  // Loose coupling!
    }
}
```

**Benefits**:
- Loosely coupled to interface
- Can inject any implementation
- Easy to test with mocks
- Follows Dependency Inversion Principle

---

## Three Types of Dependency Injection

### 1. Constructor Injection (Preferred - 95% of cases)

**What**: Dependencies passed through constructor
**When**: For **required dependencies**

```csharp
✅ Constructor Injection:
public class OrderProcessor
{
    private readonly IOrderRepository _repository;
    private readonly IInventoryService _inventory;
    
    public OrderProcessor(
        IOrderRepository repository,
        IInventoryService inventory)
    {
        _repository = repository ?? throw new ArgumentNullException();
        _inventory = inventory ?? throw new ArgumentNullException();
    }
}
```

**Advantages**:
- Dependencies clearly visible
- Component always in valid state
- Immutable once constructed (thread-safe)
- Compiler enforces providing dependencies

### 2. Property Injection (Use Sparingly)

**What**: Dependencies set through public properties
**When**: For **optional dependencies** (logging, telemetry)

```csharp
⚠️ Property Injection:
public class OrderProcessor
{
    private readonly IOrderRepository _repository;
    
    public ILogger Logger { get; set; }  // Optional
    
    public OrderProcessor(IOrderRepository repository)
    {
        _repository = repository;
    }
    
    public void ProcessOrder(int orderId)
    {
        Logger?.Log($"Processing {orderId}");  // Use if available
    }
}
```

**Disadvantages**:
- Component can be in invalid state
- Not obvious what's required
- Easy to forget to set

### 3. Method Injection (Rare)

**What**: Dependencies passed to specific methods
**When**: For **per-operation dependencies**

```csharp
⚠️ Method Injection:
public class ReportGenerator
{
    public Report Generate(IDataSource dataSource)
    {
        // dataSource varies per call
        return FormatReport(dataSource.GetData());
    }
}
```

**Use Case**: When dependency varies with each method call

---

## Inversion of Control (IoC) Containers

### What They Do

1. **Registration** (configuration phase):
```csharp
container.Register<IOrderRepository, SqlOrderRepository>();
container.Register<IInventoryService, InventoryService>();
container.Register<IOrderProcessor, OrderProcessor>();
```

2. **Resolution** (runtime phase):
```csharp
var processor = container.Resolve<IOrderProcessor>();
// Container automatically:
// 1. Creates SqlOrderRepository
// 2. Creates InventoryService
// 3. Creates OrderProcessor with both injected
```

---

## Lifetimes (Scope Management)

### Transient
**Definition**: New instance every time
**Use for**: Lightweight, stateless objects

```csharp
container.Register<IValidator, OrderValidator>(Lifetime.Transient);
```

### Singleton
**Definition**: Single instance for entire application
**Use for**: Expensive to create, thread-safe, stateless

```csharp
container.Register<ILogger, FileLogger>(Lifetime.Singleton);
```

### Scoped (Per-Request)
**Definition**: One instance per scope (web request)
**Use for**: Shared within operation but not across operations

```csharp
container.Register<IOrderRepository, SqlOrderRepository>(Lifetime.Scoped);
```

**Critical for Web**: Ensures database context isn't shared across requests

---

## Composition Root

### Definition
The **single place** in your application where all component wiring happens.

### Location
Application entry point (Main, Startup, Application_Start)

### Principle
All dependency resolution happens in ONE place, as close to application entry as possible.

### Example
```csharp
✅ Single Composition Root:
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // ALL wiring happens here
        services.AddScoped<IOrderRepository, SqlOrderRepository>();
        services.AddScoped<IInventoryService, InventoryService>();
        services.AddScoped<IOrderProcessor, OrderProcessor>();
        services.AddSingleton<ILogger, FileLogger>();
    }
}
```

**Key Point**: Components themselves NEVER interact with container. Only composition root resolves.

---

## Service Locator Anti-Pattern

### What It Is
Pattern where components ask a global registry for dependencies.

### Why It's Bad
```csharp
❌ Service Locator:
public class OrderProcessor
{
    public void ProcessOrder(int orderId)
    {
        // Component asks for dependencies
        var repository = ServiceLocator.Resolve<IOrderRepository>();
        var inventory = ServiceLocator.Resolve<IInventoryService>();
    }
}
```

**Problems**:
- **Hidden dependencies**: Not obvious what component needs
- **Runtime failures**: Missing dependencies found at runtime
- **Hard to test**: Must configure service locator in every test
- **Tight coupling**: Component coupled to service locator
- **Violates SRP**: Component responsible for obtaining dependencies

### The Right Way
```csharp
✅ Dependency Injection:
public class OrderProcessor
{
    private readonly IOrderRepository _repository;
    private readonly IInventoryService _inventory;
    
    // Dependencies explicit and obvious
    public OrderProcessor(
        IOrderRepository repository,
        IInventoryService inventory)
    {
        _repository = repository;
        _inventory = inventory;
    }
}
```

**Rule**: Components should NEVER interact with IoC container.

---

## Composition Best Practices

### 1. Constructor Injection for Required Dependencies
```csharp
✅ Always prefer constructor injection:
public OrderProcessor(IOrderRepository repository)
{
    _repository = repository ?? throw new ArgumentNullException();
}
```

### 2. Validate Dependencies
```csharp
✅ Validate in constructor:
public OrderProcessor(IOrderRepository repository)
{
    _repository = repository ?? throw new ArgumentNullException();
}

❌ Don't validate lazily:
public void ProcessOrder()
{
    if (_repository == null)  // Too late!
        throw new InvalidOperationException();
}
```

### 3. Avoid Constructor Over-Injection
**Rule**: More than 4-5 parameters suggests SRP violation

```csharp
❌ Too many dependencies:
public OrderProcessor(
    IOrderRepository repo,
    IInventoryService inventory,
    IPaymentGateway payment,
    IShippingService shipping,
    IEmailService email,
    ILogger logger,
    ICache cache,
    IEventBus eventBus,
    IMetrics metrics)  // 9 dependencies!
{
    // This component does too much
}
```

**Solution**: Break into smaller, focused components

### 4. Interface Segregation
```csharp
✅ Small, focused interfaces:
public interface IOrderReader
{
    Order GetById(int id);
}

public interface IOrderWriter
{
    void Save(Order order);
}

❌ Large, unfocused interface:
public interface IOrderRepository
{
    // 20+ methods
}
```

### 5. Avoid Circular Dependencies
```csharp
❌ Circular dependency:
public class OrderProcessor
{
    public OrderProcessor(IInventoryService inventory) { }
}

public class InventoryService
{
    public InventoryService(IOrderProcessor order) { }  // Circular!
}
```

**Solution**: Events, extract shared functionality, rethink boundaries

---

## Composition Anti-Patterns

### 1. New Keyword in Components
```csharp
❌ Creating dependencies:
public OrderProcessor()
{
    _repository = new SqlOrderRepository();
}
```

### 2. Static Dependencies
```csharp
❌ Static calls:
public void ProcessOrder()
{
    var order = OrderRepository.GetById(id);  // Static
}
```

### 3. Service Locator
```csharp
❌ Asking for dependencies:
public void ProcessOrder()
{
    var repo = ServiceLocator.Resolve<IOrderRepository>();
}
```

### 4. Ambient Context
```csharp
❌ Global state:
public void ProcessOrder()
{
    var order = Database.Current.Orders.Find(id);  // Global
}
```

---

## Testing with Composition

### Easy Mocking
```csharp
✅ Testing with DI:
[Test]
public void ProcessOrder_InsufficientInventory_ReturnsFailure()
{
    // Arrange - create mocks
    var mockRepository = new Mock<IOrderRepository>();
    var mockInventory = new Mock<IInventoryService>();
    mockInventory.Setup(i => i.IsAvailable(1, 10)).Returns(false);
    
    // Create with mocks
    var processor = new OrderProcessor(
        mockRepository.Object,
        mockInventory.Object);
    
    // Act
    var result = processor.ProcessOrder(new Order { ProductId = 1, Quantity = 10 });
    
    // Assert
    Assert.AreEqual(OrderProcessingResult.InsufficientInventory, result);
}
```

---

## Composition Checklist

- [ ] All components use constructor injection for required dependencies
- [ ] No components create dependencies with `new`
- [ ] No components use static dependencies
- [ ] No components call IoC container
- [ ] Single composition root at application entry
- [ ] IoC container configured with all dependencies
- [ ] Appropriate lifetimes set
- [ ] Business Layer defines interfaces
- [ ] Resource Access Layer implements interfaces
- [ ] Dependencies validated in constructors
- [ ] No component has more than 5 constructor parameters
- [ ] No circular dependencies
- [ ] Property injection only for optional dependencies
- [ ] Tests use mock dependencies via constructor injection
