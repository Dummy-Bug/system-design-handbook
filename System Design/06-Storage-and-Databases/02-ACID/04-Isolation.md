# Isolation

> [!info] Isolation — concurrent transactions execute as if they were running serially, one at a time. No transaction sees another's intermediate, uncommitted state.

---

## The guarantee

In a busy production database, thousands of transactions run simultaneously. Without isolation, they step on each other — one transaction reads data that another has half-written, leading to wrong results that look correct.

```
Transaction 1: Transfer $100 (Alice → Bob)
  Step 1: Deduct $100 from Alice  ← in progress, not yet committed
  Step 2: Add $100 to Bob         ← not yet done

Transaction 2: "What is Alice's balance?" ← runs simultaneously

Without isolation:
  Transaction 2 reads mid-transfer
  → Alice's balance already deducted but Bob not yet credited
  → dirty read: $400 shown, but the transaction might still roll back
  → wrong data served to the reporting system ✗

With isolation:
  Transaction 2 sees a snapshot from before Transaction 1 started
  → Alice's original balance shown ✓
  → Transaction 1's changes invisible until it fully commits
```

---

## The four anomalies isolation prevents

These are the specific things that go wrong when transactions interfere:

**Dirty Read** — reading uncommitted data from another transaction that might still roll back.
```
T1: updates Alice's balance to $400 (not yet committed)
T2: reads Alice's balance → sees $400
T1: rolls back → Alice's balance is actually still $500
T2: made a decision based on $400 that was never real ✗
```

**Non-Repeatable Read** — reading the same row twice in one transaction and getting different values because another transaction committed in between.
```
T1: reads Alice's balance → $500
T2: Alice transfers $100, commits
T1: reads Alice's balance again → $400
Same transaction, same query, different result ✗
```

**Phantom Read** — a query returns different rows when run twice because another transaction inserted or deleted rows in between.
```
T1: "how many bookings are there for room 101?" → 0 (room is free)
T2: books room 101, commits
T1: "how many bookings are there for room 101?" → 1
T1 tries to create a booking → double booking ✗
```

**Lost Update** — two transactions read the same value, both modify it, one overwrites the other's change.
```
T1: reads stock count → 10
T2: reads stock count → 10
T1: sets stock to 9 (sold one)
T2: sets stock to 9 (also sold one, but read stale value)
→ two items sold but stock only reduced by one ✗
```

---

## How databases achieve isolation — MVCC

Modern databases (PostgreSQL, MySQL InnoDB) use **MVCC (Multi-Version Concurrency Control)** rather than locking to achieve isolation.

Instead of blocking readers when a writer is active, the database keeps multiple versions of each row. Each transaction gets a **snapshot** of the database as it existed when the transaction started. It reads from that snapshot regardless of what other transactions are doing.

```
T1 starts at time 10:00:00 → gets snapshot of DB at 10:00:00
T2 updates Alice's balance at 10:00:01, commits
T1 reads Alice's balance → still sees the 10:00:00 snapshot → original value

Result: readers never block writers, writers never block readers ✓
```

This is why MVCC is the default in most production databases — it gives you isolation without the throughput cost of locks.

---

## Isolation is not binary — it's a spectrum

Full isolation (no anomaly possible) is expensive. Most systems don't need it everywhere. Databases expose **isolation levels** — you choose how much isolation you need per transaction.

```
READ UNCOMMITTED  → can see dirty reads (almost never used)
READ COMMITTED    → no dirty reads (default in many DBs)
REPEATABLE READ   → no dirty reads, no non-repeatable reads
SERIALIZABLE      → no anomalies at all, fully serial behaviour
```

Higher isolation = fewer anomalies = more locks/overhead = lower throughput.

The full trade-off matrix between isolation levels and anomalies is covered in depth in `09-Transaction-Isolation/`.

> [!important] Isolation is the most complex of the four ACID properties
> Atomicity, Consistency, and Durability are mostly binary — either you have them or you don't. Isolation is a dial. Choosing the right isolation level for each transaction type is a real design decision in production systems.
