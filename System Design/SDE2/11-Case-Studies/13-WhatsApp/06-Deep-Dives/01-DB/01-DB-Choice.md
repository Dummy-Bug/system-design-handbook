
> [!info] Choosing the right database starts with access patterns
> Don't pick a database and then figure out if it fits. Start with what the system actually does to data — the reads, the writes, the queries — and let that drive the choice.

---

## The access patterns

There are two core access patterns for message storage:

**Write pattern — send a message:**
```
INSERT message INTO conversation C1
  sender = A, content = "hey", timestamp = T
```
Pure append. No updates, no complex joins. Just insert a new row at the end of a conversation.

**Read pattern — load chat history:**
```
FOR conversation C1
  GIVE ME last 20 messages
  BEFORE timestamp T
  SORTED chronologically
```
Range scan within a single conversation. No cross-conversation joins. No aggregations. No full-text search.

These two patterns tell you everything you need to know about what the database must be good at:
- Fast sequential writes (appends)
- Fast range reads within a single partition key

---

## Write volume — why single-instance relational DBs fail

```
Peak write QPS → 20k writes/sec
Single Postgres instance → 5k–10k WPS (with indexes, constraints, WAL overhead)
```

A single Postgres instance cannot sustain 20k WPS. You'd need to shard it manually — partition the data across multiple instances, build a routing layer, manage cross-shard consistency, handle rebalancing when nodes are added. Postgres was not designed for this. It becomes an operational nightmare at this scale.

---

## Why Postgres is rejected

Postgres is a general-purpose relational database. Its strengths are:
- Complex multi-table joins
- Flexible ad-hoc queries
- ACID transactions across multiple rows and tables
- Rich indexing (B-tree, GIN, partial indexes)

None of these strengths are needed here. The access patterns are simple and uniform — always by `conversation_id`, always a range scan on `timestamp`. No joins. No aggregations. No flexible queries. Paying the overhead of a relational DB (WAL, MVCC, constraint checking) for a workload that doesn't need any of it makes no sense.

MongoDB is rejected for the same reason — it adds document model flexibility (nested JSON, dynamic schema) that chat messages simply don't need.

---

## Why Cassandra and DynamoDB win

Both are wide-column stores with the same fundamental data model:

```
Partition Key → identifies which node holds the data (conversation_id)
Sort Key      → orders data within the partition (timestamp)
```

This maps perfectly to the access patterns:
- Write: append a new row under `conversation_id` partition — O(1), sequential write to LSM tree
- Read: range scan within `conversation_id` partition — contiguous on disk, fast sequential read

Both use **LSM trees** (Log-Structured Merge trees) under the hood. LSM trees are optimised for write-heavy workloads — writes go to an in-memory buffer first (MemTable), then flush to disk as sorted files (SSTables). No random disk seeks on writes. Perfect for append-heavy chat data.

```
Write throughput:
  Postgres (single instance) → 5k–10k WPS
  Cassandra / DynamoDB       → 100k+ WPS
```

20k peak WPS is well within range. No manual sharding needed for throughput.

---

## Cassandra vs DynamoDB

Both are technically correct choices. The difference is operational:

```
Cassandra:
  → Self-managed (or via DataStax)
  → Full control over compaction, replication factor, consistency level tuning
  → More operational overhead — you run the cluster, you handle failures
  → Better for teams with Cassandra expertise

DynamoDB:
  → Fully managed by AWS
  → No cluster to tune, no compaction to worry about, no node failures to handle
  → Pay-per-request or provisioned capacity
  → Less control, more convenience
```

**Choice: DynamoDB.** The data model fits identically. At this scale, not managing a Cassandra cluster is a significant operational advantage. The engineering team can focus on the application, not the database infrastructure.

> [!tip] Interview framing
> "The access patterns are simple — append writes and range reads within a conversation. That rules out Postgres and Mongo — too much overhead for queries we don't need. Cassandra and DynamoDB both fit perfectly: partition key on conversation_id, sort key on timestamp, LSM trees for fast sequential writes. I'd pick DynamoDB over Cassandra to avoid managing the cluster — same data model, less operational burden."
