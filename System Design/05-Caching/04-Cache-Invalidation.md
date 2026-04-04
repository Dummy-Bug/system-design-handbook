# Cache Invalidation

## The Problem

> [!info] DB has the truth. Cache has a copy. DB gets updated. Cache still has the old value. How do you keep them in sync?

> [!danger] "There are only two hard things in computer science: cache invalidation and naming things."
> The reason it's hard: cache doesn't automatically know when the DB changes. You have to tell it — or wait for time to expire it.

---

## TTL-Based Invalidation

> [!info] Set a timer. When it expires, the key is deleted. Next request fetches fresh from DB.

```
cache.set("user:123:profile", data, TTL=300s)

T=0s    → key cached
T=300s  → key expires automatically
T=301s  → request comes in → cache miss → fetches fresh from DB → repopulates
```

**What's good:**
```
Simple                  → no extra infrastructure
Works for most cases    → slight staleness is acceptable for most data
```

**The blind spot:**
```
User updates profile at T=10s
TTL expires at T=300s
→ for 290 seconds, cache serves the old profile
→ TTL can't react to DB changes — it only reacts to time
```

**Choosing TTL:**
```
News feed like count   → stale 30s is fine    → TTL = 30s
User profile           → stale 5min is fine   → TTL = 300s
Bank balance           → stale 1s is not fine → don't cache, or TTL = 1s
```

> [!tip] Always set a TTL as a safety net — even if you use other invalidation strategies. Prevents stale data from living forever if something goes wrong.

---

## Event-Driven Invalidation

> [!info] Invalidate the cache key the moment the DB is updated. No stale window.

```
User updates profile
→ write to DB
→ immediately DELETE cache key "user:123:profile"
→ next read → cache miss → fetches fresh → repopulates
```

**What's good:**
```
Cache invalidated instantly     → no stale window
Reacts to DB changes            → not just time
```

**What's bad:**
```
Needs infrastructure            → who triggers the invalidation?
                                  app code, CDC (Change Data Capture), message queue
Delete → miss → repopulate      → one slow request after every write
```

**How to trigger:**
```
App code        → simplest, delete key after every DB write
CDC             → database streams change events (Debezium + Kafka)
                  cache consumer listens and invalidates
Message queue   → write service publishes event, cache service consumes
```

---

## Write-Through as Invalidation

> [!info] Instead of deleting the key on write, update it. No miss after the write.

```
User updates profile
→ write to DB
→ write new value to cache simultaneously
→ next read → cache hit → serves new value directly ✓
```

**Difference from event-driven:**
```
Event-driven    → DELETE key → next read is a miss → repopulates from DB
Write-through   → UPDATE key → next read is a hit  → serves new value directly
```

**What's good:**
```
No cache miss after write       → better for read-heavy systems
Cache always consistent
```

**What's bad:**
```
Write latency increases         → must update both DB and cache synchronously
```

---

## Cache Versioning

> [!info] Instead of invalidating a key, change the key itself. Old keys expire naturally.

```
User 123 profile cached:
  key = "user:123:profile:v1"   value = { name: "John", bio: "old bio" }

User updates bio:
  → write to key = "user:123:profile:v2"
  → old key "v1" untouched, expires naturally via TTL
  → store current version: "user:123:current-version" = "v2"

Read profile:
  1. fetch current version → v2
  2. fetch "user:123:profile:v2" → fresh data ✓
```

**Where it really shines — CDNs:**

```
JS bundle cached at thousands of edge servers worldwide:
  https://cdn.com/app.js      ← old, cached everywhere

Push new version:
  https://cdn.com/app.v2.js   ← new URL, treated as brand new resource everywhere
  old URL expires naturally
```

Why not just push invalidation to CDN edge servers?
```
Thousands of servers worldwide  → slow to propagate (minutes)
Some temporarily unreachable    → inconsistent — some users get old, some get new
Expensive                       → CDN providers charge per invalidation request

Versioned URL sidesteps all of this — new URL = instant freshness everywhere
```

This is why production JS bundles look like `app.a3f9c2.js` — the hash IS the version.

> [!tip] Cache versioning is best for CDN static assets. For DB-backed data, event-driven or write-through is simpler — the two-step version lookup adds unnecessary complexity.

---

## Stale-While-Revalidate

> [!info] TTL expires, request comes in — serve stale immediately, refresh in background. User never waits.

```
Normal TTL expiry:              Stale-while-revalidate:
  key expires                     key expires
  → cache miss                    → serve stale immediately ✓ (fast response)
  → user waits for DB fetch       → background job fetches fresh from DB
  → slow response                 → cache updated
                                  → next request gets fresh data
```

**Difference from refresh-ahead:**
```
Refresh-ahead           → proactive, refreshes BEFORE TTL expires
                          no miss at all, zero stale responses

Stale-while-revalidate  → reactive, triggered AFTER TTL expires on a request
                          one stale response, then fresh
```

**Use when:** slight staleness on one request is acceptable:
```
News feed       → showing feed from 2 seconds ago is fine ✓
Type-ahead      → slightly stale suggestions are fine ✓
Leaderboard     → rank from 5 seconds ago is fine ✓
```

**Don't use when:**
```
Bank balance    → stale even for one request is unacceptable ✗
Inventory       → stale stock count could cause overselling ✗
```

---

## The Full Picture

```
TTL-based               → simple, time-based, stale window exists — always set as safety net
Event-driven            → instant invalidation on DB write, needs infrastructure
Write-through           → update cache on write, no miss after write, slower writes
Cache versioning        → change the key, old keys expire naturally — best for CDN
Stale-while-revalidate  → serve stale, refresh in background — good for feeds and type-ahead
```

> [!important] Most production systems combine strategies:
> TTL as the safety net + event-driven for critical data + stale-while-revalidate for feeds.
> No single strategy fits everything — choose per data type.
