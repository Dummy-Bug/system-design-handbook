
## Partition Key and Clustering Key

Before writing any columns, you need to understand how Cassandra physically stores data — because the schema IS the query plan.

**Partition key** determines which node holds the data. All rows with the same partition key live on the same node. The access pattern is "give me all notifications for user X" — so `user_id` is the partition key. Every query goes to exactly one node, no scatter-gather.

If you used `notification_id` as the partition key instead, a query for user X's notifications would require hitting every node in the cluster — a full cluster scan at 10M writes/sec worth of data. That's a non-starter.

**Clustering key** determines the sort order within a partition. The access pattern is range queries — "last 3 months of notifications for user X". So `created_at DESC` is the clustering key. Cassandra physically stores rows in this order on disk, meaning a range query is a sequential disk read, not a scan. Fast and cheap.

---

## Why Two Tables?

The naive approach is to store everything — notification metadata, content, and status — in one row. The problem is over-fetching.

The most common query is a status check: "what is the current delivery status of notification X?" That query needs `channel_status` only. If content (title, body, deep_link) is inline in the same row, Cassandra reads the full row anyway — you're pulling 300 bytes of payload on every status check for no reason. At 5M status reads/sec, that's wasted network and memory at scale.

The fix is to split hot data from cold data:

- **Hot table** — queried constantly: status checks, user notification history
- **Cold table** — queried rarely: only when the full content needs to be displayed

---

## Notifications Table (Hot)

```sql
CREATE TABLE notifications (
    user_id         UUID,
    created_at      TIMESTAMP,
    notification_id UUID,
    channel_status  MAP<TEXT, TEXT>,   -- e.g. {SMS: DELIVERED, EMAIL: FAILED, PUSH: PENDING}

    PRIMARY KEY (user_id, created_at)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

**Partition key:** `user_id` — all notifications for a user on one node.
**Clustering key:** `created_at DESC` — newest first, range queries are sequential reads.
**channel_status:** A map of channel → delivery status. One row tracks the full multi-channel delivery state for a notification.

> [!info] Why MAP and not separate rows per channel?
> A map keeps all channel statuses for one notification in one row. Querying "what happened to notification X across all channels" is a single row read. Separate rows per channel would require reading multiple rows and joining them — more complex, more reads.

---

## Notification Content Table (Cold)

```sql
CREATE TABLE notification_content (
    notification_id UUID PRIMARY KEY,
    title           TEXT,
    body            TEXT,
    deep_link       TEXT,
    template_id     UUID,
    created_at      TIMESTAMP
);
```

**Partition key:** `notification_id` — content lookup is always by notification ID, never by user.
**Written once** at 5M/sec when the worker picks up the Kafka message — never updated.
**Read rarely** — only when the full notification needs to be re-displayed (e.g. notification inbox in the app).

---

## Status Updates and Cassandra's Immutability

Cassandra is append-only under the hood. There is no in-place update — every `UPDATE` statement is actually a new write with a newer timestamp. Compaction reconciles the versions later and keeps only the latest.

This means updating `channel_status` on an existing row at 5M/sec is actually 5M new writes per second — not mutations. That's exactly what Cassandra is built for. The immutability is a feature: writes are sequential appends to the commit log, no random I/O, no locking.

```
Worker delivers via SMS → status: DELIVERED
  ↓
New row written to Cassandra with newer timestamp
  ↓
channel_status = {SMS: DELIVERED, PUSH: PENDING}
  ↓
Old row (channel_status = {SMS: PENDING, PUSH: PENDING}) reconciled at compaction
```

---

## Preferences Table (PostgreSQL)

Preferences live in PostgreSQL — not Cassandra — because they need strong consistency. If a user opts out of SMS, the very next notification must respect that. Eventual consistency here is a bug.

```sql
CREATE TABLE user_preferences (
    user_id             UUID PRIMARY KEY,
    opted_out_channels  TEXT[],          -- e.g. ['SMS', 'EMAIL']
    notification_types  JSONB,           -- e.g. {marketing: false, transactional: true}
    updated_at          TIMESTAMP
);
```

**Written rarely** — users change preferences infrequently.
**Read on every notification** — but cached in Redis, so PostgreSQL only sees cache-miss reads.
**Strong consistency** — PostgreSQL ACID guarantees opt-out is immediately visible.

> [!danger] Common Trap
> Storing preferences in Cassandra and relying on tunable consistency (QUORUM reads/writes) for strong consistency. You pay Cassandra's write throughput advantage for a workload that doesn't need it, and you still don't get true ACID — just a best-effort quorum. PostgreSQL is the right tool here.

---

## Summary

| Table | DB | Partition Key | Clustering Key | Write Volume |
|---|---|---|---|---|
| notifications | Cassandra | user_id | created_at DESC | 5M/sec |
| notification_content | Cassandra | notification_id | — | 5M/sec |
| user_preferences | PostgreSQL | user_id | — | Low |

Total Cassandra writes: **10M/sec** (5M notification rows + 5M status updates)
Cassandra nodes: **300** (100 shards × 3 replicas at 100K writes/node)
