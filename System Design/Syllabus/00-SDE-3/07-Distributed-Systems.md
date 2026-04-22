# Distributed Systems

## Why Distributed Systems Are Hard
- Two Generals Problem — you can never be 100% sure the other side received your message
- Network partitions — nodes alive but cannot communicate
- This is why every distributed protocol has retries, acknowledgements, and idempotency
- **FLP Impossibility — in an asynchronous system, no deterministic consensus algorithm can tolerate even one crash failure**
  - **Practical implication — real systems use timeouts and randomization (Raft's randomized timeouts) to work around FLP**
  - **Not a reason consensus is impossible — Paxos and Raft work in practice because they give up guaranteed termination in pathological cases**

## Consistent Hashing
- Problem with modulo hashing — adding/removing a node remaps almost all keys
- Consistent hashing ring — only K/N keys remapped when a node joins/leaves
- Virtual nodes (vnodes) — each physical node owns multiple ring positions
- **Vnodes deep dive — without vnodes, adding a node only relieves one neighbor. With vnodes, load redistributes from all existing nodes evenly.**
- **Replication with consistent hashing — replicate to next N nodes clockwise on the ring**

## Replication Strategies
- Single-leader — all writes to primary, followers replicate. Simple, strong consistency.
- Multi-leader — multiple write nodes, conflict resolution needed. Use for multi-region.
- Leaderless (Dynamo-style) — any node accepts writes, quorum determines success
- Quorum reads and writes — W + R > N guarantees seeing the latest write
- Read repair — on read, detect stale replica and update it
- Anti-entropy — background process compares replicas and syncs differences
- Hinted handoff — if target node is down, store write on a live node with a hint, deliver when target recovers
- Last Write Wins (LWW) — use timestamp to resolve conflicts, risk of data loss

## Idempotency
- Same request executed multiple times = same result as once
- Why critical — network failures cause retries, retries cause duplicates
- Idempotency key — client sends unique ID, server checks if already processed
- Store idempotency key with result in DB — deduplication on retry

## Message Delivery Guarantees
- At-most-once, at-least-once, exactly-once
- Most systems use at-least-once + idempotent consumer
- Exactly-once is expensive — idempotent producer + transactional publish + idempotent consumer

## Distributed Transactions
- Two-Phase Commit (2PC), Saga Pattern, Outbox Pattern — covered in Storage section

## Consensus

### What Consensus Means
- All non-faulty nodes agree on the same value
- Why it's hard — Two Generals Problem, clocks can't be trusted, FLP impossibility

### **Raft**
- **Designed for understandability over Paxos**
- **Leader election:**
  - **Randomized election timeouts — each node waits a random time before starting election**
  - **Candidate sends RequestVote to all nodes, wins if majority votes for it**
  - **Election safety rule — candidate must have log at least as up-to-date as voter's log**
  - **Term numbers — each election increments term. Old leader receives higher term → steps down immediately.**
  - **Ghost leader problem — old leader comes back, doesn't know a new leader was elected. Term number forces it to step down.**
- **Log replication:**
  - **Leader appends entry to its own log, sends AppendEntries to all followers in parallel**
  - **Entry committed when majority of nodes have written it to their log**
  - **State machine — each node applies committed log entries in order**
- **Failure cases:**
  - **Follower crash — leader retries AppendEntries indefinitely**
  - **Leader crash — election starts after randomized timeout, new leader elected**
  - **Network partition — minority partition can't elect leader (no quorum), stops accepting writes. Majority partition elects new leader.**
- **Fencing tokens — monotonically increasing token with each leadership term. Prevents old leader from writing to storage after being deposed.**

### **ZooKeeper**
- **ZAB (ZooKeeper Atomic Broadcast) protocol — Paxos-like but optimized for ZooKeeper's primary-backup model**
- **Ephemeral nodes — znodes that disappear when the client session ends (TCP heartbeat)**
- **Watches — client registers watch on a znode, gets notified when it changes**
- **Leader election flow:**
  - **All candidates race to create /election/leader ephemeral node**
  - **Winner becomes leader, others set watches on the node**
  - **Leader dies → ephemeral node disappears → watches fire → new race begins**
- **Use cases — leader election, distributed locks, service discovery, config management**

### **etcd**
- **Raft-based — strongly consistent, CP in CAP**
- **Leases — time-limited ownership, auto-expire prevents stuck locks**
- **Fencing tokens — monotonically increasing revision number. Storage layer checks token before accepting writes.**
- **Lock vs job tracking — global lock (one actor at a time) vs per-record state machine (PENDING → IN_FLIGHT → DONE)**
- **Kubernetes control plane backbone — stores all cluster state**

### **Paxos**
- **Three roles — Proposer (initiates), Acceptor (votes), Learner (learns the chosen value)**
- **Proposal numbers — globally unique, monotonically increasing. Higher number wins.**
- **Phase 1 — Prepare/Promise:**
  - **Proposer sends Prepare(n) to majority of acceptors**
  - **Acceptor promises not to accept proposals < n, returns highest accepted value if any**
- **Phase 2 — Accept:**
  - **Proposer sends Accept(n, v) — v is highest value returned in Phase 1, or proposer's own if none**
  - **Acceptor accepts unless it has promised to a higher n**
  - **Value chosen when majority accepts**
- **Value inheritance rule — proposer must use the value from the highest-numbered accepted proposal (not its own)**
- **Livelock — two proposers keep outbidding each other, no value chosen. Fix: randomized backoff, designate a single leader.**
- **Why Raft replaced Paxos — Raft is far easier to understand and implement correctly. Paxos paper is notoriously hard to follow.**

### Redlock
- Multi-node distributed lock across independent Redis nodes
- Acquire on majority (3 of 5), release all if majority not acquired within timeout
- Covered in detail in Core Concepts section

## **Distributed Clocks and Time**

### **Clock Drift**
- **Crystal oscillators in hardware drift over time (parts per million)**
- **NTP synchronization — atomic clocks → GPS → stratum hierarchy → your server**
- **NTP accuracy — 1–10ms in practice. Not good enough for distributed ordering.**
- **Why you can't trust wall clock for ordering — two events 1ms apart on different servers may appear to happen in wrong order**

### **Lamport Clocks**
- **Logical counter, not wall clock**
- **Three rules:**
  - **On internal event: increment counter**
  - **On send: increment counter, attach to message**
  - **On receive: counter = max(local, received) + 1**
- **Happens-before ordering — if A happens-before B, Lamport(A) < Lamport(B)**
- **Limitation — converse is not true. Can't detect concurrency. If Lamport(A) < Lamport(B), A may or may not have happened before B.**

### **Vector Clocks**
- **One counter per node. Each node tracks [n1_count, n2_count, n3_count, ...]**
- **Three rules (same as Lamport but per node)**
- **Causality detection — A caused B if A's vector is strictly less than B's vector in every position**
- **Concurrency detection — neither A ≤ B nor B ≤ A → they are concurrent, conflict detected**
- **Used by — Dynamo-style systems (DynamoDB originally, Riak) for conflict detection**
- **Trade-off — vector size grows with number of nodes, pruning needed at scale**

### **TrueTime (Google Spanner)**
- **GPS receivers + atomic clocks in every datacenter**
- **TrueTime API returns an interval [earliest, latest] not a single timestamp**
- **Commit wait — Spanner waits until earliest > commit timestamp before making commit visible**
  - **This ensures any subsequent transaction's earliest > this commit's latest**
  - **Guarantees external consistency — if transaction B starts after A commits, B's timestamp > A's**
- **Why this matters — eliminates the need for distributed locks for read-only transactions**

## **CRDTs (Conflict-free Replicated Data Types)**
- **Core idea — data structures that can be merged concurrently without coordination, always converge**
- **G-Counter (Grow-only Counter):**
  - **Each node maintains its own counter**
  - **Merge = take max of each node's counter**
  - **Total value = sum of all node counters**
- **Why LWW loses data — two concurrent increments, LWW keeps only one**
- **CRDTs preserve all concurrent updates by design**
- **OT (Operational Transformation) vs CRDT:**
  - **OT — transform concurrent operations to commute. Requires central server to serialize.**
  - **CRDT — data structure guarantees convergence. No central server needed.**
  - **Google Docs uses OT. Figma uses CRDT. Interviewers may ask which and why.**
- **Use cases — collaborative editing, distributed counters, shopping carts, presence**

## **Failure Detection**

### **Heartbeat at Scale**
- **Naive heartbeat — every node pings every other node**
- **O(n²) messages — 1000 nodes = 1M heartbeat messages per interval. Doesn't scale.**

### **Gossip Protocol**
- **Each node periodically picks K random nodes and shares its knowledge**
- **Information spreads like an epidemic — O(log n) rounds to reach all nodes**
- **Counter table — each node tracks (node_id, heartbeat_count, timestamp)**
- **Node considered failed if heartbeat_count hasn't increased for T seconds**
- **Used by — Cassandra (for membership and failure detection), Consul**

### **Phi Accrual Failure Detector**
- **Not binary (alive/dead) — outputs a suspicion score φ**
- **φ = 8 → 99.9997% probability the node has failed**
- **Sliding window of heartbeat intervals → compute mean and variance → phi score based on how late the current heartbeat is**
- **Cassandra's default — φ threshold = 8**
- **Advantage over fixed timeout — adapts to changing network conditions**

## **Merkle Trees**
- **Hash tree — each leaf is hash of a data block, each internal node is hash of its children**
- **Compare two replicas — compare root hashes. If different, recurse into subtrees.**
- **Find diverged data in O(log n) comparisons instead of O(n)**
- **Anti-entropy — replicas exchange Merkle trees to find what's out of sync, only transfer diverged data**
- **Only needed for leaderless architectures — leader-based systems use WAL replay for sync**
- **Used by — DynamoDB, Cassandra, Git (internally), Bitcoin**

## Coordination Services
- ZooKeeper — znodes, watches, ephemeral nodes (covered above in consensus)
- etcd — Raft-based, Kubernetes backbone (covered above)
- Use for — leader election, distributed locks, service discovery, config management
