
> [!info] Estimation without a framework produces random numbers. Estimation with a framework produces justified architecture decisions.
> The goal is never "get the exact number." The goal is: use the number to justify your next design choice.

---

## The 6-step framework — use this order every time

### Step 0 — State assumptions out loud

Before any calculation, say what you're assuming. Interviewers want to see your reasoning, not a precise number. If your assumption is wrong, they'll correct you. If it's reasonable, they'll nod and you continue.

```
"I'll assume 100M MAU, with about 10% DAU — so 10M daily active users."
"I'll assume each user creates 0.1 URLs per day on average."
"I'll assume a 10:1 read-to-write ratio, so 10 reads per URL created."
```

---

### Step 1 — Users (DAU/MAU)

Start with who uses the system.

```
MAU → MAU × 10% = DAU (typical engagement rate for consumer apps)
What does each user DO per day? (reads? writes? both?)

Common assumptions:
Social app:       10–50 actions/day per DAU
URL shortener:    0.1 creates + 10 redirects per DAU
Chat:             50–100 messages sent/day per DAU
Video streaming:  3–5 videos watched/day per DAU
```

---

### Step 2 — QPS (always separate reads from writes)

```
Avg write QPS = DAU × writes_per_day / 86,400
Avg read QPS  = DAU × reads_per_day  / 86,400
Peak QPS      = avg × 3–5  (or × 10 for viral systems)
```

**Always sanity-check your read:write ratio:**
```
URL shortener:      1000:1  (redirects massively outnumber creates)
Social media feed:  100:1   (many more reads than posts)
Chat:               1:1     (every message sent is also received)
Ride-sharing:       1:1     (driver sends location, user reads it)
```

---

### Step 3 — Storage

Always do this in two parts: **metadata** and **media**.

```
Metadata storage = records_per_day × bytes_per_record × days_retained
                 × replication_factor (3)
                 × index_overhead (1.3–1.5)

Media storage    = records_per_day × % with media × media_size
                 × transcoding_factor (for video: ×10)
                 × replication_factor (3)
```

**Storage at 10 years for common systems:**
```
URL shortener:    50B URLs × 500 bytes = 25 TB raw → ~250 TB with overhead
Twitter (text):   ~500 GB/year text  (negligible vs media)
Twitter (media):  ~16 PB/year photos
YouTube:          ~180 PB/year video uploads (transcoded)
```

---

### Step 4 — Bandwidth

```
Incoming = write QPS × avg write payload size
Outgoing = read QPS × avg response size

Check against server NIC: 10 Gbps = 1.25 GB/s
If outgoing > 10 Gbps per server → CDN or more servers
```

---

### Step 5 — Cache sizing

```
Cache size = 20% × (daily active data)
           = 20% × (daily read QPS × record size × 86,400)

OR simpler:
Active working set = URLs created in last 3 days × 20% viral factor
Cache size = active working set × record size
```

---

### Step 6 — Server count

```
App servers  = peak QPS / QPS per server (use 1k–5k for CRUD)
DB nodes     = (peak read QPS × cache miss rate) / reads_per_node (10k–50k for Postgres)
               + write QPS / writes_per_node (5k–10k)
Redis nodes  = cache size / memory per node (64–256 GB)
               (throughput almost never the constraint)
```

Always add 20–30% headroom (N+1 minimum).

---

## Full worked example — URL Shortener

```
Step 0 — Assumptions
  100M MAU, 10% DAU = 10M DAU
  Each DAU: 0.1 creates/day, 10 reads/day

Step 1 — Users
  10M DAU

Step 2 — QPS
  Writes: 10M × 0.1 / 86,400 = 1M/day / 86,400 ≈ 12/sec avg → ~1k/sec peak
  Reads:  10M × 10  / 86,400 = 100M/day / 86,400 ≈ 1,157/sec avg → ~1M/sec peak
  Read:write ratio = 1000:1

Step 3 — Storage (10 years)
  URLs: 1M/day × 365 × 10 = 3.65B → ~50B with safety margin
  Per URL: 500 bytes
  Raw: 50B × 500 bytes = 25 TB
  With replication (3×) + indexes (1.5×): 25 × 3 × 1.5 = ~112 TB → say 250 TB

Step 4 — Bandwidth
  Outgoing: 1M reads/sec × 200 bytes (301 header) = 200 MB/s → fits 10Gbps ✓
  Incoming: 1k writes/sec × 500 bytes = 500 KB/s → negligible

Step 5 — Cache
  Active window: 3 days (80% of traffic from recent URLs)
  Active URLs: 3M → 20% viral = 600k hot URLs
  Cache size: 600k × 500 bytes = 300 MB + buffer → ~27 GB Redis cluster

Step 6 — Servers
  Redirect app servers: 1M / 50k per server = 20 servers
  Creation app servers: 1k / 50k per server = 2 servers
  DB: 8 shards (250 TB / ~30 TB per machine)
  Redis: 27 GB → 1 node (64 GB) fine, use cluster for HA
```

---

## Architecture decision cheat sheet

| Metric | Threshold | Architecture implication |
|---|---|---|
| Read QPS | > 1k | Multiple app servers + load balancer |
| Read QPS | > 10k | Redis caching |
| Read QPS | > 100k | DB read replicas |
| Read QPS | > 1M | Local in-process cache on app servers |
| Write QPS | > 1k | Async queue (Kafka/SQS) |
| Write QPS | > 10k | Shard DB primaries |
| Write QPS | > 100k | LSM DB (Cassandra) |
| Storage | > 1 TB | Plan archival strategy |
| Storage | > 10 TB | Sharding required |
| Storage | > 100 TB | Tiered storage (SSD + S3) |
| Has media | any | CDN mandatory |
| Global users | any | Regional replicas, CDN |
| Latency SLO | < 50ms | Redis cache mandatory |
| Latency SLO | < 10ms | Local in-process cache |
| Latency SLO | < 1ms | In-process only, no network |

---

> [!tip] Interview framing
> "I'll start with users — 100M MAU, ~10M DAU. 10 reads per DAU = 100M reads/day ÷ 86,400 = ~1,200/sec avg, peak 10× = ~12k/sec. Storage: 1KB per record × 100M users = 100 GB/year. Cache: 80/20 rule, cache 20% = 20 GB. Read QPS > 10k so I'll add Redis. Storage growing past 10 TB by year 3 so I'll plan for sharding early."
