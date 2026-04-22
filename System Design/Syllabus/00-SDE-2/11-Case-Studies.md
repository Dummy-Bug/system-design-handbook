## Phase 11 — Case Studies

> This is the destination. Everything in Phases 1–10 feeds directly into these systems.
> Use the same structure every time — it builds muscle memory for interviews.

### SDE-2 Depth Bar For This Phase
- A baseline architecture is not enough — discuss tradeoffs, failure modes, and scaling path.
- SDE-2 means stronger data-model and async reasoning, more realistic failure handling, better scaling discussion.
- Explain why a design works, what breaks first, and what the next evolution step is.
- Tier 4 (Google-level) case studies with deep distributed systems internals are SDE-3.

### Structure for Every Case Study
1. Functional Requirements — what the system does (2-3 core features)
2. Non-Functional Requirements — scale, latency, availability, consistency
3. Capacity Estimation — QPS, storage, bandwidth
4. API Design — key endpoints, request/response, idempotency
5. High-Level Architecture — components and data flow diagram
6. Data Model — schema or document structure
7. Deep Dive — 2-3 most critical or interesting components
8. Bottlenecks & Scaling — what breaks at 10x, how to fix

---

### Tier 1 — Beginner (Do These First)

**1. URL Shortener**
Key concepts: ID generation (Snowflake vs Base62), hash collisions, 301 vs 302 redirect, caching hot URLs, DB sharding by short code

**2. Rate Limiter**
Key concepts: All 5 algorithms (Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Log, Sliding Window Counter), distributed rate limiting with Redis, multi-region synchronization

**3. Key-Value Store**
Key concepts: Consistent hashing with vnodes, replication (quorum R+W>N), conflict resolution (LWW), Bloom filter for read optimization

**4. Pastebin**
Key concepts: Content hash as ID (deduplication), blob storage for content, expiry via TTL, read caching

**5. Unique ID Generator**
Key concepts: Snowflake architecture (timestamp+machine+sequence), clock skew handling, UUID tradeoffs, shard-encoded IDs

**6. Parking Lot System**
Key concepts: Slot reservation race condition (optimistic locking), real-time availability (Redis bitmap or counter per floor), concurrent booking prevention (DB unique constraint + idempotency key), pricing engine, entry/exit event stream

---

### Tier 2 — Intermediate

**7. Type-Ahead / Autocomplete (Generic)**
Key concepts: Trie vs Redis Sorted Set (lexicographic range query), ranking by global frequency, caching top-N results per prefix

**8. Search Autocomplete with Personalization**
Key concepts: All of generic type-ahead + per-user search history, personalization scoring (global popularity + user affinity), cold start, privacy deletion

**9. Notification System**
Key concepts: Multi-channel delivery (push, SMS, email), fan-out via Kafka (topic per channel), at-least-once delivery + idempotent consumers, user preference filtering, DLQ for failed deliveries, rate limiting per user

**10. Web Crawler**
Key concepts: Distributed BFS with URL frontier queue (Kafka), politeness (robots.txt, crawl delay, per-domain rate limiting), URL deduplication via Bloom filter, content hashing to skip unchanged pages, metadata DB + blob for raw HTML

**11. Distributed Task Queue (Celery-style)**
Key concepts: Task broker (Redis or RabbitMQ), worker pool with competing consumers, task states (PENDING → STARTED → SUCCESS/FAILURE/RETRY), at-least-once + idempotent handlers, retry with exponential backoff, priority queues, visibility timeout, DLQ for poison tasks

**12. Job Scheduling Platform**
Key concepts: Distributed scheduler with leader election (ZooKeeper ephemeral node), exactly-once job execution (idempotency key per job run), at-least-once retry, priority queue, job state machine

**13. Top-K Heavy Hitters**
Key concepts: Count-Min Sketch (approximate frequency), min-heap of size K for extraction, distributed aggregation (per-node local sketch → merge), windowed counting

**14. Leaderboard**
Key concepts: Redis Sorted Set (ZADD/ZRANGE/ZRANK), global vs per-game leaderboard, real-time score update pipeline, paginated rank reads

---

### Tier 3 — Advanced

**15. Chat System (WhatsApp)**
Key concepts: WebSocket connection management, message ordering (Kafka partition per conversation), group chat fan-out, offline delivery (push notification on reconnect), Snowflake message IDs, read receipts

**16. Live News Feed (Twitter/Facebook)**
Key concepts: Fan-out on write (precompute per follower) vs fan-out on read, hybrid approach (push for regular, pull for high-follower accounts), feed ranking, cursor pagination, per-user feed cache in Redis, activity events via Kafka

**17. Hotel / Ticket Reservation**
Key concepts: Race condition on last seat/room (optimistic locking), MVCC + SERIALIZABLE isolation, idempotent booking API, two-phase reservation (hold → confirm with timeout), Saga (book hotel + flight + charge card)

**18. Online Auction**
Key concepts: Bid race condition (optimistic locking on current_max_bid), WebSocket for real-time bid broadcast, auction state machine (OPEN → ENDING → CLOSED), idempotency key, reserve price, auction expiry via scheduled job

**19. Payment System**
Key concepts: Idempotency key on every request, exactly-once money movement, 2PC vs Saga, append-only ledger, reconciliation batch job, SERIALIZABLE isolation, currency as integers, audit trail

**20. Banking Ledger**
Key concepts: Append-only event log, balance derived by replaying events, CQRS (write = append event, read = materialized balance view), snapshot optimization, double-entry bookkeeping, idempotency, audit trail by design

**21. Dropbox / Google Drive**
Key concepts: File chunking (4–8 MB blocks), content-addressable storage (SHA256 = key, dedup), delta sync (only changed chunks uploaded), conflict resolution (conflict copy), metadata DB separate from blob storage, sync client (local watcher → diff → upload)

**22. Taxi Platform (Uber/Lyft)**
Key concepts: Real-time driver location updates (Redis geospatial), geospatial indexing (Geohash or Quadtree), nearby driver search, ETA calculation (Dijkstra on road graph with live traffic), surge pricing, WebSocket/SSE for ride status, trip state machine

**23. Ad Click Aggregation**
Key concepts: High-volume click stream (Kafka), windowed aggregation per advertiser (Count-Min Sketch per window), pre-aggregated rollups (hourly → daily), fraud detection filter

**24. Stock Broker / Trading Platform**
Key concepts: Order matching engine (price-time priority, min-heap for asks + max-heap for bids), strict message ordering, in-memory order book, append-only event log for audit trail, exactly-once trade execution, market data fan-out

**25. YouTube**
Key concepts: Transcoding pipeline (raw → multiple resolutions + formats, Kafka-triggered workers), chunked resumable upload, blob storage (S3) for raw and transcoded, metadata DB, view count with HyperLogLog, content moderation pipeline

**26. Netflix**
Key concepts: Adaptive bitrate streaming (HLS/DASH — client switches quality based on bandwidth), CDN for segment delivery (pull vs push vs hybrid), manifest file structure, DRM, resume playback

---

### Case Study → Concept Mapping

| Case Study | Key Concepts |
|---|---|
| URL Shortener | ID generation, Base62, caching, DB sharding |
| Rate Limiter | All 5 algorithms, Redis, distributed counters |
| Key-Value Store | Consistent hashing, quorum, Bloom filter |
| Parking Lot | Optimistic locking, Redis bitmap, race conditions |
| Type-Ahead | Trie, Redis sorted set, prefix caching |
| Notification System | Kafka fan-out, multi-channel, DLQ, idempotency |
| Web Crawler | BFS, Bloom filter, politeness, content hash |
| Task Queue | Competing consumers, visibility timeout, DLQ |
| Chat System | WebSockets, Kafka ordering, fan-out, offline delivery |
| News Feed | Fan-out on write/read, Kafka, Redis cache, pagination |
| Hotel Reservation | MVCC, SERIALIZABLE, Saga, optimistic locking |
| Auction | Optimistic locking, WebSocket, state machine |
| Payment System | Idempotency, exactly-once, Saga vs 2PC, ledger |
| Banking Ledger | Event log, CQRS, projection, double-entry |
| Dropbox | Chunking, S3, dedup, delta sync |
| Uber | Geohash, Quadtree, Dijkstra, Redis geo |
| Ad Clicks | Kafka, Count-Min Sketch, windowing |
| Stock Broker | Event log, order book, exactly-once |
| YouTube | Transcoding pipeline, upload flow, HyperLogLog |
| Netflix | HLS/DASH, adaptive bitrate, CDN |
