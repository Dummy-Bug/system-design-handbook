# Key-Value Stores — Interview Cheatsheet

---

## The one-line model

```
Key-Value  →  O(1) lookup, no joins, no flexible queries, extreme speed and scale
```

---

## Three KV stores at a glance

| | Redis | DynamoDB | Memcached |
|---|---|---|---|
| Storage | RAM | SSD (disk-backed) | RAM |
| Latency | ~200ns | Low millisecond | ~200ns |
| Threading | Single-threaded | Managed | Multi-threaded |
| Data structures | Rich (Hash, List, Sorted Set, Stream) | KV only | String only |
| Persistence | Optional (RDB/AOF) | Always | None |
| Sharding | Manual (Redis Cluster) | Auto | Manual |
| Best for | Cache, real-time, pub/sub | Persistent KV at scale | Extreme raw throughput |

---

## When to pick which

```
Redis       →  cache layer, sub-millisecond, rich structures, pub/sub, Streams
DynamoDB    →  persistent, write-heavy, billions of rows, fully managed, multi-region
Memcached   →  only if: >1M ops/sec on one node, simple GET/SET, can't shard
              (Redis Cluster usually replaces this need)
```

---

## KV vs other stores

```
Need joins or relational queries   →  SQL
Need flexible/nested documents     →  Document store (MongoDB)
Need multi-dimensional search      →  Search engine (Elasticsearch)
Need time-series / wide rows       →  Column-family (Cassandra, Bigtable)
Simple lookup by key               →  Key-Value ✓
```

---

## DynamoDB quick reference

```
Partition key  →  consistent hashing → which server
Sort key       →  LSM tree → range queries within partition
GSI            →  second copy, different partition key, always eventual, 2x write cost
Consistency    →  eventual (0.5x cost) vs strong (2x cost), tunable per read
Global Tables  →  async multi-region replication, eventual consistency cross-region
Scan           →  never in production
```

---

## Interview framing

> "For a cache layer I'd use Redis — sub-millisecond, in-memory, rich data structures. For persistent write-heavy storage at scale I'd use DynamoDB — auto-sharding, fully managed, handles billions of writes. In practice both coexist: Redis in front as the hot cache, DynamoDB as the source of truth. Memcached only comes up in the rare case I need more than 1M ops/sec on a single node and can't shard — Redis Cluster usually covers that instead."
