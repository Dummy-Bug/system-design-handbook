# What Is A State Machine

## The Problem It Solves

> [!info] Without rules, any part of your code can put an entity into any state. A state machine makes illegal transitions impossible.

Consider a taxi ride. It goes through a lifecycle:

```
User requests ride    → REQUESTED
Driver accepts        → MATCHED
Ride starts           → IN_PROGRESS
Ride ends             → COMPLETED
```

Without a state machine, nothing stops this:

```
Cancel a COMPLETED ride   → status = CANCELLED  ✗ nonsense
Start an IN_PROGRESS ride → status = IN_PROGRESS ✗ already there
Complete a REQUESTED ride → status = COMPLETED  ✗ never even started
```

Your system needs rules. A state machine is those rules.

---

## The Definition

> [!info] A state machine is three things:
> 1. A finite set of states an entity can be in
> 2. Events that trigger transitions
> 3. Rules about which transitions are valid from which states

```
States:       REQUESTED, MATCHED, IN_PROGRESS, COMPLETED, CANCELLED
Event:        driver accepts ride
Transition:   REQUESTED → MATCHED   ✓ valid
              COMPLETED → MATCHED   ✗ invalid — ride is over
```

At any moment, the entity is in **exactly one state**. Not two. Not between states. One.

---

## The Taxi Ride Example

```
                    driver accepts
REQUESTED ──────────────────────────→ MATCHED
    │                                     │
    │ user cancels                        │ driver cancels
    ↓                                     ↓
CANCELLED                            CANCELLED
                                         │
                                         │ ride starts
                                         ↓
                                    IN_PROGRESS
                                         │
                              ┌──────────┴──────────┐
                              │                     │
                         ride ends            user cancels
                              ↓                     ↓
                         COMPLETED            CANCELLED
```

Every arrow is a valid transition. Everything not shown is illegal.

---

## Connection to LLD State Pattern

> [!tip] If you've studied the State design pattern in LLD — this is the same concept, just applied at a different layer.

```
LLD State Pattern      → states live in code as classes
                         object changes behaviour based on state
                         e.g. vending machine behaves differently
                              in IDLE vs DISPENSING vs OUT_OF_STOCK

System Design          → states live in a database column
                         transitions validated before writing
                         e.g. rides.status = 'REQUESTED' | 'MATCHED' | ...
```

Same idea — one entity, finite states, controlled transitions.

The difference: in system design, **multiple servers** might try to transition the same entity simultaneously. That's where it connects to concurrency, locking, and transactions — covered in the next files.
