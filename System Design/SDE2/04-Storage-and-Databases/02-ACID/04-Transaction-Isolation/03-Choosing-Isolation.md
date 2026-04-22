# Choosing the Right Isolation Level

> [!abstract] Isolation level is not picked in isolation — it works together with your locking strategy. The right combination gives you the safety you need at the lowest performance cost.

---

## The Decision Framework

```
What problems can occur in this system?
  ↓
What's the cost if they occur?
  ↓
Do I have explicit locking (SELECT FOR UPDATE) in place?
  ↓
Pick the lowest isolation level that — combined with locking — prevents all critical problems
```

---

## Case 1 — View Counter

```
Problem possible: Lost update (two servers increment simultaneously)
Cost of problem:  View count off by a few → nobody cares
```

**Choice: READ COMMITTED** — or even eventual consistency (async increment via queue).

```sql
-- Don't even use transactions — just fire and forget
UPDATE videos SET views = views + 1 WHERE id = 123;
-- If a few increments are lost under high load → acceptable
```

> [!tip] For high-volume counters, accuracy matters less than throughput. Use Redis INCR instead of a DB transaction.

---

## Case 2 — Hotel Booking

```
Problem possible: Lost update → double booking
Cost of problem:  Two guests show up for same room → serious business problem
```

**Two valid approaches — both correct, different tradeoffs:**

**Option A — REPEATABLE READ + Pessimistic Locking:**
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
SELECT * FROM rooms WHERE id = 1 FOR UPDATE;  -- explicit lock
-- Check availability
UPDATE rooms SET available = false WHERE id = 1;
COMMIT;
```
- Developer explicitly locks the row — prevents the lost update (double booking)
- Snapshot isolation gives a consistent read view throughout the transaction — you won't see a different value for the same row mid-transaction
- Better performance than SERIALIZABLE
- Risk: developer must remember to add `FOR UPDATE` on every critical path

**Option B — SERIALIZABLE:**
```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
SELECT * FROM rooms WHERE id = 1;  -- no explicit lock needed
UPDATE rooms SET available = false WHERE id = 1;
COMMIT;
-- DB detects conflict automatically, forces retry
```
- DB handles everything — no developer error possible
- Slower, more overhead
- Simpler code

> [!important] The right answer depends on your assumption
> If you state "I'm using pessimistic locking" → REPEATABLE READ is sufficient.
> If you're not using explicit locking → SERIALIZABLE is required.
> Always state your assumption in an interview.

---

## Case 3 — Bank Transfer / Payment

```
Problem possible: Lost update → money disappears
Cost of problem:  Financial loss, legal liability, trust destroyed
```

**Three options — pick based on team and scale:**

**Option 1 — SERIALIZABLE (safest, simplest):**
```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- DB prevents all four problems automatically
-- No developer error possible
-- Use for smaller teams or lower-volume payment systems
```

**Option 2 — REPEATABLE READ + SELECT FOR UPDATE (performant):**
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
SELECT balance FROM accounts WHERE id = 123 FOR UPDATE;
-- compute new balance
UPDATE accounts SET balance = 1500 WHERE id = 123;
COMMIT;
-- Explicit lock prevents lost update
-- Better performance at scale (Stripe-level traffic)
```

**Option 3 — SERIALIZABLE + SELECT FOR UPDATE (redundant):**
```
❌ Avoid — paying twice for the same guarantee
   SERIALIZABLE already prevents lost updates
   SELECT FOR UPDATE on top adds overhead with no benefit
```

> [!tip] Real world
> Stripe and similar payment companies use **REPEATABLE READ + explicit locking** — senior engineers who know what they're doing, need the performance at scale. Smaller teams → SERIALIZABLE as a safety net.

---

| System | Isolation Level | Locking | Reason |
|---|---|---|---|
| View counter | READ COMMITTED | None | Slight inaccuracy acceptable |
| Social feed | READ COMMITTED | None | Eventual consistency fine |
| Audit report | REPEATABLE READ | None | Consistent snapshot across reads |
| Hotel booking | REPEATABLE READ | SELECT FOR UPDATE | Snapshot + explicit row lock |
| Hotel booking | SERIALIZABLE | None | If no explicit locking in place |
| Payment (high scale) | REPEATABLE READ | SELECT FOR UPDATE | Performance at Stripe-level traffic |
| Payment (safety net) | SERIALIZABLE | None | DB guarantees correctness automatically |

---

> [!important] Isolation levels and locking solve the same problems at different layers

```
Lost Update prevention:
  Via locking:     SELECT FOR UPDATE → pessimistic lock → one writer at a time
  Via isolation:   SERIALIZABLE → DB detects conflict → forces retry

Both work. Locking is explicit and performant. SERIALIZABLE is automatic and foolproof.
The right choice depends on team size, scale, and risk tolerance.
```
