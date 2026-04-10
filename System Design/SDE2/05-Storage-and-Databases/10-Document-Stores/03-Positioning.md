> [!info] A document store wins when your data has variable structure and your access patterns are document-centric. The moment you need joins, strict constraints, or extreme write throughput with time-series data, you've outgrown it.

## When document stores beat SQL

SQL forces a fixed schema — every row has the same columns. When different entities have genuinely different shapes, SQL fights you:

```
Product catalog:
  Shoe     → sizes, material, weight
  Laptop   → ram_gb, cpu, storage_gb
  TV       → resolution, size_inches, refresh_rate_hz

SQL:     ALTER TABLE for every new category → painful at scale
MongoDB: different documents, different fields → no migration needed
```

Document stores also win when data is hierarchical and always fetched together — nested objects and arrays map naturally to a document, while SQL would need multiple tables and joins.

---

## When SQL beats document stores

```
Relational data with joins
  Orders → line items → products → inventory
  SQL handles this in one query. MongoDB needs multiple round trips.

Strict integrity requirements
  Financial data, order records, regulated industries
  SQL constraints (NOT NULL, FOREIGN KEY) are enforced by the DB
  MongoDB constraints are enforced by your application — that's weaker

Complex multi-dimensional queries
  "All UK users aged 20-25 who bought Product X in January"
  SQL with indexes handles this naturally
  MongoDB needs multiple GSI-equivalent indexes
```

---

## When KV stores beat document stores

```
Access pattern is purely "give me everything for this key"
  No need to query inside the structure
  DynamoDB or Redis is simpler, faster, cheaper

Example: session tokens, feature flags, rate limit counters
  → pure GET/SET, no internal querying needed
  → KV store, not document store
```

---

## When column-family beats document stores

```
Write-heavy time-series at extreme scale
  IoT sensors, activity logs, chat message history
  Cassandra/Bigtable handles millions of writes/sec
  MongoDB is not optimised for this access pattern
```

---

## Decision map

```
Variable schema, nested data, document-centric reads  →  Document store (MongoDB)
Relational data, complex joins, strict integrity       →  SQL
Simple key lookup, no internal querying               →  KV store (Redis/DynamoDB)
Write-heavy time-series, extreme scale                →  Column-family (Cassandra)
Full-text search, ranked results                      →  Search engine (Elasticsearch)
```

---

> [!tip] Interview framing
> "I'd use MongoDB when the data has variable structure across entities — product catalogs, user profiles, CMS content — and access patterns are document-centric. SQL when I need joins and integrity constraints. KV store when I only need lookup by key with no internal querying. Column-family when the workload is write-heavy time-series at extreme scale."
