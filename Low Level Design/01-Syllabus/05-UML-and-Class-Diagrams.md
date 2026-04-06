## Phase 5 — UML & Class Diagrams

> LLD relevance: In machine coding rounds at Flipkart and Rippling, you often sketch a class
> diagram before writing code. It's your blueprint. You don't need full UML mastery —
> just enough to communicate your design clearly in 3-5 minutes.

---

### 5.1 Class Diagram Basics
- **A box per class** — three sections: class name | fields | methods
  ```
  ┌────────────────────────┐
  │       ParkingSpot       │
  ├────────────────────────┤
  │ - spotId: String        │
  │ - type: SpotType        │
  │ - vehicle: Vehicle      │
  │ - isOccupied: boolean   │
  ├────────────────────────┤
  │ + park(v: Vehicle): bool│
  │ + unpark(): Vehicle     │
  │ + isAvailable(): bool   │
  └────────────────────────┘
  ```
- **Access modifiers**: `+` public, `-` private, `#` protected, `~` package-private
- **Static members**: Underlined or prefixed with `<<static>>`
- **Abstract class/method**: Name in *italics* or prefixed with `<<abstract>>`
- **Interface**: Prefixed with `<<interface>>`

### 5.2 Relationships — The Only 5 You Need

#### Association (uses / knows about)
- `Driver ——→ Vehicle` — Driver knows about Vehicle
- Solid line with arrow — one class holds a reference to another
- Most common relationship — start here if unsure

#### Aggregation (has-a, can exist independently)
- `ParkingLot ◇——→ ParkingFloor` — lot has floors, but floors could conceptually exist without the lot
- Open diamond on the "whole" side
- **Weak ownership** — the part's lifecycle is independent

#### Composition (has-a, cannot exist independently)
- `ParkingFloor ◆——→ ParkingSpot` — floor has spots, spots don't exist without the floor
- Filled diamond on the "whole" side
- **Strong ownership** — if the whole is destroyed, parts are destroyed too
- **When evaluators care**: If you delete a `ChatRoom`, are the `Message` objects deleted? If yes = composition. If messages persist in user history = aggregation.

#### Inheritance (is-a)
- `Car ——▷ Vehicle` — Car extends Vehicle
- Solid line with hollow triangle pointing to parent
- Use sparingly — evaluators penalize deep inheritance trees

#### Implementation (implements interface)
- `HourlyPricing - - -▷ PricingStrategy` — implements the interface
- Dashed line with hollow triangle pointing to interface

### 5.3 Multiplicity
- `1` — exactly one
- `0..1` — zero or one (optional)
- `*` or `0..*` — zero or many
- `1..*` — one or many (at least one)
- Example: `ParkingFloor 1 ◆——→ * ParkingSpot` — one floor has many spots

### 5.4 How to Sketch a Class Diagram in an Interview (5 minutes)

**Step 1 — Identify nouns from requirements** (2 min)
- Read the problem. Underline every noun. Each noun is a candidate class.
- Parking Lot → `ParkingLot`, `ParkingFloor`, `ParkingSpot`, `Vehicle`, `Ticket`, `Payment`

**Step 2 — Identify relationships** (1 min)
- Which class "has" which? (composition/aggregation)
- Which class "is-a" subtype? (inheritance)
- Which class "uses" which? (association)

**Step 3 — Assign key fields and methods** (2 min)
- Don't list every getter/setter — only the important domain methods
- `ParkingSpot.park(vehicle)`, `ParkingLot.findAvailableSpot(vehicleType)`, `Ticket.calculateFee()`

**Do NOT draw a perfect UML diagram.** A clear sketch on paper/whiteboard with boxes and arrows is enough. Evaluators care about the right classes and relationships, not UML syntax.

### 5.5 Sequence Diagrams (Know But Don't Over-invest)
- Shows the flow of method calls between objects over time
- Useful for explaining: "User presses park → ParkingLot calls SpotManager.findSpot() → SpotManager returns spot → ParkingLot creates Ticket → returns Ticket to User"
- Draw only if the interviewer asks "walk me through the flow" — otherwise the class diagram + code is enough

### 5.6 Common Mistakes in Diagrams
- **God class** — one class with 15 methods doing everything. Break it up.
- **Missing interfaces** — if two classes can be swapped (pricing strategies), there should be an interface
- **Arrows pointing wrong way** — association arrow points FROM the class that holds the reference TO the class it references
- **Too many classes too early** — start with 4-5 core classes. Add more as the design evolves. You can always split later.
