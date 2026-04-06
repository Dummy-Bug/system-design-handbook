# FIFO and TTL

---

## FIFO — First In, First Out

> [!info] Evict the item that was inserted earliest, regardless of how often or recently it was accessed.

```
Items inserted in order: A → B → C → D
Cache is full, need to add E:
  → evict A (inserted first)
  → [B, C, D, E]
```

**Why it's almost never the right choice:**

```
A was inserted 10 minutes ago but gets 1,000,000 hits per day
B was inserted 9 minutes ago and has never been accessed again

FIFO evicts A — the hottest key in the cache — because it was inserted first
FIFO doesn't care about access patterns at all
```

Insertion order has no relationship to usefulness. FIFO only makes sense for systems where the oldest data is definitionally the least useful — ordered event processing, message queues, log buffers. For general-purpose caching, never use FIFO.

---

## TTL — Time To Live

> [!info] Time-based expiry. A key is deleted automatically after a set duration, regardless of access patterns or memory pressure.

```
cache.set("user:123:profile", data, TTL=300s)
→ after 300 seconds, key is deleted automatically
→ next request → cache miss → fetches fresh from DB → repopulates
```

---

## TTL vs Eviction — the critical distinction

These are two completely independent mechanisms. Confusing them is a common mistake.

```
TTL      → time-based. Fires after a set duration regardless of memory.
Eviction → memory-based. Fires only when cache is full and needs space.

Same key can have both:
  key = "feed:user:123"
  TTL = 5 minutes          ← deleted after 5 minutes no matter what
  Eviction policy = LRU    ← could be evicted earlier if cache fills up

Scenario 1: cache fills at 3 minutes
  → LRU eviction fires at 3 minutes (before TTL)
  → key is gone at 3 minutes

Scenario 2: cache never fills
  → TTL fires at 5 minutes
  → key is gone at 5 minutes

Whichever fires first wins.
```

---

## Choosing TTL values

TTL is a trade-off between freshness and performance. Too short: frequent cache misses. Too long: stale data served.

```
News feed like count      → TTL = 30s    (stale 30s is invisible to users)
User profile              → TTL = 300s   (stale 5min is acceptable)
Session token             → TTL = 1800s  (matches session timeout)
Bank balance              → TTL = 1s or don't cache (stale is dangerous)
Static assets (JS/CSS)    → TTL = days   (content-addressed, versioned URLs)
```

> [!tip] Always set a TTL as a safety net
> Even if you use event-driven invalidation as your primary strategy, always set a TTL too. If the invalidation event is missed for any reason, the TTL ensures the stale value eventually expires rather than living forever.

---

## TTL jitter — preventing avalanche

If you bulk-load many keys with the same TTL, they all expire simultaneously. The resulting mass cache miss can collapse the DB (covered in depth in Cache Problems). The fix:

```
Instead of: TTL = 300s for all keys
Use:        TTL = 300s + random(0, 60s) for each key

→ expirations spread across a 60-second window
→ DB sees a gentle trickle of misses, not a sudden spike
```

Always add jitter when bulk-loading the cache.
