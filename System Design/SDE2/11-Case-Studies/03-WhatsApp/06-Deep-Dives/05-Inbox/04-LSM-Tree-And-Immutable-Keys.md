
> [!info] Why you can't update a sort key — LSM tree immutability
> Cassandra and DynamoDB use LSM trees internally. SSTables are immutable. Changing a sort key isn't an update — it's a delete plus an insert.

---

## How LSM tree writes work

LSM stands for Log-Structured Merge tree. It's the storage engine under Cassandra, DynamoDB, and RocksDB.

Every write goes to an in-memory buffer first — the **memtable**:

```
Write arrives → memtable (RAM)
                ↓ (when full)
              SSTable (disk)
```

When the memtable fills up, it's flushed to disk as an **SSTable** — a Sorted String Table. Rows are written in sorted key order and the file is sealed. It is never modified after being written.

```
SSTable on disk:
  (alice, 8:00am) → { conv_id: conv_work, message: "standup at 10" }
  (alice, 8:30am) → { conv_id: conv_carol, message: "see you tmrw"  }
  (alice, 9:42am) → { conv_id: conv_bob,  message: "hey what's up?" }
```

Sorted. Immutable. Cannot be changed in place.

---

## Why immutability — the cost of in-place modification

Modifying a value in the middle of a sorted file would require shifting every row after it. For a file with millions of rows, that's a full rewrite of the file on every update. At WhatsApp scale — billions of messages per day — that would make disk I/O the bottleneck for everything.

LSM tree solves this by making writes append-only. New data always goes to a new memtable, then a new SSTable. Old SSTables are never touched. Periodically, a background **compaction** process merges SSTables and discards old versions — but this happens offline, not on the write path.

---

## What happens when you "update" a sort key

Say Alice's conversation with Bob has SK = `9:30am`. Bob sends a new message. The sort key needs to become `9:42am`.

You cannot go into the SSTable and move the row. Instead:

```
Step 1: Write a tombstone for (alice, 9:30am)
        → "this row is deleted"

Step 2: Write a new row (alice, 9:42am)
        → { conv_id: conv_bob, message: "hey what's up?", ... }
```

Two writes. The old row now exists on disk as a tombstone — a marker that says "ignore this." At read time, the tombstone suppresses the old row. At compaction time, both the tombstone and the old row are cleaned up.

---

## The tombstone problem at scale

At WhatsApp scale:

```
100B messages sent per day
Each message → 1 tombstone + 1 new insert on conversations table
             → 2 writes per message, per participant (sender + receiver)
             → 400B extra write operations per day
```

Tombstones accumulate on disk until compaction runs. Between compaction cycles:
- Read performance degrades — the DB has to scan and skip tombstones on every query
- Disk space is wasted on rows that are logically deleted but physically still present
- Compaction itself is expensive and competes with live traffic

This is the true cost of `SK = last_message_timestamp`. The sort is free at read time, but every message send leaves a tombstone behind.

> [!danger] Tombstone accumulation is a real operational problem in Cassandra
> In production Cassandra clusters, excessive tombstones from high-churn sort keys have caused read timeouts and cluster instability. It's not a theoretical concern.

> [!tip] Interview framing
> "In LSM-tree databases like Cassandra and DynamoDB, the sort key is part of the primary key and SSTables are immutable. Changing the sort key means writing a tombstone for the old row and inserting a new row. At WhatsApp scale, a timestamp sort key on the conversations table means hundreds of billions of tombstones per day — a real operational problem."
