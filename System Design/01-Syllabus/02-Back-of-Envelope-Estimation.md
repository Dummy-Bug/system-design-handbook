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

### 8.3 Practice Problems (Work Through Each)

**URL Shortener**
- 100M new URLs/day → write QPS = 100M / 86400 ≈ 1200/s, peak ~6000/s
- 10:1 read:write → read QPS ~12000/s, peak ~60000/s
- URL record ~500 bytes × 100M/day × 365 days × 5 years = ~90 TB
- Cache 20% of daily reads → ~50 GB cache

**Twitter / News Feed**
- 300M DAU, each reads 20 tweets/day = 6B read ops/day = ~70K read QPS
- 100M tweets/day = ~1200 write QPS
- Tweet ~280 bytes × 100M = 28 GB text/day
- With media attachments: ~100 TB/day

**WhatsApp**
- 2B users, 50B messages/day
- Message ~100 bytes → 5 TB/day text, media 10x more
- 50B / 86400 ≈ 580K messages/sec

**YouTube**
- 500 hours of video uploaded every minute
- 1 min video ≈ 50 MB → 500 × 50 MB = 25 GB/min = ~400 MB/s ingestion
- Transcode to 5 formats × 3 resolutions = 15x storage multiplier

**Uber**
- 14M daily rides, 1M concurrent drivers
- Each driver updates location every 4 seconds = 250K location updates/sec
- Location record ~100 bytes → 25 MB/s write bandwidth

**Rate Limiter**
- 10K users, each allowed 100 req/sec = 1M counters
- Each counter ~100 bytes in Redis = ~100 MB — easily fits in single Redis node

### 8.4 When Estimation Changes Your Architecture
- QPS > 10K → consider read replicas or caching
- QPS > 100K → consider sharding
- Storage > few TB → consider partitioning, archival tiers
- Write-heavy → consider LSM-based DB (Cassandra), async writes
- Read-heavy → consider caching, CDN, read replicas
