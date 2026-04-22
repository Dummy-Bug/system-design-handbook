## Phase 7 — Distributed Systems

> HLD relevance: Key-Value Store, Chat, Dropbox, Hotel Reservation — all require distributed systems knowledge.

### SDE-2 Depth Bar For This Phase
- Know the practical distributed-systems primitives that appear in common interview systems.
- Be able to explain consistent hashing, replication, quorum, idempotency, and distributed locking at a real engineering level.
- Understand distributed transactions well enough to defend tradeoffs.
- Consensus internals (Raft, Paxos), vector clocks, CRDTs, and gossip protocol are SDE-3 — stop short of those here.

### 5.1 Why Distributed Systems Are Hard
- Two Generals Problem — you can never be 100% sure the other side received your message
- This is why every distributed protocol has retries, acknowledgments, and idempotency
- Network Partitions — what happens when nodes can't talk to each other

### 5.2 Consistent Hashing
- Problem with modulo hashing — adding/removing a node remaps almost all keys
- Consistent hashing ring — only K/N keys remapped when a node joins/leaves
- Virtual nodes (vnodes) — each physical node owns multiple ring positions, better distribution

### 5.3 Replication Strategies
- Single-leader — all writes to primary, followers replicate. Simple, strong consistency.
- Multi-leader — multiple write nodes, conflict resolution needed. Used for multi-region.
- Leaderless (Dynamo-style) — any node accepts writes, quorum determines success
- Quorum reads and writes — W + R > N guarantees seeing latest write
- Read repair — detect stale replica on read, update it
- Hinted handoff — if target node is down, store write elsewhere with a hint for later delivery
- Last Write Wins — timestamp-based conflict resolution, risk of data loss

### 5.4 Idempotency
- Same request executed multiple times = same result as once
- Why critical — network failures cause retries, retries cause duplicates
- Idempotency key — client sends unique ID, server deduplicates

### 5.5 Message Delivery Guarantees
- At-most-once, at-least-once, exactly-once
- Most systems use at-least-once + idempotent consumer

### 5.6 Distributed Transactions
- Two-Phase Commit (2PC), Saga Pattern, Outbox Pattern — covered in Storage section

### 5.7 Distributed Locking
- Redis SET NX PX — single-node distributed lock with TTL
- When single-node lock is fine — non-critical deduplication, rate limiting, cache warming
- When you need stronger guarantees — use ZooKeeper ephemeral nodes or etcd leases
- Awareness: Redlock (multi-node Redis lock) exists but has tradeoffs — SDE-3 topic

### 5.8 Failure Detection (Awareness Level)
- Heartbeats — periodic ping to detect dead nodes
- Dead node detection — last heartbeat timestamp + timeout
- Seed nodes — how new nodes bootstrap into a cluster
- Gossip protocol, Phi Accrual failure detector — SDE-3 topics
