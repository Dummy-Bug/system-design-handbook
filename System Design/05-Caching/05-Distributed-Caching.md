# Distributed Caching

## Why Single Node Doesn't Scale

> [!info] Single cache node has two fundamental problems at scale.

```
1. Memory limit   → one server can only hold so much data
                    10M users × 10KB profile = 100GB → doesn't fit on one node

2. SPOF           → node goes down → entire cache gone
                    all requests hit DB simultaneously → DB collapses
```

Solution: distribute the cache across multiple nodes.

New problem: a request comes in for `user:123:profile` — which node do you go to?

---

## Consistent Hashing

> [!info] Hash keys to nodes on a ring. Adding/removing nodes only affects neighbouring keys — not the entire keyspace.

**Why not simple modulo hashing:**

```
10 nodes: hash("user:123") % 10 = 7  → node 7
Add node: hash("user:123") % 11 = 3  → node 3 ✗ different node

~90% of all keys map to different nodes → mass cache miss → DB collapses
```

**Consistent hashing:**

```
Nodes placed on a ring: A────B────C────A

Keys between A and B → owned by B
Keys between B and C → owned by C
Keys between C and A → owned by A

Add node D between B and C:
  → only keys between B and D move from C to D
  → everything else untouched

A────B───D───C────A
         ↑
    only this slice remapped
```

Only the slice the new node takes over is affected. No global reshuffling.

**Virtual nodes:** each physical node gets multiple positions on the ring for even distribution. Prevents hot spots when nodes have different capacities.

**Interview answer:**
> "I'd use consistent hashing so adding or removing cache nodes only remaps a minimal fraction of keys — roughly 1/N of the keyspace — instead of causing a mass cache miss."

---

## Cache Coherence

> [!info] Multiple nodes or replicas can hold different values for the same key. This is cache coherence — keeping them in sync.

```
Write → Primary Node 7 updated ✓
      → Replica 7a still has old value ✗
      → Replica 7b still has old value ✗

Next read → hits Replica 7a → stale data returned
```

**Solutions:**

```
Sync replication   → write confirmed only after all replicas updated
                     consistent but slower writes

Async replication  → write confirmed after primary, replicas catch up later
                     faster writes, brief staleness window (milliseconds)
                     most caches use this
```

**Simpler approach — primary reads:**

```
Writes → primary
Reads  → primary only (not replicas)
Replicas → failover only, not serving reads
```

Clean, no coherence issue. Works until scale gets huge.

**At massive scale:**

```
Small scale    → read from primary → strong consistency, simple
Massive scale  → read from replicas → eventual consistency, lower latency

Same trade-off as databases — CAP/PACELC applies to the cache layer too.
No free lunch.
```

---

## Replication

> [!info] Read replicas serve two purposes — availability and read throughput.

```
Availability   → primary goes down → replica promotes → cache stays up
Read throughput → spread read load across replicas → primary not bottlenecked
```

**Replication lag:** async replication means replicas are slightly behind primary. Acceptable for most cache data — a few milliseconds of staleness.

---

## Two-Level Caching (L1 + L2)

> [!info] Local in-process cache (L1) + distributed Redis cache (L2). Best of both worlds.

```
Request comes in
→ check L1 (local, nanoseconds)
  → hit  → return immediately
  → miss → check L2 (Redis, ~1ms)
    → hit  → store in L1, return
    → miss → hit DB → store in L2 + L1 → return
```

```
L1 (local)   → nanoseconds, per-server, inconsistency risk across servers
L2 (Redis)   → ~1ms, shared across all servers, consistent
DB           → ~10ms+, source of truth
```

Used by Instagram, Twitter, and most large-scale systems in production.

**L1 invalidation problem:** when data changes in Redis, local caches on each server still have the old value. Solutions:
```
Short TTL on L1 entries   → stale for at most TTL duration, simple
Pub/Sub invalidation      → Redis publishes invalidation event, all servers clear L1
```

---

## Handling Node Failure

> [!info] Consistent hashing minimises the blast radius when a node fails.

```
Node 7 goes down
→ consistent hashing routes its keys to next node on ring
→ those keys are cache misses temporarily
→ gradually repopulate as requests come in
→ rest of the cluster unaffected
```

With replicas:
```
Primary fails → replica promotes to primary → no cache miss at all
→ replication provides seamless failover
```

---

## Summary

```
Consistent hashing   → minimal remapping on node add/remove, use always
Cache coherence      → async replication for speed, primary reads for simplicity
Replication          → availability + read throughput
Two-level caching    → L1 local (nanoseconds) + L2 Redis (~1ms)
Node failure         → consistent hashing limits blast radius, replicas provide failover
```
