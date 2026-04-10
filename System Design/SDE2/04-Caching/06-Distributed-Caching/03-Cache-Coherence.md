# Cache Coherence

> [!info] When you have multiple cache nodes or replicas, they can hold different values for the same key. Coherence means keeping them consistent with each other.

---

## The problem

A write updates the primary cache node. Replicas haven't caught up yet. A read hits a replica and gets the old value.

```
Write: user updates profile picture
  → primary cache node updated ✓
  → replica A: not yet updated ← 50ms lag
  → replica B: not yet updated ← 50ms lag

Read request routes to replica A:
  → returns old profile picture ✗
```

This is the same eventual consistency problem that exists in DB replication — and the same trade-offs apply.

---

## Option 1 — Async replication (default for most caches)

Primary confirms write, replicas catch up in the background:

```
Write → update primary → return success → replicas update ~50ms later

✓ Fast writes — primary doesn't wait for replicas
✓ High availability — slow replica doesn't block anything
✗ Brief stale window on reads from replicas
```

For most cache data — feed counts, product listings, session data — a 50ms stale window is invisible to users. Async replication is the default.

---

## Option 2 — Sync replication

Primary waits for all replicas to confirm before returning success:

```
Write → update primary → wait for all replicas to confirm → return success

✓ All replicas always consistent
✗ Write latency = slowest replica round trip
✗ If any replica is slow or down → writes are blocked
```

Rarely used for cache — the performance cost negates much of the caching benefit.

---

## Option 3 — Primary reads (simplest)

Route all reads to the primary. Replicas exist only for failover, not for serving reads:

```
Writes → primary
Reads  → primary
Replicas → standby for failover only
```

No coherence problem — there's only one node serving data. Clean and simple until the primary becomes the throughput bottleneck.

---

## The CAP trade-off applies to caches too

> [!important] The cache layer faces the same consistency vs availability trade-off as databases
> During a network partition between primary and replica:
> - Serve reads from primary only (CP) → consistent, but if primary is unreachable, cache is unavailable
> - Serve reads from replica (AP) → available, but may return stale data
> Most caches choose AP — a stale cache hit is better than a cache miss that hammers the DB.
