## Phase 7 — Distributed Systems (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Distributed Systems (Consistent Hashing, Replication basics, Quorum, Leader Election, Distributed Transactions like 2PC/Saga, Idempotency, Clocks, Consensus basics like Raft).
> **SDE-3 Focus:** Moving from "how a distributed primitive works" to "how to build and operate globally distributed, strongly consistent, and resilient systems at scale."

### 7.1 — Global Consensus & External Consistency (Extension of SDE-2 5.8 & 5.9)
*In SDE-2, you know Raft. In SDE-3, you build globally strongly consistent state.*

- **Multi-Paxos vs. Raft Operationalization:** Beyond "Majority Vote"—how to handle "Leadership Handoff" and "Zombie Leaders" in cross-region clusters.
- **TrueTime & Spanner Mechanics (The SDE-3 Bar):** Understanding how to achieve "External Consistency" using Atomic Clocks/GPS without a global central lock.
- **Clock Drift & Uncertainty Intervals:** Handling the reality that "Now" is a range, not a point in time, and how it impacts the "Wait-Time" for transaction commit.

### 7.2 — Conflict-Free Replicated Data Types (CRDTs) (Extension of SDE-2 5.10)
*In SDE-2, you know G-Counter. In SDE-3, you build complex convergent state.*

- **Complex CRDTs (RGA, LWW-Set, Map):** Moving beyond simple counters—designing collaborative text editors and globally distributed shopping carts that converge without a server arbiter.
- **Metadata Overhead Management:** Handling the "Tombstone Bloat" in CRDTs where the metadata for deleted items can grow larger than the data itself.
- **CRDT vs. OT Tradeoffs (Senior Depth):** When to use which for a specific case study (e.g., Google Docs vs. Figma).

### 7.3 — Advanced Replication & Anti-Entropy (Extension of SDE-2 5.3 & 5.12)
*In SDE-2, you know Quorum. In SDE-3, you manage the "Long Tail" of data divergence.*

- **Multi-Cloud Replication:** How to build a system where data is replicated across AWS and GCP simultaneously to survive a single cloud provider outage.
- **Optimized Merkle Tree Repair:** Using "Incremental Merkle Trees" to find and fix data divergence in TB-sized shards without a full data scan.
- **Hinted Handoff at Scale:** Managing the "Replay Buffer" for 10,000+ nodes when a rack or region goes down for 24 hours.

### 7.4 — Coordination-Free Architectures (SDE-3 Exclusive)
*Moving beyond the "Central ZooKeeper" bottleneck.*

- **Coordination-Free Designs:** Identifying workloads that don't need consensus and can use "Causal Consistency" or "Eventual Convergence" to achieve infinite scale.
- **CALM Theorem:** Understanding which problems are "Monotonic" and can be solved without coordination (e.g., grow-only sets).
- **Sticky Consistency:** Designing systems where a user has "Strong Consistency" with their own data but "Eventual Consistency" with others' to save 100ms+ of global latency.

### 7.5 — Failure Detection & Membership (Extension of SDE-2 5.11)
*In SDE-2, you know Heartbeats. In SDE-3, you manage 10,000+ nodes.*

- **Scalable Gossip Protocols (SWIM):** How nodes discover each other and detect failures in a 10,000+ node cluster without a central bottleneck.
- **Phi Accrual Failure Detectors:** Using suspicion scores instead of binary "Up/Down" flags to adapt to noisy/congested networks.
- **Fencing Tokens & Distributed Leasing:** Ensuring that a "Slow Leader" is correctly fenced off from writing to the DB when its lease expires.
