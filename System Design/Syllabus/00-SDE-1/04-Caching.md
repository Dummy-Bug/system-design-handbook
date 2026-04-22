# Caching

## What is Caching and Why It Exists
- The problem caching solves (slow DB reads, repeated expensive computation)
- Cache hit vs cache miss
- Hit ratio — what it means, why above 90% is the target for caching to be worth it
- When caching is not appropriate (real-time prices/inventory, sensitive data)

## Where to Cache
- Browser/client-side cache
- Server-side in-memory cache (local — Guava, Caffeine)
- Distributed cache (Redis) — when local cache is not enough (multiple servers)
- Two-level caching — local L1 + distributed Redis L2 (reduce network hops)

## Cache Population Strategies
- Cache-aside (lazy loading) — app checks cache first, reads DB on miss, populates cache
- Read-through — cache sits in front of DB, loads on miss automatically
- Write-through — write to cache AND DB synchronously (consistent, slower writes)
- Write-back — write to cache only, async persist to DB (fast writes, risk of data loss)
- Write-around — skip cache on write, write directly to DB (for write-once data like logs)

## Cache Eviction Policies
- LRU (Least Recently Used) — evict item not accessed longest. Most common default.
- LFU (Least Frequently Used) — evict item accessed least often. Better for stable hot items (leaderboard).
- FIFO — evict oldest inserted. Rarely used in practice.
- TTL — time-based expiry. Simplest form of invalidation.
- LRU vs LFU — LRU for temporal access patterns, LFU for items that stay hot long-term
- TTL vs eviction policy — TTL expires the key on time, eviction policy decides what to remove when memory is full. Two different mechanisms.

## Cache Invalidation
- TTL — simple, stale window exists, good enough for most cases
- Manual invalidation — delete key on write event
- Why cache invalidation is hard — the moment you write DB and cache separately, there's a window of inconsistency

## Cache Problems (Awareness Level)
- Cache stampede — key expires, many requests hit DB simultaneously. Fix: mutex on miss or probabilistic early expiry.
- Cache avalanche — many keys expire at the same time. Fix: add jitter (randomize TTLs).
- Cache penetration — requests for keys that don't exist bypass cache and hammer DB. Fix: cache null with short TTL, or Bloom filter.
- Cold start — empty cache on deploy. Fix: warm the cache before switching traffic.

## Redis Basics
- What Redis is (in-memory, single-threaded event loop, extremely fast)
- Common data structures and use cases:
  - String — counters, session tokens, simple flags
  - Sorted Set — leaderboards (ZADD, ZRANK, ZRANGE), sliding window rate limiting
  - Hash — user profile fields, shopping cart
  - List — task queues (LPUSH/BRPOP), recent activity
  - Set — unique online users, tags, social connections
- TTL in Redis — EXPIRE command, how it works
- Persistence basics — RDB (snapshots) vs AOF (log every write), why it matters
