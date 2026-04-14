
> [!info] The state machine on the paste row tracks where the async upload is in its lifecycle. It lets the read path return a meaningful response at every stage — not just success or 404.

---

## The problem without states

Without a status column, the DB row looks the same whether:
- The upload is still in progress (worker picked it up, uploading now)
- The upload failed (worker gave up after retries)
- The upload never started (worker crashed before picking it up)

All three cases show s3_url = NULL. The read path can't distinguish between them. It can't tell the user "try again in 30 seconds" vs "this paste is gone."

A state machine fixes this by making each stage explicit.

---

## The states

```
IN_PROGRESS  — paste row created, S3 upload queued or in flight
PROCESSED    — S3 upload succeeded, s3_url populated, paste is readable
FAILED       — all retries exhausted, S3 upload never succeeded, paste is permanently broken
```

Transitions:

```
                S3 upload succeeds
IN_PROGRESS ─────────────────────→ PROCESSED

                all retries exhausted
IN_PROGRESS ─────────────────────→ FAILED
```

There is no transition out of PROCESSED or FAILED — both are terminal states.

---

## The schema change

One column added to the pastes table:

```sql
status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS'
  CHECK (status IN ('IN_PROGRESS', 'PROCESSED', 'FAILED'))
```

On INSERT (paste creation):

```sql
INSERT INTO pastes (short_code, user_id, content_hash, s3_url, status, ...)
VALUES ('aB3xYz', 123, 'sha256...', NULL, 'IN_PROGRESS', ...)
```

On successful upload:

```sql
UPDATE pastes
SET s3_url = 'https://s3.amazonaws.com/...', status = 'PROCESSED'
WHERE short_code = 'aB3xYz'
```

On permanent failure:

```sql
UPDATE pastes
SET status = 'FAILED'
WHERE short_code = 'aB3xYz'
```

---

## What the state machine buys you

Every read request now has a definitive answer:

```
status = PROCESSED   → paste is readable, serve content
status = IN_PROGRESS → paste is being created, ask client to retry
status = FAILED      → paste creation failed, treat as not found
```

No ambiguity. No silent broken pastes. The read path can always explain what's happening.
