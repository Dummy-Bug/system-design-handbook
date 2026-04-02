## Phase 5 — Caching

> HLD relevance: Caching is mentioned in almost every case study.
> Type-ahead, news feed, chat, URL shortener, leaderboard — all rely on it.

### 4.1 Caching Fundamentals
- What caching is — store expensive results closer to the consumer
- Cache hierarchy — local in-process (Guava/Caffeine) → distributed (Redis) → CDN
- Cache hit vs miss — hit ratio should be above 90% for caching to be worth it
- What to cache — expensive DB queries, computed results, session data, static assets
- What NOT to cache — user-specific highly sensitive data, real-time prices/inventory
- Local in-process cache vs distributed cache — tradeoffs (speed vs consistency across nodes)

### 4.2 Cache Writing Strategies
- Cache-aside (lazy loading) — app checks cache first, reads DB on miss, populates cache
  - Pro: only caches what's needed; Con: first request always slow
- Read-through — cache sits in front of DB, loads on miss automatically
- Write-through — write to cache AND DB synchronously
  - Pro: always consistent; Con: write latency increases
- Write-back (write-behind) — write to cache, async persist to DB
  - Pro: fast writes; Con: data loss if cache crashes before flush
- Write-around — write directly to DB, skip cache
  - Use for write-once data (logs, audit trails)
- Tradeoff table — consistency vs write speed vs data loss risk

### 4.3 Cache Eviction Policies
- LRU (Least Recently Used) — evict item not accessed longest, most common
- LFU (Least Frequently Used) — evict item accessed least often, better for skewed access
- TTL (Time To Live) — time-based expiry, simplest invalidation
- FIFO — evict oldest inserted, rarely used
- When to use LRU vs LFU — LRU for temporal locality, LFU for stable hot items

### 4.4 Cache Invalidation
- Why it's the hardest problem — keeping cache consistent with source of truth
- TTL-based — simple, stale window exists, good enough for most cases
- Event-driven — invalidate on write event (CDC, message queue)
- Write-through as invalidation — always updates cache on write
- Cache versioning — embed version in cache key, old keys naturally expire
- Stale-while-revalidate — serve stale, refresh in background (news feed, type-ahead)

### 4.5 Distributed Caching
- Single-node cache doesn't scale — memory limit, SPOF
- Consistent hashing for distribution — minimal remapping on node add/remove
- Cache coherence — multiple nodes can have different values
- Redis Cluster — 16384 hash slots, gossip protocol
- Replication in cache — read replicas for availability

### 4.6 Cache Problems & Solutions
- Cache stampede (Thundering herd) — key expires, 10k requests hit DB simultaneously
  - Solution: mutex on first miss, probabilistic early expiry, background refresh
- Hot key problem — single key receiving millions of req/sec (celebrity tweet)
  - Solution: replicate hot key across nodes, local in-process replica
- Cold start — empty cache on deploy or flush
  - Solution: cache warming before switching traffic
- Cache penetration — requests for non-existent keys bypass cache, hammer DB
  - Solution: cache null result with short TTL, or Bloom filter at cache layer
- Cache avalanche — many keys expire at the same time, DB gets slammed
  - Solution: add jitter to TTL values, stagger expiry

### 4.7 Redis Deep Dive
- Architecture — single-threaded event loop, why it's incredibly fast
- Data structures and case study usage
  - String — rate limit counters (INCR), session tokens, simple flags
  - Sorted Set — leaderboard (ZADD/ZRANGE), sliding window rate limiting, priority queue
  - List — task queue (LPUSH/BRPOP), recent activity feed
  - Set — unique online users, tags, user social connections
  - Hash — user profile fields, shopping cart
  - HyperLogLog — unique visitor count, distinct search queries
  - Bitmap — daily active user bitmap, feature flag per user
  - Stream — event log with consumer groups (Kafka-lite for lower scale)
- Redis Sentinel — monitors primaries, elects new primary on failure
- Redis Cluster — sharding across nodes via hash slots
- Redis as distributed lock — SET key value NX PX timeout, Redlock for multi-node
- Redis as rate limiter — INCR + EXPIRE for fixed window, Sorted Set for sliding window
- Persistence — RDB (snapshot, small file) vs AOF (every write, durable) vs hybrid
