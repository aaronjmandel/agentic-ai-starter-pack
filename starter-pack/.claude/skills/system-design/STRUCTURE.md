# Structure Reference

Detailed guide for layered architecture based on The Method.

## Core Concept

**Layered architecture** = Organizing components into horizontal layers where:
- Each layer has a **specific responsibility**
- Layers communicate through **well-defined interfaces**
- Dependencies flow in **one direction** (downward)

---

## The Four-Layer Architecture

```
┌─────────────────────────────────┐
│       Client Layer              │  (Presentation/UI)
├─────────────────────────────────┤
│       Business Layer            │  (Domain Logic)
├─────────────────────────────────┤
│       Resource Access Layer     │  (Infrastructure)
├─────────────────────────────────┤
│       Resources                 │  (External Systems)
└─────────────────────────────────┘
```

---

## Layer Definitions

### Client Layer (Presentation)
**Responsibility**: User interaction and presentation logic

**What it does**:
- Renders UI (web, mobile, desktop)
- Handles user input
- Formats data for display
- Manages UI state and navigation

**What it does NOT do**:
- Business rules or calculations
- Direct database access
- External service integration
- Data validation beyond format checking

**Key Principle**: **Thin client** - minimal logic, maximum delegation

**Examples**:
- Web controllers/pages
- Mobile app screens
- Desktop forms
- API endpoints

### Business Layer (Domain Logic)
**Responsibility**: Core business rules and workflows

**What it does**:
- Implements business logic and rules
- Orchestrates workflows
- Validates business constraints
- Makes business decisions
- Coordinates between resources

**What it does NOT do**:
- UI formatting or rendering
- Direct database calls
- Technology-specific code

**Key Principle**: **Technology agnostic** - no implementation details

**Examples**:
- Order processing logic
- Pricing calculations
- Business rule validation
- Workflow orchestration

### Resource Access Layer (Infrastructure)
**Responsibility**: Technical access to external resources

**What it does**:
- Database queries and updates
- External service calls (REST, SOAP, etc.)
- File system operations
- Message queue interactions
- Caching operations

**What it does NOT do**:
- Business logic or decisions
- UI concerns
- Workflow orchestration

**Key Principle**: **Pure technical operations**

**Examples**:
- Repositories (data access)
- External service clients
- Message publishers/subscribers
- File handlers

### Resources (External Systems)
**Responsibility**: External dependencies the system relies on

**What it is** (not code you write):
- Databases
- External APIs and services
- File systems
- Message queues
- Email servers
- Third-party systems

---

## Dependency Rules

### The Golden Rule
**Dependencies flow DOWNWARD only:**

```
Client Layer
    ↓ (depends on)
Business Layer
    ↓ (depends on)
Resource Access Layer
    ↓ (depends on)
Resources
```

### Allowed Dependencies
✅ Client → Business
✅ Business → Resource Access
✅ Resource Access → Resources

### Forbidden Dependencies
❌ Business → Client (business logic should not know about UI)
❌ Resource Access → Business (data access should not contain business logic)
❌ Resource Access → Client (data access should not know about UI)
❌ Any upward dependency
❌ Skipping layers (Client → Resource Access)

### Why This Rule Matters
- **Business layer remains pure**: No pollution from UI or data access
- **Substitutability**: Can replace any lower layer without affecting upper layers
- **Testability**: Can test business logic without UI or real databases
- **Stability**: Changes to UI or databases don't affect business logic

---

## Dependency Inversion in Structure

### The Challenge
Business layer needs data but shouldn't depend on concrete Resource Access implementations.

### The Solution: Interfaces

```
Business Layer:
  ├── Business Logic (concrete)
  └── IRepository Interfaces (abstractions)
          ↑
          | implements
Resource Access Layer:
  └── Concrete Repositories (implementations)
```

### How It Works

1. **Business Layer defines interfaces**:
```csharp
// In Business Layer
public interface IOrderRepository
{
    Order GetById(int id);
    void Save(Order order);
}
```

2. **Business Layer uses interfaces**:
```csharp
// In Business Layer
public class OrderProcessor
{
    private readonly IOrderRepository _repository;
    
    public OrderProcessor(IOrderRepository repository)
    {
        _repository = repository;
    }
}
```

3. **Resource Access Layer implements**:
```csharp
// In Resource Access Layer
public class SqlOrderRepository : IOrderRepository
{
    public Order GetById(int id) { /* SQL code */ }
    public void Save(Order order) { /* SQL code */ }
}
```

### Benefits
- Business layer depends on abstractions, not concrete implementations
- Can swap SQL for NoSQL, files, mocks without touching business logic
- True isolation and testability
- Follows Dependency Inversion Principle

---

## Layer-Specific Guidelines

### Client Layer Guidelines

**Keep It Thin**:
```csharp
❌ Bad (Fat Client):
public class OrderController
{
    public void PlaceOrder(OrderDto dto)
    {
        // Business logic in client layer
        if (dto.Total > 10000)
            dto.DiscountPercent = 10;
        
        // Data access in client layer
        var sql = "INSERT INTO Orders...";
    }
}

✅ Good (Thin Client):
public class OrderController
{
    private readonly IOrderProcessor _processor;
    
    public void PlaceOrder(OrderDto dto)
    {
        var result = _processor.ProcessOrder(dto);
        DisplayResult(result);
    }
}
```

**Responsibilities**:
- ✅ Input validation (format, required fields)
- ✅ Display formatting
- ✅ Navigation
- ✅ Calling business layer
- ❌ Business rules
- ❌ Data access
- ❌ Calculations

### Business Layer Guidelines

**Keep It Pure**:
```csharp
❌ Bad (Polluted):
public class OrderProcessor
{
    public void ProcessOrder(Order order)
    {
        var sql = "SELECT * FROM Inventory...";  // SQL in business
        Console.WriteLine("Order processed");     // UI in business
    }
}

✅ Good (Pure):
public class OrderProcessor
{
    private readonly IInventoryService _inventory;
    
    public OrderProcessingResult ProcessOrder(Order order)
    {
        if (!_inventory.IsAvailable(order.ProductId, order.Quantity))
            return OrderProcessingResult.InsufficientInventory;
        
        _inventory.Reserve(order.ProductId, order.Quantity);
        return OrderProcessingResult.Success;
    }
}
```

**Responsibilities**:
- ✅ Business rules and validation
- ✅ Workflow orchestration
- ✅ Business calculations
- ✅ Transaction coordination
- ❌ SQL or database specifics
- ❌ UI formatting
- ❌ Technology-specific code

### Resource Access Layer Guidelines

**Keep It Technical**:
```csharp
❌ Bad (Business Logic in Data Layer):
public class OrderRepository
{
    public void SaveOrder(Order order)
    {
        if (order.Total > 10000)  // Business logic!
            order.DiscountPercent = 10;
        
        _context.Orders.Add(order);
    }
}

✅ Good (Pure Technical):
public class OrderRepository : IOrderRepository
{
    public void Save(Order order)
    {
        _context.Orders.Add(order);
        _context.SaveChanges();
    }
}
```

**Responsibilities**:
- ✅ CRUD operations
- ✅ Query execution
- ✅ Connection management
- ✅ Data mapping
- ❌ Business rules
- ❌ Business validation
- ❌ Workflow orchestration

---

## Structural Anti-Patterns

### 1. Smart UI
**Problem**: Business logic in UI code

**Symptoms**:
- Controllers with hundreds of lines
- Duplicate logic across screens
- Cannot test business logic without UI

**Solution**: Move all business logic to Business Layer

### 2. Anemic Domain Model
**Problem**: Business Layer is just pass-through

**Symptoms**:
- Business Layer methods just call repository
- All logic in UI or database
- Business Layer adds no value

**Solution**: Put real business logic in Business Layer

### 3. Business Logic in Database
**Problem**: Business rules in stored procedures/triggers

**Symptoms**:
- Complex stored procedures
- Hard to test
- Hard to version control

**Solution**: Database should be dumb storage

### 4. Layer Skipping
**Problem**: Client directly calling Resource Access

**Symptoms**:
- UI code making database calls
- No centralized business logic
- Inconsistent business rules

**Solution**: Always go through Business Layer

### 5. Circular Dependencies
**Problem**: Lower layers depending on upper layers

**Solution**: Respect unidirectional dependency flow

---

## Component Placement Within Layers

Components span multiple layers (different aspects of same capability):

```
Order Management (Business Capability)
├── OrderController (Client Layer)
├── OrderProcessor (Business Layer)
├── OrderRepository (Resource Access Layer)
└── Orders Table (Resources)
```

**Important**: These are different aspects, not duplication.

---

## Testing Strategy by Layer

### Client Layer
- UI automation tests
- Component tests
- Should be thin enough that extensive testing isn't needed

### Business Layer (Most Important)
- Unit tests with mocked dependencies
- Test all business rules exhaustively
- Test edge cases and validation

### Resource Access Layer
- Integration tests with real database (test container)
- Test CRUD operations
- Less extensive than business layer

---

## Structure Checklist

- [ ] Four layers identified
- [ ] All components assigned to appropriate layers
- [ ] Client Layer contains only presentation logic
- [ ] Business Layer contains only business logic
- [ ] Resource Access Layer contains only technical operations
- [ ] Dependencies flow downward only
- [ ] No layer skipping
- [ ] Business Layer defines interfaces
- [ ] No circular dependencies
- [ ] Business Layer can be tested with mocked dependencies
- [ ] No business logic in Client Layer
- [ ] No business logic in Resource Access Layer or database
