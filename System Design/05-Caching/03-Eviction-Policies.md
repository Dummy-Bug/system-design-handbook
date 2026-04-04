# Cache Eviction Policies

## The Problem

> [!info] Cache has limited memory. When it's full and a new item needs to be cached, something has to go. Eviction policies decide what gets removed.

> [!important] Eviction and TTL are two separate mechanisms.
> **TTL** — time-based, key deleted when timer runs out regardless of memory pressure.
> **Eviction** — memory-based, triggered only when cache is full and needs space.
> Both can apply to the same key. Whichever fires first wins.

```
key = "feed:user:123"
TTL = 5 minutes       ← deleted after 5 mins regardless
Eviction = LRU        ← could be evicted earlier if cache fills up

→ cache fills at 3 mins → LRU evicts key at 3 mins (before TTL)
→ cache never fills     → TTL deletes key at 5 mins
```

---

## LRU — Least Recently Used

> [!info] Evict the item that was accessed least recently. Most common policy.

```
Cache: [A(oldest access), B, C, D(newest access)]

Cache is full, need to add E
→ evict A (accessed longest ago)
→ Cache: [B, C, D, E]
```

**Why it works:** recent past predicts near future. If you haven't accessed something in a long time, you probably won't need it soon — temporal locality.

**Where it wins:**
```
News feed, search results, user sessions
→ access patterns change over time
→ recent = likely to be accessed again
```

**Where it fails:**
```
2 am report query runs once → now it's "most recently used"
→ evicts your homepage query which runs millions of times daily
→ wrong call
```

**Real world:** Redis default eviction policy. Most common choice in practice.

---

## LFU — Least Frequently Used

> [!info] Evict the item accessed the fewest number of times. Better for stable hot items.

```
Homepage query   → 1,000,000 hits   → high frequency → keep
2am report query → 1 hit            → low frequency  → evict ✓
```

**Where it wins over LRU:**

Database query cache where 10 queries account for 90% of traffic:
```
LRU: 2am report runs once at 2am → "most recently used" → evicts homepage query ✗
LFU: homepage = 1M hits, report = 1 hit → evicts report ✓ → homepage stays cached
```

**Where it fails:**
```
New Year's Eve song → 1,000,000 plays on Dec 31 → massive count
February comes     → nobody plays it anymore
LFU still keeps it → count is too high to evict
→ burns memory on data nobody needs
```

**When to use:** stable, consistently hot data where frequency genuinely reflects ongoing demand — top products, leaderboard, config values.

> [!tip] In practice, pure LFU is rarely used. Most engineers use LRU + TTL and call it a day. Redis supports LFU (allkeys-lfu) but it's rarely configured. For SDE-2 interviews: know both exist, know the difference, say "LRU is the default, LFU is better for stable hot items."

---

## FIFO — First In First Out

> [!info] Evict the oldest inserted item, regardless of how often or recently it was accessed.

```
Items inserted: A → B → C → D
Cache full, need space
→ evict A (first inserted)
```

**Why it's rarely used:**
```
Insertion order ≠ usefulness
A might still be the hottest key in the cache
FIFO doesn't care — it evicts A anyway
```

Only useful for ordered data where recency of insertion genuinely matters. Almost never the right choice in practice.

---

## TTL — Time To Live

> [!info] Time-based expiry. Key is deleted after a set duration regardless of access patterns or memory pressure.

```
cache.set("user:123:profile", data, TTL=300s)
→ after 300 seconds, key is deleted automatically
```

**What's good:**
```
Simple                    → no need to track access patterns
Prevents stale data       → data guaranteed fresh within TTL window
Works as invalidation     → update DB, old cache key just expires
```

**What's bad:**
```
Stale window exists       → data can be up to TTL seconds old
Expiry causes misses      → key expires, next request is a cache miss
Stampede risk             → many keys with same TTL expire simultaneously → DB spike
                            → fix: add jitter to TTL values (covered in Cache Problems)
```

**Use for:** almost everything as a safety net. Even if you use LRU/LFU, always set a TTL so stale data doesn't live forever.

---

> [!important] TTL ≠ eviction. TTL expires keys by time. Eviction removes keys by memory pressure. They are independent — both can apply to the same key.
