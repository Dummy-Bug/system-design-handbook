# Phase 5 — Caching

> [!abstract] Caching is mentioned in almost every case study. Type-ahead, news feed, chat, URL shortener, leaderboard — all rely on it. Know it well.

---

### 5.1 — Caching Fundamentals

*Store expensive results closer to the consumer*

- What caching is — avoid recomputing or re-fetching expensive results
- Cache hierarchy — local in-process (Guava/Caffeine) → distributed (Redis) → CDN
- Cache hit vs miss — hit ratio should be above 90% for caching to be worth it
- What to cache — expensive DB queries, computed results, session data, static assets
- What NOT to cache — real-time prices/inventory, highly sensitive user data
- Local vs distributed cache — speed vs consistency across nodes
- [[05-Caching/01-Fundamentals|Notes →]]

---

### 5.2 — Cache Writing Strategies

*When do you write to the cache? When do you skip it?*

- Cache-aside (lazy loading) — app checks cache first, reads DB on miss, populates cache
- Read-through — cache sits in front of DB, loads on miss automatically
- Write-through — write to cache AND DB synchronously (consistent, slower writes)
- Write-back (write-behind) — write to cache, async persist to DB (fast, risk of data loss)
- Write-around — write directly to DB, skip cache (write-once data: logs, audit trails)
- [[05-Caching/02-Writing-Strategies|Notes →]]

---

### 5.3 — Cache Eviction Policies

*Cache is full — what gets thrown out?*

- LRU (Least Recently Used) — evict item not accessed longest, most common
- LFU (Least Frequently Used) — evict item accessed least often, better for skewed access
- TTL (Time To Live) — time-based expiry, simplest invalidation
- LRU vs LFU — LRU for temporal locality, LFU for stable hot items (leaderboard)
- [[05-Caching/03-Eviction-Policies|Notes →]]

---

### 5.4 — Cache Invalidation

*The hardest problem in caching — keeping cache consistent with the DB*

- TTL-based — simple, stale window exists, good enough for most cases
- Event-driven — invalidate on write event (CDC, message queue)
- Write-through as invalidation — always updates cache on write
- Cache versioning — embed version in cache key, old keys naturally expire
- Stale-while-revalidate — serve stale, refresh in background (news feed, type-ahead)
- [[05-Caching/04-Cache-Invalidation|Notes →]]

---

### 5.5 — Distributed Caching

*Single node doesn't scale — how do you distribute a cache?*

- Single-node cache — memory limit, SPOF, doesn't scale horizontally
- Consistent hashing — minimal remapping when nodes are added or removed
- Cache coherence — multiple nodes can have different values for the same key
- Replication — read replicas for availability, not just scale
- [[05-Caching/05-Distributed-Caching|Notes →]]

---

### 5.6 — Cache Problems & Solutions

*Five failure modes every interviewer asks about*

- Cache stampede (thundering herd) — key expires, 10k requests hit DB simultaneously → mutex on miss, probabilistic early expiry
- Hot key — single key receiving millions of req/sec (celebrity tweet) → replicate across nodes, local in-process replica
- Cold start — empty cache on deploy → cache warming before switching traffic
- Cache penetration — requests for non-existent keys bypass cache → cache null with short TTL, or Bloom filter
- Cache avalanche — many keys expire simultaneously → add jitter to TTL values
- [[05-Caching/06-Cache-Problems|Notes →]]

---

### 5.7 — Redis

*The standard distributed cache — know its data structures and when to use each*

**Must know — data structures:**
- String — rate limit counters (INCR), session tokens
- Sorted Set — leaderboard (ZADD/ZRANGE), sliding window rate limiting
- Hash — user profile fields, shopping cart
- List — task queue (LPUSH/BRPOP), recent activity feed
- Set — unique online users, social connections

**Must know — patterns:**
- Redis as distributed lock — SET key value NX PX timeout
- Redis as rate limiter — INCR + EXPIRE (fixed window), Sorted Set (sliding window)
- Redis Sentinel — monitors primary, elects new primary on failure

**Nice to know (not required for L4):**
- HyperLogLog, Bitmap, Stream — niche, case-study specific
- Redis Cluster hash slot internals — SDE-3 territory
- RDB vs AOF persistence — know they exist, don't deep dive
- [[05-Caching/07-Redis|Notes →]]
