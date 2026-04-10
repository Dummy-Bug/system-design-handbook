## Phase 5 - Storage and Databases

> HLD relevance: this phase is about why a storage choice works, not just which storage name to say.
> SDE-3 candidates should be comfortable reasoning about storage engines, replication, partitioning, and migration cost.

### 5.1 Database fundamentals
- structured vs semi-structured vs unstructured data
- schema-on-write vs schema-on-read
- row store vs column store
- metadata vs blob separation

### 5.2 ACID and BASE
- what ACID really buys you
- where BASE is acceptable
- why the business meaning of the data decides the answer

### 5.3 SQL systems
- relational modeling
- normalization vs denormalization
- joins and foreign keys
- materialized views
- when SQL should still be the default

### 5.4 Indexing
- primary vs secondary index
- composite index and column order
- covering index
- too many indexes hurting writes
- range-scan vs point-lookup thinking

### 5.5 Storage engines
- B+ tree
- LSM tree
- write amplification, read amplification, space amplification
- compaction and background work
- why engine choice changes workload fit

### 5.6 Replication
- single leader
- multi-leader
- leaderless
- sync vs async
- lag, stale reads, and failover consequences

### 5.7 Sharding and rebalancing
- shard key design
- hot partitions
- consistent hashing
- resharding
- cross-shard queries and transactions

### 5.8 Object and blob storage
- media and large file storage
- pre-signed URLs
- multipart upload
- chunking and content-addressable storage awareness

### 5.9 Specialized stores
- key-value
- document
- search index
- time-series
- OLAP warehouse

### 5.10 Data modeling at scale
- access-pattern-first schema design
- ownership boundaries
- soft delete vs hard delete
- auditability and history

### 5.11 Data migration and evolution
- expand / migrate / contract
- backfills
- CDC during migration
- dual-write risks
- shadow reads before cutover

