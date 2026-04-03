# ACID Properties

## What ACID Is

> [!info] ACID = the four guarantees a database transaction must provide to be considered reliable. These are the *why* behind isolation levels.

Every time you do a `BEGIN ... COMMIT` in a database, ACID defines what you're guaranteed.

---

## The Four Properties

### A — Atomicity

> All or nothing. A transaction either completes fully or not at all. No partial states.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;  -- debit
UPDATE accounts SET balance = balance + 500 WHERE id = 2;  -- credit
COMMIT;
```

If the system crashes between the two updates — atomicity ensures both are rolled back. You never end up with money debited but not credited.

```
Without atomicity:
  Debit completes → crash → credit never happens → $500 disappears

With atomicity:
  Crash → both operations rolled back → balance unchanged
  User sees: transaction never happened
```

---

### C — Consistency

> The database moves from one valid state to another valid state. Constraints are never violated.

```sql
-- DB constraint: balance >= 0
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;  -- balance was $500
-- This would make balance = -$500 → violates constraint
COMMIT;  -- FAILS → entire transaction rolled back
```

Consistency ensures integrity constraints (foreign keys, unique constraints, check constraints) are respected. A transaction that would violate them is rejected entirely.

---

### I — Isolation

> Concurrent transactions don't interfere with each other. Each transaction sees the database as if it's running alone.

This is the property that isolation levels control — **how much isolation** is enforced.

```
Full isolation (SERIALIZABLE):
  Transaction A and B running concurrently
  → each sees the DB as if it's the only one running
  → no dirty reads, no phantoms, no lost updates

Less isolation (READ COMMITTED):
  Some interference allowed
  → better performance, some anomalies possible
```

> [!important] Isolation levels are the knob that controls how strictly "I" is enforced.
> More isolation = safer but slower. Less isolation = faster but more anomalies possible.
> See `02-Isolation-Levels.md` for the full breakdown.

---

### D — Durability

> Once committed, data survives crashes, power loss, and failures.

```
Transaction commits at 10:00:00
Power cuts at 10:00:01

Without durability → data lost
With durability    → data on disk via WAL → survives → recovered on restart
```

Durability is implemented via Write-Ahead Log (WAL) — covered in full in `07-Durability/02-WAL.md`.

---

## ACID vs BASE

> [!important] ACID and BASE are opposite ends of the consistency spectrum

| | ACID | BASE |
|---|---|---|
| **Stands for** | Atomicity, Consistency, Isolation, Durability | Basically Available, Soft state, Eventually consistent |
| **Used in** | Relational DBs (PostgreSQL, MySQL) | NoSQL, distributed systems (Cassandra, DynamoDB) |
| **Consistency** | Strong — always valid state | Eventual — converges over time |
| **Availability** | May sacrifice for consistency | Prioritizes availability |
| **Use when** | Financial data, transactions, correctness critical | High scale, availability critical, staleness acceptable |

```
Payment system  → ACID (PostgreSQL, SERIALIZABLE)
Social feed     → BASE (Cassandra, eventual consistency)
Bank transfer   → ACID (can't lose money)
Like counter    → BASE (off by a few is fine)
```

> [!tip] Deep dive on ACID in distributed databases (Spanner, CockroachDB) → Phase 4 (Storage & Databases)

---

## Why ACID Matters for Isolation Levels

Isolation levels are the database's way of letting you tune the **I** in ACID:

```
SERIALIZABLE     → full I — transactions completely isolated
REPEATABLE READ  → slightly relaxed I — phantoms possible (textbook)
READ COMMITTED   → more relaxed I — non-repeatable reads possible
READ UNCOMMITTED → I almost gone — dirty reads possible
```

Choosing an isolation level = choosing how strictly you want the Isolation guarantee enforced, trading it against performance.
