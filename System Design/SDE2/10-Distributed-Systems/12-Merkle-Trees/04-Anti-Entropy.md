
> [!info] The core idea
> Anti-entropy is the periodic background process that detects and fixes silent divergence between replicas. Entropy means disorder — replicas drifting apart. Anti-entropy fights that drift. Merkle Trees are the mechanism that makes anti-entropy efficient. Only leaderless databases need this — leader-based databases use WAL replay instead.

---

## What anti-entropy means

**Entropy** in physics means disorder. In distributed systems it means replicas drifting apart — data that should be identical slowly diverging due to missed writes, network failures, or node crashes.

**Anti-entropy** is the process that fights that drift — periodically comparing replicas against each other and syncing the differences back.

Think of it like reconciliation in accounting. Your internal books should match the bank statement. You don't verify every transaction in real time — you do a periodic reconciliation to catch anything that slipped through. Anti-entropy is that reconciliation for database replicas.

---

## How Cassandra runs anti-entropy repair

Cassandra runs anti-entropy as a background job. At a configured interval — or triggered manually — each node builds a Merkle Tree for its local data and exchanges it with the other replicas holding the same data.

```
Node A builds Merkle Tree → sends root hash to Node B
Root hashes differ → drill down level by level
Find differing buckets → sync only those rows
Replicas back in sync ✓
```

Cassandra exposes this as a manual command: `nodetool repair`. In production, operators run it regularly — typically once per `gc_grace_seconds` (the window before deleted data is permanently removed) to ensure all replicas are consistent before tombstones expire.

---

## Which databases need anti-entropy — and which don't

The need for Merkle Tree-based anti-entropy comes down to one thing — **does the database have a single source of truth for write ordering?**

**Leaderless databases — need anti-entropy:**

In a leaderless system like Cassandra or DynamoDB, any node can accept any write independently. There is no central log. A write can reach Node A but silently miss Node B — and Node B has no way of knowing it missed anything. Silent divergence is a real and ongoing risk.

```
Cassandra  → leaderless, any node accepts writes → needs Merkle Tree repair
DynamoDB   → leaderless internally → uses Merkle Trees for replica sync
Riak       → leaderless like Cassandra → same problem, same solution
```

**Leader-based databases — WAL replay is enough:**

In MySQL, PostgreSQL, or any Raft-based system, there is one primary that controls all writes. Replicas follow the WAL sequentially. If a replica falls behind, it knows exactly where it stopped and replays from that point. There is no such thing as silently missing a write — the replica either has it or it knows it's behind.

```
MySQL / PostgreSQL  → single primary, sequential WAL → replica just replays from last position
etcd / CockroachDB  → Raft-based, leader controls writes → gap detection built into protocol
```

> [!important] The pattern
> Merkle Trees solve a problem that only exists in leaderless architectures — multiple nodes accepting writes independently with no single ordered log. If you have a leader, WAL replay handles divergence. If you don't, you need Merkle Trees.

> [!tip] Interview framing
> "Cassandra uses Merkle Trees for anti-entropy repair. Because it's leaderless, any node can accept writes independently — meaning a node can silently miss a write with no way of knowing. Periodically, Cassandra builds a Merkle Tree for each replica — a tree of hashes over buckets of data. Two replicas compare their trees top-down. Matching hashes mean identical data — skip. Differing hashes mean divergence — drill down. Within about 10 levels you've pinpointed the exact rows that differ, without ever transferring the full dataset. MySQL doesn't need this because replicas follow a single WAL sequentially — they can't silently diverge."
