## Phase 6 — Messaging & Event-Driven (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Messaging (Kafka basics, Partitions, Consumer Groups, DLQ, Delivery Guarantees, Outbox Pattern, Stream vs. Batch basics).
> **SDE-3 Focus:** Moving from "how to use a queue" to "how to orchestrate global event streams, manage exactly-once state at scale, and operate PB-scale pipelines."

### 6.1 — Global Event Orchestration (Extension of SDE-2 6.5)
*In SDE-2, you know Kafka replication. In SDE-3, you manage cross-continent event flow.*

- **Cross-Region Replication (MirrorMaker2 / Confluent Replicator):** Beyond "copying data"—managing "Active-Active" event streams. Handling "Cycle Detection" and "Infinite Loops" in bi-directional replication.
- **Global Event Ordering:** The "Impossible" Problem—why you can't have global strict ordering. Designing for "Per-User" or "Per-Entity" ordering across regions using "Home Region" routing.
- **Producer-Side Locality:** Routing events to the nearest regional broker and using "Async Background Replication" to the central hub.

### 6.2 — Exactly-Once Operationalization (Extension of SDE-2 6.3 & 6.5)
*In SDE-2, you know Exactly-Once exists. In SDE-3, you implement it at 1M+ QPS.*

- **Kafka Transactions at Scale:** The performance cost of `processing.guarantee=exactly_once`. Tuning "Transaction Timeouts" and "Commit Intervals" for high-throughput pipelines.
- **Idempotency Across Service Boundaries:** Beyond the DB—how to maintain exactly-once state when an event triggers an external API call (which doesn't support your transaction).
- **Zombie Fencing in Streams:** Using "Fencing Tokens" to ensure a crashed/slow worker doesn't overwrite the state of a new worker.

### 6.3 — High-Volume Partition Management (Extension of SDE-2 6.5)
*In SDE-2, you know Partitions. In SDE-3, you manage the "Partition Storm."*

- **The "10k Partition" Problem:** Why having too many partitions kills Kafka performance (Zookeeper/KRaft metadata bloat, file descriptor limits).
- **Partition Rebalancing Mitigation:** Beyond "adding members"—how to prevent a "Rebalance Storm" where the entire cluster stops processing for minutes when one node blips. (Static Membership, Incremental Rebalancing).
- **Hot Partition Isolation:** Detecting and "Shunting" a high-volume key (e.g., a celebrity user) to a dedicated high-capacity topic to protect the rest of the fleet.

### 6.4 — Advanced Stream Processing (Extension of SDE-2 6.7 & 6.9)
*In SDE-2, you know Windowing. In SDE-3, you manage PB-scale state.*

- **Large-Scale State Management (RocksDB/Flink):** Managing 10TB+ of local state for windowed joins. Handling "Checkpointing" to S3 without stalling the pipeline.
- **Stateful Reprocessing (The "Replay" Strategy):** How to fix a bug in your stream logic and "Backfill" 1 month of data without doubling your infrastructure or losing live events.
- **Late-Event Handling & Watermark Skew:** What to do when one region's clock drifts by 10 minutes—how to "Close the Window" safely without losing data.

### 6.5 — Messaging Economics & Tiered Storage (Extension of SDE-2 6.5)
*In SDE-2, you know Retention. In SDE-3, you optimize the $100k/month Kafka bill.*

- **Tiered Storage (Kafka / Pulsar):** Moving "Cold" segments to S3 automatically while keeping them searchable. Reducing disk costs by 80-90%.
- **Zero-Copy Optimization:** Understanding the "Sendfile" system call—why Kafka is fast and how to ensure your consumers stay in the "Zero-Copy Path."
- **Payload Compression Strategies:** Comparing Zstd vs. Snappy for different workloads. Why "Batching" is the secret to compression ratio.
