
> [!info] You cannot store 330K individual latency measurements per second. You don't need to.
> 300K reads/sec + 30K writes/sec = 330K requests/sec. At 86,400 seconds per day, that's ~28.5 billion data points daily. The trick is to throw away the raw numbers and keep only the shape of the distribution.

---

## The naive approach and why it fails

The obvious way to measure p99 latency: record the response time of every request, sort all of them at the end, find the 99th percentile value.

At 330K requests/second:

```
330,000 requests/sec
× 86,400 seconds/day
= 28,512,000,000 data points per day  (~28.5 billion)
```

Storing 28.5 billion latency values (even at 4 bytes each) would require ~114 GB per day. And sorting 28.5 billion values to compute a percentile is computationally impractical in real time.

You need a completely different approach.

---

## Histograms — keep the shape, throw away the raw values

Instead of storing individual latency values, you define a set of **buckets** — ranges of latency — and keep a counter for each bucket. Every request increments exactly one counter based on how long it took.

For our KV store, we need **separate histograms** for each operation type because they have different SLOs:

### Eventually consistent reads (SLO: p99 < 10ms)

```
Bucket          Counter
0-1ms:          180,000
1-5ms:          55,000
5-10ms:         12,000
10-20ms:        2,500
20-50ms:        400
50ms+:          100
-----------------------
Total:          250,000  (reads/sec at R=1)
```

### Strongly consistent reads (SLO: p99 < 50ms)

```
Bucket          Counter
0-5ms:          15,000
5-10ms:         18,000
10-20ms:        12,000
20-50ms:        4,500
50-100ms:       400
100ms+:         100
-----------------------
Total:          50,000  (reads/sec at R=2)
```

### Writes (SLO: p99 < 20ms)

```
Bucket          Counter
0-5ms:          20,000
5-10ms:         7,000
10-20ms:        2,500
20-50ms:        400
50ms+:          100
-----------------------
Total:          30,000  (writes/sec)
```

Instead of storing 330,000 individual numbers per second, you store 18 integers (6 buckets × 3 operation types). The counters live in memory on each node — incrementing a counter is a single atomic operation, essentially free.

---

## Computing p99 from a histogram

p99 means: the latency value below which 99% of requests fall. For EC reads with 250,000 total requests/sec, you need the bottom 247,500.

Walk the buckets in order, accumulating a running total until you cross 247,500:

```
0-1ms bucket:    180,000  →  running total: 180,000
1-5ms bucket:    55,000   →  running total: 235,000
5-10ms bucket:   12,000   →  running total: 247,000
10-20ms bucket:  2,500    →  running total: 249,500  ← 247,500 falls in here
```

p99 lands in the 10-20ms bucket. SLO says < 10ms. **We're breaching SLO.** Time to investigate — maybe compaction is running hot, maybe OS page cache is cold, maybe Bloom filter false positives spiked.

---

## Merging histograms across 1,200 nodes

Each of our 1,200 nodes builds its own histogram independently. To get a cluster-wide p99, you add the bucket counts together:

```
Node 1:     0-1ms: 150   1-5ms: 46   5-10ms: 10 ...
Node 2:     0-1ms: 148   1-5ms: 47   5-10ms: 11 ...
Node 3:     0-1ms: 153   1-5ms: 44   5-10ms: 9  ...
...
Node 1200:  0-1ms: 151   1-5ms: 45   5-10ms: 10 ...
────────────────────────────────────────────────────
Cluster:    0-1ms: 180,000  1-5ms: 55,000  5-10ms: 12,000 ...
```

Histograms are mergeable by design — just add the counters. This is why histograms are the standard tool for distributed latency measurement. Raw values are not mergeable without storing everything.

---

## Where the measurement happens

In our system, every node can be a coordinator. The latency that matters is the **end-to-end time from receiving the client request to sending the response** — measured at the coordinator, not at the individual replica nodes.

```
Coordinator measures:
  Start timer → hash key → find replicas → send requests → wait for quorum
  → compare timestamps (if strong) → respond to client → Stop timer

This captures EVERYTHING:
  → Ring lookup time
  → Network hop to replicas
  → Replica read/write time (memtable, Bloom filter, SSTable, WAL)
  → Quorum wait time (slowest of W or R responses)
  → Read repair overhead (if triggered)
```

Measuring at the coordinator is correct because that's what the client experiences. If a replica is slow but the quorum is met by faster replicas, the client latency is still good — and that's what the SLI should reflect.

---

## Who does the scraping

Each node exposes its histogram counters on a `/metrics` endpoint. A metrics collector (Prometheus) scrapes all 1,200 nodes at regular intervals, merges the histograms, and stores the result.

```
Every 15 seconds:
Prometheus → GET /metrics from node 1    → histogram snapshot
Prometheus → GET /metrics from node 2    → histogram snapshot
...
Prometheus → GET /metrics from node 1200 → histogram snapshot
→ merge all histograms (per operation type)
→ compute cluster-wide p99 for EC reads, SC reads, writes
→ store time-series result
```

With 1,200 nodes, scraping every 15 seconds means 80 scrapes per second — trivial for Prometheus. You now have cluster-wide p99 for each operation type, updated every 15 seconds. Plot it over time and you get a latency graph. Set thresholds at 10ms (EC reads), 50ms (SC reads), and 20ms (writes) for alerting.

---

## Per-node histograms for debugging

The merged cluster-wide histogram tells you **if** there's a problem. Per-node histograms tell you **where**. If cluster p99 spikes, you look at individual node histograms to find the outlier:

```
Cluster p99 EC read: 15ms  ← breaching 10ms SLO

Per-node breakdown:
  Node 1-1198: p99 = 5-8ms  ← healthy
  Node 1199:   p99 = 45ms   ← THIS node is the problem
  Node 1200:   p99 = 42ms   ← this one too

Investigation: Node 1199 and 1200 are on the same rack
  → rack switch is degraded → network latency spike
```

---

> [!tip] Interview framing
> "We can't store 330K raw latency measurements per second. Instead, each node maintains histograms — separate ones for EC reads, SC reads, and writes because they have different SLOs. Each histogram has buckets like 0-1ms, 1-5ms, 5-10ms. p99 is computed by walking buckets until you hit 99% of total requests. Histograms are mergeable — Prometheus scrapes all 1,200 nodes every 15 seconds, adds bucket counts, computes cluster-wide p99. Measurement happens at the coordinator because that's the end-to-end latency the client experiences. Per-node histograms help isolate which specific nodes are causing a cluster-wide SLO breach."
