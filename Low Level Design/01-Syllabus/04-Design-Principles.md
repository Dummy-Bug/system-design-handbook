## Phase 4 — Design Principles Beyond SOLID

> LLD relevance: SOLID is the foundation. These principles are the judgment layer —
> they tell you when NOT to add complexity and when your design has gone too far.
> Evaluators notice over-engineering as much as under-engineering.

---

### 4.1 DRY (Don't Repeat Yourself)
- **Rule**: Every piece of knowledge should have a single, unambiguous representation in the system
- **What it means**: If the same logic exists in 3 places, a bug fix needs 3 changes — you'll miss one
- **When to apply**: If you copy-paste a block of code and change one thing, extract the common part
- **When NOT to apply**: Two pieces of code that happen to look similar but serve different purposes are NOT duplication. Premature DRY creates wrong abstractions. **Duplication is better than the wrong abstraction.**
- **In machine coding**: If your `parkCar()` and `parkTruck()` methods are 90% identical, extract a `parkVehicle(Vehicle v)` method

### 4.2 YAGNI (You Aren't Gonna Need It)
- **Rule**: Don't build something until you actually need it
- **What it means**: In a 90-minute round, don't add plugin systems, configuration frameworks, or abstract factories for things that have one implementation
- **The trap**: Beginners build elaborate hierarchies "in case we need it later." Evaluators see this as wasted time and added complexity.
- **Example**: Don't create a `NotificationStrategy` interface with only `EmailNotification` implementing it. If there's only email, just write `EmailNotifier`. Add the interface when the second notification type appears.
- **Tension with OCP**: OCP says "be open for extension." YAGNI says "don't build the extension point until you need it." **Resolve this by**: making code easy to refactor rather than pre-building every extension point.

### 4.3 KISS (Keep It Simple, Stupid)
- **Rule**: Prefer the simplest solution that works
- **In machine coding**: If a `HashMap<String, List<Booking>>` solves your lookup problem, don't build a custom B-Tree index
- **Complexity budget**: You have 90 minutes. Every unnecessary abstraction steals time from core functionality. Simple code that works > elegant code that's half-finished.

### 4.4 Composition over Inheritance
- Covered in Phase 1 (1.6) — repeated here because it's a principle, not just an OOP concept
- **The 3-question test before using inheritance**:
  1. Is the child truly a subtype of the parent? (is-a test)
  2. Will the child honor ALL of the parent's behavior? (LSP test)
  3. Will this hierarchy stay stable, or will I need multiple inheritance later?
- If any answer is "no" → use composition

### 4.5 Program to an Interface, Not an Implementation
- **Rule**: Declare variables, parameters, and return types as the interface — not the concrete class
- **Example**: `List<String> names = new ArrayList<>()` not `ArrayList<String> names = new ArrayList<>()`
- **Why**: Swapping `ArrayList` for `LinkedList` requires changing one line, not every method signature
- **In machine coding**: Your `ParkingLot` should depend on `ParkingStrategy` (interface), not `HourlyParkingStrategy` (implementation)

### 4.6 Law of Demeter (Principle of Least Knowledge)
- **Rule**: A method should only call methods on: (1) its own object, (2) its parameters, (3) objects it creates, (4) its direct fields
- **The violation**: `order.getCustomer().getAddress().getCity()` — train wreck of chained calls
- **Why it's bad**: `Order` now knows about `Customer`, `Address`, AND `City`. If `Address` structure changes, `Order` code breaks.
- **The fix**: `order.getDeliveryCity()` — delegate to `Order`, which delegates to `Customer`, which delegates to `Address`
- **In machine coding**: If evaluator sees `parkingLot.getFloor(2).getSpot(5).getVehicle().getLicensePlate()` — that's a red flag

### 4.7 Tell, Don't Ask
- **Rule**: Tell an object what to do — don't ask for its data and do the work yourself
- **Bad**: `if (account.getBalance() >= amount) account.setBalance(account.getBalance() - amount);`
- **Good**: `account.debit(amount)` — the Account decides if the debit is valid and handles the logic
- **Why**: Keeps logic with the data. The object that owns the state should own the behavior.
- **In machine coding**: `spot.park(vehicle)` is better than `if (spot.isEmpty()) spot.setVehicle(vehicle); spot.setOccupied(true);`

### 4.8 Separation of Concerns
- **Rule**: Each module/class/method should handle one concern
- **Levels**:
  - Method level: A method should do one thing (don't mix validation + calculation + logging)
  - Class level: SRP (covered in Phase 2)
  - Package level: Group by feature/domain, not by technical layer
- **Package-by-feature vs package-by-layer**:
  - By layer: `controllers/`, `services/`, `models/`, `repositories/` — everything mixed together within each layer
  - By feature: `parking/`, `billing/`, `notification/` — each feature is self-contained
  - Prefer by feature for machine coding — easier to navigate under time pressure

### 4.9 Fail Fast
- **Rule**: If something is wrong, fail immediately with a clear error — don't propagate bad state
- **Example**: If `parkVehicle(null)` is called, throw `IllegalArgumentException` immediately — don't let null propagate until it causes a NullPointerException 10 methods deep
- **Validate at the boundary**: Constructor validation, method entry validation — catch bad input where it enters
- **In machine coding**: `if (spot == null) throw new SpotNotFoundException(spotId)` is better than returning null and hoping the caller checks

---

### How Principles Map to Evaluator Scoring

| What evaluator looks for | Principle in action |
|--------------------------|-------------------|
| "Can I add a new feature without rewriting?" | OCP + Strategy |
| "Is the code readable?" | KISS + meaningful names + small methods |
| "Is the code testable?" | DIP + constructor injection |
| "Did they over-engineer?" | YAGNI + KISS |
| "Does each class have clear purpose?" | SRP + Separation of Concerns |
| "Is the data encapsulated?" | Tell Don't Ask + Law of Demeter |
