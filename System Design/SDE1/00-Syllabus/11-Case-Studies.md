## Phase 11 - Case Studies

> This is the destination.
> Everything in the earlier phases should help you speak clearly about these systems.

### Structure for every case study
1. Functional requirements
2. Non-functional requirements
3. Capacity estimation
4. API design
5. High-level architecture
6. Data model
7. Deep dive into 1-2 critical components
8. Bottlenecks and scaling path

---

### Tier 1 - Must do first

**1. URL Shortener**
Key concepts: ID generation, redirect flow, hot-key caching, simple DB design

**2. Rate Limiter**
Key concepts: fixed window, sliding window, token bucket, Redis counters

**3. Pastebin / File Sharing**
Key concepts: blob storage, TTL expiry, metadata in DB, caching reads

**4. Notification System**
Key concepts: fan-out, queues, retries, per-channel delivery, idempotency

**5. Leaderboard**
Key concepts: Redis sorted set, rank reads, score update flow

---

### Tier 2 - Strong-hire SDE-1 systems

**6. Search Autocomplete**
Key concepts: trie, sorted set alternative, ranking, caching top prefixes

**7. Chat System**
Key concepts: WebSocket, message persistence, offline delivery, ordering at a practical level

**8. News Feed**
Key concepts: fan-out on write vs fan-out on read, cache, pagination, celebrity problem

**9. Reservation System**
Key concepts: race condition on last seat, optimistic locking, hold timeout, idempotent booking API

**10. Distributed Task Queue**
Key concepts: producer/consumer, retries, DLQ, visibility timeout, worker pool

---

### Tier 3 - Do after Tier 2 feels comfortable

**11. Key-Value Store - high-level only**
Key concepts: partitioning intuition, replication intuition, cache vs store difference

**12. Payment System - intro version**
Key concepts: idempotency, ledger intuition, external gateway retries, reconciliation

**13. Video Streaming - high-level version**
Key concepts: object storage, CDN, transcoding pipeline, metadata separation

---

### How to practice case studies

1. read the topic
2. draw the architecture from memory
3. explain it out loud in interview format
4. ask what breaks at 10x
5. repeat after a few days

---

### What strong SDE-1 case-study practice looks like

- you can finish a clean baseline architecture quickly
- you can defend simple tech choices
- you can identify bottlenecks without inventing unnecessary complexity
- you can explain one realistic failure scenario for each design

