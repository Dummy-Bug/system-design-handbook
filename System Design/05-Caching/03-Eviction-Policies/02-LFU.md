# LFU — Least Frequently Used

> [!info] Evict the item accessed the fewest number of times. Better than LRU when some items are permanently hot regardless of when they were last accessed.

---

## How it works

LFU tracks the total access count for every key. When the cache is full and something must be evicted, the key with the lowest access count is removed.

```
Cache state (ordered by access count):
  [homepage_query: 1,000,000 hits, product_123: 50,000 hits, 2am_report: 1 hit]

Cache is full, need to add new key:
  → evict 2am_report (lowest frequency: 1 hit) ✓
  → homepage_query stays ✓ (it's permanently hot)
```

---

## Where LFU wins over LRU

The classic failure case for LRU is a one-off operation polluting the cache:

```
Database query cache:
  10 queries account for 90% of all traffic — permanently hot

LRU behaviour:
  2am report runs once at 2:00am
  → result is now "most recently used"
  → LRU evicts the homepage query (accessed 5 minutes ago)
  → homepage query: 1,000,000 hits per day → now a miss ✗

LFU behaviour:
  2am report: 1 hit
  homepage query: 1,000,000 hits
  → LFU evicts 2am report ✓
  → homepage query stays ✓
```

LFU correctly identifies that access count, not recency, is what matters for stable query caches.

---

## Where LFU fails

```
New Year's Eve song:
  December 31: 1,000,000 plays → enormous frequency count
  February 1: nobody plays it anymore, but LFU count is still 1,000,000
  → LFU refuses to evict it → burns cache memory on stale data

New product launch:
  Day 1: new product page has 0 historical hits
  → LFU evicts it immediately even though it's actively being browsed
  → frequency count hasn't caught up to actual current demand
```

LFU is slow to adapt to changing access patterns. It treats historical frequency as a permanent indicator of future demand.

---

## Practical reality

In practice, pure LFU is rarely used in production. Most engineers use **LRU + TTL** as the combination — LRU for eviction, TTL as a safety net to prevent truly stale items from accumulating.

Redis supports LFU (`allkeys-lfu`, `volatile-lfu`) but it requires explicit configuration. The default is LRU.

**When to actually configure LFU:** query caches with a stable set of hot queries, leaderboard data, config values — anything where frequency genuinely reflects permanent demand and access patterns don't change seasonally.

> [!tip] Interview framing
> "LRU is the default — it works well when recent access predicts future access. I'd switch to LFU for a query cache where the same 10 queries run millions of times daily — LFU keeps those hot permanently, whereas LRU can incorrectly evict them if a one-off batch job runs."
