# Back-of-Envelope Estimation

## Numbers Every Engineer Should Know

**Latency**
| Operation | Latency |
|---|---|
| RAM access | ~100 ns |
| SSD random read | ~150 µs |
| HDD seek | ~10 ms |
| Network within same datacenter | ~0.5 ms |
| Network cross-region (US-EU) | ~100–150 ms |

**Data sizes**
- 1 KB = 10³ bytes, 1 MB = 10⁶, 1 GB = 10⁹, 1 TB = 10¹²
- Tweet: ~300 bytes
- User profile: ~1 KB
- Photo (compressed): ~300 KB–1 MB
- Video (1 min, compressed): ~50 MB

**Traffic rules of thumb**
- 1M users × 1 request/day ≈ 12 req/sec
- Peak traffic = 3–5× average
- Seconds in a day: 86,400

## Estimation Framework (Use This Order Every Time)

**Step 1 — State assumptions out loud**
Interviewers want to see reasoning, not precise numbers. Assumptions are fine.

**Step 2 — DAU / traffic**
- How many daily active users?
- What does each user do per day?
- Daily requests / 86,400 = average QPS
- Multiply by 3–5 for peak QPS
- Separate read QPS from write QPS

**Step 3 — Storage**
- Size per record × number of records × replication factor × retention period
- Add media separately (photos, videos dwarf metadata)

**Step 4 — Bandwidth**
- Incoming = write QPS × average write size
- Outgoing = read QPS × average read size

**Step 5 — Memory (Cache sizing)**
- Apply 80/20 rule — 20% of data gets 80% of traffic
- Cache size ≈ 0.2 × daily read data volume

**Step 6 — Server count**
- Assume 1 server handles ~1,000–5,000 req/sec (depends on operation)
- Servers needed = peak QPS / QPS per server

## Read vs Write Ratio
- Why most systems are read-heavy (100:1 for social apps)
- How read/write ratio changes architecture — high reads → caching, replicas. High writes → sharding, queues.
- Always estimate reads and writes separately

## When Estimation Changes Your Architecture
- QPS > 10K → consider read replicas or caching
- QPS > 100K → consider sharding
- Storage > few TB → consider partitioning or archival tiers
- Write-heavy → consider write-optimized DB (Cassandra), async writes
- Read-heavy → caching, CDN, read replicas

## Worked Examples

**URL Shortener**
- 100M DAU, 1 create/day, 10 reads/day
- Write QPS: ~1,200/sec, Read QPS: ~12,000/sec, Peak read: ~50K/sec
- Storage: 100M × 365 × 100 bytes ≈ 3.6 TB/year
- Needs caching (hot URLs), sharding after year 2

**Photo Sharing App**
- 50M DAU, 2 photos uploaded/day, 20 photos viewed/day
- Write QPS: ~1,200/sec, Read QPS: ~12,000/sec
- Storage: 50M × 2 × 500KB × 365 ≈ 18 TB/year for photos alone
- CDN is mandatory, media dwarfs metadata

**How to present in an interview**
- Round everything up, show your math
- Call out the dominant bottleneck (storage? throughput? reads?)
- Connect the number to an architecture decision ("50K QPS means we need caching")
