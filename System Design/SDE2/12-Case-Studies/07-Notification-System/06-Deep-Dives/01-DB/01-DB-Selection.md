

## Access Patterns

Two primary queries drive this system:

**Write:** A notification is dispatched to a user — insert a new notification record with status `PENDING`, then update it to `DELIVERED` or `FAILED` after the worker hears back from the external provider.

**Read:** What is the status of a notification sent to a user? Show me all notifications for a user in the last 3 months, grouped by status. This is also the analytics query — status-wise counts over a time window.

So the pattern is: **write-heavy at intake, read-by-user at query time**.

---

## Why Not Relational (PostgreSQL / MySQL)?

The first instinct is relational — structured data, familiar, ACID guarantees. But relational DBs are fundamentally read-optimised. A well-tuned PostgreSQL instance can handle around **10K–50K writes/sec** before it starts struggling — WAL contention, index update overhead, and connection pool saturation all compound at scale.

We have **10M writes/sec at peak** (5M notification inserts + 5M status updates from workers). That's 200x what a relational DB can comfortably sustain. No amount of vertical scaling fixes this — you'd need sharding, and once you shard a relational DB you lose most of the guarantees that made it attractive.

Relational is out for the notifications table.

---

## Why Not MongoDB?

MongoDB is document-oriented and more write-friendly than relational, but it still struggles at this scale. WiredTiger (MongoDB's storage engine) has similar write amplification issues at 10M/sec — particularly for updates (status changes trigger document rewrites). MongoDB's write ceiling per node sits in a similar ballpark to relational DBs for update-heavy workloads.

MongoDB is out for the notifications table.

---

## Why Cassandra?

Cassandra is a wide-column store designed from the ground up for write-heavy, high-throughput workloads. Its write path is optimised: every write goes to an in-memory memtable and a sequential append to a commit log — no random disk I/O, no index contention, no locking. This gives Cassandra a write throughput of **100K–200K writes/sec per node** for typical payloads.

At 10M writes/sec:

```
10,000,000 / 100,000 = 100 shards
100 shards × 3 replicas = 300 nodes
```

300 Cassandra nodes to serve peak write throughput with fault tolerance. That's large but entirely standard for this scale — Cassandra was built for exactly this.

Cassandra's eventual consistency model is fine here. Notification status being slightly stale for a few hundred milliseconds is acceptable — we said eventual consistency for delivery status is tolerable in the NFR.

---

## Why Not Cassandra for Preferences?

User preferences are a different access pattern entirely:

- **Low write volume** — users change notification settings rarely (maybe a few thousand writes/sec across 1B users)
- **Strong consistency required** — if a user opts out of SMS, the next notification must not send SMS. Eventual consistency here is a bug, not a trade-off.
- **Relational structure** — preferences are small, structured, and naturally fit a row-per-user model

Cassandra's tunable consistency can be pushed to strong consistency (quorum reads/writes), but you pay a latency penalty and give up the write throughput advantage — which you don't need for preferences anyway.

**PostgreSQL** is the right call for preferences:

- ACID guarantees — opt-out writes are immediately visible to all readers
- Low write volume fits comfortably within PostgreSQL's throughput ceiling
- Simple schema — one row per user, a few columns for channel preferences and notification type settings
- Default values bootstrapped at signup, PATCH updates only changed fields

> [!info] Two DBs, Two Jobs
> Cassandra handles notifications — write-heavy, eventually consistent, partitioned by user.
> PostgreSQL handles preferences — low write, strongly consistent, ACID.

> [!danger] Common Trap
> Candidates pick one DB for everything. The write pattern for notifications (10M/sec, eventual consistency OK) and preferences (low write, strong consistency required) are fundamentally different problems — they need different tools.

---

## Summary

| | Notifications | Preferences |
|---|---|---|
| DB | Cassandra | PostgreSQL |
| Write volume | 10M/sec | Low |
| Consistency | Eventual | Strong |
| Reason | Write-optimised, horizontally scalable | ACID, strong consistency, low volume |
| Nodes | 300 (100 shards × 3 replicas) | Standard replicated PostgreSQL |
