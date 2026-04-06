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

### 8.3 Practice Estimations (Do All 6)
> Don't just read the framework — practice it. Do each of these on paper in under 3 minutes.

**1. URL Shortener**
- 100M DAU, each creates 1 short URL/day, reads 10/day
- Write QPS: ~1,200/sec, Read QPS: ~12,000/sec, Peak read: ~50K/sec
- Storage: 100M × 365 days × 100 bytes ≈ 3.6 TB/year
- → Needs caching (hot URLs), sharding after year 2

**2. Chat System (WhatsApp)**
- 500M DAU, 40 messages sent/day per user
- Write QPS: ~230K/sec, Peak: ~700K/sec
- Message size: ~200 bytes text → 500M × 40 × 200 = 4 TB/day
- Media: 5% of messages have 300KB image → 500M × 2 × 300KB = 300 TB/day
- → Write-heavy, needs sharding. Media dominates storage.

**3. Video Streaming (YouTube)**
- 1B DAU, 5 videos watched/day, avg 5 min each
- Read bandwidth: 1B × 5 × 50MB = 250 PB/day → CDN is mandatory
- Upload: 500K videos/day, avg 100MB raw → 50 TB/day raw, 750 TB/day transcoded (15 resolutions × formats)
- → Transcoding pipeline is the bottleneck, not serving

**4. News Feed (Twitter/Facebook)**
- 300M DAU, 2 posts/day, 50 feed reads/day
- Write QPS: ~7K/sec, Read QPS: ~175K/sec → 25:1 read:write ratio
- Fan-out: avg 200 followers × 7K writes/sec = 1.4M feed inserts/sec
- → Fan-out on write works for most users; pull for celebrities (>1M followers)

**5. Notification System**
- 200M DAU, 10 notifications/day per user
- Total: 2B notifications/day → ~23K/sec, Peak: ~100K/sec
- Multi-channel: 60% push, 30% email, 10% SMS
- → Kafka fan-out per channel, rate limit per user (max 5/hour)

**6. Ride-Sharing (Uber)**
- 20M DAU riders, 2M active drivers
- Driver location updates: 2M × 1 update/4 sec = 500K writes/sec to geo-index
- Ride requests: 10M rides/day → ~115/sec (not the bottleneck)
- → Location updates dominate; Redis geospatial or in-memory geohash index required

### 8.4 When Estimation Changes Your Architecture
- QPS > 10K → consider read replicas or caching
- QPS > 100K → consider sharding
- Storage > few TB → consider partitioning, archival tiers
- Write-heavy → consider LSM-based DB (Cassandra), async writes
- Read-heavy → consider caching, CDN, read replicas
