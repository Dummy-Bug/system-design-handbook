## Phase 2 — Back of Envelope Estimation (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Estimation (QPS, Storage, Bandwidth, Memory, Server counts).
> **SDE-3 Focus:** Moving from "capacity planning" to "system-level feasibility and cost engineering."

### 2.1 — Cost Engineering & Cloud Economics (SDE-3 Exclusive)
*In SDE-2, you estimate servers. In SDE-3, you estimate the bill.*

- **Egress Costs:** The "Hidden Killer." Estimating the cost of moving data out of a region or between AZs. Designing to minimize "Cross-AZ" traffic (which can be 50% of a networking bill).
- **Storage Tiering Economics:** Calculating the ROI of moving 1PB from S3 Standard to Glacier Deep Archive. Factoring in "Retrieval Costs" vs. "Storage Costs."
- **Spot vs. On-Demand Math:** Designing workloads that can handle interruptions to achieve 70-90% cost savings. Estimating the "Interruption Rate" impact on SLOs.

### 2.2 — Performance Bound Estimation (Extension of SDE-2 8.1)
*In SDE-2, you memorize latency numbers. In SDE-3, you estimate the "Speed of Light" limit.*

- **Tail Latency Amplification Math:** Calculating why a system with 10 parallel sub-calls, each with 1% failure/slowness, results in a ~10% overall failure/slowness rate.
- **Queueing Theory (Little's Law):** `L = λW`. Estimating how many requests are "in flight" and how that impacts memory pressure and thread pool sizing.
- **Fan-out Depth vs. Latency:** Estimating the impact of a 3-level deep microservice chain on the total P99 latency budget.

### 2.3 — Extreme Scale Feasibility (Extension of SDE-2 8.4)
*In SDE-2, you justify sharding. In SDE-3, you justify "Radical Architecture."*

- **The "Billions" Bar:** What happens when a counter hits 2^32? When a single table has 1 Trillion rows? When a Kafka topic has 10,000 partitions?
- **Global Write Propagation:** Estimating the latency of a "Strongly Consistent Global Write" (limited by the speed of light across the Atlantic/Pacific).
- **Write Amplification Estimation:** Beyond DB-level—estimating the total I/O cost of a single user action across DB, Cache, Search Index, and Analytics.
