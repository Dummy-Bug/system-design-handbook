
> [!info] Move cold URLs to S3 — keep a pointer in the DB, serve the redirect transparently
> The user clicking a cold URL should still get redirected correctly. The extra S3 hop is a one-time cost — Redis re-warming means subsequent clicks are fast again.

---

## The schema change

The current schema stores `long_url` directly in the DB row. For cold storage, you need two new columns:

```sql
CREATE TABLE urls (
    short_code       CHAR(6)       PRIMARY KEY,
    long_url         TEXT,                        -- populated for hot URLs, null for cold
    s3_key           TEXT,                        -- populated for cold URLs, null for hot
    is_cold          BOOLEAN       DEFAULT false,
    created_at       TIMESTAMPTZ   DEFAULT NOW(),
    expires_at       TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ
);
```

When a URL goes cold, a background job:
1. Writes `long_url` to S3 at key `cold-urls/{short_code}`
2. Sets `s3_key = 'cold-urls/x7k2p9'` in the DB row
3. Sets `is_cold = true`
4. Clears `long_url` to NULL (reclaims DB storage)

The DB row now weighs almost nothing — just the short_code, s3_key, and metadata columns. The bulk of the data (the long URL string) has moved off to S3.

---

## The updated redirect flow

For hot URLs, the flow is unchanged:

```
GET /x7k2p9
→ Redis cache HIT → 301 immediately
→ Redis MISS → DB lookup → long_url found → 301, populate cache
```

For cold URLs:

```
GET /x7k2p9
→ Redis cache MISS  (cold URLs are not cached — TTL expired long ago)
→ DB lookup → is_cold = true, s3_key = 'cold-urls/x7k2p9'
→ S3 GET cold-urls/x7k2p9 → returns long_url
→ 301 redirect to long_url
→ async: populate Redis cache with long_url (TTL = 24 hours)
```

The user gets redirected correctly. They never know it was cold. The only difference is latency on that first hit.

---

## The latency trade-off

A normal redirect today:

```
Redis cache miss → DB lookup → 301
~20ms total
```

A cold URL redirect:

```
Redis cache miss → DB lookup → S3 fetch → 301
~20ms + 50-200ms S3 latency = ~220ms total
```

That is 10x slower for the first hit. For a URL that hasn't been clicked in 6 months, this is an acceptable trade-off — the user waited 6 months to click it, they can wait 220ms.

**After the first cold hit, Redis is re-warmed.** Subsequent clicks go through the normal Redis path at ~5ms. No DB lookup, no S3 fetch. The URL is hot again until the cache TTL expires.

Importantly, you do NOT write `long_url` back to the DB when a cold URL is accessed. Redis handles the re-warming automatically — TTL set on the cache entry. When the TTL expires, if nobody clicks it again, it stays cold. If someone clicks it, it warms back into Redis on demand. No DB write needed.

---

## Monitoring cold URL latency separately

Cold URL redirects have fundamentally different latency characteristics than hot redirects. If you mix them into your overall p99, a spike in S3 latency can inflate your fleet p99 without reflecting a real problem with the hot path.

The right approach: track a separate SLI for cold URL p99 latency. Set a separate SLO — say, p99 < 500ms for cold URLs (more generous than the 50ms hot SLO, because the S3 hop is expected).

```
Hot redirect SLO:   p99 < 50ms
Cold redirect SLO:  p99 < 500ms
```

Alert separately on each. A cold URL latency spike does not page on-call at 3am with the same urgency as a hot redirect latency spike.

---

> [!tip] Interview framing
> "Cold URLs get moved to S3. DB row keeps s3_key and is_cold flag, long_url is cleared. Redirect flow: cache miss → DB lookup → is_cold true → S3 fetch → 301 → async populate Redis. First cold hit takes ~220ms (S3 adds 50-200ms). After that, Redis re-warmed — subsequent hits are fast until TTL expires. No write-back to DB needed. Track cold URL latency as a separate SLI with a more generous SLO — p99 < 500ms — so S3 latency spikes don't corrupt your hot path alerting."
