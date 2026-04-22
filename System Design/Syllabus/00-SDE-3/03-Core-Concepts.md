# Core Concepts

## Performance Metrics
- Latency, Throughput, Bandwidth — three different bottlenecks, three different solutions
- Percentiles (P50/P95/P99) — why averages lie, which percentile to target per system type
- Tail latency amplification — sequential calls compound, parallel calls increase failure probability
- Jitter — variance in latency, matters more than raw latency for streaming

## Service Levels
- SLI = what you measure, SLO = internal target, SLA = external contract with penalties
- Error budget — how much failure is allowed, drives deployment velocity
- SLOs always stricter than SLAs — the gap is the safety buffer
- Error budget burn rate — how fast you're consuming the budget, basis for alerting

## Availability
- Availability = uptime / (uptime + downtime), nines of availability in real downtime numbers
- SPOF, redundancy, N+1
- Active-active vs active-passive
- Series vs parallel availability calculations

## Reliability
- Reliability vs availability — correctness vs uptime
- MTBF / MTTR — how often things break vs how fast you recover
- RTO drives failover speed, RPO drives replication strategy (sync vs async)

## Scalability
- Vertical vs horizontal scaling, stateless services scale freely
- L4 vs L7 load balancing, API gateway
- Auto-scaling — reactive vs predictive, cold start solutions

## Fault Tolerance
- Failure modes — crash, slow response, byzantine
- Graceful degradation, bulkhead pattern
- Timeouts — connect timeout, read timeout, write timeout
- Retry + exponential backoff + jitter — retry smartly, prevent retry storms
- Circuit breaker — open/closed/half-open, idempotency before retrying

## Durability
- WAL — append-only log, crash-safe, basis for replication
- Sync vs async replication — RPO=0 vs lower latency tradeoff
- Replication ≠ backup — replication copies corruption, backups protect against logical failures

## Concurrency and Locking
- Optimistic (CAS, version numbers) vs pessimistic (SELECT FOR UPDATE) — contention decides
- MVCC — readers don't block writers, snapshot isolation
- Idempotency — UUID per operation, POST needs idempotency key
- Distributed locking — Redis SET NX PX + TTL
- **Redlock — acquire lock on majority (3 of 5) independent Redis nodes**
  - **Problem it solves — single-node Redis lock vanishes if that node dies**
  - **Algorithm — acquire on majority within timeout, if not → release all and retry**
  - **Survives any 2 Redis node failures**
  - **Martin Kleppmann's critique — clock assumptions, unsafe under GC pauses**
  - **When to use vs avoid — critical sections (payments, reservations) vs non-critical deduplication**

## Transaction Isolation
- ACID — Atomicity, Consistency, Isolation, Durability
- Four anomalies — dirty read, non-repeatable read, phantom read, lost update
- READ COMMITTED → REPEATABLE READ → SERIALIZABLE
- **Snapshot isolation — what databases actually implement (PostgreSQL, MySQL InnoDB)**
  - **Each transaction sees a consistent snapshot of the DB at transaction start**
  - **Readers never block writers, writers never block readers**
  - **How it's implemented — MVCC version chains, transaction ID watermarks**
- **Write skew — two transactions read overlapping data, both make decisions based on it, both write without conflict but combined result violates invariant**
  - **Classic example — on-call doctor scheduling (both doctors go off-call thinking the other is still on)**
  - **MVCC + REPEATABLE READ does NOT prevent write skew**
  - **Fix — SERIALIZABLE isolation or SELECT FOR UPDATE to lock the read set**
- **Predicate locking — lock not a row but a predicate (all rows matching a condition), prevents phantoms**

## Consistency Models
- **Full spectrum — from strongest to weakest:**
  - **Linearizability — every operation appears to take effect instantaneously at some point between invocation and response. Reads always see the latest write.**
  - **Sequential consistency — all nodes see operations in the same order, but not necessarily real-time**
  - **Causal consistency — operations causally related are seen in order by all nodes**
  - **Monotonic read — once you read a value, you never read an older value**
  - **Read-your-own-writes — you always see your own writes immediately**
  - **Eventual consistency — given no new updates, all replicas converge eventually**
- **Stricter consistency = lower availability during partition (CAP)**
- **Choosing the model — financial data needs linearizability, social feeds can tolerate eventual**

## Network Partitions
- Partition = nodes alive but cannot communicate (not a crash)
- Split-brain — both nodes think they're primary
- Quorum (floor(N/2)+1) prevents split-brain
- R + W > N — guarantees seeing the latest write
- Quorum = a number, Consensus = a process (Raft, Paxos)

## CAP Theorem
- CA doesn't exist — partitions are inevitable, real choice is CP or AP
- C in CAP = linearizability specifically, not just any consistency
- CP (ZooKeeper, Spanner) — stop serving rather than serve stale
- AP (Cassandra, DynamoDB) — serve stale rather than go down

## **PACELC Theorem**
- **Extends CAP: IF partition → choose A vs C, ELSE (normal ops) → choose L vs C**
- **The key insight — you trade consistency for latency even when nothing is broken**
- **PA/EL — Cassandra, DynamoDB (available during partition, low latency normally)**
- **PC/EC — ZooKeeper, Spanner (consistent during partition, consistent normally)**
- **PA/EC — MongoDB (available during partition, consistent normally)**
- **PC/EL — invalid (can't sacrifice consistency during partition but accept it normally)**
- **How to use in interviews — "this system is PA/EL because we prioritize availability and latency over strict consistency"**

## Security
- Authn (who are you) vs Authz (what can you do)
- JWT — stateless, cannot be revoked → keep access token short-lived (15 min)
- Access token (15 min) + refresh token (30 days) — 401 triggers silent refresh
- HttpOnly cookie for refresh token — protected from XSS
- Encryption in transit (TLS) + at rest (AES-256) — both required

## State Machines
- Finite states, WHERE guard enforces valid transitions (0 rows = illegal transition)
- State IS the version number — optimistic locking built into one WHERE clause
- Timeout transitions — background job handles expired states
- Persist both — status column + events table, written atomically

## NFRs
- NFR → Design Decision → Tradeoff — the three-step move for every interview answer
- Availability → redundancy, multi-AZ | Consistency → quorum, CP DB
- Latency → cache, CDN | Throughput → sharding, queues
- Conflicting NFRs — name the conflict, pick a winner, state what you give up
