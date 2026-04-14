
> [!info] The retry strategy determines how hard the system tries to recover from a failed S3 upload before declaring the paste permanently broken.

---

## Why a message queue, not a direct retry

The naive approach: when S3 upload fails, the app server retries in a loop.

Problems:
- App server might crash mid-retry — upload job is lost entirely, paste stays IN_PROGRESS forever
- Retrying in the same process ties up app server threads
- If S3 is down for 30 minutes, the app server is sitting in a retry loop for 30 minutes

The right approach: enqueue the upload job into a message queue (e.g. SQS, Kafka). A dedicated upload worker picks up the job and handles retries independently of the app server.

```
App server:
  → INSERT paste row (status = IN_PROGRESS)
  → enqueue { shortCode, contentBytes } to upload queue
  → return 201 to user

Upload worker:
  → dequeues job
  → attempts S3 upload
  → on success: UPDATE paste (s3_url, status = PROCESSED), ack message
  → on failure: retry with backoff
  → on exhaustion: UPDATE paste (status = FAILED), ack message
```

The message stays in the queue until the worker explicitly acknowledges it. If the worker crashes mid-upload, the queue redelivers the job to another worker. No jobs are lost.

---

## Exponential backoff with random jitter

You don't want to hammer a struggling S3 with immediate retries. If S3 is returning 500s, hammering it makes recovery slower for everyone.

Exponential backoff: each retry waits twice as long as the previous one.

Random jitter: add a small random offset to each wait to prevent multiple workers from retrying in lockstep (thundering herd).

```
Attempt 1: immediate
Attempt 2: wait 1s  + jitter (±200ms)
Attempt 3: wait 2s  + jitter
Attempt 4: wait 4s  + jitter
Attempt 5: wait 8s  + jitter
Attempt 6: wait 16s + jitter
→ all 6 failed → mark status = FAILED
```

Total retry window: ~31 seconds. If S3 doesn't recover within ~30 seconds, the paste is marked FAILED. This is the SLO for paste creation — if S3 is down longer than 30 seconds, some pastes will fail permanently.

---

## What happens to FAILED rows

FAILED rows stay in Postgres but are permanently unreadable. A background cleanup job sweeps them up periodically — say, once a day — and deletes rows where status = FAILED and created_at is older than 24 hours.

This keeps the table clean without any urgency. A FAILED paste doesn't affect any other part of the system — it's just a dead row.
