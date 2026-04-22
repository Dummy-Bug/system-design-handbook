# Storage and Databases

## Database Fundamentals
- Structured vs unstructured vs semi-structured data
- Schema-on-write vs schema-on-read
- Storage engines — row-oriented vs column-oriented
- Soft deletes vs hard deletes — deleted_at column, audit trail, tombstone implications
- Currency must never be stored as float or double — use integer (cents) or DECIMAL

## ACID Properties
- Atomicity — all or nothing
- Consistency — valid state to valid state
- Isolation — concurrent transactions don't interfere
- Durability — committed data survives failures
- ACID vs BASE — when you can relax guarantees for performance

## SQL Databases
- Relational model — tables, rows, foreign keys
- Normalization (1NF–3NF) — remove duplication
- Denormalization — trade storage for read speed
- Joins — inner, left, right, full outer
- Views — virtual tables for read simplification
- Materialized views — precomputed, cached on disk, used for expensive aggregations

## Database Indexing
- Why indexes — O(n) table scan vs O(log n) index lookup
- Composite index — leftmost prefix rule, column order matters
- Covering index — query satisfied entirely from index, no table lookup
- When NOT to index — low-cardinality columns, write-heavy tables
- B+ Tree — structure, how range scans work, why databases prefer it
- **B+ Tree internals — page structure (typically 4–16 KB pages), page splits on insert, how splits propagate up the tree**
- **Write amplification in B+ Tree — a single small insert can rewrite an entire page (4–16 KB) due to page splits**
- LSM Tree — write-optimized (MemTable → SSTable → compaction), used in Cassandra, RocksDB
- **LSM Tree internals — MemTable (in-memory write buffer), immutable SSTable files on disk, compaction merges SSTables**
- **Compaction strategies — leveled compaction (bounded space, more I/O), tiered compaction (less I/O, more space), size-tiered**
- **Write amplification in LSM — a single write may be compacted 3–5 times across levels, but each write is sequential (fast on SSD)**
- **B+ Tree vs LSM — B+ Tree for read-heavy (no read amplification), LSM for write-heavy (sequential writes, compaction cost)**
- Hash index — O(1) equality only, no range queries

## Database Replication
- Primary-Replica — all writes to primary, reads from replicas
- Multi-Primary — multiple write nodes, conflict resolution needed
- Sync vs async replication — durability vs latency tradeoff
- Replication lag — read replicas can serve stale data
- Failover — promoting a replica when primary dies
- Split-brain — two nodes both think they're primary, the danger
- Read-your-own-writes — route user's own reads to primary briefly after write

## Database Sharding
- Why shard — single node can't hold all data or handle all writes
- Vertical partitioning — split wide table into narrower tables
- Horizontal sharding — split rows across nodes
- Shard key selection — high cardinality, evenly distributed, immutable
- Range-based sharding — easy range queries, hotspot risk
- Hash-based sharding — uniform distribution, bad for range queries
- Directory-based sharding — flexible lookup table, extra hop
- Consistent hashing for sharding — minimal reshuffling when nodes change
- Cross-shard queries — expensive, avoid by denormalizing or co-locating
- Hotspot problem — celebrity row or timestamp key hammers one shard

## **Data Migration at Scale**
- **Why it's hard — production never stops, users read and write the entire time**
- **Dual-write pattern — write to both old and new system simultaneously during migration**
  - **Problem: one write can fail, data diverges → need reconciliation job**
  - **Better alternative: CDC from old DB to populate new DB**
- **Backfill strategy — migrate historical data in batches using cursor-based scan (never OFFSET)**
  - **Rate-limit the backfill to avoid overwhelming either database**
  - **Track checkpoint (last migrated ID) — safe to restart on failure**
  - **Run on read replica of old DB, not primary**
- **Shadow reads — route copy of live read traffic to new system, compare responses, don't serve to users**
  - **Once discrepancy rate → 0, switch reads to new system**
- **Full migration playbook — Backfill → CDC/dual-write → Shadow reads → Cutover**
- **Rollback plan — keep old system writable for N days after cutover**

## **Schema Migration on Live Tables**
- **Never run ALTER TABLE with a lock on a large production table — blocks all writes**
- **gh-ost (MySQL) — copies data to new table in background, minimal locking**
- **pg_repack (PostgreSQL) — same concept, online table rebuild**
- **Expand-and-contract pattern:**
  - **Expand: add new column (nullable, no default required for existing rows)**
  - **Backfill: populate new column for existing rows in batches**
  - **Contract: deploy code that reads new column, then drop old column**

## MVCC (Multi-Version Concurrency Control)
- Readers don't block writers, writers don't block readers
- Each transaction sees a consistent snapshot of the DB at transaction start
- **Write skew — MVCC doesn't prevent it, needs SERIALIZABLE isolation**
- **How MVCC implements snapshot isolation — version chains per row, transaction ID watermarks**
- Directly applies to: hotel reservation, auction, ticket booking

## **Change Data Capture (CDC)**
- **What CDC is — stream every database change (insert, update, delete) as an event**
- **Why polling doesn't work at scale — DB load, misses deletes, high latency**
- **Log-based CDC — reads WAL/binlog directly (Debezium + Kafka), zero polling overhead**
  - **How it works — Debezium connects as a replica, reads binary log, emits change events**
  - **What it captures — before image, after image, operation type, transaction ID**
- **Outbox pattern — write event to outbox table in same DB transaction as the business change**
  - **CDC picks up outbox table changes and publishes to Kafka**
  - **Solves dual-write problem — DB write and event publish are atomic**
- **Inbox pattern — consumer stores message ID before processing, skips if already seen**
- **CDC vs event sourcing — CDC captures changes to existing DB, event sourcing IS the DB**
- **Use cases — sync search index, invalidate cache, populate analytics, microservice decoupling**

## Key-Value Stores
- Data model — key → value
- Use cases — sessions, caching, leaderboards, rate limiting, feature flags
- Redis — single-threaded event loop, in-memory, extremely fast
- DynamoDB — managed, consistent hashing, tunable consistency

## Document Stores
- Data model — JSON documents, nested objects, dynamic schema
- MongoDB — replica sets, sharding, write concern levels
- Embedding vs referencing — embedding for reads, referencing for writes
- Use cases — product catalogs, user profiles, content

## Column-Family Stores (Wide-Column)
- Data model — rows with dynamic columns grouped in column families
- Cassandra — consistent hashing ring, peer-to-peer, no SPOF
  - Partition key — determines which node holds data
  - Clustering key — sort order within partition
  - Replication factor + consistency levels — ONE, QUORUM, ALL
- **Cassandra write path — CommitLog (WAL for crash safety) → MemTable (in-memory) → SSTable flush (immutable on-disk)**
- **Cassandra read path — check MemTable first → Bloom filter (is key in this SSTable?) → SSTable scan (may read multiple SSTables)**
- **Compaction — merges SSTables, reclaims space from tombstones, keeps read amplification low**
- **Tombstones — soft deletes in Cassandra. A delete writes a tombstone marker. Compaction eventually removes it. Tombstone accumulation can cause read performance issues.**
- **Query-first data modeling — design tables around query patterns, not entities**
- **Bigtable — Google's wide-column store, row key + column family + qualifier + timestamp**
  - **Tablet server — serves a range of rows (tablet), auto-splits on size**
  - **Minor compaction — flush MemTable to SSTable**
  - **Major compaction — merge all SSTables for a tablet, remove deleted cells**
  - **Row key design is everything — determines data locality and access pattern**
  - **HBase is the open-source equivalent**

## Search Engines
- Inverted index — maps terms to document IDs, the core data structure
- Elasticsearch — shards (write), replicas (read), nodes
- Indexing pipeline — tokenization, stemming, normalization
- Ranking — TF-IDF, BM25
- Why not DB LIKE query — no ranking, no stemming, full table scan

## Graph Databases
- Data model — nodes, edges, properties
- When SQL joins become expensive — 3+ hop relationships, social graph traversal
- Neo4j — Cypher query language
- Use cases — social networks, fraud detection, recommendations

## Object / Blob Storage
- Object storage model — flat namespace, buckets, keys, metadata
- S3 — storage classes (Standard, Infrequent Access, Glacier), versioning
- Pre-signed URLs — temporary access without exposing credentials
- Multipart upload — split large files, parallel upload, resumable
- Content-addressable storage — hash of content = key, enables deduplication
- Use cases — files, videos, attachments, static assets

## NewSQL
- Problem it solves — SQL semantics + horizontal scaling
- **Google Spanner — globally distributed SQL, TrueTime for external consistency**
  - **TrueTime — GPS + atomic clocks, uncertainty window [earliest, latest]**
  - **Commit wait — Spanner waits out the uncertainty window before committing to guarantee ordering**
  - **2PC with Paxos groups — each shard is a Paxos group, cross-shard writes use 2PC between groups**
- Amazon Aurora — distributed SQL, storage-compute separation
- Azure Cosmos DB — multi-model, tunable consistency levels

## Connection Pooling
- Why raw DB connections are expensive — TCP handshake + auth + memory per connection
- Connection pool — reuse fixed set of open connections
- PgBouncer (PostgreSQL), HikariCP (Java), RDS Proxy (Amazon)

## Read/Write Splitting
- Route all writes to primary, all reads to replicas at application layer
- Trade-off — replica lag means reads may be slightly stale
- Read-your-own-writes violation — route user's own reads to primary briefly after write

## Cursor-Based Pagination vs Offset
- Offset — LIMIT 20 OFFSET 10000 — full table scan, unstable under concurrent writes
- Cursor-based — "give me 20 items after this ID/timestamp" — O(1) with index, stable
- Use cursor for feeds, timelines, infinite scroll at scale

## OLTP vs OLAP
- OLTP — low-latency reads/writes, short transactions (PostgreSQL, MySQL, DynamoDB)
- OLAP — large aggregations, full scans (Redshift, BigQuery, Snowflake)
- Never run analytics on your production OLTP DB
- Pattern — CDC or ETL pipeline copies OLTP → data warehouse

## Geospatial Indexing
- The problem — "find all drivers within 2km" — B+ Tree can't answer this
- Geohash — encode lat/lng as string, prefix = proximity, edge case at cell boundaries
- **S2 Geometry (Google) — divides sphere into cells using Hilbert space-filling curve**
  - **Each cell has a 64-bit integer ID — nearby cells have numerically close IDs**
  - **Cell hierarchy — level 0 (Earth) to level 30 (1cm²), each level splits into 4**
  - **Better than Geohash — uniform area coverage, no edge distortion at poles**
  - **Used in Google Maps, Google Earth, Uber**
  - **Mentioning S2 in a Google interview is a strong signal**
- Quadtree — recursively split 2D space into 4 quadrants, good for dynamic data (drivers)
- PostGIS — PostgreSQL extension, ST_DWithin for proximity queries

## Distributed Transactions
- Problem — ACID gives transactions within one DB, what about across two services?
- 2PC (Two-Phase Commit)
  - Phase 1 Prepare — coordinator asks all participants "can you commit?", each locks resources
  - Phase 2 Commit/Abort — all voted yes → commit, any voted no → abort
  - **Blocking protocol problem — if coordinator crashes after Phase 1, participants hold locks indefinitely (in-doubt transaction)**
  - **No automatic resolution — a new coordinator must query surviving participants for their vote**
  - **Used by Spanner (with TrueTime bounding uncertainty), some distributed SQL engines**
  - **Verdict — strong consistency, high latency, availability risk. Avoid in high-throughput systems.**
- Saga pattern — alternative to 2PC for microservices
  - Sequence of local transactions, each publishes event/message
  - On failure: compensating transactions undo previous steps
  - Choreography — decentralized, each service reacts to events
  - Orchestration — central saga orchestrator directs each step
  - Trade-off: eventual consistency, no atomicity across services
  - Compensating transactions must be idempotent

## Choosing the Right Database
- SQL — complex queries, joins, strong consistency, financial data
- Key-Value — ultra-fast simple lookups, caching, sessions, leaderboards
- Document — flexible schema, nested data, product catalogs, profiles
- Column-family — write-heavy, time-ordered, massive scale
- Graph — relationship traversal as primary operation
- Search — full-text, ranked results, faceting
- Blob/Object — large unstructured files, media, backups

## Data Modeling
- Process — requirements → entities → relationships → access patterns → schema
- Normalize first, denormalize with justification
- Embedding vs referencing in document DBs — embed for reads, reference for writes
- Many-to-many — junction table (SQL), denormalize both sides (NoSQL), native edge (graph)
- Query-first design for Cassandra — one table per query pattern
- Red flags — no PK discussion, auto-increment as shard key, derived data without invalidation
