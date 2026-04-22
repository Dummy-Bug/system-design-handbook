# PACELC — Real System Examples

## PA/EL Systems — Available and Fast

> [!info] These systems prioritize staying up during failures and minimizing latency during normal operation. Consistency is eventual.

### DynamoDB

```
Partition: keeps serving → returns data it has (may be stale)       PA
Normal:    responds immediately → doesn't wait for all replicas     EL
```

**Why:** Amazon built DynamoDB for shopping carts. A slightly stale cart (your spouse added an item you don't see for 50ms) is infinitely better than the cart failing entirely. Availability = revenue.

**Use for:** Shopping carts, sessions, user preferences, leaderboards, any data where brief staleness is acceptable.

---

### Cassandra

```
Partition: keeps serving → nodes serve what they have              PA
Normal:    responds fast → replication happens in background       EL
```

**Default behavior:** Write to one node, return success, replicate asynchronously. Another node might serve slightly stale data for a few milliseconds.

**Tunable:** Cassandra lets you override per-operation:
```
Consistency ONE    → PA/EL behavior (fastest, most available)
Consistency QUORUM → balanced
Consistency ALL    → PC/EC behavior (consistent, may be unavailable)
```

**Use for:** Social data, time-series, activity feeds, messaging at scale, anything needing massive write throughput.

---

### CouchDB

```
Partition: keeps serving on both sides of the partition            PA
Normal:    responds fast → syncs later                            EL
```

**Special feature:** Built for offline-first. Both sides of a partition can accept writes. When the partition heals, it merges using conflict resolution. 

**Use for:** Mobile apps that work offline, distributed document stores.

---

## PC/EC Systems — Consistent Always

> [!info] These systems prioritize correctness over everything. They refuse requests when they can't guarantee freshness, and accept higher latency normally.

### Zookeeper

```
Partition: stops serving → waits for quorum                       PC
Normal:    waits for majority to agree before responding          EC
```

**Why:** Zookeeper is used for leader election and distributed locks. If Zookeeper serves stale data during a partition:
```
Stale lock info → two processes enter critical section → race condition → data corruption
Stale leader    → two nodes think they're leader → split-brain → catastrophe
```

Being unavailable is infinitely better than returning wrong coordination data.

**Use for:** Leader election, distributed locks, config management, service discovery.

---

### Google Spanner

```
Partition: stops serving → waits for quorum across data centers   PC
Normal:    uses atomic clocks for real-time ordering              EC
```

**Why:** Spanner handles global financial data. It provides **linearizability** — the strictest consistency model. Uses atomic clocks + GPS receivers in every data center to ensure real wall-clock ordering.

**Use for:** Global financial systems, any data where correctness is non-negotiable at planetary scale.

---

### HBase

```
Partition: stops serving → consistency enforced via HDFS          PC
Normal:    quorum reads/writes before confirming                  EC
```

**Use for:** Strong consistency reads at scale, data warehousing on top of Hadoop.

---

## PA/EC Systems — The Middle Ground

> [!info] Consistent during normal operation. Available (but potentially stale) during partitions.

### MongoDB (default config)

```
Partition: primary unreachable → secondaries serve reads          PA
Normal:    reads from primary → strongly consistent               EC
```

**The nuance:**
```
writeConcern: majority → write confirmed by majority of replicas  (EC)
readPreference: primary → always read from primary               (EC)
readPreference: secondary → may read stale data                  (EL, overrides)
```

MongoDB's behavior depends heavily on configuration. Default is EC during normal operation, PA during partition.

**The honest take:** MongoDB's flexibility makes it a general-purpose DB but a poor choice when you need a clear guarantee. Financial data → use Postgres. Massive write throughput → use Cassandra. "Everything" → use MongoDB carefully.

---

## Quick Reference Table

| System | Label | Partition behavior | Normal behavior |
|---|---|---|---|
| DynamoDB | PA/EL | serves stale | responds immediately |
| Cassandra | PA/EL | serves stale | responds immediately |
| CouchDB | PA/EL | both sides accept writes | syncs asynchronously |
| Zookeeper | PC/EC | refuses requests | waits for quorum |
| Google Spanner | PC/EC | refuses requests | atomic clock ordering |
| HBase | PC/EC | refuses requests | quorum required |
| MongoDB | PA/EC | secondaries serve reads | reads from primary |

---

> [!tip] Interview pattern
> When asked "which DB would you use?" — don't just name a DB. Say its PACELC label and why that label matches the problem.
>
> "This is a social feed — brief staleness is fine, availability is critical. PA/EL. I'd use Cassandra."
> "This is payment processing — wrong balance is catastrophic. PC/EC. I'd use Postgres or Spanner."
