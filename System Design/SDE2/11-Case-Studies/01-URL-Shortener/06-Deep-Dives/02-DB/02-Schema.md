
> [!info] Schema design follows access patterns
> The schema is not designed by listing columns you think you need. It is designed by looking at the queries the system runs — then building the table and indexes around those queries.

---

## The dominant query

```sql
SELECT long_url FROM urls WHERE short_code = 'x7k2p9';
```

This runs 100k times per second. Everything about the schema — the table structure, the index type, the column order — is optimised for this single query.

---

## The schema

```
urls
-------------------------------
id          BIGINT PRIMARY KEY    ← internal row ID, never exposed to users
short_code  VARCHAR(6) UNIQUE     ← what users see, must be globally unique
long_url    TEXT                  ← what we redirect to
created_at  TIMESTAMP             ← when the mapping was created
expired_at  TIMESTAMP NULL        ← optional expiry, null means never expires
```

**id** — internal primary key. The DB needs a primary key for its internal B-tree. This is never returned in any API response. The short code is the external identifier.

**short_code** — 6 characters, base62. Must be unique across the entire table — the DB enforces this via a unique constraint. `VARCHAR(6)` not `TEXT` because the length is fixed and known.

**long_url** — `TEXT` because URLs can be arbitrarily long. No fixed length limit.

**created_at** — useful for debugging, analytics, and future features. Cheap to store.

**expired_at** — nullable. Most URLs have no expiry. When set, the redirect query adds `AND (expired_at IS NULL OR expired_at > NOW())` to filter out expired URLs.

---

## The indexes

**Index 1 — unique index on short_code**

```sql
CREATE UNIQUE INDEX idx_short_code ON urls(short_code);
```

Two jobs:
1. Enforces uniqueness — DB rejects duplicate short codes at insert time
2. Makes collision checks fast — `SELECT 1 WHERE short_code = 'x7k2p9'` is O(log n), not a full table scan

**Index 2 — covering index on (short_code, long_url)**

The redirect query needs `long_url` given `short_code`. With a regular index on `short_code`, the DB does two steps:

```
Step 1 → look up short_code in index → find the row's physical location on disk
Step 2 → fetch the actual row from disk → read long_url
```

Step 2 is called a **row lookup** — an extra disk read on top of the index read. At 100k reads/sec, this doubles your disk I/O.

A covering index includes `long_url` inside the index structure itself:

```sql
CREATE UNIQUE INDEX idx_short_code_covering ON urls(short_code) INCLUDE (long_url);
```

Now the DB finds `long_url` directly inside the index — no row lookup needed. The redirect query is served entirely from the index. One disk read instead of two, at every single redirect.

```
Without covering index → 2 disk reads per redirect × 100k/sec = 200k disk reads/sec
With covering index    → 1 disk read per redirect  × 100k/sec = 100k disk reads/sec
```

Half the disk I/O, same result.

---

## The QPS reality check

Even with a covering index, a single Postgres instance handles roughly **10k–50k reads/sec** under real conditions. At 100k reads/sec average and 1M/sec peak, a single DB falls over.

This is not a schema problem. The schema is already optimal — covering index, no joins, minimal columns. The problem is raw throughput. The fix is:

1. **Caching** — serve 80% of reads from Redis, DB sees only 20k/sec → covered in Caching deep dive
2. **Sharding** — split 250TB across multiple nodes → covered in the next files

---

> [!tip] Interview framing
> "One table — id, short_code, long_url, created_at, expired_at. Covering index on (short_code, long_url) so the redirect query never touches the actual row — index-only scan, half the disk I/O. Single Postgres tops out at 50k reads/sec — caching brings effective DB load to 20k/sec, sharding handles the storage limit."
