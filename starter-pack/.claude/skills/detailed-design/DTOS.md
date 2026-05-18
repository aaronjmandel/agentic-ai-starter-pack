# DTO Design Guide

Complete guide for designing Data Transfer Objects.

---

## What Are DTOs?

**Definition**: Simple objects that carry data between processes/layers, without business logic.

**Purpose**:
- Define contract data structures
- Prevent coupling to domain model
- Enable versioning and evolution
- Optimize data transfer

**Not DTOs**:
- Domain entities (have behavior)
- View models (may have presentation logic)
- Active Record objects (have persistence logic)

---

## Core DTO Rules

### Rule 1: DTOs Are Simple Data Holders

```csharp
✅ Good DTO - just data:
public class OrderRequest
{
    public int CustomerId { get; set; }
    public ShippingAddress Shipping { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
    public string PromoCode { get; set; }
}

❌ Bad DTO - has logic:
public class OrderRequest
{
    public int CustomerId { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
    
    // ❌ DTOs should NOT have logic
    public decimal CalculateTotal()
    {
        return Items.Sum(i => i.Price * i.Quantity);
    }
    
    // ❌ DTOs should NOT have validation logic
    public bool IsValid()
    {
        return CustomerId > 0 && Items.Any();
    }
}
```

### Rule 2: DTOs Should Be Serializable

```csharp
✅ Easily serializable:
public class OrderInfo
{
    public int OrderId { get; set; }
    public string CustomerName { get; set; }
    public decimal Total { get; set; }
    public DateTime OrderDate { get; set; }
    public List<OrderLineDto> Lines { get; set; }
}

❌ Not serializable:
public class OrderInfo
{
    public Order DomainOrder { get; set; }           // Complex domain object
    public IQueryable<OrderLine> Lines { get; set; } // Lazy loading
    public SqlConnection Connection { get; set; }    // Non-serializable
    public Func<decimal> Calculator { get; set; }    // Function reference
    public Stream DataStream { get; set; }           // Stream
}
```

### Rule 3: Keep DTO Hierarchies Flat

```csharp
❌ Too deep (5 levels):
public class OrderRequest
{
    public CustomerInfo Customer { get; set; }
}

public class CustomerInfo
{
    public AddressInfo Address { get; set; }
}

public class AddressInfo
{
    public CountryInfo Country { get; set; }
}

public class CountryInfo
{
    public RegionInfo Region { get; set; }
}
// Hard to work with, hard to serialize

✅ Flat structure (2 levels max):
public class OrderRequest
{
    public int CustomerId { get; set; }
    public ShippingAddress Shipping { get; set; }
    public BillingAddress Billing { get; set; }
}

public class ShippingAddress
{
    public string Street { get; set; }
    public string City { get; set; }
    public string State { get; set; }
    public string Country { get; set; }
    public string ZipCode { get; set; }
}
```

### Rule 4: Separate DTOs from Domain Model

```csharp
❌ Exposing domain model:
public interface IOrderService
{
    Order PlaceOrder(Order order);        // Domain object in contract
    Customer GetCustomer(int id);         // Domain object exposed
}

✅ Separate DTOs:
public interface IOrderService
{
    OrderResult PlaceOrder(OrderRequest request);   // Request DTO
    CustomerInfo GetCustomer(int customerId);       // Response DTO
}

// Domain model (internal)
public class Order
{
    public int Id { get; private set; }
    public Customer Customer { get; private set; }
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();
    
    public void AddLine(Product product, int quantity)
    {
        // Domain logic here
    }
    
    public decimal CalculateTotal()
    {
        // Business logic here
    }
}

// DTO (external contract)
public class OrderInfo
{
    public int OrderId { get; set; }
    public int CustomerId { get; set; }
    public string CustomerName { get; set; }
    public decimal Total { get; set; }
    public List<OrderLineInfo> Lines { get; set; }
}
```

**Why separate?**
- Domain model can evolve independently
- Contract remains stable
- Domain has behavior, DTOs are just data
- Can optimize DTO for network/serialization

---

## DTO Categories

### Request DTOs (Input)

**Purpose**: Carry data INTO an operation

```csharp
public class OrderRequest
{
    public int CustomerId { get; set; }
    public ShippingAddress Shipping { get; set; }
    public PaymentInfo Payment { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
    public string PromoCode { get; set; }
}

public class OrderLineItem
{
    public int ProductId { get; set; }
    public int Quantity { get; set; }
}

public class PaymentInfo
{
    public PaymentMethod Method { get; set; }
    public string CardNumber { get; set; }
    public string ExpiryDate { get; set; }
    public string Cvv { get; set; }
}
```

### Response DTOs (Output)

**Purpose**: Carry data OUT of an operation

```csharp
public class OrderInfo
{
    public int OrderId { get; set; }
    public DateTime OrderDate { get; set; }
    public OrderStatus Status { get; set; }
    public CustomerSummary Customer { get; set; }
    public decimal Subtotal { get; set; }
    public decimal Tax { get; set; }
    public decimal Total { get; set; }
    public IEnumerable<OrderLineInfo> Lines { get; set; }
}

public class OrderLineInfo
{
    public int LineId { get; set; }
    public string ProductName { get; set; }
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal LineTotal { get; set; }
}
```

### Result DTOs (Operation Outcome)

**Purpose**: Communicate success/failure with details

```csharp
public class OrderResult
{
    public bool IsSuccessful { get; set; }
    public int OrderId { get; set; }
    public OrderResultCode ResultCode { get; set; }
    public string ErrorMessage { get; set; }
    public ValidationErrors ValidationErrors { get; set; }
}

public enum OrderResultCode
{
    Success,
    InsufficientInventory,
    PaymentDeclined,
    InvalidAddress,
    InvalidPromoCode,
    CustomerNotFound
}

public class ValidationErrors
{
    public Dictionary<string, string[]> Errors { get; set; }
    
    public bool HasErrors => Errors?.Any() == true;
}
```

### Search/Filter DTOs (Criteria)

**Purpose**: Define search parameters

```csharp
public class OrderSearchCriteria
{
    public int? CustomerId { get; set; }
    public DateRange OrderDateRange { get; set; }
    public OrderStatus? Status { get; set; }
    public decimal? MinTotal { get; set; }
    public decimal? MaxTotal { get; set; }
    public IEnumerable<int> ProductIds { get; set; }
}

public class DateRange
{
    public DateTime? From { get; set; }
    public DateTime? To { get; set; }
}

public class PagingOptions
{
    public int PageNumber { get; set; } = 1;
    public int PageSize { get; set; } = 20;
    public string SortBy { get; set; }
    public SortDirection SortDirection { get; set; }
}
```

---

## DTO Naming Conventions

### Pattern: [Entity][Purpose]

| Purpose | Suffix | Example |
|---------|--------|---------|
| Input/Request | Request | `OrderRequest`, `PaymentRequest` |
| Output/Response | Info, Dto, or none | `OrderInfo`, `CustomerDto`, `Order` |
| Result/Outcome | Result | `OrderResult`, `PaymentResult` |
| Search criteria | Criteria, Filter | `OrderSearchCriteria`, `ProductFilter` |
| Summary/Light | Summary | `CustomerSummary`, `OrderSummary` |
| Full/Detailed | Details | `OrderDetails`, `CustomerDetails` |

### Examples

```csharp
// Request DTOs
public class CreateOrderRequest { }
public class UpdateCustomerRequest { }
public class TransferFundsRequest { }

// Response DTOs
public class OrderInfo { }
public class CustomerDetails { }
public class ProductSummary { }

// Result DTOs
public class OrderResult { }
public class PaymentResult { }
public class ValidationResult { }

// Criteria DTOs
public class OrderSearchCriteria { }
public class ProductFilterCriteria { }
```

---

## DTO Design Patterns

### Pattern 1: Immutable DTOs (Recommended for Responses)

```csharp
public class OrderInfo
{
    public int OrderId { get; init; }
    public DateTime OrderDate { get; init; }
    public decimal Total { get; init; }
    public IReadOnlyCollection<OrderLineInfo> Lines { get; init; }
}

// Or using records (C# 9+)
public record OrderInfo(
    int OrderId,
    DateTime OrderDate,
    decimal Total,
    IReadOnlyCollection<OrderLineInfo> Lines);
```

**Benefits**:
- Thread-safe
- Predictable
- Clear intent (data won't change)

### Pattern 2: Builder for Complex DTOs

```csharp
public class OrderRequest
{
    public int CustomerId { get; private set; }
    public ShippingAddress Shipping { get; private set; }
    public List<OrderLineItem> Items { get; private set; }
    
    private OrderRequest() { }
    
    public class Builder
    {
        private readonly OrderRequest _request = new();
        
        public Builder ForCustomer(int customerId)
        {
            _request.CustomerId = customerId;
            return this;
        }
        
        public Builder ShipTo(ShippingAddress address)
        {
            _request.Shipping = address;
            return this;
        }
        
        public Builder AddItem(int productId, int quantity)
        {
            _request.Items ??= new List<OrderLineItem>();
            _request.Items.Add(new OrderLineItem { ProductId = productId, Quantity = quantity });
            return this;
        }
        
        public OrderRequest Build() => _request;
    }
}

// Usage
var request = new OrderRequest.Builder()
    .ForCustomer(123)
    .ShipTo(address)
    .AddItem(productId, 2)
    .AddItem(anotherProductId, 1)
    .Build();
```

### Pattern 3: Projection DTOs

**Purpose**: Return only needed fields (avoid over-fetching)

```csharp
// Full entity has many fields
public class CustomerInfo
{
    public int Id { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public DateTime RegisteredDate { get; set; }
    public Address Address { get; set; }
    public IEnumerable<OrderInfo> Orders { get; set; }
}

// Summary projection - just what's needed for a list
public class CustomerSummary
{
    public int Id { get; set; }
    public string FullName { get; set; }  // Computed: FirstName + LastName
    public string Email { get; set; }
}

// Different contexts need different projections
IEnumerable<CustomerSummary> GetCustomerList();  // For dropdowns, lists
CustomerInfo GetCustomerDetails(int id);          // For detail view
```

---

## Mapping Between DTOs and Domain

### Manual Mapping

```csharp
public class OrderMapper
{
    public OrderInfo ToDto(Order order)
    {
        return new OrderInfo
        {
            OrderId = order.Id,
            OrderDate = order.OrderDate,
            Status = order.Status,
            Total = order.CalculateTotal(),
            Lines = order.Lines.Select(ToLineDto).ToList()
        };
    }
    
    public OrderLineInfo ToLineDto(OrderLine line)
    {
        return new OrderLineInfo
        {
            LineId = line.Id,
            ProductName = line.Product.Name,
            Quantity = line.Quantity,
            UnitPrice = line.UnitPrice,
            LineTotal = line.GetLineTotal()
        };
    }
    
    public Order ToDomain(OrderRequest request)
    {
        var order = new Order(request.CustomerId);
        foreach (var item in request.Items)
        {
            order.AddLine(item.ProductId, item.Quantity);
        }
        return order;
    }
}
```

### Extension Methods for Mapping

```csharp
public static class OrderMappingExtensions
{
    public static OrderInfo ToDto(this Order order)
    {
        return new OrderInfo
        {
            OrderId = order.Id,
            OrderDate = order.OrderDate,
            Total = order.CalculateTotal()
        };
    }
    
    public static IEnumerable<OrderInfo> ToDtos(this IEnumerable<Order> orders)
    {
        return orders.Select(o => o.ToDto());
    }
}

// Usage
var orderDto = order.ToDto();
var orderDtos = orders.ToDtos();
```

---

## DTO Anti-Patterns

### Anti-Pattern 1: Anemic Domain Model Disguised as DTOs

```csharp
❌ This is NOT a proper DTO - it's an anemic domain model:
public class Order
{
    public int Id { get; set; }
    public int CustomerId { get; set; }
    public List<OrderLine> Lines { get; set; }
    public decimal Total { get; set; }
    public string Status { get; set; }
}

// All logic in "service"
public class OrderService
{
    public decimal CalculateTotal(Order order) { }
    public bool CanShip(Order order) { }
    public void AddLine(Order order, int productId) { }
}
```

### Anti-Pattern 2: One DTO for Everything

```csharp
❌ One DTO used everywhere:
public class CustomerDto
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public string Password { get; set; }  // Exposed in responses!
    public string CreditCardNumber { get; set; }  // Security issue!
    public List<OrderDto> Orders { get; set; }  // Over-fetching
    public List<AddressDto> Addresses { get; set; }
    // ... 50 more fields
}

✅ Purpose-specific DTOs:
public class CustomerRegistrationRequest { /* just registration fields */ }
public class CustomerInfo { /* safe to return */ }
public class CustomerSummary { /* for lists */ }
public class CustomerDetails { /* for detail view */ }
```

### Anti-Pattern 3: DTOs with Infrastructure Dependencies

```csharp
❌ DTO depends on infrastructure:
public class OrderDto
{
    public int Id { get; set; }
    
    [JsonIgnore]
    public DbContext Context { get; set; }  // Infrastructure dependency!
    
    public IQueryable<OrderLineDto> Lines =>  // Lazy loading!
        Context.OrderLines.Where(l => l.OrderId == Id);
}
```

---

## DTO Checklist

- [ ] DTO is a simple data holder (no business logic)
- [ ] DTO is serializable (no streams, connections, functions)
- [ ] DTO hierarchy is flat (2 levels max)
- [ ] DTO is separate from domain model
- [ ] DTO has appropriate suffix (Request, Info, Result, Criteria)
- [ ] Request DTOs contain only input data
- [ ] Response DTOs don't expose sensitive data
- [ ] Result DTOs include success/failure and error details
- [ ] DTOs are designed for their specific use case (not one-size-fits-all)
- [ ] Collections use IEnumerable or IReadOnlyCollection (not List)
- [ ] Immutable where appropriate (especially responses)
- [ ] No infrastructure dependencies in DTOs
