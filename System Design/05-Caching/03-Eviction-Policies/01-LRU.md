# LRU — Least Recently Used

> [!info] Evict the item that was accessed least recently. The default eviction policy and the right choice for most systems.

---

## How it works

LRU tracks the last access time for every key in the cache. When the cache is full and a new item needs to be stored, the key that was accessed longest ago gets evicted.

```
Cache state (ordered by last access, oldest first):
  [A — 10min ago, B — 5min ago, C — 1min ago, D — just now]

Cache is full, need to add E:
  → evict A (accessed longest ago)
  → [B — 5min ago, C — 1min ago, D — just now, E — just now]
```

---

## Why it works — temporal locality

The underlying assumption is **temporal locality**: if you accessed something recently, you're likely to access it again soon. If you haven't accessed something in a long time, you probably won't need it soon either.

This assumption holds for most real-world access patterns:
- A user scrolling their feed reads the same posts multiple times in one session
- Popular products on an e-commerce site keep getting viewed
- A trending tweet gets read millions of times in a short window

LRU keeps these hot items in cache and evicts the stale ones.

---

## Where LRU wins

```
News feed        → users repeatedly view the same recent posts in one session
Search results   → same query often repeated in a short window
User sessions    → active users keep hitting their session data
Homepage content → same trending content viewed by many users
```

---

## Where LRU fails

```
2am batch report runs once:
  → query executed → result now "most recently used" → stays in cache
  → evicts your homepage query that runs millions of times daily
  → LRU made the wrong call: recency ≠ importance
```

Any one-off operation can push important stable keys out of cache if LRU doesn't know those keys are permanently hot.

---

## Implementation

LRU is typically implemented with a **doubly linked list + hash map**:
- Hash map: O(1) key lookup
- Doubly linked list: O(1) move-to-front on access, O(1) evict from tail

Every cache access moves that key to the front. The tail is always the LRU candidate.

**Redis default:** `allkeys-lru` or `volatile-lru` (only keys with TTL). LRU is what Redis uses out of the box.
