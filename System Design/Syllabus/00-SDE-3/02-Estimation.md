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

## Google-Scale Additional Numbers

At 1B+ DAU the numbers change architecture decisions that are invisible at 100M scale.

**Cross-region replication bandwidth**
- Formula: write QPS × average write size × number of regions
- Example (WhatsApp at Google scale): 2M writes/sec × 200 bytes × 3 regions = 1.2 GB/s sustained replication traffic
- At this volume, async replication is the only viable option — sync replication across US-EU (150ms RTT) caps write throughput
- Private backbone bandwidth between Google/AWS/Azure regions: ~400–800 Gbps. Cross-region replication at 1.2 GB/s = ~10 Gbps. Feasible but must be budgeted.

**Storage tier cost awareness**
- S3 Standard: ~$23/TB/month
- S3 Infrequent Access: ~$12.5/TB/month
- S3 Glacier: ~$4/TB/month
- Rule: data not accessed in 30+ days → move to IA. 90+ days → Glacier.
- Example: YouTube at 1 exabyte (1M TB) total storage. If 90% is cold: 900K TB × $4 = $3.6M/month saved vs keeping it all in Standard.

**CDN egress cost**
- AWS CloudFront: ~$85/TB for first 10 TB/month, drops to ~$20/TB at petabyte scale
- YouTube serves 250 PB/day. At $20/TB = $250,000/day in CDN egress alone.
- This is why Google/Netflix/Meta build their own CDN and peer directly with ISPs — saves 80%+ vs commercial CDN.

**At Google scale, always estimate:**
- Cross-region replication bandwidth (not just storage)
- Storage lifecycle cost across tiers (not just total storage)
- CDN egress cost (not just bandwidth volume)

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

## Google-Scale Practice Estimations

**Google Search (1B+ DAU)**
- 1B DAU, 10 queries/day per user → 10B queries/day → ~115K QPS average, peak ~400K QPS
- Result page: ~50 KB (HTML + metadata) → outgoing bandwidth: 400K × 50 KB = 20 GB/s at peak → CDN mandatory
- Index size: web has ~45B indexed pages × ~10 KB per doc = 450 PB of raw index data
- Sharded across ~1M servers. Each shard serves ~45K pages.
- Cross-region replication of index updates: ~1M page updates/day × 10 KB × 3 regions = 30 GB/day of replication — trivial compared to serving
- → The bottleneck is index read latency, not write throughput. Every query touches hundreds of shards in parallel (scatter-gather), so P99 tail latency amplifies severely.

**Google Maps (1B+ DAU)**
- 1B DAU, 5 map tile requests per session, 3 sessions/day → 15B tile requests/day → ~175K tile QPS average
- Map tile: ~200 KB → outgoing: 175K × 200 KB = 35 GB/s at peak → edge CDN is the entire serving strategy
- Real-time traffic updates: 500M location probes/day from Android devices → ~6K writes/sec globally
- Cross-region: traffic model updated every 2 min, pushed to all 10 regions: model diff ~50 MB per update × 10 regions = 500 MB per 2 min = ~4 MB/s replication
- Storage: full planet map tiles at all zoom levels ≈ 10–100 PB. Zoom levels 0–14 fit in ~1 PB. Zoom 15–20 (street level) = the rest.
- → CDN hit ratio is everything. Cache miss on a tile = origin fetch = 50–150ms latency visible to user. Target >99% CDN hit rate for zoom ≤ 14.

**How Google-scale changes architecture decisions**
- At 100M users: one database cluster with read replicas is sufficient
- At 1B users: cross-shard fan-out latency becomes a P99 problem, sharding strategy determines query shape
- At 100M users: CDN is an optimization
- At 1B users: CDN is the primary serving infrastructure, origin is the fallback
- At 100M users: async cross-region replication lag of 1–2s is acceptable
- At 1B users: 1–2s lag means millions of users see stale data simultaneously — may need region-specific consistency policies
