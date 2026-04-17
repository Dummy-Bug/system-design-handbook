## The Fundamental Decision

Before drawing any architecture, we need to answer one question: **how do nodes coordinate writes?** Everything else — replication, consistency, failure handling — flows from this choice.

There are three options:

```
1. Single-leader      — one node accepts all writes, replicas follow
2. Multi-leader       — multiple nodes accept writes, sync with each other
3. Leaderless         — no node is special, quorum math guarantees correctness
```

We'll evaluate each one against our requirements: 30K writes/sec, 300K reads/sec, 12 PB of data across 1,200 nodes, tunable consistency (clients can choose strong or eventual per request), and high availability.

---

## Option 1 — Single-Leader

### How it works

One node is the **primary** (leader). All writes go to that node. The primary writes to its WAL, applies the change, then replicates to follower replicas asynchronously via a replication stream.

```
Write path:
  Client → Primary → write to WAL → ack to client → replicate to replicas async

Read path (eventual consistency):
  Client → any replica → return value (might be slightly behind primary)

Read path (strong consistency):
  Client → primary → return value (guaranteed latest)
```

### Can we shard it?

At 12 PB of data, a single machine can't hold everything. So we'd need to shard — split the key space into ranges, each range owned by a separate shard. Each shard has its own primary and replicas.

```
Shard 1: keys hash range 0-999      → Primary A + Replica B, Replica C
Shard 2: keys hash range 1000-1999  → Primary D + Replica E, Replica F
...
Shard N: keys hash range ...        → Primary X + Replica Y, Replica Z

~1,200 nodes → hundreds of shards, each with its own primary
```

This is exactly what MongoDB does — sharded, with each shard having a single primary.

### Where strong vs eventual consistency lives

This is a critical point to understand. In single-leader, the strong vs eventual trade-off **only exists on the read path, not the write path.**

**Writes are always the same.** Every write goes to the primary. There's no "fast write" vs "durable write" option — the primary is the only node that accepts writes. The client sends the write, the primary confirms, done. Whether you configure sync replication (primary waits for one replica to ack) or async replication (primary acks immediately, replicas catch up later), the write still **funnels through the primary**. The client always talks to the primary for writes.

**Reads are where the choice happens:**

```
Eventual read → hit any replica → fast, one hop, but might be slightly stale
                The replica streams changes from the primary's WAL
                There's a small window where the replica hasn't caught up yet

Strong read   → hit the primary → guaranteed latest, but all reads funnel
                through one node instead of spreading across replicas
```

Read-your-own-writes is handled by routing the reading client to the primary for a short window after their write, then falling back to replicas once replication catches up.

### Why we reject it

The rejection comes down to one scenario: **what happens when a primary dies?**

The replicas still have the data (possibly slightly behind). But before the shard can accept writes again:

1. Replicas detect the primary is down (heartbeat timeout — a few seconds)
2. Leader election runs (Raft or similar — a few more seconds)
3. A replica is promoted to new primary
4. The shard starts accepting writes again

**During this window, all writes to that shard are blocked.** Every client — whether they wanted strong consistency or eventual consistency — gets rejected. There's no "just write to a replica instead" option, because replicas don't accept writes in single-leader.

Now think about our scale. We have ~1,200 nodes. At large clusters, industry data shows roughly 2-3 machine failures per day per 1,000 nodes. That means on any given day, some shard's primary is dying. Some shard is always in failover. Some writes are always being blocked.

Our NFR promised **tunable consistency** — clients can choose availability over consistency. A client storing user preferences doesn't care about perfect consistency, they just want their write to succeed. Single-leader can't offer this. When the primary is down, everyone is blocked, even clients who'd happily accept a weaker guarantee.

```
Single-leader rejection:

  ✓ Reads can be tunable (replica for eventual, primary for strong)
  ✗ Writes always funnel through one node — no availability-first option
  ✗ Primary dies → writes blocked for entire shard during failover
  ✗ At 1,200 nodes, some shard is always in failover → constant write disruptions
  ✗ Cannot fulfill our "tunable consistency" NFR on the write path
```

---

> [!tip] Interview framing
> "Single-leader won't work here. The strong vs eventual trade-off only applies to reads — writes always funnel through the primary. When a primary dies, writes are blocked until leader election completes. At 1,200 nodes, some shard's primary is always failing — we can't have constant write disruptions. And we promised tunable consistency on writes too, which single-leader fundamentally can't offer. This is the architecture MongoDB uses — great for smaller clusters, but not for a 1,200-node KV store with availability requirements."
