# Eviction Policies — Interview Cheatsheet

---

## The default answer

> [!tip] LRU + TTL is the right answer for almost everything. Say this first, then explain when you'd deviate.

---

## Policy selector

| Access pattern | Policy | Reason |
|---|---|---|
| General purpose, sessions, feeds | LRU | Recent access predicts future access |
| Stable hot data, query cache | LFU | Frequency better predicts demand than recency |
| Ordered processing, log buffers | FIFO | Insertion order matters |
| Any cache, always | TTL as safety net | Prevents stale data living forever |

---

## One-line definitions

> [!info] LRU (Least Recently Used)
> Evict the key not accessed for the longest time. Default policy. Best when recent access predicts future access.

> [!info] LFU (Least Frequently Used)
> Evict the key with the lowest total access count. Better when some keys are permanently hot regardless of recency.

> [!info] FIFO (First In First Out)
> Evict the oldest inserted key. Almost never appropriate for caching — insertion order ≠ usefulness.

> [!info] TTL (Time To Live)
> Time-based expiry, independent of eviction. Always set as a safety net.

---

## The key distinction to state

> [!important] TTL ≠ Eviction — say this explicitly
> "TTL expires keys by time. Eviction removes keys by memory pressure. They're independent mechanisms — the same key can have both, and whichever fires first wins."

---

## Interview framing

> "I'd configure Redis with LRU eviction and set TTL on every key as a safety net. For the query cache specifically, I'd use LFU — the same 10 queries account for 90% of traffic, and LFU keeps those permanently hot even if a one-off batch job runs and would otherwise push them out under LRU."
