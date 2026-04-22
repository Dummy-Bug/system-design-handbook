# Cold Start

> [!info] The cache is completely empty. Fresh deployment, Redis restart, new region. Every request is a cache miss. The DB sees 100% of production traffic instead of its usual 5%.

---

## How it happens

```
Scenario 1: Fresh deployment
  New Redis instance spun up → 0 keys
  Traffic switches to new instance
  → every request → cache miss → hits DB
  → DB absorbs full production traffic
  → DB that normally handles 5% of reads now handles 100% → collapses

Scenario 2: Redis restart (OOM kill, upgrade)
  All keys lost from memory
  Same result

Scenario 3: New region launch
  Cache in new region is empty
  First users in that region → all cache misses
  → DB in that region (or cross-region DB) hammered
```

---

## How cold start differs from stampede

Same symptom (DB hammered), completely different cause:

```
Cache Stampede → one popular key expires → one burst of misses → recovers quickly
Cold Start     → entire cache is empty  → every key misses → sustained DB load
                                           until cache gradually fills up (minutes)
```

Cold start is sustained. A stampede is a spike. Cold start can last minutes; a stampede resolves in seconds once one request repopulates the key.

---

## Fix — Cache Warming

Pre-populate the cache before opening traffic.

```
Before switching traffic to new cache instance:
  Step 1 → analyse yesterday's access logs → identify top-N most-requested keys
  Step 2 → fetch those values from DB
  Step 3 → write them all into the new cache
  Step 4 → open traffic

First real request → cache hit ✓ (key was pre-loaded)
DB → never sees the cold-start spike
```

**How to identify what to warm:**
```
Access log analysis      → replay yesterday's requests, top keys by frequency
Traffic shadowing        → mirror production reads to new instance before cutover
Popularity tracking      → maintain a sorted set of most-accessed keys in Redis,
                           use this list to seed new instances
```

**Netflix approach:** pre-warm caches for new regions with the top trending content before the region goes live. The first user in São Paulo should hit a warm cache, not a cold DB in Virginia.

> [!tip] Interview framing
> "On deploy I'd warm the cache before switching traffic — fetch the top-N keys from the DB based on yesterday's access patterns and load them into the new instance. This prevents the cold-start DB spike that would otherwise occur when every initial request misses."
