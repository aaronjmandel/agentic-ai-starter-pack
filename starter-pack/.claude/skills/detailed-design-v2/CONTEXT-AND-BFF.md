# Context, BFF, and Boundary Patterns

Backend for Frontend (BFF) patterns, controller implementation strategies, out-of-band context via headers, gateway security, and API design.

---

## Gateway and Security Boundary

The gateway and WebAPI must be separate concerns.

### Gateway (No Code)

The gateway performs **authentication**—it is the security boundary. It:
- Negotiates the token with the identity provider
- Validates credentials
- Sets up **claims** (roles, permissions)
- Conveys the token to the backend
- Extracts the data contract from the token

The gateway contains no business code. In Azure, this is API Management (APIM).

### Important: Authentication Can Differ by Context

Different client types may use different authentication mechanisms:
- **Online** context: OAuth2 / OIDC tokens
- **Restaurant** context: API keys or certificate-based auth
- **Internal** context: Windows authentication / Kerberos

Claims, roles, and permissions are different between contexts. The gateway handles this variance.

---

## Out-of-Band Context

Context (origination, security, workflow state) flows **out of band**—in message headers, not in method signatures.

### Why Headers, Not Parameters?

```csharp
❌ BAD: Context pollutes method signatures
public interface ISalesManager
{
    Task<FindResponse> SearchAsync(
        FindCriteria criteria,
        string authToken,        // System concern in signature
        string originContext,    // System concern in signature
        string correlationId);   // System concern in signature
}

✅ GOOD: Context flows via headers — transparent to the contract
public interface ISalesManager
{
    Task<FindResponse> SearchAsync(FindCriteria criteria);
}

// Inside the service, context is accessed from base class
public class SalesManager : ServiceBase
{
    async Task<FindResponse> SearchAsync(FindCriteria criteria)
    {
        OriginationContext origination = Origination;  // From headers
        MyContext context = MyContext;                   // From headers
        // ...
    }
}
```

**Headers are transparent**—not encrypted and available to every service in the chain to interrogate. The controller in WebAPI packages headers from the incoming HTTP request into the internal messaging format and calls the manager.

### Context Types

| Context | Purpose | Scope |
|---------|---------|-------|
| **OriginationContext** | Identifies the requesting system/client type | Per request |
| **SecurityContext** | Claims, roles, authorization data | Per request |
| **SessionContext** | Session state for stateful interactions | Per session |
| **TraceContext** | Correlation IDs, distributed tracing | Per request |
| **RunContext** | Workflow execution state | Per workflow |
| **EnvironmentContext** | Deployment environment information | Per service instance |

### Security Context at the Manager

Security context is most relevant at the Manager level, where authorization decisions are made. The gateway has already authenticated; the manager authorizes based on claims.

---

## BFF (Backend for Frontend) Pattern

BFF provides a boundary tailored to a specific client type. Each BFF serves only the use cases relevant to its context.

### BFF by Client Type

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Patient Website  │  │ Patient Mobile  │  │ Patient Chat    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
    ┌────▼────┐          ┌───▼────┐           ┌───▼────┐
    │ Web BFF │          │Mob BFF │           │Chat BFF│
    └────┬────┘          └───┬────┘           └───┬────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │    Gateway      │  ← Authentication
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Internal WebAPI │  ← Authorization, routing
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Manager      │  ← Business logic
                    └─────────────────┘
```

### Value of BFF

- **Express API in context terms**: Operations may be subtly different from patient context vs doctor context perspective
- **Independent evolution**: Public API evolves at different speed from internal API
- **Different nomenclature**: Internal API may use domain-specific terms; public API uses consumer-friendly names
- **Additional endpoints**: Public API may need wrapper endpoints, convenience methods
- **Context-specific security**: Different client types need different auth flows

### BFF Only Serves the Client

BFF is **not** about backend rendering. It serves the website, mobile app, or chat—it packages and routes requests. It does not contain business logic.

### Separate Public and Private API

You need separate Public API and Private API because:
- **Speed of evolution**: Private API evolves faster than Public API
- **Nomenclature**: Internal names differ from external consumer names
- **Endpoints**: Public API may need additional endpoints not in private API
- **Stability guarantees**: Public API has stricter backward-compatibility requirements

```csharp
// For public consumers — auto-generated TypeScript SDKs
// Use openapi-typescript-codegen to generate client code from OpenAPI spec
[ApiController]
[Route("api/v1/orders")]
public class PublicOrdersController : ControllerBase
{
    // Consumer-friendly names, stable contract
    [HttpPost("search")]
    public async Task<ActionResult<SearchResult>> SearchOrders(
        [FromBody] SearchRequest request) { /* ... */ }
}

// For internal services — domain-specific names
[ApiController]
[Route("internal/sales")]
public class InternalSalesController : ControllerBase
{
    // Domain names, faster evolution
    [HttpPost("find")]
    public async Task<ActionResult<FindResponseBase>> Search(
        [FromBody] FindCriteriaBase criteria) { /* ... */ }
}
```

---

## Controller Implementation Options

### Option 1: Decorator Pattern

Controller injects the proxy type into the call. Boilerplate that handles mapping, defines which interface to call, creates proxy, makes the call, catches exceptions and translates to HTTP status codes.

```csharp
[ApiController]
public class DashboardController : ControllerBase
{
    [HttpPost("load")]
    public async Task<IActionResult> Load([FromBody] DashboardCriteria criteria)
    {
        try
        {
            var proxy = ProxyFactory.Create<IDashboardManager>();
            var result = await proxy.LoadAsync(criteria);
            return Ok(result);
        }
        catch (ApplicationException ex)
        {
            return StatusCode(500, ex.Message);
        }
    }
}
```

**Tip**: You can have subclasses in `DashboardCriteria` to support different flows. One `Load` operation is informed by the specific criteria type passed.

### Option 2: Strategy Pattern (Generally Preferred)

Strategy pattern leads resolution based on context. Preferred when the frontend can use a polymorphic API, passing different types of criteria.

```csharp
[ApiController]
public class SalesController : ControllerBase
{
    [HttpPost("search")]
    public async Task<IActionResult> Search([FromBody] FindCriteriaBase criteria)
    {
        // Context from headers determines which manager facet to call
        var context = ExtractContext(Request.Headers);
        var proxy = ProxyFactory.CreateForContext<ISalesManager>(context);
        var result = await proxy.SearchAsync(criteria);
        return Ok(result);
    }
}
```

### Option 3: Namespace-Based Resolution (Internal Only)

Internal manager namespaces in the header dynamically resolve at the WebAPI level. Simplifies code but **only safe in internal enterprise systems** where leaking namespaces to frontend is acceptable.

```csharp
[ApiController]
public class GenericController : ControllerBase
{
    [HttpPost("invoke")]
    public async Task<IActionResult> Invoke([FromBody] object payload)
    {
        // Namespace comes from header
        string targetNamespace = Request.Headers["X-Service-Namespace"];
        var proxy = ProxyFactory.CreateFromNamespace(targetNamespace);
        var result = await proxy.InvokeAsync(payload);
        return Ok(result);
    }
}
```

### Option 4: Workflow-Driven Frontend

Backend workflow drives frontend UX workflow. A sequence configuration controls which UI steps the user sees. A workflow engine runs in-process next to the manager.

**Important**: Not everything is a flow! Operations-based approach is more appropriate when the UI doesn't need a flow-type sequence of functionalities.

---

## API Versioning

### Version in Header (Preferred)

```
GET /api/orders/123
Accept: application/vnd.myapp.v2+json
Api-Version: 2.1
```

Headers are the better place for version because:
- Routing rules in API Gateway can filter on headers
- URLs stay clean
- Supports minor version increments without URL changes

### Version in URI (Also Acceptable)

```
GET /api/v2/orders/123
```

More visible but harder to manage with minor versions.

### Interface as SDK

Think of the interface in your naming convention as an **SDK** which you can ship to your consumer:
- Package SDK into private NuGet packages, version it, and distribute
- For external consumers, auto-generate TypeScript from OpenAPI specifications

### Webhook as Separate Boundary

If you expose webhooks, they should be a separate boundary in the gateway—not mixed with the main API.

---

## Boundary Design Checklist

- [ ] Gateway handles authentication only (no business code)
- [ ] Authentication mechanism varies by client context
- [ ] Context flows via headers, not method signatures
- [ ] BFF per client type (web, mobile, chat, IVR)
- [ ] BFF contains no business logic—only routing and packaging
- [ ] Public API and Private API are separate
- [ ] Controller strategy chosen (decorator, strategy, namespace, workflow)
- [ ] Controller is thin—packages headers and delegates to manager
- [ ] API versioning in headers (preferred) or URI
- [ ] Interfaces packaged as SDK (NuGet, TypeScript codegen)
- [ ] Webhooks are a separate gateway boundary
- [ ] System context not leaked into domain DTOs
