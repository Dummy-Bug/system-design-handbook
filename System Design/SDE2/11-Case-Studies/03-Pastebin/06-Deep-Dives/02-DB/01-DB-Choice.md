
> [!info] Database choice follows from access patterns — not personal preference, not familiarity.
> The right question is: what queries does this system run, and which DB handles them best?

---

## Access Patterns

The system has two core queries:

```
1. GET paste by short code
   SELECT * FROM pastes WHERE short_code = 'aX3kZ9'
   → point lookup, called 3,000/sec at peak

2. INSERT new paste
   INSERT INTO pastes ...
   → 30 writes/sec at peak
```

There is no full-text search, no content querying, no graph traversal. The paste content itself is treated as a dumb blob — the system stores it and returns it as-is, never querying inside it.

---

## Why PostgreSQL

The data is structured and relational:
- A paste belongs to a user
- A paste points to a content blob
- Content blobs have reference counts tracking how many pastes point at them

These are foreign key relationships. The reference counting logic (increment on create, decrement on delete, physical delete at zero) benefits from ACID transactions — you don't want a ref_count decrement and a content row deletion to be two separate non-atomic operations.

**Why not MongoDB?**
Document stores make sense when schema is flexible or when you're querying inside nested documents. Neither applies here — schema is fixed and the paste content is never queried. MongoDB adds operational complexity with no benefit.

**Why not Cassandra?**
Cassandra excels at write-heavy workloads (100k-200k writes/sec per node). At 30 writes/sec peak, this system is nowhere near Cassandra territory. Cassandra also lacks ACID transactions — the ref counting logic would become significantly more complex to implement correctly.

---

## Content Storage — S3 for Blobs, Postgres for Metadata

A paste is ~10KB. At 150TB over 10 years, storing the full text in Postgres rows would work but is wasteful — Postgres is optimised for structured queries, not blob retrieval. Large text columns bloat indexes, slow down row scans, and make backups heavier.

The right split:

```
Postgres  → metadata (short_code, user_id, expiry, content_hash, ref_count)
S3        → actual paste text (10KB blob, retrieved by s3_url)
```

This keeps the DB rows small (< 200 bytes each), makes index scans fast, and offloads blob storage to a system designed for it. S3 is infinitely scalable, cheap, and durable by default (11 nines durability).

---

> [!tip] Interview framing
> "PostgreSQL for metadata — structured data, relational ownership, ACID needed for ref counting. S3 for paste content — 10KB blobs don't belong in DB rows, S3 is cheaper and designed for blob retrieval. No Cassandra — 30 writes/sec doesn't need LSM. No MongoDB — schema is fixed, content is never queried."
