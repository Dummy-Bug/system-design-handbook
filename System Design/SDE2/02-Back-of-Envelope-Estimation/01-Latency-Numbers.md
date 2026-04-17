
> [!info] Every architecture decision has a latency justification behind it
> These are Jeff Dean's numbers — the standard reference every interviewer expects you to know. Memorise the order of magnitude, not the exact value.


## The numbers

| Operation | Latency | In human terms |
|---|---|---|
| L1 cache hit | 0.5 ns | fastest thing a CPU can do |
| L2 cache hit | 7 ns | 14× slower than L1 |
| RAM access | 100 ns | 200× slower than L1 |
| Read 1MB from RAM | 250 µs | sequential, fast |
| SSD random read (4KB) | 150 µs | 1,500× slower than RAM access |
| Read 1MB from SSD | 1 ms | sequential SSD read |
| HDD disk seek | 10 ms | moving mechanical parts |
| Read 1MB from HDD | 30 ms | sequential HDD read |
| Network — same datacenter | 0.5 ms | fast, synchronous calls are fine |
| Network — cross-region (US–EU) | 100–150 ms | too slow for synchronous critical path |

---

## What these numbers actually mean for design

**RAM is 1,000× faster than SSD.**
This is why you cache hot data in memory. A Redis lookup (RAM) at 0.1ms vs a Postgres disk read (SSD) at 5ms — that's a 50× difference in the real world. At 1M reads/sec, the difference between serving from cache vs going to disk is the difference between a system that works and one that falls over.

**SSD is 100× faster than HDD.**
This is why databases run on SSDs, not spinning disks. HDD is only viable for cold storage (S3, archival) where you accept high latency in exchange for cheap cost.

**Same-datacenter network is 0.5ms.**
Synchronous service-to-service calls within the same region are fine. An app server calling Redis, calling a DB shard, calling an auth service — all within the same DC, all sub-millisecond.

**Cross-region is 100–150ms.**
A synchronous call from US to EU on the critical path adds 100ms of unavoidable physics latency. This is why read replicas exist in each region — you cannot serve users globally from a single datacenter without cross-region latency killing your p99.

---

## The key ratios to remember

```
RAM vs SSD:        ~1,000× faster
SSD vs HDD:        ~100× faster
Same DC vs cross-region: ~300× faster (0.5ms vs 150ms)
```

If an interviewer asks "why cache in Redis instead of reading from DB every time?" — the answer is 1,000×. That's the ratio. That's the justification.

---

## Derived latency estimates for common operations

These are not memorised — they are derived from the fundamentals above:

```
Redis read (cache hit):          0.1 – 0.5 ms   (RAM access + network within DC)

Redis write:                     0.1 – 0.5 ms
Postgres read (indexed, hot):    1   – 5 ms     (SSD + query execution)

Postgres write (INSERT):         5   – 10 ms    (SSD write + WAL flush)

Cassandra write:                 0.5 – 2 ms     (memtable, no disk on hot path)

Cassandra read:                  5   – 10 ms    (may check multiple SSTables)

MongoDB read (indexed):          1   – 5 ms

S3 GET (object storage):         50  – 200 ms   (network + S3 internals)

Kafka produce (ack=1):           5   – 15 ms    (broker write + network)

Kafka end-to-end (produce→consume): 10 – 50 ms
```

---

> [!tip] Interview framing
> "Redis is sub-millisecond — 0.1 to 0.5ms. Postgres indexed read is 1–5ms. SSD is 1,000× faster than HDD, RAM is 1,000× faster than SSD. Cross-region adds 100–150ms of unavoidable physics — that's why you need regional replicas for global systems."
