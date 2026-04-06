## Phase 3 — Design Patterns

> LLD relevance: Patterns are reusable solutions to recurring design problems.
> You don't need to memorize all 23 GoF patterns. You need to recognize WHEN a problem
> calls for a pattern and apply it naturally. These 16 are the ones that appear in interviews.

---

### Creational Patterns — How objects are created

#### 3.1 Factory Method
- **Problem**: You need to create objects but the exact type depends on runtime input
- **Solution**: A method returns the right subclass based on input — caller doesn't use `new` directly
- **When it appears**: `VehicleFactory.create("car")` → returns `Car`. `SpotFactory.create("compact")` → returns `CompactSpot`
- **Interview trigger**: Anytime you're creating different subtypes of the same interface based on a parameter
- **Appears in**: Parking Lot (vehicle/spot creation), Chess (piece creation), Vending Machine (item creation)

#### 3.2 Abstract Factory
- **Problem**: You need to create families of related objects that must be used together
- **Solution**: Factory of factories — one factory per family
- **When it appears**: `UIFactory` → `DarkThemeFactory` creates `DarkButton + DarkTextBox`, `LightThemeFactory` creates `LightButton + LightTextBox`
- **Interview trigger**: Multiple related objects that vary together as a group
- **Appears in**: Cross-platform UI, game themes, multi-database support
- **Honestly**: Rarely asked directly. Know it exists, but Factory Method covers 90% of cases.

#### 3.3 Builder
- **Problem**: Object has many optional fields — constructor with 10 parameters is unreadable
- **Solution**: Fluent API — `Order.builder().item(pizza).size(LARGE).addTopping(CHEESE).build()`
- **Interview trigger**: Any entity with optional configuration — orders, queries, notifications, game configs
- **Key rule**: `build()` should validate — don't allow invalid objects to be constructed
- **Appears in**: Any problem with configurable entities — Order, Query, Notification, Game setup

#### 3.4 Singleton
- **Problem**: Only one instance should exist — DB connection pool, config manager, logger
- **Solution**: Private constructor + static `getInstance()` method
- **Thread-safe versions**: Double-checked locking, enum singleton (Java), module-level (Python)
- **Why it's controversial**: It's essentially a global variable. Hard to test, hard to mock, hidden dependency.
- **Interview stance**: "I'd use Singleton for the ParkingLot instance since there's physically one lot, but I'd still inject it as a dependency rather than calling `ParkingLot.getInstance()` everywhere — keeps it testable."
- **Appears in**: Parking Lot, Library Management (one library), any system with a single orchestrator

#### 3.5 Prototype
- **Problem**: Creating an object from scratch is expensive; cloning an existing one is cheaper
- **Solution**: `clone()` method that copies the current object
- **Shallow vs deep clone**: Shallow copies references (both point to same inner object). Deep clone copies everything recursively.
- **Interview trigger**: Game board reset (clone initial state), document templates, undo functionality
- **Appears in**: Chess (reset board), Spreadsheet (copy cell with formula), Document editor

---

### Structural Patterns — How objects are composed

#### 3.6 Adapter
- **Problem**: Two incompatible interfaces need to work together
- **Solution**: Wrapper class that translates one interface to another
- **Interview trigger**: Integrating a third-party library or legacy system with a different interface
- **Example**: Your system expects `PaymentGateway.charge(amount)` but Stripe SDK has `Stripe.createCharge(params)` → `StripeAdapter implements PaymentGateway`
- **Appears in**: Payment integration, notification channels (SMS/Email have different APIs)

#### 3.7 Decorator
- **Problem**: Add behavior to an object dynamically without modifying its class
- **Solution**: Wrap the object in a decorator that adds behavior and delegates to the original
- **The key insight**: Decorators are stackable — `new EncryptedStream(new CompressedStream(new FileStream()))` — each layer adds behavior
- **Interview trigger**: "Add logging/caching/validation/encryption to existing behavior without changing it"
- **Classic example**: Coffee shop — `new WhipCream(new Mocha(new Espresso()))` — each decorator adds cost and description
- **Appears in**: I/O streams, Pizza/Coffee ordering (toppings), Logger decoration, cache layers

#### 3.8 Facade
- **Problem**: A subsystem has many classes — clients shouldn't know about all of them
- **Solution**: One simplified interface that coordinates the complex subsystem
- **Example**: `BookingFacade.book(user, movie, seats)` internally calls `SeatLockService`, `PaymentService`, `NotificationService`, `TicketGenerator`
- **Interview trigger**: When your system has 5+ internal services and external callers need a simple entry point
- **Appears in**: BookMyShow (booking flow), Hotel Reservation, any multi-step operation

#### 3.9 Composite
- **Problem**: Individual objects and groups of objects should be treated uniformly
- **Solution**: Tree structure where leaves and composites implement the same interface
- **Classic example**: File system — `File` and `Directory` both implement `FileSystemItem`. `Directory` contains a list of `FileSystemItem` (can be files or other directories).
- **Interview trigger**: Hierarchical/tree-structured data with uniform operations
- **Appears in**: File System, organizational hierarchy, menu systems, expression trees (spreadsheet formulas)

#### 3.10 Proxy
- **Problem**: Control access to an object — add lazy loading, access control, or logging without changing the object
- **Solution**: Proxy class with the same interface that intercepts calls
- **Types**: Virtual proxy (lazy load), Protection proxy (access control), Remote proxy (network call), Caching proxy
- **Appears in**: Image lazy loading, access-controlled documents, API rate limiting

---

### Behavioral Patterns — How objects communicate

#### 3.11 Strategy
- **Problem**: Multiple algorithms for the same task — don't hardcode the choice
- **Solution**: Define a family of algorithms, encapsulate each, make them interchangeable
- **This is THE most important pattern in LLD interviews**
- **Interview trigger**: Any `if-else` or `switch` that picks behavior based on type → replace with Strategy
- **Example**: `PricingStrategy` — `HourlyPricing`, `FlatRatePricing`, `SurgePricing` — swap at runtime
- **Appears in**: Parking Lot (pricing), Ride-sharing (fare calculation), Payment (payment method), Elevator (scheduling algorithm), Splitwise (split strategy)

#### 3.12 Observer
- **Problem**: When one object changes state, multiple other objects need to know — without tight coupling
- **Solution**: Subject maintains a list of observers, notifies all on state change
- **Interview trigger**: "Notify users when X happens", "update dashboard when score changes", "alert when stock price crosses threshold"
- **Push vs Pull**: Push — subject sends data with notification. Pull — observer queries subject after notification.
- **Appears in**: Notification systems, Stock ticker, Auction (bid updates), Event bus, Cricket scoreboard

#### 3.13 State
- **Problem**: Object behavior changes based on its internal state — complex `if-else` on state
- **Solution**: Each state is a class. Object delegates behavior to its current state object.
- **How it differs from Strategy**: Strategy is chosen by the CLIENT. State transitions happen INTERNALLY based on events.
- **Interview trigger**: Any entity with a lifecycle — Order (PLACED → CONFIRMED → SHIPPED → DELIVERED), Elevator (IDLE → MOVING_UP → MOVING_DOWN → DOOR_OPEN), Vending Machine (IDLE → COIN_INSERTED → DISPENSING)
- **Appears in**: Vending Machine, Elevator, Order management, ATM, Traffic Light

#### 3.14 Command
- **Problem**: You need to encapsulate a request as an object — for undo/redo, queuing, or logging
- **Solution**: Wrap each action as a Command object with `execute()` and `undo()` methods
- **Interview trigger**: "Support undo/redo", "queue operations", "log all actions for replay"
- **Example**: Text editor — `InsertCommand`, `DeleteCommand`, `BoldCommand` — each has `execute()` and `undo()`. Stack of commands = undo history.
- **Appears in**: Text Editor, Spreadsheet, Remote Control, Task Queue, any undo/redo system

#### 3.15 Chain of Responsibility
- **Problem**: A request should be handled by one of several handlers, but the sender shouldn't know which
- **Solution**: Chain handlers together — each handler either processes the request or passes it to the next
- **Interview trigger**: Validation pipelines, approval workflows, log level filtering, request processing
- **Example**: Expense approval — `Manager` (up to 1000) → `Director` (up to 10000) → `VP` (up to 100000) → `CEO` (any amount)
- **Appears in**: Logger, Vending Machine (coin/note processing), ATM (denomination dispenser), Request validation

#### 3.16 Template Method
- **Problem**: Multiple classes follow the same algorithm structure but differ in specific steps
- **Solution**: Base class defines the skeleton, subclasses override specific steps
- **Interview trigger**: Same workflow with different implementations — payment processing, report generation, game turn flow
- **Example**: `DataParser` defines `readFile() → parseData() → validate() → output()`. `CSVParser` and `JSONParser` override `parseData()` differently.
- **Appears in**: Game loop (initialize → play → end), Payment processing, Report generation

#### 3.17 Mediator
- **Problem**: Many objects communicate with many other objects — spaghetti coupling
- **Solution**: Central mediator coordinates all communication — objects only know the mediator
- **Interview trigger**: Chat rooms, auction houses, air traffic control — anything where N participants need to communicate
- **Example**: Chat room — users don't message each other directly. They send to the `ChatRoom` mediator, which routes to the right recipients.
- **Appears in**: Chat system, Auction, Air traffic control, UI components coordination

#### 3.18 Iterator
- **Problem**: Traverse a collection without exposing its internal structure
- **Solution**: `Iterator` interface with `hasNext()` and `next()`
- **Interview trigger**: Custom collections, tree traversal, paginated results
- **Appears in**: File system traversal, playlist navigation, social feed pagination

---

### Pattern Combinations That Win Interviews

| Problem         | Pattern Combo                                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------------- |
| Parking Lot     | Factory (create vehicles/spots) + Strategy (pricing) + Observer (notify on full) + Singleton (lot instance)           |
| Elevator System | State (elevator states) + Strategy (scheduling algorithm) + Observer (floor display) + Command (button press)         |
| Vending Machine | State (machine states) + Chain of Responsibility (coin processing) + Factory (product creation)                       |
| Chess           | Factory (piece creation) + Strategy (move validation per piece) + Command (undo move) + Observer (check notification) |
| Splitwise       | Strategy (split type) + Observer (notify on expense) + Factory (create split)                                         |
| BookMyShow      | Facade (booking flow) + Strategy (seat selection) + Observer (notifications) + Builder (ticket)                       |
