# ACID Properties

---

## The Problem ACID Solves

You're building a banking app. Alice wants to transfer $100 to Bob. Under the hood that's two operations:

```
Step 1: Deduct $100 from Alice's account
Step 2: Add $100 to Bob's account
```

What happens if the server crashes after step 1 but before step 2? Alice loses $100. It vanishes. The bank is now in an inconsistent state.

ACID is a set of four properties that databases guarantee to prevent exactly this kind of problem. Every serious database (PostgreSQL, MySQL, Oracle) is ACID-compliant.

---

## A — Atomicity

Either **all** operations in a transaction succeed together, or **none** of them happen. No partial state. Ever.

```
Transfer $100: Alice → Bob

Without atomicity:
  Step 1: Deduct $100 from Alice ✓
  CRASH
  Step 2: Add $100 to Bob ✗ never happened
  → $100 gone forever, Alice debited, Bob never credited

With atomicity:
  Step 1: Deduct $100 from Alice ✓
  CRASH
  → rollback → Alice's $100 restored automatically
  → as if the transaction never started ✓
```

The database tracks every operation in a transaction. If anything fails — crash, error, constraint violation — the entire transaction is rolled back to the state before it started.

> [!info] Atomicity = "all or nothing." There is no in-between state that persists.

---

## C — Consistency

The database must always go from one **valid state** to another **valid state**. Your own rules — constraints, foreign keys, balance checks — must never be broken.

Example: Alice only has $50 but tries to transfer $100.

```
Alice balance: $50
Transfer: $100

Without consistency:
  Deduct $100 → Alice balance = -$50
  → database allows it → invalid state ✗

With consistency:
  Deduct $100 → balance would be -$50
  → violates constraint: balance >= 0
  → transaction rejected
  → database stays in valid state ✓
```

You define consistency through constraints:
```
balance >= 0          → no negative balances
email UNIQUE          → no duplicate accounts
foreign key exists    → no orphaned records
```

The database checks these on every write and rejects anything that would violate them.

> [!info] Consistency = your rules are always enforced. The database can never be put into a state that violates your defined constraints.

---

## I — Isolation

Concurrent transactions must not see each other's intermediate states. Each transaction runs as if it's the only one in the system.

The bank's reporting system runs a query — "what is Alice's balance?" — at the exact moment her transfer is in progress:

```
Transaction 1: Transfer $100 (Alice → Bob)
  Step 1: Deduct $100 from Alice  ← in progress
  Step 2: Add $100 to Bob         ← not yet done

Transaction 2: Read Alice's balance  ← runs simultaneously

Without isolation:
  Transaction 2 reads mid-transfer
  → sees Alice's balance after deduct, before credit
  → dirty read → wrong data served ✗

With isolation:
  Transaction 2 reads the snapshot from before Transaction 1 started
  → sees Alice's original balance ✓
  → Transaction 1's changes only visible after it fully commits
```

This "old snapshot" is how databases implement isolation — each transaction sees a consistent point-in-time snapshot of the data.

> [!info] Isolation = concurrent transactions don't interfere with each other. Changes are invisible to others until committed.

> [!important] Isolation has levels — not all databases enforce it equally strictly. Full isolation (SERIALIZABLE) is safest but slowest. Weaker levels trade safety for performance. This is covered in depth in Transaction Isolation Levels.

---

## D — Durability

Once a transaction is committed, that data **must survive** — crashes, power loss, hardware failure, anything. If the database said "success", it means it.

```
Transaction commits → "Transfer successful" returned to user
Server loses power 2 seconds later

Without durability:
  Data was only in memory → power loss → gone
  → user told "transfer successful" but money never actually moved ✗

With durability:
  Committed data written to disk before "success" is returned
  → server restarts → data still there ✓
  → transfer stands
```

Databases achieve durability through a **Write-Ahead Log (WAL)** — every change is written to disk in a log *before* it's applied to the actual data. If the server crashes mid-transaction, on recovery it replays the log and restores the committed state.

> [!info] Durability = committed means committed. The database's promise survives any failure.

---

## The Full Picture

```
A — Atomicity    → all or nothing, no partial transactions
C — Consistency  → rules always enforced, no invalid states
I — Isolation    → concurrent transactions don't see each other's mid-state
D — Durability   → committed data survives crashes and power loss
```

> [!important] ACID is not free. Each property has a cost:
> ```
> Atomicity  → rollback overhead
> Consistency → constraint checks on every write
> Isolation  → locks or snapshot overhead, reduced concurrency
> Durability → disk write before acknowledging commit, slower writes
> ```
> This is why some systems (especially high-scale NoSQL) relax ACID guarantees in exchange for performance. That trade-off is called BASE — covered later.

---

## Where ACID Matters Most

```
Banking / payments     → all four, non-negotiable
Hotel / ticket booking → atomicity + isolation critical (double booking)
E-commerce orders      → atomicity critical (charge without order = disaster)
Social media likes     → ACID overkill, eventual consistency is fine
```

Any system where partial failure = data corruption or financial loss needs full ACID guarantees.
