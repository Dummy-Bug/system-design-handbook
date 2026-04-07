# TTL-Based Invalidation

> [!info] Set a timer on every cache key. When it expires, the key is deleted automatically. The next request fetches fresh data from the DB and repopulates the cache.

---

## How it works

```
T=0s    → key cached with TTL = 300s
T=10s   → DB updated (user changes profile picture)
T=10s   → cache still has old value ← stale window begins
T=300s  → TTL expires → key deleted automatically
T=301s  → next request → cache miss → fetches fresh from DB → repopulates ✓
```

No code required for invalidation. No infrastructure. The timer does the work.

---

## What's good

```
Simple               → one line when setting the key: cache.set(key, value, TTL=300)
No infrastructure    → no event system, no CDC, no message queues
Works for most data  → slight staleness is acceptable for most use cases
Safety net           → even if other invalidation fails, TTL cleans up eventually
```

---

## The blind spot

TTL doesn't know when the DB changes. It only knows when time expires.

```
User updates profile picture at T=10s
→ DB has new photo
→ cache still has old photo for the next 290 seconds
→ user sees their old photo for almost 5 minutes
```

For data that changes infrequently and where brief staleness is acceptable (news feed counts, leaderboard positions, product descriptions), this is fine. For data that must be fresh immediately after a write (user's own profile, inventory counts), 290 seconds of staleness is too long.

---

## Choosing the right TTL

The TTL is a direct control on how stale data is allowed to get:

```
News feed like count      → TTL = 30s    (stale 30s is invisible)
User profile              → TTL = 300s   (stale 5min is acceptable)
Trending search results   → TTL = 60s    (changes slowly)
Bank balance              → TTL = 1s or don't cache at all
Static assets (JS/CSS)    → TTL = days   (versioned URLs mean content never changes)
```

> [!important] Always set TTL as a safety net
> Even when you use event-driven or write-through invalidation as your primary strategy, always set a TTL too. If the invalidation event is missed for any reason — a bug, a network failure, a deployment gap — TTL ensures the stale value eventually expires rather than living in cache forever.
