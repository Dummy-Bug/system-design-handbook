
> [!info] Async S3 upload means the app server returns a shortCode to the user immediately — without waiting for S3 to confirm the content was stored. The upload happens in the background.

---

## The write latency problem

The synchronous write flow looks like this:

```
POST /paste arrives
  → generate shortCode
  → hash content (dedup check)
  → INSERT into Postgres
  → upload content to S3       ← this takes 50–200ms
  → UPDATE Postgres (s3_url)
  → return 201 to user
```

The user is blocked waiting for S3. That 50–200ms S3 round trip sits on the critical path of every single paste creation. At 30 writes/sec that's fine on average — but under load spikes, or when S3 has elevated latency, write p99 climbs.

More importantly: the user doesn't need to wait for S3. They just need their shortCode. The content upload can happen after the response goes back.

---

## The async flow

```
POST /paste arrives
  → generate shortCode
  → hash content (dedup check)
  → INSERT into Postgres (s3_url = NULL, status = IN_PROGRESS)
  → enqueue S3 upload job
  → return 201 Created + shortCode   ← user gets this immediately

Background worker:
  → picks up S3 upload job
  → uploads content to S3
  → UPDATE Postgres (s3_url = ..., status = PROCESSED)
```

The user gets their shortCode in milliseconds. The S3 upload completes ~100–200ms later in the background.

---

## Why 201, not 200 or 202

This is where HTTP semantics matter.

**200 OK** — generic success. Means the request was processed and completed. No specific implication about resource creation.

**201 Created** — the request resulted in a new resource being created. The resource exists. The `Location` header or response body tells you where it lives. This is exactly what happened — a paste row was created in Postgres, a shortCode was assigned.

**202 Accepted** — the request was received and will be processed, but processing is not complete yet. Implies the resource may not exist yet. This would be the right code if we hadn't even created the DB row yet — just queued a job.

In our flow, the paste row *does* exist after the request. The shortCode is valid. The resource was created. The S3 upload is a background detail the client doesn't need to know about. So **201 Created** is correct.

```
POST /paste → 201 Created
  Body: { "shortCode": "aB3xYz", "url": "https://pastebin.com/aB3xYz" }
```