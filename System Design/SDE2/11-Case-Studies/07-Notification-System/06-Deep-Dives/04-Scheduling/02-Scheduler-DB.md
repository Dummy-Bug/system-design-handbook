# Scheduler DB — Scheduling

## Why Cassandra

Scheduled notifications are 20% of total volume:
```
5M/sec × 20% = 1M scheduled notifications/sec write volume
```

1M writes/sec rules out relational DBs (PostgreSQL/MySQL cap around 10-50K writes/sec) and MongoDB (similar ceiling under update-heavy workloads). Cassandra handles 100K-200K writes/node — 1M/sec needs ~10 nodes, well within range.

---

## Access Pattern — Not By User, By Time

This is the critical insight that drives the entire schema. The scheduler's query is never:

> "Give me all scheduled notifications for user X"

It is always:

> "Give me all notifications that are due right now — across all users"

This is a fundamentally different access pattern from the notifications table. Partitioning by `user_id` here would mean the scheduler has to hit every partition in the cluster to find due notifications — a full scatter-gather at every poll. At 1M notifications stored across hundreds of partitions, that's hundreds of DB calls every second just to find what's due.

The partition key must be **time-based**.

---

## Partition Key — Minute Bucket

**Why not exact timestamp?**
If `scheduled_at` is the partition key with full timestamp precision (e.g. `2026-04-19 09:00:03.421`), every notification lands on its own partition. Millions of tiny partitions, each with one row. Cassandra's overhead per partition makes this extremely inefficient.

**Why not hour bucket?**
`hour_bucket = "2026-04-19-09"` groups all notifications due between 9am and 10am on the same partition. At first glance this seems fine — but a marketing campaign scheduled for 9:00am puts 10M notifications in the same partition simultaneously. Hot partition.

**Why minute bucket works:**
`minute_bucket = "2026-04-19-09-00"` groups all notifications due within the same minute. Fine enough to spread load across 60× more partitions than hour buckets, coarse enough to avoid millions of single-row partitions.

```
Scheduler queries one minute bucket at a time:
SELECT * FROM scheduled_notifications 
WHERE minute_bucket = '2026-04-19-09-00' 
AND scheduled_at <= now()
```

One partition read — no scatter-gather.

---

## Clustering Key — scheduled_at ASC

Within a minute bucket partition, rows are sorted by `scheduled_at` ascending. The scheduler reads from the earliest due notification to the latest — a sequential disk read. Efficient range scan.

---

## Schema

```sql
CREATE TABLE scheduled_notifications (
    minute_bucket   TEXT,          -- e.g. '2026-04-19-09-00'
    scheduled_at    TIMESTAMP,
    notification_id UUID,
    user_id         UUID,
    channel         TEXT,          -- PUSH / SMS / EMAIL
    template_data   TEXT,          -- JSON blob
    created_at      TIMESTAMP,

    PRIMARY KEY (minute_bucket, scheduled_at, notification_id)
) WITH CLUSTERING ORDER BY (scheduled_at ASC, notification_id ASC);
```

`notification_id` is included in the primary key to avoid collisions — two notifications scheduled for the exact same millisecond would otherwise overwrite each other.

---

> [!danger] Common Trap — Partitioning by user_id
> The instinct is to reuse the same partition key as the notifications table. But the access pattern here is "what's due now across all users" — not "what's scheduled for this user." Partitioning by user_id forces a full cluster scan on every scheduler poll. Always design the partition key around the query, not the entity.
