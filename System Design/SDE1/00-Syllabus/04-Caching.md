# Phase 4 - Caching

> HLD relevance: caching appears in almost every interview system.
> At SDE-1 level, you should know when to use it, how stale data happens, and what the common failure modes are.

---

### 4.1 Caching fundamentals

- cache expensive reads, computed responses, and hot metadata
- do not cache everything blindly
- local in-process cache vs distributed cache
- cache hit, miss, and hit ratio

### 4.2 Cache read/write strategies

- cache-aside - most common application pattern
- read-through - cache loads data on miss
- write-through - write cache and DB together
- write-around - skip cache on write
- TTL as the default simplification

### 4.3 Cache invalidation

- TTL-based invalidation
- write-triggered invalidation
- stale-while-revalidate intuition
- why invalidation is the hardest caching problem

### 4.4 Distributed caching

- why single-node cache fails at scale
- Redis as the default distributed cache answer
- replication and failover at a high level
- hot keys and skewed traffic
- local L1 + Redis L2 as a common pattern

### 4.5 Cache eviction

- LRU
- LFU
- TTL vs eviction - different concepts

### 4.6 Common cache failure modes

- cache stampede
- cache avalanche
- cache penetration
- cold start after deploy
- hot key meltdown

### 4.7 Redis essentials for interviews

- String - counters, simple values
- Hash - user profile or cart fields
- Sorted Set - leaderboard and sliding-window rate limiting
- Set - uniqueness tracking
- List - simple queue-like usage

### 4.8 What to say in interviews

- "I would start with cache-aside and a TTL"
- "I accept some stale data here because read performance matters more"
- "I would protect against stampede with a mutex or refresh-ahead for hot keys"

