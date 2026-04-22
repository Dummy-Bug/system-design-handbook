
> [!info] Sharding is the right solution to the right problem. Before committing to it, verify whether the problem actually exists.

---

## Why sharding was on the table

In the estimation phase, we calculated storage requirements assuming all paste data — content and metadata — lives in Postgres:

```
Total pastes (10 years):  3.65B
Per paste:                ~10KB (content) + ~100 bytes (metadata) ≈ 10KB
Raw storage:              3.65B × 10KB = 36.5TB
With replication (3×):    ~110TB
With index overhead:      ~150TB
```

A single Postgres machine handles ~10TB practically. At 150TB, sharding was listed as a hard requirement in the NFR.

The NFR file stated: **sharding required — 150TB exceeds single-machine limit.**

---

## Rejecting sharding on traffic grounds first

Before even touching storage, check whether read or write QPS demands sharding.

```
Peak write QPS:  30 writes/sec
Peak read QPS:   3,000 reads/sec

Single Postgres primary:   10,000–50,000 reads/sec capacity
Single Postgres primary:   1,000–5,000 writes/sec capacity
```

QPS thresholds from back-of-envelope reference:

```
Read QPS > 10k   → caching required
Read QPS > 100k  → DB sharding required

Write QPS > 1k   → write batching or async queue
Write QPS > 10k  → shard primaries
```

Our peak read QPS is 3,000 — well under the 10k threshold where even caching becomes necessary (and we're adding caching anyway for latency, not throughput). Our peak write QPS is 30 — orders of magnitude below the 1k threshold.

**Traffic alone does not require sharding.** A single Postgres primary handles our load with significant headroom.

---

## Rejecting sharding on storage grounds — the S3 correction

The original 150TB estimate was wrong because it assumed paste content lives in Postgres. But in our DB design, we offload all content to S3 and store only a pointer in Postgres.

What actually lives in Postgres per paste:

```
short_code:    ~8 bytes
user_id:       8 bytes  (bigint)
content_hash:  32 bytes (SHA-256)
s3_url:        ~100 bytes
created_at:    8 bytes
expires_at:    8 bytes
deleted_at:    8 bytes (nullable)
ref_count:     4 bytes

Total per row: ~180 bytes → round to ~200 bytes
```

Recalculating Postgres storage:

```
Total pastes (10 years):   3.65B rows
Per row (metadata only):   ~200 bytes
Raw storage:               3.65B × 200 bytes = 730GB ≈ 0.73TB
With replication (3×):     0.73 × 3 = ~2.2TB
With index overhead (1.3×): ~2.9TB

→ ~3TB in Postgres
```

A single Postgres machine handles 10TB comfortably. **3TB is well within single-machine territory.**

S3 stores the content:

```
3.65B pastes × 10KB = 36.5TB of content in S3
```

S3 is object storage designed for petabytes. 36.5TB is routine. No sharding, no special configuration — S3 handles this natively.

---

## The verdict

```
                   Original estimate   Corrected estimate
Postgres storage:  150TB               ~3TB
Sharding needed?   Yes                 No

Why the difference:
  Original assumed content (10KB) in Postgres
  Corrected moves content to S3, Postgres stores only metadata (~200 bytes)
  Storage drops by 50×
```

> [!important] The decision to offload content to S3 didn't just reduce latency and improve DB performance — it eliminated the sharding requirement entirely. Architecture decisions compound: one good call (S3 for blobs) removed a significant operational burden (shard key selection, consistent hashing, cross-shard queries).

Sharding remains the right answer if Postgres storage approaches 10TB. At ~3TB with 10 years of data, we have headroom and no need to introduce the operational complexity of a sharded setup.

---

> [!tip] Interview framing
> "We initially flagged sharding as required — 150TB exceeds the single-machine limit. But that assumed content lives in Postgres. Once we moved content to S3, Postgres only stores metadata at ~200 bytes per row. 3.65B rows × 200 bytes = ~3TB with replication — well under the 10TB single-machine limit. Traffic doesn't require sharding either: 3k peak reads/sec and 30 peak writes/sec are handled by a single primary with headroom. Sharding is off the table."
