# Back-of-Envelope Estimation

## Numbers to Memorize

**Latency (Jeff Dean's numbers)**
| Operation | Latency |
|---|---|
| L1 cache hit | ~0.5 ns |
| L2 cache hit | ~7 ns |
| RAM access | ~100 ns |
| SSD random read | ~150 µs |
| HDD seek | ~10 ms |
| Network within same datacenter | ~0.5 ms |
| Network cross-region (US-EU) | ~100–150 ms |

**Data sizes**
- Tweet: ~280 bytes text
- User profile: ~1 KB
- Photo (compressed): ~300 KB–1 MB
- Video (1 min, compressed): ~50 MB
- Server RAM: 64–256 GB

**Traffic rules of thumb**
- 1M users × 1 request/day = ~12 req/sec
- Peak traffic = 3–5× average
- Read:write ratio for social apps = ~100:1
- Seconds in a day: 86,400

## Estimation Framework

**Step 1 — State assumptions out loud**
Interviewers want to see reasoning, not precise numbers.

**Step 2 — DAU/MAU**
- How many daily active users?
- What does each user do per day?

**Step 3 — QPS**
- Daily requests / 86,400 = average QPS
- Multiply by 3–5 for peak QPS
- Separate read QPS from write QPS

**Step 4 — Storage**
- Size per record × number of records × replication factor × retention period
- Add media separately — photos and videos dwarf metadata

**Step 5 — Bandwidth**
- Incoming = write QPS × average write size
- Outgoing = read QPS × average read size × fan-out factor

**Step 6 — Memory (cache sizing)**
- Apply 80/20 rule — 20% of data gets 80% of traffic
- Cache size = 0.2 × daily read data

**Step 7 — Server count**
- Assume 1 server handles ~1,000–5,000 req/sec
- Servers needed = peak QPS / QPS per server

## When Estimation Changes Your Architecture
- QPS > 10K → read replicas or caching
- QPS > 100K → sharding
- Storage > few TB → partitioning, archival tiers
- Write-heavy → LSM-based DB (Cassandra), async writes
- Read-heavy → caching, CDN, read replicas
- Media dominates → CDN is mandatory

## Practice Estimations

**URL Shortener**
- 100M DAU, 1 create/day, 10 reads/day
- Write QPS ~1,200/sec, Read QPS ~12,000/sec, Peak read ~50K/sec
- Storage: 100M × 365 × 100 bytes ≈ 3.6 TB/year
- → Needs caching (hot URLs), sharding after year 2

**Chat System (WhatsApp)**
- 500M DAU, 40 messages/day per user
- Write QPS ~230K/sec, Peak ~700K/sec
- Message: ~200 bytes → 4 TB/day text. Media: 5% × 300KB → 300 TB/day
- → Write-heavy, needs sharding. Media dominates storage.

**Video Streaming (YouTube)**
- 1B DAU, 5 videos watched/day avg 5 min each
- Read bandwidth: 1B × 5 × 50MB = 250 PB/day → CDN is mandatory
- Upload: 500K videos/day, 100MB raw → 750 TB/day transcoded
- → Transcoding pipeline is the bottleneck, not serving

**News Feed (Twitter)**
- 300M DAU, 2 posts/day, 50 feed reads/day
- Write QPS ~7K/sec, Read QPS ~175K/sec → 25:1 ratio
- Fan-out: 200 followers × 7K writes/sec = 1.4M feed inserts/sec
- → Fan-out on write for most users, pull for celebrities

**Notification System**
- 200M DAU, 10 notifications/day per user
- 2B notifications/day → ~23K/sec, Peak ~100K/sec
- 60% push, 30% email, 10% SMS
- → Kafka fan-out per channel, rate limit per user

**Ride-Sharing (Uber)**
- 20M DAU riders, 2M active drivers
- Driver location: 2M × 1 update/4 sec = 500K writes/sec
- → Location updates dominate. Redis geospatial or geohash index required.
