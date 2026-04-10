## Phase 2 - Back of Envelope Estimation

> HLD relevance: estimation is where architecture stops being generic.
> SDE-3 depth means you should identify the dominant cost driver, not just compute average QPS.

### SDE-3 depth bar for this phase
- Estimate the system in the order that changes architecture decisions.
- Identify what actually dominates: fan-out, bandwidth, cross-region latency, storage growth, hot-key skew, or queue lag.
- Split averages from peaks and explain p95 / p99 consequences.
- Use estimates to justify migration path, not just initial design.

### 2.1 Numbers to Memorize

**Latency**
| Operation | Rough latency |
|---|---|
| RAM access | ~100 ns |
| SSD random read | ~100-200 us |
| HDD seek | ~10 ms |
| same-datacenter network | ~0.5 ms |
| cross-region network | ~100-150 ms |

**Data sizes**
- short text message: ~200 bytes
- user profile: ~1 KB
- image: ~300 KB to 1 MB
- short compressed video: tens of MB

**Traffic rules of thumb**
- peak traffic is usually 3x to 5x average
- social systems are often read-heavy but celebrity-skewed
- media dominates storage and bandwidth, not metadata
- global traffic is usually uneven across regions and time zones

### 2.2 Estimation Framework (Use This Order Every Time)

**Step 1 - product workload**
- DAU / MAU
- actions per user per day
- read QPS vs write QPS
- sync path vs async path

**Step 2 - peak load**
- average QPS
- peak multiplier
- burstiness and traffic spikes
- regional split if global

**Step 3 - storage**
- record size
- retention
- replication factor
- hot / warm / cold storage split

**Step 4 - bandwidth**
- ingress bandwidth
- egress bandwidth
- fan-out amplification
- CDN offload percentage

**Step 5 - compute / memory**
- working-set size
- hot-key / hot-shard risk
- rough server and cache footprint
- consumer count for async systems

**Step 6 - latency budget**
- request budget by hop
- cache hit vs miss path
- p95 / p99 budget
- cross-service amplification

### 2.3 Senior-Level Estimation Concerns
- Fan-out amplification in feeds and notifications.
- Write amplification in indexes, replicas, and event-driven pipelines.
- Cross-region latency tax when strong consistency is required.
- Hot partitions caused by celebrity users, skewed tenants, or timestamp-based keys.
- Queue drain time under backlog conditions.
- Reconciliation / backfill cost for historical reprocessing.

### 2.4 Practice Estimations

**1. News Feed**
- post write QPS vs feed read QPS
- fan-out cost
- celebrity skew
- cache footprint of recent feeds

**2. Chat System**
- concurrent connections
- message QPS
- message history growth
- media path vs text path split

**3. Video Streaming**
- ingest bandwidth
- transcode expansion
- CDN egress vs origin egress
- storage tiering

**4. Payment System**
- write-heavy ledger storage
- external-gateway callback volume
- reconciliation batch size
- audit retention cost

**5. Ad Click Aggregation**
- raw click ingest rate
- stream processor throughput
- state-store size
- nightly exact recomputation size

**6. Distributed Task Queue**
- producer QPS
- worker throughput
- retry amplification
- worst-case queue backlog drain time

### 2.5 When Estimation Changes Architecture
- QPS > 10K: cache, read replicas, and async side effects become common.
- QPS > 100K: sharding, queue partitioning, and hotspot mitigation become design-level topics.
- Storage in TB / PB scale: storage tiering and lifecycle management matter.
- Fan-out-heavy systems: the write path may be harder than the read path.
- Global systems: regional placement and consistency cost may dominate more than raw compute.

### 2.6 What Strong SDE-3 Estimation Sounds Like
- "The dominant cost here is not request QPS, it is feed fan-out on write."
- "The metadata is cheap; CDN egress and transcode storage dominate the bill."
- "Average traffic is irrelevant here. The peak plus skew drives the shard design."
- "If I choose cross-region quorum, I am paying the speed-of-light tax on every write."
