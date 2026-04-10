## Phase 3 - Core System Design Concepts

> HLD relevance: these are the words you will use in almost every design discussion.
> The SDE-1 bar is not deep theory, but you should use these concepts correctly and practically.

### 3.1 Performance metrics
- latency vs throughput vs bandwidth
- p50, p95, p99
- why averages hide real user pain
- tail latency matters for multi-hop systems

### 3.2 Service levels
- SLI - what you measure
- SLO - internal target
- SLA - external promise
- basic intuition for error budgets

### 3.3 Availability
- uptime as a percentage
- nines of availability
- single point of failure
- redundancy and failover

### 3.4 Reliability
- availability is not the same as correctness
- a system can be up and still wrong
- MTBF and MTTR at a high level

### 3.5 Scalability
- vertical vs horizontal scaling
- stateless services scale more easily
- database is usually the first bottleneck, not app servers

### 3.6 Fault tolerance
- timeouts
- retries
- exponential backoff
- jitter
- circuit breaker at a high level
- graceful degradation instead of full failure

### 3.7 Durability
- WAL intuition
- sync vs async replication
- replication is not backup

### 3.8 Concurrency and locking
- race conditions
- optimistic locking with version field
- pessimistic locking when contention is high
- idempotency keys for duplicate-request safety

### 3.9 Transaction isolation - basics only
- dirty read
- non-repeatable read
- phantom read
- READ COMMITTED vs REPEATABLE READ vs SERIALIZABLE
- know when SERIALIZABLE is worth the cost - reservations and money movement

### 3.10 Consistency basics
- strong consistency
- read-your-writes
- eventual consistency
- stale reads - when acceptable and when dangerous

### 3.11 What SDE-1 should be comfortable saying
- "I can tolerate stale reads here"
- "I need idempotency because retries can duplicate requests"
- "I would use optimistic locking to avoid double booking"
- "I would accept eventual consistency for the feed, but not for payment state"

