### 2.1 — Performance Metrics

*Why averages lie and what P99 actually means*

- Latency, Throughput, Bandwidth — three different bottlenecks, three different solutions
- Percentiles (P50/P95/P99) — why averages lie, which percentile to target per system type
- Tail latency amplification — sequential calls compound, parallel calls increase failure probability
- Jitter — variance in latency, matters more than raw latency for streaming
- [[System Design/SDE2/03-Core-Concepts/01-Performance-Metrics/00-Overview|Notes →]]

---

### 2.2 — Service Levels

*SLI → SLO → SLA → Error Budget*

- SLI = what you measure, SLO = internal target, SLA = external contract with penalties
- Error budget — how much failure is allowed, drives deployment velocity (burned → freeze deploys)
- SLOs always stricter than SLAs — the gap is the safety buffer
- [[System Design/SDE2/03-Core-Concepts/02-Service-Levels/00-Overview|Notes →]]

---

### 2.3 — Availability

*Can the system respond? What happens when parts of it fail?*

- Availability = uptime / (uptime + downtime), nines of availability in real downtime numbers
- SPOF, redundancy, N+1, Active-Active vs Active-Passive, series vs parallel calculations
- [[System Design/SDE2/03-Core-Concepts/03-Availability/00-Overview|Notes →]]

---

### 2.4 — Reliability

*Correctness vs uptime — different problems, different solutions*

- Reliability vs Availability — correctness vs uptime
- MTBF / MTTR — how often things break vs how fast you recover
- RTO drives failover speed, RPO drives replication strategy (sync vs async)
- [[System Design/SDE2/03-Core-Concepts/04-Reliability/00-Overview|Notes →]]

---

### 2.5 — Scalability

*The DB is the bottleneck, not the app servers*

- Vertical vs horizontal scaling, stateless services scale freely
- L4 vs L7 load balancing, API gateway (auth + rate limiting + versioning)
- Auto-scaling — reactive vs predictive, cold start solutions
- [[System Design/SDE2/03-Core-Concepts/05-Scalability/00-Overview|Notes →]]

---

### 2.6 — Fault Tolerance

*What happens when things go wrong — and they will*

- Failure modes — crash, slow response, byzantine
- Graceful degradation, bulkhead pattern, timeouts (connect + read + write)
- Retry + exponential backoff + jitter — retry smartly, prevent retry storms
- Circuit breaker — open/closed/half-open, idempotency before retrying
- [[System Design/SDE2/03-Core-Concepts/06-Fault-Tolerance/00-Overview|Notes →]]

---

### 2.7 — Durability

*Data must survive crashes, disk failures, and data center fires*

- WAL — append-only log, crash-safe, basis for replication
- Sync vs async replication — RPO=0 vs lower latency trade-off
- Replication ≠ backup — replication copies corruption, backups protect against logical failures
- [[System Design/SDE2/03-Core-Concepts/07-Durability/00-Overview|Notes →]]

---

### 2.8 — Concurrency & Locking

*Two requests hit the same data at the same time — what happens?*

- Optimistic (CAS, version numbers) vs pessimistic (SELECT FOR UPDATE) — contention decides
- MVCC — readers don't block writers, snapshot isolation
- Idempotency — UUID per operation, POST needs idempotency key
- Distributed locking — Redis SET NX PX + TTL
- **Redlock (distributed lock across multiple Redis nodes)**
  - Problem: single-node Redis lock — if that Redis dies, the lock vanishes, two clients both think they hold it
  - Redlock algorithm: acquire lock on majority (3 out of 5) of independent Redis nodes
  - If majority acquired within timeout → lock is held; if not → release all and retry
  - Survives any 2 Redis node failures — truly distributed, unlike single-node SET NX
  - Trade-off: slower (must contact 5 nodes), more complex, still debated (Martin Kleppmann's critique)
  - When to use: critical sections across distributed services (payment deduction, seat reservation)
  - When single-node lock is fine: non-critical deduplication, rate limiting, cache warming mutex
- [[System Design/SDE2/03-Core-Concepts/08-Concurrency-Locking/00-Overview|Notes →]]

---

### 2.9 — Transaction Isolation Levels

*How much do concurrent transactions interfere with each other?*

- ACID — Atomicity, Consistency, Isolation, Durability
- Four anomalies — dirty read, non-repeatable read, phantom read, lost update
- READ COMMITTED → REPEATABLE READ → SERIALIZABLE
- Snapshot isolation — what DBs actually implement
- [[System Design/05-Storage-and-Databases/02-ACID/04-Transaction-Isolation/00-Overview|Notes →]]

---

### 2.10 — Consistency Models

*How stale is too stale? Depends on what the data represents*

- Spectrum: Linearizable → Strong → Causal → Monotonic → Read-Your-Writes → Eventual
- Each model — what it guarantees, what it doesn't, real-world example
- Stricter consistency = lower availability during partition
- [[System Design/SDE2/03-Core-Concepts/09-Consistency-Models/00-Overview|Notes →]]

---

### 2.11 — Network Partitions

*Nodes don't always crash. Sometimes they just stop talking to each other*

- Partition = nodes alive but cannot communicate (not a crash)
- Split-brain — both nodes think they're primary, quorum (floor(N/2)+1) prevents it
- R + W > N — guarantees seeing latest write
- Quorum = a number, Consensus = a process (Raft, Paxos)
- [[System Design/SDE2/03-Core-Concepts/10-Network-Partitions/00-Overview|Notes →]]

---

### 2.12 — CAP Theorem

*During a partition, pick one: consistency or availability*

- CA doesn't exist — partitions are inevitable, real choice is CP or AP
- C in CAP = linearizability specifically, not just any consistency
- CP (ZooKeeper, Spanner) — stop serving rather than serve stale
- AP (Cassandra, DynamoDB) — serve stale rather than go down
- [[System Design/SDE2/03-Core-Concepts/11-CAP-Theorem/00-Overview|Notes →]]

---

### 2.13 — PACELC Theorem

*CAP tells you what breaks during failure. PACELC tells you what you trade even when healthy*

- Extends CAP: IF partition → A vs C, ELSE (normal) → L vs C
- PA/EL (Cassandra, DynamoDB), PC/EC (Zookeeper, Spanner), PA/EC (MongoDB), PC/EL = invalid
- Consistency always costs latency — even when nothing is broken
- [[System Design/SDE2/03-Core-Concepts/12-PACELC/00-Overview|Notes →]]

---

### 2.14 — Security

*Who are you, what can you do, and is your data protected?*

- Authn (who are you) vs Authz (what can you do)
- JWT — stateless, cannot be revoked → keep access token short-lived (15min)
- Access token (15min) + refresh token (30 days) — 401 triggers silent refresh
- HttpOnly cookie for refresh token — protected from XSS
- Encryption in transit (TLS) + at rest (AES-256) — both required
- [[System Design/SDE2/03-Core-Concepts/13-Security/00-Overview|Notes →]]

---

### 2.15 — State Machines 

*Every entity has a lifecycle. Define the states. Enforce the transitions*

- Finite states, WHERE guard enforces valid transitions (0 rows = illegal)
- State IS the version number — optimistic locking built into one WHERE clause
- Timeout transitions — background job (lazy expiry breaks queries by status)
- Persist both — status column + events table, written atomically
- [[System Design/SDE2/03-Core-Concepts/14-State-Machines/00-Overview|Notes →]]

---

### 2.16 — NFRs

*NFRs come before design. Every decision traces back to one*

- NFR → Design Decision → Trade-off — the three-step move for every interview answer
- Availability → redundancy, multi-AZ | Consistency → quorum, CP DB
- Latency → cache, CDN | Throughput → sharding, queues
- Conflicting NFRs — name the conflict, pick a winner, state what you give up
- [[System Design/SDE2/03-Core-Concepts/15-NFRs/00-Overview|Notes →]]
