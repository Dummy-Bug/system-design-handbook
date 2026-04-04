# Cache Problems

## Cache Stampede

> [!info] A hot key's TTL expires. Thousands of requests arrive at the same moment — all get a cache miss simultaneously. All of them go to the DB at once.

```mermaid
flowchart LR
    subgraph Normal["Normal Flow"]
        A1["Request"] --> A2["Cache hit ✓"] --> A3["Done"]
        style A2 fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph Stampede["Stampede"]
        B1["Key expires at T=300s"] --> B2["10,000 requests arrive"]
        B2 --> B3["All get cache miss"]
        B3 --> B4["All fetch from DB simultaneously"]
        B4 --> B5["DB gets 10,000 queries instead of 1"]
        B5 --> B6["DB collapses ✗"]
        style B3 fill:#f8d7da,stroke:#dc3545,color:#000
        style B5 fill:#f8d7da,stroke:#dc3545,color:#000
        style B6 fill:#f8d7da,stroke:#dc3545,color:#000
    end
```

The problem isn't the cache miss itself. It's the **thundering herd** — thousands of identical DB queries happening in parallel because nobody coordinated.

---

**Fix 1 — Refresh-Ahead**

Don't wait for the key to expire. Refresh it proactively before it dies.

```mermaid
flowchart LR
    A["Key TTL = 60s"] --> B["T=45s — background job detects<br/>key is about to expire"]
    B --> C["Fetch fresh data from DB"]
    C --> D["Update cache"]
    D --> E["T=60s — key would have expired<br/>but it's already fresh ✓"]
    E --> F["Users never see a miss<br/>DB never sees the spike ✓"]
    style E fill:#d4edda,stroke:#28a745,color:#000
    style F fill:#d4edda,stroke:#28a745,color:#000
```

How do you know which keys to refresh ahead? You track which keys are being hit frequently. If a key is getting thousands of hits per second, it's worth refreshing before it expires. Low-traffic keys — let them expire naturally.

> [!tip] Refresh-ahead is proactive. You need to know in advance which keys are hot. Works great for predictable traffic — trending posts, homepage content, leaderboard top 10. Doesn't help for unpredictable spikes.

---

**Fix 2 — Mutex with Double-Checked Locking**

When a key expires, only let one request fetch from DB. The rest wait.

```mermaid
flowchart TD
    A["Key expires → 10,000 requests get cache miss"] --> B["All try to acquire lock"]
    B --> C["One request wins the lock"]
    B --> D["9,999 requests wait"]
    C --> E["Fetch from DB → write to cache → release lock"]
    D --> F["Wake up → check cache again → HIT ✓"]
    E --> F
    style C fill:#fff3cd,stroke:#ffc107,color:#000
    style F fill:#d4edda,stroke:#28a745,color:#000
```

The critical detail: waiters must **check the cache again** after acquiring the lock. This is double-checked locking.

```mermaid
flowchart LR
    subgraph Without["Without Double-Check"]
        W1["Waiter acquires lock"] --> W2["Fetches from DB"]
        W2 --> W3["Next waiter acquires lock"] --> W4["Fetches from DB again"]
        W4 --> W5["...and again, 9,999 times"]
        W5 --> W6["DB still hammered ✗"]
        style W6 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph With["With Double-Check"]
        X1["Waiter acquires lock"] --> X2["Checks cache → HIT ✓"]
        X2 --> X3["Returns immediately"]
        X3 --> X4["DB gets exactly 1 query total ✓"]
        style X2 fill:#d4edda,stroke:#28a745,color:#000
        style X4 fill:#d4edda,stroke:#28a745,color:#000
    end
```

```python
function get(key):
  value = cache.get(key)
  if value: return value          # first check (no lock)

  lock.acquire(key)
    value = cache.get(key)        # second check (inside lock)
    if value:
      lock.release()
      return value                # someone else already fetched it

    value = db.fetch(key)
    cache.set(key, value)
    lock.release()
    return value
```

> [!important] The second cache check inside the lock is what makes this work. Without it, you've serialised the DB queries instead of eliminating them. With it, DB gets exactly one query no matter how many concurrent waiters.

---

**Fix 3 — Probabilistic Early Expiry**

Instead of refreshing at a fixed threshold, each request near the end of TTL flips a coin. If it wins, it refreshes early.

```mermaid
flowchart TD
    A["TTL = 60s<br/>Key has 10s remaining"] --> B["Each request near expiry flips a coin"]
    B -->|"heads — 20% chance"| C["This request refreshes cache proactively"]
    B -->|"tails"| D["Serve stale, do nothing"]
    C --> E["Cache refreshed before expiry"]
    E --> F["No thundering herd ✓<br/>no coordination needed, no locks"]
    style F fill:#d4edda,stroke:#28a745,color:#000
```

As TTL approaches zero, more requests win the coin flip — cache gets refreshed before it ever expires. The randomness spreads the refresh load naturally.

---

## Cold Start

> [!info] Cache is completely empty. Fresh deployment, Redis restart, new region. Every request is a cache miss. DB sees 100% of traffic.

```mermaid
flowchart LR
    A["New cache deployed<br/>0 keys"] --> B["Every request → cache miss"]
    B --> C["Hits DB"]
    C --> D["DB sees full production traffic<br/>instead of the usual 5%"]
    D --> E["DB collapses ✗"]
    style D fill:#f8d7da,stroke:#dc3545,color:#000
    style E fill:#f8d7da,stroke:#dc3545,color:#000
```

Same symptom as stampede — DB getting hammered. Different cause. Stampede is one key dying. Cold start is nothing ever existed to begin with.

**Fix — Cache Warming**

Before opening traffic to the new cache, pre-populate it.

```mermaid
flowchart LR
    A["Before launch"] --> B["Script reads top-N popular keys from DB"]
    B --> C["Writes them all into cache"]
    C --> D["Open traffic"]
    D --> E["Users hit cache → already warm ✓"]
    E --> F["DB never sees the spike ✓"]
    style E fill:#d4edda,stroke:#28a745,color:#000
    style F fill:#d4edda,stroke:#28a745,color:#000
```

How do you know which keys to warm? Replay yesterday's access logs. If those keys were hot yesterday, they'll be hot today. Start with homepage content, top products, trending posts.

---

## Cache Penetration

> [!info] Requests for keys that don't exist in the DB. Every request is a cache miss. Every request hits DB. DB returns null. Nothing gets cached. Cycle repeats forever.

Normal cache miss resolves itself — fetch from DB, store in cache, next request is a hit. Penetration never resolves:

```mermaid
flowchart LR
    A["GET /user/99999999<br/>user doesn't exist"] --> B["Cache miss"]
    B --> C["Fetch from DB → null"]
    C --> D["Nothing to cache"]
    D --> E["Next request → cache miss again"]
    E --> C
    style B fill:#f8d7da,stroke:#dc3545,color:#000
    style D fill:#f8d7da,stroke:#dc3545,color:#000
```

1,000 requests/sec for non-existent keys → 1,000 DB queries/sec, all returning null → DB dies.

**Fix 1 — Cache the Null**

```mermaid
flowchart LR
    A["DB returns null for user:99999999"] --> B["cache.set('user:99999999', NULL, TTL=60s)"]
    B --> C["Next 1,000 requests → cache hit → return null ✓"]
    C --> D["DB sees zero queries ✓"]
    style C fill:#d4edda,stroke:#28a745,color:#000
    style D fill:#d4edda,stroke:#28a745,color:#000
```

Short TTL on null entries. If the user gets created later, the null expires and real data gets cached on the next request.

**Fix 2 — Bloom Filter**

A bloom filter answers: *"has this key ever existed in the DB?"*

```mermaid
flowchart TD
    A["Request arrives for user:99999999"] --> B["Check bloom filter<br/>'has this user ever been inserted?'"]
    B -->|"NO — definitely not"| C["Return 404 immediately ✓<br/>cache and DB never touched"]
    B -->|"YES or maybe"| D["Proceed normally to cache → DB"]
    style C fill:#d4edda,stroke:#28a745,color:#000
```

Bloom filters have no false negatives. If it says no, it's definitely no. They can have false positives (says yes when actually no) but the rate is very low and controllable.

> [!tip] Bloom filters are used in production everywhere — Cassandra, HBase, Postgres all use them to avoid disk lookups for non-existent keys. Put the bloom filter in front of the cache layer — non-existent keys never reach cache or DB.

---

## Cache Avalanche

> [!info] Thousands of keys expire at the same time. Mass cache miss. DB gets hammered across the entire keyspace simultaneously.

```mermaid
flowchart LR
    A["Bulk-load 50,000 product pages<br/>at 11:55pm, all TTL = 5min"] --> B["12:00am — all 50,000 keys<br/>expire simultaneously"]
    B --> C["Every product page → cache miss"]
    C --> D["50,000 DB queries at once"]
    D --> E["DB collapses ✗"]
    style B fill:#f8d7da,stroke:#dc3545,color:#000
    style D fill:#f8d7da,stroke:#dc3545,color:#000
    style E fill:#f8d7da,stroke:#dc3545,color:#000
```

Stampede is one key. Avalanche is the entire cache. Happens whenever you bulk-load with identical TTLs — all keys born together, all die together.

**Fix — TTL Jitter**

Add randomness to the TTL so expirations are spread out:

```mermaid
flowchart LR
    subgraph Bad["Without Jitter"]
        W1["All 50,000 keys<br/>TTL = 300s"] --> W2["All expire at the same second"]
        W2 --> W3["50,000 DB queries at once ✗"]
        style W2 fill:#f8d7da,stroke:#dc3545,color:#000
        style W3 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph Good["With Jitter"]
        G1["TTL = 300s + random(0, 60s)"] --> G2["Key A → 312s<br/>Key B → 347s<br/>Key C → 301s ..."]
        G2 --> G3["Expirations spread across 60s window"]
        G3 --> G4["~833 misses/sec instead of 50,000 ✓"]
        style G3 fill:#d4edda,stroke:#28a745,color:#000
        style G4 fill:#d4edda,stroke:#28a745,color:#000
    end
```

One line change. Completely solves it. Always add jitter when bulk-loading the cache.

---

## Summary

| Problem | Cause | Fix |
|---|---|---|
| Stampede | One hot key expires, thousands hit DB simultaneously | Refresh-ahead, mutex + double-checked locking, probabilistic expiry |
| Cold Start | Cache empty — fresh deploy, restart, new region | Warm cache before opening traffic (replay access logs) |
| Penetration | Non-existent keys bypass cache forever, DB returns null forever | Cache null values (short TTL), bloom filter at entry point |
| Avalanche | Thousands of keys expire at the same time — bulk-loaded with identical TTL | TTL jitter — add randomness to expiry on bulk loads |

> [!important] These four problems have the same root symptom — DB getting hammered — but completely different causes. Diagnosing which one you have tells you which fix to reach for.
