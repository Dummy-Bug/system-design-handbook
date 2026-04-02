## Phase 3 — Core System Design Concepts

> HLD relevance: These are the words and mental models you use to justify every design decision.
> An interviewer will ask "why did you choose X" — this phase gives you the answers.

### 2.1 Performance Metrics
- Latency, Throughput, Bandwidth — three different bottlenecks, three different solutions
- Percentiles (P50/P95/P99/P999) — why averages lie and which percentile to target per system type
- Latency vs Throughput tradeoff — optimizing one can hurt the other
- Interview checklist — assess all three metrics, attach percentile targets before designing
- 📁 Notes: `04-Core-Concepts/01-Performance-Metrics/`

### 2.2 Service Levels (SLI / SLO / SLA / Error Budget)
- SLI — what you measure, SLO — internal target, SLA — external contract with penalties
- Error Budget — how much failure is allowed, drives deployment velocity decisions
- SLOs always stricter than SLAs — the gap is the safety buffer
- 📁 Notes: `04-Core-Concepts/02-Service-Levels/`

### 2.3 Availability
- Availability = uptime / (uptime + downtime), causes of unavailability
- SPOF, redundancy, automatic failover
- Active-Active vs Active-Passive — stateless vs stateful components
- Nines of availability — 99% to 99.999% in real downtime numbers
- Series vs parallel availability calculations
- 📁 Notes: `04-Core-Concepts/03-Availability/`

### 2.4 Reliability & Redundancy
- Reliability vs Availability — uptime vs correctness, different problems
- N+1 redundancy pattern
- MTBF and MTTR — how often things break vs how fast you recover
- RTO and RPO — maximum acceptable downtime vs maximum acceptable data loss
- 📁 Notes: `04-Core-Concepts/04-Reliability-Redundancy/`

### 2.5 Scalability
- Vertical scaling (scale up) — bigger machine, has a ceiling
- Horizontal scaling (scale out) — more machines, near-infinite
- Stateless vs stateful services — stateless is easy to scale horizontally
- Auto-scaling — reactive (CPU/memory metric) vs predictive (schedule)
- Database as the most common bottleneck — scale app tier first, then DB

### 2.6 Concurrency & Locking
- Race conditions — two operations interfere, wrong result
- Optimistic locking — read, compute, write only if nothing changed (CAS)
- Pessimistic locking — lock the row before reading, others wait
- When to use optimistic vs pessimistic — contention level determines the choice
- Deadlocks — what causes them, how to prevent (lock ordering, timeouts)
- Read-Write locks — multiple readers allowed, single writer
- MVCC (Multi-Version Concurrency Control)
  - Readers don't block writers, writers don't block readers
  - Snapshot isolation — each transaction sees a consistent snapshot
  - How PostgreSQL implements it — xmin/xmax on rows
- Distributed locking
  - Redis-based lock — SET NX PX, Redlock algorithm
  - ZooKeeper-based lock — ephemeral nodes
  - When you need distributed locking vs DB-level locking

### 2.7 Transaction Isolation Levels
- Dirty read, non-repeatable read, phantom read, lost update — what each means
- READ COMMITTED — no dirty reads, PostgreSQL default
- REPEATABLE READ — no dirty or non-repeatable reads, MySQL default
- SERIALIZABLE — full isolation, slowest
- Snapshot isolation — what most modern databases actually use
- Choosing the right level — hotel reservation needs higher isolation than a view counter

### 2.8 Consistency Models
- Strong consistency — every read sees the latest write
- Eventual consistency — replicas converge over time
- Read-your-writes — you always see your own writes
- Causal consistency — operations causally related are seen in order
- Linearizability — real-time ordering guarantee
- When each model fits — chat (causal), shopping cart (eventual), bank transfer (strong)

### 2.9 CAP Theorem
- Consistency, Availability, Partition Tolerance — can only guarantee 2 during a partition
- Partitions are not optional — they will happen in any distributed system
- CP systems — ZooKeeper, HBase, etcd — stop serving rather than give stale data
- AP systems — Cassandra, DynamoDB — serve potentially stale data over going down
- How to apply in interviews — "this system needs AP because availability > consistency"

### 2.10 PACELC Theorem
- CAP only describes partition time — PACELC also covers normal operation
- Even without partitions: Latency vs Consistency tradeoff exists
- DynamoDB — optimizes for latency (EL), Spanner — optimizes for consistency (EC)
- Use this when an interviewer pushes on your latency vs consistency choice

### 2.11 Fault Tolerance
- Failure modes — crash, slow response, wrong answer
- Graceful degradation — return partial results rather than total failure
- Redundancy — the primary tool for fault tolerance
- Failover — detecting failure and switching to backup
- Bulkhead pattern — isolate failures so one component doesn't cascade

### 2.12 Durability
- Data survives crashes, power loss, disk failure
- Write-Ahead Log (WAL) — log the operation before applying it
- Replication as durability — copies on multiple nodes/racks/regions
- Backup strategies — full, incremental, differential
- RTO and RPO — design decisions flow from these numbers

### 2.13 Non-Functional Requirements (NFRs)
- How to identify NFRs from the problem statement in an interview
- NFR → Design Decision mapping
  - High availability → redundancy, multi-AZ, active-active
  - Low latency → caching, CDN, read replicas, async processing
  - High throughput → horizontal scaling, partitioning, batching
  - Strong consistency → single-leader writes, quorum
  - Durability → replication factor 3+, WAL, cross-region backup
  - Security → auth, encryption in transit and at rest
- Conflicting NFRs — availability vs consistency, cost vs latency — state the tradeoff explicitly

### 2.14 State Machines
> Appears in 7+ case studies: Auction, Taxi, Task Queue, Hotel, Order, Payment, Chat

- What a state machine is — a finite set of states, transitions triggered by events, and rules about which transitions are valid
- Why it matters in system design — it forces you to enumerate every possible state an entity can be in and prevents illegal transitions at the DB level
- How to model in a database — a `status` column (enum or varchar), enforced valid transitions in application logic or DB constraint
- State machine examples across case studies
  - Auction: `OPEN → ENDING_SOON → CLOSED → SETTLED`
  - Taxi ride: `REQUESTED → DRIVER_MATCHED → IN_PROGRESS → COMPLETED | CANCELLED`
  - Task: `PENDING → IN_PROGRESS → SUCCESS | FAILED | RETRYING`
  - Hotel reservation: `HOLD → CONFIRMED → CANCELLED | EXPIRED`
  - Payment: `INITIATED → PROCESSING → COMPLETED | FAILED | REFUNDED`
- Invalid transition guard — never allow jumping from CANCELLED directly to COMPLETED; check current state before applying transition
- Timeout-driven transitions — a HOLD reservation automatically moves to EXPIRED after 10 minutes if not confirmed (handled by a scheduled job or TTL-based event)
- Persisting state transitions — append an event row per transition (audit trail) vs overwrite a status column (simpler but no history)
- When the interviewer asks "walk me through the states" — draw states as circles, transitions as arrows, label the trigger event on each arrow
