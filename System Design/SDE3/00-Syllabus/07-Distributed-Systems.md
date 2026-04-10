## Phase 7 - Distributed Systems

> HLD relevance: this is where senior-level system design rounds often get decided.
> You are expected to reason about correctness under partial failure, not just high-level component diagrams.

### 7.1 Why distributed systems are hard
- Two Generals Problem awareness
- partial failures
- retries create duplicates
- no shared memory
- no perfect clock

### 7.2 Consistent hashing
- modulo hashing remaps too much
- ring-based assignment
- virtual nodes
- operational consequences during node add/remove

### 7.3 Replication strategies
- single leader
- multi-leader
- leaderless
- quorum reads and writes
- read repair
- hinted handoff
- anti-entropy

### 7.4 Conflict resolution
- last-write-wins
- version vectors / vector clocks
- application-level merge
- when conflict avoidance is better than conflict resolution

### 7.5 Leader election
- why it exists
- Raft-based election intuition
- ZooKeeper / etcd style election
- fencing tokens
- epoch numbers

### 7.6 Distributed transactions
- why they are hard
- 2PC
- Saga choreography
- Saga orchestration
- outbox as the pragmatic default for dual-write safety

### 7.7 Idempotency
- API idempotency
- consumer idempotency
- idempotency key storage
- DB-level uniqueness enforcement

### 7.8 Message delivery guarantees
- at-most-once
- at-least-once
- exactly-once
- pragmatic recommendation in most systems

### 7.9 Distributed clocks and time
- wall clock drift
- Lamport clocks
- vector clocks
- logical ordering vs real-time ordering
- TrueTime awareness

### 7.10 Consensus
- what consensus solves
- Raft fundamentals
- quorum vs consensus
- Paxos awareness only

### 7.11 CRDTs
- convergent replicated data types
- G-Counter intuition
- where CRDTs beat coordination

### 7.12 OT vs CRDT
- centralized transformation vs coordination-free merge
- collaborative editing tradeoffs
- offline editing implications

### 7.13 Failure detection
- heartbeats
- gossip protocol
- phi accrual failure detector awareness

### 7.14 Merkle trees
- anti-entropy repair
- efficient divergence detection
- where they appear in distributed databases

### 7.15 Coordination services
- ZooKeeper
- etcd
- service discovery
- config management
- distributed locking and leader election

