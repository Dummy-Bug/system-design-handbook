## Phase 2 - Back of Envelope Estimation

> HLD relevance: SDE-3 interviews expect more than rough QPS.
> You should be able to estimate what actually dominates the design: fan-out, bandwidth, hot partitions, cross-region cost, or tail latency.

### 2.1 Numbers to memorize

**Latency**
| Operation | Rough latency |
|---|---|
| RAM access | ~100 ns |
| SSD random read | ~100-200 us |
| HDD seek | ~10 ms |
| same-datacenter network | ~0.5 ms |
| cross-region network | ~100-150 ms |

**Traffic and size intuition**
- peak is usually 3x to 5x average
- media dominates metadata
- global systems often have uneven regional distribution
- hot users and hot keys dominate real-world skew

### 2.2 Estimation framework

**Step 1 - workload**
- DAU / MAU
- actions per user per day
- read QPS vs write QPS
- peak multiplier

**Step 2 - storage**
- record size
- retention period
- replication factor
- hot vs warm vs cold storage tiers

**Step 3 - bandwidth**
- ingress
- egress
- fan-out amplification
- CDN offload percentage

**Step 4 - compute and cache**
- working set size
- hot-key distribution
- rough server count
- queue consumer count

**Step 5 - latency budget**
- edge / gateway budget
- application budget
- cache / DB / downstream budget
- p95 / p99 budget split across hops

### 2.3 Senior-level estimation concerns
- write amplification
- read amplification
- celebrity amplification in social systems
- shard hotspot risk
- per-region traffic split
- replication lag exposure
- RPO / RTO implications

### 2.4 Practice estimations

**1. News Feed**
- feed fan-out cost
- celebrity skew
- cache footprint

**2. Chat System**
- text vs media storage
- concurrent connections
- message write rate

**3. Video Streaming**
- ingest bandwidth
- transcoding workload
- CDN egress

**4. Payment System**
- write QPS
- ledger growth
- reconciliation workload

**5. Ad Click Aggregation**
- raw event volume
- stream processing throughput
- batch recomputation size

### 2.5 What strong SDE-3 estimation sounds like
- "The dominant cost here is not request QPS, it is fan-out amplification."
- "The DB is not the first bottleneck; cross-region latency is."
- "This workload is write-light but read-extremely-skewed, so hotspot mitigation matters more than raw storage."

