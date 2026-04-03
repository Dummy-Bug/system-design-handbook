# Audit Trail vs Overwrite

## Option 1 — Overwrite The Status Column

> [!info] Every transition just updates the status column. Previous state is gone.

```
rides table
-----------
id  | status
1   | IN_PROGRESS    ← REQUESTED and MATCHED are gone
```

**What's good:**
- Simple — one row per entity
- Fast reads — current state is always right there
- Easy to query — `WHERE status = 'IN_PROGRESS'`

**What you lose:**
```
When did this ride get matched?        → no idea
How long was it in REQUESTED state?    → no idea
Who triggered the transition?          → no idea
Was this ride ever cancelled and re-requested? → no idea
```

No history. No audit. No debugging trail.

---

## Option 2 — Append An Event Row Per Transition

> [!info] Every transition writes a new row to an events table. Full history preserved.

```
ride_events table
-----------------
id | ride_id | from_state  | to_state    | triggered_by | timestamp
1  | 1       | REQUESTED   | MATCHED     | driver_456   | 10:00
2  | 1       | MATCHED     | IN_PROGRESS | driver_456   | 10:05
3  | 1       | IN_PROGRESS | COMPLETED   | system       | 10:45
```

Full lifecycle of every ride. You can answer every question overwrite can't.

**What you lose:**
- Getting current state = read the latest event row (slightly more complex)
- Table grows fast at scale

---

## Do Both — The SDE-2 Answer

> [!important] Maintain the status column for fast operational reads AND the events table for history. Write to both atomically.

```
rides table       → current status  (fast queries, operational use)
ride_events table → full history    (audit trail, debugging, analytics)
```

On every transition, write to both inside a single transaction:

```sql
BEGIN;

-- optimistic lock guard + state transition
UPDATE rides
SET status = 'MATCHED'
WHERE id = 1
AND status = 'REQUESTED';     ← 0 rows = illegal transition → ROLLBACK

-- audit trail
INSERT INTO ride_events (ride_id, from_state, to_state, triggered_by, timestamp)
VALUES (1, 'REQUESTED', 'MATCHED', 'driver_456', NOW());

COMMIT;
```

Either both succeed or neither does. The audit trail is never out of sync with the current status.

---

## Everything Composing Together

> [!important] This single transaction combines three concepts working together:

```
Optimistic locking   → WHERE status = 'REQUESTED' guards against concurrent transitions
State machine        → only valid transitions are applied
Atomicity            → both writes succeed or both fail — no partial state
```

```
Flow:
  UPDATE affects 0 rows → ROLLBACK → event never inserted → consistent
  UPDATE affects 1 row  → INSERT event → COMMIT → both written atomically
```

This is what interviewers mean when they say "think about edge cases." You're not just updating a column — you're composing locking, validation, and history tracking into one atomic operation.

---

## Connection To Event Sourcing

> [!tip] The events table approach is the beginning of event sourcing — a pattern where the event log IS the source of truth, and current state is derived from replaying events.
>
> At SDE-2 level: know it exists, know why someone would do it (full history, replayability, audit compliance).
> You don't need to design a full event sourcing system.
