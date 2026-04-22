
> [!info] The cleanup job and watchdog both query by status — but status has low cardinality, making a naive index on it nearly useless. Partial indexes solve this precisely.

---

## The low cardinality problem

Status columns look like good index candidates — queries filter on them constantly. But cardinality matters enormously for index usefulness.

Cardinality = how many distinct values exist relative to the number of rows.

```
pastes table: 3.65B rows
deletion_status values: NOT_EXPIRED, DELETION_IN_PROGRESS, DELETED

Distribution at steady state:
  NOT_EXPIRED:           ~95% of rows (pastes not yet expired)
  DELETED:               ~4.9% of rows (already cleaned up)
  DELETION_IN_PROGRESS:  ~0.1% of rows (currently being processed)
```

A B-tree index on deletion_status would have 3 leaf nodes, each pointing to billions of row pointers. When the cleanup job queries `WHERE deletion_status = 'NOT_EXPIRED'`, Postgres would use the index to find that node — then fetch 95% of the table anyway. At that point, a full table scan is faster. Postgres's query planner would likely ignore the index entirely.

> [!danger] Low cardinality indexes don't just fail to help — they waste storage and slow down writes (every INSERT/UPDATE must maintain the index). They are actively harmful.

---

## Partial indexes — index only the rows you actually query

A partial index is an index with a WHERE clause. It only indexes rows that satisfy the condition. Rows that don't match are not in the index at all.

For the cleanup job's main query:

```sql
CREATE INDEX idx_cleanup_expired
ON pastes (expires_at)
WHERE deletion_status = 'NOT_EXPIRED';
```

This index contains only NOT_EXPIRED rows, sorted by expires_at. At any given time, that's pastes which haven't expired yet — a large set initially, but the query filters to `expires_at < now()`, which is a small, time-bounded range at the front of the index.

For the watchdog query:

```sql
CREATE INDEX idx_watchdog_stuck
ON pastes (deletion_initiated_at)
WHERE deletion_status = 'DELETION_IN_PROGRESS';
```

This index contains only DELETION_IN_PROGRESS rows. At steady state that's a tiny fraction of 3.65B rows — maybe a few thousand at most. The entire index fits in a few pages. The watchdog's query hits it instantly.

---

## Why not include deletion_status in the index body?

You might think to write:

```sql
CREATE INDEX idx_watchdog_stuck
ON pastes (deletion_status, deletion_initiated_at)
WHERE deletion_status = 'DELETION_IN_PROGRESS';
```

But the partial condition `WHERE deletion_status = 'DELETION_IN_PROGRESS'` already guarantees that every row in this index has deletion_status = 'DELETION_IN_PROGRESS'. Storing it again in the index body is redundant — it wastes space in the index and adds no query benefit.

The single-column partial index is smaller, faster to maintain, and equally effective:

```sql
-- Redundant (status stored twice — once in partial condition, once in body)
ON pastes (deletion_status, deletion_initiated_at)
WHERE deletion_status = 'DELETION_IN_PROGRESS'

-- Correct (status filters via partial condition, body only stores what's needed)
ON pastes (deletion_initiated_at)
WHERE deletion_status = 'DELETION_IN_PROGRESS'
```

---

## Summary of indexes for the cleanup system

```sql
-- Cleanup job: find expired, unprocessed pastes efficiently
CREATE INDEX idx_cleanup_expired
ON pastes (expires_at)
WHERE deletion_status = 'NOT_EXPIRED';

-- Watchdog: find rows stuck in DELETION_IN_PROGRESS
CREATE INDEX idx_watchdog_stuck
ON pastes (deletion_initiated_at)
WHERE deletion_status = 'DELETION_IN_PROGRESS';
```

Two small, targeted indexes. Each serves exactly one query pattern. Neither wastes space on rows that are irrelevant to that query.

> [!tip] Interview framing
> "Status columns have low cardinality — a full index on deletion_status is nearly useless because Postgres would still scan most of the table. Partial indexes solve this: the cleanup job gets an index on expires_at filtered to NOT_EXPIRED rows only, and the watchdog gets an index on deletion_initiated_at filtered to DELETION_IN_PROGRESS rows only. Each index is tiny because it only covers the small subset of rows that the query actually needs. Including deletion_status in the index body would be redundant — the partial condition already guarantees every row in the index matches that status."
