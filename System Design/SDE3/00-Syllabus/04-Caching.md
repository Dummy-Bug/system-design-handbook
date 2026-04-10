# Phase 4 - Caching

> HLD relevance: caching appears in almost every system, but at SDE-3 level the bar is not "add Redis".
> You should be able to explain what to cache, where to cache it, how it becomes stale, how it fails under skew, and what consistency guarantees the product actually needs.

### SDE-3 depth bar for this phase
- Know the common cache patterns and their write-path tradeoffs.
- Explain cache correctness, not just cache speed.
- Be able to discuss multi-layer caching, hotspot management, and cache failure modes under real load.
- Tie caching choices to product semantics like read-your-writes, staleness windows, and operational cost.

### 4.1 Caching Fundamentals
- What to cache: expensive DB reads, derived responses, hot metadata, rendered fragments, static assets.
- What not to cache: highly sensitive data, fast-changing correctness-critical state, write-heavy values with low reuse.
- Local in-process cache vs distributed cache vs CDN.
- Hit ratio, miss ratio, and why a cache with poor hit ratio can cost more than it saves.
- Working set size vs total dataset size.

### 4.2 Cache Writing and Reading Strategies
- Cache-aside: simplest and most common; app owns miss handling.
- Read-through: cache layer loads from backing store on miss.
- Write-through: keep DB and cache aligned synchronously; safer reads, slower writes.
- Write-back / write-behind: fastest writes, more risk on crash.
- Write-around: avoid polluting cache with write-only data.
- Refresh-ahead: proactively warm hot keys before TTL expiry.
- Senior-level depth: explain which pattern you would choose and why for feed, payment, leaderboard, or profile systems.

### 4.3 Cache Eviction Policies
- LRU for temporal locality.
- LFU for stable skew and long-lived hot items.
- FIFO as a baseline but rarely ideal.
- TTL as expiry, not really an eviction policy.
- Memory pressure, eviction churn, and how policy interacts with workload.

### 4.4 Cache Invalidation
- TTL-based invalidation as the default simplification.
- Event-driven invalidation using write events or CDC.
- Write-through as an implicit invalidation strategy.
- Versioned keys and namespace bumping during deploys.
- Stale-while-revalidate for low-risk reads.
- Senior-level depth: describe acceptable staleness window and what user-visible inconsistency it creates.

### 4.5 Distributed Caching
- Why one cache node becomes a bottleneck.
- Sharding across cache nodes.
- Consistent hashing to reduce key remapping during scale events.
- Replication and failover.
- Two-level caching: local L1 + distributed L2.
- Cache cluster rebalance and warm-up concerns after node add / remove.

### 4.6 Cache Correctness and Coherence
- Read-your-writes problems when cache and DB are not updated in the same path.
- Multi-node coherence issues when each app instance has local cache.
- Replica lag plus cache can compound staleness.
- Serving stale data intentionally vs accidentally.
- Product-level decision: stale feed is okay, stale payment balance is not.

### 4.7 Cache Problems and Solutions
- Stampede / thundering herd on hot-key expiry.
- Avalanche when many keys expire together.
- Penetration when nonexistent keys keep hitting origin.
- Cold start after deploy or failover.
- Hot key meltdown where one key becomes the whole system's bottleneck.
- Common mitigations: request coalescing, mutex on miss, TTL jitter, negative caching, local replication of ultra-hot items.

### 4.8 Scaling Cache Infrastructure
- Hot-key replication.
- Pinning or special-casing skewed keys.
- Tiered cache with edge + local + distributed layers.
- Memory economics: do not cache everything just because you can.
- Cache observability: hit ratio, miss latency, eviction rate, hot-key detection.

### 4.9 Redis Deep Dive
- Strings, hashes, lists, sets, sorted sets, bitmaps, HyperLogLog.
- Sorted sets for leaderboards and sliding-window rate limiting.
- Atomic operations, Lua scripts, and why race-free multi-step ops matter.
- Pipelining and batching.
- Persistence awareness: RDB, AOF, hybrid.
- Sentinel and Cluster awareness.
- Distributed lock caveat: lease expiry and fencing problems.

### 4.10 What SDE-3 Should Be Comfortable Saying
- "I would start with cache-aside, but I need to call out the stale-read window explicitly."
- "This cache helps p99 only if the hot working set actually fits in memory."
- "I need a hot-key strategy here because celebrity traffic will dominate one key."
- "I would not promise read-your-writes from cache unless the write path updates it synchronously or versions the data."
