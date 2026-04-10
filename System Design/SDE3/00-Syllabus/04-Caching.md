# Phase 4 - Caching

> HLD relevance: at SDE-3 level, caching is not just "add Redis".
> You need to reason about coherence, invalidation, economics, and failure behavior under skew.

---

### 4.1 Cache hierarchy

- client cache
- CDN
- local in-process cache
- distributed cache
- database page cache awareness

### 4.2 Caching strategies

- cache-aside
- read-through
- write-through
- write-back / write-behind
- write-around
- refresh-ahead

### 4.3 Invalidation strategies

- TTL
- event-driven invalidation
- cache versioning
- stale-while-revalidate
- explicit write-through invalidation

### 4.4 Distributed caching

- single node limits
- cluster mode
- consistent hashing
- replication and failover
- two-level cache patterns

### 4.5 Cache correctness

- stale reads
- read-your-writes issues
- coherence across fleets
- when serving stale data is acceptable
- when stale data is dangerous

### 4.6 Cache failure modes

- stampede
- avalanche
- penetration
- cold start
- hot key amplification

### 4.7 Hotspot management

- hot-key replication
- local replication for ultra-hot reads
- request coalescing / single-flight
- admission control when cache misses become dangerous

### 4.8 Eviction and memory economics

- LRU
- LFU
- TTL vs eviction
- memory pressure tradeoffs
- what to keep hot and what to let miss

### 4.9 Redis depth for senior interviews

- strings, hashes, lists, sets, sorted sets
- counters and rate limiting
- sorted sets for leaderboards and sliding windows
- persistence awareness - RDB, AOF, hybrid
- Sentinel and Cluster awareness

