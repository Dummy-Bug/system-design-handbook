# Concurrency & Locking — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of race conditions, pessimistic vs optimistic locking, deadlocks, and idempotency. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is a Race Condition?

> [!question] What is a race condition? Give me a concrete example with a shopping cart.

> [!success]- Answer
>
> **Race condition:**
> When two operations read the same value, both make a decision based on it, and both write back — one write overwrites the other. The final result is wrong.
>
> **Shopping cart example:**
> ```
> Item has 1 unit in stock.
>
> User A reads stock: 1 (available)
> User B reads stock: 1 (available)
>
> User A places order → writes stock = 0
> User B places order → writes stock = 0
>
> Result: 2 orders fulfilled, 0 units in stock
>         One customer will get a cancellation email
>         Inventory is oversold
> ```
>
> **Why it happens:**
> ```
> Read → (gap) → write is not atomic
> Another write can sneak into the gap
> Both readers acted on the same stale value
> ```
>
> **The general pattern:**
> ```
> SELECT quantity FROM inventory WHERE id = 1  → both read 1
> -- gap here --
> UPDATE inventory SET quantity = 0 WHERE id = 1  → both write 0
> ```
>
> > [!important] Race conditions happen whenever read and write are not atomic. The fix is to make the check-and-update a single atomic operation, or lock the row between read and write.
>
> > [!tip] Interview framing
> > *"A race condition is when two operations read the same value and both write back based on it — one write clobbers the other. Classic example: two users buying the last item. Both read stock = 1, both place orders, both write stock = 0. Result: oversold inventory."*

---

## Q2 — Pessimistic vs Optimistic Locking

> [!question] What is the difference between pessimistic and optimistic locking? When would you use each?

> [!success]- Answer
>
> **Pessimistic locking — assume conflict will happen:**
> ```
> Lock the row before reading it
> No one else can touch it until you're done
>
> SELECT * FROM rooms WHERE id = 1 FOR UPDATE
> -- row is locked --
> Check availability: 1 room
> Book it: UPDATE rooms SET booked = true WHERE id = 1
> COMMIT → lock released
>
> User B tries to book same room → waits at FOR UPDATE
> B gets lock → reads booked = true → room unavailable → no double booking ✓
> ```
>
> **Optimistic locking — assume conflict is rare:**
> ```
> Don't lock. Add a version number to every row.
> Read the version, make changes, update only if version is still the same.
>
> SELECT *, version FROM items WHERE id = 1  → {stock: 5, version: 3}
> -- no lock --
> UPDATE items SET stock = 4, version = 4 WHERE id = 1 AND version = 3
>
> If 0 rows updated → someone else changed it → retry
> ```
>
> **When to use each:**
>
> | Scenario | Contention | Strategy |
> |---|---|---|
> | Hotel last room | High — many users want same room | Pessimistic |
> | Flash sale last item | High | Pessimistic |
> | User editing their own profile | Low — only one user edits it | Optimistic |
> | Document collaboration | Low most of the time | Optimistic |
> | Bank transfer | High — correctness critical | Pessimistic |
>
> > [!important] High contention → pessimistic (lock upfront, avoid retries). Low contention → optimistic (no locking overhead, retry on the rare conflict).
>
> > [!tip] Interview framing
> > *"Pessimistic locks the row — one at a time, guaranteed no conflict. Optimistic adds a version number — check on write, retry if stale. Use pessimistic for hotel bookings and flash sales where contention is high. Use optimistic for profile edits where conflicts are rare and retries are cheap."*

---

## Q3 — Deadlocks

> [!question] What is a deadlock? How do you prevent it?

> [!success]- Answer
>
> **Deadlock:**
> Two transactions each hold a lock the other needs. Neither can proceed. Both wait forever.
>
> ```
> Transaction A: locks Account 1, wants Account 2
> Transaction B: locks Account 2, wants Account 1
>
> A waits for B to release Account 2
> B waits for A to release Account 1
> Neither will ever release → deadlock
> ```
>
> **Two prevention strategies:**
>
> **1. Lock ordering — always acquire locks in the same global order:**
> ```
> Rule: always lock lower account ID first
>
> Transfer A→B (A=1, B=2):  lock Account 1, then Account 2 ✓
> Transfer B→A (A=2, B=1):  lock Account 1, then Account 2 ✓
>
> Both transactions try to lock Account 1 first
> One succeeds, the other waits — no circular dependency possible
> Deadlock structurally impossible ✓
> ```
>
> **2. Lock timeout — if you can't get a lock within N seconds, give up:**
> ```
> Transaction A: locks Account 1, waiting for Account 2
> Transaction B: locks Account 2, waiting for Account 1
>
> After 5 seconds: Transaction B times out → releases Account 2 → rolls back
> Transaction A: gets Account 2 → completes successfully ✓
> Transaction B: retries from scratch
> ```
>
> **In practice:** use both. Lock ordering prevents deadlocks structurally. Timeouts are the safety net for cases that slip through.
>
> > [!tip] Interview framing
> > *"Deadlock: two transactions waiting on each other's lock forever. Prevention: lock ordering — always acquire locks in the same global order, breaking the circular dependency. Timeout: if lock not acquired in N seconds, roll back and retry. Ordering prevents it; timeout catches edge cases."*

---

## Q4 — MVCC

> [!question] What is MVCC and what problem does it solve?

> [!success]- Answer
>
> **The problem it solves:**
> Without MVCC, a read must wait for any in-progress write to finish. A write must wait for any active reads. This serialises all access and destroys throughput.
>
> **MVCC — Multi-Version Concurrency Control:**
> Instead of locking, the database keeps multiple versions of each row. Readers see the version that existed when their transaction started. Writers create a new version.
>
> ```
> Row: {user_id: 1, name: "Alice", version: 5}
>
> Transaction A starts (sees version 5)
> Transaction B updates name to "Alicia" (creates version 6)
> Transaction B commits
>
> Transaction A still reads "Alice" (version 5)
> Transaction A commits
>
> New Transaction C starts → reads "Alicia" (version 6)
> ```
>
> **What this enables:**
> ```
> Readers never block writers
> Writers never block readers
>
> Long-running report query → doesn't block writes happening simultaneously
> High write throughput    → doesn't block reads
> ```
>
> **Consistent paginated reads:**
> ```
> Page 1 of results: reads 100 rows from snapshot at T=100
> Write happens at T=101, modifies row 50
> Page 2 of results: still reads from snapshot at T=100
> → row 50 appears with its old value → consistent pagination
> ```
>
> > [!tip] Interview framing
> > *"MVCC keeps multiple row versions. Readers see a snapshot from when their transaction started — unaffected by concurrent writes. Writers create new versions — don't block readers. This is why Postgres can handle heavy concurrent reads and writes without locking contention."*

---

## Q5 — Idempotency

> [!question] What is idempotency? Why does it matter for payment APIs?

> [!success]- Answer
>
> **Idempotency:**
> An operation is idempotent if performing it multiple times produces the same result as performing it once.
>
> ```
> Idempotent:      GET /orders/123    → always returns same order
>                  DELETE /orders/123 → first call deletes, second call: already gone, same result
>                  PUT (full replace)  → same data written regardless of how many times
>
> Not idempotent:  POST /payments     → each call creates a new charge
>                  POST /orders       → each call creates a new order
> ```
>
> **Why it matters for payments:**
> ```
> User clicks "Pay"
> Request sent → network timeout → client doesn't know if it succeeded
>
> Without idempotency:
>   Client retries → two charges processed ✗
>   User sees: "Wait, why was I charged twice?"
>
> With idempotency key:
>   Client generates unique ID: "order-abc-payment-xyz"
>   First call:  charge processed, key stored
>   Retry call:  key already seen → return original response → no new charge ✓
> ```
>
> **How to implement:**
> ```
> Client generates UUID per operation
> Sends: POST /payments { amount: 50, idempotency_key: "uuid-here" }
>
> Server:
>   check: has this key been processed before?
>   Yes → return cached response (no new charge)
>   No  → process → store key + response → return response
> ```
>
> > [!important] Idempotency keys make retries safe. Without them, every retry on a payment endpoint risks a duplicate charge. The key must be generated by the client — not the server — so retries carry the same key.
>
> > [!tip] Interview framing
> > *"Idempotency means repeat calls produce the same result. Critical for payments — a network timeout means the client doesn't know if the charge succeeded. Without idempotency keys, retry = double charge. Key is client-generated UUID, server deduplicates using it."*
