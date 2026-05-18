# Service Contract Factoring

Splitting service interfaces into cohesive, focused facets aligned with behavioral concerns and volatility boundaries.

---

## What is Contract Factoring?

Contract factoring is the process of splitting a large service interface into smaller, focused interfaces (facets). Each facet groups operations that share a common behavioral concept. A service class then implements multiple facets—this is a **multifaceted service**.

**Key insight**: An interface is a behavioral abstraction. It is a formal service contract for behavior and information. Everything inside the curly braces of an interface must be related to the name of that interface—there must be COHESION.

---

## Factoring by Behavioral Concept

### Principle

Identify separate behavioral concepts and separate them into distinct interfaces. Operations on a facet are messages—they are verbs that tell the consumer what they can do.

### Example: The Dog Problem

```csharp
❌ BAD: Mixed behavioral concepts in one interface
[ServiceContract]
public interface IAnimalAttack
{
    [OperationContract]
    void DogPounce();      // Dog behavior

    [OperationContract]
    void DogBite();        // Dog behavior

    [OperationContract]
    void CatPounce();      // Cat behavior — different concept!

    [OperationContract]
    void CatBite();        // Cat behavior — different concept!
}

✅ GOOD: Separated by behavioral concept
[ServiceContract]
public interface IDogAttack
{
    [OperationContract]
    void Pounce();         // All operations relate to "Dog Attack"

    [OperationContract]
    void Bite();
}

[ServiceContract]
public interface ICatAttack
{
    [OperationContract]
    void Pounce();         // All operations relate to "Cat Attack"

    [OperationContract]
    void Bite();
}
```

**Note**: Operations within each facet use simple names (Pounce, Bite)—the interface name provides the context. No need for `DogPounce` when you're already on `IDogAttack`.

---

## Multifaceted Services

Every service will be multifaceted—implementing multiple interfaces. Each facet is raised as an endpoint that can be deployed and scaled independently.

### Example: Vet Clinic Service

```csharp
// Canine behavioral facet
[ServiceContract]
public interface IDog
{
    [OperationContract]
    void Fetch(GoodDog dog);

    [OperationContract]
    void Bark(GoodDog dog);
}

// Clinic behavioral facet — different volatility area
[ServiceContract]
public interface IPet
{
    [OperationContract]
    void ScheduleAppointment(Pet pet);

    [OperationContract]
    void Vaccinate(Pet pet);
}

// Service implements both facets
[ServiceBehavior]
public class PoodleService : IDog, IPet
{
    // IDog operations
    public void Fetch(GoodDog dog) { /* canine behavior */ }
    public void Bark(GoodDog dog) { /* canine behavior */ }

    // IPet operations
    public void ScheduleAppointment(Pet pet) { /* clinic behavior */ }
    public void Vaccinate(Pet pet) { /* clinic behavior */ }
}
```

### Why Multifaceted?

- **Agility**: Each facet can be deployed as a separate endpoint
- **Independent scaling**: Scale canine behavior independently from clinic behavior
- **Separation of concerns**: Different volatility areas evolve independently
- **Clear contracts**: Consumers depend only on the facet they need

---

## Compositional vs Hierarchical Style

### Compositional (Preferred)

Compositional style keeps facets decoupled from each other. No facet establishes a dependency or parent-child relationship with another.

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  IDog    │  │  IPet    │  │  IMammal │   ← Independent facets
└──────────┘  └──────────┘  └──────────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
              ┌──────────────┐
              │ PoodleService │   ← Implements all, no hierarchy between facets
              └──────────────┘
```

### Hierarchical (Use Only When Justified)

Hierarchical relationships between contracts are allowed only when there is a genuine logical hierarchy—when a change to the parent necessitates a change to all children.

```csharp
// Hierarchical is justified when Mammal properties genuinely
// apply to all subtypes and changes cascade correctly
[DataContract]
[KnownType(typeof(Dog))]
public class Mammal
{
    [DataMember] public int Coat { get; set; }
    [DataMember] public int Gender { get; set; }
}

[DataContract]
public class Dog : Mammal { }

[ServiceContract]
interface IMammal
{
    [OperationContract]
    void Shed(Mammal mammal);

    [OperationContract]
    void Lactate(Mammal mammal);
}
```

**When to use hierarchical**: IoT device trees, classification taxonomies, or when there is genuine continuity of behaviors across a hierarchy. Never use hierarchical just for code reuse.

---

## Contract Factoring at Each Layer

### Manager Level

At the manager, every facet is a **collection of use cases**. Operations are named by the call chain they represent—chunky operations that represent what the business needs.

```csharp
// Each facet represents a different area of business volatility
[ServiceContract]
public interface ISalesManager  // Online context use cases
{
    [OperationContract]
    Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria);
}

// Same service, different facet for restaurant context
namespace Restaurant
{
    [ServiceContract]
    public interface ISalesManager  // Restaurant context use cases
    {
        [OperationContract]
        Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria);
    }
}
```

### Engine Level

At engines, promote reuse. Facets may be shared across contexts rather than diverging by context.

```csharp
[ServiceContract]
public interface IValidationEngine
{
    [OperationContract]
    Task<ValidationResult> ConfirmRequestAsync(string request);
}

[ServiceContract]
public interface IOrderingEngine
{
    [OperationContract]
    Task<MatchResult> MatchAsync(MatchCriteria criteria);
}

[ServiceContract]
public interface IPricingEngine
{
    [OperationContract]
    Task<PriceResult> CalculateAsync(PriceCriteria criteria);
}
```

### Access Level

At the access layer, facets align with resource boundaries.

```csharp
[ServiceContract]
public interface IRestaurantAccess
{
    [OperationContract]
    Task FilterAsync();
}

[ServiceContract]
public interface IMenuAccess
{
    [OperationContract]
    Task<MenuItems> GetItemsAsync(MenuCriteria criteria);
}

[ServiceContract]
public interface ICustomerAccess
{
    [OperationContract]
    Task<CustomerProfile> GetProfileAsync(int customerId);
}
```

---

## Factoring Anti-Patterns

### Anti-Pattern 1: Interface Per Operation

One interface with one operation leads to an explosion of interfaces and handler classes.

```csharp
❌ BAD: One interface per operation
interface IFetchDog { void Fetch(Dog dog); }
interface IBarkDog { void Bark(Dog dog); }
interface ISchedulePet { void Schedule(Pet pet); }
interface IVaccinatePet { void Vaccinate(Pet pet); }
// Explosion of code, no cohesion

✅ GOOD: Group by behavioral concept
interface IDog { void Fetch(Dog dog); void Bark(Dog dog); }
interface IPet { void Schedule(Pet pet); void Vaccinate(Pet pet); }
```

### Anti-Pattern 2: Proliferation of Endpoints

Creating one endpoint per use case prohibits reuse. When a new use case arrives, another endpoint is added instead of leveraging existing facets with polymorphism.

### Anti-Pattern 3: Property-Like Operations

Operations should be verbs—actions the consumer can perform. Avoid getter/setter operations that turn the service into a remote data store.

```csharp
❌ BAD: Property-like operations
interface IDogProperties
{
    string GetName();
    void SetName(string name);
    int GetAge();
    void SetAge(int age);
}

✅ GOOD: Behavioral operations
interface IDog
{
    void Fetch(FetchRequest request);
    BarkResponse Bark(BarkRequest request);
}
```

### Anti-Pattern 4: Canonical Data Contract Across All Facets

Do not apply a single canonical DTO (e.g., `Dog`) to all factored facets. Each facet needs its own autonomous data contracts. See `DATA-CONTRACTS.md` for details.

---

## Factoring Checklist

- [ ] Each interface groups operations by a single behavioral concept
- [ ] Interface name provides context so operations use simple names
- [ ] All operations within a facet relate to the interface name (cohesion test)
- [ ] Compositional style used between facets unless genuine hierarchy exists
- [ ] Services implement multiple facets (multifaceted)
- [ ] Each facet can be raised as an independent endpoint
- [ ] No interface-per-operation explosion
- [ ] No property-like operations on service contracts
- [ ] Operations are verbs that tell the consumer what they can do
- [ ] Manager facets aligned with use case groups by context
- [ ] Engine facets promote reuse across contexts
- [ ] Access facets align with resource boundaries
