> [!info] In most systems, reads vastly outnumber writes — often 100:1. Forcing both through a single database node means reads and writes compete for the same connections, locks, and CPU. Read/Write Splitting routes writes to a primary node and reads to replica nodes, scaling each independently.

# The Problem — One Node For Everything

## Reads vastly outnumber writes

Take Twitter. 300 million daily users open their feed multiple times a day — every one of those is a read. A much smaller fraction actually posts a tweet — that's a write.

The ratio for most social apps:

```
Reads : Writes = 100 : 1
```

This isn't unique to Twitter. Most systems are read-heavy by nature — users consume far more than they produce. E-commerce sites: browsing products (reads) vs placing orders (writes). News sites: reading articles (reads) vs publishing them (writes).

---

## What happens on a single node

If your database is one node handling both reads and writes simultaneously, two problems emerge:

**Problem 1 — Connection pool exhaustion**

Your connection pool has a fixed size — say 20 connections. At 100:1 read/write ratio, reads are consuming most of those connections constantly. **A write arrives and has to wait in queue behind a flood of reads**. Write latency spikes even though the write itself is simple.

**Problem 2 — Lock contention**

Reads and writes compete for row-level locks. A heavy write — say a bulk insert or an update touching many rows — locks those rows. Concurrent reads on the same rows are blocked until the write completes. Read latency spikes because of writes it had nothing to do with.

```
Single node:
  Read  Read  Read  Read  Write  Read  Read
  ↓     ↓     ↓     ↓     ↓      ↓     ↓
  [DB — one node, one connection pool, shared locks]
  → reads slow down writes
  → writes slow down reads
  → both suffer
```

---

## The natural fix

Separate the concerns. Have dedicated nodes for reads and dedicated nodes for writes. They no longer compete.

> [!important] Why not just scale the single node vertically?
> You can — add more CPU, more RAM, faster SSDs. But vertical scaling has a ceiling and is expensive. Horizontal scaling (adding read replicas) is cheaper and scales linearly. Adding a replica doubles your read capacity. Adding another doubles it again.
