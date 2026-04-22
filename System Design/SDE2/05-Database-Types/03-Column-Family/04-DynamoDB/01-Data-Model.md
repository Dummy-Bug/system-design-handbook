> [!info] DynamoDB is AWS's fully managed wide-column store. No servers to provision, no indexes to tune manually, no replication to configure. You define a partition key, optionally a sort key, and DynamoDB handles everything else — sharding, replication across 3 availability zones, scaling up and down automatically.

AWS markets DynamoDB as a "key-value store" because the simplest use case is: give it a key, get back an item. But that label is misleading. A partition key can return multiple items. A sort key lets you query ranges of items within a partition. You can get back one item, many items, or a sorted slice — that's wide-column behavior, not pure key-value.

True key-value (Redis): one key → exactly one value, always.
DynamoDB: partition key → one partition containing many rows, sorted by sort key. Much richer.

> [!info] DynamoDB has two keys: a partition key that routes your data to the right server, and an optional sort key that orders your data within that server. Everything else — joins, flexible queries, schema — is your problem to solve upfront in how you model your data.

---

## The problem DynamoDB solves

You're building Instagram. Users post photos, like posts, watch stories. At 500M users you're generating billions of writes per day — every like, every view, every scroll event.

A single SQL server with a B+ tree index handles reads fine — O(log n) lookup, fast enough. But billions of writes per day overwhelm a single machine. You need to shard.
okay why 
DynamoDB is sharding built into the database itself. You don't manage it — you just define a partition key and DynamoDB handles the rest.

---

## Partition key — which server

When you write a row, DynamoDB runs the partition key through a hash function. The hash output determines which physical server (partition) stores that row.

```
user_id: 42   → hash(42)   = 7823...  → Server 3
user_id: 891  → hash(891)  = 2341...  → Server 1
user_id: 205  → hash(205)  = 9102...  → Server 7
```

When you read, DynamoDB hashes the partition key again, goes directly to that server. No broadcasting, no scanning all servers.

```
Query: give me user 42's data
→ hash(42) → Server 3
→ done. O(1) regardless of how many servers exist.
```

This is consistent hashing — the same mechanism used in distributed caches and manual sharding setups, except DynamoDB manages it automatically.

---

## Sort key — order within a partition

The sort key is optional. When present, all rows with the same partition key are stored together on the same server, physically sorted by the sort key.

```
Table: likes
Partition key: user_id
Sort key: created_at

Server 3 (user_id = 42):
  → like: post_1, created_at: 2024-01-01
  → like: post_5, created_at: 2024-01-03
  → like: post_9, created_at: 2024-01-07
```

All of user 42's likes live on one server, in chronological order. A single read fetches them all — or a range of them — without touching any other server.

---

## How data is stored underneath — LSM Tree

DynamoDB stores data within each partition using an LSM Tree (Log-Structured Merge Tree). Writes go to an in-memory buffer first, then flush to disk in sorted order — extremely fast writes, no random disk seeks.

> See `06-Storage-and-Databases/04-Indexing/04-LSM-Tree.md` for the full explanation.

This is why DynamoDB is write-heavy friendly — the same reason Cassandra is. The LSM tree underneath absorbs write bursts without the penalty of in-place B+ tree updates.

---

## The full picture

```
Write: user_id=42, post_id=9, created_at=2024-01-07
  → hash(42) → Server 3
  → stored in LSM tree, sorted by created_at within user 42's partition

Read: give me all likes by user 42 in January
  → hash(42) → Server 3
  → range scan on created_at within that partition
  → one server, one fast sequential read
```

> [!important] The partition key decides WHERE. The sort key decides ORDER within that where. Everything is designed around these two keys — there is no query planner figuring things out at runtime.
