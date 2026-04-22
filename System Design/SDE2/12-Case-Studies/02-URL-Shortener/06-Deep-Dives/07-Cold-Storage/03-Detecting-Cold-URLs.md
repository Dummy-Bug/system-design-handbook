
> [!info] Knowing which URLs are cold requires tracking when each one was last accessed — without writing to the DB on every redirect
> 1M redirects/second × 1 DB write each = the DB dies instantly. The solution is batching, with sampling as an alternative.

---

## The last_accessed_at column

To know if a URL is cold, you need to know when it was last clicked. That requires a `last_accessed_at` timestamp on each URL row:

```sql
last_accessed_at  TIMESTAMPTZ
```

The nightly background job then uses this to identify cold URLs:

```sql
SELECT short_code, long_url
FROM urls
WHERE last_accessed_at < NOW() - INTERVAL '6 months'
  AND is_cold = false
```

Any URL not clicked in 6 months is a candidate for cold storage. Simple query, runs during off-peak hours, moves matching rows to S3.

The 6-month threshold is a product decision. You could use 3 months for more aggressive tiering, 1 year for more conservative. The right value depends on your storage costs vs acceptable first-hit latency penalty.

---

## The naive approach kills the DB

The obvious way to update `last_accessed_at`: fire an UPDATE on every redirect.

```sql
UPDATE urls SET last_accessed_at = NOW() WHERE short_code = 'x7k2p9'
```

At 1M redirects/second, this is 1M UPDATE statements per second hitting your DB.

Your DB currently handles:
```
Reads:   ~200k/sec across 16 read nodes (after caching)
Writes:  ~125/sec per shard primary (URL creation only)
```

1M additional writes per second would immediately overwhelm every shard primary. The system falls over. This approach is not viable.

---

## Fix 1 — Batching

Instead of writing to the DB on every request, each app server keeps a small in-memory set of recently accessed short codes. Every 60 seconds, it flushes the entire set to the DB in a single batch UPDATE.

```
Request arrives: bit.ly/x7k2p9
→ add "x7k2p9" to local in-memory set
→ return 301 (no DB write)

Request arrives: bit.ly/x7k2p9 again
→ "x7k2p9" already in set, skip
→ return 301

Request arrives: bit.ly/abc123
→ add "abc123" to local in-memory set
→ return 301

... 60 seconds later ...

App server flushes:
UPDATE urls SET last_accessed_at = NOW()
WHERE short_code IN ('x7k2p9', 'abc123', ...)
```

How much does this reduce DB load?

```
1M requests/sec × 60 seconds = 60M requests per flush window
Unique short codes in 60M requests (80/20 rule): ~few thousand
20 app servers each flush once every 60 seconds = ~20 batch UPDATEs/min

1,000,000 writes/sec → ~20 batch updates/minute
```

The DB barely notices. And for cold storage purposes, precision doesn't matter — you don't care if `last_accessed_at` is accurate to the millisecond. You care if a URL was accessed in the last 6 months. A 60-second batching delay is completely irrelevant to that question.

The one risk: if an app server crashes before it flushes, that 60-second window of access data is lost. URLs accessed only in that window might appear stale. For cold storage purposes this is acceptable — losing 60 seconds of access data out of 6 months is noise.

---

## Fix 2 — Sampling

An alternative: only record 1 in every 100 accesses. Every redirect, generate a random number 1–100. If it equals 1, update `last_accessed_at`. Otherwise skip.

```
Request arrives: bit.ly/x7k2p9
→ random number = 47 → skip, no update

Request arrives: bit.ly/x7k2p9
→ random number = 1  → UPDATE last_accessed_at = NOW()

Request arrives: bit.ly/x7k2p9
→ random number = 83 → skip, no update
```

```
1M requests/sec × 1% sample rate = 10,000 writes/sec
Spread across 8 shard primaries  = 1,250 writes/sec per primary  ← manageable
```

**Trade-off vs batching:**

```
Batching:  accurate last_accessed_at (60s delay only), no missed accesses
Sampling:  lower DB load, but risk of mislabelling active URLs as cold

Risk example: a URL gets exactly 5 hits/day at 1% sample rate
→ expected samples per day: 0.05 → likely never recorded
→ last_accessed_at goes stale → URL incorrectly moved to cold storage
→ user clicks it → 220ms cold hit instead of instant redirect
```

For cold storage, **batching is the safer choice**. Sampling risks mislabelling low-traffic-but-still-active URLs as cold. A URL getting 10 hits per day is not cold — but at 1% sample rate, it has a real chance of never being sampled on a given day.

You can combine both approaches — sample at 10% AND batch the samples every 60 seconds. Even lower DB load than pure batching, with lower mislabelling risk than pure sampling.

---

## The full cold storage pipeline

```
Every redirect:
→ Add short_code to app server in-memory set (batching)

Every 60 seconds:
→ App server flushes set → batch UPDATE last_accessed_at

Every night (off-peak):
→ Background job queries: last_accessed_at < 6 months ago, is_cold = false
→ For each match:
   - Write long_url to S3 at key cold-urls/{short_code}
   - UPDATE urls SET s3_key = '...', is_cold = true, long_url = NULL
→ Storage reclaimed from DB, data lives in S3
```

---

> [!tip] Interview framing
> "To detect cold URLs we track last_accessed_at. Naive approach — UPDATE on every redirect — is 1M writes/sec, kills the DB. Fix: batching. Each app server keeps an in-memory set of accessed short codes, flushes a single batch UPDATE every 60 seconds. 1M writes/sec becomes ~20 batch updates/minute. Sampling (1-in-100) is an alternative but risks mislabelling low-traffic URLs as cold — batching is safer for this use case. Nightly job queries last_accessed_at < 6 months, moves matching URLs to S3, clears long_url from DB row."
