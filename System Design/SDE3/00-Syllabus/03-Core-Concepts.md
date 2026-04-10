## Phase 3 - Core Concepts

> HLD relevance: these are the concepts that let you defend architecture choices instead of listing technologies.
> SDE-3 depth means you should be able to explain not only what a concept is, but what it buys you, what it costs, and when it breaks down.

### SDE-3 depth bar for this phase
- Define the concept clearly and use it correctly.
- Compare at least two plausible choices under that concept.
- Explain one failure mode or operational downside for each major choice.
- Tie the concept back to concrete systems like chat, feeds, payments, search, or storage engines.

### 3.1 Performance Metrics
- Latency, throughput, and bandwidth are different bottlenecks and need different fixes.
- p50, p95, and p99 tell different stories; p99 is where user pain usually hides.
- Tail latency amplification in fan-out or microservice chains.
- Queueing delay and saturation effects when a component approaches capacity.
- Jitter matters in streaming, real-time, and tightly budgeted chains.

### 3.2 Service Levels
- SLI = what you measure, SLO = internal target, SLA = external promise.
- Error budget is how much failure the service can spend before rollout posture changes.
- Senior-level expectation: explain how SLO pressure changes deploy strategy and alerting thresholds.
- Not every low-priority workflow deserves the same SLO as the core request path.

### 3.3 Availability
- Availability math, nines, and what downtime they actually imply.
- SPOF analysis, N+1 redundancy, active-active vs active-passive.
- Series vs parallel dependency intuition.
- Availability is about serving a response, not necessarily the correct response.

### 3.4 Reliability
- Reliability is correctness over time, not just uptime.
- A service can be highly available and still return wrong answers.
- MTBF, MTTR, RTO, and RPO at the operational level.
- Senior-level expectation: connect business risk to reliability target.

### 3.5 Scalability
- Vertical vs horizontal scaling.
- Stateless services scale easier than stateful ones.
- Data, coordination, and hotspots are usually the real scaling limit.
- Auto-scaling is not a fix for badly partitioned state or cross-service contention.

### 3.6 Fault Tolerance
- Crash, slow response, and partial failure are different failure modes.
- Timeout strategy: connect timeout, read timeout, and total deadline.
- Retry with exponential backoff and jitter to avoid retry storms.
- Circuit breaker, bulkhead, and graceful degradation patterns.
- Senior-level expectation: explain how your system avoids cascading failure.

### 3.7 Durability
- WAL as the basis for crash recovery and replication.
- Sync vs async replication and the latency / RPO tradeoff.
- Replication is not backup; backups protect against logical corruption and operator mistakes.
- Durability is not free: it costs latency and IO.

### 3.8 Concurrency and Locking
- Optimistic locking when contention is moderate and conflicts are rare.
- Pessimistic locking when correctness matters more than throughput and contention is high.
- MVCC so readers do not block writers.
- Idempotency is separate from locking; retries can still duplicate side effects.
- Distributed locks are fragile without fencing tokens and careful lease handling.
- Senior-level expectation: know when to model away the need for a lock entirely.

### 3.9 Transaction Isolation Levels
- Dirty read, non-repeatable read, phantom read, lost update.
- READ COMMITTED, REPEATABLE READ, SERIALIZABLE.
- Snapshot isolation and what anomalies it still allows.
- Choose isolation level based on business risk, not habit.
- Payments and reservations often justify higher isolation; feeds and analytics usually do not.

### 3.10 Consistency Models
- Linearizable, strong, causal, read-your-writes, monotonic reads, eventual consistency.
- What each model guarantees and what it does not.
- Match model to workload: feed ranking can often accept eventual consistency, payment settlement cannot.
- Senior-level expectation: choose the weakest guarantee that is still safe.

### 3.11 Network Partitions
- Partition means nodes are alive but cannot communicate reliably.
- Split-brain risk when both sides think they can write.
- Quorum as a defense against multiple primaries.
- Senior-level expectation: explain what your system does during partition, not only during healthy steady state.

### 3.12 CAP Theorem
- CAP matters only during partition.
- Real distributed systems do not get to be truly CA under partition.
- CP systems stop serving or reject writes to preserve correctness.
- AP systems continue serving with stale or conflicting data.
- Senior-level expectation: give concrete workload-specific examples, not slogans.

### 3.13 PACELC Theorem
- CAP explains partition-time tradeoff; PACELC explains normal-time latency vs consistency.
- Even when healthy, stronger coordination usually costs latency.
- Senior-level expectation: use PACELC to explain why globally consistent writes are slower.

### 3.14 Security
- Authentication vs authorization.
- RBAC, ACL, service-to-service auth, short-lived credentials.
- Encryption in transit and at rest.
- Token lifetime, refresh flow, revocation, and secret handling awareness.
- Security must be mentioned where the case study touches money, private data, or cross-tenant access.

### 3.15 State Machines
- Every important entity has a lifecycle and legal state transitions.
- Encode allowed transitions in the write path, not just in application comments.
- Timeout-based transitions often need scheduled jobs or lazy-expiry logic.
- Persisting state plus event log together improves auditability and debugging.

### 3.16 NFR-Driven Design
- NFR -> design decision -> tradeoff is the standard move for senior interview answers.
- Availability, latency, consistency, durability, cost, and compliance often conflict.
- Strong answers name the conflict, choose a winner, and state what is being sacrificed.
