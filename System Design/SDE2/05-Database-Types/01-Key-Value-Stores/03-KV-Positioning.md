> [!info] A Key-Value store is the right tool when your access pattern is simple — give me everything for this key, or give me a range within this key. The moment you need joins, multi-dimensional filtering, or flexible schema, you've outgrown KV.

---

## The core trade-off

**KV stores give up query flexibility to gain speed and scale**.

```
SQL         →  any query you want, at the cost of complexity and scaling difficulty
Key-Value   →  only the queries you designed for, but O(1) at any scale
```

This is not a flaw — it's the design. You pre-compute your access patterns into the data model. The database does no thinking at runtime. It just hashes the key and goes to the right server.

---

## When KV beats SQL

**Single-entity lookups at massive scale**

```
"Give me user 42's profile"
→ hash(42) → server → done
→ no query planner, no index scan, no join
→ works identically whether you have 1M or 1B users
```

SQL with a primary key index also does this fast — **but sharding SQL at 1B users is operationally painful**. KV stores (DynamoDB especially) shard automatically.

**Write-heavy event storage**

```
Likes, views, clicks, scroll events — billions per day
→ LSM tree underneath absorbs write bursts
→ SQL B+ tree struggles with this volume on a single node
```

**Cache layer**

```
Redis sits in front of any database
→ hot data served from RAM in 200ns
→ database only hit on cache miss
```

---

## When KV loses to other stores

**You need joins**

```
"Give me all orders for user 42, with product names and shipping address"
→ requires joining orders + products + addresses
→ KV has no JOIN — you'd have to fetch each table separately and join in code
→ SQL is the right tool here
```

**You need flexible, nested documents**

```
User profiles where different users have different fields
→ one user has "company", another has "school", another has neither
→ Document store (MongoDB) handles variable schema naturally
→ KV stores everything as a flat value — nested structure is your problem
```

**You need multi-dimensional queries**

```
"Give me UK users aged 20–25 who signed up this month"
→ three dimensions: country, age, signup date
→ KV can only index on partition key + sort key
→ every additional dimension needs a GSI (DynamoDB) or a separate Redis key
→ too many dimensions → relational DB or search engine is cleaner
```

**You need time-series or wide-row data at scale**

```
IoT sensors writing 1M events/sec, queried by device + time range
→ Column-family store (Cassandra, Bigtable) is optimised for this
→ same LSM write performance, but richer query model across many columns
```

---

## Decision map

```
Access pattern                          →  Store
─────────────────────────────────────────────────
Lookup by ID, simple KV                →  Redis (if in-memory) / DynamoDB (if persistent)
Write-heavy events at massive scale    →  DynamoDB
Cache layer, sub-millisecond           →  Redis
Complex joins, relational data         →  SQL (Postgres, MySQL)
Flexible/nested documents              →  Document store (MongoDB)
Multi-dimensional search               →  Search engine (Elasticsearch)
Time-series, wide rows                 →  Column-family (Cassandra, Bigtable)
```

---

## The hybrid pattern

In practice, KV stores rarely replace other databases — they sit alongside them:

```
Request
  → Redis (cache, 200ns)
      ↓ miss
  → DynamoDB / Postgres (source of truth)
```

Redis handles the hot read traffic. The primary DB handles durability, complex queries, and writes. This pattern is the default architecture for any read-heavy system at scale.

> [!tip] Interview framing
> "I'd use a KV store when the access pattern is simple — lookup by key, or range within a key. Redis for in-memory caching and sub-millisecond reads, DynamoDB for persistent write-heavy storage at scale. The moment I need joins or multi-dimensional queries I'd reach for SQL or a document store instead."
