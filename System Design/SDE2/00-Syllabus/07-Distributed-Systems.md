## Phase 7 — Distributed Systems

> HLD relevance: Key-Value Store, Distributed DB, Chat, Dropbox, Collaborative Editing,
> Stock Broker, Hotel Reservation — all require deep distributed systems knowledge.

### SDE-2 Depth Bar For This Phase
- Know the practical distributed-systems primitives that appear in common interview systems.
- Be able to explain consistent hashing, replication, quorum, leader election, idempotency, consensus, and clocks at a real engineering level.
- Understand distributed transactions and conflict resolution well enough to defend tradeoffs.
- This is deeper than SDE-1 awareness, but not yet the same operational bar as SDE-3.

---

### 5.1 Why Distributed Systems Are Hard ✓
- Two Generals Problem — you can never be 100% sure the other side received your message
- This is why every distributed protocol has retries, acknowledgments, and idempotency
- Network Partitions — what happens when nodes can't talk to each other

### 5.2 Consistent Hashing ✓
- Backlink → covered in Caching and Storage phases
- Problem with modulo hashing — adding/removing a node remaps almost all keys
- Consistent hashing ring — only K/N keys remapped when a node joins/leaves
- Virtual nodes (vnodes) — each physical node owns multiple ring positions, better distribution

### 5.3 Replication Strategies ✓
- Backlink → covered in Storage phase
- Single-leader, multi-leader, leaderless (Dynamo-style)
- Quorum reads and writes — W + R > N guarantees you see latest write
- Read repair, anti-entropy, hinted handoff, Last Write Wins

### 5.4 Idempotency ✓
- Backlink → covered in Messaging phase
- Same request executed multiple times = same result as once
- Why critical — network failures cause retries, retries cause duplicates
- Idempotency key — client sends unique ID, server deduplicates

### 5.5 Message Delivery Guarantees ✓
- Backlink → covered in Messaging phase
- At-most-once, at-least-once, exactly-once
- Most systems use at-least-once + idempotent consumer

### 5.6 Distributed Transactions ✓
- Backlink → covered in Storage phase
- Two-Phase Commit (2PC), Saga Pattern, Outbox Pattern

---

### 5.7 Consensus ✓
- What consensus means — all non-faulty nodes agree on the same value
- Why it's hard — Two Generals Problem, clocks can't be trusted

#### Raft ✓
- What is Raft — designed for understandability over Paxos
- Leader election — randomized timeouts, heartbeats, re-election, election safety rule
- Term numbers — ghost leader problem, how term numbers force old leader to step down
- Log replication — WAL, AppendEntries, majority ack, commit, state machine
- Log replication failure cases — 3 crash scenarios
- Fencing tokens ✓

#### ZooKeeper ✓
- ZooKeeper-based election — ephemeral nodes, watches, TCP heartbeat, ZAB protocol
- Leader election flow — race to create ephemeral node, watch on deletion, new race begins

#### Redis Distributed Locks ✓
- SETNX + TTL, async replication gap failure scenario
- Redlock — acquire on majority of independent Redis nodes
- Redis vs ZooKeeper — speed vs correctness, async vs consensus replication

#### Paxos ✓
- What is Paxos — proposer, acceptor, learner roles, proposal numbers, quorum
- Two phases — Prepare/Promise, Accept, value inheritance rule
- Retry cases — Case 1 (DB-2 still in Phase 1), Case 2 (DB-2 already committed)
- Livelock — randomized backoff, designate-a-leader fix, why Raft replaced Paxos

---

### 5.8 Distributed Clocks & Time ✓
- Clock drift — crystal oscillator, T=1/f, PPM, why clocks diverge
- NTP — atomic clocks, GPS hierarchy, T1-T4 delay estimation, slewing, 1-10ms accuracy limit
- Lamport Clocks — logical counter, 3 rules, happens-before ordering, limitation (can't detect concurrency)
- Vector Clocks — one counter per node, 3 rules, causality vs concurrency detection, conflict detection
- TrueTime ✓
  - GPS and atomic clocks — satellites, GPS time signal, GPS primary + atomic backup, military correction
  - Uncertainty window — [earliest, latest] interval, commit wait, Spanner external consistency

### 5.9 CRDTs ← not started
- Merge concurrent writes without coordination, always converges
- G-Counter — grow-only counter, per-node count, merge = max per node
- OT vs CRDT — Google Docs interviewers will ask this directly

### 5.10 Failure Detection ← not started
- Heartbeats — periodic ping, simple but chatty at scale
- Gossip protocol — nodes randomly share state, failure info propagates like an epidemic
- Phi Accrual Failure Detector — probabilistic suspicion score, adapts to network jitter

### 5.11 Merkle Trees ← not started
- Hash tree — each node = hash of its children
- Compare two trees — find diverged subtree in O(log n) instead of O(n)
- Anti-entropy — replicas compare Merkle trees to find what's out of sync

### 5.12 Coordination Services ← not started
- ZooKeeper — znodes, watches, ephemeral nodes (partially covered in 5.7)
  - Use for: leader election, distributed locks, service discovery, config management
- etcd — Raft-based, simpler API, Kubernetes control plane backbone
