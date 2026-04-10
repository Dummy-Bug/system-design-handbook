## Phase 3 - Core Concepts

> HLD relevance: these are the concepts that let you defend tradeoffs instead of naming technologies.
> SDE-3 performance depends on using them precisely.

### 3.1 Performance metrics
- latency, throughput, bandwidth
- p50 / p95 / p99
- tail latency amplification
- jitter and queueing delay

### 3.2 Service levels
- SLI, SLO, SLA
- error budget
- how SLO pressure changes rollout strategy

### 3.3 Availability
- uptime formula and nines
- SPOF analysis
- redundancy, N+1, active-active, active-passive
- series vs parallel availability intuition

### 3.4 Reliability
- correctness vs uptime
- MTBF, MTTR
- RTO and RPO
- why a system can be highly available and still unreliable

### 3.5 Scalability
- vertical vs horizontal scaling
- stateless scaling
- why state and coordination create the real limits
- auto-scaling awareness

### 3.6 Fault tolerance
- crash vs slow vs partial failure
- timeout, retry, backoff, jitter
- circuit breaker
- bulkhead
- graceful degradation

### 3.7 Durability
- WAL
- sync vs async replication
- replication vs backup
- logical corruption vs hardware failure

### 3.8 Concurrency and locking
- optimistic vs pessimistic locking
- MVCC
- idempotency
- distributed locking awareness
- why locking is often a symptom of a modeling problem

### 3.9 Transaction isolation levels
- dirty read
- non-repeatable read
- phantom read
- lost update
- READ COMMITTED -> REPEATABLE READ -> SERIALIZABLE
- snapshot isolation

### 3.10 Consistency models
- linearizable
- strong
- causal
- read-your-writes
- monotonic reads
- eventual consistency

### 3.11 Network partitions
- partition vs crash
- split-brain
- quorum as a protection mechanism
- why partitions are inevitable

### 3.12 CAP theorem
- CAP only matters under partition
- CA is not a meaningful distributed choice in the real world
- CP vs AP with concrete examples

### 3.13 PACELC theorem
- even without partition, latency vs consistency is still a tradeoff
- how to explain PACELC without sounding academic

### 3.14 Security
- authentication vs authorization
- RBAC vs ACL
- encryption in transit and at rest
- short-lived access tokens, refresh tokens, service auth

### 3.15 State machines
- entity lifecycle thinking
- valid transitions
- timeout-driven transitions
- state plus events together

### 3.16 NFR-driven design
- NFR -> design decision -> tradeoff
- latency, consistency, availability, cost, durability, compliance
- conflicting NFRs and how to choose a winner explicitly

