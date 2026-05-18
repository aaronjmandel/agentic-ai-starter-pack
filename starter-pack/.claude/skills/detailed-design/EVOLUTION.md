# Contract Evolution and Versioning

Strategies for evolving contracts without breaking existing clients.

---

## The Versioning Challenge

Once a contract is published and used by clients, changing it is **expensive** and **risky**:
- Breaking changes require all clients to update
- Multiple versions may need to coexist
- Backward compatibility must be maintained
- Coordination across teams is complex

**Goal**: Design contracts that can evolve without breaking clients.

---

## Evolution Strategies

### Strategy 1: Additive Changes (Preferred)

**Principle**: Add new things, don't modify or remove existing things.

#### Adding New Methods

```csharp
// V1
public interface IOrderService
{
    OrderResult PlaceOrder(OrderRequest request);
    Order GetOrder(int orderId);
}

// V2 - Add new method (safe)
public interface IOrderService
{
    OrderResult PlaceOrder(OrderRequest request);
    Order GetOrder(int orderId);
    
    // New method - doesn't affect existing clients
    Task<OrderResult> PlaceOrderAsync(OrderRequest request);
}
```

#### Adding Properties to DTOs

```csharp
// V1
public class OrderRequest
{
    public int CustomerId { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
}

// V2 - Add optional properties (safe)
public class OrderRequest
{
    public int CustomerId { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
    
    // New properties - old clients simply don't send them
    public string PromoCode { get; set; }
    public GiftOptions GiftOptions { get; set; }
}
```

**Key**: New properties should be **optional** with sensible defaults.

#### Adding Optional Parameters

```csharp
// V1
public OrderResult PlaceOrder(OrderRequest request)

// V2 - Add optional parameter (safe)
public OrderResult PlaceOrder(OrderRequest request, OrderOptions options = null)
{
    options ??= new OrderOptions(); // Default if not provided
    // Process order with options
}
```

### Strategy 2: Deprecation Path

**Principle**: Mark old things as obsolete, provide new alternatives, give clients time to migrate.

```csharp
// V1
public interface IOrderService
{
    OrderResult PlaceOrder(int customerId, IEnumerable<OrderLineItem> items);
}

// V2 - Deprecate old, add new
public interface IOrderService
{
    [Obsolete("Use PlaceOrder(OrderRequest) instead. Will be removed in V3.")]
    OrderResult PlaceOrder(int customerId, IEnumerable<OrderLineItem> items);
    
    // New preferred method
    OrderResult PlaceOrder(OrderRequest request);
}

// V3 (future) - Remove deprecated method
public interface IOrderService
{
    OrderResult PlaceOrder(OrderRequest request);
}
```

**Deprecation Timeline**:
1. **V2**: Mark as obsolete, provide alternative
2. **V2.x**: Warn in logs when deprecated method called
3. **V3**: Remove deprecated method

### Strategy 3: Versioned Interfaces

**When to use**: Breaking changes are unavoidable.

```csharp
// V1 - Keep for backward compatibility
public interface IOrderService
{
    OrderResult PlaceOrder(OrderRequest request);
}

// V2 - New interface for breaking changes
public interface IOrderServiceV2
{
    Task<OrderResultV2> PlaceOrderAsync(OrderRequestV2 request);
    void CancelOrder(int orderId, CancellationReason reason); // New parameter
}
```

**Implementation Pattern**:
```csharp
public class OrderService : IOrderService, IOrderServiceV2
{
    // V1 implementation (delegates to V2)
    public OrderResult PlaceOrder(OrderRequest request)
    {
        var v2Request = MapToV2(request);
        var v2Result = PlaceOrderAsync(v2Request).GetAwaiter().GetResult();
        return MapToV1(v2Result);
    }
    
    // V2 implementation (main logic)
    public async Task<OrderResultV2> PlaceOrderAsync(OrderRequestV2 request)
    {
        // Actual implementation
    }
}
```

---

## Breaking vs Non-Breaking Changes

### Non-Breaking Changes (Safe)

✅ **Adding** new methods to interface
✅ **Adding** optional properties to DTOs
✅ **Adding** optional parameters to methods
✅ **Adding** new values to enums (at end)
✅ **Widening** return type (List → IEnumerable)
✅ **Relaxing** validation (accepting more values)

### Breaking Changes (Avoid or Version)

❌ **Removing** methods from interface
❌ **Removing** properties from DTOs
❌ **Removing** parameters from methods
❌ **Changing** property types
❌ **Changing** method signatures
❌ **Renaming** methods or properties
❌ **Adding** required properties
❌ **Narrowing** return type (IEnumerable → specific List)
❌ **Changing** enum values or removing them
❌ **Tightening** validation (rejecting previously valid values)

---

## DTO Evolution Patterns

### Pattern 1: Additive Properties

```csharp
public class OrderRequest
{
    // Original properties
    public int CustomerId { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
    
    // V2 additions - nullable/optional
    public string? PromoCode { get; set; }
    public string? Notes { get; set; }
    
    // V3 additions
    public GiftOptions? GiftOptions { get; set; }
}
```

### Pattern 2: Wrapper for New Required Fields

```csharp
// V1 DTO
public class PaymentRequest
{
    public decimal Amount { get; set; }
    public string CardNumber { get; set; }
}

// V2 - Need to add required currency
// Option A: New DTO
public class PaymentRequestV2
{
    public Money Amount { get; set; }  // Money includes currency
    public CardInfo Card { get; set; }
}

// Option B: Computed default for old clients
public class PaymentRequest
{
    public decimal Amount { get; set; }
    public string Currency { get; set; } = "USD";  // Default for V1 clients
    public string CardNumber { get; set; }
}
```

### Pattern 3: Extension Point

```csharp
public class OrderRequest
{
    public int CustomerId { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
    
    // Extension point for future additions
    public Dictionary<string, object> Extensions { get; set; }
}

// V2: Use extension for new feature before promoting to property
var request = new OrderRequest
{
    CustomerId = 123,
    Items = items,
    Extensions = new Dictionary<string, object>
    {
        ["gift_message"] = "Happy Birthday!"
    }
};
```

---

## Enum Evolution

### Safe Enum Changes

```csharp
// V1
public enum OrderStatus
{
    Pending,
    Confirmed,
    Shipped,
    Delivered
}

// V2 - Add at end (safe)
public enum OrderStatus
{
    Pending,
    Confirmed,
    Shipped,
    Delivered,
    Cancelled,    // New
    Returned      // New
}
```

### Unsafe Enum Changes

```csharp
❌ Don't reorder (changes integer values):
public enum OrderStatus
{
    Cancelled,    // Was at position 4, now 0!
    Pending,
    Confirmed,
    Shipped,
    Delivered
}

❌ Don't remove values:
public enum OrderStatus
{
    Pending,
    // Confirmed - REMOVED! Breaks existing data!
    Shipped,
    Delivered
}
```

### Enum Best Practice: Explicit Values

```csharp
// Future-proof with explicit values
public enum OrderStatus
{
    Pending = 1,
    Confirmed = 2,
    Shipped = 3,
    Delivered = 4,
    
    // V2 additions
    Cancelled = 10,
    Returned = 11,
    
    // Leave gaps for related additions
    // PartiallyShipped = 5,
    // OutForDelivery = 6,
}
```

---

## API Versioning Patterns

### URL Path Versioning

```
GET /api/v1/orders/123
GET /api/v2/orders/123
```

**Pros**: Clear, explicit
**Cons**: URL changes, caching complexity

### Query Parameter Versioning

```
GET /api/orders/123?api-version=1.0
GET /api/orders/123?api-version=2.0
```

**Pros**: Same URL base
**Cons**: Easy to forget parameter

### Header Versioning

```
GET /api/orders/123
Accept: application/vnd.myapp.v1+json
Accept: application/vnd.myapp.v2+json
```

**Pros**: Clean URLs
**Cons**: Harder to test, less visible

### Recommended: URL Path for Major, Header for Minor

```
// Major version in URL
GET /api/v2/orders/123

// Minor version in header
Api-Version: 2.1
```

---

## Semantic Versioning for Contracts

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (new interface version)
- **MINOR**: New features (backward compatible additions)
- **PATCH**: Bug fixes (no contract changes)

### Examples

| Change | Version Bump |
|--------|--------------|
| Add optional property to DTO | Minor |
| Add new method to interface | Minor |
| Add new enum value | Minor |
| Fix documentation | Patch |
| Change method signature | Major |
| Remove property | Major |
| Change property type | Major |

---

## Migration Strategies

### Strategy 1: Parallel Operation

```
Both V1 and V2 endpoints active
V1 → Adapter → V2 Logic
V2 → V2 Logic

Timeline:
1. Deploy V2 alongside V1
2. Migrate clients to V2
3. Monitor V1 usage
4. Deprecate V1 when usage is low
5. Remove V1
```

### Strategy 2: Strangler Fig

```
Gradually replace V1 with V2

Timeline:
1. Deploy V2 for new features
2. Route some V1 traffic to V2
3. Expand V2 coverage
4. Eventually all traffic goes to V2
5. Remove V1
```

### Strategy 3: Big Bang (Avoid if Possible)

```
Replace V1 with V2 at single point in time

Timeline:
1. Develop V2
2. Coordinate with all clients
3. Switch everything at once
4. Hope nothing breaks

Risk: High
Recommended: Only when client count is small and controlled
```

---

## Contract Evolution Checklist

### Before Making Changes
- [ ] Is this change necessary?
- [ ] Can it be additive (non-breaking)?
- [ ] Who are the clients affected?
- [ ] How will clients be notified?
- [ ] What's the migration timeline?

### For Additive Changes
- [ ] New properties are optional/nullable
- [ ] New parameters have default values
- [ ] New methods don't affect existing ones
- [ ] New enum values added at end
- [ ] Defaults provide sensible behavior for old clients

### For Breaking Changes
- [ ] Is a new interface version needed?
- [ ] Is there a deprecation path?
- [ ] Can old and new coexist?
- [ ] Is there an adapter from old to new?
- [ ] Have clients been notified?
- [ ] Is timeline communicated?

### Documentation
- [ ] Changelog maintained
- [ ] Migration guide provided
- [ ] Deprecation warnings added
- [ ] Version documented in contract
