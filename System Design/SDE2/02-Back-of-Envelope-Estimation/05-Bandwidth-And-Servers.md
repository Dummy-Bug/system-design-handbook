
> [!info] Bandwidth and server count tell you whether your hardware can physically handle the load
> Before you add a CDN or split into microservices, you need to know if the raw numbers fit on the machines you have.

---

## Network bandwidth

```
1 Gbps  = 125 MB/s   (typical commodity server NIC)
10 Gbps = 1.25 GB/s  (high-end server, common in modern DCs)
25 Gbps = 3.1 GB/s   (high-performance nodes)
100 Gbps = 12.5 GB/s (backbone, specialized hardware)

Mobile connection: 10–100 Mbps (LTE/5G)
Home broadband:    50–500 Mbps
```

**Bandwidth formula:**
```
Incoming bandwidth = write QPS × average write payload size
Outgoing bandwidth = read QPS × average response size

Convert bytes/sec → bits/sec: multiply by 8
  1 MB/s  = 8 Mbps
  1 GB/s  = 8 Gbps
```

**Example — URL shortener:**
```
Outgoing (redirect responses):
1M reads/sec × 200 bytes = 200 MB/s × 8 = 1,600 Mbps = 1.6 Gbps
→ fits on a single 10Gbps NIC with headroom ✓

Incoming (creation requests):
1k writes/sec × 500 bytes = 500 KB/s × 8 = 4 Mbps
→ negligible
```

**Example — Pastebin:**
```
Outgoing (paste reads):
3,000 reads/sec × 10 KB = 30 MB/s × 8 = 240 Mbps
→ well under 10Gbps NIC ✓

Incoming (paste writes):
30 writes/sec × 10 KB = 300 KB/s × 8 = 2.4 Mbps
→ negligible
```

**Example — video streaming:**
```
Outgoing:
1M concurrent viewers × 2 Mbps (720p) = 2 Tbps
→ no single server handles this → CDN is mandatory
```

The moment your outgoing bandwidth exceeds ~10 Gbps per server, you need either more servers or a CDN.

---

## CDN — when it becomes mandatory

CDN is not optional when:
- Static content (images, videos, JS, CSS) is served at scale — the bandwidth is too high for origin servers
- Users are globally distributed — cross-region latency (100–150ms) makes serving from one DC unacceptable
- Read QPS for static assets exceeds what your origin can handle

```
YouTube:   CDN mandatory (petabytes/day of video egress)
Twitter:   CDN for media (images, videos in tweets)
URL shortener: CDN not needed (no media, redirect responses are tiny)
```

---

## App server capacity

```
Simple CRUD app server (read a record, return JSON): 1,000 – 5,000 req/sec
Moderate complexity (cache lookup + DB query):       500 – 1,000 req/sec
CPU-intensive (image processing, crypto):            50 – 200 req/sec

Memory per server:   4 GB – 64 GB (typical)
CPU cores:           8 – 64 cores (typical)
```

**Server count formula:**
```
Servers needed = peak QPS / QPS per server

URL shortener redirect at peak:
1,000,000 / 50,000 per server = 20 servers

(50k/server for a simple Redis lookup + 301 — fast operation, can handle more)
```

**Why you add N+1 headroom:**
If you need 20 servers at peak, run 22–25. Losing one server during peak should not push remaining servers past capacity. N+1 means: lose any single server, remaining fleet still handles full load.

---

## Connection server capacity — persistent connections are different

Regular app servers handle **request-response** — a client connects, sends a request, gets a response, disconnects. The connection lives for milliseconds.

Chat systems, WebSocket servers, and any real-time system are different. Connections are **persistent** — a user connects and stays connected for hours, waiting for messages. The server holds that connection open the entire time.

**The classic model — one thread per connection — collapses fast:**

```
1 thread stack           → ~1 MB RAM
10M concurrent users     → 10M threads × 1 MB = 10 TB RAM
```

No machine has 10 TB of RAM. This is why the naive "one thread per connection" model fails for real-time systems.

**The fix — async I/O (epoll on Linux):**

Instead of one thread per connection, one thread watches thousands of connections simultaneously. The OS monitors all open connections via epoll and only wakes the thread when a connection actually has data to process. Between events, the thread is free to handle other connections.

```
Async I/O capacity per server  → ~50k–100k concurrent connections
100M DAU, 10% online at once   → 10M concurrent connections
Servers needed                 → 10M / 100k = ~100 connection servers
```

This is why chat systems always have a dedicated **connection service** — a horizontally scalable fleet of servers whose only job is to hold open WebSocket connections. The rest of the system (message routing, storage, delivery) is separate.

```
Stateless app server:        1k–5k req/sec
Connection server (async):   50k–100k concurrent persistent connections
```

> [!important] Persistent connections change your server count math
> For a request-response API, you size servers by QPS. For a real-time system, you size connection servers by **concurrent users online**, not by message throughput. These are very different numbers. 10M users online simultaneously requires ~100 connection servers regardless of whether they're sending 1 message/hour or 100 messages/hour.

---

## Cache sizing — the 80/20 rule

Not all data needs to be in cache — only the hot fraction that gets the most traffic.

**The rule:**
```
~20% of content receives ~80% of traffic
Cache that 20% → serve 80% of reads from cache
```

**Cache size formula:**
```
Cache size = 20% × (daily read data volume)
           = 20% × (daily read QPS × avg record size × seconds per day)
```

**URL shortener cache sizing:**
```
Daily reads: 100M/day
Record size: 500 bytes per URL
Total daily read data: 100M × 500 bytes = 50 GB

Cache 20%: 50 GB × 0.20 = 10 GB

But active window is 3 days (80% of traffic is from recent URLs):
3-day active data: 3M URLs × 500 bytes = 1.5 GB

With 20% viral factor and safety buffer → 27 GB Redis cluster
```

**Cache hit rate target:**
```
Good:      80–90% hit rate
Very good: 90–95% hit rate
Excellent: 95%+ hit rate (only for extremely hot, stable data)

Below 80% → cache is not helping enough → either wrong eviction policy
             or cache is too small → increase size
```

**Redis memory budget per entry (with overhead):**
```
Small entry (6-byte key + 200-byte value): ~500 bytes total with Redis internals
Large entry (key + 1KB value):             ~1.2 KB total
Always add ~50–100 bytes overhead per key for Redis metadata
```

---

## Time constants — critical for QPS math

```
Seconds in a minute:  60
Seconds in an hour:   3,600
Seconds in a day:     86,400  → round to 100,000 for easy mental math
Seconds in a month:   ~2,500,000  (~2.5M)
Seconds in a year:    ~31,500,000 (~31.5M)
```

**The 100k trick:**
Instead of dividing by 86,400, divide by 100,000. You get a number 15% lower than reality but the math is instant:

```
100M requests/day ÷ 100,000 = 1,000 req/sec  (actual: 1,157 req/sec)
For estimation, 1,000 is close enough
```

**DAU → QPS formula:**
```
Avg QPS = DAU × actions_per_day / 86,400

100M DAU × 10 reads/day  = 1B reads/day  ÷ 86,400 = ~11,574 req/sec ≈ 12k/sec
100M DAU × 0.1 writes/day = 10M writes/day ÷ 86,400 = ~115 writes/sec ≈ 100/sec
```

**Peak multiplier:**
```
Peak = 3–5× average for most systems
Peak = 10× average for viral/event-driven systems (product launches, breaking news)
```

---

## When estimation forces architecture decisions

```
Read QPS > 1k     → load balancing (multiple app servers)
Read QPS > 10k    → caching (Redis) — single DB can't sustain this
Read QPS > 100k   → DB sharding — even with caching, DB sees too many misses
Read QPS > 1M     → local in-process cache on app servers (hot key problem)

Write QPS > 1k    → write batching or async queue
Write QPS > 10k   → shard primaries
Write QPS > 100k  → LSM-based DB (Cassandra), async write buffer

Storage > 1 TB    → think about archival
Storage > 10 TB   → sharding is unavoidable
Storage > 100 TB  → tiered storage (hot SSD + cold S3)

Latency SLO < 10ms  → local cache mandatory, Redis alone not enough
Latency SLO < 1ms   → in-process cache only, no network hops

Media in the system  → CDN mandatory
Users globally distributed → CDN mandatory, regional replicas for DB reads
```

---

> [!tip] Interview framing
> "A 10Gbps NIC gives you 1.25 GB/s of bandwidth. App server handles 1k–5k req/sec for typical CRUD. Cache sizing: 80/20 rule — cache 20% of hot data to serve 80% of reads. Seconds in a day is 86,400 — round to 100k for mental math. Peak = 3–5x average, 10x for viral. QPS > 10k → add caching. QPS > 100k → shard."
