# Data Contract Factoring

Designing DTOs (Data Transfer Objects) that are autonomous per facet, separated by volatility area through namespaces, and polymorphic for context-driven variability.

---

## Core Principle: Autonomous Data Contracts Per Facet

**You should NOT apply a canonical data contract to all facets which were factored out.** Autonomous facets must have autonomous data contracts. Just as you factor service contracts by behavioral concern, you must factor data contracts to match.

### The Problem with Canonical DTOs

```csharp
❌ BAD: One canonical DTO used across different facets
// Single "Dog" DTO used everywhere
public class Dog
{
    public string Name { get; set; }
    public int Age { get; set; }
    public string ThingToFetch { get; set; }     // Only for IDog facet
    public Volume BarkVolume { get; set; }        // Only for IDog facet
    public long VetClinicNumber { get; set; }     // Only for IPet facet
    public List<Vaccination> Vaccinations { get; set; } // Only for IPet facet
}

// Both facets use the same bloated DTO
interface IDog { void Fetch(Dog dog); void Bark(Dog dog); }
interface IPet { void Vaccinate(Dog dog); void ScheduleAppointment(Dog dog); }
```

**Problems**: Couples the canine behavioral area to the clinic area. A change to clinic requirements forces changes to the canine DTO. Violates autonomy.

### The Solution: Separate DTOs Per Facet

```csharp
✅ GOOD: Autonomous DTOs per behavioral area

// Canine namespace — only canine-related properties
namespace Canine
{
    [DataContract]
    public class GoodDog
    {
        [DataMember] public string ThingToFetch { get; set; }
        [DataMember] public int InterestLevel { get; set; }
        [DataMember] public ushort FetchTimeout { get; set; }
        [DataMember] public BarkStyle BarkType { get; set; }
        [DataMember] public Volume BarkVolume { get; set; }
        [DataMember] public ushort BarkLength { get; set; }
    }
}

// Clinic namespace — only clinic-related properties
namespace Clinic
{
    [DataContract]
    public class Pet
    {
        [DataMember] public string Name { get; set; }
        [DataMember] public ushort Age { get; set; }
        [DataMember] public ulong VetClinicNumber { get; set; }
        [DataMember] public IEnumerable<Appointment> Appointments { get; set; }
        [DataMember] public IEnumerable<Vaccination> Vaccinations { get; set; }
    }

    [DataContract]
    public class Dog : Pet
    {
        [DataMember] public bool RequiresMuzzle { get; set; }
        [DataMember] public bool KennelCough { get; set; }
    }
}

// Each facet uses its own DTOs
interface IDog { void Fetch(Canine.GoodDog dog); void Bark(Canine.GoodDog dog); }
interface IPet { void Vaccinate(Clinic.Pet pet); void ScheduleAppointment(Clinic.Pet pet); }
```

---

## Namespace Separation by Volatility Area

Use namespaces to separate DTO classes per different volatility area. Each namespace represents a cohesive set of data contracts that change together.

### Namespace Strategy

```
Company.Manager.Sales.Interface/
├── Common/
│   ├── FindCriteriaBase.cs        ← Shared abstractions
│   └── FindResponseBase.cs
├── Online/
│   ├── ISalesManager.cs           ← Online context facet
│   ├── ItemCriteria.cs            ← Online-specific criteria
│   ├── RestaurantCriteria.cs      ← Another online variation
│   └── FindResponse.cs            ← Online-specific response
└── Restaurant/
    ├── ISalesManager.cs           ← Restaurant context facet
    ├── FindCriteria.cs            ← Restaurant-specific criteria
    └── FindResponse.cs            ← Restaurant-specific response
```

### Implementation

```csharp
// Common base — shared abstractions
namespace IDesign.Manager.Sales.Interface
{
    [DataContract]
    public abstract class FindCriteriaBase
    {
        [DataMember]
        public string Term { get; set; }
    }

    [DataContract]
    public abstract class FindResponseBase
    { }
}

// Online context — specific DTOs
namespace IDesign.Manager.Sales.Interface.Online
{
    [DataContract]
    public class ItemCriteria : FindCriteriaBase
    {
        [DataMember]
        public Guid Id { get; set; }
    }

    [DataContract]
    public class RestaurantCriteria : FindCriteriaBase
    {
        [DataMember]
        public string Address { get; set; }
    }

    [DataContract]
    public class FindResponse : FindResponseBase
    { }
}

// Restaurant context — different specific DTOs
namespace IDesign.Manager.Sales.Interface.Restaurant
{
    [DataContract]
    public class FindCriteria : FindCriteriaBase
    {
        [DataMember]
        public DateTime StartDate { get; set; }

        [DataMember]
        public DateTime EndDate { get; set; }
    }

    [DataContract]
    public class FindResponse : FindResponseBase
    { }
}
```

---

## Polymorphic DTO Strategy

Use base DTOs with context-specific subclasses. The DTO type itself drives resolution logic through polymorphism—"Look Ma, no switch!"

### Base Criteria Pattern

```csharp
// Abstract base with common fields
public abstract class FindCriteriaBase
{
    public string Term { get; set; }
}

// Online context uses item-based search
public class ItemCriteria : FindCriteriaBase
{
    public Guid Id { get; set; }
}

// Online context also searches by restaurant
public class RestaurantCriteria : FindCriteriaBase
{
    public string Address { get; set; }
}

// Restaurant context uses date-based search
namespace Restaurant
{
    public class FindCriteria : FindCriteriaBase
    {
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
    }
}
```

### Service Contract with Polymorphic Parameters

```csharp
// Both facets accept the base type — polymorphism handles routing
[ServiceContract]
public interface ISalesManager : IService
{
    [OperationContract]
    Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria);
}
```

**In service orientation, do not overload methods.** Instead, use polymorphism—embed the role in the criteria DTO itself.

---

## DTO Rules for Service Orientation

### Rule 1: Ship Primitives, Not Logic

In service orientation, we do not ship logic across boundaries—just send primitives (data). DTOs are pure data holders with no behavior.

```csharp
✅ GOOD: Pure data
[DataContract]
public class BarkRequest
{
    [DataMember] public BarkStyle Type { get; set; }
    [DataMember] public Volume Volume { get; set; }
    [DataMember] public ushort Length { get; set; }
}

❌ BAD: Logic in DTO
public class BarkRequest
{
    public BarkStyle Type { get; set; }
    public Volume Volume { get; set; }
    public bool IsLoud() => Volume == Volume.High;  // No logic!
}
```

### Rule 2: Constructors Enforce Validity

Nobody should be able to create an object which is not valid. Use constructors to enforce required fields.

```csharp
[DataContract]
public class CustomerProfile
{
    public CustomerProfile(string name, string email)
    {
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Email = email ?? throw new ArgumentNullException(nameof(email));
    }

    [DataMember] public string Name { get; private set; }
    [DataMember] public string Email { get; private set; }
    [DataMember] public IEnumerable<Address> Addresses { get; set; }
}
```

### Rule 3: Aggregate Root DTOs Use Collections

Customer is an aggregate root type DTO—it contains collections of related entities like profiles and preferences.

```csharp
[DataContract]
public class Customer
{
    [DataMember] public int Id { get; set; }
    [DataMember] public string Name { get; set; }
    [DataMember] public IEnumerable<CustomerProfile> Profiles { get; set; }
    [DataMember] public IEnumerable<Address> Addresses { get; set; }
}
```

### Rule 4: Weak References for Decoupling

When you need to lift a concern out of an aggregate (e.g., Preferences out of Customer), use weak references by ID rather than direct object references. Let each use case decide what it needs to retrieve.

```csharp
// Customer has a weak reference to preferences
[DataContract]
public class Customer
{
    [DataMember] public int Id { get; set; }
    [DataMember] public string Name { get; set; }
    [DataMember] public int PreferencesId { get; set; }  // Weak reference
}

// Preferences lives in its own schema, queried separately
[DataContract]
public class CustomerPreferences
{
    [DataMember] public int Id { get; set; }
    [DataMember] public int CustomerId { get; set; }  // Weak back-reference
    [DataMember] public IEnumerable<Preference> Items { get; set; }
}
```

### Rule 5: Each Layer Can Have Its Own DTOs

For highly volatile use cases, every layer should emit its own unique request and response DTOs. There is risk in reusing DTOs across layers when the use case is volatile.

```
Manager Layer:  SearchRequest → SearchResponse
Engine Layer:   MatchCriteria → MatchResult
Access Layer:   QueryFilter   → QueryResult
```

For stable use cases, sharing DTOs across layers is acceptable to reduce duplication.

### Rule 6: Response Wrappers for Cross-Boundary Calls

When interacting with third-party systems or IoT devices, use response wrappers that include business error codes. Do not include exception information—the error codes are for business-related errors.

```csharp
[DataContract]
public class Response<T>
{
    [DataMember] public bool IsSuccessful { get; set; }
    [DataMember] public T Value { get; set; }
    [DataMember] public string ErrorCode { get; set; }
    [DataMember] public string ErrorMessage { get; set; }
}
```

### Rule 7: Linear Growth, Not Exponential

With autonomous DTOs per facet, the number of operations across assets grows linearly. Data contracts also grow linearly. This is the correct growth pattern—as opposed to exponential growth from a single canonical DTO that must accommodate every context.

---

## Do Not Mix System Concerns with Domain DTOs

System-related concepts (security context, session info, trace data, origination) must not be mixed with business-domain DTOs.

```csharp
❌ BAD: System concerns in domain DTO
public class OrderRequest
{
    public int CustomerId { get; set; }
    public string AuthToken { get; set; }      // System concern!
    public string SessionId { get; set; }      // System concern!
    public string CorrelationId { get; set; }  // System concern!
    public IEnumerable<OrderLineItem> Items { get; set; }
}

✅ GOOD: System concerns flow via headers (out-of-band)
public class OrderRequest
{
    public int CustomerId { get; set; }
    public IEnumerable<OrderLineItem> Items { get; set; }
}
// AuthToken, SessionId, CorrelationId flow in message headers
```

---

## Data Contract Factoring Checklist

- [ ] No canonical DTO used across all facets
- [ ] DTOs separated into namespaces by volatility area
- [ ] Polymorphic base types used for context-driven criteria and responses
- [ ] DTOs are pure data holders—no business logic
- [ ] Constructors enforce required fields (no invalid objects)
- [ ] Aggregate roots contain collections of related entities
- [ ] Weak references (by ID) used when decoupling related entities
- [ ] System concerns not mixed into domain DTOs
- [ ] Response wrappers used for cross-boundary / third-party calls
- [ ] Each highly volatile layer has its own request/response DTOs
- [ ] Method overloading avoided—polymorphic DTOs used instead
- [ ] DTO growth is linear, not exponential
