## Phase 5 — Storage & Databases (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Storage (SQL/NoSQL basics, Indexing, B+Tree vs LSM, ACID vs BASE, CDC, 2PC vs Saga).
> **SDE-3 Focus:** Moving from "how a database works" to "how to manage distributed state, global consistency, and massive-scale data evolution."

### 5.1 — Distributed Consensus & Strong Consistency (Extension of SDE-2 3.2, 3.5, 3.15, 3.21)
*In SDE-2, you know ACID and Replication. In SDE-3, you build globally distributed strongly consistent state.*

- **Paxos vs. Raft Implementation Details:** Beyond naming them—how leader election and log replication work at scale. Handling "Zombie Leaders" and "Stale Reads."
- **NewSQL Internals (Spanner/CockroachDB):** How they combine the relational model with horizontal scale using distributed consensus at the storage layer.
- **External Consistency:** Ensuring that if transaction A finishes before B starts, every observer sees A first—even across different continents.

### 5.2 — Advanced Operational Patterns (Extension of SDE-2 3.6, 3.8, 3.17, 3.23)
*In SDE-2, you know Sharding and CDC. In SDE-3, you orchestrate the migration.*

- **Zero-Downtime Petabyte-Scale Migration:** Moving 1PB of data from SQL to NoSQL while taking 100k QPS. Detailed 4-phase plan (Backfill → CDC → Shadow Reads → Cutover).
- **Online Resharding:** Moving data between shards without downtime. Handling "Dirty Pages" and "Consistency Checks" during the move.
- **CDC for Data Governance:** Beyond cache invalidation—using CDC for "Audit Trails," "Compliance Reports," and "Data Lineage."

### 5.3 — Global Data Management (Extension of SDE-2 3.14, 3.15)
*In SDE-2, you know S3 and Replication. In SDE-3, you handle the legal and latency constraints.*

- **Data Residency & Sovereignty (GDPR/CCPA):** Designing a system where EU data *physically* stays in the EU, while still allowing global search and analytics.
- **Conflict Resolution at Global Scale:** Using "Last Write Wins" (LWW) is rarely enough—implementing "Application-Level Conflict Resolution" or "Vector Clocks" for complex state.
- **Storage Economics (TCO):** Beyond "S3 is cheap"—designing "Tiered Storage" (Hot → Warm → Cold) that automatically moves TBs of data based on access frequency to save $1M+ / year.

### 5.4 — Analytical & Operational Convergence (Extension of SDE-2 3.19, 3.20)
*In SDE-2, you know OLTP vs OLAP. In SDE-3, you build the bridge.*

- **HTAP (Hybrid Transactional/Analytical Processing):** Running real-time analytics on your production data *without* impacting latency (e.g., TiDB or SingleStore).
- **Streaming Aggregation vs. Exact Billing:** Using approximate counters (HyperLogLog) for dashboards but replaying raw logs for "Exact Invoicing."
- **Data Lake vs. Data Mesh:** Beyond the Buzzwords—how to structure data so that 50+ different teams can query it independently without a central bottleneck.
