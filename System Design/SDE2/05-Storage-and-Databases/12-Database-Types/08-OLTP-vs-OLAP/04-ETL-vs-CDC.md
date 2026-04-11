# How Data Moves — ETL vs CDC

The OLAP warehouse is a separate system. It needs data from your OLTP production database. The question is: how do you keep it fed and up to date?

There are two approaches: **ETL** (batch snapshots) and **CDC** (real-time streaming).

---

## Approach 1 — ETL (Extract, Transform, Load)

ETL is the naive but simple approach. A scheduled job wakes up every few hours and does three things:

```
Extract  → pull data from OLTP
           SELECT * FROM orders WHERE updated_at > last_run_time

Transform → clean it, reshape it, join tables, compute derived columns

Load     → write the result into the OLAP warehouse
```

The warehouse now holds a **snapshot** of the production database as of the last job run. Analysts query that snapshot.

### The fundamental problem — staleness

If the ETL job runs every 6 hours, the warehouse is at worst **6 hours stale**.

For a weekly revenue report, that's fine. But imagine your fraud detection team is watching for suspicious transactions. A fraudster makes 50 transactions in 10 minutes. Your ETL runs every 6 hours. You won't see it in the warehouse for 6 hours. By then the money is gone.

ETL is **batch** — you get a snapshot of the past, not the present.

> [!important] ETL = snapshots
> Every ETL run takes a point-in-time snapshot of production data and loads it into the warehouse. The warehouse is always some hours behind the live database.

---

## Approach 2 — CDC (Change Data Capture)

You've already studied CDC in detail. Here's how it fits into the OLAP pipeline:

Every write to your OLTP database — a new user, a new order, a deleted post — gets captured by CDC as it happens. CDC reads the database's internal write log (WAL in PostgreSQL, binlog in MySQL) and publishes each change as an event to **Kafka**.

A consumer pulls those events from Kafka and writes them into the OLAP warehouse.

```
OLTP (PostgreSQL)
    ↓  CDC reads WAL
Kafka (event stream)
    ↓  consumer pulls events
OLAP (BigQuery / Redshift)
    ↑
Analysts query fresh data
```

Instead of a 6-hour-old snapshot, the warehouse is now **5–10 seconds behind** the live database. Your fraud detection team sees the suspicious transactions almost as they happen.

---

## ETL vs CDC — the trade-off

| | ETL | CDC |
|---|---|---|
| How it works | Batch job, runs on a schedule | Streams every change in real-time |
| Data freshness | Hours old | Seconds old |
| Complexity | Simple — just a scheduled query | More moving parts — Kafka, consumers, schema evolution |
| Best for | Reporting, historical analysis, BI dashboards | Fraud detection, real-time dashboards, search index sync |

> [!tip] Interview framing
> When an interviewer asks "how would you keep your data warehouse up to date?" — lead with CDC for freshness-sensitive use cases (fraud, real-time analytics), and mention ETL as the simpler alternative when near-real-time isn't needed (weekly reports, BI dashboards).

---

## Why CDC is harder

CDC sounds strictly better — fresher data, same result. But it comes with complexity:

- **Schema changes are painful** — if you add a column to your OLTP table, your CDC consumer and warehouse schema both need to be updated in sync.
- **Message ordering** — Kafka guarantees ordering within a partition, but cross-partition ordering requires careful partition key design.
- **Exactly-once delivery** — if a consumer crashes and restarts, it may re-process some events. The warehouse write must be idempotent.

ETL avoids all of this — it's just a SQL query on a schedule. For teams that don't need real-time analytics, ETL is the right call.
