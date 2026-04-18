
## Sliding Window Log

Fixed Window Counter has a boundary bug — a user can burst to 2× the limit at window edges. Sliding Window Log fixes this completely by replacing the fixed clock boundary with a true rolling window.

---

### The Core Idea

Instead of storing a single counter that resets at clock boundaries, store the **actual timestamp of every allowed request**. When a new request arrives, look at the list and count how many timestamps fall within the last 60 seconds. That count is the true number of requests in the rolling window — no boundary, no clock tick, no burst possible.

---

### The Algorithm Step by Step

A request arrives at timestamp T. The limit is 5 requests per minute.

```
Step 1 — Clean
  Remove all timestamps where (T - timestamp) > 60
  These are outside the rolling window — they don't count anymore

Step 2 — Count
  How many timestamps remain in the list?

Step 3 — Decide
  count < limit  → add T to the list → allow
  count >= limit → do NOT add T → block
```

The critical detail in step 3: **only add the timestamp if you allow the request**. Never add timestamps for blocked requests. If you add timestamps for blocked requests, an attacker sending 10,000 requests per minute would accumulate 10,000 timestamps — all blocked, but all stored, blowing up memory.

---

### Worked Example

```
Current timestamp : 3720
Window start      : 3720 - 60 = 3660
List              : [3650, 3680, 3695, 3710]
Limit             : 5

Step 1 — Clean:
  3650 < 3660 → remove (outside window)
  3680 > 3660 → keep
  3695 > 3660 → keep
  3710 > 3660 → keep

Step 2 — Count:
  3 timestamps remain

Step 3 — Decide:
  3 < 5 → add 3720 → allow

List after: [3680, 3695, 3710, 3720]
```

---

### Why the Boundary Bug Is Gone

Fixed Window Counter resets at fixed clock ticks. A user could send 5 requests at 00:58 and 5 more at 01:02 — both windows see a count of 5, both allow. 10 requests in 60 seconds.

Sliding Window Log has no clock ticks. At 01:02, the window looks back at the last 60 seconds from right now — it sees the 5 requests at 00:58 still in the list. Count = 5, already at limit, blocked. The burst is impossible.

---

### Redis Implementation

Redis Sorted Set is the natural data structure here. The score is the timestamp, the member is the timestamp (or a unique request ID). This gives O(log n) insert and O(log n) range delete.

```
Key   : user:{user_id}:{endpoint}
Value : Sorted Set of timestamps (score = timestamp)

On every request at timestamp T:
  ZREMRANGEBYSCORE key 0 (T-60)   ← remove expired timestamps
  count = ZCARD key               ← count remaining
  if count < limit:
    ZADD key T T                  ← add current timestamp
    allow
  else:
    block
```

Set TTL on the key to window size + buffer so it auto-expires when the user goes idle.

---

### The Memory Problem

The fix of "only add on allow" keeps the list bounded at `limit` entries per user. But the limit itself is the problem.

```
Fixed Window Counter:
  Per user : 1 integer = 8 bytes
  1M users : 8MB

Sliding Window Log (limit = 5 req/min):
  Per user : 5 timestamps × ~58 bytes (value + Redis sorted set overhead)
           = ~290 bytes
  1M users : ~290MB   ← 36× more than Fixed Window

Sliding Window Log (limit = 1000 req/min, like /search at Google scale):
  Per user : 1000 timestamps × 58 bytes = ~58KB
  1M users : 58GB   ← completely unacceptable
```

The memory scales with the **limit**, not just the number of users. A generous limit on a popular endpoint means storing thousands of timestamps per user. At 1M active users with a limit of 1000 req/min, you need 58GB just for rate limit state.

This is why Sliding Window Log is accurate but not production-ready at scale. It solves the correctness problem and introduces a memory problem. The next algorithm fixes the memory problem.

---

### Summary

```
Storage    : sorted set of timestamps per (user + endpoint)
             max entries = limit (never store blocked request timestamps)
Redis ops  : ZREMRANGEBYSCORE + ZCARD + ZADD (3 ops per request)
Accuracy   : perfect — true rolling window, no boundary bug
Memory     : scales with limit × active users
             unusable when limit is large (1000+ req/min)
Best for   : low-limit sensitive endpoints where accuracy matters
             e.g. /login with limit = 5 req/min
Not for    : high-limit endpoints at scale
```
