# Distributed Caching — Interview Cheatsheet

---

## The standard answer for "how do you scale your cache?"

> "I'd distribute the cache across multiple nodes using consistent hashing so adding or removing nodes only remaps ~1/N of keys. Each node has a replica for availability — Redis Sentinel handles automatic failover. For extreme read volume, I'd add a local in-process L1 cache on each app server to absorb the hottest keys without a network round trip."

---

## One-line definitions

> [!info] Consistent Hashing
> Keys and nodes mapped to a ring. Each key routes to the first node clockwise. Adding/removing a node remaps ~1/N of keys instead of ~80%.

> [!info] Virtual Nodes
> Each physical node gets 150-200 positions on the ring for even key distribution. Prevents one node owning a disproportionate share of the keyspace.

> [!info] Cache Coherence
> Keeping multiple cache replicas in sync. Async replication is the default — brief stale window. Sync replication is consistent but slow.

> [!info] Two-Level Caching (L1 + L2)
> Local in-process cache (nanoseconds, per-server) + Redis (1ms, shared). L1 eliminates Redis round trips for the hottest keys.

---

## Key numbers to know

```
L1 local cache   → nanoseconds
L2 Redis         → ~1ms
DB query         → ~10ms+

Single Redis node capacity → typically 32-64GB RAM
Single Redis node throughput → ~100,000 ops/sec
```

---

## Failure scenarios and answers

| Failure | Impact | Fix |
|---|---|---|
| Cache node dies, no replicas | ~1/N of keys become DB misses | Consistent hashing limits blast radius |
| Cache node dies, with replicas | Zero impact — replica promotes | Redis Sentinel handles automatically |
| Mass key expiry | Cache miss spike → DB hammered | TTL jitter, Refresh-Ahead |
| Scale out (add node) | ~1/N of keys remap | Consistent hashing minimises disruption |
| Cold start on recovery | Keys remap back to empty node → misses | Warm up before returning to live traffic |
