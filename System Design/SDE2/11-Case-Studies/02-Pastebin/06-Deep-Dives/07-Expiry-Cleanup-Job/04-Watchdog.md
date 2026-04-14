
> [!info] A worker can crash mid-batch after marking rows as DELETION_IN_PROGRESS but before finishing the deletion. Without a watchdog, those rows are stuck forever — never deleted, never queryable.

---

## The stuck row problem

A worker acquires the lock, marks 1000 rows as DELETION_IN_PROGRESS, releases the lock, and starts processing. Halfway through the batch — after deleting 400 rows — the worker process crashes.

The remaining 600 rows are now in DELETION_IN_PROGRESS permanently:

```
status = 'DELETION_IN_PROGRESS'
deletion_initiated_at = 2 hours ago
```

No other worker will touch them — the cleanup query filters `WHERE status = 'NOT_EXPIRED'`. They are invisible to the cleanup job. They will never be deleted. They accumulate silently.

Over time, a crashed-worker event every few days leaves thousands of rows permanently stuck. Storage grows. The table drifts out of sync with S3.

---

## The watchdog

A separate lightweight background job — the watchdog — runs periodically and looks for rows that have been stuck in DELETION_IN_PROGRESS for longer than the expected processing window.

```sql
UPDATE pastes
SET status = 'NOT_EXPIRED',
    deletion_initiated_at = NULL
WHERE status = 'DELETION_IN_PROGRESS'
AND deletion_initiated_at < now() - interval '2 hours'
```

Two hours is generous — a healthy worker should complete a 1000-row batch in seconds. Any row stuck for 2 hours means the worker that claimed it is definitely dead.

The watchdog resets these rows back to NOT_EXPIRED. The next cleanup run picks them up normally.

---

## The full state machine

```
NOT_EXPIRED
    │
    │  cleanup worker picks up batch, marks row
    ▼
DELETION_IN_PROGRESS
    │                        │
    │  worker completes      │  worker crashes, stuck > 2hrs
    ▼                        ▼
DELETED              NOT_EXPIRED  ← watchdog resets
                          │
                          │  next cleanup run picks it up
                          ▼
                    DELETION_IN_PROGRESS → DELETED
```

DELETED is the only terminal state. A row either gets deleted successfully or gets reset and retried — it never disappears into a permanent limbo.

---

## Schema additions

Two columns added to the pastes table to support this:

```sql
deletion_status    VARCHAR(20) DEFAULT 'NOT_EXPIRED'
                   CHECK (deletion_status IN ('NOT_EXPIRED', 'DELETION_IN_PROGRESS', 'DELETED'))

deletion_initiated_at  TIMESTAMPTZ NULL
```

deletion_initiated_at is NULL until a worker claims the row, then set to now(). Reset to NULL by the watchdog if the worker crashes.
