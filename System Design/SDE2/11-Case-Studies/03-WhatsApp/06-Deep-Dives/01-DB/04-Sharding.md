
> [!info] Do we need manual sharding?
> Sharding means splitting data across multiple nodes so no single node holds everything or handles all traffic. In Postgres you manage this yourself. In DynamoDB, it's handled internally — what DynamoDB calls "partitions" is what Postgres engineers call "shards." The question is whether we need to intervene manually or let DynamoDB handle it.

---

## Sharding vs Partitioning — same concept, different ownership

```
Postgres sharding:
  → You decide how many shards
  → You build the routing layer (which shard gets this conversation_id?)
  → You manage rebalancing when nodes are added or removed
  → You handle cross-shard queries
  → Fully manual, fully your problem

DynamoDB partitioning:
  → DynamoDB decides how many partitions
  → DynamoDB handles routing internally via consistent hashing
  → DynamoDB rebalances automatically as data grows
  → You never think about it — unless a partition gets too hot (covered next)
```

This is one of the core reasons DynamoDB was chosen over Postgres — not just write throughput, but eliminating the entire operational burden of manual sharding.

---

## Do the numbers require manual intervention?

Let's check both throughput and storage against DynamoDB's per-partition limits:

**Throughput:**
```
Peak WPS            → 20k writes/sec
Peak RPS            → 20k reads/sec
Total ops/sec       → 40k ops/sec

DynamoDB per-partition limits:
  Write  → 1,000 WPS
  Read   → 3,000 RPS
  Total  → 4,000 ops/sec per partition

Partitions needed for throughput = 40,000 / 4,000 = 10 partitions minimum
```

10 partitions for throughput — trivial.

**Storage:**
```
Hot data (90 days)           → 22.5 TB = 22,500 GB
DynamoDB per-partition limit → 10 GB

Partitions needed for storage = 22,500 / 10 = 2,250 partitions
```

Storage dominates. DynamoDB automatically creates ~2,250 partitions to hold 22.5 TB.

**Throughput capacity unlocked by those 2,250 partitions:**
```
2,250 partitions × 4,000 ops/sec = 9,000,000 ops/sec available
Actual need                      = 40,000 ops/sec

Headroom: 225× more capacity than needed
```

The storage requirement forces DynamoDB to create far more partitions than throughput alone would need. Those extra partitions come with massive throughput headroom as a side effect.

---

## Conclusion — no manual sharding needed

DynamoDB auto-partitions based on storage and throughput. With 22.5 TB of hot data, it creates ~2,250 internal partitions automatically. No routing layer to build, no rebalancing to manage, no cross-shard queries to handle.

The only manual intervention needed is **hot partition salting** — when a specific conversation_id generates too many writes to a single partition. That's a throughput concentration problem, not a sharding problem. It's covered in the next section.

```
Manual sharding (Postgres style) → not needed
DynamoDB auto-partitioning       → handles it
Hot partition salting            → only for conversation-level throughput spikes
```

> [!tip] Interview framing
> DynamoDB handles partitioning automatically. With 22.5 TB of hot data it creates ~2,250 partitions, giving us 9M ops/sec of capacity against our 40k ops/sec need — 225× headroom. No manual sharding needed. The only manual intervention is hot partition salting for individual conversations that exceed 1,000 WPS — which is a different problem.
