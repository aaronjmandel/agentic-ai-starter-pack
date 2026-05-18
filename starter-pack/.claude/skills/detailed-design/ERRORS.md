# Error Handling in Contracts

Patterns for handling and communicating errors in service contracts.

---

## Two Approaches to Error Handling

### 1. Result Objects (Preferred for Business Errors)

**When to use**:
- Expected business failures (payment declined, validation errors)
- Client needs to handle different outcomes
- Multiple failure modes exist

**Benefits**:
- Explicit success/failure
- Type-safe error codes
- Client forced to handle result
- No exception overhead
- Clear API contract

### 2. Exceptions (For Unexpected Errors Only)

**When to use**:
- Truly exceptional conditions (database down, network failure)
- Programming errors (null argument, invalid state)
- Infrastructure failures
- Conditions that cannot be recovered from

---

## Result Object Patterns

### Basic Result Object

```csharp
public class OperationResult
{
    public bool IsSuccessful { get; set; }
    public string ErrorMessage { get; set; }
    public string ErrorCode { get; set; }
    
    public static OperationResult Success() 
        => new() { IsSuccessful = true };
    
    public static OperationResult Failure(string code, string message)
        => new() { IsSuccessful = false, ErrorCode = code, ErrorMessage = message };
}
```

### Generic Result Object

```csharp
public class Result<T>
{
    public bool IsSuccessful { get; private set; }
    public T Value { get; private set; }
    public string ErrorMessage { get; private set; }
    public string ErrorCode { get; private set; }
    
    public static Result<T> Success(T value)
        => new() { IsSuccessful = true, Value = value };
    
    public static Result<T> Failure(string code, string message)
        => new() { IsSuccessful = false, ErrorCode = code, ErrorMessage = message };
}

// Usage
public Result<Order> GetOrder(int orderId)
{
    var order = _repository.Find(orderId);
    if (order == null)
        return Result<Order>.Failure("NOT_FOUND", $"Order {orderId} not found");
    
    return Result<Order>.Success(order);
}
```

### Domain-Specific Result Object

```csharp
public class OrderResult
{
    public bool IsSuccessful { get; set; }
    public int OrderId { get; set; }
    public OrderResultCode ResultCode { get; set; }
    public string ErrorMessage { get; set; }
    public ValidationErrors ValidationErrors { get; set; }
    
    // Factory methods for common outcomes
    public static OrderResult Placed(int orderId)
        => new() { IsSuccessful = true, OrderId = orderId, ResultCode = OrderResultCode.Success };
    
    public static OrderResult InsufficientInventory(string productName)
        => new() 
        { 
            IsSuccessful = false, 
            ResultCode = OrderResultCode.InsufficientInventory,
            ErrorMessage = $"Insufficient inventory for {productName}"
        };
    
    public static OrderResult PaymentDeclined(string reason)
        => new()
        {
            IsSuccessful = false,
            ResultCode = OrderResultCode.PaymentDeclined,
            ErrorMessage = reason
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

### Validation Result

```csharp
public class ValidationResult
{
    public bool IsValid => !Errors.Any();
    public Dictionary<string, List<string>> Errors { get; } = new();
    
    public void AddError(string field, string message)
    {
        if (!Errors.ContainsKey(field))
            Errors[field] = new List<string>();
        Errors[field].Add(message);
    }
    
    public static ValidationResult Success() => new();
    
    public static ValidationResult WithError(string field, string message)
    {
        var result = new ValidationResult();
        result.AddError(field, message);
        return result;
    }
}

// Usage in contract
public class OrderResult
{
    public bool IsSuccessful { get; set; }
    public ValidationResult Validation { get; set; }
}

// Client handling
if (!result.IsSuccessful && result.Validation != null)
{
    foreach (var (field, errors) in result.Validation.Errors)
    {
        foreach (var error in errors)
        {
            Console.WriteLine($"{field}: {error}");
        }
    }
}
```

---

## Error Code Design

### Use Enums for Type Safety

```csharp
public enum PaymentResultCode
{
    // Success
    Approved,
    
    // Card Issues
    CardDeclined,
    CardExpired,
    InvalidCardNumber,
    InvalidCvv,
    
    // Account Issues
    InsufficientFunds,
    AccountClosed,
    AccountFrozen,
    
    // Security
    SecurityCheckFailed,
    FraudDetected,
    
    // Technical
    NetworkError,
    ProcessorUnavailable,
    Timeout
}
```

### Error Code Naming Conventions

```csharp
// Use consistent prefixes for categories
public static class ErrorCodes
{
    // Validation errors
    public const string VALIDATION_REQUIRED = "VALIDATION_REQUIRED";
    public const string VALIDATION_FORMAT = "VALIDATION_FORMAT";
    public const string VALIDATION_RANGE = "VALIDATION_RANGE";
    
    // Not found errors
    public const string NOT_FOUND_ORDER = "NOT_FOUND_ORDER";
    public const string NOT_FOUND_CUSTOMER = "NOT_FOUND_CUSTOMER";
    public const string NOT_FOUND_PRODUCT = "NOT_FOUND_PRODUCT";
    
    // Business rule violations
    public const string BUSINESS_INSUFFICIENT_INVENTORY = "BUSINESS_INSUFFICIENT_INVENTORY";
    public const string BUSINESS_PAYMENT_DECLINED = "BUSINESS_PAYMENT_DECLINED";
    public const string BUSINESS_ORDER_ALREADY_SHIPPED = "BUSINESS_ORDER_ALREADY_SHIPPED";
    
    // Authorization errors
    public const string AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED";
    public const string AUTH_FORBIDDEN = "AUTH_FORBIDDEN";
}
```

---

## Client-Side Error Handling

### Pattern: Switch on Result Code

```csharp
var result = orderService.PlaceOrder(request);

if (result.IsSuccessful)
{
    Console.WriteLine($"Order placed: {result.OrderId}");
    return RedirectToConfirmation(result.OrderId);
}

switch (result.ResultCode)
{
    case OrderResultCode.InsufficientInventory:
        ShowError("Some items are out of stock. Please update your cart.");
        return RedirectToCart();
    
    case OrderResultCode.PaymentDeclined:
        ShowError($"Payment was declined: {result.ErrorMessage}");
        return RedirectToPayment();
    
    case OrderResultCode.InvalidAddress:
        ShowError("Please verify your shipping address.");
        return RedirectToShipping();
    
    case OrderResultCode.ValidationFailed:
        ShowValidationErrors(result.ValidationErrors);
        return View(model);
    
    default:
        ShowError("An unexpected error occurred. Please try again.");
        return RedirectToCart();
}
```

### Pattern: Fluent Result Handling

```csharp
public static class ResultExtensions
{
    public static TResult Match<T, TResult>(
        this Result<T> result,
        Func<T, TResult> onSuccess,
        Func<string, TResult> onFailure)
    {
        return result.IsSuccessful 
            ? onSuccess(result.Value) 
            : onFailure(result.ErrorMessage);
    }
}

// Usage
var response = orderService.PlaceOrder(request)
    .Match(
        onSuccess: orderId => Ok(new { OrderId = orderId }),
        onFailure: error => BadRequest(new { Error = error })
    );
```

---

## Exception Guidelines

### When to Throw Exceptions

```csharp
public class OrderService
{
    public OrderResult PlaceOrder(OrderRequest request)
    {
        // ✅ Throw for programming errors (precondition violations)
        if (request == null)
            throw new ArgumentNullException(nameof(request));
        
        // ✅ Throw for invalid state (logic errors)
        if (_disposed)
            throw new ObjectDisposedException(nameof(OrderService));
        
        // ❌ Don't throw for business failures - return Result
        if (!ValidateCustomer(request.CustomerId))
            return OrderResult.CustomerNotFound();
        
        // ❌ Don't throw for validation - return Result
        var validation = Validate(request);
        if (!validation.IsValid)
            return OrderResult.ValidationFailed(validation);
        
        try
        {
            // Process order...
            return OrderResult.Success(orderId);
        }
        catch (SqlException ex)
        {
            // ✅ Log and wrap infrastructure exceptions
            _logger.LogError(ex, "Database error placing order");
            throw new OrderServiceException("Failed to place order", ex);
        }
    }
}
```

### Custom Exception Hierarchy

```csharp
// Base exception for the service
public class OrderServiceException : Exception
{
    public OrderServiceException(string message) : base(message) { }
    public OrderServiceException(string message, Exception inner) : base(message, inner) { }
}

// Specific exceptions (use sparingly)
public class OrderNotFoundException : OrderServiceException
{
    public int OrderId { get; }
    
    public OrderNotFoundException(int orderId) 
        : base($"Order {orderId} not found")
    {
        OrderId = orderId;
    }
}
```

### Document Exception Behavior

```csharp
/// <summary>
/// Retrieves an order by ID.
/// </summary>
/// <param name="orderId">The order identifier.</param>
/// <returns>The order details.</returns>
/// <exception cref="ArgumentException">Thrown when orderId is less than 1.</exception>
/// <exception cref="OrderNotFoundException">Thrown when order does not exist.</exception>
/// <exception cref="OrderServiceException">Thrown for infrastructure failures.</exception>
Order GetOrder(int orderId);
```

---

## HTTP/REST Error Mapping

### Result to HTTP Status Code

```csharp
public static class ResultExtensions
{
    public static IActionResult ToActionResult<T>(this Result<T> result)
    {
        if (result.IsSuccessful)
            return new OkObjectResult(result.Value);
        
        return result.ErrorCode switch
        {
            "NOT_FOUND" => new NotFoundObjectResult(result.ErrorMessage),
            "VALIDATION" => new BadRequestObjectResult(result.ErrorMessage),
            "UNAUTHORIZED" => new UnauthorizedResult(),
            "FORBIDDEN" => new ForbidResult(),
            "CONFLICT" => new ConflictObjectResult(result.ErrorMessage),
            _ => new ObjectResult(result.ErrorMessage) { StatusCode = 500 }
        };
    }
}

// Usage in controller
[HttpGet("{id}")]
public IActionResult GetOrder(int id)
{
    var result = _orderService.GetOrder(id);
    return result.ToActionResult();
}
```

### Standard Error Response Format

```csharp
public class ApiErrorResponse
{
    public string Code { get; set; }
    public string Message { get; set; }
    public string Target { get; set; }
    public List<ApiErrorDetail> Details { get; set; }
    public string TraceId { get; set; }
}

public class ApiErrorDetail
{
    public string Code { get; set; }
    public string Message { get; set; }
    public string Target { get; set; }  // e.g., "email", "shipping.zipCode"
}

// Example response
{
    "code": "VALIDATION_ERROR",
    "message": "One or more validation errors occurred.",
    "traceId": "abc123",
    "details": [
        {
            "code": "REQUIRED",
            "message": "Email is required.",
            "target": "email"
        },
        {
            "code": "INVALID_FORMAT",
            "message": "Invalid zip code format.",
            "target": "shipping.zipCode"
        }
    ]
}
```

---

## Error Handling Anti-Patterns

### Anti-Pattern 1: Using Exceptions for Flow Control

```csharp
❌ Bad:
public Order GetOrder(int orderId)
{
    var order = _repository.Find(orderId);
    if (order == null)
        throw new OrderNotFoundException(orderId);  // Expected case!
    return order;
}

// Client code
try
{
    var order = service.GetOrder(id);
    // process order
}
catch (OrderNotFoundException)
{
    // Handle not found - common case
}

✅ Good:
public Result<Order> GetOrder(int orderId)
{
    var order = _repository.Find(orderId);
    if (order == null)
        return Result<Order>.Failure("NOT_FOUND", $"Order {orderId} not found");
    return Result<Order>.Success(order);
}

// Client code
var result = service.GetOrder(id);
if (result.IsSuccessful)
{
    // process result.Value
}
else
{
    // Handle not found
}
```

### Anti-Pattern 2: Catching and Ignoring

```csharp
❌ Bad:
public void ProcessOrder(OrderRequest request)
{
    try
    {
        // process
    }
    catch (Exception)
    {
        // Silently ignore - dangerous!
    }
}

✅ Good:
public OrderResult ProcessOrder(OrderRequest request)
{
    try
    {
        // process
        return OrderResult.Success(orderId);
    }
    catch (SqlException ex)
    {
        _logger.LogError(ex, "Database error");
        return OrderResult.Failure("DATABASE_ERROR", "Failed to process order");
    }
}
```

### Anti-Pattern 3: Generic Error Messages

```csharp
❌ Bad:
return Result.Failure("ERROR", "An error occurred");

✅ Good:
return Result.Failure("PAYMENT_DECLINED", "Payment was declined: insufficient funds");
return Result.Failure("INVENTORY_INSUFFICIENT", "Product 'Widget' has only 5 units available");
```

---

## Error Handling Checklist

- [ ] Expected business failures use Result objects (not exceptions)
- [ ] Result objects include specific error codes
- [ ] Error codes are enums or constants (not magic strings)
- [ ] Error messages are descriptive and actionable
- [ ] Validation errors include field-level details
- [ ] Exceptions reserved for truly exceptional conditions
- [ ] Exceptions are documented in contract
- [ ] Infrastructure exceptions are logged and wrapped
- [ ] Client can determine error type programmatically
- [ ] Error responses follow consistent format
- [ ] Sensitive information not exposed in error messages
