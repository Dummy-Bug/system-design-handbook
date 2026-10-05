> [!abstract] Parking Lot
> Flavor A (domain modeling) · Target: 90 min from a blank editor · Patterns: Singleton, Strategy, Factory, Observer

---

## 📄 Problem Statement

Design a parking lot for a mall.

The lot has **multiple floors**, and each floor has **spots of different sizes**. A vehicle drives up to an entry gate, is assigned a spot, and receives a **ticket**. When it leaves, the fee is calculated from the time parked and the vehicle's type, the driver pays at the exit gate, and the spot is released.

Several entry gates operate at once, so two vehicles can arrive at the same instant.

---

## 🔍 FR, NFR or design: sorting what gets said in the first ten minutes

Every line said while clarifying lands in one of three buckets. Putting a line in the wrong bucket is how a requirements list ends up naming classes before any class exists, or promising behaviour the build never delivers. Two questions sort every line.

```mermaid
flowchart TD
    L[A line about the system] --> Q1{Could a person using or running<br/>the lot ever notice it?}
    Q1 -- no --> D[Design decision<br/>lives in the callout of the class it decides]
    Q1 -- yes --> Q2{What the lot does,<br/>or how well it does it?}
    Q2 -- what it does, for one car --> F[Functional requirement]
    Q2 -- how well: many at once,<br/>how fresh, how easy to change --> N[Non-functional requirement]
    classDef d fill:#fde2e2,stroke:#c0392b,color:#000
    classDef f fill:#dff5e1,stroke:#27ae60,color:#000
    classDef n fill:#e3ecfb,stroke:#2e6fd8,color:#000
    class D d
    class F f
    class N n
```

**Question 1 filters out design.** The people who can notice things are the driver (the gate, the ticket in hand, the spot they are sent to, the bill), the next driver, the admin reading the display, and the owner asking for a change. If none of them could ever tell the difference, the line is about how the code is built, not about the lot.

**Question 2 splits what is left.** What happens when one car arrives or leaves is functional. Whether that still holds when many cars arrive at once, how fresh a number has to be, and how cheaply a rule can be changed later are non-functional: qualities of the system rather than things it does.

| Line | Who could notice it | Bucket |
|---|---|---|
| A bike is sent to the smallest free spot it fits in | the biker, reading the spot on the ticket | **FR** |
| Floors are stored in a `Map` | nobody: a `List` sends the biker to the same spot | **Design** |
| `Spot.tryOccupy()` is `synchronized` | nobody directly | **Design** |
| Two gates at the same instant never get the same spot | the second driver, finding a car in their spot | **NFR** (many at once) |
| The spot is freed only after payment succeeds | the next driver, sent to a spot that still has a car in it | **FR** |
| A full lot returns `Optional.empty()` instead of throwing | nobody: the driver sees the same rejection either way | **Design** |
| The availability count may be a few seconds stale | the admin | **NFR** (freshness) |
| A weekend flat rate can be added without touching park and unpark | the owner, asking for the change | **NFR** (ease of change) |

> [!tip] One topic, two buckets, two different claims
> Pricing appears as FR5 and again in NFR3, and that is not a duplicate. FR5 states **today's** rule, which the driver reads on the bill. NFR3 states that **tomorrow** a different rule can be added without changing the parking flow, which only the owner asking for the change ever notices. Allocation splits the same way: FR3 is the rule in use, NFR3 is the freedom to swap it.

---

## ✅ Functional Requirements

1. **Floors.** A lot has multiple floors, each with a configurable number of spots.
2. **Spot sizes.** A spot is `SMALL`, `MEDIUM` or `LARGE`.
3. **Vehicles and fitting.** The lot supports bikes, cars and trucks. A vehicle gets the **smallest free spot it fits in, across the whole lot**; a bigger spot is used only when no spot of its own size is free anywhere.
4. **Ticket on entry.** The lot issues a ticket carrying a ticket id, the allocated spot and the entry time.
5. **Fee on exit.** The fee is computed from the time parked, rounded up to the hour, and the vehicle type. No exit until payment succeeds.
6. **Release on payment.** The spot becomes free **only when payment succeeds**. A declined payment leaves the ticket active and the spot occupied.
7. **No compatible spot.** Entry is rejected when no spot the vehicle fits in is free. Not when the lot is full: with every `LARGE` spot taken and forty `SMALL` spots free, a truck is still rejected.
8. **Exit validation.** Exit is rejected for an unknown ticket or a ticket that has already been paid.
9. **Gates.** The lot has several entry gates and several exit gates.
10. **Availability.** The admin sees free spot counts per floor and per size.

> [!question] FR3 is a clarifying question, not an assumption
> Interviewers do not share one rule here; some mean smallest compatible spot, some mean nearest floor. Ask, then commit out loud:
> > Should a bike stay on the floor it entered, or should we protect the big spots across the whole lot? I will default to the smallest compatible spot anywhere in the lot, so trucks are not turned away while bikes sit in large spots.

## ⚙️ Non-functional Requirements

1. **Concurrency.** With several gates working at the same instant, a spot is never given to two vehicles, and a ticket is paid at most once.
2. **Freshness.** The admin's availability count may be slightly stale. Locking the whole lot to count it would make every gate wait for the count.
3. **Ease of change.** A new pricing rule or a new allocation rule can be added without changing the parking flow.

### Out of scope (do not build)

Advance reservations · real payment gateway · multi-lot · pricing by floor · exit-gate barriers.


## 🔩 Classes

Every class below owns exactly one thing. If you can't say what a class owns in one sentence,
it shouldn't exist — that test alone kills most of the clutter people add under time pressure.

We build bottom-up: fixed values first, then dumb containers, then the classes with logic.

### Enums

#### `SpotSize` — the ranking

> *"Classify parking spots by size and match them with appropriate vehicles"*

`SMALL, MEDIUM, LARGE`. This is the only place in the system where sizes are ordered, and the **declaration order is the ordering** — `ordinal()` gives us `SMALL < MEDIUM < LARGE` for free.

That ordering is what makes "a bike may use a car spot" expressible in code. Without a rank,`BIKE` and `CAR` are just two unrelated labels and no loop can walk from one to the other.

#### `VehicleType` — identity, plus the size it needs

> *"Support multiple vehicle types, including bikes, cars, and trucks"*

`BIKE, CAR, ELECTRIC_CAR, TRUCK`, each constant carrying the minimum `SpotSize` it fits in.
Many types collapse onto one size: `CAR` and `ELECTRIC_CAR` are both `MEDIUM`.

> [!tip] Why not one enum for both, or a class per vehicle?
> **One enum** (`VehicleSize` doing double duty) works, and is what the AlgoMaster chapter does
> — but then vehicle identity has to live somewhere else, so it grows `Bike`/`Car`/`Truck`
> subclasses: three extra files that hold no behaviour.
> **Our version** keeps identity in the enum constant and size in a field, so it's one file
> instead of four. Both designs are correct; this one is smaller.
> What matters is the shared principle: **allocation is written in terms of size, never type.**
> That's why adding `MINI_TRUCK` is one constant and zero edits to the search loop.

#### `SpotStatus`

`FREE, OCCUPIED`. Deliberately two values, and the missing third one is the decision.

> [!note] A lock is not a `LOCKED` status
> A held reservation — a `LOCKED` value plus a TTL plus a reaper to clean up abandoned holds —
> is only needed when there's a **human-sized gap** between claiming and confirming.
> BookMyShow has one: you pick seats, then spend four minutes entering card details, and you
> can't hold a mutex that long, so the hold has to become data.
> Parking has no gap. The car arrives and parks inside a single method call, microseconds apart.
> A mutex covers it, so `LOCKED` would buy nothing but a reaper you don't need.

### Data classes

#### `Vehicle`

A licence plate and a `VehicleType`. No behaviour, both fields final. It exists so that a plate
and its type travel together instead of being passed as two loose arguments.

#### `Ticket`

> *"Issue a parking ticket upon vehicle entry and track entry and exit times"*

Ticket id, the `Vehicle`, the assigned `Spot`, and the entry time. Created on entry; the exit
time is the only thing that changes later.

The `Spot` reference is the important field and it's the one people forget. Without it, exit
means scanning every floor for the spot holding this vehicle — 2,500 checks on a 5×500 lot,
every single time a car leaves. With it, exit is O(1).

### The classes with logic

#### `Spot`

An id, its `SpotSize`, its `SpotStatus`, and the one operation that matters:

`tryOccupy()` — `synchronized`, returns `boolean`. Checks free and marks occupied **as one
atomic step**, so two gates can never both win the same spot. Returning `false` rather than
throwing keeps a lost race on the normal path, where it belongs: two cars arriving together is
a Tuesday, not an exceptional condition.

> [!danger] The check-then-act race — why `tryOccupy()` exists
> ```java
> Spot s = findFree(size);      // both threads return S12   ← check
> s.setStatus(OCCUPIED);        // both write                 ← act
> ```
> `ConcurrentHashMap` does **not** fix this — each map call is individually safe, but the race
> spans two of them.
>
> **Lock per spot, not per lot.** Finding and claiming stay two steps, so the lot's search loop
> *is* the retry: when `tryOccupy()` returns `false`, it moves to the next candidate. Only the
> loser retries, and gates working on different spots never block each other.
> A single `synchronized` on `ParkingLot.park()` is also correct and simpler to write, but it
> serializes every entry in the building. Say which you chose and why.

> [!tip] Occupancy lives here, not on an association class
> Status splits onto an association (like `ShowSeat`) only when it varies over a **second
> dimension**. BookMyShow has time — one seat is free for the 6pm show and booked for the 9pm.
> Parking has only "now", so a plain field on `Spot` is correct.
> *Add advance reservations and that changes:* occupancy would move to a spot × time-window
> class. Name that in the interview; don't pre-build it.

> [!note] The spot does not hold the vehicle
> The ticket already links vehicle to spot. Storing it on the spot too means the same fact
> lives in two places and both must be updated on every exit.
> (The AlgoMaster chapter stores it, justified as "we need to know which vehicle is parked
> there to generate tickets" — but the lot creates the ticket and already holds the vehicle.)

#### `Floor`

> *"Support multiple parking floors, each with a configurable number of spots"*

A floor number and `Map<SpotSize, List<Spot>>`. It answers exactly one question:
**"do you have a free spot of *this exact size*?"**

The floor knows nothing about fitting rules, nothing about vehicles, and nothing about other
floors. That ignorance is the point — it's why the map can be keyed by size and looked up
directly instead of scanned.

> [!important] Whoever owns the data owns the code that builds it
> The constructor takes counts — `new Floor(1, 2, 2, 1)` — and fills its own map. It does **not**
> take a ready-made `Map<SpotSize, List<Spot>>` built by the caller.
> Hand-building that map in `Main` splits the knowledge: the driver would have to know the map
> has one bucket per size, how spot ids are formatted, and that a new spot starts `FREE`.
> Add `SpotSize.XL` for buses and you'd edit the enum *and* every caller that ever builds a floor.
> **The test that it landed in the right class: the caller's import list gets shorter.**
> `Main` should not import `SpotSize`, `SpotStatus`, `ArrayList`, or `Map` at all.

#### `ParkingLot` — the orchestrator

> *"Automatically assign parking spots based on availability"*

Singleton. Holds `Map<Integer, Floor>`, the active `PricingStrategy` and `AllocationStrategy`, and a `ConcurrentHashMap<String, Ticket>` of live tickets. Three operations: `park`, `unpark`, `displayAvailability`.

`park()` derives the vehicle's `minSize`, hands the floors to the `AllocationStrategy`, wraps the claimed spot in a `Ticket`, and stores it. Four lines: it **sequences**, it doesn't search. The fitting walk itself lives in `BestFitStrategy`: sizes from `minSize` upward, every floor asked the exact-size question for one size before moving to the next size, `tryOccupy()` on each candidate, moving on if another gate won it. Smallest-fits across the whole lot (FR3) falls out of that walk order.

Keeping the walk behind one interface is the whole reason a new vehicle type, or a new allocation policy, costs zero edits to the orchestrator.

> [!note] No compatible spot is a return value, not an exception
> `park()` returns `Optional.empty()` when nothing fits (FR7). A truck arriving when every large spot is taken is a normal Saturday afternoon, so it stays on the normal path; an exception would make the gate code catch something that is not exceptional.

> [!tip] Eager singleton, not double-checked locking
> `static final ParkingLot INSTANCE = new ParkingLot();` with a `private ParkingLot() {}`. The JVM guarantees class initialization runs once and is thread-safe, so no lock is needed. The chapter uses double-checked locking with `volatile`: more code, more ways to get it wrong, and pointless when construction is cheap. Use the holder idiom if it ever isn't.

> [!bug] The build left out the private constructor
> `ParkingLot.java` declares no constructor, so Java supplies a public one and `new ParkingLot()` compiles anywhere. Measured on a copy of the build: `new ParkingLot() == ParkingLot.getInstance()` printed `false`. With `private ParkingLot() {}` added, the same call fails to compile with `ParkingLot() has private access in ParkingLot`. The build in `ParkingLot/src` still has the bug; it is fixed in the Day 12 rebuild.

> [!bug] The build double-charges a ticket scanned at two exits at once
> The build's `unpark()` reads the ticket with `get()`, takes payment, and only then calls `remove()`. Two exit gates scanning the same ticket both pass the `get()` before either removes it: the same check-then-act race as `park()`, on the exit side. Measured on a copy of the build with a payment that takes 200 ms: both scans printed `paid 100.0` and the card was charged twice. The fix is under Key code; the build in `ParkingLot/src` still has the bug until the Day 12 rebuild.

#### `PricingStrategy` + `HourlyPricing`, `FlatRatePricing`

> *"Calculate fees based on duration, and support different pricing strategies"*

`calculatePrice(Ticket, exitTime) → double`. The trigger is NFR3: the interviewer has said pricing will change, and what pricing changes is a stock follow-up. An interface rather than a rate parameter, because the next rule has a different **shape**: hourly scales with duration, a flat weekend rate ignores duration entirely, so no single formula with a parameter can express both.

Each implementation holds its own config: `HourlyPricing` a rate, `FlatRatePricing` an amount. The lot **receives** a strategy; it never constructs one.

> [!bug] The build prices every vehicle the same
> FR5 prices by vehicle type, but the build has only `HourlyPricingStrategy` with one rate for all vehicles, and no `FlatRatePricing`. Per-type rates (a rate per `VehicleType`, read in `calculatePrice`) are a Day 12 rebuild target.

#### `PaymentProcessor`

`pay(amount) → boolean`, stubbed. It exists only so the failure path is real: the spot is freed
**only when this returns true**. Free it earlier and a declined card leaves a car sitting in a
spot the system believes is empty, and the next driver gets sent into it.

> [!note] Why `Payment` and `PaymentStatus` were cut
> A real gateway is out of scope, and a status enum with no transitions to protect is ceremony.
> A boolean is enough to exercise the only rule that matters here.

#### `AllocationStrategy` + `BestFitStrategy`, `FirstFitStrategy`

> *"Support multiple allocation policies"*

`allocate(floors, minSize) → Optional<Spot>`, returning a spot it has **already claimed**. `park()` delegates to it, so the orchestrator sequences and the strategy searches.

- `BestFitStrategy` (the default, and the one FR3 describes): sizes outer, floors inner. Every floor is asked for the smallest size before any floor is asked for the next size, so a bike never takes a car spot while a bike spot is free anywhere.
- `FirstFitStrategy` (the alternative): floors outer, sizes inner. The first floor with any fitting spot wins, so a bike stays on its floor and takes a car spot there rather than walking up a level.

> [!bug] The build shipped first-fit as the default, which breaks FR3
> Measured on a copy of the build, floor 1 with one `SMALL` spot and floor 2 with two: the second bike went to `1-MEDIUM-0` while floor 2 still had two `SMALL` spots free. With `BestFitStrategy` as the default the same run sends it to `2-SMALL-0`. The build in `ParkingLot/src` still defaults to first-fit until the Day 12 rebuild.

> [!tip] Why the interface is worth it
> Two reasons, and neither is that it demonstrates the code could be extended someday, which is the justification bar point 5 rejects. First, it **lifts the floor loop out of `park`**: the orchestrator shrinks to four lines instead of wrapping one class and removing nothing. Second, a requirement asks for it: NFR3 makes allocation swappable, and two real policies already exist. A lone interface that wraps one class and removes nothing is the over-engineering to avoid.

---

## 🧱 Class Diagram

```mermaid
classDiagram
    direction TB

    class ParkingLot {
        -Map~Integer, Floor~ floors
        -Map~String, Ticket~ activeTickets
        -PricingStrategy pricingStrategy
        -AllocationStrategy allocationStrategy
        +getInstance()$ ParkingLot
        +addFloor(Floor)
        +park(Vehicle) Optional~Ticket~
        +unpark(String, PaymentStrategy) double
        +displayAvailability()
    }
    class Floor {
        -int floorNumber
        -Map~SpotSize, Spot[]~ spots
        +claimFreeSpot(SpotSize) Optional~Spot~
        +claimSpotOfSize(SpotSize) Optional~Spot~
        +freeCountsBySize() Map
    }
    class Spot {
        -String id
        -SpotSize size
        -SpotStatus status
        +tryOccupy() boolean
        +release()
    }
    class Ticket {
        -String ticketId
        -Vehicle vehicle
        -Spot spot
        -Instant entryTime
        -Instant exitTime
    }
    class Vehicle {
        -String plate
        -VehicleType type
    }
    class VehicleType {
        <<enumeration>>
        BIKE, CAR, TRUCK
        -SpotSize minSize
    }
    class SpotSize {
        <<enumeration>>
        SMALL, MEDIUM, LARGE
    }
    class SpotStatus {
        <<enumeration>>
        FREE, OCCUPIED
    }
    class PricingStrategy {
        <<interface>>
        +calculatePrice(Ticket, Instant) double
    }
    class PaymentStrategy {
        <<interface>>
        +pay(double) boolean
    }
    class AllocationStrategy {
        <<interface>>
        +allocate(Collection~Floor~, SpotSize) Optional~Spot~
    }

    ParkingLot "1" o--> "*" Floor : floors
    ParkingLot --> PricingStrategy : receives, never builds
    ParkingLot --> AllocationStrategy : receives, never builds
    ParkingLot ..> PaymentStrategy : uses on exit
    Floor "1" o--> "*" Spot : by size
    Spot --> SpotSize
    Spot --> SpotStatus
    Ticket --> Spot : frees this on exit
    Ticket --> Vehicle
    Vehicle --> VehicleType
    VehicleType --> SpotSize : minSize
    AllocationStrategy ..> Floor : claims through
    PricingStrategy <|.. HourlyPricingStrategy
    PaymentStrategy <|.. CashPaymentStrategy
    AllocationStrategy <|.. FirstFitStrategy
    AllocationStrategy <|.. BestFitStrategy
```

---

## 🔑 Key code (the load-bearing bits — revise these, not the whole file)

**Size/type decoupling** — `VehicleType` carries its `minSize` as an enum-constructor field; the
fitting rule reads size, never type. Adding `MINI_TRUCK` is one constant, zero other edits.

```java
public enum VehicleType {
    BIKE(SpotSize.SMALL), CAR(SpotSize.MEDIUM), TRUCK(SpotSize.LARGE);
    private final SpotSize minSize;
    VehicleType(SpotSize minSize) { this.minSize = minSize; }
    public SpotSize getMinSize() { return minSize; }
}
```

**The concurrency answer** — `tryOccupy()` makes check-and-claim one atomic step, so two gates
can't win the same spot. The search loop *is* the retry: a lost race returns `false`, caller moves on.

```java
public synchronized boolean tryOccupy() {
    if (status == SpotStatus.FREE) { status = SpotStatus.OCCUPIED; return true; }
    return false;                       // someone beat me → caller tries next spot
}
public synchronized void release() { status = SpotStatus.FREE; }
```

**Smallest fit across the lot (FR3)**: `Floor` answers only the exact-size question; `BestFitStrategy` walks sizes from `minSize` upward and asks every floor at each size before going bigger. `ordinal()` gives the size ranking for free.

```java
// Floor: claim a free spot of EXACTLY this size
public Optional<Spot> claimSpotOfSize(SpotSize size) {
    for (Spot spot : spots.getOrDefault(size, List.of()))
        if (spot.tryOccupy()) return Optional.of(spot);
    return Optional.empty();
}

// BestFitStrategy: sizes outer, floors inner
public Optional<Spot> allocate(Collection<Floor> floors, SpotSize minSize) {
    for (SpotSize size : SpotSize.values()) {
        if (size.ordinal() < minSize.ordinal()) continue;
        for (Floor floor : floors) {
            Optional<Spot> spot = floor.claimSpotOfSize(size);
            if (spot.isPresent()) return spot;
        }
    }
    return Optional.empty();
}
```

**`park` sequences, doesn't search** — derives `minSize`, delegates to the `AllocationStrategy`,
wraps in a `Ticket`. `Optional.empty()` = no compatible spot free (FR7, a clean return, not an exception).

```java
public Optional<Ticket> park(Vehicle vehicle) {
    SpotSize minSize = vehicle.getType().getMinSize();
    Optional<Spot> spot = allocationStrategy.allocate(floors.values(), minSize);
    if (spot.isEmpty()) return Optional.empty();          // lot full
    Ticket ticket = new Ticket(vehicle, spot.get());
    activeTickets.put(ticket.getTicketId(), ticket);
    return Optional.of(ticket);
}
```

**`unpark`: claim the ticket first, release on success only** (FR6, FR8, NFR1). `remove()` on a `ConcurrentHashMap` is atomic and returns the ticket to exactly one caller, so a second scan of the same ticket gets `null` and is rejected. A declined payment puts the ticket back and leaves the spot `OCCUPIED`, because the car is still there.

```java
public double unpark(String ticketId, PaymentStrategy payment) {
    Ticket ticket = activeTickets.remove(ticketId);          // claim: only one exit gets it
    if (ticket == null)
        throw new IllegalArgumentException("Unknown or already-used ticket: " + ticketId);
    ticket.setExitTime(Instant.now());
    double fee = pricingStrategy.calculatePrice(ticket, ticket.getExitTime());
    if (!payment.pay(fee)) {
        activeTickets.put(ticketId, ticket);                 // declined: ticket active again
        throw new IllegalStateException("Payment failed for " + ticketId);
    }
    ticket.getSpot().release();                              // only on success
    return fee;
}
```

Measured on a copy of the build with this version (JDK 25):

```
--- same ticket scanned at two exits at once ---
rejected: Unknown or already-used ticket: T-3
paid 100.0
times card charged = 1
--- payment declined, then retried ---
declined -> Payment failed for T-4, spot 1-LARGE-0 is OCCUPIED
retry -> paid 100.0, spot is FREE
```

**Integer ceil pricing** — `(a + b - 1) / b`, min 1 hour, no floating point.

```java
long minutes = Duration.between(t.getEntryTime(), exitTime).toMinutes();
long hours = Math.max(1, (minutes + 59) / 60);   // ceil(minutes/60), min 1 hour
return hours * hourlyRate;
```

## 🎯 Strong-hire talking points (SDE-2, 3–4 YOE — say these out loud)

Researched against senior LLD rubrics. The build is at the bar; these are the *spoken* gaps that
separate hire from strong-hire — they cost zero code.

- **Deadlock-freedom.** The classic parking-lot deadlock is "car holds a floor lock *and* waits for
  a spot lock." We avoid it structurally: **only one lock is ever held — the spot's** (`tryOccupy`).
  No nested locks → no deadlock. Say this; it's the difference between "I used a lock" and "I
  reasoned about lock ordering."
- **The exit side has the same race.** Everyone guards `park()`; the probe is whether you also guard `unpark()`. Two exit gates scanning one ticket is check-then-act on the ticket map, and the cost is a double charge. Answer: claim the ticket with an atomic `remove()` before taking payment, and put it back if payment is declined.
- **Optimistic locking = the distributed answer.** Single-JVM uses `synchronized` per spot
  (pessimistic). Make it multi-node and that becomes a **version column + CAS**:
  `UPDATE spot SET status=OCCUPIED WHERE id=? AND version=?` — retry on 0 rows updated. Name this
  when asked "now make it distributed." (See [[CLAUDE#Concurrency control cheat-sheet]].)
- **Lock granularity, stated as a choice.** Per-spot lock (fine-grained, high throughput) vs one lock
  on the lot (simple, serializes every gate). We chose per-spot; say *why* — the lot lock makes two
  gates on different floors block each other for no reason.
- **Fair queue (if pushed on ordering).** If cars must be served first-come-first-served under
  contention, a fair `ReentrantLock(true)` or a request queue — name it, don't build it.
