# Method Signature Patterns

Detailed guide for designing clean, maintainable method signatures.

---

## Parameter Design Patterns

### Pattern 1: Parameter Object

**When to use**: Method needs > 3 related parameters

```csharp
❌ Before:
public OrderResult PlaceOrder(
    int customerId,
    string shippingStreet,
    string shippingCity,
    string shippingState,
    string shippingZip,
    string paymentMethod,
    string cardNumber,
    string expiryDate,
    string cvv,
    IEnumerable<int> productIds,
    IEnumerable<int> quantities)

✅ After:
public OrderResult PlaceOrder(OrderRequest request)

public class OrderRequest
{
    public int CustomerId { get; set; }
    public ShippingAddress Shipping { get; set; }
    public PaymentInfo Payment { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
}
```

**Benefits**:
- Clear grouping of related data
- Easy to extend (add properties)
- Self-documenting
- Reduces cognitive load

### Pattern 2: Fluent Builder for Complex Objects

**When to use**: Complex parameter objects with many optional fields

```csharp
// Builder pattern for complex requests
var request = new OrderRequestBuilder()
    .ForCustomer(customerId)
    .ShipTo(address)
    .PayWith(paymentInfo)
    .AddItem(product1, quantity1)
    .AddItem(product2, quantity2)
    .ApplyPromoCode("SAVE10")
    .Build();

var result = orderService.PlaceOrder(request);
```

### Pattern 3: Value Objects for Domain Concepts

**When to use**: Primitive types don't express domain meaning

```csharp
❌ Primitive Obsession:
public void Transfer(int fromAccountId, int toAccountId, decimal amount)
// Easy to mix up the two ints!

✅ Value Objects:
public void Transfer(AccountId from, AccountId to, Money amount)

public record AccountId(int Value);
public record Money(decimal Amount, Currency Currency)
{
    public static Money USD(decimal amount) => new(amount, Currency.USD);
    public static Money EUR(decimal amount) => new(amount, Currency.EUR);
}

// Usage is now explicit:
Transfer(AccountId.From(123), AccountId.To(456), Money.USD(100));
```

**Benefits**:
- Type safety (can't mix up parameters)
- Self-documenting
- Can add validation in constructor
- Can add domain methods

### Pattern 4: Options Pattern for Optional Configuration

**When to use**: Many optional settings/flags

```csharp
❌ Boolean flags explosion:
public void SendEmail(
    string to, string subject, string body,
    bool sendAsync, bool trackOpens, bool trackClicks,
    bool requireTls, bool allowRetry, int maxRetries)

✅ Options object:
public void SendEmail(EmailMessage message, EmailOptions options = null)

public class EmailOptions
{
    public bool SendAsync { get; set; } = true;
    public TrackingOptions Tracking { get; set; }
    public SecurityOptions Security { get; set; }
    public RetryOptions Retry { get; set; }
}
```

---

## Return Type Patterns

### Pattern 1: Result Object for Failable Operations

**When to use**: Operation can fail with business-level errors

```csharp
public class OperationResult<T>
{
    public bool IsSuccessful { get; }
    public T Value { get; }
    public string ErrorMessage { get; }
    public ErrorCode ErrorCode { get; }
    
    public static OperationResult<T> Success(T value) 
        => new() { IsSuccessful = true, Value = value };
    
    public static OperationResult<T> Failure(ErrorCode code, string message)
        => new() { IsSuccessful = false, ErrorCode = code, ErrorMessage = message };
}

// Usage
public OperationResult<Order> GetOrder(int orderId)
{
    var order = _repository.Find(orderId);
    if (order == null)
        return OperationResult<Order>.Failure(
            ErrorCode.NotFound, 
            $"Order {orderId} not found");
    
    return OperationResult<Order>.Success(order);
}
```

### Pattern 2: Specialized Result Types

**When to use**: Operation has specific success/failure modes

```csharp
public class PaymentResult
{
    public bool IsSuccessful { get; set; }
    public string TransactionId { get; set; }
    public PaymentResultCode ResultCode { get; set; }
    public string ErrorMessage { get; set; }
    
    // Helper methods
    public static PaymentResult Approved(string transactionId)
        => new() { IsSuccessful = true, TransactionId = transactionId, ResultCode = PaymentResultCode.Approved };
    
    public static PaymentResult Declined(string reason)
        => new() { IsSuccessful = false, ResultCode = PaymentResultCode.Declined, ErrorMessage = reason };
}

public enum PaymentResultCode
{
    Approved,
    Declined,
    InsufficientFunds,
    ExpiredCard,
    InvalidCard,
    SecurityCheckFailed,
    NetworkError
}
```

### Pattern 3: Async with Cancellation

**When to use**: Long-running or I/O-bound operations

```csharp
public interface IOrderService
{
    Task<OrderResult> PlaceOrderAsync(
        OrderRequest request, 
        CancellationToken cancellationToken = default);
    
    Task<IEnumerable<Order>> GetOrdersAsync(
        int customerId,
        CancellationToken cancellationToken = default);
}
```

### Pattern 4: Pagination for Collections

**When to use**: Returning potentially large collections

```csharp
public class PagedResult<T>
{
    public IEnumerable<T> Items { get; set; }
    public int TotalCount { get; set; }
    public int PageNumber { get; set; }
    public int PageSize { get; set; }
    public bool HasNextPage => PageNumber * PageSize < TotalCount;
    public bool HasPreviousPage => PageNumber > 1;
}

public interface IOrderQueryService
{
    PagedResult<Order> GetOrders(OrderSearchCriteria criteria, PagingOptions paging);
}

public class PagingOptions
{
    public int PageNumber { get; set; } = 1;
    public int PageSize { get; set; } = 20;
    public string SortBy { get; set; }
    public SortDirection SortDirection { get; set; } = SortDirection.Ascending;
}
```

---

## Naming Patterns

### Commands (State-Changing Operations)

**Pattern**: Verb + Noun (imperative mood)

```csharp
✅ Good command names:
PlaceOrder(OrderRequest request)
ConfirmPayment(int orderId)
CancelOrder(int orderId, string reason)
ShipOrder(int orderId, ShipmentInfo info)
ApplyDiscount(int orderId, string promoCode)
DeactivateCustomer(int customerId)
TransferFunds(TransferRequest request)
```

### Queries (Data Retrieval Operations)

**Pattern**: Get + Noun (for single items) or Get + PluralNoun (for collections)

```csharp
✅ Good query names:
Order GetOrder(int orderId)
Customer GetCustomer(int customerId)
IEnumerable<Order> GetOrders(OrderSearchCriteria criteria)
IEnumerable<Order> GetCustomerOrders(int customerId)
IEnumerable<Order> GetPendingOrders()
OrderStatistics GetOrderStatistics(DateRange period)
```

### Boolean Queries

**Pattern**: Is/Has/Can + Condition

```csharp
✅ Good boolean query names:
bool IsEmailAvailable(string email)
bool HasActiveSubscription(int customerId)
bool CanPlaceOrder(int customerId)
bool IsInStock(int productId, int quantity)
```

### Avoid These Names

```csharp
❌ Bad names (too generic):
void Process(object data)
void Execute(Request request)
void Handle(Event event)
object Get(int id)
void Set(int id, object value)
void DoSomething(Data data)
Result PerformAction(Input input)
```

---

## Overloading Patterns

### Pattern 1: Convenience Overloads

**When to use**: Common use cases with fewer parameters

```csharp
public interface IOrderService
{
    // Full version
    IEnumerable<Order> GetOrders(OrderSearchCriteria criteria, PagingOptions paging);
    
    // Convenience overload - default paging
    IEnumerable<Order> GetOrders(OrderSearchCriteria criteria)
        => GetOrders(criteria, PagingOptions.Default);
    
    // Convenience overload - get by customer
    IEnumerable<Order> GetCustomerOrders(int customerId)
        => GetOrders(new OrderSearchCriteria { CustomerId = customerId });
}
```

### Pattern 2: Optional Parameters vs Overloads

**Prefer optional parameters** for backward compatibility:
```csharp
// V1
OrderResult PlaceOrder(OrderRequest request)

// V2 - Add optional parameter
OrderResult PlaceOrder(OrderRequest request, OrderOptions options = null)
```

**Prefer overloads** for significantly different signatures:
```csharp
// Different parameter types warrant overloads
Order GetOrder(int orderId);
Order GetOrder(string orderReference);
IEnumerable<Order> GetOrders(OrderSearchCriteria criteria);
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Boolean Parameters

```csharp
❌ Boolean parameters hide intent:
public void SendEmail(string to, string body, bool isHtml, bool isUrgent, bool trackOpens)
// What does SendEmail(to, body, true, false, true) mean?

✅ Use enums or options object:
public void SendEmail(string to, string body, EmailFormat format, EmailPriority priority, EmailOptions options)
// Or
public void SendEmail(EmailMessage message, EmailOptions options)
```

### Anti-Pattern 2: Out/Ref Parameters

```csharp
❌ Out parameters:
public bool TryGetOrder(int orderId, out Order order)

✅ Return result object:
public OrderResult GetOrder(int orderId)

public class OrderResult
{
    public bool Found { get; set; }
    public Order Order { get; set; }
}
```

### Anti-Pattern 3: Inconsistent Async

```csharp
❌ Mixing sync and async:
public interface IOrderService
{
    Order GetOrder(int orderId);
    Task<OrderResult> PlaceOrderAsync(OrderRequest request);
    IEnumerable<Order> GetOrders();
    Task DeleteOrderAsync(int orderId);
}

✅ Consistent async:
public interface IOrderService
{
    Task<Order> GetOrderAsync(int orderId);
    Task<OrderResult> PlaceOrderAsync(OrderRequest request);
    Task<IEnumerable<Order>> GetOrdersAsync();
    Task DeleteOrderAsync(int orderId);
}
```

---

## Checklist: Method Signature Review

- [ ] ≤ 3-4 parameters (use parameter object if more)
- [ ] No primitive obsession (use value objects for domain concepts)
- [ ] Return specific types, not generic (no object, Dictionary<string, object>)
- [ ] Return domain types, not infrastructure (no DataTable, SqlDataReader)
- [ ] Failable operations return Result objects
- [ ] Collections return IEnumerable or IReadOnlyCollection
- [ ] Large collections support pagination
- [ ] Names reveal business intention
- [ ] Commands use imperative verbs (Place, Confirm, Cancel)
- [ ] Queries use Get + Noun pattern
- [ ] No boolean parameters (use enums or options)
- [ ] No out/ref parameters (use result objects)
- [ ] Async methods suffixed with "Async"
- [ ] Async methods accept CancellationToken
