# Cassandra — Interview Cheatsheet

---

## The trigger in your head

```
Write-heavy + time-series + known entity at query time?  →  Cassandra
Need cross-entity queries ("all tweets with X")?         →  Cassandra + Elasticsearch
Joins, transactions, relational data?                    →  SQL
Interviewer asks "how does Cassandra scale writes?"      →  Ring + LSM tree (CommitLog → MemTable → SSTable)
Interviewer asks "how do you guarantee consistency?"     →  R + W > N  (QUORUM + QUORUM)
```

---

## The three scenarios to nail

### 1. "Design a time-series analytics system"

> "How would you store and query billions of sensor readings per day?"

**Wrong answer:** Postgres with a timestamp index — hits write throughput ceiling fast.

**Right answer:**
> "I'd use Cassandra. The partition key encodes the sensor ID, the clustering column is timestamp — so all readings for a given sensor are physically sorted on disk. Queries like 'give me sensor_42's readings for the last hour' become a sequential scan of one contiguous partition. Cassandra's LSM tree absorbs the write volume natively through CommitLog and MemTable, without the random-write overhead of row-oriented SQL."

---

### 2. "Cassandra is AP — so reads can be stale, right?"

**Wrong answer:** "Yes, Cassandra is eventually consistent."

**Right answer:**
> "Not necessarily. Cassandra's consistency is tunable. With QUORUM on both reads and writes, R+W > N — at least one node overlaps between the write set and read set, guaranteeing you always read the latest write. The AP label only applies at lower consistency levels like ONE. You choose the trade-off per operation."

---

### 3. "What if you need to query across all users, not just one?"

> "Your Cassandra cluster has data for 100 million users. How do you find all users in a given city?"

**Wrong answer:** Filter by city in the WHERE clause — Cassandra will do a full cluster scan.

**Right answer:**
> "Cassandra has no efficient global secondary index. A city filter without a partition key means scanning every node, every partition. I'd pair Cassandra with Elasticsearch — Cassandra stores the raw data, Elasticsearch maintains a global index for cross-entity searches. CDC streams changes from Cassandra's commitlog to Elasticsearch to keep them in sync."

---

## One-line definitions

> [!info] Consistent Hashing (Ring)
> Hash space 0–2^64 laid out as a ring. Each node owns an arc. Partition key is hashed to find the owning node. Adding a node only moves data in the affected arc — not the whole cluster.

> [!info] CommitLog
> Append-only file on disk. Every write is recorded here first for durability. Replayed on restart to rebuild the MemTable if the server crashed.

> [!info] MemTable
> In-memory sorted data structure. Holds recent writes in partition key + clustering column order. Flushed to SSTable when full.

> [!info] SSTable (Sorted String Table)
> Immutable, sorted file on disk produced by a MemTable flush. Updates create new SSTables — existing files are never modified.

> [!info] Compaction
> Background process that merges multiple SSTables into one, keeping only the latest version of each key. Reduces the number of files reads must check.

> [!info] Bloom Filter
> Probabilistic in-memory structure per SSTable. Can say "definitely not here" (skip the file entirely) or "maybe here" (read the file). Never misses a key that exists, but can false-positive. Eliminates most disk reads on the read path.

> [!info] Replication Factor (RF)
> How many copies of each row exist across nodes. RF=3 means 3 nodes store every row.

> [!info] Consistency Level
> How many replicas must acknowledge a read or write before success. ONE = 1, QUORUM = majority, ALL = every replica.

> [!info] Tombstone
> A delete marker written as a regular append. Marks a row as logically deleted. Original data stays on disk until compaction runs and erases both the tombstone and the original value together.

> [!info] TTL (Time To Live)
> A per-write expiry setting. When TTL expires, Cassandra automatically writes a tombstone. Standard pattern for expiring IoT and time-series data without application-level deletes.

---

## The R + W > N rule

| RF | Write CL | Read CL | W + R | > N? | Result |
|---|---|---|---|---|---|
| 3 | QUORUM (2) | QUORUM (2) | 4 | ✅ > 3 | Strong consistency |
| 3 | ONE (1) | ONE (1) | 2 | ❌ ≤ 3 | Eventual consistency |
| 3 | ALL (3) | ONE (1) | 4 | ✅ > 3 | Strong consistency, fragile writes |

---

## What Cassandra guarantees

| Property | Detail |
|---|---|
| Write throughput | Millions/sec via LSM tree — all writes are sequential appends |
| Range queries | Fast when scoped to a known partition key (sequential scan) |
| Scalability | Add nodes with minimal data movement via consistent hashing ring |
| Tunable consistency | ONE / QUORUM / ALL per operation — trade throughput for guarantees |
| No single point of failure | Masterless — any node can be coordinator |

> [!danger] What Cassandra does NOT guarantee
> No joins. No multi-partition transactions. No efficient cross-entity queries without a secondary index tool. If you don't know the partition key at query time, Cassandra will scan the entire cluster.
