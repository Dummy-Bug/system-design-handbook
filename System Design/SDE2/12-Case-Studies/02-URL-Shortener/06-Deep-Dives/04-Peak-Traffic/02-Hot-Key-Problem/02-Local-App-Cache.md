
> [!info] Fix 1 — stop the hot key from reaching Redis at all
> The simplest fix for a hot key is to cache it locally on each app server. If the viral URL lives in the app server's own memory, the request never leaves the machine — Redis never sees it.

---

## How it works

Each app server maintains a small in-process cache — a hash map in memory. When a hot key is detected, the app server stores the value locally.

```
Normal flow (cold key):
  Request for x7k2p9
  → check local cache → miss
  → check Redis → hit
  → return long URL

Hot key flow (after promotion):
  Request for x7k2p9
  → check local cache → HIT → return long URL immediately
  → Redis never involved
```

With 10 app servers, each caches the hot URL locally. 1M requests/sec distributed across 10 servers = 100k per server. Each server serves those entirely from local memory. Redis sees zero reads for that key.

---

## Why URL shorteners are perfect for local caching

Local caching has one notorious problem: **cache invalidation**. If the data changes, you need to invalidate the local cache on every app server simultaneously. With no central coordination, stale data can persist.

For most systems this is a real concern. For a URL shortener it is not — because **short URL mappings are immutable**. Once `x7k2p9` maps to a long URL, that mapping never changes. The data you cache locally today is valid forever.

```
Mutable data  → local cache is dangerous (stale reads, invalidation complexity)
Immutable data → local cache is perfect (cache forever, TTL only for memory management)
```

URL shortener data is immutable. Local caching is not just acceptable here — it's ideal.

---

## TTL on local cache entries

Even though the data never becomes stale, you still set a TTL on local cache entries — not for correctness, but for memory management. You don't want your app server's heap filling up with millions of cached URLs.

```
Local cache TTL → 60 seconds (short, just long enough to absorb a spike)
```

After 60 seconds, the entry expires. If the URL is still hot, the next read re-populates it from Redis and re-caches locally. If the spike is over, the entry just expires and memory is freed.

---

## The trade-off

```
Benefit → eliminates Redis load for hot keys entirely, zero network calls
Cost    → uses app server heap memory
         → slight staleness window on deletion (if deletion were in scope)
         → each app server independently decides what to cache
```

For this system — deletion out of scope, immutable data, small TTL — the cost is negligible. The benefit is massive.

---

> [!tip] Interview framing
> "Local app server cache for hot keys — the viral URL gets cached in the app server's own memory. Request never leaves the machine, Redis never sees it. Safe here because URL mappings are immutable — no invalidation problem. Short TTL (60s) for memory management, not correctness."

---

**Next:** Local caching works perfectly for immutable data. But for systems where data can change, you need the second approach — replicating the hot key across multiple Redis nodes using key salting.
