# Two-Level Caching (L1 + L2)

> [!info] Local in-process cache (L1) + distributed Redis cache (L2). L1 is nanoseconds but per-server only. L2 is ~1ms but shared across all servers. Together they give you the speed of local memory with the consistency of a shared cache.

---

## The problem with Redis alone

Redis is fast — ~1ms round trip. But at extreme read volume, even 1ms adds up:

```
100,000 reads/second × 1ms = 100 seconds of Redis round-trip time per second
→ Redis becomes the bottleneck
→ Redis connection pool saturated
→ reads start queuing
```

And each Redis read is a network call — CPU, network overhead, serialization. For data that doesn't change often, this is wasteful.

---

## How two-level caching works

Add a local in-process cache (L1) on each app server. Check L1 first. Only go to Redis (L2) on an L1 miss. Only go to the DB on an L2 miss.

```
Request arrives at app server
  → check L1 (local, nanoseconds)
     → HIT → return immediately ✓ (no network call at all)
     → MISS → check L2 (Redis, ~1ms)
        → HIT → store in L1 → return ✓
        → MISS → query DB (~10ms)
           → store in L2 → store in L1 → return ✓
```

For hot keys that every server reads constantly, L1 eliminates the Redis round trip entirely.

---

## L1 characteristics

```
Speed:       nanoseconds (memory access on same JVM/process)
Scope:       per server only — each app server has its own L1
Capacity:    small — typically 100MB-1GB (bounded by app server RAM)
Consistency: weaker — each server's L1 can drift from Redis
```

**The invalidation problem:** when data changes in Redis (L2), all the L1 caches on every app server still have the old value.

```
User updates profile:
  → Redis updated ✓
  → App Server 1 L1: old value ✗
  → App Server 2 L1: old value ✗
  → App Server 3 L1: old value ✗
```

**Fix 1 — Short TTL on L1 entries:**
```
L1 TTL = 5 seconds
→ stale for at most 5 seconds per server
→ simple, no extra infrastructure
→ acceptable for most data
```

**Fix 2 — Pub/Sub invalidation:**
```
Data changes in Redis
→ Redis publishes invalidation event to a channel
→ all app servers subscribe to the channel
→ each server clears its L1 entry immediately ✓
→ zero stale window, more complex infrastructure
```

---

## Who uses two-level caching

Instagram, Twitter, and most large-scale systems use L1 + L2 in production. The numbers justify it:

```
Without L1: 100,000 reads/sec → 100,000 Redis calls/sec
With L1 (80% hit rate): 20,000 Redis calls/sec → 5x reduction in Redis load
```

> [!tip] Interview framing
> "I'd add a local in-process cache (Caffeine/Guava) as L1 with a 5-second TTL for hot keys. Redis serves as L2. Most reads hit L1 and never touch Redis — significantly reduces Redis load at scale. L1 staleness is at most 5 seconds, which is acceptable for feed and profile data."
