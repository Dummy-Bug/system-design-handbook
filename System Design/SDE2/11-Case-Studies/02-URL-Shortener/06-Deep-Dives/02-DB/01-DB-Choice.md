
> [!info] Start with access patterns, not the database
> The right way to pick a database is to first understand exactly what queries the system needs to run — then choose the DB that handles those queries best. Picking a DB before understanding access patterns is guessing.

---

## Step 1 — what are the access patterns?

Two flows. Two queries.

```
Creation  → INSERT a new row (short_code + long_url)
Redirect  → given a short_code, return the long_url
```

The redirect query dominates — 100k reads/sec vs 1k writes/sec. The DB must be optimised for fast single-key lookups.

There are no:
- Complex joins across multiple tables
- Aggregations (COUNT, SUM, GROUP BY)
- Full-text search
- Graph traversals
- Time-series queries
- Flexible or dynamic schemas

Just one table, one query pattern: look up a short code, return a long URL.

---

## Step 2 — what are the nouns?

Before picking columns, identify the entities:

```
URL        → the mapping between short code and long URL
Short code → the key users see and click
User       → who created the URL
```

Users are anonymous — anyone can shorten a URL without logging in. No user table, no user_id, no foreign key joins. One less table on every query.

URL and short code could be separate tables, but the redirect query always needs both together. A join on every redirect at 100k QPS is unnecessary latency. One denormalized table is correct.

---

## Step 3 — relational vs NoSQL

**Why relational (Postgres / MySQL)?**

The schema is fixed and simple. Short code maps to long URL — no dynamic fields, no nested documents, no schema changes expected. Relational databases are designed exactly for this.

Relational DBs also give:
- **ACID guarantees** — the uniqueness constraint on `short_code` is enforced at the storage layer, not just in application code. Two servers racing to insert the same short code — the DB rejects the duplicate automatically.
- **Mature indexing** — covering indexes, query planners, index-only scans. All battle-tested.
- **Simple operations** — no complex query patterns that would benefit from a specialised DB.

**Why not NoSQL?**

NoSQL databases (Cassandra, DynamoDB, MongoDB) are designed for:
- Massive write throughput across distributed nodes (Cassandra)
- Flexible schemas that change frequently (MongoDB)
- Key-value lookups at extreme scale with simple operations (DynamoDB)

DynamoDB is actually a reasonable choice here — it's essentially a managed key-value store and our access pattern is pure key-value. But it adds vendor lock-in and cost complexity. Postgres gives you the same key-value lookup with a covering index, full ACID guarantees, and no lock-in.

The rule: don't reach for NoSQL unless you have a specific problem that relational can't solve. Here, relational solves it cleanly.

---

## The decision

**Postgres or MySQL** — either works. Both handle the access pattern, both support covering indexes, both give ACID guarantees.

The DB choice is not the interesting part of this system. The interesting parts are sharding, caching, and key generation. Pick Postgres, state your reasoning, move on.

---

> [!tip] Interview framing
> "Access pattern is one query — look up short code, return long URL. Fixed schema, no joins needed since users are anonymous, no complex queries. Relational DB is the right call — ACID guarantees enforce short code uniqueness at the storage layer, covering index makes the redirect query an index-only scan. NoSQL adds complexity without solving a specific problem here."
