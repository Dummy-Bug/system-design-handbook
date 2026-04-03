## Phase 3 — Core System Design Concepts

> HLD relevance: These are the words and mental models you use to justify every design decision.
> An interviewer will ask "why did you choose X" — this phase gives you the answers.

### 2.1 Performance Metrics
- Latency, Throughput, Bandwidth — three different bottlenecks, three different solutions
- Percentiles (P50/P95/P99/P999) — why averages lie and which percentile to target per system type
- Latency vs Throughput tradeoff — optimizing one can hurt the other
- Tail latency amplification — sequential calls compound, parallel calls increase failure probability
- Jitter — variance in latency, matters more than raw latency for streaming systems
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
- N+1 redundancy — always have one more than you need
- Active-Active vs Active-Passive — stateless vs stateful components
- Nines of availability — 99% to 99.999% in real downtime numbers
- Series vs parallel availability calculations
- 📁 Notes: `04-Core-Concepts/03-Availability/`

### 2.4 Reliability
- Reliability vs Availability — uptime vs correctness, different problems, different solutions
- MTBF and MTTR — how often things break vs how fast you recover
- RTO and RPO — maximum acceptable downtime vs maximum acceptable data loss
- 📁 Notes: `04-Core-Concepts/04-Reliability/`

### 2.5 Fault Tolerance
- Failure modes — crash, slow response, byzantine (wrong answer)
- Graceful degradation — return partial results rather than total failure, reliability vs availability tradeoff
- Bulkhead pattern — isolate thread/connection pools so one service can't starve others
- Timeout — don't wait forever, connect + read + write timeouts
- Retry + exponential backoff + jitter — retry smartly, prevent retry storms
- Circuit Breaker — open/closed/half-open states, stop trying when service is known broken
- Idempotency before retrying non-safe operations
- 📁 Notes: `04-Core-Concepts/06-Fault-Tolerance/`

### 2.6 Durability
- Data survives crashes, power loss, disk failure
- Durability vs Availability — independent guarantees (Redis = available not durable, Postgres = both)
- Write-Ahead Log (WAL) — append-only sequential log, crash-safe, basis for replication
- Replication as durability — node → data center → multi-region layers
- Synchronous vs asynchronous replication — RPO = 0 vs lower latency tradeoff
- Backup strategies — full, incremental, middle ground (weekly full + daily incremental)
- Backup frequency determines RPO — continuous WAL archiving for RPO in seconds
- Replication ≠ backup — replication copies corruption instantly, backups protect against logical failures
- 📁 Notes: `04-Core-Concepts/07-Durability/`

### 2.7 Scalability
- Vertical scaling (scale up) — bigger machine, has a ceiling
- Horizontal scaling (scale out) — more machines, near-infinite
- Stateless vs stateful services — stateless is easy to scale horizontally
- Three bottleneck chain — app servers → database → network
- Load Balancing — algorithms (round robin, least connections, IP hashing, weighted)
- L4 vs L7 load balancing — protocol-driven decision, NAT, connection tables
- API Gateway — auth, rate limiting, versioning, three-layer architecture (L4 NLB → GW → internal LB)
- Auto-scaling — reactive (CPU/memory metric) vs predictive (schedule)
- Connection draining — stop new requests, complete in-flight, then terminate
- Cold start — pre-baked AMIs (90s), warm pools (5s), predictive scaling (0s during spike)
- Database as the most common bottleneck — scale app tier first, then DB
- 📁 Notes: `04-Core-Concepts/05-Scalability/`

### 2.8 Concurrency & Locking
- Race conditions — two operations interfere, wrong result
- Optimistic locking — read, compute, write only if nothing changed (CAS), version numbers
- Pessimistic locking — lock the row before reading, others wait (SELECT FOR UPDATE)
- When to use optimistic vs pessimistic — contention level determines the choice
- Livelock — optimistic locking breaks down under high contention
- Deadlocks — what causes them, how to prevent (lock ordering, timeouts)
- Read-Write locks — multiple readers allowed, single writer
- MVCC (Multi-Version Concurrency Control)
  - Readers don't block writers, writers don't block readers
  - Snapshot isolation — each transaction sees a consistent snapshot
  - Paginated reads stay consistent even if data changes mid-scroll
- Idempotency — preventing duplicate operations (payments, order creation)
  - Two-layer protection — client → your service → stripe, enforce at every hop
  - UUID per operation, safe to retry GET/PUT/DELETE, POST needs idempotency key
- Distributed locking — Redis SET NX PX + TTL for crash safety
  - When to use: multiple servers, no DB write, third-party API calls
- 📁 Notes: `04-Core-Concepts/08-Concurrency-Locking/`

### 2.9 Transaction Isolation Levels
- ACID properties — Atomicity, Consistency, Isolation, Durability (the why behind isolation levels)
  - Atomicity — all or nothing, no partial transactions
  - Consistency — DB moves from one valid state to another
  - Isolation — concurrent transactions don't interfere (this is what isolation levels control)
  - Durability — committed data survives crashes (covered in 2.6)
  - Deep dive on ACID → Phase 4 (3.2)
- Dirty read, non-repeatable read, phantom read, lost update — what each means and which isolation level prevents each
- READ COMMITTED — no dirty reads, PostgreSQL default
- REPEATABLE READ — snapshot isolation in practice (prevents 3 of 4), MySQL default
- SERIALIZABLE — prevents all four, slowest, safety net against developer error
- Snapshot isolation — what databases actually implement (not textbook REPEATABLE READ)
- Isolation + locking combinations — REPEATABLE READ + SELECT FOR UPDATE vs SERIALIZABLE alone
- Choosing the right level — depends on contention, stakes, and whether explicit locking is in place
- Connection to concurrency — isolation levels are the DB's answer to the same problems locking solves
- 📁 Notes: `04-Core-Concepts/09-Transaction-Isolation/`

### 2.10 Consistency Models
- Strong consistency — every read sees the latest write (quorum)
- Eventual consistency — replicas converge over time, order not guaranteed
- Read-your-writes — you always see your own writes (even if others don't yet)
- Monotonic reads — once you see a value, you never see an older one
- Causal consistency — causally related operations seen in correct order by everyone
- Linearizability — real-time ordering guarantee, requires synchronized clocks (Google Spanner)
- The spectrum: Linearizable → Strong → Causal → Monotonic → Read-Your-Writes → Eventual
- When each model fits — chat (causal), shopping cart (eventual), bank transfer (strong)
- Availability tradeoff — stricter consistency = lower availability during partition
- 📁 Notes: `04-Core-Concepts/10-Consistency-Models/`

### 2.11 Network Partitions
- What a partition is — two nodes alive but cannot communicate (not a crash)
- Why partitions are inevitable — undersea cables, routers, data center connectivity, cloud outages
- During partition: serve stale data OR refuse requests — system-dependent decision
- Split-brain — both nodes think they're primary, accept conflicting writes
- Quorum — floor(N/2) + 1, only majority group continues, prevents split-brain
- Odd number of nodes — 3, 5, 7 — one group always has clear majority
- Recovery after partition — stepped-down node replays WAL from new leader
- Quorum vs Consensus — quorum is a number, consensus is a process (Raft, Paxos)
- R + W > N — quorum reads/writes guarantee seeing latest write
- 📁 Notes: `04-Core-Concepts/11-Network-Partitions/`

### 2.12 CAP Theorem
- Consistency, Availability, Partition Tolerance — can only guarantee 2 during a partition
- CA systems don't exist in distributed systems — partitions are not optional
- The C in CAP = linearizability specifically (not just any consistency)
- CP systems — ZooKeeper, HBase, etcd — stop serving rather than give stale data
- AP systems — Cassandra, DynamoDB — serve potentially stale data over going down
- How to apply in interviews — "this system needs AP because availability > consistency"

### 2.13 PACELC Theorem
- CAP only describes partition time — PACELC also covers normal operation
- Even without partitions: Latency vs Consistency tradeoff exists
- DynamoDB — optimizes for latency (EL), Spanner — optimizes for consistency (EC)
- Use this when an interviewer pushes on your latency vs consistency choice

### 2.14 Non-Functional Requirements (NFRs)
- How to identify NFRs from the problem statement in an interview
- NFR → Design Decision mapping
  - High availability → redundancy, multi-AZ, active-active
  - Low latency → caching, CDN, read replicas, async processing
  - High throughput → horizontal scaling, partitioning, batching
  - Strong consistency → single-leader writes, quorum
  - Durability → replication factor 3+, WAL, cross-region backup
  - Security → auth, encryption in transit and at rest
- Conflicting NFRs — availability vs consistency, cost vs latency — state the tradeoff explicitly

### 2.15 State Machines
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
