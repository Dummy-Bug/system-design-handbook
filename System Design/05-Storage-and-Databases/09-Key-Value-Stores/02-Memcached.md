> [!info] Memcached is a simple, multi-threaded, in-memory cache. It predates Redis and has one job — store strings in RAM and return them fast. No data structures, no persistence, no replication. Just raw caching throughput.

## What Memcached is

The entire Memcached interface:

```
SET key value TTL  → store something
GET key            → retrieve it
DELETE key         → remove it
```

That's essentially the full feature set. No sorted sets, no bitmaps, no streams, no Lua scripts, no persistence. Restart Memcached and everything is gone. No built-in replication, no Sentinel, no Cluster.

---

## The one advantage — multithreading

Redis is single-threaded — it uses one CPU core regardless of how many cores the server has. Memcached is multi-threaded — it uses all available cores.

```
Redis on a 16-core machine:
  Uses 1 core out of 16
  Ceiling: ~1,000,000 ops/sec

Memcached on the same 16-core machine:
  Uses all 16 cores
  Ceiling: ~10,000,000–16,000,000 ops/sec

Same hardware. Up to 16x the throughput for pure cache reads.
```

---

## When multithreading actually matters

This advantage is only real in a specific scenario: small values, extreme read throughput, where RAM is not the bottleneck but CPU is.

```
10M feature flags × 100 bytes = 1GB RAM used (out of 256GB) ← RAM is fine
2,000,000 reads/sec requested
→ exceeds Redis's 1M ops/sec single thread ← CPU is the ceiling

Redis:      CPU overloaded at 200%, requests queue up, latency spikes ✗
Memcached:  16 cores absorb 2M ops/sec easily ✓
```

---

## Why Memcached is rare in new systems today

Redis caught up:

```
1. Memcached             → multi-threaded, handles 2M ops/sec on one node
   
2. Redis + sharding      → shard reads across 3 Redis nodes, each at 700K ops/sec
                             → same throughput, plus all Redis features

With Redis Cluster, sharding is handled automatically.
You get the throughput AND data structures, persistence, Streams.
```

Memcached only wins if:
- You need maximum raw throughput on a single node
- You have no need for any Redis feature beyond simple GET/SET
- You can't shard (rare)

That combination almost never exists in new systems. Which is why Redis has largely replaced Memcached in practice — Redis hits the same throughput ceiling for 99% of workloads, while offering far more.

---

## Memcached vs Redis — honest comparison

| | Memcached | Redis |
|---|---|---|
| Threading | Multi-threaded — all cores | Single-threaded — one core |
| Raw throughput | Higher on same hardware | ~1M ops/sec per node |
| Data structures | Strings only | String, Hash, List, Sorted Set, Set, HyperLogLog, Bitmap, Stream |
| Persistence | None — restart = data gone | RDB, AOF, Hybrid |
| Replication | Not built-in | Sentinel (failover), Cluster (sharding) |
| Use today | Legacy systems, extreme throughput edge case | Default choice for almost everything |

> [!tip] Interview framing
> "I'd use Redis as the default. Memcached only comes up if I'm in Scenario B — small values, extreme read throughput above 1M ops/sec on a single node, and I can't shard. In practice, Redis Cluster handles that case just as well while keeping all of Redis's other capabilities."
