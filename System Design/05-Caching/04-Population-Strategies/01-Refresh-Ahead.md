# Refresh-Ahead

> [!info] Proactively refresh a cache key before its TTL expires. Users never see a miss on hot keys.

---

## The problem it solves

Without refresh-ahead, when a hot key's TTL expires, the next request hits a cold miss:

```
T=0s   → key cached (TTL = 60s)
T=60s  → key expires → 50,000 simultaneous requests all get a miss
       → all 50,000 hit DB simultaneously → DB spike → stampede
```

This is the cache stampede problem — and it's entirely predictable if you know when the key expires.

---

## How refresh-ahead works

Instead of waiting for the key to expire, a background job detects that expiry is approaching and refreshes the key before it dies.

```
T=0s   → key cached (TTL = 60s)
T=45s  → background job: "this key expires in 15s and it's hot"
       → fetches fresh data from DB
       → updates cache with new value + resets TTL
T=60s  → key would have expired, but it's already been refreshed
       → users keep hitting cache hits, never see a miss ✓
       → DB never sees the expiry spike ✓
```

The refresh threshold is typically **70-80% of TTL**. For a 60s TTL, refresh at ~45s. Too early wastes DB reads. Too late risks a miss window if the refresh is slow.

---

## What's good

```
Zero cache misses on hot keys    → seamless user experience
Prevents stampede on TTL expiry  → DB never sees the expiry spike
Deterministic                    → predictable refresh schedule for known hot keys
```

---

## What's bad

```
May refresh data nobody requests again  → wasted DB reads if the key goes cold
Requires background refresh mechanism  → more operational complexity
Only works for known hot keys           → unpredictable spikes not covered
```

---

## When to use

Refresh-ahead works best when:
- You can identify which keys are hot in advance (high-traffic keys)
- Access patterns are predictable — trending posts, homepage content, leaderboard top 10
- The cost of a miss (stampede on DB) exceeds the cost of proactive refreshes

It does **not** help for unpredictable or one-time spikes — you can't refresh-ahead a key you didn't know would be popular.

> [!tip] Tracking hot keys
> You need to know which keys are worth refreshing ahead. Track keys that are hit more than a threshold per second. If a key is getting 10,000 requests/second, it's worth refreshing proactively. Keys with 1 request/hour — let them expire naturally.
