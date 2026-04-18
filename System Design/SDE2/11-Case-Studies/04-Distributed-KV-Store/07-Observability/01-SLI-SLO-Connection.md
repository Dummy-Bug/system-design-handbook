
> [!info] SLO is the target. SLI is the measurement. You need both.
> Writing "p99 EC read < 10ms" in your NFR is easy. Knowing whether you're actually hitting it in production — with 1,200 nodes, compaction running, vnodes rebalancing, and anti-entropy competing for disk I/O — requires something else entirely.

---

## The gap between design and reality

When we designed this KV store, we made assumptions. Memtable lookups are sub-millisecond. Bloom filters skip 99% of SSTables. WAL appends are fast sequential writes. We ran the numbers and concluded: p99 write latency should be under 20ms, EC reads under 10ms.

But those are estimates. Production is not a whiteboard.

Maybe compaction is running aggressively on a node, consuming disk bandwidth — SSTable reads that normally take 1ms now take 15ms. Maybe a node just restarted and its OS page cache is cold — every read hits physical disk instead of cached pages. Maybe gossip marked a node as dead 8 seconds too late, and the coordinator wasted time sending requests to a node that wasn't responding. Maybe a Bloom filter had a spike in false positives because a particular SSTable has an unusual key distribution.

**None of this shows up in your estimates. It only shows up when you measure.**

---

## What SLI actually means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

Our KV store has three latency SLOs and one availability SLO from the NFR. Each maps directly to an SLI:

```
SLO 1:  p99 eventually consistent read < 10ms
SLI 1:  actual measured p99 of all GET requests with consistency=eventual

SLO 2:  p99 strongly consistent read < 50ms
SLI 2:  actual measured p99 of all GET requests with consistency=strong

SLO 3:  p99 write latency < 20ms
SLI 3:  actual measured p99 of all PUT requests

SLO 4:  99.99% availability
SLI 4:  successful requests / total requests, measured continuously
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

---

## Why "checking if the node is alive" is not enough

With 1,200 nodes, the instinct is to rely on gossip — if a node's heartbeat is incrementing, it's alive and healthy. But gossip tells you about **node liveness**, not **request quality**.

A node can be alive in gossip while:
- Serving corrupted data (silent disk corruption, checksum failures)
- Returning stale data (missed writes during a partition, anti-entropy hasn't run yet)
- Responding slowly (compaction consuming all disk I/O, memtable flush blocking writes)
- Accepting writes but failing reads (disk full — WAL appends fail, existing SSTables still readable)

All of these pass the gossip heartbeat check. None of them are caught by node-level health monitoring. SLIs measure what **clients actually experience** — did their request succeed, and how long did it take?

---

## KV store-specific SLIs beyond latency and availability

Beyond the standard latency and availability SLIs, a distributed KV store needs to track metrics specific to its internal mechanisms:

```
SLI                              What it tells you
───                              ─────────────────
Read repair rate                 How often quorum reads find stale replicas
                                 High rate → replicas are diverging frequently

Hinted handoff queue depth       How many hints are waiting to be delivered
                                 Growing queue → nodes are staying down too long

Anti-entropy differences found   How many keys differ per Merkle tree comparison
                                 High count → something is systematically broken

Bloom filter false positive rate Percentage of "probably here" that were wrong
                                 Above 1% → filters may need resizing

Compaction backlog               How many SSTables are waiting to be compacted
                                 Growing backlog → compaction can't keep up with writes

SSTable count per node           How many SSTables exist on each node
                                 High count → reads are getting slower (more files to check)

Tombstone ratio                  Percentage of reads that hit tombstones
                                 High ratio → lots of deleted data not yet compacted
```

These aren't SLOs — you don't page someone at 3am for a Bloom filter false positive rate of 1.2%. But they're leading indicators that something is drifting toward a real SLO breach. By the time p99 latency actually crosses 10ms, the root cause (compaction backlog, cold cache, SSTable accumulation) has been building for hours.

---

> [!tip] Interview framing
> "SLO is the target from our NFR — p99 EC read under 10ms, write under 20ms, 99.99% availability. SLI is what we actually measure in production. We track SLIs separately for eventual vs strong consistency reads because they have different latency profiles and different SLOs. Beyond client-facing SLIs, we track internal metrics — read repair rate, compaction backlog, Bloom filter false positive rate, hinted handoff queue depth — as leading indicators. These catch problems before they become SLO breaches. Gossip heartbeats tell us if nodes are alive, but SLIs tell us if the service is actually working."
