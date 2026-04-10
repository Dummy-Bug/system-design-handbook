## Phase 7 - Distributed Systems

> HLD relevance: even when your design is simple, production systems are distributed by default.
> At SDE-1 level, this phase is about practical awareness, not deep protocol internals.

### 7.1 Why distributed systems are hard
- machines fail independently
- networks are unreliable
- clocks are not perfectly synchronized
- retries create duplicates

### 7.2 Replication strategies - high level
- single leader
- multi-leader
- leaderless at a high level
- know the tradeoff between simplicity and conflict handling

### 7.3 Consistent hashing - practical intuition
- modulo hashing remaps too much when nodes change
- consistent hashing reduces remapping
- where it appears - distributed cache and key-value stores

### 7.4 Idempotency
- retries happen because networks fail
- idempotency keys prevent duplicate side effects
- essential for booking, payment, and webhook handling

### 7.5 Distributed transactions - only the practical view
- 2PC exists but is expensive and blocking
- Saga is common for long workflows
- outbox pattern solves DB write + event publish problem

### 7.6 Message delivery guarantees
- at-most-once
- at-least-once
- exactly-once as a careful claim, not magic

### 7.7 Clocks and time
- do not trust wall clock across machines for correctness
- ordering in distributed systems is harder than it looks
- know that Lamport clocks and vector clocks exist

### 7.8 Consensus and coordination - awareness only
- leader election is needed in some systems
- Raft solves consensus and replicated log agreement
- ZooKeeper / etcd are coordination tools
- SDE-1 should know what they solve, not implement them

### 7.9 What SDE-1 should take away
- retries require idempotency
- replication creates consistency tradeoffs
- partitions and lag are why distributed systems are tricky
- do not over-design unless the requirements truly demand it

