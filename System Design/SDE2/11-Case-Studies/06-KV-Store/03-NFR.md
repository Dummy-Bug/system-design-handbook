## Durability — the highest priority

This is a database, not a cache. Once the system acknowledges a `put`, that data must not be lost — even if the node crashes one second later. This is the non-negotiable NFR that separates a KV store from Redis.

In practice, this means the write must be persisted to a durable medium (WAL on disk) and replicated to at least one other node before the client gets an acknowledgment. We never return success on a write that only exists in one machine's memory.

```
Client → put(key, value)
  → write to WAL on disk (node A)
  → replicate to node B and node C
  → ack to client
  → data survives even if node A dies immediately after
```

---

## CAP Trade-off — tunable, not fixed

In a distributed system, when a network partition happens, you must choose between availability and consistency. But the key insight for a KV store is: **you don't have to make this choice globally — you make it per request.**

This is exactly what DynamoDB and Cassandra do. The client chooses on each request:

- **Eventually consistent read** — fast, can hit any replica. Might return slightly stale data (milliseconds behind). Good for use cases like user profiles, feature flags, session data — where milliseconds of staleness don't matter.

- **Strongly consistent read** — slower, must contact a quorum of replicas to guarantee you're reading the latest write. Good for use cases like financial balances, inventory counts — where stale data causes real problems.

**Why not just always be strongly consistent?**

Because it costs latency and availability. A strongly consistent read must wait for a quorum to respond — if one replica is slow or partitioned, the read is slow or fails. An eventually consistent read can return immediately from any single healthy replica. At 300K reads/sec, that latency difference adds up — and during a partition, strongly consistent reads would fail entirely while eventually consistent reads keep working.

**When there's no partition (normal operation):**

During normal operation (no partition), you're not forced into the CAP trade-off. Here we prioritize **consistency over latency** — because this is a source of truth. We minimize the inconsistency window as much as possible through fast replication. The eventually consistent path still exists for clients who want maximum speed, but the system is designed to converge quickly.

```
CAP during partition:
  AP mode → client says "give me eventual consistency, keep serving"
  CP mode → client says "give me strong consistency, reject if can't guarantee"

Normal operation (no partition):
  Consistent by default — replicas converge in milliseconds
  Client can still opt into eventual consistency for extra speed
```

---

## Consistency — tunable per request

The consistency model is the most important design decision for a KV store. We support two modes:

**Eventually consistent (default):**
Read can go to any replica. The value might be slightly behind the latest write — by milliseconds, not seconds. The system uses anti-entropy (Merkle trees) and read repair to converge replicas quickly. For most use cases, this is indistinguishable from strong consistency.

**Strongly consistent (opt-in):**
Read goes to a quorum. With replication factor N=3, a quorum read contacts at least 2 replicas and returns the value with the highest timestamp. Combined with quorum writes (W=2), this guarantees W + R > N (2 + 2 > 3), so at least one node in the read quorum has the latest write.

```
Tunable consistency via quorum:

  N = 3 (replication factor)
  W = 2 (write to 2 nodes before ack)    → write is durable
  R = 2 (read from 2 nodes)              → read sees latest write
  
  W + R > N → 2 + 2 > 3 → strong consistency guaranteed
  
  OR for speed:
  R = 1 (read from 1 node)               → fast but possibly stale
  W + R ≤ N → 2 + 1 ≤ 3 → eventual consistency
```

---

## Latency SLO — single-digit milliseconds, not hundreds

A KV store is a simple key lookup — not a complex SQL query. The latency target is much tighter than you'd expect:

```
Eventually consistent read:    p99 < 10ms
Strongly consistent read:      p99 < 50ms
Write:                         p99 < 20ms
```

**Why so fast even though data is on disk?**

Writes don't hit disk synchronously for the data path. They go to an in-memory memtable first (LSM Tree architecture). The WAL (Write-Ahead Log) is a sequential disk append — the fastest disk operation possible. The client gets an ack after WAL + memtable, both of which are fast.

Reads have multiple shortcuts before touching disk:

1. **Memtable** (memory) — recently written keys are here
2. **Block cache** (memory) — frequently accessed SSTables are cached in RAM
3. **Bloom filter** (memory) — skips SSTables that definitely don't contain the key
4. **Disk** — only if all the above miss

Most reads at scale never actually touch the disk. That's why single-digit millisecond latency is achievable for a disk-backed store.

The strongly consistent read is slower (50ms vs 10ms) not because of disk — but because it must wait for multiple replicas to respond and agree. Network round-trips between nodes add latency.

---

## Fault Tolerance — partial failure is normal operation

At 1,200 nodes, machine failures aren't an edge case — they're a daily occurrence. If even 0.1% of nodes fail per day, that's 1-2 nodes dying every day. The system must handle this as routine, not as an emergency.

**What fault tolerance means here:**
- 200 nodes down out of 1,200 → system still fully operational
- Data on failed nodes is still accessible via replicas (replication factor 3 means 2 copies survive)
- Failed nodes are detected automatically (gossip protocol, heartbeats)
- Data re-replicates to healthy nodes to restore replication factor
- No human intervention needed for routine failures

---

## Data Integrity — what goes in must come out unchanged

The value the client reads must be **byte-for-byte identical** to what they wrote. No corruption, no partial writes, no silent data mutation. This is enforced through checksums — every value is stored with a checksum, verified on every read. If a checksum fails, the system reads from another replica.

---

## Availability — 99.99% (four nines)

Because this is infrastructure that other services depend on, the availability bar is higher than a consumer-facing app. If the KV store goes down, every service that depends on it goes down too — cascading failure.

```
99.9%  = ~8.7 hours downtime/year   (too loose for infrastructure)
99.99% = ~52 minutes downtime/year  ← our target
99.999% = ~5 minutes downtime/year  (aspirational, extremely expensive)
```

Four nines gives 52 minutes of total downtime per year. With 1,200 nodes and replication factor 3, individual node failures don't count as downtime — the data is still available on other replicas. True downtime only happens if an entire quorum for some partition fails simultaneously.

---

## Summary

```
Durability:         Zero data loss after ack — WAL + replication before ack
CAP trade-off:      Tunable per request — client chooses AP or CP
Consistency:        Eventually consistent by default, strongly consistent on demand
                    Quorum: W=2, R=2 for strong; R=1 for eventual (N=3)
Latency (p99):      EC read < 10ms | SC read < 50ms | Write < 20ms
Fault tolerance:    200 nodes down → system still operational
Data integrity:     Checksums on every value, verified on every read
Availability:       99.99% — infrastructure-grade, higher bar than consumer apps
```

---

> [!tip] Interview framing
> "Durability is the top priority — WAL plus replication before ack, zero data loss. Consistency is tunable per request: eventually consistent reads hit any single replica for speed, strongly consistent reads use quorum (W+R>N) for correctness. Client decides per request, not a system-wide setting. Latency targets are single-digit ms for EC reads, under 50ms for SC reads — fast because LSM Trees buffer writes in memory and Bloom filters skip unnecessary disk reads. Fault tolerance: at 1,200 nodes, daily failures are expected — replication factor 3 means data survives. 99.99% availability because this is infrastructure — if we go down, everything goes down."
