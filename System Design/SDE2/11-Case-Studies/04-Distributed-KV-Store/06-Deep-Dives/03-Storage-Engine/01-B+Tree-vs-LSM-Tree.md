## Starting From Our Numbers

Before choosing a storage engine, let's see what each node actually handles. We need to go from cluster-level numbers to per-node numbers — because the storage engine lives on a single node.

### Our estimated scale

```
Cluster-level:
  Writes: 30K/sec (peak)
  Reads:  300K/sec (peak)
  Nodes:  1,200
  Replication factor: N=3
```

### Per-node write load

Each write goes to N=3 nodes (the replica set). So the total node-level writes across the cluster is higher than the client-level write rate:

```
Client writes:     30K/sec
× replication:     × 3
= Node-level writes: 90K/sec across the entire cluster

Per node: 90K / 1,200 = 75 writes/sec per node
```

75 writes/sec per node. That's tiny.

### Per-node read load

For reads, it depends on the consistency level. With eventual consistency (R=1), each read hits only 1 node. With strong consistency (R=2), each read hits 2 nodes. Let's take the worst case — all reads are strong (R=2):

```
Client reads:      300K/sec
× quorum reads:    × 2
= Node-level reads: 600K/sec across the entire cluster

Per node: 600K / 1,200 = 500 reads/sec per node
```

Even in the worst case: 500 reads/sec per node.

```
Summary per node:
  Writes: 75/sec
  Reads:  250-500/sec (depending on consistency level)
```

---

## Can B+ Tree Handle This?

**Absolutely.** A single B+ Tree on an SSD can handle:

```
Random reads:   5,000 - 50,000/sec (depends on data size and caching)
Random writes:  1,000 - 10,000/sec (each write may trigger page splits)
```

Our per-node load of 75 writes/sec and 500 reads/sec is **well within** what a B+ Tree can handle. It's not even close to the limit. We could 10x the traffic and B+ Tree would still be comfortable.

### What about reads?

B+ Tree is actually **optimized for reads**. Every lookup is O(log n) — traverse from root to leaf, following pointers. With billions of keys, that's maybe 4-5 levels deep. The top levels of the tree stay in memory (page cache), so most reads hit disk only once (for the leaf page). At 500 reads/sec, this is trivial.

```
B+ Tree read path:
  Root (in memory) → Internal node (in memory) → ... → Leaf (maybe 1 disk read)
  Total: O(log n) = ~4-5 comparisons for billions of keys
  Latency: sub-millisecond if cached, 1-5ms if hitting disk
```

---

## What If We Had 300K Writes/sec Instead?

Let's stress test this. Imagine the interviewer says "make it write-heavy — 300K writes/sec instead of 30K." Now the numbers change:

```
Client writes:     300K/sec
× replication:     × 3
= Node-level writes: 900K/sec across the cluster

Per node: 900K / 1,200 = 750 writes/sec per node
```

750 writes/sec per node. Can B+ Tree handle this?

```
B+ Tree on SSD: 1,000 - 10,000 random writes/sec
Our load:       750 writes/sec

Still within range. B+ Tree survives even a 10x write increase.
```

So even at 10x the write load, B+ Tree doesn't collapse. The numbers show it can handle it.

---

## So Why Not Just Use B+ Tree?

If B+ Tree handles both our current scale and a 10x write increase, why do Cassandra, DynamoDB, and RocksDB all use LSM Trees? There are three reasons.

### Reason 1 — Write amplification on B+ Tree gets worse over time

B+ Tree writes are **random I/O**. When you write a key, the tree finds the correct leaf page, modifies it in place, and writes it back to disk. The problem is:

```
B+ Tree write path:
  1. Read the leaf page from disk (4 KB page)
  2. Modify the one key-value pair you care about
  3. Write the entire 4 KB page back to disk
  4. Maybe the page is full → page split → write 2 pages + update parent
```

You wanted to write 1 KB of data, but you had to read and rewrite a 4 KB page. That's **write amplification** — the disk does more work than the actual data change requires.

It gets worse:
- Page splits cascade upward — one write can trigger multiple page writes
- The pages are scattered across the disk — random I/O, not sequential
- As the tree grows and fragments, the ratio of useful writes to total disk writes gets worse

At 75 writes/sec this doesn't matter. At 750 writes/sec it's noticeable. At 7,500 writes/sec it becomes a real problem — especially on HDDs where random writes are 100x slower than sequential writes.

### Reason 2 — LSM Tree turns random writes into sequential writes

LSM Tree's write path is radically different:

```
LSM Tree write path:
  1. Write to WAL (append-only, sequential — the fastest possible disk write)
  2. Write to memtable (in-memory sorted structure)
  3. Ack to client — done

  Later (in background):
  4. Memtable fills up → flush to disk as an SSTable (one big sequential write)
  5. SSTables accumulate → compaction merges them (sequential reads and writes)
```

Every disk write is **sequential** — appending to the WAL, flushing a sorted file, merging sorted files. No random page reads, no page splits, no in-place modifications.

```
Sequential vs random writes on SSD:
  Sequential: 500 MB/s - 3 GB/s
  Random:     50 MB/s - 500 MB/s

Sequential vs random writes on HDD:
  Sequential: 100 - 200 MB/s
  Random:     0.5 - 2 MB/s (100x slower!)
```

At any write rate, LSM Tree does less disk work per write than B+ Tree. The gap is small at 75 writes/sec (both are fine), but becomes huge as write rates increase.

### Reason 3 — The KV store is general-purpose infrastructure

This is the real reason. Our current estimation says 10:1 read-heavy. But our KV store will be used by **many different services**:

```
Service A (user profiles):     100:1 read-heavy   → B+ Tree would be great
Service B (IoT telemetry):     1:100 write-heavy   → B+ Tree would struggle
Service C (session store):     1:1 balanced         → either works
Service D (event logging):     pure writes          → B+ Tree would be terrible
```

If we pick B+ Tree, we optimize for Service A but hurt Service B and D. If we pick LSM Tree, we handle all four workloads well:

- Write-heavy? LSM Tree is built for this — sequential writes, no page splits
- Read-heavy? LSM Tree adds Bloom filters and block cache to make reads fast enough
- Balanced? LSM Tree handles both

LSM Tree is the **more flexible** choice. It's not the fastest for any single workload, but it's good enough for all of them. That's what you want for general-purpose infrastructure.

---

## The Trade-off — What LSM Tree Gives Up

LSM Tree isn't strictly better. It trades **read performance** for **write performance**:

```
                    B+ Tree              LSM Tree
                    ───────              ────────
Write speed         Good (random I/O)    Great (sequential I/O)
Read speed          Great (O(log n))     Good (check memtable → check SSTables)
Write amplification Higher (page splits) Lower (sequential flushes)
Read amplification  Lower (one tree)     Higher (multiple SSTables to check)
Space amplification Lower                Higher (duplicate keys across SSTables
                                         until compaction merges them)
Best for            Read-heavy           Write-heavy or mixed
```

The key weakness of LSM Tree is **read amplification**. A read might need to check the memtable, then multiple SSTables on disk. If the key is in the oldest SSTable, you've checked every level before finding it. This is where Bloom filters come in — they skip SSTables that definitely don't contain the key, bringing read performance close to B+ Tree in practice.

---

## Our Decision — LSM Tree

```
At our estimated scale (75 writes/sec, 500 reads/sec per node):
  → Either storage engine works fine
  → B+ Tree would actually be slightly better for our 10:1 read-heavy ratio

At scale (if workload changes to write-heavy):
  → B+ Tree struggles with random I/O and page splits
  → LSM Tree handles it naturally with sequential writes

For a general-purpose KV store serving many different services:
  → LSM Tree is the more flexible, future-proof choice
  → Read performance gap is closed by Bloom filters and caching
```

This is why Cassandra, DynamoDB (uses LSM-based storage), LevelDB, and RocksDB all chose LSM Trees. Not because B+ Tree can't handle the throughput — but because LSM Tree handles a wider range of workloads without falling off a cliff when writes spike.

> [!important] In an interview, know both options
> If the interviewer says "this is a read-heavy system, justify your storage engine choice," you can argue for B+ Tree — and that's correct. If they say "general-purpose KV store" or "write-heavy," LSM Tree is the answer. Knowing why both work (and when each wins) is stronger than dogmatically picking one.

---

> [!tip] Interview framing
> "At our scale of 75 writes/sec per node, both B+ Tree and LSM Tree work fine — the per-node load is well within either engine's capability. We chose LSM Tree because this is general-purpose infrastructure — different services will use it with different read/write ratios. LSM Tree handles write-heavy workloads by turning random writes into sequential I/O, while Bloom filters close the read performance gap. B+ Tree would be the right choice for a dedicated read-heavy service, but for a KV store that needs to handle any workload, LSM Tree is more flexible. This is why Cassandra and DynamoDB both use LSM-based storage."
