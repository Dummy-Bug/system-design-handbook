# Type-Ahead System — Redis as the Serving Layer

> [!question] Why Redis?
> We need the two-HashMap model from [[06 Tries]] to work at 1M QPS across multiple machines.
> A plain in-memory HashMap on one server can't do that.
> Redis is essentially a **distributed, persistent, in-memory HashMap** — exactly what we need.

---

## Why Not a Plain In-Memory HashMap?

| Requirement | Plain HashMap | Redis |
|---|---|---|
| Sub-millisecond reads | ✅ | ✅ |
| Survives server restart | ❌ Lost on crash | ✅ Built-in persistence |
| Multiple machines | ❌ Single machine only | ✅ Native clustering |
| Replication | ❌ None | ✅ Primary + replicas |
| Sharding | ❌ Manual, painful | ✅ Redis Cluster handles it |

> [!info] What is Redis?
> Redis is an open-source, ==in-memory data store== that supports rich data structures — strings, lists, sets, sorted sets, hashmaps. Everything lives in RAM so reads are sub-millisecond. It's the most widely used cache in the world. Used by Twitter, GitHub, Snapchat, and Google-scale systems.

---

## How Redis Maps to Our Two-HashMap Model

From [[06 Tries]], we need:
1. `prefix → top K results` (read path)
2. `query → frequency count` (write path)

Redis has native data structures for both.

### Structure 1 — Sorted Set (ZSET) for Prefix → Top K

A ==Redis Sorted Set== stores members with a **score**. Members are automatically ordered by score. Perfect for ranking.

```
Key:   prefix:par
Type:  ZSET (Sorted Set)

Members + scores:
  "paris weather"           →  score: 5,421,000
  "paris hotels"            →  score: 4,980,000
  "park near me"            →  score: 3,900,000
  "paris city cost of living" → score: 2,100,000
  ...
```

To read top 10 for prefix `"par"`:

```redis
ZRANGE prefix:par 0 9 REV WITHSCORES
```

> [!info] What does this command mean?
> - `ZRANGE` — get a range of members from a sorted set
> - `prefix:par` — the key
> - `0 9` — positions 0 through 9 (first 10)
> - `REV` — reversed order (highest score first)
> - `WITHSCORES` — also return the scores
>
> Redis executes this in `O(log N + K)` time — nearly instant even with millions of members.

### Structure 2 — Hash for Query → Frequency

```
Key:   query_counts
Type:  HASH

Fields:
  "paris"                      →  50,000,000
  "pizza near me"              →  40,000,000
  "paris city cost of living"  →  12,045
```

To increment a count:
```redis
HINCRBY query_counts "paris city cost of living" 1
```

---

## Read Path — How a Typeahead Request Works

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Redis

    User->>API: GET /typeahead?partialSearchQuery=par
    API->>Redis: ZRANGE prefix:par 0 9 REV
    Redis-->>API: ["paris weather", "paris hotels", "park near me", ...]
    API-->>User: 200 OK — top 10 suggestions
```

**Latency:** < 1ms for the Redis call. Total response under 5ms including network.
No Trie traversal. No DFS. No sorting. Redis does it all.

---

## Write Path Problem — 100k Writes/sec is Too Much

From [[05 Estimations]] and [[06 Tries]], every search submission triggers ~10 prefix updates:

```
1 search "paris city cost of living"
→ update prefix:p, prefix:pa, prefix:par ... (10 prefixes)
→ update query_counts hash

1B searches/day × 10 updates = 10B writes/day = ~100,000 write QPS
```

> [!danger] Updating Redis directly on every search submission
> - Redis write throughput: ~100k ops/sec per node
> - We're already at that limit just from writes — reads get zero budget
> - Redis cluster starts thrashing, read latency spikes
> - ==This kills the system==

We need to ==drastically reduce write volume== without breaking ranking quality.

---

## Key Insight — Autocomplete Doesn't Need Exact Counts

> [!success] The saving grace
> Autocomplete only needs **relative ordering** — which query is more popular than another.
> It does NOT need exact counts.

```
Exact counts:                 Approximate counts:
  "paris"      = 50,000,000    "paris"      = 500,000
  "pizza"      = 40,000,000    "pizza"      = 400,000
  "python"     = 30,000,000    "python"     = 300,000

Rankings are identical ✅ — the user sees the same suggestions either way.
```

This means we can ==trade accuracy for throughput== — as long as relative order is preserved, the user experience is identical.

---

## Strategy 1 — Batching

Instead of pushing every single count increment to Redis, accumulate locally and push only when the count crosses a threshold.

```mermaid
flowchart LR
    Search["Search submitted"] --> Local["Local counter\n+1"]
    Local --> Check{count % 100\n== 0?}
    Check -- No --> Ignore["Discard\n(99 out of 100)"]
    Check -- Yes --> Push["Push update\nto Redis"]
```

```
Without batching:   "paris" searched 100 times → 100 Redis writes
With batching:      "paris" searched 100 times → 1 Redis write

Reduction: 100x fewer writes ✅
```

> [!info] How stale does this make the ranking?
> If a query gets searched 1,000 times a day and we batch every 100:
> Redis gets 10 updates per day for that query — about every 2.4 hours.
> For popular stable queries ("paris", "pizza") this is completely fine.
> For breaking news ("earthquake 2026"), this introduces ~hours of lag.
> The freshness trade-off is acceptable for most queries.

---

## Strategy 2 — Sampling

Instead of batching by threshold, randomly decide whether to record each search at all.

```mermaid
flowchart LR
    Search["Search submitted"] --> Roll{"Random 1%\nchance?"}
    Roll -- No 99% --> Drop["Drop this event\n(don't update Redis)"]
    Roll -- Yes 1% --> Update["Update Redis"]
```

```
Without sampling:   "paris" searched 1,000 times → Redis count = 1,000
With 1% sampling:   "paris" searched 1,000 times → Redis count = ~10

Reduction: ~100x fewer writes ✅
Relative order: still preserved ✅
```

> [!info] Why does sampling preserve relative order?
> If "paris" is 2× more popular than "pizza", then 1% sampling still records "paris" ~2× more than "pizza".
> Proportions are preserved even when absolute numbers shrink.

---

## Strategy 3 — Combined Pipeline (Production Style)

In production, both strategies are combined:

```mermaid
flowchart TD
    Event["Search submitted\n'paris city cost of living'"]
    --> Sample{"Sampling filter\n1% pass rate"}
    Sample -- 99% dropped --> Bin["🗑️ Discarded"]
    Sample -- 1% pass --> Agg["Local Aggregator\nbatch counter"]
    Agg --> Thresh{"Threshold\nreached?"}
    Thresh -- No --> Wait["Wait for more"]
    Thresh -- Yes --> Redis["Update Redis\nZSET + Hash"]
```

**Effect:**
```
Raw search events:        100,000 / sec
After 1% sampling:          1,000 / sec
After 100x batching:           10 / sec  ← actual Redis writes
```

> [!success] From 100,000 writes/sec down to ~10 writes/sec
> A 10,000x reduction in Redis write load — with no visible impact on suggestion quality for the user.

---

## Why This Is Safe — The Math

```
Query A is searched 10,000 times/day
Query B is searched  5,000 times/day

After 1% sampling + 100x batching:
  Redis sees A = 1 update/day
  Redis sees B = 0 or 1 update/day

After enough time: A consistently ranks above B ✅
```

> [!warning] One edge case — brand new trending queries
> A query that explodes from 0 to 1M searches in 1 hour (breaking news) may take hours to surface in suggestions because of batching lag.
> This is the freshness trade-off. Acceptable for most use cases. Can be partially mitigated with a separate "trending" pipeline that bypasses batching.

---

## Final Mental Model

> [!abstract] Redis is not the source of truth — it's the serving cache
>
> ```
> Source of truth:   Offline analytics pipeline (exact counts, updated daily)
> Redis:             High-speed approximate ranking cache (updated in near-real-time)
> ```
>
> Exact counts live in the data warehouse.
> Typeahead uses fast, approximate, good-enough data from Redis.
> The user never knows the difference.

---

## Read vs Write Path Summary

```mermaid
flowchart LR
    subgraph READ["Read Path — latency critical"]
        U["User types 'par'"] --> API["API Server"]
        API --> RD["Redis ZSET\nZRANGE prefix:par 0 9 REV"]
        RD --> Resp["Top 10 suggestions\n< 1ms"]
    end

    subgraph WRITE["Write Path — throughput controlled"]
        S["User submits search"] --> Q["Queue / Aggregator"]
        Q --> Filter["Sample + Batch"]
        Filter --> RW["Redis ZSET update\n~10 writes/sec"]
    end
```

| | Read Path | Write Path |
|---|---|---|
| **Trigger** | Every keystroke (after debounce) | Every search submission |
| **Redis operation** | `ZRANGE` — top K by score | `ZADD` / `HINCRBY` — update score |
| **Latency** | < 1ms | Not critical — async |
| **Volume** | 1M QPS peak | ~10 writes/sec after batching + sampling |
