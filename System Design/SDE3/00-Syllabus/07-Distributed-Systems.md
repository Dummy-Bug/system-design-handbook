## Phase 7 - Distributed Systems

> HLD relevance: this is where senior-level interviews often get decided.
> SDE-3 depth means you should be able to explain what happens when the network is unreliable, clocks drift, writes conflict, leaders fail, and replicas disagree.

### SDE-3 depth bar for this phase
- Know the main distributed-systems primitives well enough to explain their write path, failure behavior, and operational tradeoffs.
- Compare at least two approaches for replication, coordination, and transaction handling.
- Be able to explain what correctness guarantee your system actually ends up with.
- Be able to connect these topics to KV stores, chat, payments, collaborative editing, and distributed databases.

### 7.1 Why Distributed Systems Are Hard
- Partial failure means one node can be slow while others are healthy.
- Retries create duplicates and reorderings.
- There is no shared memory and no perfectly trustworthy global clock.
- Two Generals Problem awareness: perfect coordination is impossible on an unreliable network.
- Senior-level expectation: reason in terms of failure scenarios, not ideal behavior.

### 7.2 Consistent Hashing
- Why modulo hashing causes mass remapping on node membership change.
- Ring-based placement and clockwise ownership.
- Virtual nodes for better distribution and smoother rebalancing.
- Operational concerns: hot partitions, uneven workloads, node add / remove shock.
- Where it fits: distributed cache, KV stores, CDN routing, partition ownership.

### 7.3 Replication Strategies
- Single-leader replication: simple write path, lagged replicas, failover risk.
- Multi-leader replication: better write locality, conflict pain.
- Leaderless replication: availability and parallelism, harder correctness model.
- Quorum reads and writes (R + W > N).
- Read repair, anti-entropy, hinted handoff.
- Senior-level depth: compare these by latency, conflict risk, and operational complexity.

### 7.4 Conflict Resolution
- Last-write-wins and where it loses valid writes.
- Version vectors / vector clocks to detect concurrency.
- Application-level merge logic for domain-specific conflict handling.
- Conflict avoidance by routing writes to a single authority when possible.
- Senior-level expectation: know when avoiding conflicts is cheaper than resolving them.

### 7.5 Leader Election
- Why systems need a single writer or coordinator.
- Raft-style randomized timeouts and terms.
- ZooKeeper / etcd style ephemeral-node election.
- Epoch numbers and fencing tokens to reject stale leaders.
- Election storms and slow network as practical failure sources.

### 7.6 Distributed Transactions
- Why local DB transactions do not solve cross-service correctness.
- 2PC: prepare / commit flow, blocking risk, coordinator failure.
- Saga choreography vs orchestration.
- Reservation / hold-confirm as an alternative pattern in booking-like flows.
- Outbox pattern for DB write + event publish.
- Senior-level depth: compare payment, booking, and inventory workflows explicitly.

### 7.7 Idempotency
- API-level idempotency with request key.
- Consumer-level idempotency for retry-safe async processing.
- Natural vs synthetic idempotency.
- Idempotency key storage, replay semantics, and retention window.
- DB uniqueness constraint as a hard backstop.

### 7.8 Message Delivery Guarantees
- At-most-once, at-least-once, exactly-once.
- Delivery guarantee at one boundary does not imply end-to-end business correctness.
- Exactly-once often means dedup plus transactional state update in a narrow scope.
- Senior-level expectation: explain where duplicates can still appear.

### 7.9 Distributed Clocks and Time
- Wall-clock drift and why timestamps cannot define truth by themselves.
- Lamport clocks for happens-before ordering.
- Vector clocks for conflict detection.
- Leases, expiry, and time-based coordination risk.
- TrueTime awareness for globally ordered systems like Spanner.

### 7.10 Consensus Algorithms
- What consensus actually solves: one agreed sequence of decisions.
- Raft: leader election, log replication, commit index, safety, terms.
- Quorum is a voting threshold; consensus is a process for one agreed history.
- Paxos awareness only, unless the interview explicitly asks deeper.
- Senior-level depth: be able to explain why consensus is expensive but sometimes unavoidable.

### 7.11 CRDTs (Conflict-free Replicated Data Types)
- Convergence without central coordination.
- G-Counter as the mental-model starter.
- OR-Set awareness for more realistic data.
- Good fit for collaborative or merge-heavy domains.
- Tradeoff: metadata overhead and more complex data model.

### 7.12 OT vs CRDT
- OT uses a central order and transforms operations against prior edits.
- CRDTs allow convergence without a single serialization point.
- Offline editing support is much easier with CRDT-style merge.
- Operational complexity and metadata overhead differ significantly.
- Senior-level expectation: justify the choice for collaborative editing systems.

### 7.13 Failure Detection
- Heartbeats as the simple baseline.
- Gossip protocol for scalable membership dissemination.
- Phi accrual failure detector awareness.
- False positives under network jitter and the cost of reacting too aggressively.

### 7.14 Merkle Trees
- Hash-tree comparison to find divergence cheaply.
- Anti-entropy repair in leaderless stores.
- Useful in large replica repair scenarios where full compare is too expensive.

### 7.15 Coordination Services
- ZooKeeper and etcd as coordination systems, not general-purpose databases.
- Leader election, distributed locks, config management, service discovery.
- Linearizable writes and why coordination systems must be treated as critical dependencies.
- Senior-level expectation: know when to avoid using coordination for every problem.

### 7.16 What SDE-3 Should Be Comfortable Saying
- "I do not get global exactly-once here, so I am relying on idempotency plus reconciliation."
- "I choose single-leader replication because conflict avoidance is cheaper than conflict resolution for this domain."
- "I need fencing tokens, otherwise an old leader can still write after lease expiry."
- "This system is available during partition only because I am accepting stale or conflicting state."
