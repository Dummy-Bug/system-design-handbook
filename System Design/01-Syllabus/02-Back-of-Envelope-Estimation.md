## Phase 2 — Back of Envelope Estimation

> HLD relevance: Every Google interview starts with estimation.
> It drives your architecture — do you need sharding? caching? CDN?

### 8.1 Numbers to Memorize

**Latency (Jeff Dean's numbers)**
| Operation | Latency |
|---|---|
| L1 cache hit | ~0.5 ns |
| L2 cache hit | ~7 ns |
| RAM access | ~100 ns |
| SSD random read | ~150 µs |
| HDD seek | ~10 ms |
| Network within same datacenter | ~0.5 ms |
| Network cross-region (US-EU) | ~100-150 ms |

**Data sizes**
- 1 KB = 10^3 bytes, 1 MB = 10^6, 1 GB = 10^9, 1 TB = 10^12
- Tweet: ~280 bytes text
- User profile: ~1 KB
- Photo (compressed): ~300 KB–1 MB
- Video (1 min, compressed): ~50 MB
- Server RAM: 64–256 GB

**Traffic rules of thumb**
- 1M users × 1 request/day = ~12 req/sec
- Peak traffic = 3–5x average
- Read:write ratio for social apps = ~100:1

### 8.2 Estimation Framework (Use This Order Every Time)

**Step 0 — State assumptions out loud**
Interviewers want to see your reasoning, not a precise number.

**Step 1 — DAU/MAU**
- How many daily active users?
- What does each user do per day (posts, reads, searches)?

**Step 2 — QPS**
- Daily requests / 86,400 = average QPS
- Multiply by 3–5 for peak QPS
- Separate read QPS from write QPS

**Step 3 — Storage**
- Size per record × number of records × replication factor × retention period
- Add media separately (photos, videos are orders of magnitude larger than metadata)

**Step 4 — Bandwidth**
- Incoming = write QPS × average write size
- Outgoing = read QPS × average read size × fan-out factor

**Step 5 — Memory (Cache sizing)**
- Apply 80/20 rule — 20% of data gets 80% of traffic
- Cache size = 0.2 × daily read data

**Step 6 — Server count**
- Assume 1 server handles ~1000–5000 req/sec (depends on operation complexity)
- Total servers = peak QPS / QPS per server

### 8.4 When Estimation Changes Your Architecture
- QPS > 10K → consider read replicas or caching
- QPS > 100K → consider sharding
- Storage > few TB → consider partitioning, archival tiers
- Write-heavy → consider LSM-based DB (Cassandra), async writes
- Read-heavy → consider caching, CDN, read replicas
