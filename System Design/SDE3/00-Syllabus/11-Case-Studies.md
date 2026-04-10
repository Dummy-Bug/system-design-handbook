## Phase 11 - Case Studies

> This is the destination.
> The same system can appear at SDE-1, SDE-2, and SDE-3, but the expected depth is completely different.

### SDE-3 depth bar for this phase
- A baseline architecture is table stakes, not the finish line.
- You should be able to discuss correctness, failure handling, migration, observability, and 10x evolution.
- For the same case study, SDE-3 means deeper reasoning about partitioning, consistency, recovery, and operational tradeoffs.

### Same Case Study, Different Tiers
- SDE-1: baseline components, simple scaling, one or two bottlenecks.
- SDE-2: standard tradeoffs, caching, queues, replicas, common failure handling.
- SDE-3: correctness boundaries, multi-region implications, migration path, observability, disaster recovery, and alternative designs.

### Structure for every case study
1. Functional requirements
2. Non-functional requirements
3. Capacity estimation
4. API design
5. High-level architecture
6. Data model
7. Deep dive into 2-3 critical components
8. Failure modes, migration path, and what breaks at 10x

---

### Tier 0 - Warm-up only

**1. URL Shortener**
SDE-3 depth:
- baseline redirect system is easy; use it to practice structure and speed
- talk about hot-key caching, ID strategy, redirect latency, abuse / spam protection
- mention migration path from single DB to sharded storage

**2. Rate Limiter**
SDE-3 depth:
- compare token bucket, sliding window, and fixed window
- discuss per-user vs per-tenant vs per-IP limits
- discuss distributed coordination and edge enforcement
- mention failure behavior when Redis is down

---

### Tier 1 - Core senior systems

**3. Chat System**
SDE-3 depth:
- WebSocket connection service and sticky routing strategy
- message ordering per conversation vs global ordering
- offline delivery, history sync, dedup on reconnect
- presence accuracy vs cost
- group chat fan-out and large-room hotspots
- cross-region home-region model for conversations
- media path separated from text path

**4. News Feed**
SDE-3 depth:
- fan-out on write vs fan-out on read vs hybrid
- celebrity asymmetry and write amplification
- ranking service and fallback behavior if ranking is down
- feed cache invalidation and pagination strategy
- activity stream, denormalized read model, and backfill / rebuild path
- multi-region read locality vs write ownership

**5. Distributed Task Queue**
SDE-3 depth:
- competing consumers, visibility timeout, retry policy, and DLQ
- task idempotency and poison-message handling
- worker autoscaling from queue lag
- priority handling and starvation risk
- exactly-once claim vs practical at-least-once behavior
- operational debugging: why is the queue draining slowly?

**6. Job Scheduling Platform**
SDE-3 depth:
- scheduler leader election and fencing
- exactly-once run semantics vs at-least-once execution
- workflow state machine
- retry orchestration and backoff policy
- missed-trigger recovery after scheduler outage
- persistent execution history and auditability

**7. Reservation / Booking System**
SDE-3 depth:
- race on last seat / room / slot
- optimistic locking vs SERIALIZABLE vs reservation-hold model
- hold-confirm-expire flow and timeout jobs
- idempotency key on confirm path
- payment coupling and Saga / compensation
- how to prevent oversell under retries and failover

**8. Payment System**
SDE-3 depth:
- idempotent payment initiation
- external gateway retry behavior and callback races
- ledger as append-only truth
- exactly-once business semantics vs transport semantics
- reconciliation as safety net
- dispute / refund / reversal workflow awareness
- operational recovery after partial failure

**9. Banking Ledger**
SDE-3 depth:
- double-entry bookkeeping
- event sourcing and immutable transaction history
- CQRS and snapshot strategy
- balance derivation vs stored balance
- idempotency and auditability
- invariants that must never break
- replay / repair strategy when projections corrupt

**10. Distributed Key-Value Store**
SDE-3 depth:
- consistent hashing and vnode layout
- replication strategy and quorum math
- conflict resolution
- hinted handoff, read repair, anti-entropy
- failure detection and membership changes
- why this is very different from a cache

---

### Tier 2 - Strong-hire differentiators

**11. Ad Click Aggregation**
SDE-3 depth:
- high-volume ingest with Kafka
- stream processing vs batch correction
- approximate real-time counters vs exact billing numbers
- windowing, watermark, and late-event handling
- OLTP serving path vs OLAP reporting path
- fraud filtering and replay path

**12. Web Search**
SDE-3 depth:
- crawler frontier and dedup
- inverted index build and shard layout
- query serving path and ranking pipeline
- freshness vs indexing cost
- cache strategy at query and result level
- degraded mode when ML ranking is unavailable

**13. Video Streaming Platform**
SDE-3 depth:
- ingest path and transcode pipeline
- HLS / DASH manifest and segment delivery
- CDN offload and origin protection
- metadata vs media separation
- storage / bandwidth economics
- fallback under transcode backlog or regional CDN failure

**14. Dropbox / Google Drive**
SDE-3 depth:
- chunking, deduplication, and content-addressable storage
- delta sync and resumable upload
- metadata DB vs blob storage
- conflict resolution between concurrent edits
- sync replay after client reconnect
- migration and re-chunking strategy

**15. Stock Broker / Matching Engine**
SDE-3 depth:
- price-time priority and deterministic matching
- strict ordering and single-writer / replicated-log design
- audit trail and replay
- exactly-once trade execution
- market data fan-out
- low-latency path isolation from slow control-plane operations

**16. Taxi / Geo-Spatial Platform**
SDE-3 depth:
- moving-object geo index updates
- nearby-driver lookup under high write rate
- ETA pipeline and routing service boundary
- surge trigger pipeline
- rider / driver state machine
- region-local reads with central coordination where needed

---

### Tier 3 - Hard senior systems

**17. Google Docs / Collaborative Editing**
SDE-3 depth:
- OT vs CRDT comparison
- operation ordering and convergence guarantees
- offline editing and merge behavior
- cursor / presence fan-out
- audit log / replay of edits
- large-document performance and metadata growth

**18. Google Maps**
SDE-3 depth:
- graph partitioning and hierarchical routing
- Dijkstra vs A* vs precomputation
- live traffic ingestion and overlay
- tile serving vs route-serving path separation
- geo placement and regional serving strategy
- degraded mode when live traffic is stale

**19. Gmail**
SDE-3 depth:
- SMTP / IMAP / mailbox flow
- per-user storage model and search indexing
- threading model and label model
- spam pipeline and eventual classification updates
- storage retention, quotas, and search freshness

**20. Distributed Message Queue (Kafka from scratch)**
SDE-3 depth:
- append-only log segments
- partition leader / follower replication
- ISR and commit semantics
- consumer-group partition assignment
- retention vs compaction
- producer idempotency and transactional semantics

**21. Distributed Cache (Redis from scratch)**
SDE-3 depth:
- single-threaded event loop implications
- eviction policies and memory pressure
- replication and Sentinel failover
- cluster partitioning
- persistence tradeoffs (RDB / AOF / hybrid)
- hot-key and failover behavior

**22. Distributed Database (DynamoDB / Cassandra style)**
SDE-3 depth:
- leaderless replication
- quorum reads / writes
- vector clocks and conflict resolution
- hinted handoff and anti-entropy with Merkle trees
- failure detection and gossip
- tunable consistency tradeoffs

---

### How to practice case studies
1. draw the baseline architecture fast
2. identify the hardest correctness or scaling problem
3. compare two viable designs
4. explain failure handling and rollback
5. explain what changes at 10x and during migration

---

### What strong SDE-3 case-study practice looks like
- you can answer the same "design chat" prompt at a much deeper bar than SDE-1 or SDE-2
- you do not stop at cache + DB + queue
- you discuss consistency boundary, recovery, and observability
- you can say what would force a redesign later
- you can explain not just the architecture, but how to evolve into it safely
