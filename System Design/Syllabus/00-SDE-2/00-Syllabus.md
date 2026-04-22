# SDE-2 System Design Syllabus — FAANGM Strong Hire

> Assumes everything in SDE-1 is already known.
> Topics marked **Stretch** are not required to pass an SDE-2 interview but knowing them puts you at the top of the SDE-2 pool and signals early SDE-3 readiness.

## Phases

1. Networking Fundamentals
2. Back-of-Envelope Estimation
3. Core Concepts
4. Caching
5. Storage and Databases
6. Messaging and Event-Driven Systems
7. Distributed Systems
8. Infrastructure and Reliability
9. Supplementary Topics
10. Interview Framework
11. Case Studies

---

## Required vs Stretch

> **Required** — must know to pass an SDE-2 system design interview.
> **Stretch** — knowing it puts you at the top of the SDE-2 pool and signals early SDE-3 readiness.

### Networking

| Topic | Level |
|---|---|
| HTTP/2 multiplexing — what it fixes over HTTP/1.1 | Required |
| WebSocket vs SSE vs Long Polling — when to choose each | Required |
| CDN push vs pull — when to use each | Required |
| gRPC for internal services — why over REST | Required |
| Idempotency keys — essential for payment, booking, auction | Required |
| Async API pattern — 202 Accepted + job ID polling | Required |
| Webhooks — push-based callbacks, HMAC verification | Required |
| API Gateway — routing, auth, rate limiting, transformation | Required |
| HTTP/3 and QUIC | **Stretch → SDE-3** |
| WebRTC — STUN/TURN/ICE | **Stretch → SDE-3** |
| mTLS — mutual TLS for service-to-service auth | **Stretch → SDE-3** |

### Estimation

| Topic | Level |
|---|---|
| Full estimation framework — QPS, storage, bandwidth, cache, servers | Required |
| All 6 worked examples — URL shortener through Uber | Required |
| Connecting estimation numbers to architecture decisions | Required |

### Core Concepts

| Topic | Level |
|---|---|
| P99 tail latency and tail latency amplification | Required |
| SLIs, SLOs, SLAs, error budget | Required |
| CAP theorem — CP vs AP, C in CAP = linearizability | Required |
| Consistency models — eventual vs strong, read-your-own-writes | Required |
| Transaction isolation levels — READ COMMITTED → SERIALIZABLE | Required |
| MVCC — readers don't block writers | Required |
| Optimistic vs pessimistic locking — when to choose each | Required |
| Circuit breaker — closed/open/half-open | Required |
| Retry + exponential backoff + jitter | Required |
| RTO vs RPO — what they drive | Required |
| PACELC — latency vs consistency outside of partitions | Required |
| State machines — WHERE guard, optimistic locking in one clause | Required |
| NFR → Design Decision → Trade-off pattern | Required |
| Write skew — MVCC doesn't prevent it, needs SERIALIZABLE | **Stretch → SDE-3** |
| Predicate locking — lock a condition not a row | **Stretch → SDE-3** |
| Full consistency spectrum — linearizability through sequential through causal | **Stretch → SDE-3** |
| Redlock — multi-node Redis distributed lock | **Stretch → SDE-3** |

### Caching

| Topic | Level |
|---|---|
| All read/write strategies — cache-aside through refresh-ahead | Required |
| All eviction policies — LRU, LFU, TTL | Required |
| Distributed caching — consistent hashing, hot key, two-level caching | Required |
| All 4 cache problems — stampede, avalanche, penetration, cold start | Required |
| Redis deep dive — all data structures, patterns, persistence, Sentinel | Required |
| Redis Cluster — hash slots, gossip-based membership | **Stretch → SDE-3** |
| Cross-region cache invalidation strategies | **Stretch → SDE-3** |
| Cache warming on region failover | **Stretch → SDE-3** |

### Storage and Databases

| Topic | Level |
|---|---|
| SQL normalization and denormalization — when each | Required |
| B+ Tree — structure, range scans, write amplification (awareness) | Required |
| LSM Tree — write-optimized, MemTable → SSTable → compaction | Required |
| Composite index, covering index, leftmost prefix rule | Required |
| Replication — sync vs async, replication lag, failover, split-brain | Required |
| Read-your-own-writes violation and fix | Required |
| Sharding — hash vs range vs directory vs consistent hashing | Required |
| Hotspot problem and shard key selection | Required |
| MVCC — snapshot isolation internals | Required |
| Cassandra — partition key, clustering key, replication factor, consistency levels, query-first modeling | Required |
| Object storage — multipart upload, pre-signed URLs, content-addressable | Required |
| Cursor-based vs offset pagination — why cursor wins at scale | Required |
| OLTP vs OLAP — never run analytics on production DB | Required |
| Geospatial indexing — Geohash vs Quadtree | Required |
| 2PC vs Saga — when each, trade-offs | Required |
| Choosing the right DB — decision framework | Required |
| LSM compaction strategies — leveled vs tiered vs size-tiered | **Stretch → SDE-3** |
| B+ Tree write amplification — page splits, what they cost | **Stretch → SDE-3** |
| Cassandra write/read path internals — CommitLog, MemTable, SSTable, tombstones | **Stretch → SDE-3** |
| Bigtable — tablet server, compaction types, row key design | **Stretch → SDE-3** |
| Google Spanner + TrueTime — external consistency, commit wait | **Stretch → SDE-3** |
| CDC — log-based change capture with Debezium | **Stretch → SDE-3** |
| Data migration at scale — dual-write, shadow reads, backfill, cutover | **Stretch → SDE-3** |
| Schema migration on live tables — gh-ost, expand-and-contract | **Stretch → SDE-3** |
| S2 geometry — spherical cells, Hilbert curve | **Stretch → SDE-3** |

### Messaging and Event-Driven

| Topic | Level |
|---|---|
| Kafka deep dive — partitions, offsets, consumer groups, ISR, retention, compacted topics | Required |
| Delivery guarantees — at-most-once, at-least-once, effectively-once | Required |
| Outbox pattern — atomic DB write + event publish | Required |
| Fan-out vs competing consumers | Required |
| Kafka vs RabbitMQ vs SQS — when to choose each | Required |
| Event sourcing — immutable event log, replay, projections | **Stretch → SDE-3** |
| CQRS — separate write and read models | **Stretch → SDE-3** |
| Kafka exactly-once — idempotent producer + transactional API | **Stretch → SDE-3** |
| Backpressure — consumer lag monitoring, load shedding | **Stretch → SDE-3** |
| Stream processing — windowing, watermarks, Flink vs Kafka Streams | **Stretch → SDE-3** |
| Lambda vs Kappa architecture | **Stretch → SDE-3** |
| Schema evolution — Avro + Schema Registry, Protobuf field numbers | **Stretch → SDE-3** |

### Distributed Systems

| Topic | Level |
|---|---|
| Consistent hashing + virtual nodes | Required |
| Replication strategies — single-leader, multi-leader, leaderless | Required |
| Quorum — W+R>N with worked example (N=3, W=2, R=2) | Required |
| Hinted handoff — short-term, hint window | Required |
| Read repair — lazy/passive replica healing | Required |
| Idempotency key — client-side UUID, server-side dedup | Required |
| Distributed locking — Redis SET NX PX, ZooKeeper ephemeral nodes | Required |
| Failure detection — heartbeats, dead node detection | Required |
| PACELC per database — Cassandra PA/EL, Spanner PC/EC | Required |
| Raft — what it is, why it replaced Paxos | **Stretch → SDE-3** |
| ZooKeeper — ZAB protocol, ephemeral nodes, watches, leader election | **Stretch → SDE-3** |
| Paxos — phases, value inheritance, livelock | **Stretch → SDE-3** |
| Vector clocks — causality vs concurrency detection | **Stretch → SDE-3** |
| Lamport clocks — happens-before ordering | **Stretch → SDE-3** |
| CRDTs — G-counter, OT vs CRDT | **Stretch → SDE-3** |
| Gossip protocol — O(log n) convergence | **Stretch → SDE-3** |
| Merkle trees — anti-entropy, find diverged data in O(log n) | **Stretch → SDE-3** |

### Infrastructure and Reliability

| Topic | Level |
|---|---|
| All 5 rate limiting algorithms — Token Bucket through Sliding Window Counter | Required |
| Distributed rate limiting — Redis INCR + Lua script | Required |
| Bloom filter — false negatives impossible, false positives tunable | Required |
| HyperLogLog — approximate unique count, O(log log n) memory | Required |
| Count-Min Sketch — approximate frequency, always overestimates | Required |
| Snowflake ID — 64-bit, timestamp + machine + sequence | Required |
| Deployment strategies — rolling, blue-green, canary | Required |
| Multi-region — active-passive vs active-active, GeoDNS | Required |
| Service mesh + sidecar pattern — Istio, Envoy | **Stretch → SDE-3** |
| Multi-region conflict resolution — LWW vs CRDT vs application merge | **Stretch → SDE-3** |
| Data residency — GDPR enforcement at data layer | **Stretch → SDE-3** |
| Cost estimation — compute, storage, CDN egress with real numbers | **Stretch → SDE-3** |
| Capacity planning — leading indicators, autoscaling targets | **Stretch → SDE-3** |
| Adaptive bitrate streaming — HLS/DASH full architecture | **Stretch → SDE-3** |

### Observability

| Topic | Level |
|---|---|
| Logging — structured logs, log levels, correlation ID | Required |
| Metrics — counter, gauge, histogram; Prometheus + Grafana | Required |
| Key metrics — error rate, P99 latency, QPS, queue depth, cache hit ratio | Required |
| SLIs / SLOs / error budgets — the three terms cold | Required |
| Distributed tracing — trace ID, spans, OpenTelemetry | Required |
| Alerting — page on symptoms not causes | Required |
| Error budget burn rate — why raw thresholds fail | Required |
| Multi-window alerting — 5m and 1h windows, burn rate math | **Stretch → SDE-3** |
| Metrics at scale — cardinality explosion, downsampling, federation | **Stretch → SDE-3** |
| Head-based vs tail-based tracing sampling | **Stretch → SDE-3** |
| Chaos engineering — Chaos Monkey, game days, blast radius | **Stretch → SDE-3** |

---

## Case Studies

### Tier 1 — Required

| Case Study | Why Required |
|---|---|
| URL Shortener | ID generation, caching, sharding — three foundational concepts in one system |
| Rate Limiter | All 5 algorithms directly tested, distributed rate limiting with Redis |
| Unique ID Generator | Snowflake internals come up in every other case study |
| Pastebin | Blob storage, dedup, expiry — required for any media/content system |

### Tier 2 — Required

| Case Study | Why Required |
|---|---|
| Type-Ahead / Autocomplete | Trie vs Redis sorted set — very common at Google specifically |
| Notification System | Kafka fan-out, multi-channel, DLQ, idempotency — 6 concepts in one |
| Leaderboard | Redis sorted set operations directly tested |
| Top-K Heavy Hitters | Count-Min Sketch + min-heap — common standalone question |

### Tier 3 — Required

| Case Study | Why Required |
|---|---|
| Chat System (WhatsApp) | WebSocket, message ordering, fan-out, offline delivery |
| Live News Feed | THE defining SDE-2 question — fan-out on write vs read |
| Hotel / Ticket Reservation | MVCC, SERIALIZABLE, Saga, optimistic locking |
| Payment System | Idempotency, exactly-once, append-only ledger |
| Dropbox / Google Drive | Chunking, content-addressable, delta sync |
| Taxi Platform (Uber) | Geospatial indexing, real-time location, surge pricing |
| YouTube | Transcoding pipeline, CDN, HLS/DASH |

### Stretch → SDE-3

| Case Study | Why Stretch |
|---|---|
| Key-Value Store | Teaches consistent hashing + quorum but rarely asked standalone at SDE-2 |
| Parking Lot | Concurrency focused, low frequency at FAANGM L4 |
| Web Crawler | Good distributed BFS exercise, lower frequency than others |
| Distributed Task Queue | Good but rarely primary question at SDE-2 |
| Job Scheduling Platform | Leader election depth — more SDE-3 territory |
| Online Auction | Race conditions + WebSocket — good but lower frequency |
| Banking Ledger | CQRS + event sourcing — firmly SDE-3 |
| Ad Click Aggregation | Count-Min Sketch + windowing — SDE-3 stream processing |
| Stock Broker | Order matching engine — SDE-3 / fintech specific |
| Netflix | HLS/DASH internals — SDE-3 streaming depth |
| Search Autocomplete with Personalization | Cold start, privacy deletion — SDE-3 additions |
