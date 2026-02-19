
We want:

- Fast reads like in-memory HashMap.
- Distributed system.
- Persistence.
- Easy sharding.

In-memory HashMap fails because:

- Single machine memory bound.
- No replication.
- No durability.
- No horizontal scaling.

Redis solves this:

- Sub-millisecond reads.
- Distributed cluster.
- Built-in persistence.
- Sharding and replication.

So Redis becomes our **shared in-memory index layer**.

---

## Step 2. How Redis Fits the Prefix → Top K Model

We store:

### Prefix → Sorted Set

Redis data structure:

`ZSET (Sorted Set)`

Example:

Key:

`prefix:par`

Value:

`("paris hotels", 5421) ("paris weather", 4980) ("park near me", 3900)`

Sorted automatically by score (frequency).

---

### Query → Count Map

Another Redis structure:

`HASH`

Example:

`query:paris city cost of living → 12045`

---

## Step 3. Read Path (Typeahead)

When user types:

`par`

Flow:

`Service → Redis → ZRANGE prefix:par 0 9 REV`

Redis returns top 10 directly.

No Trie traversal.

No DFS.

No sorting.

Latency:

< 1ms.

This is extremely fast.

---

## Step 4. Write Path Problem

Search submissions are huge:

`~10^5 writes/sec`

If we update:

- Query count.
- All prefix ZSETs.

For every search.

Redis becomes bottleneck.

So we must reduce write volume.

---

## Step 5. Key Insight

Autocomplete ranking does NOT require exact counters.

It requires:

> Relative popularity ordering.

Approximation is acceptable.

So we trade accuracy for throughput.

---

## Step 6. Batching Strategy

Instead of:

Update Redis every time count increases by 1.

We do:

- Maintain local in-memory counter.
- Only push update when count increases by 100.

Example:

`Search count grows: 1 → ignore 2 → ignore ... 99 → ignore 100 → update Redis`

Effect:

- Redis sees 1 write instead of 100.
- Ranking still roughly correct.
- Lag introduced but bounded.

This alone gives:

100x write reduction.

---

## Step 7. Sampling Strategy 

Instead of updating Redis every time:

We randomly update.

Example:

- Only update 1 out of every 100 searches.
- Ignore remaining 99.

So:

Actual count:

`1000`

Redis sees:

`10`

Relative ranking still preserved.

Trend detection still works.

Absolute numbers become approximate.

Autocomplete does not need exact counts.

---

## Step 8. Why This Is Safe

Autocomplete is ranking based.

If:

Query A = 10,000 searches 
Query B = 5,000 searches

With sampling:

A becomes 100 
B becomes 50

Order remains correct.

That is what matters.

---

## Step 9. Combined Strategy (Production Style)

We usually combine both:

### Pipeline:

```
Search Event    
↓ Local Aggregator    
↓ Sampling Filter    
↓ Batch Threshold    
↓ Redis Update
```

Result:

- Huge write reduction.
- Stable Redis load.
- Fresh-enough ranking.

---

## Step 10. Final Redis Architecture

### Read Path

`Client → API → Redis ZSET → Response`

Fast. Simple.

---

### Write Path

`Search Submit → Queue → Aggregator → Batch + Sample → Redis Update`

Controlled load.

---

## Brutal Truth

If you update Redis on every search:

- You will hit throughput ceiling.
- Costs explode.
- Latency spikes.
- Cluster thrashes.

Approximation is mandatory at this scale.

---

## Final Mental Model

Redis is not your source of truth.

Redis is your:

> High-speed approximate ranking cache.

Exact counts live in offline analytics.

Typeahead uses fast, dirty, good-enough data.

---

## One-Line Summary

"We use Redis Sorted Sets for prefix ranking and reduce write load using batching and sampling to maintain high availability while preserving relative popularity trends."