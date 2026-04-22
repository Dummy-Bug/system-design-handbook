> [!info] Redis and DynamoDB look similar on the surface — both are fast, both are key-based lookups. But they are fundamentally different types of databases solving different problems.

## Why they look similar — and why that's misleading

Both Redis and DynamoDB are accessed by a key. Both return data fast. That surface-level similarity is why DynamoDB was historically grouped with Redis under "key-value stores."

But the similarity stops at the API. Underneath they are completely different:

```
Redis      →  true key-value: one key → one value, always
DynamoDB   →  wide-column: partition key → many rows, sorted by sort key, range queries supported
```

Redis is a pure key-value store. `GET user:123` returns one thing. If you want richer structure, you use Redis data types (sorted sets, hashes, lists) — but it's still one key mapping to one structure.

DynamoDB is a wide-column store marketed as key-value. A partition key maps to a whole partition of rows. You can query a range of sort keys, get the last 50 items, scan a slice. That's the same model as Cassandra — it just lives inside AWS and AWS calls it key-value for simplicity.

## The actual difference

```
Redis      →  in-memory, sub-millisecond, single-node ceiling, rich data structures
DynamoDB   →  disk-backed, low millisecond, scales infinitely, managed sharding
```

Redis keeps everything in RAM. A read is a RAM lookup — ~200ns. DynamoDB reads from SSD-backed storage — still fast, but low milliseconds not nanoseconds.

DynamoDB manages sharding automatically across as many servers as needed. Redis needs manual sharding via Redis Cluster. At truly massive scale (billions of rows), DynamoDB is operationally simpler.

---

## When to use Redis

```
✓  Sub-millisecond latency is a hard requirement (real-time leaderboards, session tokens)
✓  Rich data structures needed (Sorted Sets for rankings, Lists for queues, HyperLogLog)
✓  Pub/Sub or Streams for event processing
✓  Data fits in RAM (or you're fine sharding manually)
✓  Cache layer in front of another database
```

## When to use DynamoDB

```
✓  Data is too large for RAM — billions of rows, terabytes of data
✓  Write-heavy at massive scale (likes, events, activity logs)
✓  Simple access patterns — lookup by key, range by sort key
✓  Don't want to manage infrastructure (fully managed on AWS)
✓  Multi-region low latency via Global Tables
```

---

## Side by side

| | Redis | DynamoDB |
|---|---|---|
| Storage | RAM | SSD (disk-backed) |
| Latency | ~200ns (sub-millisecond) | Low millisecond |
| Scale | Manual sharding (Redis Cluster) | Auto-sharding, infinite scale |
| Data structures | String, Hash, List, Sorted Set, Stream | Wide-column (partition key + sort key, range queries) |
| Persistence | Optional (RDB/AOF) | Always persistent |
| Managed | Self-hosted or Redis Cloud | Fully managed (AWS) |
| Multi-region | Manual setup | Global Tables (built-in) |
| Best for | Cache, real-time, pub/sub | Massive persistent wide-column storage at scale |

---

## The typical pattern in production

They're not mutually exclusive. Most large systems use both:

```
Request → Redis (cache, sub-millisecond)
           ↓ cache miss
         DynamoDB (persistent store, millisecond)
```

Redis is the hot layer. DynamoDB is the source of truth. Redis absorbs the read traffic, DynamoDB handles durability and scale.

> [!tip] Interview framing
> "For a cache layer I'd use Redis — sub-millisecond, rich data structures. For persistent storage of billions of events I'd use DynamoDB — auto-sharding, fully managed, handles write-heavy workloads without me managing Redis Cluster. In practice both often coexist — Redis in front, DynamoDB behind."
