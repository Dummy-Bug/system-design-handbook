# The Problem ACID Solves

> [!question] What happens when a database operation is interrupted halfway through? Without any guarantees, the answer is: data corruption that silently looks like success.

---

## The banking transfer

Alice wants to transfer $100 to Bob. Simple enough. Under the hood, that's two separate database operations:

```
Step 1: Deduct $100 from Alice's account
Step 2: Add $100 to Bob's account
```

These two operations are not atomic by default. They're just two separate writes, and anything can happen between them.

```
Step 1: Deduct $100 from Alice  ✓  (Alice: $500 → $400)
SERVER CRASHES
Step 2: Add $100 to Bob         ✗  never executed

Result:
  Alice: $400  (debited)
  Bob:   $300  (unchanged)
  $100 has vanished from the system
  The bank is insolvent by $100
```

The database is now in a **corrupt state** — the total money in the system no longer adds up. And crucially, the system doesn't know it. There's no error logged. No alert fired. Just silent corruption.

---

## What ACID provides

ACID is a set of four guarantees designed to make **multi-step database operations** safe. Instead of "two separate writes that might be interrupted," ACID gives you a **transaction** — a unit of work that either completes entirely or leaves no trace.

```
BEGIN TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 'alice';
  UPDATE accounts SET balance = balance + 100 WHERE id = 'bob';
COMMIT;
```

With ACID, this either completes fully or rolls back completely. There is no state where Alice is debited and Bob is not credited.

The four properties — Atomicity, Consistency, Isolation, Durability — each protect against a different class of failure. Together they make the database a reliable foundation for systems where correctness is non-negotiable.
