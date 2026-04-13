
> [!info] The storage problem
> Caching solves the read throughput problem — 80% of reads never reach the DB. But there is a second problem that caching cannot fix: 250TB of data over 10 years cannot fit on a single machine. That requires sharding.

---

## What caching does and doesn't fix

After adding Redis:

```
Read throughput  → FIXED. 80% of reads served from cache. DB sees ~20k reads/sec.
Storage          → NOT FIXED. All 250TB still lives on one machine.
```

A single machine — even a large one — tops out at around 10-20TB of practical storage for a database. SSDs are expensive, and beyond a certain size, a single machine becomes a single point of failure for your entire dataset.

From the estimation:

```
Storage per year        = 25TB
Storage over 10 years   = 250TB
Single machine limit    = ~10-20TB practical
```

250TB on one machine is not feasible. The data must be split across multiple machines. This is sharding.

---

## What sharding means

Sharding means splitting your dataset horizontally — different rows live on different machines. Each machine (shard) owns a subset of the data.

```
Without sharding:
  One machine → stores all 250TB → single point of failure, storage ceiling hit

With sharding:
  Shard 1 → stores rows where short_code starts with [a-f]
  Shard 2 → stores rows where short_code starts with [g-m]
  Shard 3 → stores rows where short_code starts with [n-z]
  ...and so on
```

Each shard is an independent Postgres instance. Queries are routed to the correct shard based on the short code.

---

## Sharding is not the same as replication

These two concepts are often confused:

```
Replication → same data on multiple machines (for fault tolerance and read scaling)
Sharding    → different data on different machines (for storage scaling)
```

Sharding splits the dataset. Replication copies it. You need both — sharding to fit the data, replication to survive machine failures. Each shard will have its own replicas.

---

> [!important] When to shard
> Don't shard prematurely. Sharding adds significant operational complexity — cross-shard queries become harder, transactions spanning shards are difficult, and adding shards requires data migration. Shard when you actually need it — when storage or write throughput cannot be handled by a single machine, even with vertical scaling. For this system, 250TB forces the decision.

---

**Next:** Once you decide to shard, the most important question is: what column do you use to decide which shard a row belongs to?
