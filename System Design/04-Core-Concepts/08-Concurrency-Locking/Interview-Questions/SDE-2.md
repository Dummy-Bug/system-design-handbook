# Concurrency & Locking — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around locking strategies, deadlock prevention, distributed locks, and idempotency in complex payment flows. Expected at SDE-2 level.

---

## Q1 — Hotel Booking Concurrency

> [!question] 500 users simultaneously try to book the last available room in a hotel. Only one should succeed. Walk me through your implementation using pessimistic locking.

> [!success]- Answer
>
> **The problem without locking:**
> ```
> 500 users → all read availability: 1 room
> All pass the "available?" check
> All write: booked = true
> Result: 500 confirmed bookings for 1 room ✗
> ```
>
> **Pessimistic locking with SELECT FOR UPDATE:**
> ```sql
> BEGIN TRANSACTION
>
> -- Lock the room row
> SELECT availability FROM rooms
> WHERE room_id = 456
> FOR UPDATE  ← acquires exclusive lock
>
> -- Only one user's transaction can be here at a time
> IF availability > 0:
>     -- Decrement availability
>     UPDATE rooms SET availability = availability - 1 WHERE room_id = 456
>
>     -- Create booking
>     INSERT INTO bookings (user_id, room_id, check_in, check_out) VALUES (...)
>
>     COMMIT  → lock released
>     RETURN success
> ELSE:
>     ROLLBACK  → lock released
>     RETURN "no rooms available"
> ```
>
> **What happens to the other 499 users:**
> ```
> User 1's FOR UPDATE succeeds → holds lock
> Users 2-500: their FOR UPDATE blocks → waits in queue
>
> User 1 commits:
>   availability = 0 now
>   Lock released
>
> User 2 gets lock:
>   Reads availability = 0
>   No rooms → rollback → returns "unavailable"
>
> Users 3-500: same as User 2 → all return "unavailable" ✓
> ```
>
> **Performance consideration at 500 concurrent:**
> ```
> FOR UPDATE serializes access → effectively processes one at a time
> Queue of 499 waiters → last user waits until 498 ahead of them complete
>
> If each transaction takes 50ms → last user waits 50ms × 499 = 24 seconds
> This is the cost of correctness at extreme concurrency
>
> Mitigation: fail fast if queue is full (connection timeout)
>              rather than waiting 24 seconds to be told "no rooms"
> ```
>
> > [!tip] Interview framing
> > *"SELECT FOR UPDATE locks the row — only one transaction can read it at a time. User 1 locks, decrements, commits. User 2 gets lock, reads 0, returns unavailable. 500 concurrent users become serial — correctness guaranteed but throughput is sequential. At very high concurrency, use fail-fast timeouts so users aren't waiting 24 seconds."*

---

## Q2 — Avoiding Deadlock in Fund Transfer

> [!question] Your service transfers money between two bank accounts. A deadlock occurs when two transfers happen simultaneously (A→B and B→A). How do you prevent it?

> [!success]- Answer
>
> **The deadlock scenario:**
> ```
> Transfer 1: Alice ($100) → Bob
>   Locks Account A (Alice)
>   Waiting to lock Account B (Bob)
>
> Transfer 2: Bob ($50) → Alice
>   Locks Account B (Bob)
>   Waiting to lock Account A (Alice)
>
> T1 holds A, wants B
> T2 holds B, wants A
> → Circular dependency → deadlock → neither completes
> ```
>
> **Fix 1 — Lock ordering (best approach):**
> ```
> Rule: always lock the account with the LOWER ID first
>
> Transfer 1 (Alice=1, Bob=2):
>   Lock Account 1 (Alice), then Account 2 (Bob) ✓
>
> Transfer 2 (Bob=2, Alice=1):
>   Must lock Account 1 (Alice) first, then Account 2 (Bob)
>   → Not Account 2 first (even though Bob is the sender)
>
> Both transactions try to lock Account 1 first:
>   T1 gets it → T2 waits
>   T1 also gets Account 2 → executes → commits
>   T2 gets Account 1 (T1 released it) → gets Account 2 → executes ✓
>
> No circular dependency possible → deadlock impossible ✓
> ```
>
> **Fix 2 — Lock timeout (safety net):**
> ```
> SET lock_timeout = '5s'
>
> If a transaction waits >5s for a lock → it times out → rolls back
> The other transaction completes
> The timed-out one retries with fresh locks
>
> This catches any edge cases that slip through ordering
> ```
>
> **Implementation:**
> ```python
> def transfer(from_id, to_id, amount):
>     # Always lock in ascending ID order
>     first_id  = min(from_id, to_id)
>     second_id = max(from_id, to_id)
>
>     with transaction():
>         lock_account(first_id)   # SELECT ... FOR UPDATE
>         lock_account(second_id)
>         debit(from_id, amount)
>         credit(to_id, amount)
> ```
>
> > [!tip] Interview framing
> > *"Deadlock from A→B and B→A transfers: both lock one account and wait for the other. Fix: global lock ordering — always lock lower account ID first. Both transactions now try to acquire the same first lock → one waits, no circular dependency. Timeout as safety net for any edge cases."*

---

## Q3 — Optimistic vs Pessimistic: Flash Sale

> [!question] 10,000 users try to buy a limited-edition item (100 units) simultaneously. Compare optimistic vs pessimistic locking — which would you use and why?

> [!success]- Answer
>
> **Optimistic locking approach:**
> ```sql
> SELECT stock, version FROM inventory WHERE item_id = 1
> -- stock = 100, version = 5
>
> -- Try to buy:
> UPDATE inventory
> SET stock = stock - 1, version = version + 1
> WHERE item_id = 1 AND version = 5  ← check version
>
> IF rows_affected = 0:
>     RETRY  ← version changed (someone else bought) → re-read and try again
> ```
>
> **Problem with optimistic locking at 10,000 concurrent users:**
> ```
> 10,000 users all read version = 5
> All try to update WHERE version = 5
> Database processes them serially:
>   User 1: succeeds, version becomes 6
>   Users 2-9999: version mismatch → 0 rows → must retry
>
> Each retry: re-read (stock = 99, version = 6) → try update WHERE version = 6
>   User 2: succeeds
>   Users 3-9999: must retry AGAIN
>
> 10,000 users → each fails on average 100 times → 1,000,000 total DB operations
> Massive write amplification, DB under extreme load
> ```
>
> **Pessimistic locking is better here:**
> ```sql
> BEGIN
> SELECT stock FROM inventory WHERE item_id = 1 FOR UPDATE
>
> IF stock > 0:
>     UPDATE inventory SET stock = stock - 1 WHERE item_id = 1
>     INSERT INTO orders (user_id, item_id) VALUES (...)
>     COMMIT
> ELSE:
>     ROLLBACK → "sold out"
> ```
>
> **Better still — atomic decrement:**
> ```sql
> UPDATE inventory
> SET stock = stock - 1
> WHERE item_id = 1 AND stock > 0
>
> IF rows_affected = 1: success
> IF rows_affected = 0: sold out (stock was 0)
>
> Single atomic operation — no separate SELECT needed
> Database handles concurrency internally
> Much simpler, very efficient
> ```
>
> **Why pessimistic/atomic wins at high contention:**
> ```
> Each request: one DB operation, immediate result
> No retry loops, no re-reads, no version checking
> 10,000 requests → 10,000 DB operations → 100 succeed, 9,900 get "sold out"
> ```
>
> > [!tip] Interview framing
> > *"Optimistic locking at 10,000 concurrent users creates retry storms — each retry generates more DB operations. At high contention, pessimistic (or atomic decrement) wins. `UPDATE SET stock = stock - 1 WHERE stock > 0` is a single atomic operation — no retries, no race conditions, extremely efficient."*

---

## Q4 — Redis Distributed Lock

> [!question] You need to ensure only one server processes a scheduled job at a time (e.g., sending weekly digest emails). How do you implement this with Redis?

> [!success]- Answer
>
> **The problem without a distributed lock:**
> ```
> 3 app servers, each with a cron job firing every Monday at 9am:
>   Server A: runs job → sends 1M emails
>   Server B: runs job → sends 1M emails again (duplicate)
>   Server C: runs job → sends 1M emails again (triple)
>
>   Users receive 3 copies of the weekly digest ✗
> ```
>
> **Redis distributed lock — SET NX PX:**
> ```
> SET weekly-digest-lock <server-id> NX PX 300000
>
> NX  = only set if key does NOT exist (atomic check-and-set)
> PX  = expire in 300000 milliseconds (5 minutes = TTL)
> <server-id> = unique identifier for this server instance (UUID)
>
> Returns: OK if lock acquired, nil if already taken
> ```
>
> **Full implementation:**
> ```python
> def run_weekly_digest():
>     lock_key = "weekly-digest-lock"
>     server_id = str(uuid.uuid4())  # unique per server per run
>     ttl_ms = 5 * 60 * 1000  # 5 minutes
>
>     # Try to acquire lock
>     acquired = redis.set(lock_key, server_id, nx=True, px=ttl_ms)
>     if not acquired:
>         return  # another server has the lock
>
>     try:
>         send_weekly_digest_emails()  # actual work
>     finally:
>         # Only release YOUR lock, not someone else's
>         if redis.get(lock_key) == server_id:
>             redis.delete(lock_key)
> ```
>
> **Why TTL is critical:**
> ```
> Server A acquires lock → crashes mid-job
>
> Without TTL: lock stays forever → weekly digest never runs again
> With TTL (5 min): lock auto-expires → Server B acquires it next run ✓
>
> TTL must be > max expected job duration
> If job takes 4 minutes, TTL must be > 4 minutes
> ```
>
> **Why use server_id as value (not just "1"):**
> ```
> Server A acquires lock (TTL 5 min)
> Job takes 6 minutes → TTL expires → lock released automatically
> Server B acquires lock (TTL 5 min) → starts job
>
> Server A finishes (after 6 min) → tries to delete lock
> Without server_id check: Server A deletes Server B's lock → Server C also starts job
> With server_id check: Server A's server_id ≠ Server B's value → don't delete ✓
> ```
>
> > [!tip] Interview framing
> > *"SET key value NX PX ttl — atomic, NX ensures only one server gets it. Store server UUID as value, only delete if it's your UUID — prevents a slow server from deleting someone else's lock after its TTL expires. TTL must exceed max job duration to prevent lock starvation on crash."*

---

## Q5 — MVCC in Practice

> [!question] You're building a paginated API: GET /products?page=2&size=100. Without MVCC, what race condition can users experience? How does MVCC fix it?

> [!success]- Answer
>
> **The problem without MVCC (with row-level locking):**
> ```
> User fetches page 1: rows 1-100 (sorted by ID)
>   → products 1, 2, 3, ..., 100 returned
>
> While user is looking at page 1:
>   New product inserted with ID 50 (auto-increment, but out of order)
>   Or: product with ID 45 is deleted
>
> User fetches page 2: rows 101-200
>   → If row was inserted at ID 50: some row may appear on BOTH page 1 and page 2
>   → If row at ID 45 was deleted: a row from page 1's range might now appear on page 2
>
>   User experience: sees same product twice, or misses a product entirely
> ```
>
> **How MVCC fixes it:**
> ```
> With MVCC (PostgreSQL REPEATABLE READ or SERIALIZABLE):
>
> BEGIN TRANSACTION  ← implicit for any read
>
> Transaction gets a snapshot ID: "you see the database as it was at T=1000"
>
> Page 1 request:
>   Sees snapshot at T=1000
>   Returns rows 1-100 as they existed at T=1000
>
>   New product inserted at T=1001 → not in snapshot
>   Product deleted at T=1001 → still in snapshot
>
> Page 2 request (same transaction or same snapshot):
>   Still sees T=1000
>   Returns rows 101-200 as they existed at T=1000
>   Completely consistent with page 1 ✓
>
> COMMIT
> ```
>
> **Practical implementation:**
> ```
> Option 1: explicit transaction
>   BEGIN (REPEATABLE READ) → fetch all pages → COMMIT
>   Consistent snapshot across all page fetches
>   Works but keeps transaction open for entire pagination session
>
> Option 2: cursor-based pagination
>   "Return products WHERE id > last_seen_id LIMIT 100"
>   Stable cursor even without explicit transaction
>   Deletes: row disappears from results (not duplicated)
>   Inserts: only affects future pages (ID higher than cursor)
>   No MVCC needed — cursor provides stability
> ```
>
> > [!tip] Interview framing
> > *"Without MVCC, inserts and deletes between page fetches cause duplicates and skips. MVCC gives each transaction a consistent snapshot — page 2 sees the same database state as page 1. Alternatively, cursor-based pagination (WHERE id > last_id LIMIT 100) provides stability without transactions."*
