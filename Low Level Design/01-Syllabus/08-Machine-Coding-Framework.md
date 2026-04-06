## Phase 8 — Machine Coding Interview Framework

> LLD relevance: This is HOW you execute. Knowing OOP and patterns isn't enough —
> you need to produce clean, working, extensible code in 60-90 minutes under pressure.
> This phase is the equivalent of Phase 9 in the System Design syllabus.

---

### 8.1 How the Round Works

| Company | Format | Time | What They Test |
|---------|--------|------|----------------|
| **Flipkart** | Machine coding on laptop/IDE | 90 min | Working code, extensibility, clean OOP |
| **Rippling** | Machine coding on laptop/IDE | 75-90 min | Working code, design patterns, testability |
| **Google** | OOD on whiteboard or doc | 45 min | Class design, relationships, key methods (less focus on compiling code) |
| **Amazon** | OOD on whiteboard | 45 min | Class design, LP connection ("tell me about a time...") |
| **Meta** | Less common, but system design can have LLD component | 45 min | API design + class structure |
| **Microsoft** | OOD on whiteboard or coding | 45-60 min | Class design, clean code |

**Flipkart and Rippling are the hardest** — they expect compiling, running code with driver/main method demonstrating all use cases.

### 8.2 What Evaluators Score

| Criteria | Weight | What They Look For |
|----------|--------|--------------------|
| **Working code** | 30% | Does it compile and run? Does the happy path work? |
| **Object modeling** | 25% | Right classes, right responsibilities, right relationships |
| **Extensibility** | 20% | Can a new requirement be added by adding a class, not modifying existing ones? |
| **Code quality** | 15% | Naming, method size, SRP, no code duplication |
| **Edge cases & validation** | 10% | Null checks, boundary conditions, error handling |

**The #1 mistake**: Spending 60 minutes on a perfect design and having no working code. **Working code with decent design >> perfect design with no code.**

### 8.3 The 90-Minute Playbook

#### Minutes 0-5: Read & Clarify
- Read the problem statement completely — don't start coding after reading 2 lines
- Ask clarifying questions (even if not interactive, write down assumptions):
  - What are the core use cases? (Park a vehicle, unpark, get fee)
  - What types/categories exist? (Vehicle types, spot types, user roles)
  - Any concurrency requirement?
  - Should I focus on a specific feature or build end-to-end?
- Write down 3-5 use cases as comments in your main file

#### Minutes 5-15: Identify Classes & Sketch Relationships
- List the nouns → candidate classes
- List the verbs → candidate methods
- Draw a quick class diagram (on paper or comments) — 5-6 core classes max
- Identify which patterns you'll use:
  - Multiple types of same thing → **Factory**
  - Behavior that varies → **Strategy**
  - State lifecycle → **State pattern or Enum**
  - Notification/events → **Observer**
- **Don't over-design** — start with the minimum classes needed for the core use case

#### Minutes 15-55: Implement Core Logic
- **Build in this order**:
  1. Enums and constants (VehicleType, SpotType, TicketStatus)
  2. Core model classes (Vehicle, ParkingSpot, Ticket)
  3. The main service/manager class (ParkingLotService)
  4. The happy-path flow (park → get ticket → unpark → get fee)
- **Get the happy path working first** — compiling and running beats perfect design
- Apply patterns as you go — don't force patterns that don't fit
- Keep methods small — if a method exceeds 15 lines, extract

#### Minutes 55-75: Handle Edge Cases & Extensions
- Add validation (spot already occupied, invalid vehicle type, ticket already paid)
- Add secondary use cases (get available spots count, find vehicle by plate number)
- If the problem states extension requirements, add one (new vehicle type, new pricing strategy)

#### Minutes 75-90: Demo & Polish
- Write a `Main.java` / `main.py` that demonstrates all use cases
- Print output that shows the system working
- Quick cleanup — remove dead code, fix naming
- **Don't add new features in the last 15 minutes** — polish what you have

### 8.4 Code Organization

```
src/
├── model/                   # Pure data classes and enums
│   ├── Vehicle.java
│   ├── VehicleType.java     # Enum
│   ├── ParkingSpot.java
│   ├── SpotType.java        # Enum
│   └── Ticket.java
├── service/                 # Business logic
│   ├── ParkingLotService.java
│   ├── PricingService.java
│   └── SpotAssignmentService.java
├── strategy/                # Strategy pattern implementations
│   ├── PricingStrategy.java         # Interface
│   ├── HourlyPricingStrategy.java
│   └── FlatRatePricingStrategy.java
├── factory/                 # Factory classes
│   └── VehicleFactory.java
├── exception/               # Custom exceptions
│   ├── SpotNotAvailableException.java
│   └── InvalidTicketException.java
└── Main.java                # Driver with demo use cases
```

**For time-constrained rounds (60 min)**: Put everything in 3-4 files. Don't spend 15 minutes creating directories. Organization matters less than working code.

### 8.5 Common Mistakes That Fail Candidates

| Mistake | Why It Fails You |
|---------|-----------------|
| No working code at the end | 0 on 30% of the scoring rubric |
| God class with 20 methods | Shows no understanding of SRP |
| `if-else` chains on type | Evaluator asks "add a new type" — you modify 5 files |
| No encapsulation | Public fields, no methods, logic in Main |
| Over-engineering | Abstract factory for one product, observer for one listener |
| No driver/main method | Evaluator can't see the system working |
| Hardcoded values | `if (hours > 3) price = 50` — put constants in a config or enum |
| Ignoring the problem statement | Building features that weren't asked for while missing core ones |

### 8.6 The "New Requirement" Test

At the 60-minute mark in Flipkart/Rippling rounds, the interviewer often adds:
- "Now support motorcycles" (new vehicle type)
- "Now add surge pricing on weekends" (new pricing strategy)
- "Now send an SMS when the lot is full" (new observer/notification)
- "Now support multiple parking lots" (scale from one instance to many)

**If your design is good**: You add 1 new class that implements an existing interface. No existing code changes.

**If your design is bad**: You modify 3-5 existing files, add if-else branches, and run out of time.

This single test separates pass from fail in most machine coding rounds.

### 8.7 Language-Specific Tips

#### Java (Most Common for LLD)
- Use `enum` liberally — type-safe, can have methods and fields
- Use `interface` for all strategy/behavior contracts
- Use `Optional<>` instead of returning null
- Use `Collections.unmodifiableList()` to return read-only views
- Override `toString()` on every model class — makes demo output readable

#### Python
- Use `@dataclass` for model classes — reduces boilerplate
- Use `ABC` (Abstract Base Class) for interfaces
- Use `Enum` from `enum` module
- Use type hints everywhere — `def park(self, vehicle: Vehicle) -> Ticket:`
- Use `__str__` for readable output

#### C++
- Use `virtual` methods for polymorphism
- Use `std::unique_ptr` / `std::shared_ptr` for ownership semantics
- Use `enum class` (scoped enums)
- Use `override` keyword explicitly
