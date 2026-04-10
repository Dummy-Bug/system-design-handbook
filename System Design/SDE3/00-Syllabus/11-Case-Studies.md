## Phase 11 - Case Studies

> This is the destination.
> Strong SDE-3 prep means going deep on fewer systems, not memorizing a shallow answer for everything.

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
Key concepts: fast structure, estimation, caching, ID generation

**2. Rate Limiter**
Key concepts: algorithm choice, Redis, distributed enforcement

---

### Tier 1 - Core senior systems

**3. Distributed Key-Value Store**
Key concepts: partitioning, replication, quorum, conflict resolution

**4. Chat System**
Key concepts: WebSocket connection management, ordering, presence, offline delivery

**5. News Feed**
Key concepts: fan-out on write vs fan-out on read, ranking, celebrity handling

**6. Distributed Task Queue**
Key concepts: competing consumers, retries, DLQ, visibility timeout, worker scaling

**7. Job Scheduling Platform**
Key concepts: leader election, exactly-once run semantics, retry orchestration

**8. Reservation System**
Key concepts: optimistic locking, hold-confirm flow, SERIALIZABLE tradeoffs, Saga awareness

**9. Payment System**
Key concepts: idempotency, external gateway retries, ledger, reconciliation, correctness-first design

**10. Banking Ledger**
Key concepts: event sourcing, CQRS, snapshots, double-entry bookkeeping, auditability

---

### Tier 2 - Strong-hire differentiators

**11. Ad Click Aggregation**
Key concepts: Kafka, stream processing, OLTP vs OLAP, batch correction

**12. Web Search**
Key concepts: crawler, inverted index, ranking pipeline, freshness vs cost

**13. Video Streaming Platform**
Key concepts: transcoding pipeline, CDN, media/object separation, bandwidth economics

**14. Dropbox / Google Drive**
Key concepts: chunking, deduplication, delta sync, metadata vs blob, conflict handling

**15. Stock Broker / Matching Engine**
Key concepts: deterministic ordering, low latency, order book, audit trail

**16. Taxi / Geo-Spatial Platform**
Key concepts: moving geo indexes, nearest-neighbor lookup, ETA, surge triggers

---

### Tier 3 - Hard senior systems

**17. Google Docs / Collaborative Editing**
Key concepts: OT vs CRDT, convergence, offline editing, operation ordering

**18. Google Maps**
Key concepts: routing, hierarchical graph search, traffic overlay, geo partitioning

**19. Gmail**
Key concepts: email protocols, per-user storage, search, spam pipeline, threading

**20. Distributed Message Queue (Kafka from scratch)**
Key concepts: append-only log, partitions, replication, ISR, compaction, consumer groups

**21. Distributed Cache (Redis from scratch)**
Key concepts: event loop, eviction, replication, persistence, cluster failover

**22. Distributed Database (DynamoDB / Cassandra style)**
Key concepts: leaderless replication, quorum, Merkle trees, vector clocks, tunable consistency

---

### How to practice case studies

1. read the detailed notes
2. draw the architecture without looking
3. explain it out loud as if in an interview
4. pressure-test the hardest failure scenario
5. return later and redraw from memory

---

### What strong SDE-3 case-study practice looks like

- you can explain the baseline design quickly
- you can identify the dominant bottleneck early
- you can compare at least two viable approaches
- you can explain migration and rollback, not just steady state
- you can go deep on correctness and failure handling without losing structure

