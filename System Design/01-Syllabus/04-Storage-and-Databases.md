## Phase 4 — Storage & Databases

> HLD relevance: Every case study has a data storage layer.
> This phase teaches you how to pick the right DB and design its schema, replication, and sharding.

### 3.1 Database Fundamentals
- Structured vs unstructured vs semi-structured data
- Schema-on-write vs schema-on-read
- Storage engines — how databases store data on disk (row-oriented vs column-oriented)
- **Currency must never be stored as float or double** — binary floating point cannot represent 0.1 exactly; `0.1 + 0.2 = 0.30000000000000004` in IEEE 754. Always store money as integers (cents: $9.99 → 999) or use a Decimal/Numeric type. See `Fundamentals/Binary Number Rounding.md` for the full explanation. Applies to: Payment System, Banking Ledger, Auction, Stock Broker case studies.

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
- Query optimization — how indexes speed up reads

### 3.4 Database Indexing (Deep Dive)
- Why indexes — O(n) table scan vs O(log n) index lookup
- B+ Tree — how range scans work, why databases prefer it
- LSM Tree — write-optimized (MemTable → SSTable → compaction), used in Cassandra, RocksDB
- Hash index — O(1) equality only, no range queries
- Composite index — leftmost prefix rule, column order matters
- Covering index — query satisfied entirely from index, no table lookup
- When NOT to index — low-cardinality columns, write-heavy tables

### 3.5 Database Replication
- Primary-Replica — all writes to primary, reads from replicas
- Multi-Primary — multiple write nodes, conflict resolution needed
- Sync vs Async replication — durability vs latency tradeoff
- Replication lag — read replicas can serve stale data
- Read replicas — offload read traffic (news feed reads, analytics)
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
- Resharding — live data migration nightmare, plan ahead
- Cross-shard queries — expensive, avoid by denormalizing or co-locating
- Hotspot problem — celebrity row or timestamp key hammers one shard

### 3.7 MVCC (Multi-Version Concurrency Control)
- Readers don't block writers, writers don't block readers
- Each transaction sees a snapshot of the DB at transaction start
- How PostgreSQL implements it — xmin/xmax version stamps per row
- Vacuum process — garbage collects old row versions
- Write skew — MVCC doesn't prevent it, needs SERIALIZABLE
- Directly applies to: hotel reservation, auction, ticket booking case studies

### 3.8 Change Data Capture (CDC)
- Stream database changes as events without polling
- Use cases — sync search index, invalidate cache, populate analytics, event sourcing
- Log-based CDC — reads WAL/binlog (Debezium), minimal DB overhead
- Outbox pattern — write event to same DB transaction, CDC picks it up
- Where it fits — notification system, search (YouTube/Google indexing), real-time analytics

### 3.9 Key-Value Stores
- Data model — key → value
- Use cases — sessions, caching, leaderboards, rate limiting, feature flags
- Redis — single-threaded event loop, in-memory, extremely fast
  - String — counters, tokens, simple KV
  - List — queues, activity feeds, recent items
  - Set — unique members, tags, social connections
  - Sorted Set — leaderboards, rate limiting windows, priority queues
  - Hash — user profiles, object fields
  - HyperLogLog — approximate unique count (DAU, unique views)
  - Bitmap — per-user feature flags, daily active tracking
  - Stream — append-only log, consumer groups (mini Kafka)
  - Persistence — RDB snapshot vs AOF (append-only file)
  - Redis Sentinel — high availability, automatic failover
  - Redis Cluster — horizontal sharding via hash slots
- DynamoDB — managed, consistent hashing, tunable consistency, global tables
- Memcached — simple, multi-threaded, no persistence, pure caching

### 3.10 Document Stores
- Data model — JSON documents, nested objects, arrays, dynamic schema
- MongoDB — replica sets, sharding, write concern levels
- Embedding vs referencing — embedding for reads, referencing for writes
- Use cases — product catalogs, user profiles, content (CMS), event data
- Limitation — no cross-document joins, denormalize intentionally

### 3.11 Column-Family Stores (Wide-Column)
- Data model — rows with dynamic columns, grouped in column families
- Cassandra architecture — consistent hashing ring, peer-to-peer, no SPOF
  - Partition key — determines which node holds data
  - Clustering key — sort order within partition
  - Replication factor + consistency levels — ONE, QUORUM, ALL
  - Write path — CommitLog → MemTable → SSTable flush
  - Read path — MemTable → Bloom filter check → SSTable scan
  - Compaction — merging SSTables, reclaiming space for tombstones
  - Query-first data modeling — design tables around query patterns
- Use cases — chat message history, IoT/time-series, write-heavy event logs, analytics

### 3.12 Search Engines
- Inverted index — maps terms to document IDs, the core data structure
- How Elasticsearch works — shards (write), replicas (read), nodes
- Indexing pipeline — tokenization, stemming, normalization
- Ranking — TF-IDF, BM25
- Why not just use DB LIKE query — no ranking, no stemming, full table scan
- Where it fits — web search, product search, log search, type-ahead

### 3.13 Graph Databases
- Data model — nodes, edges, properties
- When SQL joins become unacceptably expensive — social graph traversal, 3+ hop relationships
- Neo4j — Cypher query language
- Use cases — social networks (followers/following), fraud detection, recommendations, knowledge graphs

### 3.14 Object / Blob Storage
- Object storage model — flat namespace, buckets, keys, metadata
- Amazon S3 — storage classes (Standard, Infrequent Access, Glacier), versioning
- Pre-signed URLs — give temporary access without exposing credentials
- Multipart upload — split large files, parallel upload, resumable
- Use cases — Dropbox/Drive (files), YouTube (videos), Gmail (attachments), static assets
- Content-addressable storage — hash of content = key, enables deduplication

### 3.15 NewSQL
- Problem it solves — SQL semantics + horizontal scaling
- Google Spanner — globally distributed, TrueTime for external consistency
- CockroachDB — distributed SQL, MVCC, Raft per range
- When to mention — global systems needing strong consistency at scale (stock broker, banking)

### 3.16 Choosing the Right Database
- SQL — complex queries, joins, strong consistency, financial data
- Key-Value — ultra-fast simple lookups, caching, sessions, leaderboards
- Document — flexible schema, nested data, product catalogs, profiles
- Column-family — write-heavy, time-ordered, massive scale (Cassandra)
- Graph — relationship traversal as primary operation
- Search — full-text, ranked results, faceting
- Blob/Object — large unstructured files, media, backups
- Apply this in every case study data model section
