# Cache Problems

## Cache Stampede

> [!info] A hot key's TTL expires. Thousands of requests arrive at the same moment — all get a cache miss simultaneously. All of them go to the DB at once.

```
Normal flow:
  request → cache hit → done ✓

Stampede:
  key expires at T=300s
  10,000 requests arrive at T=300s
  → all get cache miss
  → all fetch from DB simultaneously
  → DB gets 10,000 queries instead of 1
  → DB collapses
```

The problem isn't the cache miss itself. It's the thundering herd — thousands of identical DB queries happening in parallel because nobody coordinated.

---

**Fix 1 — Refresh-Ahead**

Don't wait for the key to expire. Refresh it proactively before it dies.

```
Key TTL = 60s
At T=45s → background job detects key is about to expire
         → fetches fresh data from DB
         → updates cache
At T=60s → key would have expired, but it's already been refreshed

Users never see a miss. DB never sees the spike.
```

How do you know which keys to refresh ahead? You track which keys are being hit frequently. If a key is getting thousands of hits per second, it's worth refreshing before it expires. Low-traffic keys — let them expire naturally.

> [!tip] Refresh-ahead is proactive. You need to know in advance which keys are hot. Works great for predictable traffic — trending posts, homepage content, leaderboard top 10. Doesn't help for unpredictable spikes.

---

**Fix 2 — Mutex with Double-Checked Locking**

When a key expires, only let one request fetch from DB. The rest wait.

```
Key expires → 10,000 requests get cache miss
→ all try to acquire lock
→ one request wins the lock
→ the other 9,999 wait

Winner: fetches from DB → writes to cache → releases lock
Waiters: wake up → check cache again → hit ✓ → return immediately
```

The critical detail: waiters must **check the cache again** after acquiring the lock. This is double-checked locking.

```
Without double-check:
  waiter acquires lock → fetches from DB → writes to cache → releases
  next waiter acquires lock → fetches from DB again → and again → and again
  → all 9,999 still hit DB sequentially
  → DB doesn't collapse but is still hammered

With double-check:
  waiter acquires lock → checks cache → HIT → returns immediately
  → DB gets exactly 1 query total
```

```
function get(key):
  value = cache.get(key)
  if value: return value          ← first check (no lock)

  lock.acquire(key)
    value = cache.get(key)        ← second check (inside lock)
    if value:
      lock.release()
      return value                ← someone else already fetched it

    value = db.fetch(key)
    cache.set(key, value)
    lock.release()
    return value
```

> [!important] The second cache check inside the lock is what makes this work. Without it, you've serialised the DB queries instead of eliminating them. With it, DB gets exactly one query no matter how many concurrent waiters there are.

---

**Fix 3 — Probabilistic Early Expiry**

Instead of refreshing at a fixed threshold (e.g. 75% of TTL), each request near the end of TTL flips a coin. If it wins, it refreshes early.

```
TTL = 60s. Key has 10s remaining.
Each request near expiry: flip a coin
  → heads (20% chance) → this request refreshes the cache proactively
  → tails → serve stale, do nothing

As TTL approaches zero → more requests win the coin flip
→ cache gets refreshed before it expires
→ no thundering herd
```

No coordination needed. No locks. The randomness spreads the refresh load naturally.

---

## Cold Start

> [!info] Cache is completely empty. Fresh deployment, Redis restart, new region. Every request is a cache miss. DB sees 100% of traffic.

```
New cache deployed → 0 keys
→ every request → cache miss → hits DB
→ DB sees full production traffic instead of the usual 5%
→ DB collapses
```

Same symptom as stampede — DB getting hammered. Different cause. Stampede is one key dying. Cold start is nothing ever existed to begin with.

**Fix — Cache Warming**

Before opening traffic to the new cache, pre-populate it.

```
Before launch:
  → run a script: read top N most popular keys from DB
  → write them all into cache
  → then open traffic

Users hit cache → already warm → DB never sees the spike
```

How do you know which keys to warm? Replay yesterday's access logs. If those keys were hot yesterday, they'll be hot today. Start with homepage content, top products, trending posts — whatever your most-requested data is.

---

## Cache Penetration

> [!info] Requests for keys that don't exist in the DB. Every request is a cache miss. Every request hits DB. DB returns null. Nothing gets cached. Cycle repeats forever.

Normal cache miss resolves itself — fetch from DB, store in cache, next request is a hit.

Penetration never resolves:

```
Attacker sends: GET /user/99999999 (user doesn't exist)
→ cache miss
→ fetch from DB → DB returns null
→ nothing to cache
→ next request → cache miss again → DB again → null again
→ forever

1,000 requests/sec for non-existent keys
→ 1,000 DB queries/sec, all returning null
→ DB dies
```

The cache protects nothing because there's nothing to cache.

**Fix 1 — Cache the Null**

```
DB returns null for user:99999999
→ cache.set("user:99999999", NULL, TTL=60s)

Next 1,000 requests → cache hit → return null → DB sees zero queries
```

Short TTL on null entries. If the user gets created later, the null expires and real data gets cached on the next request.

**Fix 2 — Bloom Filter**

A bloom filter is a data structure that answers: *"has this key ever existed in the DB?"*

```
Request arrives for user:99999999
→ check bloom filter: "has this user ever been inserted?"
→ NO → return 404 immediately. Cache and DB never touched.
→ YES (or maybe) → proceed normally
```

Bloom filters have no false negatives. If it says no, it's definitely no. They can have false positives (says yes when it's actually no) but the rate is very low and controllable.

> [!tip] Bloom filters are used in production everywhere — Cassandra, HBase, Postgres all use them to avoid disk lookups for non-existent keys. For cache penetration: put the bloom filter in front of the cache layer. Non-existent keys never reach cache or DB.

---

## Cache Avalanche

> [!info] Thousands of keys expire at the same time. Mass cache miss. DB gets hammered across the entire keyspace simultaneously.

```
Midnight sale launch:
→ bulk-loaded 50,000 product pages into cache at 11:55pm
→ all given TTL = 5 minutes
→ 12:00am → all 50,000 keys expire simultaneously
→ every product page request → cache miss
→ 50,000 DB queries at once
→ DB collapses
```

Stampede is one key. Avalanche is the entire cache. Happens whenever you bulk-load with identical TTLs — all keys born together, all die together.

**Fix — TTL Jitter**

Add randomness to the TTL so expirations are spread out:

```
Instead of:  TTL = 300s  (all 50,000 keys expire at the same second)

Use:         TTL = 300s + random(0, 60s)

Key A → 312s
Key B → 347s
Key C → 301s
Key D → 358s
...

Expirations spread across a 60-second window
→ DB sees ~833 misses/sec instead of 50,000 all at once
→ no avalanche
```

One line change. Completely solves it. Always add jitter when bulk-loading the cache.

---

## Summary

```
Stampede    → one hot key expires, thousands hit DB simultaneously
              fix: refresh-ahead (proactive), mutex + double-checked locking, probabilistic expiry

Cold Start  → cache empty, 100% of traffic hits DB
              fix: warm cache before opening traffic (replay access logs)

Penetration → non-existent keys bypass cache forever, DB returns null forever
              fix: cache null values (short TTL), bloom filter at entry point

Avalanche   → thousands of keys expire at the same time, mass DB spike
              fix: TTL jitter — add randomness to expiry times on bulk loads
```

> [!important] These four problems have the same root symptom — DB getting hammered — but completely different causes. Diagnosing which one you have tells you which fix to reach for.
