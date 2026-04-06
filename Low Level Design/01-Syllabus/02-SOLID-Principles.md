## Phase 2 — SOLID Principles

> LLD relevance: SOLID is the scoring rubric. Evaluators don't count lines of code —
> they check if your design can handle a new requirement without rewriting existing code.
> Every principle below directly maps to what interviewers mark on their scorecard.

### 2.1 Single Responsibility Principle (SRP)
- **Rule**: A class should have only one reason to change
- **What it means in practice**: `ParkingLot` should not handle ticket pricing, display formatting, AND payment processing. Each is a separate concern.
- **How to spot violations**: If you're describing a class and use the word "and" — "this class manages spots AND calculates pricing AND sends notifications" — it has too many responsibilities.
- **The fix**: Extract each responsibility into its own class — `SpotManager`, `PricingEngine`, `NotificationService`
- **Real example**:
  - Bad: `Order` class that validates, calculates total, applies discount, sends email, updates inventory
  - Good: `OrderValidator`, `PricingCalculator`, `DiscountEngine`, `NotificationService`, `InventoryService` — each with one job
- **Interview signal**: When the interviewer adds a new requirement ("now add surge pricing"), you should only touch the `PricingEngine` class — nothing else changes. That's SRP working.

### 2.2 Open/Closed Principle (OCP)
- **Rule**: Open for extension, closed for modification
- **What it means**: When a new requirement comes, you ADD a new class — you don't MODIFY existing working code
- **The canonical violation**: `if-else` chains based on type
  ```
  // BAD — adding a new vehicle type means modifying this method
  if (vehicle.type == CAR) rate = 10;
  else if (vehicle.type == TRUCK) rate = 20;
  else if (vehicle.type == BUS) rate = 30;  // added later — modified existing code
  ```
- **The fix**: Strategy pattern or polymorphism
  ```
  // GOOD — adding a new vehicle type means adding a new class
  interface PricingStrategy { int getRate(); }
  class CarPricing implements PricingStrategy { int getRate() { return 10; } }
  class TruckPricing implements PricingStrategy { int getRate() { return 20; } }
  // New type? Add BusPricing. Existing code untouched.
  ```
- **This is the #1 thing Flipkart/Rippling evaluators test**: They will add a requirement mid-round ("now support motorcycles"). If you need to modify 5 files, you violated OCP. If you add 1 new class, you pass.

### 2.3 Liskov Substitution Principle (LSP)
- **Rule**: Subtypes must be substitutable for their base type without breaking correctness
- **The classic violation**: Rectangle and Square
  ```
  class Rectangle { setWidth(w); setHeight(h); }
  class Square extends Rectangle { setWidth(w) { this.w = w; this.h = w; } }
  // Breaks: code that does rect.setWidth(5); rect.setHeight(10); expect area = 50
  // But Square makes area = 100 — substituting Square for Rectangle breaks the caller
  ```
- **How to spot it**: If a subclass overrides a method and changes the behavior in a way the caller doesn't expect — LSP is violated
- **Real LLD example**: `ReadOnlyUser extends User` that throws `UnsupportedOperationException` on `setName()` — the caller expects all `User` objects to be modifiable. LSP broken.
- **The fix**: Don't inherit if the subclass can't honor the parent's full contract. Use composition or separate interfaces instead.

### 2.4 Interface Segregation Principle (ISP)
- **Rule**: No client should be forced to depend on methods it doesn't use
- **The violation**:
  ```
  interface Worker {
      void code();
      void test();
      void attendMeeting();
      void writeDocument();
  }
  // A Junior Developer is forced to implement writeDocument() even though they never do it
  ```
- **The fix**: Split into focused interfaces
  ```
  interface Coder { void code(); }
  interface Tester { void test(); }
  interface Documenter { void writeDocument(); }
  // JuniorDev implements Coder, Tester — only what it actually does
  ```
- **In machine coding**: If your `Vehicle` interface has `fly()`, `sail()`, `drive()` and a `Car` has to implement `fly()` as no-op — that's an ISP violation. Split into `Flyable`, `Drivable`, `Sailable`.
- **Connection to SRP**: SRP is about classes, ISP is about interfaces — same idea, different level.

### 2.5 Dependency Inversion Principle (DIP)
- **Rule**: High-level modules should not depend on low-level modules. Both should depend on abstractions.
- **The violation**:
  ```
  class OrderService {
      private MySQLDatabase db = new MySQLDatabase();  // tightly coupled to MySQL
      void placeOrder(Order o) { db.insert(o); }
  }
  // Switching to PostgreSQL means changing OrderService — it shouldn't care about DB choice
  ```
- **The fix**: Depend on an interface, inject the implementation
  ```
  class OrderService {
      private Database db;  // depends on abstraction
      OrderService(Database db) { this.db = db; }  // injected from outside
  }
  // Now works with MySQL, Postgres, InMemoryDB — OrderService doesn't know or care
  ```
- **Constructor injection** — pass dependencies through the constructor. This is the most common form in machine coding rounds. Don't use `new` inside classes for dependencies.
- **Why DIP matters in interviews**: It makes your code testable (inject a mock DB for tests) and extensible (swap implementations without touching business logic).

---

### How SOLID Shows Up in Machine Coding Rounds

| Principle | How evaluator tests it | What they want to see |
|-----------|----------------------|----------------------|
| SRP | "Add email notifications for booking" | You create a new NotificationService, not add email logic to BookingService |
| OCP | "Now support a new vehicle type / payment method" | You add a new class, not modify existing if-else |
| LSP | "What if some spots don't support all vehicles?" | You don't force-fit a subclass that breaks the parent's contract |
| ISP | "Not all users can do all actions" | Your interfaces are granular, not god-interfaces |
| DIP | "How would you test this?" | Your classes take dependencies via constructor, not hardcoded `new` |
