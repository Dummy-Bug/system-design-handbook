# SDE-3 System Design Syllabus — FAANGM Strong Hire

> Everything in SDE-2 is included here. Topics marked **bold** are additions at the SDE-3 layer.

## Concepts

1. Networking
2. Back-of-Envelope Estimation
3. Core Concepts
4. Caching
5. Storage and Databases
6. Messaging and Event-Driven Systems
7. Distributed Systems
8. Infrastructure and Reliability
9. Observability
10. Interview Framework

## Case Studies

### Tier 1 — Foundation (Revisited at SDE-3 Depth)
1. URL Shortener
2. Pastebin
3. Unique ID Generator
4. Parking Lot System

### Tier 2 — Intermediate
5. Type-Ahead / Autocomplete
6. Search Autocomplete with Personalization
7. Notification System
8. Web Crawler
9. Distributed Task Queue
10. Job Scheduling Platform
11. Top-K Heavy Hitters
12. Leaderboard

### Tier 3 — Advanced
13. Chat System (WhatsApp)
14. Live News Feed (Twitter/Facebook)
15. Hotel / Ticket Reservation
16. Online Auction
17. Payment System
18. Banking Ledger
19. Dropbox / Google Drive
20. Taxi Platform (Uber/Lyft)
21. Ad Click Aggregation
22. Stock Broker / Trading Platform
23. YouTube
24. Netflix

### Tier 4 — Google-Level / Hard
25. Google Maps
26. Google Docs (Collaborative Editing)
27. Gmail
28. Kafka from Scratch
29. Redis from Scratch
30. DynamoDB from Scratch

---

## Required vs Stretch

> **Required** — must know to pass an SDE-3 / Staff system design interview.
> **Stretch** — Staff+ / Principal territory. Knowing it is a signal, not a requirement.

### Networking

| Topic | Level |
|---|---|
| QUIC — reliability on UDP, 0-RTT, eliminates TCP HOL blocking | Required |
| HTTP/3 — QUIC-based, how it differs from HTTP/2 | Required |
| WebRTC — STUN, TURN, ICE negotiation | Required |
| mTLS — mutual auth, certificate rotation via service mesh | Required |
| GSLB — routing across datacenters, Anycast | Required |
| CDN internals — origin shield, PoP hierarchy, CDN-to-CDN peering | Required |
| Email protocols — SMTP, IMAP, POP3, MX records | Required |
| Private backbone vs public internet — latency engineering | Required |
| TCP congestion control internals — CUBIC vs BBR | **Stretch → Staff+** |

### Estimation

| Topic | Level |
|---|---|
| Cross-region replication bandwidth formula | Required |
| Storage tier cost awareness — S3 Standard vs IA vs Glacier | Required |
| CDN egress cost — when to build your own CDN | Required |
| Google Search scale estimation — 400K QPS, 450 PB index | Required |
| Google Maps scale estimation — 35 GB/s egress, map tile lifecycle | Required |
| How Google-scale changes architecture decisions vs 100M users | Required |

### Core Concepts

| Topic | Level |
|---|---|
| Write skew — MVCC doesn't prevent it, needs SERIALIZABLE | Required |
| Predicate locking — lock a condition not a row, prevents phantoms | Required |
| Full consistency spectrum — linearizability → sequential → causal → eventual | Required |
| Redlock — acquire on majority of 5 Redis nodes, Kleppmann's critique | Required |
| Snapshot isolation implementation — version chains, transaction ID watermarks | Required |
| Serializability vs linearizability — orthogonal properties | **Stretch → Staff+** |

### Storage and Databases

| Topic | Level |
|---|---|
| LSM compaction strategies — leveled vs tiered vs size-tiered, write amplification | Required |
| B+ Tree page structure — 4-16 KB pages, splits, write amplification per insert | Required |
| Cassandra full internals — CommitLog → MemTable → SSTable, tombstones, compaction | Required |
| Bigtable — tablet server, minor/major compaction, row key design as primary concern | Required |
| Google Spanner — TrueTime API, commit wait, 2PC with Paxos groups | Required |
| CDC — log-based (Debezium reads WAL/binlog), before/after image, outbox integration | Required |
| Data migration playbook — backfill → dual-write → shadow reads → cutover → rollback | Required |
| Schema migration on live tables — gh-ost, pg_repack, expand-and-contract | Required |
| S2 geometry — spherical cells, Hilbert curve, level 0-30, used in Google Maps and Uber | Required |
| 2PC blocking protocol problem — in-doubt transactions, coordinator failure | Required |
| NewSQL awareness — Spanner, Aurora, Cosmos DB — when to mention | Required |

### Messaging and Event-Driven

| Topic | Level |
|---|---|
| Kafka internals — segment files, active vs closed segments, index + log files | Required |
| ISR guarantee — committed only when all ISR replicas written | Required |
| Kafka exactly-once — idempotent producer (epoch + seq) + transactional API | Required |
| Backpressure — consumer lag monitoring, autoscale trigger, load shedding | Required |
| Event sourcing — append-only log, projection, snapshot optimization | Required |
| CQRS — separate write and read models, eventual consistency between them | Required |
| Stream processing — tumbling/sliding/session windows, watermarks, checkpointing | Required |
| Lambda vs Kappa architecture — when each, operational tradeoffs | Required |
| Schema evolution — Avro + Schema Registry, Protobuf field numbers, backward/forward compat | Required |
| MapReduce + Spark — how they work, when batch appears in case studies | Required |
| Batch processing — MapReduce paper, Spark DAG, 10-100x faster than Hadoop | **Stretch → Staff+** |

### Distributed Systems

| Topic | Level |
|---|---|
| FLP Impossibility — deterministic consensus impossible with one crash (awareness) | Required |
| Raft full internals — leader election (randomized timeouts, term numbers, ghost leader), log replication, failure cases, fencing tokens | Required |
| ZooKeeper — ZAB protocol, ephemeral nodes, watches, leader election flow | Required |
| etcd — Raft-based, leases, fencing tokens, Kubernetes backbone | Required |
| Paxos — Prepare/Promise/Accept phases, value inheritance rule, livelock fix | Required |
| Lamport clocks — happens-before, the limitation (can't detect concurrency) | Required |
| Vector clocks — causality detection, concurrency detection, pruning at scale | Required |
| TrueTime — GPS + atomic clocks, uncertainty interval, commit wait mechanism | Required |
| CRDTs — G-counter, why LWW loses data, OT vs CRDT (Google Docs vs Figma) | Required |
| Gossip protocol — O(log n) rounds, counter table, used by Cassandra | Required |
| Phi Accrual failure detector — suspicion score φ, adapts to network conditions | Required |
| Merkle trees — hash tree, anti-entropy, O(log n) divergence detection | Required |
| Redlock controversy — Martin Kleppmann's clock assumptions critique | **Stretch → Staff+** |
| CRDT advanced types beyond G-counter | **Stretch → Staff+** |

### Infrastructure and Reliability

| Topic | Level |
|---|---|
| Service mesh + sidecar — Istio, Envoy, mTLS without app code changes | Required |
| Multi-region conflict resolution — LWW vs CRDT vs application merge | Required |
| Data residency — GDPR enforcement at data layer not just routing | Required |
| Cost estimation — compute ($1-2K/server/year), storage tiers, CDN egress | Required |
| Capacity planning — leading indicators, autoscaling targets at 60-70% | Required |
| HLS/DASH full architecture — transcode → segment → manifest → CDN → client buffer | Required |
| Delta sync — chunk hashing, only upload changed chunks, 1-byte change = 1 chunk | Required |
| Adaptive bitrate — buffer management, quality switching algorithm | Required |

### Observability

| Topic | Level |
|---|---|
| Cardinality explosion — high-cardinality labels kill Prometheus | Required |
| Downsampling — 15s → 1m → 1h resolution ladder | Required |
| Prometheus federation — per-datacenter + global federation | Required |
| Head-based vs tail-based tracing sampling — memory cost vs completeness tradeoff | Required |
| Multi-window alerting — 5m at >14.4× and 1h at >6× burn rate, why two windows | Required |
| Burn rate math — burn rate 1 = 30-day exhaustion, page on rate not raw error count | Required |
| Chaos engineering — Chaos Monkey, game days, blast radius control | Required |
| On-call runbook design — "if metric X exceeds Y, do Z" | Required |

### Interview Framework

| Topic | Level |
|---|---|
| Migration and evolution questions — zero-downtime SQL → NoSQL, re-sharding | Required |
| Multi-region failure questions — full region down, EU data residency | Required |
| Operational correctness questions — exactly-once payment, split-brain recovery | Required |
| What to say when you don't know — template + real examples | Required |

---

## Case Studies

### Tier 1 — Required (at SDE-3 depth)

| Case Study | SDE-3 Additions Over SDE-2 |
|---|---|
| URL Shortener | Multi-region architecture, zero-downtime migration to new DB |
| Pastebin | CDC pipeline, cold storage lifecycle, cross-region dedup |
| Unique ID Generator | Clock skew handling, Snowflake at multi-region scale |
| Parking Lot | Distributed lock correctness (Redlock), multi-region reservation |

### Tier 2 & 3 — Required (revisited at SDE-3 depth)

All Tier 2 and Tier 3 SDE-2 case studies revisited with:
- Multi-region architecture and conflict resolution
- Data migration path from naive to final design
- Observability — SLOs, alerting, on-call runbook
- Failure scenarios with exact recovery procedures

### Tier 4 — Required for SDE-3

| Case Study | Key SDE-3 Concepts |
|---|---|
| Google Maps | S2 geometry, geospatial at 1B users, map tile CDN strategy, ETA at scale |
| Google Docs | OT vs CRDT decision, operational transform internals, conflict-free editing |
| Gmail | SMTP/IMAP/MIME, attachment storage, search inverted index at Gmail scale |
| Kafka from Scratch | Segment files, ISR, consumer groups, exactly-once, retention internals |
| Redis from Scratch | Skip list, hash table rehashing, AOF + RDB persistence, Cluster gossip |
| DynamoDB from Scratch | Dynamo paper — consistent hashing, vector clocks, quorum, hinted handoff, sloppy quorum |

### Stretch → Staff+

| Topic | Why Stretch |
|---|---|
| DDIA simplified for interviews | Content for Staff+ preparation, not SDE-3 bar |
| Database internals (storage engine implementation) | Principal-level depth |
| TCP congestion control internals (CUBIC vs BBR) | Rarely tested even at Staff level |
| Paxos Multi-Paxos optimizations | Academic depth beyond interview bar |
