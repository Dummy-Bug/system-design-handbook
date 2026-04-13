
> [!info] Sharding splits data. Replication protects it.
> Each shard is a single machine. If that machine dies, the chunk of data it owns becomes unavailable — and since URLs are durable (once created, never lost), that's a violation of a core NFR. Every shard needs replicas.

---

## Why each shard needs replicas

Sharding gives you storage scale. But each shard is still a single point of failure. If Shard-3 goes down:

```
Without replication:
All short codes that hash to Shard-3 → unavailable
Redirects return 404
Users cannot follow links → business impact
```

Replication means each shard has multiple copies of its data on different machines. If the primary fails, a secondary takes over.

---

## The replication setup — 3 replicas per shard

The standard production setup is **1 primary + 2 secondaries** per shard:

```
Shard-1:
  Primary   → handles all writes
  Secondary → replicates from primary, handles reads
  Secondary → replicates from primary, handles reads (spare for failover)
```

Why 3 total (not 2)?

With 2 replicas (1 primary + 1 secondary):
- Primary dies → secondary becomes primary → now you have only 1 machine → zero fault tolerance
- Before you can provision a new replica, you're one machine failure away from data loss

With 3 replicas (1 primary + 2 secondaries):
- Primary dies → one secondary becomes primary → you still have 1 secondary → fault tolerant while you provision a replacement

3 replicas is the minimum for production durability. This is why Kafka, Cassandra, MongoDB, and most distributed systems default to a replication factor of 3.

---

## Reads and writes with replication

```
Writes → always go to the primary
         Primary replicates to secondaries asynchronously

Reads  → can go to primary or secondaries
         Secondaries may be slightly stale (async replication lag)
```

For a URL shortener:
- Redirect reads go to secondaries — slight staleness is acceptable. A URL created 1 second ago might not be on the secondary yet, but that's a rare edge case covered by read-your-own-writes (next file).
- Creation writes go to the primary.

This also helps with read throughput. With 2 secondaries per shard, read traffic is spread across 3 machines per shard instead of 1. Combined with caching, this comfortably handles the remaining 20k DB reads/sec.

---

## Total machine count

```
8 shards (day 1 provisioning) × 3 replicas = 24 machines
64 shards (long-term target)  × 3 replicas = 192 machines
```

192 machines sounds like a lot. But at 250TB across 64 shards, each shard holds ~4TB. A 4TB SSD machine is commodity hardware. This is well within the infrastructure budget of a system handling 100M users.

---

## Replication lag — the one problem

Async replication means secondaries are not always perfectly up to date. After a write to the primary, there's a small window — typically milliseconds — before the secondaries reflect the change.

For most redirects this doesn't matter — the URL was created days or weeks ago and is fully synced across all replicas.

The one case it matters: the creator clicking their own link immediately after creation. That's the read-your-own-writes problem — covered in the next file.

---

> [!tip] Interview framing
> "3 replicas per shard — 1 primary, 2 secondaries. Writes go to primary, reads to secondaries. 3 replicas because losing 1 still leaves 2 machines — you stay fault tolerant while provisioning a replacement. With 8 shards on day 1, that's 24 machines. Long-term at 64 shards, 192 machines. Async replication means secondaries are slightly stale — covered by read-your-own-writes for the creator edge case."
