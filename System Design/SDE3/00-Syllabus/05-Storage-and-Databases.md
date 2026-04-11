## Phase 5 - Storage and Databases

> HLD relevance: every serious design eventually turns into a data design problem.
> SDE-3 depth means you should be able to explain not only which database to choose, but how it behaves under contention, scale, migration, and failure.

### SDE-3 depth bar for this phase
- Know the major storage families and what workload each one fits.
- Be able to reason about engine-level tradeoffs like B+ tree vs LSM tree, replication lag, and write amplification.
- Be able to discuss migration, resharding, and dual-write / CDC risks.
- Tie storage choice to access pattern, correctness needs, latency targets, and operational burden.

### 5.1 Database Fundamentals
- Structured vs semi-structured vs unstructured data.
- Schema-on-write vs schema-on-read.
- Row store vs column store intuition.
- Metadata vs blob separation.
- Soft delete vs hard delete and their operational consequences.

### 5.2 ACID Properties
- Atomicity, consistency, isolation, durability as engineering guarantees, not just definitions.
- Which user flows need ACID and which do not.
- Why strong correctness surfaces usually justify transactional cost.
- ACID does not automatically mean globally consistent distributed behavior.

### 5.3 ACID vs BASE
- BASE as a practical tradeoff for availability and scale.
- Eventually convergent systems vs immediately correct systems.
- Senior-level expectation: choose based on business semantics, not ideology.

### 5.4 SQL Databases
- Tables, foreign keys, joins, transactional guarantees.
- Normalization vs denormalization.
- Materialized views and precomputed read models.
- SQL remains the default answer unless scale / access pattern argues otherwise.

### 5.5 Database Indexing (Deep Dive)
- Primary vs secondary indexes.
- Composite indexes and column-order effects.
- Covering indexes.
- Point lookup vs range scan vs sort support.
- Index maintenance cost on write-heavy systems.
- Senior-level depth: explain how query pattern drives index design.

### 5.6 Database Replication
- Single-leader replication.
- Multi-leader replication.
- Leaderless replication awareness.
- Sync vs async replication.
- Read replicas and stale reads.
- Failover, failback, and replica promotion risk.

### 5.7 Database Sharding / Partitioning
- Why one machine stops being enough.
- Range-based vs hash-based partitioning.
- Shard-key design and hotspot risk.
- Rebalancing and resharding cost.
- Cross-shard queries and cross-shard transactions.
- Senior-level depth: explain what breaks during shard-key mistakes.

### 5.8 MVCC (Multi-Version Concurrency Control)
- Readers do not block writers.
- Snapshot reads and snapshot isolation.
- Vacuum / cleanup cost awareness.
- Why MVCC helps concurrency but does not solve every isolation anomaly.

### 5.9 Change Data Capture (CDC)
- CDC as a way to propagate DB changes into downstream systems.
- Log-based CDC vs polling-based CDC.
- Outbox + CDC for safe event publication.
- Use cases: search indexing, analytics, cache invalidation, read-model updates.

### 5.10 Key-Value Stores
- Access pattern: key -> value, very fast point lookup.
- Great for caching, sessions, simple metadata, counters.
- Weak for rich ad hoc querying.
- Senior-level depth: distinguish a cache from a durable KV system.

### 5.11 Document Stores
- Flexible schema and nested objects.
- Good fit when entity is read and written as a single document.
- Denormalization can reduce joins but increase update complexity.
- Query flexibility varies a lot by product.

### 5.12 Column-Family Stores (Wide-Column)
- Partition key plus clustering key mental model.
- Very high write throughput and horizontal scale.
- Query model is access-pattern-driven, not join-driven.
- LSM-tree alignment with write-heavy workloads.

### 5.13 Search Engines
- Inverted index model.
- Full-text query, ranking, stemming, tokenization.
- Search index is not the source of truth.
- Refresh lag and indexing delay are normal.

### 5.14 Graph Databases
- Useful when relationship traversal is the dominant access pattern.
- Social graphs, recommendation graph traversals, fraud networks.
- Not every relational workload should become a graph database.

### 5.15 Object / Blob Storage
- Files, images, videos, backups, large documents.
- Pre-signed URL pattern for direct client upload / download.
- Multipart upload, resumable upload, and storage tiers.
- Metadata in DB, bytes in object store.

### 5.16 NewSQL
- Goal: SQL ergonomics plus distributed scale / stronger consistency.
- Spanner / CockroachDB / Yugabyte awareness.
- Senior-level depth: know when operational simplicity of one distributed SQL layer is worth the cost.

### 5.17 Connection Pooling
- DB connections are expensive.
- Pool size, saturation, and timeout behavior matter.
- Connection storms can take down a DB before query load does.

### 5.18 Read / Write Splitting
- Writes go to primary; reads go to replicas.
- Replica lag creates stale-read problems.
- Read-your-writes routing exceptions may be needed.
- Senior-level depth: do not casually promise read-your-writes on replica-based architectures.

### 5.19 Cursor-Based Pagination vs Offset Pagination
- Offset gets slower and less stable with large datasets.
- Cursor / keyset pagination scales better and is more stable under concurrent writes.
- Senior-level expectation: know when cursor pagination is mandatory.

### 5.20 OLTP vs OLAP
- OLTP: low-latency transactional workload.
- OLAP: large scans and aggregations over historical data.
- Split serving DB from analytical warehouse.
- CDC into warehouse is a common bridge.

### 5.20a OLAP Internals (SDE-3 depth)
- Columnar storage format: why storing by column beats row-store for analytical scans.
- Parquet / ORC / Capacitor — what they are and why they compress so well (similar values grouped together).
- Predicate pushdown: filter at the storage layer before loading data into memory.
- Vectorized execution: process columns in batches instead of row-by-row.
- Partitioning and clustering: BigQuery partition pruning, Snowflake micro-partitions, Redshift sort keys.
- Data lake vs data warehouse distinction — when each makes sense.
- ClickHouse MergeTree: columnar + sorted + merge-on-read — how it achieves near-real-time analytics.
- Apache Druid: real-time OLAP on event streams — ingestion vs query path.
- Materialized views and pre-aggregation: when to precompute instead of scanning raw data.
- Senior-level depth: explain the full data pipeline — prod DB → CDC/ETL → warehouse → dashboard — and where each component can fail.

### 5.21 Geospatial Indexing
- Geohash, quadtree, S2 awareness.
- Nearby lookup vs moving-object update tradeoffs.
- Write-heavy geo workloads are different from static map-tile systems.

### 5.22 Distributed Transactions (2PC and Saga)
- 2PC for strong coordination, with blocking and availability cost.
- Saga for long-running workflows with compensating actions.
- Outbox pattern as the practical default for DB write + event publish.
- Senior-level depth: compare these explicitly in payment / booking systems.

### 5.23 Choosing the Right Database
- Choose from access pattern first.
- Then layer in correctness, latency, scale, operational burden, and team familiarity.
- Senior-level expectation: compare two realistic choices and say what you are giving up.

### 5.24 Data Modeling (Schema Design from Requirements)
- Start from reads and writes, not from entities in the abstract.
- Model hot paths first.
- Think about history, audit, soft delete, tenant boundaries, and migration cost.
- Strong SDE-3 answer: explain why this schema will still work at 10x, and how you would evolve it if it does not.
