## Phase 3 — Core Concepts (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Core Concepts (ACID, CAP/PACELC, Distributed Locks, Fault Tolerance basics).
> **SDE-3 Focus:** Moving from "what is the concept" to "how to build and operate it at massive scale, multi-region, and under extreme failure."

### 3.1 — Global Consistency & Spanner Mechanics (Extension of SDE-2 2.12 & 2.15)
*In SDE-2, you know CAP. In SDE-3, you build globally consistent systems.*

- **TrueTime & External Consistency:** Understanding how Google Spanner uses Atomic Clocks/GPS to achieve "Strong Consistency" globally without the 2PC performance hit.
- **Clock Drift & Uncertainty Intervals:** Handling the reality that "Now" is a range, not a point in time.
- **Conflict-Free Replicated Data Types (CRDTs):** Building convergent systems without central coordination (Collaborative editing, globally distributed counters).

### 3.2 — Cell-Based Architecture & Blast Radius Control (Extension of SDE-2 2.3 & 2.6)
*In SDE-2, you know Redundancy. In SDE-3, you build "Islands of Stability."*

- **The Cell Pattern:** Partitioning the entire stack (LB to DB) into independent "Cells" to limit the blast radius of a failure.
- **Shuffle Sharding:** A "Probabilistic" way to assign users to cells so that no two users share more than a few nodes—effectively isolating "bad users" from the fleet.
- **Static Stability:** Designing systems that continue to work correctly *without* their control plane (e.g., if the central config DB is down, the data plane stays up with its last known good config).

### 3.3 — Performance & Tail Latency Orchestration (Extension of SDE-2 2.1)
*In SDE-2, you know P99. In SDE-3, you fight the "Tail At Scale."*

- **Hedged Requests:** Sending a duplicate request if the first one hasn't returned by a certain percentile (e.g., P95). This "trims the tail" and reduces overall P99 latency.
- **Tied Queues:** Allowing nodes to "steal" work from each other to prevent one slow node from becoming a bottleneck.
- **Micro-burst Handling:** Why P99 is sometimes fine, but the system still "feels slow"—detecting and mitigating 100ms traffic spikes that don't show up in 1-minute averages.

### 3.4 — Disaster Recovery (DR) Orchestration (Extension of SDE-2 2.4 & 2.7)
*In SDE-2, you know RTO/RPO. In SDE-3, you orchestrate the failover.*

- **Failback vs. Failover:** The "hidden" cost of moving traffic back to a recovered region. Handling data "rehydration" and reconvergence.
- **Chaos Engineering (Principles of Chaos):** Beyond "killing nodes"—injecting latency, corrupting packets, and simulating "Grey Failures" (when a node is alive but slow/degraded).
- **Game Days & Operational Readiness:** The human element of operating a complex system under stress.
