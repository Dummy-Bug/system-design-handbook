
> [!info] Know the throughput ceiling of each database before you design around it
> "Can a single Postgres instance handle this?" — you need a number to answer that, not a guess.


## PostgreSQL / MySQL (relational, SSD-backed)

```
Single instance read QPS:    10,000 – 50,000 reads/sec    (indexed queries, warm cache)

Single instance write QPS:   5,000  – 10,000 writes/sec   (INSERT/UPDATE with WAL flush)


Read latency (indexed):      1 – 5 ms
Write latency:               5 – 10 ms

Max practical storage:       ~10 TB on one machine before ops gets painful

Connection limit:            ~500–1000 connections (use PgBouncer to pool)
```

**When one Postgres instance is not enough:**
- Read QPS > 50k → add read replicas
- Write QPS > 10k → shard
- Storage > 10TB → shard

**What eats your read QPS budget fast:**
- Complex joins across large tables
- Full table scans (missing index)
- Queries that return large result sets
- High connection count without pooling

Simple point lookups by primary key (like URL shortener short_code → long_url) are at the fast end — closer to 50k/sec. Complex analytical queries are at the slow end.

---

## Redis (in-memory key-value)

```
Single node read throughput:   100,000 – 500,000 ops/sec
Single node write throughput:  100,000 – 500,000 ops/sec

Read latency:                  0.1 – 0.5 ms
Write latency:                 0.1 – 0.5 ms

Memory per node:               64 GB – 256 GB (typical server)

Cluster:                       scales horizontally, each node owns a shard
Pipeline throughput:           up to 1M+ ops/sec (batch commands)
```

**Memory overhead per key:**
Redis doesn't just store your data — it stores metadata per key. Budget ~50–100 bytes overhead per key on top of the actual value.

```
Example: URL shortener cache entry
  key:   short_code (6 bytes)
  value: long_url (~200 bytes)
  overhead: ~70 bytes
  total per entry: ~280 bytes → rounds to ~500 bytes with all Redis internals
```

**When Redis becomes the bottleneck:**
At 500k ops/sec per node, Redis is rarely the bottleneck for reads. It becomes a concern for writes at very high scale — which is why app servers batch-fetch keys and cache locally.

**Redis data structure throughput varies:**
```
GET/SET (strings):      fastest — 500k ops/sec
LPOP/RPUSH (lists):     ~200–400k ops/sec
ZADD/ZRANGE (sorted sets): ~100–200k ops/sec (more CPU per op)
```

---

## MongoDB (document store)

```
Single node read QPS:    50,000 – 100,000 reads/sec    (indexed)
Single node write QPS:   20,000 – 50,000 writes/sec
Read latency (indexed):  1 – 5 ms
Write latency:           2 – 10 ms
```

Mongo's write throughput is higher than Postgres for document writes because it uses a more relaxed durability model by default and its document model avoids multi-table joins. But for strict ACID with sync WAL flushes, it approaches Postgres numbers.

---

## Cassandra (wide-column, LSM-tree)

```
Write throughput per node:   100,000 – 200,000 writes/sec
Read throughput per node:    50,000  – 80,000  reads/sec

Write latency:               0.5 – 2 ms    ← writes go to memtable (RAM) first

Read latency:                5   – 10 ms   ← may need to check multiple SSTables
```

**Why Cassandra writes are fast:**
Cassandra uses an LSM tree. Writes go to an in-memory buffer (memtable) first, then flush to disk as immutable SSTables. There's no random write I/O on the critical path. This is why Cassandra dominates for write-heavy workloads.

**Why Cassandra reads are slower than writes:**
A read may need to check multiple SSTables (data spreads across levels over time). Bloom filters help avoid most unnecessary SSTable checks, but reads are still slower than writes — the opposite of Postgres.

**When to choose Cassandra over Postgres:**
- Write QPS > 50k per node needed
- Time-series data (append-only, natural for LSM)
- No complex joins needed
- Horizontal scale is a hard requirement from day one

---

## Elasticsearch (search engine)

```
Indexing throughput:    10,000 – 100,000 docs/sec per node (depends on doc size)
Search latency:         10 – 100 ms    (full-text search, aggregations)
Storage:                ~2–3× raw data size (inverted index overhead)
```

Not a primary DB — a search index. Always backed by a primary store (Postgres, Cassandra). You write to primary store + async index into Elasticsearch.

---

## Summary comparison

| Database | Best for | Read QPS (single node) | Write QPS (single node) | Read latency |
|---|---|---|---|---|
| PostgreSQL | Relational, ACID, complex queries | 10k–50k | 5k–10k | 1–5ms |
| Redis | Cache, session, leaderboard, rate limit | 100k–500k | 100k–500k | 0.1–0.5ms |
| MongoDB | Flexible schema, document, moderate scale | 50k–100k | 20k–50k | 1–5ms |
| Cassandra | Write-heavy, time-series, high scale | 50k–80k | 100k–200k | 5–10ms |
| Elasticsearch | Full-text search, log analytics | varies | 10k–100k | 10–100ms |

---

> [!tip] Interview framing
> "Single Postgres instance handles 10k–50k reads/sec and 5k–10k writes/sec. Redis is 100k–500k ops/sec at sub-millisecond. Cassandra flips the ratio — writes are faster than reads (LSM tree, memtable). If write QPS > 50k per node, Cassandra. If you need sub-millisecond, Redis. If you need ACID + joins, Postgres."
