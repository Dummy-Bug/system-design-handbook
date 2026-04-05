# Transaction Isolation — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around isolation levels, lost updates, phantom reads, and choosing the right isolation for specific business scenarios. Expected at SDE-2 level.

---

## Q1 — Lost Update in Inventory

> [!question] Two users simultaneously try to buy the last item in stock. Without proper isolation, both succeed — item stock goes negative. What isolation level and locking strategy prevents this?

> [!success]- Answer
>
> **The lost update:**
> ```
> Item: { item_id: 1, stock: 1 }
>
> User A transaction:
>   SELECT stock FROM inventory WHERE id = 1  → stock = 1
>   -- application code: if stock > 0, proceed --
>   UPDATE inventory SET stock = stock - 1 WHERE id = 1
>
> User B transaction (runs simultaneously):
>   SELECT stock FROM inventory WHERE id = 1  → stock = 1 (same stale read)
>   UPDATE inventory SET stock = stock - 1 WHERE id = 1
>
> Result: stock = -1 ✗
> ```
>
> **Option A — REPEATABLE READ + SELECT FOR UPDATE:**
> ```sql
> BEGIN;  -- REPEATABLE READ is default in MySQL, explicit in Postgres
>
> SELECT stock FROM inventory WHERE id = 1 FOR UPDATE;  -- acquires lock
>
> -- If stock > 0:
> UPDATE inventory SET stock = stock - 1 WHERE id = 1;
> INSERT INTO orders ...;
> COMMIT;  -- releases lock
> ```
>
> Result: User B's `SELECT FOR UPDATE` blocks until User A commits.
> User B then reads stock = 0 → fails check → no purchase.
>
> **Option B — SERIALIZABLE (no explicit locks):**
> ```sql
> BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
>
> SELECT stock FROM inventory WHERE id = 1;
> -- application code checks stock > 0
> UPDATE inventory SET stock = stock - 1 WHERE id = 1;
> INSERT INTO orders ...;
> COMMIT;
> ```
>
> DB detects conflicting access pattern → one transaction aborts with serialization failure → client retries.
>
> **Option C — Atomic update (cleanest for this case):**
> ```sql
> UPDATE inventory
> SET stock = stock - 1
> WHERE id = 1 AND stock > 0;
>
> IF rows_affected = 1: purchased ✓
> IF rows_affected = 0: out of stock ✗
> ```
>
> Single atomic statement — no separate SELECT, no race condition.
>
> **When to use each:**
> ```
> Simple stock decrement → atomic UPDATE (Option C)
> Multi-step transaction (check stock, create order, charge) → Option A (REPEATABLE READ + FOR UPDATE)
> Complex logic, developer safety net → Option B (SERIALIZABLE)
> ```
>
> > [!tip] Interview framing
> > *"Three options: atomic `UPDATE SET stock = stock-1 WHERE stock > 0` (simplest, no race), REPEATABLE READ + SELECT FOR UPDATE (explicit lock, multi-step safe), SERIALIZABLE (DB detects conflict, safe but performance cost). For simple inventory, atomic update is cleanest. For multi-step checkout, REPEATABLE READ + FOR UPDATE."*

---

## Q2 — Phantom Read in Reporting

> [!question] You're generating a financial report: first you count total orders, then sum the order amounts. Between your two queries, a new order is inserted. The count and sum don't match. What isolation level fixes this?

> [!success]- Answer
>
> **The phantom read scenario:**
> ```
> Transaction: generate monthly revenue report
>
> Query 1: SELECT COUNT(*) FROM orders WHERE month = '2026-01'
>   → returns 1000 orders
>
>   --- New order inserted by another transaction, month = 2026-01 ---
>
> Query 2: SELECT SUM(amount) FROM orders WHERE month = '2026-01'
>   → returns sum for 1001 orders
>
> Report says: 1000 orders, $105,234 total
> Average per order: $105,234 / 1000 = $105.23
>
> But actual average: $105,234 / 1001 orders
> Report is internally inconsistent ✗ (1001 orders worth of sum, 1000-order count)
> ```
>
> **Why READ COMMITTED doesn't fix it:**
> ```
> READ COMMITTED: each statement sees its own snapshot
>   Query 1: snapshot at T=100 → 1000 orders ✓
>   New order inserted at T=101
>   Query 2: snapshot at T=102 → 1001 orders ✗
>   Different snapshots → inconsistency
> ```
>
> **Fix — REPEATABLE READ (snapshot isolation):**
> ```sql
> BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
>
> SELECT COUNT(*) FROM orders WHERE month = '2026-01';
> -- snapshot taken at transaction start, T=100
> -- returns 1000 ✓
>
> -- New order inserted by another transaction at T=101
>
> SELECT SUM(amount) FROM orders WHERE month = '2026-01';
> -- still sees snapshot at T=100 → sees the same 1000 orders
> -- returns sum for 1000 orders ✓
>
> COMMIT;
> ```
>
> Both queries see the same consistent snapshot. Phantom row at T=101 not visible.
>
> > [!important] PostgreSQL's REPEATABLE READ is snapshot isolation — the entire transaction sees a consistent view taken at transaction start. Any inserts/updates by other transactions are invisible. This is why it prevents phantom reads in Postgres (unlike theoretical REPEATABLE READ which only prevents non-repeatable reads).
>
> > [!tip] Interview framing
> > *"READ COMMITTED gives each statement its own snapshot — a new order inserted between two queries makes the report inconsistent. REPEATABLE READ (snapshot isolation in PostgreSQL) gives the entire transaction one consistent snapshot taken at start. Both queries see the same set of rows."*

---

## Q3 — Choosing Isolation for Hotel Booking

> [!question] You're implementing a hotel booking system. Two users try to book the same room simultaneously. Compare using REPEATABLE READ + SELECT FOR UPDATE vs SERIALIZABLE. Which do you choose and why?

> [!success]- Answer
>
> **Both prevent double booking — the question is trade-offs:**
>
> **REPEATABLE READ + SELECT FOR UPDATE:**
> ```sql
> BEGIN;  -- REPEATABLE READ
>
> SELECT availability FROM rooms WHERE room_id = 456 FOR UPDATE;
>   → locks the row
>
> IF availability > 0:
>   UPDATE rooms SET availability = availability - 1 WHERE room_id = 456;
>   INSERT INTO bookings ...;
>   COMMIT;  ← lock released
>
> User B: blocks at FOR UPDATE → waits → gets lock after User A commits
>         reads availability = 0 → no booking
> ```
>
> **SERIALIZABLE:**
> ```sql
> BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
>
> SELECT availability FROM rooms WHERE room_id = 456;
>   → no lock taken
>
> IF availability > 0:
>   UPDATE rooms SET availability = availability - 1 WHERE room_id = 456;
>   INSERT INTO bookings ...;
>   COMMIT;  ← may fail with serialization error
> ```
>
> If User A and User B both commit concurrently, PostgreSQL detects the conflicting access pattern → one gets a serialization failure → must retry.
>
> **Why REPEATABLE READ + FOR UPDATE is the better choice for hotel booking:**
>
> ```
> Performance:
>   FOR UPDATE: User B waits predictably → resumes after User A → no retry needed
>   SERIALIZABLE: User B completes → then fails at commit → retries from scratch
>                 Retry = re-read + re-execute + re-insert → more total work
>
> Predictability:
>   FOR UPDATE: deterministic — one user waits, then gets a clear answer
>   SERIALIZABLE: non-deterministic — may retry multiple times under contention
>
> At high volume (100 concurrent bookings):
>   SERIALIZABLE: many retries → retry cascade → DB under higher load
>   FOR UPDATE: ordered queue → predictable throughput
> ```
>
> **When to prefer SERIALIZABLE:**
> ```
> Complex transactions where it's hard to identify ALL rows needing FOR UPDATE
> Teams with mixed experience → can't trust everyone to add FOR UPDATE correctly
> "Safety net" when correctness > performance
> ```
>
> > [!tip] Interview framing
> > *"Both prevent double booking. REPEATABLE READ + FOR UPDATE is better for hotel booking at scale — User B waits, then gets a definitive answer, no retry needed. SERIALIZABLE may cause User B to retry multiple times under contention, amplifying DB load. SERIALIZABLE shines when you can't identify all the rows that need locking."*

---

## Q4 — READ COMMITTED Trap

> [!question] A developer uses READ COMMITTED isolation for a multi-step bank transfer. What can go wrong and how do you fix it?

> [!success]- Answer
>
> **The multi-step bank transfer:**
> ```
> Transaction: move $100 from Alice (ID=1) to Bob (ID=2)
>
> Step 1: Read Alice's balance → $500
> Step 2: Validate Alice has enough → yes, $500 > $100
> Step 3: Deduct $100 from Alice
> Step 4: Add $100 to Bob
> COMMIT
> ```
>
> **What READ COMMITTED allows:**
> ```
> READ COMMITTED: each statement sees latest committed data
>
> Step 1: Alice balance = $500 (committed by another transfer in progress)
>         Pass validation: $500 > $100 ✓
>
> -- Another transfer simultaneously withdraws $450 from Alice and commits --
>
> Step 3: UPDATE accounts SET balance = balance - 100 WHERE id = 1
>         This reads current balance: $50 (after other transaction committed)
>         Sets balance to $50 - $100 = -$50
>
>         But we validated against $500!
>         Validation was done on stale data ✗
>         Alice goes negative ✗
> ```
>
> This is a non-repeatable read — same row (Alice's balance) returned different values at Step 1 and Step 3.
>
> **Fix — REPEATABLE READ + SELECT FOR UPDATE:**
> ```sql
> BEGIN;
>
> SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  ← locks Alice
> SELECT balance FROM accounts WHERE id = 2 FOR UPDATE;  ← locks Bob
>
> -- Concurrent transfer cannot modify Alice until this transaction commits
>
> IF alice_balance >= 100:
>     UPDATE accounts SET balance = balance - 100 WHERE id = 1;
>     UPDATE accounts SET balance = balance + 100 WHERE id = 2;
>     COMMIT;
> ELSE:
>     ROLLBACK;
> ```
>
> The lock prevents concurrent modification. The validation and deduction see the same balance.
>
> > [!tip] Interview framing
> > *"READ COMMITTED is dangerous for multi-step transfers — each statement sees fresh data, so the balance you validated against changes before you deduct. Fix: REPEATABLE READ + SELECT FOR UPDATE. Lock both accounts at the start — concurrent transfers wait, your validation and deduction see the same balance."*

---

## Q5 — Isolation Level Performance Impact

> [!question] Your service runs at 50,000 transactions per second. The DBA says "upgrade all transactions from READ COMMITTED to SERIALIZABLE for safety." You push back. Why?

> [!success]- Answer
>
> **SERIALIZABLE at 50,000 TPS — what it means:**
>
> **Performance cost of SERIALIZABLE:**
> ```
> SERIALIZABLE uses predicate locking (tracks what rows each transaction READS)
>   → Higher memory usage per transaction
>   → More lock tracking overhead per statement
>
> Under high contention:
>   Serialization failures → transactions abort and retry
>   Each retry = full transaction re-execution
>   At 50k TPS with contention: retry storms possible
>
> Benchmark reality:
>   READ COMMITTED: baseline throughput
>   REPEATABLE READ: ~10-15% throughput reduction
>   SERIALIZABLE: ~20-40% throughput reduction (varies wildly with contention)
> ```
>
> **The actual risk of READ COMMITTED:**
> ```
> READ COMMITTED allows:
>   Non-repeatable reads → same row, different value within transaction
>   Phantom reads        → new rows appear within transaction
>
> Whether this is a real problem depends entirely on the transaction logic:
>   Single-read operations: READ COMMITTED is perfectly safe
>   Aggregate reports: may be inconsistent → needs REPEATABLE READ
>   Multi-step financial: needs explicit FOR UPDATE + REPEATABLE READ
>   Simple CRUD: READ COMMITTED is fine for 90%+ of operations
> ```
>
> **The right approach — selective isolation:**
> ```
> Default: READ COMMITTED (fast, safe for most operations)
>
> Add REPEATABLE READ for:
>   Report queries that read multiple times
>   Any operation that validates then writes
>
> Add SELECT FOR UPDATE for:
>   Inventory, booking, balance checks followed by writes
>
> Use SERIALIZABLE only for:
>   Complex transactions where identifying all rows needing FOR UPDATE is impractical
>   Correctness is non-negotiable and team experience is mixed
> ```
>
> **The response to the DBA:**
> ```
> "Blanket SERIALIZABLE on 50k TPS will hurt throughput significantly.
>  Let's audit which transactions actually need it.
>  I suspect 80% are safe at READ COMMITTED.
>  Let's upgrade the 20% that touch financial data — not everything."
> ```
>
> > [!tip] Interview framing
> > *"Blanket SERIALIZABLE at 50k TPS adds significant overhead — retry storms under contention, 20-40% throughput loss. Most READ COMMITTED transactions are safe — single reads, simple CRUD. Upgrade selectively: REPEATABLE READ for reports and multi-read transactions, SELECT FOR UPDATE for inventory/bookings. Reserve SERIALIZABLE for truly complex cases."*
