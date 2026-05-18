# Complete Worked Examples

End-to-end examples showing contract factoring, data contract design, context-driven resolution, and interaction patterns combined.

---

## Example 1: Food Ordering Platform — Sales Manager

A platform where customers can order food Online or from a Restaurant kiosk. The Sales Manager handles search and ordering across both contexts.

### System Design Context

```
Managers:   SalesManager, CustomerManager, NotificationManager
Engines:    ValidationEngine, OrderingEngine, PricingEngine
Access:     RestaurantAccess, MenuAccess, CustomerAccess, SpecialsAccess
```

### Step 1: Factor Service Contracts

The SalesManager needs separate facets for Online and Restaurant contexts because:
- Different use cases per context
- Different DTOs per context
- Different speed of evolution
- When behavior of context diverges over time, segregate facets

```csharp
// Online context facet
namespace IDesign.Manager.Sales.Interface.Online
{
    [ServiceContract(Namespace = "IDesign.Manager.Sales.Interface.Online")]
    public interface ISalesManager : IService
    {
        [OperationContract]
        Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria);
    }
}

// Restaurant context facet — same operation name, different namespace
namespace IDesign.Manager.Sales.Interface.Restaurant
{
    [ServiceContract(Namespace = "IDesign.Manager.Sales.Interface.Restaurant")]
    public interface ISalesManager : IService
    {
        [OperationContract]
        Task<FindResponseBase> SearchAsync(FindCriteriaBase criteria);
    }
}
```

### Step 2: Factor Data Contracts

**Common base** with shared properties, **context-specific subclasses** for variability.

```csharp
// Shared base — in Common namespace
namespace IDesign.Manager.Sales.Interface
{
    [DataContract]
    public abstract class FindCriteriaBase
    {
        [DataMember]
        public string Term { get; set; }
    }

    [DataContract]
    public abstract class FindResponseBase { }
}

// Online context DTOs — search by item or by restaurant
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
    public class FindResponse : FindResponseBase { }
}

// Restaurant context DTOs — search by date range
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
    public class FindResponse : FindResponseBase { }
}
```

### Step 3: Implement Manager as Mediator

```csharp
// Base partial class — shared setup
[ApplicationManifest("IDesign.Microservice.Sales", "SalesManager")]
public partial class SalesManager : ServiceBase
{
    public SalesManager(StatelessServiceContext context) : base(context) { }
}

// Online facet implementation
public partial class SalesManager : Online.ISalesManager
{
    async Task<FindResponseBase> Online.ISalesManager.SearchAsync(
        FindCriteriaBase criteria)
    {
        OriginationContext origination = Origination;
        MyContext context = MyContext;

        // Strategy resolves by criteria type — no switch statement
        return await UseCaseFactory.CallAsync<FindCriteriaBase, FindResponseBase>(
            this, criteria);
    }
}

// Restaurant facet implementation
public partial class SalesManager : Restaurant.ISalesManager
{
    async Task<FindResponseBase> Restaurant.ISalesManager.SearchAsync(
        FindCriteriaBase criteria)
    {
        OriginationContext origination = Origination;
        MyContext context = MyContext;

        return await UseCaseFactory.CallAsync<FindCriteriaBase, FindResponseBase>(
            this, criteria);
    }
}
```

### Step 4: Use Case Classes (Not Services)

```csharp
// Online use cases — one method per criteria type
namespace IDesign.Manager.Sales.Service.Online
{
    public class UseCases
    {
        ServiceBase Service { get; set; }

        public UseCases(ServiceBase service)
        {
            Service = service;
        }

        // When online user searches by item
        public async Task<FindResponseBase> SearchAsync(ItemCriteria criteria)
        {
            IRestaurantAccess restaurantProxy =
                Proxy.ForComponent<IRestaurantAccess>(Service);
            await restaurantProxy.FilterAsync();

            IOrderingEngine orderingProxy =
                Proxy.ForComponent<IOrderingEngine>(Service);
            var matched = await orderingProxy.MatchAsync(
                new MatchCriteria { ItemId = criteria.Id });

            IPricingEngine pricingProxy =
                Proxy.ForComponent<IPricingEngine>(Service);
            var priced = await pricingProxy.CalculateAsync(
                new PriceCriteria { Items = matched.Items });

            return new Online.FindResponse { /* populate from priced */ };
        }

        // When online user searches by restaurant location
        public async Task<FindResponseBase> SearchAsync(RestaurantCriteria criteria)
        {
            IRestaurantAccess restaurantProxy =
                Proxy.ForComponent<IRestaurantAccess>(Service);
            await restaurantProxy.FilterAsync();

            return new Online.FindResponse { /* populate */ };
        }
    }
}

// Restaurant use cases — different implementation for restaurant context
namespace IDesign.Manager.Sales.Service.Restaurant
{
    public class UseCases
    {
        ServiceBase Service { get; set; }

        public UseCases(ServiceBase service)
        {
            Service = service;
        }

        // When restaurant kiosk searches by date range
        public async Task<FindResponseBase> SearchAsync(
            Interface.Restaurant.FindCriteria criteria)
        {
            IMenuAccess menuProxy = Proxy.ForComponent<IMenuAccess>(Service);
            var items = await menuProxy.GetItemsAsync(
                new MenuCriteria
                {
                    StartDate = criteria.StartDate,
                    EndDate = criteria.EndDate
                });

            ISpecialsAccess specialsProxy =
                Proxy.ForComponent<ISpecialsAccess>(Service);
            // ... combine with daily specials

            return new Interface.Restaurant.FindResponse { /* populate */ };
        }
    }
}
```

### Step 5: Tests

```csharp
[TestClass]
public class SalesManagerTests
{
    UnitTestHarness harness;

    [TestInitialize]
    public void Setup()
    {
        harness = new UnitTestHarness();
        harness.Setup(harness.ActorServiceFactory,
            typeof(SalesManager),
            typeof(ValidationEngine),
            typeof(RestaurantAccess),
            typeof(OrderingEngine),
            typeof(CustomerAccess),
            typeof(MenuAccess),
            typeof(PricingEngine),
            typeof(SpecialsAccess));
    }

    [TestMethod]
    public void Test_Online_SearchAsync_With_ItemCriteria()
    {
        MyContext contextMock = new MyContext { Value = "Test" };

        Action<Online.ISalesManager> callerMock = (proxy) =>
        {
            ItemCriteria criteria = new ItemCriteria { Id = Guid.NewGuid() };
            FindResponse response =
                proxy.SearchAsync(criteria).Result as FindResponse;
        };

        harness.TestService<Online.ISalesManager>(callerMock, contextMock);
    }

    [TestMethod]
    public void Test_Restaurant_SearchAsync()
    {
        MyContext contextMock = new MyContext { Value = "Test" };

        Action<Restaurant.ISalesManager> callerMock = (proxy) =>
        {
            Restaurant.FindCriteria criteria = new Restaurant.FindCriteria
            {
                StartDate = DateTime.Today,
                EndDate = DateTime.Today.AddDays(7)
            };
            Restaurant.FindResponse response =
                proxy.SearchAsync(criteria).Result as Restaurant.FindResponse;
        };

        harness.TestService<Restaurant.ISalesManager>(callerMock, contextMock);
    }

    [TestMethod]
    public void Test_Online_SearchAsync_With_RestaurantMock()
    {
        MyContext contextMock = new MyContext { Value = "Test" };

        // Mock a downstream dependency
        var restaurantAccessMock = new Mock<IRestaurantAccess>();
        restaurantAccessMock.Setup(x => x.FilterAsync());

        Action<Online.ISalesManager> callerMock = (proxy) =>
        {
            ItemCriteria criteria = new ItemCriteria();
            proxy.SearchAsync(criteria).Wait();
        };

        harness.TestService<Online.ISalesManager>(
            callerMock, restaurantAccessMock, contextMock);
    }
}
```

---

## Example 2: Vet Clinic — Contract Factoring

Demonstrating how to factor service and data contracts for a veterinary clinic system with canine, feline, and clinic behavioral areas.

### Factored Service Contracts

```csharp
// Canine behavioral area
namespace Canine
{
    [ServiceContract]
    public interface IDog
    {
        [OperationContract]
        void Fetch(GoodDog dog);

        [OperationContract]
        void Bark(GoodDog dog);
    }
}

// Feline behavioral area
namespace Feline
{
    [ServiceContract]
    public interface ICat
    {
        [OperationContract]
        void Purr(Cat cat);

        [OperationContract]
        void CatchMouse(Cat cat);
    }
}

// Clinic behavioral area — shared across animal types
namespace Clinic
{
    [ServiceContract]
    public interface IPet
    {
        [OperationContract]
        void ScheduleAppointment(Pet pet);

        [OperationContract]
        void Vaccinate(Pet pet);
    }
}

// Classification behavioral area — biological taxonomy
namespace Classification
{
    [ServiceContract]
    interface IMammal
    {
        [OperationContract]
        void Shed(Mammal mammal);

        [OperationContract]
        void Lactate(Mammal mammal);
    }
}
```

### Factored Data Contracts

Each behavioral area has its own autonomous DTOs in its own namespace:

```csharp
// Canine DTOs — only canine properties
namespace Canine
{
    public enum BarkStyle { Growl, Bark, Yelp }
    public enum Volume { Low, Normal, High }

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

    // Separate DTOs per operation for high volatility
    [DataContract]
    public class Fetching { /* fetch-specific fields */ }

    [DataContract]
    public class BarkRequest
    {
        [DataMember] public BarkStyle Type { get; set; }
        [DataMember] public Volume Volume { get; set; }
        [DataMember] public ushort Length { get; set; }
    }
}

// Clinic DTOs — only clinic properties
namespace Clinic
{
    [DataContract]
    [KnownType(typeof(Dog))]
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

    // Clinic-specific supporting DTOs
    [DataContract]
    public struct Vaccination
    {
        [DataMember] public DateTime Date { get; set; }
        [DataMember] public string Description { get; set; }
    }
}

// Feline DTOs — only feline properties
namespace Feline
{
    [DataContract]
    public class Cat
    {
        [DataMember] public int LevelOfContentment { get; set; }
        [DataMember] public int PettingStyle { get; set; }
        [DataMember] public bool Claws { get; set; }
        [DataMember] public int Speed { get; set; }
    }
}
```

### Multifaceted Services

```csharp
// Poodle service implements canine + clinic facets
[ServiceBehavior]
public class PoodleService : IDog, IPet
{
    public void Fetch(Canine.GoodDog dog) { }
    public void Bark(Canine.GoodDog dog) { }
    public void ScheduleAppointment(Clinic.Pet pet) { }
    public void Vaccinate(Clinic.Pet pet) { }
}

// Siamese service implements feline + clinic facets
[ServiceBehavior]
public class SiameseService : ICat, IPet
{
    public void Purr(Feline.Cat cat) { }
    public void CatchMouse(Feline.Cat cat) { }
    public void ScheduleAppointment(Clinic.Pet pet) { }
    public void Vaccinate(Clinic.Pet pet) { }
}

// Clinic-only service — just the clinic facet
[ServiceBehavior]
public class ClinicService : IPet
{
    public void ScheduleAppointment(Clinic.Pet pet) { }
    public void Vaccinate(Clinic.Pet pet) { }
}
```

---

## Example 3: Workflow Manager — Production Pipeline

A workflow manager that orchestrates a production pipeline through multiple subsystems.

```csharp
// Workflow definition
var workflow = new Workflow
{
    Name = "Production",
    Steps = new[]
    {
        new Step
        {
            Name = "Harvest",
            Subsystem = typeof(IFeedManager),
            Timeout = TimeSpan.FromMinutes(30)
        },
        new Step
        {
            Name = "Process",
            Subsystem = typeof(IProcessingManager),
            Timeout = TimeSpan.FromMinutes(30)
        },
        new Step
        {
            Name = "Evaluate",
            Subsystem = typeof(IControlManager),
            Timeout = TimeSpan.FromMinutes(30)
        },
        new Step
        {
            Name = "Verify",
            Subsystem = typeof(IControlManager),
            Timeout = TimeSpan.FromMinutes(30)
        },
        new Step
        {
            Name = "Notify",
            Subsystem = typeof(INotificationManager),
            Timeout = TimeSpan.FromMinutes(30)
        }
    }
};

// Manager separates admin and execution facets
[ServiceContract]
public interface IRunAdminManager
{
    [OperationContract]
    void Start(string installationId);

    [OperationContract]
    void Suspend(string installationId, TimeSpan span);

    [OperationContract]
    void Abort(string installationId);

    [OperationContract]
    void Watch(string installationId);
}

// OnComplete receives callback when step finishes
[ServiceContract]
interface IRunManager : IService
{
    [OperationContract(IsOneWay = true)]
    void OnComplete(Message message);
}

// Implementation orchestrates the flow
public class RunManager : ServiceBase, IRunAdminManager, IRunManager
{
    void IRunAdminManager.Start(string installationId)
    {
        InitializeWorkflow(installationId);
        Transition();  // Start first step
    }

    void IRunManager.OnComplete(Message message)
    {
        Transition();  // Move to next step
    }

    private void Transition()
    {
        Step next = FindNextStep();
        if (next == null) { CompleteWorkflow(); return; }

        ActivateStep(next.Name);

        // Proxy to subsystem — reflectively invoke
        var proxy = ProxyFactory.Create(next.Subsystem);
        proxy.Invoke(next.Name);
    }
}
```

---

## Pattern Summary

| Pattern | Where Applied | Purpose |
|---------|--------------|---------|
| **Multifaceted Service** | Manager, Engine, Access | Multiple interfaces per service class |
| **Partial Classes** | Manager | Organize facet implementations into separate files |
| **Namespace Separation** | Interface + DTO projects | Separate volatility areas |
| **Polymorphic DTOs** | Criteria and Response types | Context-driven variability without switch |
| **UseCaseFactory** | Manager → Use Case delegation | Reflection-based strategy routing by DTO namespace |
| **Proxy Pattern** | All inter-service calls | Abstract transport, enable technology evolution |
| **Workflow Manager** | Sequential business flows | Step-based orchestration with subsystem delegation |
| **BFF** | API boundary | Client-type-specific API surface |
| **Marker Interfaces** | Messaging | IEvent, IObservable, ICommand for clarity |
| **Response Wrapper** | Cross-boundary calls | Response\<T\> with error codes |
