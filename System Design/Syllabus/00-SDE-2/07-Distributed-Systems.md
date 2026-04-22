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

**Quorum — how it works with real numbers**
- N = total replicas, W = nodes that must ack a write, R = nodes that must respond to a read
- Rule: W + R > N guarantees at least one node in every read has the latest write
- Example: N=3, W=2, R=2 → W+R=4 > 3. One node overlap guaranteed.
  - Write goes to nodes A, B, C. A and B ack (W=2 satisfied). C is slow/down.
  - Read goes to B and C. B has the latest write. Quorum is satisfied — you see the latest.
- What happens if W=1, R=1? No overlap guarantee → stale reads possible
- Common Cassandra tuning: W=QUORUM, R=QUORUM (majority of replicas for both)
- Strong consistency shortcut: W=N (all nodes must ack write) — but now any node failure blocks writes

**Read Repair**
- During a read, coordinator asks R nodes for their value
- If responses differ (one node is stale), coordinator writes the latest value back to the stale node
- This is lazy — repair only happens when a read occurs, not on every write
- Passive healing mechanism — stale replicas catch up gradually through read traffic

**Hinted Handoff**
- Target node for a write is temporarily down
- Another node accepts the write and stores a "hint" — a note saying "deliver this to node C when it comes back"
- When node C recovers, the hint is replayed and the write is delivered
- Short-term solution only — hints are usually kept for a few hours max, not indefinitely
- If C is down longer than the hint window → anti-entropy repair (Merkle tree comparison) fills the gap

- Last Write Wins — timestamp-based conflict resolution, risk of data loss (concurrent writes, one silently dropped)

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

### 5.9 PACELC (Awareness Level)
- CAP only describes behaviour during a partition — but partitions are rare. What about normal operation?
- PACELC asks the question CAP doesn't: **even when the system is running fine, do you optimise for latency or consistency?**
- Full form: if Partition → choose Availability or Consistency. Else → choose Latency or Consistency.
- Why it matters in interviews — when you say "I chose eventual consistency for availability," the interviewer may push: "what's the latency tradeoff even without a partition?" PACELC is the answer.
- Examples:
  - Cassandra: PA/EL — available during partition, low latency during normal operation (async replication)
  - Spanner: PC/EC — consistent during partition, also consistent during normal operation (sync, higher latency)
  - DynamoDB (default): PA/EL — available + low latency, eventual consistency
- SDE-2 move: mention PACELC when justifying a DB choice — "Cassandra is PA/EL — we get low write latency in normal operation, accepting that replicas may briefly diverge."
