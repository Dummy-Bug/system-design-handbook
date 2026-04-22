# The Four Isolation Problems

> [!abstract] When two transactions run concurrently without proper isolation, four specific things go wrong. Isolation levels are defined by which of these they prevent.

## Problem 1 — Dirty Read

Reading data from another transaction that hasn't committed yet — and might get rolled back.

```sql
-- Transaction B (transfer in progress, NOT committed yet)
UPDATE accounts SET balance = 1500 WHERE id = 123;  -- was 1000, adding 500
-- B has not committed yet

-- Transaction A reads mid-transfer
SELECT balance FROM accounts WHERE id = 123;
-- Returns: 1500  ← dirty read, B's write not committed

-- Transaction B fails → rolls back
UPDATE accounts SET balance = 1000 WHERE id = 123;  -- reverted

-- A saw $1500 that never actually existed
```

> [!danger] You made a decision based on money that was never real.

---

## Problem 2 — Non-Repeatable Read

Same query, same transaction, same row — different result because another transaction committed in between.

```sql
BEGIN TRANSACTION;  -- Transaction A (audit report)

SELECT balance FROM accounts WHERE id = 123;
-- Returns: 1000

-- Meanwhile Transaction B commits: balance = 1500

SELECT balance FROM accounts WHERE id = 123;
-- Returns: 1500  ← same query, same transaction, different result

COMMIT;
```

> [!warning] Within a single transaction, the world should look frozen.
> For casual reads — fine, you refresh and see latest. For audit reports, financial calculations, multi-step operations — inconsistency within one transaction corrupts the result.

**Non-Repeatable vs Dirty Read:**
```
Dirty Read          → reading UNCOMMITTED data
Non-Repeatable Read → reading COMMITTED data, but it changed between reads
```

---

## Problem 3 — Phantom Read

Same query, same transaction — but new rows appear (or disappear) because another transaction inserted/deleted.

```sql
BEGIN TRANSACTION;  -- Transaction A (processing today's orders)

SELECT COUNT(*) FROM orders WHERE date = '2026-04-03';
-- Returns: 100

-- Meanwhile Transaction B inserts 2 new orders and commits

SELECT COUNT(*) FROM orders WHERE date = '2026-04-03';
-- Returns: 102  ← phantom rows appeared

COMMIT;
```

> [!warning] Like seeing ghosts — rows that weren't there before suddenly appear.

**Phantom vs Non-Repeatable Read:**
```
Non-Repeatable Read → same ROW changed its value
Phantom Read        → new ROWS appeared or existing rows disappeared
```

---

## Problem 4 — Lost Update

Two transactions read the same committed value, both compute an update based on it, both write — one overwrites the other.

> [!important] The read is not stale — both transactions read the correct, committed value. The problem is a **write-write conflict**: neither transaction knows the other is also in progress, both independently decide to write, and the second write silently stomps the first.

```sql
-- Both transactions read balance = 1000 (correct, committed value)

-- Transaction A: adds $500
SELECT balance FROM accounts WHERE id = 123;  -- gets 1000 ← correct
-- (gap — B also reads the same correct value)
UPDATE accounts SET balance = 1500 WHERE id = 123;  -- 1000 + 500

-- Transaction B: adds $200 (based on the 1000 it also correctly read)
UPDATE accounts SET balance = 1200 WHERE id = 123;  -- 1000 + 200 ← overwrites A

-- Correct result: 1000 + 500 + 200 = $1700
-- Actual result:  $1200  ← A's $500 deposit is gone
```

This also explains the **hotel double-booking** problem — both users read "room available" (correct, committed value), both decide to book, both write. Neither read was stale. The conflict is purely in the concurrent writes.

```
T1: read → room available = true  ← correct committed value
T2: read → room available = true  ← correct committed value
T1: write → available = false
T2: write → available = false     ← both succeed, double booking
```

> [!danger] Lost update is a write-write conflict, not a stale read problem.
> Solved by pessimistic locking (`SELECT FOR UPDATE`) or SERIALIZABLE isolation.

---

| Problem | What happens | Caused by |
|---|---|---|
| Dirty Read | Read uncommitted data that gets rolled back | No read isolation |
| Non-Repeatable Read | Same row, different value within one transaction | Another transaction committed between reads |
| Phantom Read | New rows appear/disappear within one transaction | Another transaction inserted/deleted between reads |
| Lost Update | One write overwrites another's committed write | Both transactions read the same correct value, both write — write-write conflict |
