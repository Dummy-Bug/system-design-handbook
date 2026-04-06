## Phase 1 — Object-Oriented Programming Fundamentals

> LLD relevance: Every machine coding round tests whether you can model a real-world problem
> as classes with clear responsibilities. OOP is the language you think in during LLD.

### 1.1 Classes, Objects & Constructors
- Class = blueprint, Object = instance — the building block of every LLD solution
- Constructor — initialize state at creation time, enforce required fields
- Why it matters — in a Parking Lot problem, `ParkingSpot`, `Vehicle`, `Ticket` are classes. Your first 5 minutes should be identifying these.

### 1.2 Encapsulation
- Hide internal state — expose behavior through methods, not raw fields
- Access modifiers — private (internal), protected (subclass), public (everyone)
- Getters with logic — `getPrice()` computes from internal state, doesn't just return a field
- Why it matters — an evaluator seeing `ticket.price = 50` vs `ticket.calculatePrice()` knows whether you understand encapsulation. The second lets you change pricing logic without touching every caller.

### 1.3 Abstraction
- Abstract class — partial implementation, shared state + some concrete methods + some abstract methods
- Interface — pure contract, no state, just method signatures
- When abstract class — shared behavior across related classes (e.g., `Vehicle` with common `getType()` but abstract `getLicensePlate()`)
- When interface — unrelated classes sharing a capability (e.g., `Printable`, `Serializable`, `Observable`)
- Java 8+ default methods blur the line — but the mental model still holds
- **Rule of thumb**: if it's an "is-a" with shared code → abstract class. If it's a "can-do" capability → interface.

### 1.4 Inheritance
- is-a relationship — `Car extends Vehicle`, `PremiumSpot extends ParkingSpot`
- Method overriding — subclass provides specific behavior for a parent's method
- When to use — there's a genuine hierarchy and shared behavior (not just code reuse)
- **When NOT to use** — if you're inheriting just to reuse 2 methods, use composition instead. Inheritance is the tightest coupling in OOP.
- Diamond problem — multiple inheritance of classes is forbidden in Java/C# for this reason. Interfaces solve it.

### 1.5 Polymorphism
- **Runtime polymorphism** (dynamic dispatch) — `Vehicle v = new Car(); v.getType();` calls `Car.getType()`, not `Vehicle.getType()`
  - This is the core of Strategy, State, and Factory patterns — you program to the interface, the runtime picks the right implementation
- **Compile-time polymorphism** (overloading) — same method name, different parameters: `park(Car c)` vs `park(Truck t)`
- Why it matters — in a machine coding round, if your code has `if (type == "CAR") ... else if (type == "TRUCK") ...` scattered everywhere, you've failed the polymorphism test. Each vehicle type should know its own behavior.

### 1.6 Composition over Inheritance
- **Composition** = has-a relationship — `Car` has an `Engine`, not `Car extends Engine`
- Prefer composition — it's flexible, swappable at runtime, and doesn't create fragile hierarchies
- Example: `PaymentProcessor` has a `PaymentStrategy` (composition) vs `CreditCardPaymentProcessor extends PaymentProcessor` (inheritance)
  - With composition, you swap the strategy at runtime: `processor.setStrategy(new UPIPayment())`
  - With inheritance, you need a new subclass for every payment type
- **The test**: "would I ever want to change this relationship at runtime?" → if yes, composition. Always.

### 1.7 Enums
- Type-safe constants — `VehicleType.CAR` instead of magic string `"car"`
- Use for finite, fixed states — `SpotType`, `OrderStatus`, `PaymentMethod`, `PieceType` (chess)
- Enums can have behavior — `SpotType.COMPACT.getHourlyRate()` is valid and keeps logic co-located
- Why it matters — evaluators look for enums where beginners use strings. Strings are typo-prone, un-autocomplete-able, and don't enforce valid values at compile time.

### 1.8 Generics
- Type-safe collections and classes — `List<Vehicle>` instead of raw `List`
- Bounded generics — `<T extends Comparable<T>>` for a generic sorted collection
- Where it appears in LLD — generic `Cache<K, V>`, generic `EventBus<T extends Event>`, generic `Repository<T>`
- Don't overuse — if you're only ever using it with one type, skip the generic. YAGNI.

### 1.9 The `equals`, `hashCode`, and `toString` Contract
- If two objects are "logically equal" (same booking ID), `equals()` must return true
- If `equals()` is true, `hashCode()` MUST be the same — otherwise HashMap/HashSet break silently
- Override `toString()` for debugging — evaluators will see `Ticket@3f2a` vs `Ticket{id=T001, vehicle=KA-01-1234, spot=A-12}` in your console output
- This matters in machine coding — you'll use HashMaps and HashSets. If your key class doesn't override these, lookups silently fail.
