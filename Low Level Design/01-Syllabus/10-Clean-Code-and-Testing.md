## Phase 10 — Clean Code & Testability

> LLD relevance: Evaluators read your code. Poorly named variables, 50-line methods,
> and untestable classes will tank your score even if the design is correct.
> Clean code isn't a nice-to-have — it's 15% of the scoring rubric.

---

### 10.1 Naming

- **Classes** — nouns: `ParkingSpot`, `BookingService`, `HourlyPricingStrategy`
- **Methods** — verbs: `parkVehicle()`, `calculateFee()`, `findAvailableSpot()`
- **Booleans** — questions: `isAvailable`, `hasActiveBooking`, `canPark`
- **Collections** — plural: `List<Ticket> activeTickets`, `Map<SpotId, ParkingSpot> spotsById`
- **Avoid**:
  - Single letters: `p`, `v`, `t` — meaningless to the reader
  - Generic names: `data`, `info`, `manager`, `handler`, `processor` — too vague
  - Abbreviations: `calc`, `mgr`, `svc` — save 3 characters, lose all readability
  - Negative booleans: `isNotFull` — double negatives confuse: `if (!isNotFull)` = ???
- **The test**: Can someone reading your code understand what this variable/method does without seeing the implementation?

### 10.2 Method Design

- **One thing per method** — if you need to use "and" to describe what a method does, split it
- **Max 10-15 lines** — if longer, extract a helper. In a 90-minute round, short methods save debugging time.
- **Max 2-3 parameters** — more than 3? Pass an object instead (Builder pattern for parameter objects)
- **Return early** — guard clauses at the top, happy path below. Don't nest 5 levels of if.
  ```java
  // BAD
  void park(Vehicle v) {
      if (v != null) {
          if (v.getType() != null) {
              if (hasAvailableSpot(v.getType())) {
                  // actual logic buried here
              }
          }
      }
  }
  
  // GOOD
  void park(Vehicle v) {
      if (v == null) throw new IllegalArgumentException("Vehicle cannot be null");
      if (v.getType() == null) throw new IllegalArgumentException("Vehicle type required");
      if (!hasAvailableSpot(v.getType())) throw new SpotNotAvailableException(v.getType());
      // actual logic at top level — clean, readable
  }
  ```

### 10.3 Error Handling

- **Custom exceptions** — `SpotNotAvailableException`, `InvalidTicketException` — not raw `RuntimeException("spot not found")`
- **Fail fast** — validate at boundaries (constructor, method entry), not deep inside logic
- **Never swallow exceptions** — `catch (Exception e) {}` is a hidden bug. At minimum, log it.
- **Don't use exceptions for control flow** — `try { findSpot(); } catch (NotFoundException e) { createSpot(); }` — use `Optional` or check existence first.
- **Machine coding reality**: You won't write full exception handling in 90 minutes. But having 2-3 custom exceptions and throwing them at the right points shows the evaluator you think about failure cases.

### 10.4 Code Organization

- **Group by feature** (in machine coding):
  ```
  model/     — data classes (Vehicle, Ticket, ParkingSpot)
  service/   — business logic (ParkingService, PricingService)
  strategy/  — strategy implementations
  exception/ — custom exceptions
  Main.java  — driver
  ```
- **In a time crunch**: 2-3 files is fine. Don't spend 10 minutes creating packages for a 60-minute round.

### 10.5 Testability (Design for It, Even If You Don't Write Tests)

The evaluator may not ask for tests, but **testable design = good design**. If your code is testable, it's automatically well-separated, injectable, and modular.

**What makes code testable:**
- **Constructor injection** — pass dependencies in, don't create them inside
  ```java
  // UNTESTABLE — hardcoded dependency
  class ParkingService {
      PricingStrategy pricing = new HourlyPricing(); // can't test with different pricing
  }
  
  // TESTABLE — inject dependency
  class ParkingService {
      PricingStrategy pricing;
      ParkingService(PricingStrategy pricing) { this.pricing = pricing; }
  }
  ```
- **No static state** — static mutable state (global variables) can't be reset between tests
- **Interface dependencies** — depend on `PricingStrategy` (interface), not `HourlyPricing` (class)
- **Pure logic in separate methods** — `calculateFee(hours, rate)` is a pure function, easy to test with any inputs

**How to mention testing in the interview:**
"My ParkingService takes a PricingStrategy via constructor injection. In production, I'd inject HourlyPricing. In tests, I'd inject a mock that returns a fixed price — so I can test parking logic independently from pricing logic."

### 10.6 Anti-Patterns to Avoid

| Anti-Pattern | What It Looks Like | The Fix |
|-------------|-------------------|---------|
| God Class | `ParkingLot` with 25 methods handling everything | Split into `SpotManager`, `PricingEngine`, `TicketService` |
| Primitive Obsession | `String vehicleType = "car"` everywhere | Use `VehicleType.CAR` enum |
| Feature Envy | `PricingService` reads 5 fields from `Ticket` to compute price | Move the computation to `Ticket.calculateFee()` |
| Data Class | Class with only getters/setters, no behavior | Add methods: `ticket.calculateFee()` not `pricingService.calculateFee(ticket)` |
| Shotgun Surgery | Adding a vehicle type requires changing 7 files | Use Factory + Strategy — change 1 file (add new class) |
| Long Method | 40-line method with nested ifs | Extract into small named methods |
| Magic Numbers | `if (hours > 3) price = 50 * hours` | `if (hours > FREE_HOURS) price = HOURLY_RATE * hours` |

### 10.7 The 30-Second Code Review Checklist

Before submitting or finishing the round, scan for:
- [ ] No public fields — all state is private with methods
- [ ] No `if-else` chains on type — use polymorphism
- [ ] No magic strings or numbers — use enums and constants
- [ ] Every class has a clear single purpose
- [ ] Methods are under 15 lines
- [ ] Dependencies are injected, not created inside
- [ ] `toString()` on model classes for readable output
- [ ] Working `main()` that demos all use cases
