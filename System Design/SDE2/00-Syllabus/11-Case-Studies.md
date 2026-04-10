## Phase 11 — Case Studies

> This is the destination. Everything in Phases 1–10 feeds directly into these 32 systems.
> Use the same structure every time — it builds muscle memory for interviews.

### SDE-2 Depth Bar For This Phase
- A baseline architecture is not enough; you should be able to discuss tradeoffs, failure modes, and scaling path.
- For the same case study, SDE-2 means more than SDE-1 but less than SDE-3: stronger design depth without needing full senior-level operational ownership.
- You should be able to explain why a design works, what breaks first, and what your next evolution step would be.

### Same Case Study, Different Tiers
- SDE-1: basic components, simple bottlenecks, simple mitigations.
- SDE-2: clearer tradeoffs, stronger data-model and async reasoning, more realistic failure handling, better scaling discussion.
- SDE-3: deeper correctness boundary, migration plan, multi-region implications, observability, and disaster recovery.

### Example: Chat Across Tiers
- SDE-1: WebSocket vs polling, message storage, offline delivery, basic ordering intuition.
- SDE-2: connection service, ordering by conversation, group fan-out, push on reconnect, presence tradeoffs, message IDs.
- SDE-3: cross-region conversation ownership, reconnect dedup, hotspot rooms, media-path split, consistency boundary and migration path.

### Example: News Feed Across Tiers
- SDE-1: basic feed generation, cache, pagination.
- SDE-2: fan-out on write vs read, hybrid strategy, celebrity problem, ranking, activity pipeline.
- SDE-3: rebuild path, denormalized read-model recovery, multi-region write ownership, ranking fallback and observability.

### Example: Payment Across Tiers
- SDE-1: idempotency, simple payment flow, safe retry awareness.
- SDE-2: ledger, Saga vs 2PC, reconciliation, audit trail, external gateway callback handling.
- SDE-3: business exactly-once boundary, dispute / reversal flows, operational recovery after partial failure, migration and correctness monitoring.

### Structure for Every Case Study
1. **Functional Requirements** — what the system does (2-3 core features)
2. **Non-Functional Requirements** — scale, latency, availability, consistency
3. **Capacity Estimation** — QPS, storage, bandwidth
4. **API Design** — key endpoints, request/response, idempotency
5. **High-Level Architecture** — components and data flow diagram
6. **Data Model** — schema or document structure
7. **Deep Dive** — 2-3 most critical or interesting components
8. **Bottlenecks & Scaling** — what breaks at 10x, how to fix

---

### Tier 1 — Beginner (Do These First)

**1. URL Shortener**
Key concepts: ID generation (Snowflake vs Base62), hash collisions, 301 vs 302 redirect, caching hot URLs, DB sharding by short code

**2. Rate Limiter**
Key concepts: All 5 algorithms (Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Log, Sliding Window Counter), distributed rate limiting with Redis, multi-region synchronization

**3. Key-Value Store**
Key concepts: Consistent hashing with vnodes, replication (quorum R+W>N), conflict resolution (LWW vs vector clocks), LSM Tree storage engine, Bloom filter for read optimization

**4. Pastebin**
Key concepts: Content hash as ID (deduplication), blob storage for content, expiry via TTL, read caching

**5. Unique ID Generator**
Key concepts: Snowflake architecture (timestamp+machine+sequence), clock skew handling, UUID tradeoffs, shard-encoded IDs

**6. Parking Lot System**
Key concepts: Slot reservation race condition (optimistic locking on slot status), real-time availability (Redis bitmap or counter per floor), concurrent booking prevention (DB unique constraint + idempotency key), slot type hierarchy (compact/regular/handicapped), pricing engine, entry/exit event stream

---

### Tier 2 — Intermediate

**7. Type-Ahead / Autocomplete (Generic)**
Key concepts: Trie vs Redis Sorted Set (lexicographic range query), ranking by global frequency, distributed trie sharding by prefix, caching top-N results per prefix

**8. Search Autocomplete with Personalization**
Key concepts: All of generic type-ahead, plus — per-user search history in Redis/Cassandra, personalization scoring (blend global popularity + user affinity weight), cold start problem (no history → fall back to global ranking), history deletion for privacy, A/B testing ranking model

**9. Notification System**
Key concepts: Multi-channel delivery (push, SMS, email), fan-out via message queue (Kafka topic per channel), at-least-once delivery with idempotent consumers, user preference filtering before fan-out, DLQ for failed deliveries, rate limiting per user

**10. Web Crawler**
Key concepts: Distributed BFS with URL frontier queue (Kafka), politeness (robots.txt, crawl delay, per-domain rate limiting), URL deduplication via Bloom filter, content hashing to skip unchanged pages, storage in blob (raw HTML) + metadata DB, DNS cache

**11. Distributed Task Queue (Celery-style)**
Key concepts: Task broker (Redis or RabbitMQ), worker pool with competing consumers, task states (PENDING → STARTED → SUCCESS/FAILURE/RETRY), at-least-once delivery + idempotent task handlers, retry with exponential backoff, priority queues, task routing by queue name, result storage (Redis with TTL), visibility timeout to prevent duplicate execution by multiple workers, DLQ for poison tasks, scheduled/periodic tasks

**12. Job Scheduling Platform**
Key concepts: Distributed scheduler with leader election (ZooKeeper ephemeral node), exactly-once job execution (idempotency key per job run), at-least-once retry with exponential backoff, priority queue for job ordering, worker pool, dead letter queue, job state machine

**13. Top-K Heavy Hitters**
Key concepts: Count-Min Sketch (approximate frequency), min-heap of size K for top-K extraction, distributed aggregation (per-node local sketch → merge), windowed counting (tumbling/sliding windows), HyperLogLog for unique item count

**14. Leaderboard**
Key concepts: Redis Sorted Set (ZADD/ZRANGE/ZRANK), sharding by user cohort for massive scale, global vs per-game leaderboard, real-time score update pipeline, paginated rank reads

---

### Tier 3 — Advanced

**15. Chat System (WhatsApp)**
Key concepts: WebSocket connection management (connection service maps user → server), message ordering (Kafka partition per conversation guarantees order), group chat fan-out (Kafka → each member's message queue), offline delivery (message store + push notification on reconnect), message ID generation (Snowflake), read receipts, end-to-end encryption overview

**16. Live News Feed (Twitter/Facebook)**
Key concepts: Fan-out on write (precompute feed per follower, good for most users) vs fan-out on read (compute on request, for celebrities), hybrid approach (push for regular users, pull for high-follower accounts), feed ranking (ML score), cursor-based pagination, per-user feed cache in Redis, activity events via Kafka

**17. Hotel / Ticket Reservation**
Key concepts: Race condition on last seat/room (optimistic locking — check version before update), MVCC + SERIALIZABLE isolation, idempotent booking API with idempotency key, two-phase reservation (hold → confirm with timeout), distributed transaction via Saga (book hotel + book flight + charge card), compensating transactions on failure

**18. Online Auction**
Key concepts: Bid acceptance race condition (optimistic locking on current_max_bid column), WebSocket for real-time bid broadcast, auction state machine (OPEN → ENDING → CLOSED), preventing duplicate bids (idempotency key), reserve price check, eventual winner determination, auction expiry via scheduled job

**19. Payment System**
Key concepts: Idempotency key on every payment request to prevent double charge, exactly-once money movement, two-phase commit vs Saga (debit source → credit destination — which to use when), ledger as append-only event log, reconciliation batch job to detect discrepancies, retrying external payment gateway calls with idempotency, SERIALIZABLE isolation or 2PC for strong consistency, currency stored as integers (avoid float precision bugs), audit trail

**20. Banking Ledger**
Key concepts: Event sourcing as the core model — every transaction is an immutable append-only event, account balance is never stored directly (derived by replaying events), CQRS — write model (append event) vs read model (materialized balance view updated by projection), snapshot optimization (checkpoint balance every N events to avoid full replay), double-entry bookkeeping (every debit must have a matching credit), idempotency key per transaction, exactly-once guarantee, audit trail by design, Kafka or custom append-only log as event store

**21. Dropbox / Google Drive**
Key concepts: File chunking (4-8 MB blocks), content-addressable storage (SHA256 of chunk = key, automatic dedup), delta sync (only changed chunks uploaded), conflict resolution (last-write-wins or version branching for concurrent edits), metadata DB (file tree, chunk references) separate from blob storage (S3), sync client architecture (local watcher → diff → upload changed chunks)

**22. Taxi Platform (Uber/Lyft)**
Key concepts: Real-time driver location updates (every 4 seconds → Redis geospatial), geospatial indexing (Geohash or Quadtree), nearby driver search, driver-rider matching algorithm, ETA calculation (Dijkstra on road graph with live traffic weights), surge pricing triggers, WebSocket/SSE for ride status updates, trip lifecycle state machine

**23. Ad Click Aggregation**
Key concepts: High-volume click stream (Kafka), windowed aggregation per advertiser (Count-Min Sketch per window), exactly-once counting (Kafka transactions + idempotent store), Lambda architecture (batch layer for accuracy + speed layer for low latency), pre-aggregated rollups (hourly → daily), fraud detection filter before aggregation

**24. Stock Broker / Trading Platform**
Key concepts: Order matching engine (price-time priority, order book as sorted structure — min-heap for asks, max-heap for bids), strict message ordering (single-threaded matching or Raft replicated state machine), low latency (in-memory order book), audit trail via event sourcing (every order event is immutable), exactly-once trade execution, market data fan-out to subscribers

**25. Web Search (Google)**
Key concepts: Web crawler feeds inverted index, index sharding by document hash range, query processing pipeline (tokenize → stem → lookup posting lists → intersect → rank), ranking (PageRank + TF-IDF + ML features), query result cache, spelling correction (edit distance), index freshness (near-real-time vs batch rebuild)

**26. Video Streaming (YouTube/Netflix)**
Key concepts: Transcoding pipeline (raw video → multiple resolutions + formats, async Kafka-triggered worker pool), adaptive bitrate streaming (HLS/DASH — client switches quality based on bandwidth), CDN for video segment delivery, blob storage (S3) for raw and transcoded segments, metadata DB, view count with HyperLogLog, recommendation system overview

---

### Tier 4 — Google-Level / Hard

**27. Google Maps**
Key concepts: Road network as weighted directed graph, Dijkstra/A* for shortest path routing, hierarchical routing (precompute highways, fall back for local roads), real-time traffic overlay (GPS probe data aggregated via stream processing), map tile rendering and CDN delivery, ETA combining historical + live traffic, S2 geometry for spatial indexing

**28. Google Docs (Collaborative Editing)**
Key concepts: Operational Transformation (OT) — transform concurrent operations so they commute, OR CRDT approach (RGA for character sequences), server as serialization arbiter, operational log for replay, cursor and presence sharing via WebSocket, conflict-free by construction with CRDT, offline editing and merge on reconnect

**29. Gmail**
Key concepts: Email storage at scale (per-user blob + inverted index for search), SMTP/IMAP protocol overview, spam detection pipeline (ML model + rule engine), email threading algorithm (group by subject + References header), storage quotas, search using Elasticsearch or custom inverted index, label/folder system

**30. Distributed Message Queue (Kafka from Scratch)**
Key concepts: Partition as append-only log on disk (segment files), leader/follower replication per partition, ISR (In-Sync Replicas), consumer group and partition assignment, offset tracking and commit, retention policy (time + size), log compaction, ZooKeeper/KRaft for metadata and leader election, producer partitioner, exactly-once via transactions

**31. Distributed Cache (Redis from Scratch)**
Key concepts: Consistent hashing for shard assignment, single-threaded event loop, LRU/LFU eviction implementation, AOF + RDB persistence tradeoffs, async primary-replica replication, Sentinel for automatic failover, hash slot assignment in cluster mode (16384 slots), gossip protocol for cluster health

**32. Distributed Database (DynamoDB from Scratch)**
Key concepts: Consistent hashing ring with vnodes for data placement, vector clock versioning for conflict detection, quorum reads/writes (R+W>N), hinted handoff for temporary node failure, anti-entropy repair via Merkle tree comparison, gossip protocol for membership and failure detection, tunable consistency (eventual by default, strong on request)

---

### How to Practice Case Studies

1. **Read** — study the case study notes in `/System Design/`
2. **Draw** — open Excalidraw, draw the architecture from memory
3. **Talk** — explain it out loud as if in an interview (actually speak)
4. **Stress test** — ask yourself: what fails if DB goes down? what if traffic 10x?
5. **Repeat** — come back in 3 days and draw it again without notes

---

### Case Study → Concept Mapping

| Case Study | Key Concepts from Phases 1–10 |
|---|---|
| URL Shortener | ID generation, Base62, caching, DB sharding |
| Rate Limiter | All 5 algorithms, Redis, distributed counters |
| Key-Value Store | Consistent hashing, quorum, LSM, Bloom filter |
| Parking Lot | Optimistic locking, Redis bitmap, race conditions |
| Type-Ahead | Trie, Redis sorted set, prefix caching |
| Search Autocomplete | Personalization scoring, cold start, user history |
| Distributed Task Queue | Competing consumers, visibility timeout, DLQ, retry |
| Notification System | Kafka fan-out, multi-channel, DLQ, idempotency |
| Web Crawler | BFS, Bloom filter, politeness, content hash |
| Chat System | WebSockets, Kafka ordering, fan-out, offline delivery |
| News Feed | Fan-out on write/read, Kafka, Redis cache, pagination |
| Hotel Reservation | MVCC, SERIALIZABLE, Saga, optimistic locking |
| Auction | Optimistic locking, WebSocket, state machine |
| Payment System | Idempotency, exactly-once, Saga vs 2PC, audit log |
| Banking Ledger | Event sourcing, CQRS, projection, double-entry |
| Dropbox | Chunking, S3, dedup, delta sync, conflict resolution |
| Uber | Geohash, Quadtree, Dijkstra, WebSocket, Redis geo |
| Ad Clicks | Kafka, Count-Min Sketch, windowing, Lambda arch |
| Stock Broker | Event sourcing, order book, Raft, exactly-once |
| Web Search | Inverted index, PageRank, sharding, query pipeline |
| YouTube | Transcoding, HLS/DASH, CDN, HyperLogLog |
| Google Maps | A*, S2, hierarchical routing, traffic stream |
| Google Docs | CRDT / OT, WebSocket, conflict-free merge |
| Gmail | Inverted index, threading, SMTP, search at scale |
| Kafka from Scratch | Append-only log, ISR, consumer groups, compaction |
| Redis from Scratch | Consistent hashing, LRU, AOF, Sentinel, cluster |
| DynamoDB from Scratch | Vnodes, vector clocks, quorum, Merkle trees, gossip |
