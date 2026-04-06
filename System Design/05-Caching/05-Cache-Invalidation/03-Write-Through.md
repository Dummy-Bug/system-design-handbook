# Write-Through as Invalidation

> [!info] Instead of deleting the cache key on a write, update it with the new value. The cache is always current, and the next read is a hit — not a miss.

---

## How it differs from event-driven invalidation

Both strategies react to a DB write. The difference is what they do to the cache key:

```
Event-Driven:
  Write to DB → DELETE cache key → next read = MISS → repopulate from DB

Write-Through:
  Write to DB → UPDATE cache key with new value → next read = HIT ✓
```

Event-driven creates one guaranteed miss after every write. Write-through eliminates that miss.

---

## Why this matters at scale

For a heavily read system, that one post-write miss adds up:

```
Instagram profile updates: 1 million/day
Each update → 1 cache miss → DB query

Event-Driven:  1,000,000 extra DB queries per day from post-write misses
Write-Through: 0 extra DB queries — next read always hits cache
```

For read-heavy data that's written frequently and read immediately after, write-through is strictly better.

---

## What's good

```
No cache miss after write         → better for read-heavy systems
Cache always consistent with DB   → no stale window at all
Reads after writes are fast       → user updates profile, sees new value immediately
```

---

## What's bad

```
Write latency increases   → must update both DB and cache synchronously
                            user waits for two writes before getting "success"
Race condition risk        → DB write succeeds, cache update fails
                            → cache has old value, DB has new value
                            → TTL as safety net becomes critical here
Write amplification       → every write updates two systems
```

---

## The race condition

```
T=1: DB write succeeds: Alice balance = $400
T=2: Cache update starts
T=3: Cache update fails (Redis timeout)
     → DB: $400 (correct)
     → Cache: $500 (old value, stale)
     → reads return $500 until TTL expires ✗
```

This is why you should **always set TTL even with write-through**. If the cache update fails, TTL ensures the stale value eventually expires.

---

## When to use write-through vs event-driven

```
Write-Through  → data is read back immediately after write
                 (user updates profile, reads it right away)
                 write frequency is low enough to afford the extra latency

Event-Driven   → data is written more often than it's read back immediately
                 write frequency is high (accepting one miss per write is cheaper)
                 write latency is critical (can't afford the extra cache round trip)
```
