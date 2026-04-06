# Stale-While-Revalidate

> [!info] When a key expires, serve the stale value immediately to the current request, while refreshing the cache in the background. The user never waits. The next request gets fresh data.

---

## The problem with normal TTL expiry

With regular TTL, when a key expires the next request hits a cold miss:

```
T=60s → TTL expires
       → request comes in → cache miss
       → user waits while DB is queried (10-50ms)
       → cache repopulated
       → user finally gets a response
```

For a high-traffic key, this is a stampede in the making. And even for a moderate key, the user who happened to arrive at the expiry moment gets a slow response.

---

## How stale-while-revalidate works

```
T=60s → TTL expires
       → request comes in
       → serve stale value immediately ✓ (user gets fast response)
       → background: fetch fresh data from DB
       → update cache with fresh value
       → next request → hits fresh value ✓
```

The user who triggers the miss gets the stale value instead of waiting. One request gets slightly stale data. Every subsequent request gets fresh data.

---

## How it differs from Refresh-Ahead

Both strategies aim to avoid making a user wait on a cache miss. The difference is timing:

```
Refresh-Ahead (proactive):
  T=45s → key still alive, 15s remaining
         → background refresh fires → fetches DB → updates cache
  T=60s → key would expire but it's already fresh
         → zero stale responses ever ✓

Stale-While-Revalidate (reactive):
  T=60s → key expires → request arrives
         → serve stale to this request (one stale response)
         → background refresh fires → fetches DB → updates cache
         → next request → fresh ✓
```

Refresh-Ahead is strictly better for user experience — zero stale responses — but requires knowing which keys are hot in advance. Stale-While-Revalidate works for any key without prior knowledge.

---

## When to use

```
✓ News feeds       → 2 seconds stale is invisible to users
✓ Type-ahead       → slightly stale suggestions are fine
✓ Leaderboards     → rank from 5 seconds ago is acceptable
✓ Search results   → freshness within seconds is enough

✗ Bank balance     → stale even once is incorrect
✗ Inventory count  → stale can cause overselling
✗ User's own data  → user expects to see their own changes immediately
```

The key question: **is one stale response acceptable for this data type?** If yes, stale-while-revalidate is a clean solution with no extra infrastructure.

> [!tip] Interview framing
> "For the news feed I'd use stale-while-revalidate — when a cache key expires, we serve the stale feed immediately while refreshing in the background. Users don't notice one slightly stale feed load, but they do notice waiting 50ms on a DB query."
