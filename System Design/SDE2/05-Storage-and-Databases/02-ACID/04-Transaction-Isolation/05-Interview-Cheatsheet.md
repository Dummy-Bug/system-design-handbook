# Interview Cheatsheet — Transaction Isolation Levels

> [!question] When does isolation come up in an interview?
> When you design any system where two users touch the same data. The interviewer will ask "how do you prevent inconsistent reads?" or "what isolation level do you use?" — this cheatsheet is your answer.

---

## The Four Problems

| Problem | What happens | Trigger |
|---|---|---|
| Dirty Read | Read uncommitted data that gets rolled back | No read isolation |
| Non-Repeatable Read | Same row, different value within one transaction | Another transaction committed between your reads |
| Phantom Read | New rows appear or disappear within one transaction | Another transaction inserted or deleted between your reads |
| Lost Update | One write silently overwrites another | Write-write conflict — both read the same committed value, both write |

---

## The Levels — What Each Prevents

| Level | Dirty Read | Non-Repeatable | Phantom | Lost Update | Default for |
|---|---|---|---|---|---|
| READ COMMITTED | ✅ | ❌ | ❌ | ❌ | PostgreSQL, Oracle |
| REPEATABLE READ (snapshot) | ✅ | ✅ | ✅ | ❌ | MySQL |
| SERIALIZABLE | ✅ | ✅ | ✅ | ✅ | — (explicit choice) |

> [!important] Say "snapshot isolation" not just "REPEATABLE READ"
> PostgreSQL's REPEATABLE READ = snapshot isolation. You get phantom read protection even though the textbook says you shouldn't. Say this in interviews — it shows you know what databases actually implement.

> [!warning] REPEATABLE READ does NOT prevent lost updates on its own.
> You need either `SELECT FOR UPDATE` (pessimistic lock) or SERIALIZABLE to stop a write-write conflict.

---

## Moment 1 — "What isolation level do you use?"

> [!tip] Always state your assumption first — the answer changes depending on whether you have explicit locking in place.

```
With SELECT FOR UPDATE (pessimistic locking):
  → REPEATABLE READ is sufficient
  → explicit lock prevents the lost update
  → snapshot isolation ensures consistent reads throughout the transaction

Without explicit locking:
  → SERIALIZABLE is required
  → DB tracks dependencies and detects conflicts automatically
  → forces one transaction to retry on conflict
```

---

## Moment 2 — "How do you prevent double booking?"

> [!tip] Two valid options — name both and state your tradeoff.

**Option A — REPEATABLE READ + SELECT FOR UPDATE**

```sql
BEGIN;
SELECT * FROM rooms WHERE id = 1 FOR UPDATE;
UPDATE rooms SET available = false WHERE id = 1;
COMMIT;
```

- Explicit lock prevents double booking (lost update)
- Snapshot isolation gives consistent reads throughout
- Better performance — targeted row lock, no system-wide tracking
- Risk: every developer must remember `FOR UPDATE` on every critical path

**Option B — SERIALIZABLE**

```sql
BEGIN;
SELECT * FROM rooms WHERE id = 1;
UPDATE rooms SET available = false WHERE id = 1;
COMMIT;
```

- DB detects the write-write conflict automatically via SSI
- No developer error possible — no lock to forget
- Slower — system-wide dependency tracking + retry on conflict

---

## Moment 3 — "Why use SERIALIZABLE if locking achieves the same thing?"

> [!tip] Frame it as a safety net against human error, not a technical superiority.

```
REPEATABLE READ + SELECT FOR UPDATE
  → correct only if every developer adds FOR UPDATE on every critical path
  → one missed FOR UPDATE = race condition = money lost or double booking

SERIALIZABLE
  → DB enforces correctness automatically
  → no developer error possible
  → worth the performance cost for smaller teams or when stakes are highest
```

---

## The Combination Guide

| System               | Isolation Level | Locking           | Why                                     |
| -------------------- | --------------- | ----------------- | --------------------------------------- |
| View counter         | READ COMMITTED  | None              | Slight inaccuracy acceptable            |
| Social feed          | READ COMMITTED  | None              | Eventual consistency fine               |
| Audit report         | REPEATABLE READ | None              | Consistent snapshot across all reads    |
| Hotel booking        | REPEATABLE READ | SELECT FOR UPDATE | Lock prevents double booking            |
| Hotel booking        | SERIALIZABLE    | None              | If not using explicit locking           |
| Payment (high scale) | REPEATABLE READ | SELECT FOR UPDATE | Performance at Stripe-level traffic     |
| Payment (safety net) | SERIALIZABLE    | None              | DB guarantees correctness automatically |
|                      |                 |                   |                                         |
|                      |                 |                   |                                         |
|                      |                 |                   |                                         |

> [!danger] Never combine SERIALIZABLE + SELECT FOR UPDATE
> SERIALIZABLE already prevents lost updates via SSI. Adding SELECT FOR UPDATE on top pays twice for the same guarantee with no benefit.

---

## Full Checklist

- [ ] Named the specific isolation level and justified the choice
- [ ] Stated whether explicit locking is in place — changes the answer
- [ ] Said "snapshot isolation" when discussing REPEATABLE READ
- [ ] Explained which problems the chosen level prevents
- [ ] Mentioned the performance tradeoff of SERIALIZABLE
- [ ] For payments: explained why SERIALIZABLEand a exists even when locking achieves the same result
