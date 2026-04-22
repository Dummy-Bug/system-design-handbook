# Caching

## Caching Fundamentals
- Cache hierarchy — local in-process (Guava/Caffeine) → distributed (Redis) → CDN
- Cache hit vs miss — hit ratio should be above 90% for caching to be worth it
- What to cache — expensive DB queries, computed results, session data, static assets
- What NOT to cache — real-time prices/inventory, highly sensitive user data
- Local vs distributed cache — speed vs consistency across nodes

## Cache Writing and Reading Strategies
- Cache-aside (lazy loading) — app checks cache first, reads DB on miss, populates cache
- Read-through — cache sits in front of DB, loads on miss automatically
- Write-through — write to cache AND DB synchronously (consistent, slower writes)
- Write-back (write-behind) — write to cache, async persist to DB (fast, risk of data loss)
- Write-around — write directly to DB, skip cache (write-once data: logs, audit trails)
- Refresh-ahead — proactively refresh cache before TTL expires, avoids miss on hot keys

## Cache Eviction Policies
- LRU (Least Recently Used) — evict item not accessed longest, most common
- LFU (Least Frequently Used) — evict item accessed least often, better for skewed access
- FIFO — evict oldest inserted, rarely used in practice
- TTL (Time To Live) — time-based expiry, simplest invalidation
- LRU vs LFU — LRU for temporal locality, LFU for stable hot items (leaderboard)
- TTL vs eviction policy — TTL expires the key on time, eviction decides what to remove when memory is full. Two different mechanisms.

## Cache Invalidation
- TTL-based — simple, stale window exists, good enough for most cases
- Event-driven — invalidate on write event (CDC, message queue)
- Write-through as invalidation — always updates cache on write
- Cache versioning — embed version in cache key, old keys naturally expire
- Stale-while-revalidate — serve stale, refresh in background (news feed, type-ahead)

## Distributed Caching
- Single-node cache — memory limit, SPOF, doesn't scale horizontally
- Consistent hashing — minimal remapping when nodes added or removed
- Hot key problem — single key receiving millions of req/sec → replicate across nodes, local in-process replica
- Cache coherence — multiple nodes can have different values for the same key
- Two-level caching — local in-process L1 + distributed Redis L2, reduces network hops
- Replication — read replicas for availability
- Handling node failure — consistent hashing minimizes remapping, replicas take over

## Cache Problems and Solutions
- Cache stampede (thundering herd) — key expires, many requests hit DB simultaneously → mutex on miss, probabilistic early expiry
- Cold start — empty cache on deploy → cache warming before switching traffic
- Cache penetration — requests for non-existent keys bypass cache → cache null with short TTL, or Bloom filter
- Cache avalanche — many keys expire simultaneously → add jitter to TTL values

## Redis Deep Dive
**Data structures and use cases:**
- String — rate limit counters (INCR), session tokens, simple flags
- Sorted Set — leaderboard (ZADD/ZRANGE/ZRANK), sliding window rate limiting
- Hash — user profile fields, shopping cart
- List — task queue (LPUSH/BRPOP), recent activity feed
- Set — unique online users, social connections, tags
- HyperLogLog — unique visitor count, distinct search queries (approximate, ~1-2% error)
- Bitmap — daily active users, feature flags per user

**Patterns:**
- Distributed lock — SET key value NX PX timeout
- Rate limiter — INCR + EXPIRE (fixed window), Sorted Set (sliding window)

**Persistence:**
- RDB — periodic snapshots, smaller file, some data loss on crash
- AOF — logs every write, durable, larger file
- Hybrid — both enabled, recommended for production

**Operations:**
- Redis Sentinel — monitors primary, automatically elects new primary on failure
- Redis Cluster — sharding across nodes, 16384 hash slots, gossip-based membership

## Multi-Region Caching

Single-region caching is solved. At SDE-3 the hard problems are: how do you keep caches consistent across regions, and what happens to your cache when a region fails?

**Cross-region cache invalidation**

The problem: user updates their profile in the US region. The EU region's cache still has the old profile. How do you invalidate it?

Three strategies:

- **TTL-based expiry (simplest)** — let EU cache expire naturally. Stale window = TTL duration (e.g., 60 seconds). Acceptable for profile data, social feeds. Not acceptable for inventory, pricing, auth tokens.

- **Pub/Sub invalidation** — US region publishes invalidation event to a global Kafka topic. EU region consumes it and deletes the key from its local Redis.
  - Propagation delay: Kafka cross-region replication ~100–150ms. Short stale window.
  - Risk: invalidation message lost if consumer is down → stale indefinitely. Mitigation: short TTL as a safety net (5 min), so worst case is bounded.
  - Pattern: invalidate on write, not on read. Delete the key, don't overwrite it — let the next read populate from DB (cache-aside).

- **Write-through to all regions (strongest)** — write to remote region's cache directly on every local write.
  - Adds ~150ms latency to every write (cross-region round trip)
  - Only viable for very small, extremely hot datasets (auth session tokens, feature flags)
  - Not practical for user-generated content at scale

**Cache warming on region failover**

The problem: primary region (US-East) goes down. Traffic fails over to US-West. US-West Redis is cold — every request is a cache miss hitting an already-stressed DB.

This is the cold cache thundering herd — and it's one of the most dangerous failure scenarios in multi-region systems.

Three mitigation strategies:

- **Proactive replication** — continuously replicate cache entries from primary region to standby region using Redis replication or a background sync process. On failover, standby cache is warm. Trade-off: doubles cache memory cost, sync lag means standby is slightly stale.

- **Read-through with DB rate limiting** — on failover, add a mutex per cache key so only one request per key hits DB simultaneously. All others wait for the first to populate. Prevents thundering herd but adds latency during warmup.

- **Staggered traffic cutover** — don't route 100% of traffic to the cold region instantly. Use weighted DNS (10% → 25% → 50% → 100%) over several minutes as the cache warms up naturally. Only works if primary is degraded but not fully down.

**Eventual consistency of caches across regions**

Accept it and design around it:
- Define the maximum acceptable stale window per data type (session tokens: 0s, user profiles: 60s, feed content: 5m)
- Use TTL as the ceiling, invalidation events as the floor
- For data that must be globally consistent immediately (auth revocation, account bans) — skip the cache entirely, read from the primary DB with cross-region routing. Accept the latency for correctness.
- Communicate the stale window in your design: "profile cache has a maximum 60s stale window across regions, which is acceptable because profile reads are not safety-critical"
