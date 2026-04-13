
> [!info] Start with access patterns, not columns
> The right way to design a schema is to look at what queries the system needs to run — then build the table around those queries. If you start by listing columns without thinking about how they'll be queried, you'll miss indexes, create unnecessary joins, and design for the wrong thing.

---

## Step 1 — what queries does this system actually run?

Two flows. Two queries. That's it.

```
Creation flow  → INSERT a new row (short_code + long_url)
Redirect flow  → given a short_code, find the long_url
```

The redirect query is the dominant one — 100k reads/sec vs 1k writes/sec. The schema must be optimised for it.

---

## Step 2 — what are the nouns?

Before jumping to columns, identify the entities in the system:

```
URL         → the mapping between short code and long URL
Short code  → the key users see and click
User        → who created the URL
```

Users are anonymous in this system — anyone can shorten a URL without logging in. So there's no user table, no user_id foreign key, no auth. That's one less join on every query.

URL and short code could theoretically be separate tables. But this system is read-heavy and the queries always need both together. Splitting them into two tables means a join on every redirect — extra latency for no benefit. One denormalized table is the right call.

---

## Step 3 — the schema

```
urls
-------------------------------
id          BIGINT PRIMARY KEY    ← internal row ID, never exposed to users
short_code  VARCHAR(6) UNIQUE     ← what users see, must be unique
long_url    TEXT                  ← what we redirect to
created_at  TIMESTAMP             ← when the mapping was created
expired_at  TIMESTAMP             ← optional, for URL expiry (nullable)
```

`id` is the internal primary key — it exists for DB internals and is never part of the API response. The short code is what identifies a URL from the outside.

`expired_at` is nullable. Most URLs have no expiry. When it's set, the redirect flow checks `WHERE expired_at IS NULL OR expired_at > NOW()` before returning the long URL.

---

## Step 4 — the indexes

**Index 1: unique index on short_code**

```sql
CREATE UNIQUE INDEX idx_short_code ON urls(short_code);
```

This does two things:
- Enforces uniqueness at the storage layer — the DB rejects duplicate short codes
- Makes collision checks during creation fast — O(log n) lookup, not a full table scan

**Index 2: covering index on (short_code, long_url)**

The redirect query is:
```sql
SELECT long_url FROM urls WHERE short_code = 'x7k2p9';
```

With a regular index on `short_code`, the DB does two steps:
1. Look up `short_code` in the index → find the row location
2. Fetch the actual row from disk to read `long_url`

Step 2 is called a **row lookup** — an extra disk read on top of the index read. At 100k reads/sec, this adds up.

A covering index includes `long_url` inside the index itself:

```sql
CREATE UNIQUE INDEX idx_short_code_covering ON urls(short_code, long_url);
```

Now the DB finds `long_url` directly in the index — no row lookup needed. The redirect query is served entirely from the index, never touching the actual table row. One disk read instead of two.

---

## Step 5 — DB choice

**Why relational (Postgres / MySQL)?**

The data is structured and the schema is fixed. Short code → long URL is a simple key-value relationship with no complex nesting, no dynamic fields, no schema-on-read. There's no reason to reach for NoSQL here.

Relational DBs also give you:
- ACID guarantees — the uniqueness constraint on short_code is enforced at the DB level, not just in application code
- Mature indexing — the covering index pattern above works exactly as described
- Simple operations — there are no complex aggregations, graph traversals, or time-series queries

The access pattern is simple enough that Postgres or MySQL handles it cleanly.

**Why not NoSQL?**

NoSQL databases (Cassandra, DynamoDB) are designed for massive write throughput across distributed nodes, or for flexible schemas that change frequently. Neither applies here. Introducing NoSQL for a simple key-value lookup adds operational complexity with no benefit at this scale.

**The QPS reality check**

A single Postgres instance handles roughly **10k–50k reads/sec** under real conditions depending on query complexity, hardware, and index efficiency. Our system needs 100k reads/sec on average, with peaks up to 1M/sec.

A single DB instance cannot handle this. The covering index helps — it reduces each read to a single index lookup — but even optimised reads hit a ceiling. This is not a schema problem. It's a scale problem. The fix is caching in front of the DB, not a better schema. That's the first deep dive.

---

> [!tip] Interview framing
> "I start with access patterns — redirect is the dominant query, 100x more frequent than writes. One table, denormalized since users are anonymous and we always need short_code and long_url together. Covering index on (short_code, long_url) so the redirect query never touches the actual row — served entirely from the index. Relational DB because the schema is fixed, we need ACID uniqueness on short_code, and NoSQL adds complexity with no benefit here. Single Postgres tops out at 50k reads/sec — 100k QPS needs a cache in front of it, that's deep dive one."
