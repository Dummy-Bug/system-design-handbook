## Phase 3 — Core Concepts

> HLD relevance: these are the concepts you will use to justify almost every design choice.
> SDE-2 depth means you should be able to explain what a concept buys you, what it costs, and when it should or should not be used.

### SDE-2 Depth Bar For This Phase
- Know the common performance, reliability, consistency, and concurrency concepts correctly.
- Be able to connect each concept to a real design choice or failure mode.
- Go deeper than SDE-1 on things like isolation levels and CAP.
- Stop short of SDE-3 operational depth (PACELC, full consistency spectrum, write skew internals).

### 2.1 — Performance Metrics
- Latency, Throughput, Bandwidth — three different bottlenecks, three different solutions
- Percentiles (P50/P95/P99) — why averages lie, which percentile to target per system type
- Tail latency amplification — sequential calls compound, parallel calls increase failure probability
- Jitter — variance in latency, matters more than raw latency for streaming

---

### 2.2 — Service Levels
- SLI = what you measure, SLO = internal target, SLA = external contract with penalties
- Error budget — how much failure is allowed, drives deployment velocity (burned → freeze deploys)
- SLOs always stricter than SLAs — the gap is the safety buffer

---

### 2.3 — Availability
- Availability = uptime / (uptime + downtime), nines of availability in real downtime numbers
- SPOF, redundancy, N+1, Active-Active vs Active-Passive, series vs parallel calculations

---

### 2.4 — Reliability
- Reliability vs Availability — correctness vs uptime
- MTBF / MTTR — how often things break vs how fast you recover
- RTO drives failover speed, RPO drives replication strategy (sync vs async)

---

### 2.5 — Scalability
- Vertical vs horizontal scaling, stateless services scale freely
- L4 vs L7 load balancing, API gateway (auth + rate limiting + versioning)
- Auto-scaling — reactive vs predictive, cold start solutions

---

### 2.6 — Fault Tolerance
- Failure modes — crash, slow response, byzantine
- Graceful degradation, bulkhead pattern, timeouts (connect + read + write)
- Retry + exponential backoff + jitter — retry smartly, prevent retry storms
- Circuit breaker — open/closed/half-open, idempotency before retrying

---

### 2.7 — Durability
- WAL — append-only log, crash-safe, basis for replication
- Sync vs async replication — RPO=0 vs lower latency trade-off
- Replication ≠ backup — replication copies corruption, backups protect against logical failures

---

### 2.8 — Concurrency & Locking
- Optimistic (CAS, version numbers) vs pessimistic (SELECT FOR UPDATE) — contention decides
- MVCC — readers don't block writers, snapshot isolation
- Idempotency — UUID per operation, POST needs idempotency key
- Distributed locking — Redis SET NX PX + TTL

---

### 2.9 — Transaction Isolation Levels
- ACID — Atomicity, Consistency, Isolation, Durability
- Four anomalies — dirty read, non-repeatable read, phantom read, lost update
- READ COMMITTED → REPEATABLE READ → SERIALIZABLE
- Snapshot isolation — what DBs actually implement

---

### 2.10 — Consistency Models
- Eventual consistency — given no new updates, all replicas converge eventually
- Read-your-own-writes — you always see your own writes immediately
- Stricter consistency = lower availability during partition
- Know the tradeoff: financial data needs strong consistency, social feeds can tolerate eventual

---

### 2.11 — Network Partitions
- Partition = nodes alive but cannot communicate (not a crash)
- Split-brain — both nodes think they're primary, quorum (floor(N/2)+1) prevents it
- R + W > N — guarantees seeing latest write

---

### 2.12 — CAP Theorem
- CA doesn't exist — partitions are inevitable, real choice is CP or AP
- C in CAP = linearizability specifically, not just any consistency
- CP (ZooKeeper, Spanner) — stop serving rather than serve stale
- AP (Cassandra, DynamoDB) — serve stale rather than go down

---

### 2.13 — Security
- Authn (who are you) vs Authz (what can you do)
- JWT — stateless, cannot be revoked → keep access token short-lived (15min)
- Access token (15min) + refresh token (30 days) — 401 triggers silent refresh
- HttpOnly cookie for refresh token — protected from XSS
- Encryption in transit (TLS) + at rest (AES-256) — both required

---

### 2.14 — State Machines
- Finite states, WHERE guard enforces valid transitions (0 rows = illegal)
- State IS the version number — optimistic locking built into one WHERE clause
- Timeout transitions — background job (lazy expiry breaks queries by status)
- Persist both — status column + events table, written atomically

---

### 2.15 — NFRs
- NFR → Design Decision → Trade-off — the three-step move for every interview answer
- Availability → redundancy, multi-AZ | Consistency → quorum, CP DB
- Latency → cache, CDN | Throughput → sharding, queues
- Conflicting NFRs — name the conflict, pick a winner, state what you give up
