# MongoDB — Replication and Sharding

> [!info] MongoDB's replication and sharding follow the same fundamentals covered in the database replication and sharding notes — primary-replica, consistent hashing, quorum writes. The MongoDB-specific pieces are: replica sets as the replication unit, write concern levels for tunable durability, and mongos as the transparent query router.

---

## Replica Sets — MongoDB's replication unit

A replica set is one primary and one or more secondaries. All writes go to the primary. Secondaries replicate asynchronously.

```mermaid
graph TD
    App["App Server"]
    App -->|"all writes"| Primary
    Primary -->|"async replication"| Secondary1["Secondary 1"]
    Primary -->|"async replication"| Secondary2["Secondary 2"]
    App -->|"reads (optional)"| Secondary1
    App -->|"reads (optional)"| Secondary2
```

If the primary goes down, the secondaries hold an election and promote one of themselves to primary automatically. No manual intervention needed.

---

## Write Concern — tunable durability

Write concern controls how many nodes must confirm a write before MongoDB returns success to your application. You set it per-operation.

```
w: 0        →  fire and forget — don't even wait for primary acknowledgement
               fastest, zero durability guarantee
               use for: metrics, analytics, logs where losing a write is acceptable

w: 1        →  primary confirmed (default)
               primary has written it, secondaries may not have replicated yet
               risk: primary crashes before replicating → write lost
               use for: non-critical writes, high-throughput event storage

w: majority →  more than half the nodes confirmed
               survives primary crash — majority already have the data
               slower (waits for replication round trip)
               use for: user profile updates, orders, payments, anything critical
```

This is the same R + W > N quorum principle from replication notes — majority write ensures at least one surviving node has the data after any single-node failure.

```
3-node replica set, w: majority = 2 nodes must confirm

Write arrives → primary writes → secondary 1 writes → "success" returned
             → secondary 2 replicates in background

Primary crashes → secondary 1 still has the write → no data loss ✓
```

---

## Sharding — scaling beyond one replica set

When a single replica set can't handle the data volume or write throughput, MongoDB shards across multiple replica sets. Each shard is itself a replica set.

You pick a **shard key** — MongoDB hashes it and routes to the right shard. Same consistent hashing you know from DynamoDB and the sharding notes.

The MongoDB-specific piece is **mongos** — a query router that sits between your application and the shards:

```mermaid
graph TD
    App["App Server"]
    App -->|"query"| Mongos["mongos\n(query router)"]
    Mongos -->|"hash(shard_key) → Shard 1"| Shard1["Shard 1\n(replica set)"]
    Mongos -->|"hash(shard_key) → Shard 2"| Shard2["Shard 2\n(replica set)"]
    Mongos -->|"hash(shard_key) → Shard 3"| Shard3["Shard 3\n(replica set)"]
```

Your application connects to mongos as if it's a single MongoDB instance. mongos knows which shard holds which key ranges, routes the query, returns the result. The sharding is completely transparent to the application.

---

## Summary

```
Replica set    →  1 primary + N secondaries, automatic failover
Write concern  →  w:0 (fire/forget) → w:1 (primary) → w:majority (quorum)
Sharding       →  consistent hashing on shard key, each shard is a replica set
mongos         →  transparent query router, app talks to one endpoint
```

> [!tip] Interview framing
> "MongoDB replication uses replica sets — one primary, multiple secondaries, automatic failover. Write concern is tunable: w:majority for critical data to ensure quorum durability, w:1 for high-throughput non-critical writes. For horizontal scaling, MongoDB shards via consistent hashing with a mongos router that makes sharding transparent to the application."
