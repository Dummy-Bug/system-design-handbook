# ACID — Interview Cheatsheet

---

## When to mention ACID

```
Payment, banking, financial ledger?     → ACID non-negotiable, justify why
Hotel / ticket / seat booking?          → Atomicity + Isolation critical (double booking)
E-commerce order + payment?             → Atomicity critical (charge without order)
"Why SQL over NoSQL here?"              → ACID guarantees
"How do you prevent double booking?"    → Isolation + constraints (consistency)
"What DB would you use?"                → mention ACID if correctness matters
```

---

## One-line definitions

> [!info] Atomicity
> All operations in a transaction succeed together, or none happen. No partial state ever persists. Implemented via WAL rollback.

> [!info] Consistency
> The database always moves from one valid state to another. Your constraints (balance ≥ 0, unique email, foreign keys) are enforced on every write.

> [!info] Isolation
> Concurrent transactions don't see each other's uncommitted changes. Each transaction runs as if it's the only one. Implemented via MVCC (snapshot per transaction).

> [!info] Durability
> Committed data survives crashes, power loss, anything. fsync() ensures the WAL is on disk before "success" is returned.

---

## The four anomalies (Isolation deep-dive)

| Anomaly | What happens | Prevented by |
|---|---|---|
| Dirty read | Read uncommitted data that may roll back | READ COMMITTED+ |
| Non-repeatable read | Same row returns different values in one transaction | REPEATABLE READ+ |
| Phantom read | Same query returns different rows in one transaction | SERIALIZABLE |
| Lost update | Two transactions overwrite each other's changes | FOR UPDATE lock or SERIALIZABLE |

---

## ACID vs BASE decision

| Use ACID when | Use BASE when |
|---|---|
| Financial data | Social feeds, likes, follower counts |
| Inventory / bookings | Analytics and metrics |
| Any partial failure = corruption | Write throughput > correctness requirement |
| Correctness is non-negotiable | Stale data is acceptable to the user |

---

## The C confusion — say this to be precise

> [!danger] C in ACID ≠ C in CAP
> C in ACID = constraint enforcement within one database (balance ≥ 0, unique emails)
> C in CAP = linearizability across distributed nodes (all nodes see the same value simultaneously)
> These are unrelated. In interviews, clarify which one you mean.

---

## The strong hire move

Don't just recite ACID. Show you know when to relax it:

> "I'd use PostgreSQL with full ACID guarantees for the payment and booking tables — partial failures there cause real financial errors. For the activity feed and like counts, I'd use Cassandra — the write volume is too high for fsync on every event, and a 100ms inconsistency window on a like count is invisible to users. Splitting ACID-critical from BASE-tolerant data into separate stores is standard at scale."
