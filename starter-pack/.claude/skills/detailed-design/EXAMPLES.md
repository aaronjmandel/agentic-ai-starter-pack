# Detailed Design Examples

Complete worked examples showing contract design in practice.

---

## Example 1: Payment Processing Service

### Bad Design (Anti-Patterns)

```csharp
❌ BAD: Too many parameters, primitive obsession, generic names
public interface IPaymentManager
{
    bool Process(int orderId, string cardNumber, string cvv, string expiry, 
                 decimal amount, string currency, int customerId);
    DataTable GetHistory(int customerId);
    void Update(int paymentId, int statusCode);
}
```

### Good Design

```csharp
✅ GOOD: Segregated interfaces, clear names, proper DTOs

public interface IPaymentProcessor
{
    PaymentResult ProcessPayment(PaymentRequest request);
    RefundResult ProcessRefund(RefundRequest request);
}

public interface IPaymentQueryService
{
    PaymentInfo GetPayment(int paymentId);
    IEnumerable<PaymentInfo> GetPaymentHistory(int customerId);
}

// Request DTO
public class PaymentRequest
{
    public int OrderId { get; set; }
    public int CustomerId { get; set; }
    public Money Amount { get; set; }
    public PaymentMethod Method { get; set; }
}

public record Money(decimal Amount, Currency Currency);

// Result DTO
public class PaymentResult
{
    public bool IsSuccessful { get; set; }
    public int PaymentId { get; set; }
    public string TransactionReference { get; set; }
    public PaymentResultCode ResultCode { get; set; }
    public string ErrorMessage { get; set; }
}

public enum PaymentResultCode
{
    Approved,
    Declined,
    InsufficientFunds,
    ExpiredCard,
    InvalidCard,
    SecurityCheckFailed
}
```

---

## Example 2: Inventory Management Service

```csharp
public interface IInventoryService
{
    AvailabilityResult CheckAvailability(int productId, int requestedQuantity);
    ReservationResult ReserveInventory(ReservationRequest request);
    void ReleaseReservation(string reservationId);
    void CommitReservation(string reservationId);
}

public interface IInventoryQueryService
{
    InventoryLevel GetInventoryLevel(int productId);
    IEnumerable<InventoryLevel> GetLowStockItems(int threshold);
}

public class AvailabilityResult
{
    public bool IsAvailable { get; set; }
    public int ProductId { get; set; }
    public int AvailableQuantity { get; set; }
    public int RequestedQuantity { get; set; }
    public DateTime? NextRestockDate { get; set; }
}

public class ReservationRequest
{
    public int ProductId { get; set; }
    public int Quantity { get; set; }
    public int OrderId { get; set; }
    public TimeSpan? ExpirationPeriod { get; set; }
}

public class ReservationResult
{
    public bool IsSuccessful { get; set; }
    public string ReservationId { get; set; }
    public DateTime ExpiresAt { get; set; }
    public ReservationResultCode ResultCode { get; set; }
}

public enum ReservationResultCode
{
    Success,
    InsufficientInventory,
    ProductNotFound,
    ProductDiscontinued
}
```

---

## Example 3: Customer Management Service

```csharp
public interface ICustomerCommandService
{
    RegistrationResult RegisterCustomer(CustomerRegistrationRequest request);
    void UpdateProfile(int customerId, ProfileUpdateRequest update);
    void DeactivateCustomer(int customerId, string reason);
}

public interface ICustomerQueryService
{
    CustomerInfo GetCustomer(int customerId);
    IEnumerable<CustomerSummary> SearchCustomers(CustomerSearchCriteria criteria);
    bool IsEmailAvailable(string email);
}

public class CustomerRegistrationRequest
{
    public string Email { get; set; }
    public string Password { get; set; }
    public PersonalInfo PersonalInfo { get; set; }
    public Address Address { get; set; }
}

public class RegistrationResult
{
    public bool IsSuccessful { get; set; }
    public int CustomerId { get; set; }
    public RegistrationResultCode ResultCode { get; set; }
    public ValidationResult Validation { get; set; }
}

public enum RegistrationResultCode
{
    Success,
    EmailAlreadyExists,
    WeakPassword,
    ValidationFailed
}

// Response DTO (safe to return)
public class CustomerInfo
{
    public int CustomerId { get; set; }
    public string Email { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public Address Address { get; set; }
    public DateTime RegisteredDate { get; set; }
}

// Lightweight projection for lists
public class CustomerSummary
{
    public int CustomerId { get; set; }
    public string FullName { get; set; }
    public string Email { get; set; }
}
```

---

## Example 4: Search with Pagination

```csharp
public interface IProductSearchService
{
    PagedResult<ProductSearchResult> SearchProducts(ProductSearchRequest request);
}

public class ProductSearchRequest
{
    // Search criteria
    public string Query { get; set; }
    public int? CategoryId { get; set; }
    public decimal? MinPrice { get; set; }
    public decimal? MaxPrice { get; set; }
    public bool? InStockOnly { get; set; }
    
    // Paging
    public PagingOptions Paging { get; set; } = new();
    
    // Sorting
    public ProductSortBy SortBy { get; set; } = ProductSortBy.Relevance;
}

public class PagingOptions
{
    public int PageNumber { get; set; } = 1;
    public int PageSize { get; set; } = 20;
}

public class PagedResult<T>
{
    public IEnumerable<T> Items { get; set; }
    public int TotalCount { get; set; }
    public int PageNumber { get; set; }
    public int PageSize { get; set; }
    
    public int TotalPages => (int)Math.Ceiling(TotalCount / (double)PageSize);
    public bool HasNextPage => PageNumber < TotalPages;
    public bool HasPreviousPage => PageNumber > 1;
}

public class ProductSearchResult
{
    public int ProductId { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public string ImageUrl { get; set; }
    public decimal? AverageRating { get; set; }
    public bool InStock { get; set; }
}
```

---

## Example 5: Order Service (Complete)

### Interfaces

```csharp
// Commands
public interface IOrderCommandService
{
    OrderResult PlaceOrder(OrderRequest request);
    void ConfirmOrder(int orderId);
    void CancelOrder(int orderId, string reason);
    void ShipOrder(int orderId, ShipmentInfo shipment);
}

// Queries
public interface IOrderQueryService
{
    Order GetOrder(int orderId);
    IEnumerable<OrderSummary> GetCustomerOrders(int customerId);
    PagedResult<OrderSummary> SearchOrders(OrderSearchCriteria criteria);
}
```

### Request/Response DTOs

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

public class ShippingAddress
{
    public string Street { get; set; }
    public string City { get; set; }
    public string State { get; set; }
    public string Country { get; set; }
    public string ZipCode { get; set; }
}

public class OrderResult
{
    public bool IsSuccessful { get; set; }
    public int OrderId { get; set; }
    public OrderResultCode ResultCode { get; set; }
    public string ErrorMessage { get; set; }
    public ValidationResult Validation { get; set; }
    
    public static OrderResult Success(int orderId)
        => new() { IsSuccessful = true, OrderId = orderId, ResultCode = OrderResultCode.Success };
    
    public static OrderResult InsufficientInventory(string productName)
        => new() 
        { 
            IsSuccessful = false, 
            ResultCode = OrderResultCode.InsufficientInventory,
            ErrorMessage = $"Insufficient inventory for {productName}"
        };
}

public enum OrderResultCode
{
    Success,
    InsufficientInventory,
    PaymentDeclined,
    InvalidAddress,
    InvalidPromoCode,
    CustomerNotFound,
    ValidationFailed
}
```

### Query DTOs

```csharp
public class Order
{
    public int OrderId { get; set; }
    public DateTime OrderDate { get; set; }
    public OrderStatus Status { get; set; }
    public CustomerSummary Customer { get; set; }
    public ShippingAddress ShippingAddress { get; set; }
    public IEnumerable<OrderLineInfo> Lines { get; set; }
    public decimal Subtotal { get; set; }
    public decimal Tax { get; set; }
    public decimal ShippingCost { get; set; }
    public decimal Total { get; set; }
}

public class OrderSummary
{
    public int OrderId { get; set; }
    public DateTime OrderDate { get; set; }
    public OrderStatus Status { get; set; }
    public int ItemCount { get; set; }
    public decimal Total { get; set; }
}

public class OrderLineInfo
{
    public int LineId { get; set; }
    public int ProductId { get; set; }
    public string ProductName { get; set; }
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal LineTotal { get; set; }
}

public enum OrderStatus
{
    Pending,
    Confirmed,
    Processing,
    Shipped,
    Delivered,
    Cancelled,
    Returned
}
```

---

## Design Pattern Summary

### Checklist for Each Service

1. **Segregate interfaces** by role:
   - Commands (state-changing)
   - Queries (read-only)
   - Admin (maintenance)
   - Reporting (analytics)

2. **Design Request DTOs**:
   - Group related parameters
   - Use nested objects for structure
   - Keep flat (2 levels max)

3. **Design Response DTOs**:
   - Return only what clients need
   - Use projections (Summary, Details)
   - Include computed properties

4. **Design Result objects**:
   - Include IsSuccessful flag
   - Include specific ResultCode enum
   - Include ErrorMessage for context
   - Include ValidationResult for field-level errors

5. **Design for pagination**:
   - Use PagedResult<T> wrapper
   - Include TotalCount, HasNextPage, HasPreviousPage
   - Accept PagingOptions in request

6. **Apply naming conventions**:
   - Commands: Verb + Noun (PlaceOrder, CancelOrder)
   - Queries: Get + Noun (GetOrder, GetCustomerOrders)
   - Requests: [Entity]Request (OrderRequest)
   - Results: [Entity]Result (OrderResult)
   - Summaries: [Entity]Summary (OrderSummary)
