# Pessimistic Locking

## What it is

> [!info] Pessimistic locking assumes conflict WILL happen. Lock the resource before anyone touches it — only one transaction can proceed at a time.

**When to use:** High contention — thousands of users fighting for the same resource simultaneously. Hotel booking on New Year's Eve. Flash sale last item.

---

## How It Works

```
User A clicks Book Now
  → acquires lock on room row (SELECT FOR UPDATE)
  → reads availability: 1 room left
  → books the room
  → writes: availability = 0
  → releases lock

User B clicks Book Now (same moment)
  → tries to acquire lock
  → lock held by A → B waits...
  → A releases lock
  → B acquires lock
  → reads availability: 0
  → "sorry, no rooms available"
  → releases lock
```

No race condition. No double booking. Guaranteed.

**In SQL:**
```sql
BEGIN;
SELECT * FROM rooms WHERE id = 1 FOR UPDATE;  -- acquires lock
-- do your logic
UPDATE rooms SET available = 0 WHERE id = 1;
COMMIT;  -- releases lock
```

---

## Deadlocks

The danger of pessimistic locking — two transactions waiting for each other forever.

```
User A locks Room 1, needs Room 2
User B locks Room 2, needs Room 1

A waits for B to release Room 2
B waits for A to release Room 1

Circular dependency → both wait forever → deadlock
```

### Prevention 1 — Lock Ordering

Always acquire locks in the same global order, regardless of what you need.

```
Rule: always lock by room number ascending

User A needs Room 1 and 2 → locks: Room 1 → Room 2
User B needs Room 2 and 3 → locks: Room 2 → Room 3

User A locks Room 1 ✓
User B locks Room 2 ✓
User A tries Room 2 → B holds it → A waits
User B locks Room 3 ✓ → B finishes → releases Room 2 and 3
User A acquires Room 2 ✓ → A finishes

No circular dependency → no deadlock
```

> [!important] Lock ordering works because someone always makes progress
> Deadlock requires circular waiting — A waits for B, B waits for A. With ordering, B never waits for A — B moves forward and finishes. No circle.

### Prevention 2 — Timeout

If a lock isn't acquired within X seconds, give up and retry.

```
User A waiting for Room 2 → timeout after 5 seconds
→ releases Room 1
→ retries entire transaction from scratch

Deadlock broken automatically — no circular wait possible forever
```

> [!tip] Use both together
> Lock ordering prevents deadlocks when you know what you need upfront. Timeouts are the safety net for cases where ordering isn't possible or known in advance.

---

## The Cost of Pessimistic Locking

> [!warning] Every request pays the lock cost — even when there's no contention

```
1000 users updating their own profile bio (low contention)
Each request: acquire lock → do work → release lock
Lock acquisition = database overhead on every single request
At 100k requests/second → massive unnecessary overhead
```

Pessimistic locking is the right tool for high contention. For low contention, it's expensive overkill — use optimistic locking instead.
