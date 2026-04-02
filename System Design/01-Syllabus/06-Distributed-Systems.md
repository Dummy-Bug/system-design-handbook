## Phase 6 — Distributed Systems

> HLD relevance: Key-Value Store, Distributed DB, Chat, Dropbox, Collaborative Editing,
> Stock Broker, Hotel Reservation — all require deep distributed systems knowledge.

### 5.1 Why Distributed Systems Are Hard
- Two Generals Problem — you can never be 100% sure the other side received your message
- This is why every distributed protocol has retries, acknowledgments, and idempotency

### 5.2 Consistent Hashing
- Problem with modulo hashing — adding/removing a node remaps almost all keys
- Consistent hashing ring — only K/N keys remapped when a node joins/leaves
- Virtual nodes (vnodes) — each physical node owns multiple ring positions, better distribution
- Where used — Cassandra, DynamoDB, Memcached clusters, CDN routing
- Directly applies to: Key-Value Store, Distributed Cache case studies

### 5.3 Replication Strategies
- Single-leader — all writes to one node, replicas follow
- Multi-leader — multiple write nodes, conflict resolution required
- Leaderless (Dynamo-style) — any node accepts writes, quorum decides truth
- Quorum reads and writes — W + R > N guarantees you see latest write
  - N=3, W=2, R=2 — standard Dynamo config
- Read repair — fix stale replica when read detects divergence
- Anti-entropy — background process syncs replicas
- Hinted handoff — buffer write for a down node, deliver when it returns
- Last Write Wins (LWW) — simplest conflict resolution, loses concurrent writes

### 5.4 Leader Election
- Why needed — someone must be the single writer to avoid split-brain
- Raft leader election — randomized timeouts, first to get majority wins
- ZooKeeper-based election — ephemeral node, whoever creates it is leader
- Fencing tokens — monotonically increasing token, old leader's writes rejected
- Epoch numbers — each new leader gets higher epoch, old leader ignored

### 5.5 Distributed Transactions
- Why hard — no shared memory, partial failures possible, no global clock
- Two-Phase Commit (2PC)
  - Phase 1: coordinator asks all participants "can you commit?"
  - Phase 2: if all say yes, coordinator sends commit; else sends abort
  - Problem: coordinator failure leaves participants blocked (blocking protocol)
  - Use when: strong consistency needed, low frequency operations
- Saga Pattern — break transaction into steps, each with a compensating transaction
  - Choreography — services emit events and react to each other's events
  - Orchestration — central coordinator tells each service what to do
  - Use when: long-running distributed transactions (hotel + flight + car booking)
- Outbox Pattern — write DB row + event in one transaction, CDC picks up event
  - Solves: "write to DB and send to Kafka" dual-write problem
- Directly applies to: Hotel Reservation, Stock Broker, Auction case studies

### 5.6 Idempotency
- Same request executed multiple times = same result as once
- Why critical — network failures cause retries, retries cause duplicates
- Idempotency key — client sends unique ID, server deduplicates
- Natural idempotent ops — GET, PUT (full replace), DELETE
- Making non-idempotent ops idempotent — store result keyed by idempotency key
- DB-level — unique constraint on (user_id, idempotency_key) prevents double insert
- Applies to every API that handles money, reservations, or notifications

### 5.7 Message Delivery Guarantees
- At-most-once — send and forget, can lose messages (metrics, logs)
- At-least-once — retry until ack, can duplicate, need idempotent consumer
- Exactly-once — dedup at consumer or transactional producer+consumer (Kafka)
- Most systems use at-least-once + idempotent consumer — pragmatic and correct

### 5.8 Distributed Clocks & Time
- Clocks drift — you cannot trust wall clock time across machines
- Lamport Clocks — logical counter, increment on each event, max+1 on receive
  - Gives happens-before ordering, not wall-clock time
  - Use in: chat message ordering, distributed logs
- Vector Clocks — one counter per node, detects concurrent writes
  - Use in: Dynamo-style systems to detect conflicts
- Google TrueTime — GPS + atomic clocks give a bounded time uncertainty window; Spanner uses this for global external consistency. Know it exists; don't study the internals for SDE-2.

### 5.9 Consensus Algorithms
- What consensus means — all non-faulty nodes agree on the same value
- Raft (understand well)
  - Leader election — randomized timeouts, term numbers
  - Log replication — leader sends AppendEntries, majority must ack before commit
  - Safety — at most one leader per term, committed entries never lost
  - Used in: etcd (Kubernetes), CockroachDB, Kafka KRaft
- Paxos — the original consensus algorithm; harder to implement correctly than Raft. Proposer, Acceptor, Learner roles, two phases (prepare + accept). Know it exists and why Raft replaced it in practice. Don't study it deeply for SDE-2.
- When consensus appears in case studies — distributed key-value store, distributed DB

### 5.10 CRDTs (Conflict-free Replicated Data Types)
- Merge concurrent writes without coordination, always converges
- G-Counter — grow-only counter, per-node count, merge = max per node (know this one well; it explains the core idea)
- The key property: any two replicas that have seen the same set of operations will have the same state, regardless of the order operations were applied
- Directly applies to: Google Docs (collaborative editing), shopping cart, distributed counters

#### OT (Operational Transformation) vs CRDT — Know the Difference
> Google Docs interviewers will ask this directly

- **Operational Transformation (OT)**
  - When two users concurrently edit the same document, each operation (insert/delete at position X) must be transformed relative to what the other user did before it can be applied
  - Requires a **central server to serialize operations** — the server receives all concurrent ops and determines the canonical order; clients apply the server-ordered ops
  - Example: User A inserts "X" at position 5; simultaneously User B deletes character at position 3. The server transforms A's insert to position 4 (accounting for B's delete) before sending to B's client.
  - Used in: Google Docs (historically), Etherpad
  - Tradeoff: simpler to reason about for text, but requires the server to be the arbiter — no true peer-to-peer editing; offline editing is hard

- **CRDT approach for text (RGA — Replicated Growable Array)**
  - Each character is given a globally unique ID (timestamp + node ID); insertions and deletions reference these IDs, not positions
  - Because IDs are stable (position shifts don't affect them), two replicas can merge without coordination — no server arbitration needed
  - Clients can edit offline and merge when reconnected — the merge is always conflict-free
  - Used in: Figma (multiplayer), Notion, newer collaborative editors
  - Tradeoff: more complex implementation, metadata overhead per character

- **Which to say in an interview** — "I'd use a CRDT-based approach because it supports offline editing and peer-to-peer sync without a serialization bottleneck. OT is simpler conceptually but requires the server to serialize all operations, which creates a single point of ordering."

### 5.11 Failure Detection
- Heartbeats — periodic ping, simple but chatty at scale
- Gossip protocol — nodes randomly share state, failure info propagates like an epidemic
  - Used in: Cassandra, DynamoDB — scalable, no single coordinator
- Phi Accrual Failure Detector — Cassandra uses a probabilistic suspicion score (instead of binary up/down) that adapts to network jitter. Know it exists; one line in an interview is enough.

### 5.12 Merkle Trees
- Hash tree — each node = hash of its children
- Compare two trees — find diverged subtree in O(log n) instead of O(n)
- Anti-entropy — replicas compare Merkle trees to find what's out of sync
- Used in: Cassandra (replica repair), DynamoDB, Git

### 5.13 Coordination Services
- ZooKeeper — distributed coordination, znodes, watches, ephemeral nodes
  - Use for: leader election, distributed locks, service discovery, config management
  - Linearizable writes, sequential consistency for reads
- etcd — Raft-based, simpler API, Kubernetes control plane backbone
- Use in case studies — any system needing distributed coordination (job scheduler, key-value store)
