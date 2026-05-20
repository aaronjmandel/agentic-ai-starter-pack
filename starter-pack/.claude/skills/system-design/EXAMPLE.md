# System Design Example: Online Banking

A complete worked example demonstrating The Method's system design process.

## Business Requirements

Design a system for a bank that allows customers to:
1. View account balances and transaction history
2. Transfer money between accounts
3. Pay bills to external payees
4. Set up recurring payments
5. Receive alerts for account activities
6. Manage personal information

**Constraints**:
- Must integrate with existing core banking system (mainframe)
- Must be highly secure
- Must be available 24/7
- Must handle millions of transactions daily
- Must comply with banking regulations

---

## Step 1: Functional Decomposition

### Initial Brain Dump (Too Many Items)
- Account viewing, balance inquiry, transaction history
- Money transfers, bill payments, payment scheduling, recurring payments
- User authentication, profile management
- Alert notifications, security, audit logging
- External system integration, reporting

**Problem**: 15+ items, not organized

### Applying 3-9 Rule

**Final Top-Level Components (6)**:

1. **Account Management**
   - Purpose: Handle all account-related inquiries
   - Responsibilities: Account details, balances, transaction history, statements

2. **Payment Processing**
   - Purpose: Execute and manage all types of payments
   - Responsibilities: Transfers, bill payments, recurring payments, scheduling

3. **Customer Management**
   - Purpose: Manage customer information and profiles
   - Responsibilities: Personal info, authentication, preferences, contacts

4. **Notification Service**
   - Purpose: Deliver alerts and messages
   - Responsibilities: Email/SMS/push notifications, alert preferences

5. **Core Banking Integration**
   - Purpose: Interface with existing core banking system
   - Responsibilities: Transaction execution, account data retrieval

6. **Reporting & Analytics**
   - Purpose: Generate reports and business intelligence
   - Responsibilities: Customer reports, regulatory reports, dashboards

**Count**: 6 components ✓

**Note**: Security and audit are cross-cutting concerns, handled via infrastructure.

---

## Step 2: SOLID Validation

### Account Management
- **SRP** ✓: Single responsibility - account information
- **OCP** ✓: New account types addable without modification
- **ISP** ✓: Separate `IAccountReader`, `IAccountHistory` interfaces
- **DIP** ✓: Depends on `ICoreAccountProvider` interface

### Payment Processing
- **SRP** ✓: Single responsibility - payment execution
- **OCP** ✓: Strategy pattern for payment types
- **ISP** ✓: Separate `IPaymentProcessor`, `IPaymentScheduler`, `IPaymentHistory`
- **DIP** ✓: Depends on interfaces, not concrete implementations

### Customer Management
- **SRP** ✓: Single responsibility - customer information
- **OCP** ✓: New authentication methods addable
- **ISP** ✓: Separate `ICustomerReader`, `ICustomerWriter`, `IAuthenticationService`

### Notification Service
- **SRP** ✓: Single responsibility - notifications
- **OCP** ✓: New channels addable via `INotificationChannel`
- **DIP** ✓: Depends on channel abstractions

### Core Banking Integration
- **SRP** ✓: Single responsibility - legacy system integration
- **ISP** ✓: Separate `ICoreAccountService`, `ICoreTransactionService`

### Reporting & Analytics
- **SRP** ✓: Single responsibility - reports and analytics
- **OCP** ✓: Template pattern for report generation

---

## Step 3: Component Interactions

### Dependency Graph
```
AccountManagement → CoreBankingIntegration
PaymentProcessing → CoreBankingIntegration
PaymentProcessing → AccountManagement (for validation)
PaymentProcessing → NotificationService
CustomerManagement → (standalone)
NotificationService → (standalone)
ReportingAnalytics → AccountManagement (read-only)
ReportingAnalytics → PaymentProcessing (read-only)
```

### Validation
- ✓ No circular dependencies
- ✓ Clear direction of dependencies
- ✓ CoreBankingIntegration is a leaf
- ✓ NotificationService is independent
- ⚠️ PaymentProcessing has 3 dependencies - monitor for SRP violation

---

## Step 4: Layered Structure

### Client Layer
- `AccountViewController`
- `PaymentController`
- `CustomerProfileView`
- `NotificationViewController`
- `ReportViewController`

### Business Layer
All 6 main components:
- `AccountService`, `TransactionHistoryService`
- `PaymentProcessor`, `PaymentScheduler`, `RecurringPaymentService`
- `CustomerService`, `AuthenticationService`
- `NotificationManager`, `AlertService`
- `CoreBankingAdapter`, `TransactionAdapter`
- `ReportGenerator`, `AnalyticsEngine`

### Resource Access Layer
- `AccountRepository`
- `CustomerRepository`
- `PaymentRepository`
- `MainframeBridgeClient`
- `EmailServiceClient`, `SmsServiceClient`
- `CacheRepository`

### Resources
- SQL Server database
- Legacy core banking system (mainframe)
- Email service (SMTP)
- SMS gateway
- Redis cache

---

## Step 5: Interface Definitions

### Business Layer Defines
```csharp
// Account data access
public interface IAccountRepository
{
    Account GetById(string accountId);
    IEnumerable<Account> GetByCustomerId(string customerId);
}

// Core banking integration
public interface ICoreTransactionService
{
    TransactionResult ExecuteTransfer(string from, string to, decimal amount);
    TransactionResult ExecutePayment(PaymentDetails payment);
}

// Notification channels
public interface IEmailChannel
{
    void Send(string recipient, string subject, string body);
}

// Component interactions
public interface IAccountService
{
    Account GetAccount(string accountId);
    bool ValidateAccountExists(string accountId);
}

public interface IPaymentProcessor
{
    PaymentResult ProcessTransfer(TransferRequest request);
    PaymentResult ProcessBillPayment(BillPaymentRequest request);
}
```

### Resource Access Layer Implements
```csharp
public class SqlAccountRepository : IAccountRepository { }
public class MainframeTransactionService : ICoreTransactionService { }
public class SmtpEmailService : IEmailChannel { }
```

---

## Step 6: Composition

### Composition Root
```csharp
public void ConfigureServices(IServiceCollection services)
{
    // Resource Access Layer
    services.AddScoped<IAccountRepository, SqlAccountRepository>();
    services.AddScoped<ICustomerRepository, SqlCustomerRepository>();
    services.AddScoped<IPaymentRepository, SqlPaymentRepository>();
    
    // Core banking integration
    services.AddSingleton<IMainframeClient, MainframeClient>();
    services.AddScoped<ICoreTransactionService, MainframeTransactionService>();
    
    // Notification channels
    services.AddSingleton<IEmailChannel, SmtpEmailService>();
    services.AddSingleton<ISmsChannel, TwilioSmsService>();
    
    // Business Layer
    services.AddScoped<IAccountService, AccountService>();
    services.AddScoped<IPaymentProcessor, PaymentProcessor>();
    services.AddScoped<ICustomerService, CustomerService>();
    services.AddScoped<INotificationService, NotificationService>();
    
    // Client Layer
    services.AddControllersWithViews();
}
```

### Component Implementation
```csharp
public class PaymentProcessor : IPaymentProcessor
{
    private readonly ICoreTransactionService _transactionService;
    private readonly IAccountService _accountService;
    private readonly INotificationService _notificationService;
    private readonly IPaymentRepository _paymentRepository;
    
    public PaymentProcessor(
        ICoreTransactionService transactionService,
        IAccountService accountService,
        INotificationService notificationService,
        IPaymentRepository paymentRepository)
    {
        _transactionService = transactionService ?? throw new ArgumentNullException();
        _accountService = accountService ?? throw new ArgumentNullException();
        _notificationService = notificationService ?? throw new ArgumentNullException();
        _paymentRepository = paymentRepository ?? throw new ArgumentNullException();
    }
    
    public PaymentResult ProcessTransfer(TransferRequest request)
    {
        // Validate accounts
        if (!_accountService.ValidateAccountExists(request.FromAccount) ||
            !_accountService.ValidateAccountExists(request.ToAccount))
            return PaymentResult.InvalidAccount;
        
        // Execute transfer
        var result = _transactionService.ExecuteTransfer(
            request.FromAccount, request.ToAccount, request.Amount);
        
        if (result.IsSuccessful)
        {
            _paymentRepository.Save(new Payment { /* ... */ });
            _notificationService.SendTransactionAlert(request.CustomerId, result.Transaction);
            return PaymentResult.Success;
        }
        
        return PaymentResult.Failed;
    }
}
```

---

## Step 7: Validation

### Scenario: Customer Transfers $500

1. Customer submits form → `PaymentController` (Client) ✓
2. Controller delegates → `IPaymentProcessor.ProcessTransfer()` ✓
3. Processor validates → `IAccountService.ValidateAccountExists()` ✓
4. Processor executes → `ICoreTransactionService.ExecuteTransfer()` ✓
5. Processor saves → `IPaymentRepository.Save()` ✓
6. Processor notifies → `INotificationService.SendTransactionAlert()` ✓
7. Controller displays → Returns view ✓

**Result**: ✓ Clean flow, proper layer boundaries

### Change Impact Analysis

| Change | Impact | Effort |
|--------|--------|--------|
| New payment type (crypto) | Only PaymentProcessor | Low ✓ |
| Switch mainframe to cloud | Only MainframeTransactionService | Low ✓ |
| Add mobile app | New Client Layer only | Low ✓ |
| New approval workflow | PaymentProcessor + new component | Medium ✓ |

---

## Key Design Decisions

### Decision 1: Core Banking as Business Component
**Question**: Should this be just in Resource Access Layer?
**Decision**: Business Layer component
**Rationale**: Significant business logic in adapting to mainframe, error handling is business concern

### Decision 2: Notification as Separate Component
**Question**: Should notifications be part of each component?
**Decision**: Separate NotificationService
**Rationale**: Multiple components need it, complex logic (routing, preferences, templates)

### Decision 3: Payment Processing Orchestrator
**Question**: Should transfers and bill payments be separate?
**Decision**: Single component
**Rationale**: Share common validation and workflow logic

---

## Testing Strategy

### Business Layer (Most Important)
```csharp
[Test]
public void ProcessTransfer_ValidAccounts_Success()
{
    // Arrange
    var mockTransaction = new Mock<ICoreTransactionService>();
    var mockAccount = new Mock<IAccountService>();
    var mockNotification = new Mock<INotificationService>();
    var mockRepository = new Mock<IPaymentRepository>();
    
    mockAccount.Setup(s => s.ValidateAccountExists(It.IsAny<string>())).Returns(true);
    mockTransaction.Setup(s => s.ExecuteTransfer(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<decimal>()))
        .Returns(new TransactionResult { IsSuccessful = true });
    
    var processor = new PaymentProcessor(
        mockTransaction.Object, mockAccount.Object,
        mockNotification.Object, mockRepository.Object);
    
    // Act
    var result = processor.ProcessTransfer(new TransferRequest { /* ... */ });
    
    // Assert
    Assert.AreEqual(PaymentResult.Success, result);
    mockRepository.Verify(r => r.Save(It.IsAny<Payment>()), Times.Once);
}
```

---

## Summary

### What Made This Design Successful
1. ✓ Systematic approach (followed The Method)
2. ✓ Right granularity (6 components)
3. ✓ Clear boundaries (SRP per component)
4. ✓ Proper layering (four layers)
5. ✓ Dependency inversion (interfaces defined by Business)
6. ✓ Testability (all business logic mockable)
7. ✓ Flexibility (changes well-isolated)

### What Was Avoided
- ✗ Smart UI
- ✗ Anemic Domain Model
- ✗ Business logic in database
- ✗ Layer violations
- ✗ God components
- ✗ Circular dependencies

### Time Spent
- Decomposition: 1 day
- Structure: 1 day
- Composition: 0.5 day
- Validation: 0.5 day
- **Total**: ~3 days ✓
