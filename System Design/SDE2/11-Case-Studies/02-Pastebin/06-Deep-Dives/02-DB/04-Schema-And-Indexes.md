
> [!info] Every column exists to serve a query or enforce a constraint. Every index exists to make a specific query fast.
> If you can't name the query a column or index serves, it shouldn't be there.

---

## Full Schema

```sql
-- Users table
CREATE TABLE users (
  user_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(100) NOT NULL,
  email       VARCHAR(255) NOT NULL UNIQUE,
  created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Content table (one row per unique piece of content)
CREATE TABLE content (
  content_hash  VARCHAR(64) PRIMARY KEY,   -- SHA-256 hex string (64 chars)
  s3_url        VARCHAR(512) NOT NULL,     -- pointer to blob in S3
  ref_count     INTEGER NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Pastes table (one row per user per paste — ownership record)
CREATE TABLE pastes (
  short_code    VARCHAR(8) PRIMARY KEY,    -- random Base62 or custom alias
  user_id       UUID NOT NULL REFERENCES users(user_id),
  content_hash  VARCHAR(64) NOT NULL REFERENCES content(content_hash),
  expires_at    TIMESTAMP NOT NULL,        -- created_at + 1/7/30 days
  created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at    TIMESTAMP                  -- NULL = active, SET = soft deleted
);
```

---

## Column Reasoning

**`content_hash` as PK of content table**
The hash is globally unique by the nature of SHA-256. It's also the natural lookup key — when you want to check if content already exists, you query by hash. Using it as PK means the existence check and the primary index are the same operation. No surrogate ID needed.

**`short_code` as PK of pastes table**
Short codes are globally unique by design — the system guarantees no two pastes share a short code. It's also the only lookup key for reads (`GET /pastes/:shortCode`). Using it as PK means the read query hits the primary index directly. A surrogate auto-increment ID would add a column no query ever uses.

**`deleted_at` as timestamp, not boolean**
A boolean `is_deleted` tells you nothing about when the deletion happened. A timestamp `deleted_at` gives you the deletion time for audit purposes and lets the cleanup job order deletions chronologically. Pattern: NULL = active, SET = deleted.

**`expires_at` as absolute timestamp, not duration**
Storing "expires in 7 days" as an integer requires computing `created_at + 7 days` on every read to check expiry. Storing the absolute expiry timestamp means the check is a single comparison: `expires_at < NOW()`. Simpler query, faster execution.

**`s3_url` on content table, not pastes table**
The S3 blob belongs to the content, not to any individual paste. If you stored `s3_url` on the pastes table, 500 users sharing the same content would each store the same S3 URL 500 times. Keeping it on content means it's stored once.

---

## Indexes

```sql
-- Cleanup job: find expired or soft-deleted pastes efficiently
CREATE INDEX idx_pastes_expires_at ON pastes(expires_at);

-- Login lookup: find user by email on every login
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Already auto-indexed (as PKs):
--   content(content_hash)
--   pastes(short_code)
--   users(user_id)
```

**Why `idx_pastes_expires_at`?**
The nightly cleanup job runs:
```sql
SELECT short_code, content_hash 
FROM pastes 
WHERE expires_at < NOW() OR deleted_at IS NOT NULL;
```
Without the index, this is a full table scan across 3.65B rows at year 10. With the index, it's a fast range scan. This is the only non-PK index needed on the pastes table — reads go by `short_code` (PK), writes are inserts.

**Why no index on `content_hash` in pastes?**
You never query pastes by `content_hash`. The flow is: lookup by `short_code` → get `content_hash` → lookup `content` table by `content_hash` (its PK). The join goes from pastes → content, using the content PK. No extra index needed.

---

## What the Schema Does NOT Have

**No surrogate ID on pastes** — `short_code` is already unique and is the only lookup key. A surrogate key would be pure overhead.

**No `content` column on pastes** — the actual text lives in S3, pointer lives in `content` table. Storing text in the DB row would make rows 10KB each, bloating every index scan.

**No `username` column on pastes** — content creator identity is in the `users` table via `user_id` FK. Denormalising it onto `pastes` would duplicate data that can be joined cheaply.

---

> [!tip] Interview framing
> "Three tables: users (user_id PK), content (content_hash PK, s3_url, ref_count), pastes (short_code PK, user_id FK, content_hash FK, expires_at, deleted_at). short_code as PK because it's globally unique and the only read lookup key. expires_at stored as absolute timestamp — single comparison on read instead of computing offset each time. One extra index: pastes(expires_at) for the cleanup job."
