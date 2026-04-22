
> [!info] Caching sits in front of your slow storage layers and serves repeated reads from memory — sub-millisecond instead of tens or hundreds of milliseconds.

---

## The problem without caching

Your base architecture for a paste read looks like this:

```
Client → App Server → Postgres (metadata) → S3 (content) → Client
```

Two network hops on every single read. At 1k reads/sec average and 3k peak, both hops happen thousands of times per second.

The Postgres hop is fast — a primary key lookup on a warm index is typically 1–5ms. That's fine.

The S3 hop is the problem. S3 is object storage built for durability and throughput, not low latency. A single S3 GET request takes **50–200ms** under normal conditions. At peak that's variable and often worse.

Your read SLO is **p99 < 50ms**. S3 alone blows that SLO before Postgres even responds.

---

## The decision: cache the URL or cache the content?

When you first think about caching, the instinct is to cache the S3 URL — it's small (a few hundred bytes vs 10KB of content), so you fit more entries in RAM. The logic seems sound.

But it doesn't solve the problem.

```
Cache hit (S3 URL cached):
  Redis lookup → get S3 URL → S3 GET → return content
  Total latency: ~1ms (Redis) + ~50–200ms (S3) = still violates SLO

Cache hit (content cached):
  Redis lookup → return content directly
  Total latency: ~1ms
  SLO met.
```

Caching the URL still makes a round trip to S3 on every cache hit. You've only saved the Postgres lookup — you haven't touched the slow part.

**The decision comes down to two things:**

1. **Latency requirements** — if your SLO is tight (p99 < 50ms), you cannot afford an S3 hop on cache hits. You must cache content directly.
2. **RAM availability** — caching content at 10KB per paste costs more memory than caching URLs at ~200 bytes per paste. If RAM is genuinely scarce, caching URLs is a reasonable trade-off — you accept higher latency in exchange for fitting more entries in cache.

In Pastebin's case: RAM is cheap (we calculated ~6GB needed), and the SLO is tight. Both factors point to caching content directly in Redis.

```
Decision:
  Tight SLO + cheap RAM  → cache content (our case)
  Relaxed SLO + scarce RAM → cache S3 URL (acceptable trade-off)
```

---

## What caching gives you

```
Without cache:
  Every read → Postgres + S3 → 50–200ms → SLO violated

With Redis cache:
  Cache hit  → Redis only → ~1ms → SLO met
  Cache miss → Postgres + S3 → ~50–200ms → populate cache → SLO may be tight on first hit
```

Cache misses still hit S3 — that's unavoidable on first access. But once a paste is in Redis, every subsequent read is sub-millisecond. Given the 100:1 read:write ratio, most reads are repeat reads, so the cache hit rate will be high.

---

> [!tip] Interview framing
> "S3 is 50–200ms. Our read SLO is p99 < 50ms. Without caching we violate the SLO on every read. Caching the S3 URL doesn't help — you still make the S3 round trip on cache hits. We cache the content itself in Redis. The decision of URL vs content comes down to two things: latency requirements and available RAM. Our SLO is tight and RAM is cheap, so we cache content."
