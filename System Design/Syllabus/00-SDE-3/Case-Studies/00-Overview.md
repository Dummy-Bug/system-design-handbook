# Case Studies

## SDE-3 Depth Bar
- Baseline architecture is not enough
- Discuss correctness boundary, failure modes, scaling path, migration plan, multi-region implications, and observability
- Know what breaks first and what the next evolution step looks like

## Same Case Study, Different Tiers
- SDE-1: basic components, simple bottlenecks, simple mitigations
- SDE-2: clear tradeoffs, stronger data-model and async reasoning, realistic failure handling
- SDE-3: correctness boundary, migration plan, multi-region implications, disaster recovery, observability, operational ownership

## Structure for Every Case Study
1. Functional Requirements — what the system does (2-3 core features)
2. Non-Functional Requirements — scale, latency, availability, consistency
3. Capacity Estimation — QPS, storage, bandwidth
4. API Design — key endpoints, request/response, idempotency
5. High-Level Architecture — components and data flow diagram
6. Data Model — schema or document structure
7. Deep Dive — 2-3 most critical components
8. Bottlenecks and Scaling — what breaks at 10x, how to fix
9. **Observability — how do you know it's healthy**
10. **Migration Path — how do you get from current state to this design**

---

## Tier 1 — Foundation (Revisited at SDE-3 Depth)

**1. URL Shortener**
Key concepts: ID generation (Snowflake vs Base62), hash collisions, 301 vs 302 redirect, caching hot URLs, DB sharding by short code
**SDE-3 additions: multi-region deployment, global consistent short code uniqueness, migration from SQL to sharded architecture, observability**

**2. Pastebin**
Key concepts: short code generation, blob storage for content, expiry via TTL, caching
**SDE-3 additions: content deduplication (content-addressable storage), cross-region replication, expiry at scale**

**3. Unique ID Generator**
Key concepts: Snowflake architecture (timestamp+machine+sequence), clock skew handling, UUID tradeoffs
**SDE-3 additions: clock skew recovery strategy, multi-datacenter machine ID assignment, monotonicity guarantees across regions**

**4. Parking Lot System**
Key concepts: slot reservation race condition, real-time availability via Redis bitmap, optimistic locking, pricing engine
**SDE-3 additions: multi-location rollup, event sourcing for audit trail, reconciliation between physical sensors and DB**

---

## Tier 2 — Intermediate

**5. Type-Ahead / Autocomplete**
Key concepts: Trie vs Redis Sorted Set (lexicographic range), ranking by global frequency, prefix caching

**6. Search Autocomplete with Personalization**
Key concepts: per-user history, personalization scoring (blend global + affinity), cold start, privacy deletion

**7. Notification System**
Key concepts: multi-channel delivery (push/SMS/email), Kafka fan-out per channel, at-least-once + idempotent consumer, DLQ, rate limiting per user
**SDE-3 additions: cross-region delivery, exactly-once guarantee, user preference consistency across regions**

**8. Web Crawler**
Key concepts: distributed BFS, URL frontier (Kafka), politeness (robots.txt, per-domain rate limit), Bloom filter for dedup, content hashing

**9. Distributed Task Queue (Celery-style)**
Key concepts: broker (Redis/RabbitMQ), competing consumers, task state machine, at-least-once + idempotent handlers, retry with backoff, visibility timeout, DLQ, scheduled tasks

**10. Job Scheduling Platform**
Key concepts: leader election (ZooKeeper ephemeral node), exactly-once job execution (idempotency key per run), at-least-once retry, priority queue, job state machine

**11. Top-K Heavy Hitters**
Key concepts: Count-Min Sketch (approximate frequency), min-heap of size K, distributed aggregation (local sketch → merge), windowed counting

**12. Leaderboard**
Key concepts: Redis Sorted Set (ZADD/ZRANGE/ZRANK), global vs per-game leaderboard, real-time score pipeline, paginated rank reads
**SDE-3 additions: multi-shard global leaderboard, cross-region leaderboard consistency**

---

## Tier 3 — Advanced

**13. Chat System (WhatsApp)**
Key concepts: WebSocket connection management, message ordering (Kafka partition per conversation), group fan-out, offline delivery, Snowflake message IDs, read receipts
**SDE-3 additions: cross-region conversation ownership, reconnect deduplication, hotspot rooms, media path split from message path, consistency boundary**

**14. Live News Feed (Twitter/Facebook)**
Key concepts: fan-out on write vs read, hybrid (push regular / pull celebrity), feed ranking, cursor pagination, Redis feed cache, Kafka activity pipeline
**SDE-3 additions: rebuild path (denormalized read-model recovery), multi-region write ownership, ranking fallback, observability on feed freshness**

**15. Hotel / Ticket Reservation**
Key concepts: race condition on last seat (optimistic locking), MVCC + SERIALIZABLE, idempotent booking API, two-phase reservation (hold → confirm with timeout), Saga (hotel + flight + payment)
**SDE-3 additions: correctness boundary under partial Saga failure, compensating transaction idempotency, cross-region booking consistency**

**16. Online Auction**
Key concepts: bid race condition (optimistic locking on current_max_bid), WebSocket real-time broadcast, auction state machine, idempotency key, reserve price, scheduled expiry

**17. Payment System**
Key concepts: idempotency key per request, exactly-once money movement, Saga vs 2PC, append-only ledger, reconciliation batch job, SERIALIZABLE isolation, currency as integers
**SDE-3 additions: business exactly-once boundary, dispute/reversal flows, operational recovery after partial Saga failure, correctness monitoring**

**18. Banking Ledger**
Key concepts: event sourcing as core model (immutable append-only events), balance derived by replay, CQRS (write = append event, read = materialized balance view), snapshot optimization, double-entry bookkeeping, idempotency, audit trail by design

**19. Dropbox / Google Drive**
Key concepts: file chunking (4-8 MB blocks), content-addressable storage (SHA256), delta sync (only changed chunks), conflict resolution (conflict copy or CRDT merge), metadata DB separate from blob storage, sync client (local watcher → diff → upload)

**20. Taxi Platform (Uber/Lyft)**
Key concepts: real-time driver location (every 4 sec → Redis geospatial), geohash/Quadtree, nearby driver search, driver-rider matching, ETA (Dijkstra on road graph with live traffic), surge pricing, WebSocket/SSE ride status, trip state machine

**21. Ad Click Aggregation**
Key concepts: Kafka click stream, windowed aggregation (Count-Min Sketch per window), exactly-once counting (Kafka transactions + idempotent store), Lambda architecture (batch for accuracy + stream for real-time), pre-aggregated rollups, fraud filter

**22. Stock Broker / Trading Platform**
Key concepts: order matching engine (price-time priority, min-heap for asks + max-heap for bids), strict ordering (single-threaded or Raft replicated state machine), in-memory order book, event sourcing for audit trail, exactly-once trade execution, market data fan-out

**23. YouTube**
Key concepts: transcoding pipeline (raw → multiple resolutions + formats, Kafka-triggered), chunked resumable upload, S3 (raw + transcoded), metadata DB, view count via HyperLogLog, recommendation overview, content moderation pipeline

**24. Netflix**
Key concepts: adaptive bitrate streaming (HLS/DASH), manifest file, segment delivery via CDN, push vs pull vs hybrid CDN, DRM, resume playback, buffer management

---

## Tier 4 — Google-Level / Hard

**25. Google Maps**
Key concepts: road network as weighted directed graph, Dijkstra/A* for shortest path, hierarchical routing (precompute highways, local fallback), real-time traffic overlay (GPS probe stream processing), map tile rendering + CDN, ETA combining historical + live traffic, S2 geometry for spatial indexing

**26. Google Docs (Collaborative Editing)**
Key concepts: Operational Transformation (OT) — transform concurrent operations so they commute, OR CRDT (RGA for character sequences), server as serialization arbiter, operational log for replay, cursor/presence via WebSocket, offline editing and merge on reconnect
**SDE-3: OT vs CRDT tradeoff, why Google Docs uses OT, why Figma uses CRDT**

**27. Gmail**
Key concepts: email storage at scale (per-user blob + inverted index for search), SMTP/IMAP protocol, spam detection pipeline (ML + rule engine), email threading algorithm (group by subject + References header), storage quotas, search via Elasticsearch or custom inverted index, label/folder system

**28. Kafka from Scratch**
Key concepts: partition as append-only log (segment files), leader/follower replication per partition, ISR, consumer group and partition assignment, offset tracking and commit, retention policy, log compaction, ZooKeeper/KRaft for metadata, producer partitioner, exactly-once via transactions

**29. Redis from Scratch**
Key concepts: consistent hashing for shard assignment, single-threaded event loop, LRU/LFU eviction, AOF + RDB persistence tradeoffs, async primary-replica replication, Sentinel for failover, hash slot assignment in cluster mode (16384 slots), gossip for cluster health

**30. DynamoDB from Scratch**
Key concepts: consistent hashing ring with vnodes, vector clock versioning, quorum reads/writes (R+W>N), hinted handoff, anti-entropy via Merkle tree comparison, gossip protocol for membership and failure detection, tunable consistency

---

## Case Study → Concept Mapping

| Case Study | Key Concepts |
|---|---|
| URL Shortener | ID generation, Base62, caching, sharding |
| Rate Limiter | All 5 algorithms, Redis Lua, distributed counters |
| Key-Value Store | Consistent hashing, quorum, LSM, Bloom filter |
| Parking Lot | Optimistic locking, Redis bitmap, race conditions |
| Notification System | Kafka fan-out, multi-channel, DLQ, idempotency |
| Chat System | WebSocket, Kafka ordering, fan-out, offline delivery |
| News Feed | Fan-out write/read, Kafka, Redis cache, pagination |
| Hotel Reservation | MVCC, SERIALIZABLE, Saga, optimistic locking |
| Payment System | Idempotency, exactly-once, Saga vs 2PC, ledger |
| Banking Ledger | Event sourcing, CQRS, projection, double-entry |
| Dropbox | Chunking, S3, delta sync, conflict resolution |
| Uber | Geohash, Quadtree, Dijkstra, Redis geo |
| Ad Clicks | Kafka, Count-Min Sketch, windowing, Lambda arch |
| Stock Broker | Event sourcing, order book, Raft, exactly-once |
| YouTube | Transcoding pipeline, upload flow, HyperLogLog |
| Netflix | HLS/DASH, CDN pull/push/hybrid, DRM |
| Google Maps | A*, S2, hierarchical routing, traffic stream |
| Google Docs | CRDT/OT, WebSocket, conflict-free merge |
| Gmail | Inverted index, threading, SMTP/IMAP, search |
| Kafka from Scratch | Segment files, ISR, consumer groups, compaction |
| Redis from Scratch | Consistent hashing, LRU, AOF, Sentinel, cluster |
| DynamoDB from Scratch | Vnodes, vector clocks, quorum, Merkle trees, gossip |
