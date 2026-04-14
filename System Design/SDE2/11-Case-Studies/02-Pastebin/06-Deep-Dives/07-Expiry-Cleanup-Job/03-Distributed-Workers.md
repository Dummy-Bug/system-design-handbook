
> [!info] A single cleanup worker falls behind on heavy expiry days. Multiple workers run in parallel — but they must coordinate so they don't process the same rows twice.

---

## Why one worker isn't enough

The cleanup job runs at off-peak hours — say midnight onwards. At 1M expirations per day, even with batch processing of 1000 rows at a time, a single worker processing one batch every few seconds could take hours.

On a heavy day — where a cohort of 30-day pastes all expire together — you might have 5–10M rows to process. A single worker cannot clear this before peak traffic resumes in the morning.

Multiple workers solve the throughput problem. Each worker processes a different subset of expired rows in parallel.

---

## The double-processing problem

Two workers running in parallel both query:

```sql
SELECT short_code FROM pastes
WHERE expires_at < now()
AND status = 'NOT_EXPIRED'
LIMIT 1000
```

They get overlapping results. Both pick up the same 1000 rows. Both decrement ref_count, both delete from S3, both delete from Postgres. The result:

- ref_count goes to -1 (wrong)
- S3 delete called twice (harmless but wasteful)
- Second Postgres DELETE fails silently (row already gone)

At best this is wasteful. At worst it corrupts ref_count, which causes content to be deleted while other pastes still reference it — breaking those pastes permanently.

---

## Redis distributed lock + status transition

The solution has two parts working together:

**Part 1 — Redis distributed lock**

Before a worker starts processing a batch, it acquires a Redis lock with a short TTL (e.g. 30 seconds). Only one worker holds the lock at a time. Other workers fail fast on lock acquisition and wait before retrying.

This prevents two workers from querying the same rows simultaneously.

**Part 2 — Status transition to DELETION_IN_PROGRESS**

Once a worker acquires the lock and fetches a batch, it immediately marks those rows:

```sql
UPDATE pastes
SET status = 'DELETION_IN_PROGRESS',
    deletion_initiated_at = now()
WHERE short_code IN (...)
```

Then it releases the lock. Now other workers can acquire the lock and fetch the next batch — but their query filters `WHERE status = 'NOT_EXPIRED'`, so they never see rows already claimed.

```
Worker 1: acquires lock → fetches batch A → marks DELETION_IN_PROGRESS → releases lock → processes batch A
Worker 2: acquires lock → fetches batch B (NOT_EXPIRED only) → marks DELETION_IN_PROGRESS → releases lock → processes batch B
Worker 3: acquires lock → fetches batch C → ...
```

Workers process their batches in parallel with no overlap. The lock is only held for the brief window of fetching and marking — processing happens lock-free.

---

## Scheduling

Workers run nightly starting at midnight. Each worker loops continuously — fetch batch, mark, process, repeat — until no more NOT_EXPIRED rows with expires_at < now() are found. Then it sleeps until the next scheduled run.
