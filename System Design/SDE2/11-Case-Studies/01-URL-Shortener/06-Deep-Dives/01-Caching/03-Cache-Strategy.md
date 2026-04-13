
> [!info] The question
> We know the cache size (~27GB) and the hit rate target (80%). Now we need to decide: when do entries go into the cache, and how do they get there? There are three main strategies — and each has a different trade-off.

---

## The three caching strategies

### Write-through

Every time a URL is created, it gets written to both the DB and the cache simultaneously.

```
User creates URL
→ App server writes to DB
→ App server writes to Redis
→ Returns short URL to user
```

**The problem:** You're caching every URL on creation — including ones that will never be clicked more than once. If 90M URLs are created per day and most go cold immediately, you're filling your cache with useless entries. Every new URL pollutes the cache, pushing out hot entries that are actually being read.

Write-through makes sense when you know the data will be read — it doesn't make sense here because most created URLs never go viral.

---

### Write-around

Only write to the DB on creation. The cache stays out of it entirely. An entry only enters the cache when it is first read — i.e., when someone actually clicks the link.

```
User creates URL
→ App server writes to DB only
→ Cache is not touched

First click on bit.ly/x7k2p9
→ Cache miss → App server queries DB → gets long URL
→ App server writes entry to cache
→ Returns 301 to user

All subsequent clicks
→ Cache hit → returns long URL from Redis
→ DB never involved
```

**Why this is better:** The cache only fills up with URLs that are actually being clicked. A URL that gets created and never clicked never enters the cache. Only URLs with real traffic earn their spot. This is exactly the behaviour you want for a URL shortener.

**The trade-off:** The very first click on any URL always misses the cache. The user who first clicks a viral link gets a slightly slower response (DB read instead of cache read). Every click after that is fast. This is acceptable — the first-click penalty is negligible compared to the benefit of a clean cache.

---

### Write-back (write-behind)

Write to the cache first, and asynchronously persist to the DB later.

```
User creates URL
→ App server writes to cache
→ Returns short URL immediately
→ DB write happens asynchronously in background
```

**Why this is wrong here:** If the cache dies before the async DB write completes, the URL is lost permanently. A URL shortener has a strict durability requirement — once a short URL is created, it must never be lost. Write-back violates this. Never use write-back when durability matters.

---

## The decision — write-around

Write-around is the right strategy:

```
Creation  → write to DB only, skip cache
Redirect  → check cache first, miss goes to DB, then populate cache
```

---

## TTL — when do entries expire?

Every cache entry gets a TTL of **3 days**. After 3 days, the entry is automatically deleted from Redis.

Why 3 days? Because that's the active window — URLs stay hot for roughly 3 days. After that, they go cold and don't deserve cache space.

```
URL created and clicked → enters cache with TTL=3 days
3 days pass → entry expires automatically
Next click → cache miss → DB hit → re-enters cache with fresh 3-day TTL
```

If a URL that expired gets clicked again, it re-enters the cache. This is correct — a URL that goes dormant for a week and then gets viral again should re-enter the cache.

---

## Cache update — sync or async?

On a cache miss, the app server queries the DB and gets the long URL. When should it write that result back to the cache?

**Sync (before responding to the user):**
```
Cache miss → DB query → write to cache → return 301 to user
```
The user waits for both the DB query and the cache write before getting their redirect.

**Async (after responding to the user):**
```
Cache miss → DB query → return 301 to user → write to cache in background
```
The user gets their redirect immediately. The cache write happens after.

Async is better here. The user's redirect is not blocked by the cache write. In the worst case — app server dies after returning the 301 but before writing to cache — the next user who clicks the same link gets another cache miss and hits the DB again. No data is lost, the URL is still in the DB. The only consequence is one more DB read.

---

> [!tip] Interview framing
> "Write-around caching — only URLs that get clicked enter the cache, not every URL on creation. This keeps the cache clean and hot. 3-day TTL matches the active window. Cache updates on miss are async — user gets the redirect immediately, cache population happens in the background. Worst case on async failure is one extra DB read, not data loss."

---

**Next:** TTL handles absolute expiry. But what happens when the cache fills up before TTLs expire? That's where the eviction policy comes in.
