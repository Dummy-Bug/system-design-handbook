## Phase 4 — Storage & Databases

> HLD relevance: Every case study has a data storage layer.
> This phase teaches you how to pick the right DB and design its schema, replication, and sharding.

### SDE-2 Depth Bar For This Phase
- Know the major storage families and the workloads they fit.
- Be able to reason about indexing, replication, sharding, and distributed transactions.
- Compare SQL, NoSQL, search, blob storage, and analytical systems using access patterns and correctness needs.
- Explain how schema and data-model choices affect scale, latency, and migration difficulty.

### 3.1 Database Fundamentals
- Structured vs unstructured vs semi-structured data
- Schema-on-write vs schema-on-read
- Storage engines — how databases store data on disk (row-oriented vs column-oriented)
- Currency must never be stored as float or double — use integer (cents) or DECIMAL
- Soft deletes vs hard deletes — deleted_at column vs DELETE row, audit trail, tradeoffs

### 3.2 ACID Properties
- Atomicity — all or nothing
- Consistency — valid state to valid state
- Isolation — concurrent transactions don't interfere
- Durability — committed data survives failures
- ACID vs BASE — when you can relax guarantees for performance

### 3.3 SQL Databases
- Relational model — tables, rows, foreign keys
- Normalization (1NF–3NF) — remove duplication; know when to denormalize
- Denormalization — trade storage for read speed (news feed, type-ahead)
- Joins — inner, left, right, full outer
- Views — virtual tables for read simplification
- Materialized views — precomputed, cached on disk, used for expensive aggregations

### 3.4 Database Indexing
- Query optimization — how indexes speed up reads
- Why indexes — O(n) table scan vs O(log n) index lookup
- Composite index — leftmost prefix rule, column order matters
- Covering index — query satisfied entirely from index, no table lookup
- When NOT to index — low-cardinality columns, write-heavy tables
- B+ Tree — what it is, how it's structured, why databases prefer it, how range scans work
- LSM Tree — write-optimized (MemTable → SSTable → compaction), used in Cassandra, RocksDB
- Hash index — O(1) equality only, no range queries

### 3.5 Database Replication
- Primary-Replica — all writes to primary, reads from replicas
- Multi-Primary — multiple write nodes, conflict resolution needed
- Sync vs Async replication — durability vs latency tradeoff
- Replication lag — read replicas can serve stale data
- Read replicas — offload read traffic
- Failover — promoting a replica when primary dies
- Split-brain — two nodes both think they're primary, the danger

### 3.6 Database Sharding / Partitioning
- Why shard — single node can't hold all data or handle all writes
- Vertical partitioning — split wide table into narrower tables
- Horizontal sharding — split rows across nodes
- Shard key selection — must be high cardinality, evenly distributed, immutable
- Range-based sharding — easy range queries, hotspot risk (time-based keys)
- Hash-based sharding — uniform distribution, bad for range queries
- Directory-based sharding — flexible lookup table, extra hop
- Consistent hashing for sharding — minimal reshuffling when nodes change
- Cross-shard queries — expensive, avoid by denormalizing or co-locating
- Hotspot problem — celebrity row or timestamp key hammers one shard

### 3.7 MVCC (Multi-Version Concurrency Control)
- Readers don't block writers, writers don't block readers — why this matters at scale
- Each transaction sees a consistent snapshot of the DB at transaction start
- Directly applies to: hotel reservation, auction, ticket booking case studies

### 3.8 Key-Value Stores
- Data model — key → value
- Use cases — sessions, caching, leaderboards, rate limiting, feature flags
- Redis — single-threaded event loop, in-memory, extremely fast
- DynamoDB — managed, consistent hashing, tunable consistency

### 3.9 Document Stores
- Data model — JSON documents, nested objects, arrays, dynamic schema
- MongoDB — replica sets, sharding, write concern levels
- Embedding vs referencing — embedding for reads, referencing for writes
- Use cases — product catalogs, user profiles, content (CMS), event data

### 3.10 Column-Family Stores (Wide-Column)
- Data model — rows with dynamic columns, grouped in column families
- Cassandra architecture — consistent hashing ring, peer-to-peer, no SPOF
  - Partition key — determines which node holds data
  - Clustering key — sort order within partition
  - Replication factor + consistency levels — ONE, QUORUM, ALL
  - Query-first data modeling — design tables around query patterns
- Bigtable — Google's wide-column store (HBase is open-source equivalent)
  - Difference in Cassandra and Bigtable is good enough for SDE-2
- Use cases — chat message history, IoT/time-series, write-heavy event logs

### 3.11 Search Engines
- Inverted index — maps terms to document IDs, the core data structure
- How Elasticsearch works — shards (write), replicas (read), nodes
- Indexing pipeline — tokenization, stemming, normalization
- Ranking — TF-IDF, BM25
- Why not just use DB LIKE query — no ranking, no stemming, full table scan

### 3.12 Graph Databases
- Data model — nodes, edges, properties
- When SQL joins become unacceptably expensive — 3+ hop relationships
- Neo4j — Cypher query language
- Use cases — social networks, fraud detection, recommendations

### 3.13 Object / Blob Storage
- Object storage model — flat namespace, buckets, keys, metadata
- Amazon S3 — storage classes (Standard, Infrequent Access, Glacier), versioning
- Pre-signed URLs — give temporary access without exposing credentials
- Multipart upload — split large files, parallel upload, resumable
- Content-addressable storage — hash of content = key, enables deduplication
- Use cases — Dropbox/Drive (files), YouTube (videos), Gmail (attachments), static assets

### 3.14 NewSQL (Awareness Level)
- Problem it solves — SQL semantics + horizontal scaling
- Google Spanner, Amazon Aurora, Azure Cosmos DB — know what they are and when to mention
- When to mention — global systems needing strong consistency at scale

### 3.15 Connection Pooling
- Why raw DB connections are expensive — TCP handshake + auth + memory per connection
- Connection pool — reuse a fixed set of open connections across many app threads
- PgBouncer (PostgreSQL), HikariCP (Java), RDS Proxy (Amazon)

### 3.16 Read/Write Splitting
- Route all writes to primary, all reads to read replicas at the application layer
- Trade-off — replica lag means reads may be slightly stale
- Fix — route a user's own reads to primary for a short window after they write

### 3.17 Cursor-based Pagination vs Offset Pagination
- Offset pagination — LIMIT 20 OFFSET 10000 — simple but breaks at scale
- Cursor-based pagination — "give me 20 items after this ID/timestamp"
  - Stable under concurrent writes, O(1) with an index
  - Trade-off — no random page access, only next/prev
- Use cursor pagination for feeds, timelines, infinite scroll at scale

### 3.18 OLTP vs OLAP
- OLTP — operational DB, low-latency reads/writes, short transactions (PostgreSQL, MySQL)
- OLAP — analytical DB, large aggregations, full scans (Redshift, BigQuery, Snowflake)
- Never run analytics queries against your production OLTP DB at scale
- Pattern — CDC or ETL pipeline copies OLTP data → data warehouse

### 3.19 Geospatial Indexing
- The problem — "find all drivers within 2km" — standard B+Tree cannot answer this
- Geohash — encode lat/lng as a base32 string, prefix = proximity
  - Edge case: cells on opposite sides of boundary → always query 8 surrounding cells too
- Quadtree — recursively split 2D space into 4 quadrants, good for dynamic driver locations
- PostGIS — PostgreSQL extension for native geospatial queries
- Practical pattern — store raw lat/lng (for display) + Geohash (for proximity indexing)

### 3.20 Distributed Transactions (2PC & Saga)
- The problem — ACID gives you transactions within one DB; what about across two services?
- 2-Phase Commit (2PC)
  - Phase 1 (Prepare) — coordinator asks all participants "can you commit?" — each locks resources
  - Phase 2 (Commit/Abort) — if all voted yes, coordinator sends commit; if any voted no, abort
  - Used by distributed SQL engines for cross-shard transactions
  - Verdict: strong consistency, but high latency and availability risk
- Saga pattern — alternative to 2PC for microservices
  - Sequence of local transactions, each publishing an event/message
  - On failure: execute compensating transactions to undo previous steps
  - Choreography — decentralized, each service reacts to events
  - Orchestration — central saga orchestrator directs each step
  - Trade-off: eventual consistency, no atomicity across services
- When 2PC, when Saga?
  - 2PC when: you need true atomicity and can afford latency
  - Saga when: you need availability and can tolerate brief inconsistency

### 3.21 Choosing the Right Database
- SQL — complex queries, joins, strong consistency, financial data
- Key-Value — ultra-fast simple lookups, caching, sessions, leaderboards
- Document — flexible schema, nested data, product catalogs, profiles
- Column-family — write-heavy, time-ordered, massive scale (Cassandra)
- Graph — relationship traversal as primary operation
- Search — full-text, ranked results, faceting
- Blob/Object — large unstructured files, media, backups

### 3.22 Data Modeling (Schema Design from Requirements)
- Process — requirements → entities → relationships → access patterns → schema
- Normalize first, denormalize with justification
- Embedding vs referencing (Document DBs) — embed for reads, reference for writes
- Many-to-many — junction table (SQL), denormalize both sides (NoSQL)
- Modeling for access patterns (Cassandra) — one table per query pattern
- Common schema patterns — user + profile, user → posts, followers, event/activity log
- Red flags — no PK discussion, auto-increment as shard key, derived data without invalidation
