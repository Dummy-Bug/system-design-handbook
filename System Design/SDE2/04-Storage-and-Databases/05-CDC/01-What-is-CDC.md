# What is Change Data Capture?

> [!question] You have a Postgres database powering your app. Three other systems need to stay in sync with it. How do you do it without things silently going out of sync?

> [!abstract] CDC solves one of the most dangerous problems in distributed systems — keeping multiple systems in sync with your database without ever writing to two systems at once. Every time you have a search index, a cache, or a data warehouse sitting next to your primary DB, CDC is the answer to how they stay consistent.

---

## The problem — dual write

Imagine your app has:
- A **PostgreSQL** database as the source of truth
- An **Elasticsearch** index for product search
- A **Redis** cache that must be invalidated on updates
- A **data warehouse** for analytics

The naive approach is to write to all of them every time data changes:

```
App → writes to Postgres
    → also writes to Elasticsearch
    → also invalidates Redis
    → also sends to warehouse
```

This is called a **dual write** — your application code writes the same piece of data to two completely separate systems:

```java
db.save(order);           // write 1 — Postgres
elastic.index(order);     // write 2 — Elasticsearch
```

Two separate network calls, two separate systems, no transaction wrapping them. And this has a fatal flaw.

What if the Postgres write succeeds but the Elasticsearch write fails? Your database and your search index are now out of sync — permanently and silently. You don't know it happened. Users search for an order that exists in the DB but returns nothing in search.

At 10 million writes per day, even a 0.001% failure rate means 100 silent inconsistencies every day. They accumulate.

> [!danger] There is no safe order for dual writes
> Write to Postgres first, then Elasticsearch fails → DB has it, search doesn't.
> Write to Elasticsearch first, then Postgres fails → search has it, DB doesn't.
> Neither order is safe. The problem is structural, not ordering.

---

## The fix — watch the database's diary

Every database that takes durability seriously already maintains an internal log of every change that happens to it. In Postgres this is called the **WAL (Write-Ahead Log)**. In MySQL it's called the **binlog**.

This log exists purely for the database's own crash recovery. Before Postgres writes anything to disk, it first writes a log entry:

```
"At 10:04:32 — row inserted into users — id=99, name=Alice"
"At 10:04:33 — row updated in orders — id=55, status: pending → paid"
"At 10:04:34 — row deleted from sessions — id=12"
```

If the database crashes mid-write, it replays this log to restore itself. This is already happening regardless of whether CDC exists or not.

CDC says: **what if we read that log and stream those changes to everyone who cares?**

---

## How CDC works — Debezium and the WAL

**Debezium** is the most widely used CDC tool. It connects to Postgres, reads the WAL, and for every change it produces a structured JSON event:

```json
{
  "operation": "UPDATE",
  "table": "orders",
  "before": { "id": 55, "status": "pending" },
  "after":  { "id": 55, "status": "paid" }
}
```

That event goes onto a Kafka topic. Every downstream system that cares — Elasticsearch, Redis, the warehouse — subscribes to that topic and does its own thing with it.

```
Postgres WAL
    → Debezium reads it (side read, no extra DB write)
    → converts to structured JSON event
    → publishes to Kafka topic
    → Elasticsearch consumer updates search index
    → Redis consumer invalidates cache key
    → Warehouse consumer inserts row
```

Your app only writes to Postgres. Everything else reacts to the change stream. One write, guaranteed propagation.

---

## Does CDC add overhead to your database?

This is the right question to ask. The answer is: **nearly zero overhead**.

Your database is already writing the WAL. It has no choice — that is how it guarantees durability. Two WAL writes happen for every transaction regardless:

```
Write request arrives
    → WAL pre-write entry        ← 1st WAL write (before the change)
    → actual data page written   ← the real data write
    → WAL commit entry           ← 2nd WAL write (marks transaction complete)
    → success returned to app
```

These three writes are the price of the D in ACID — the guarantee that committed data survives a crash. You cannot skip them. They happen with or without CDC.

**Debezium reads the WAL after the commit entry appears** — like a silent observer reading over the database's shoulder. It does not ask Postgres to write anything extra. The user got their success response long before Debezium even starts reading.

```
User writes → 3 writes happen → user gets "success"
                                        ↓
                              CDC reads async (user is gone)
                                        ↓
                                      Kafka
```

Compare this to the dual write approach — where the user was waiting for Postgres + Elasticsearch + Redis all in the same request. CDC is strictly lighter for the user.

---

## What CDC guarantees

- **Ordered** — changes are streamed in the exact order they were committed to the DB
- **Complete** — every committed change is captured, nothing is skipped
- **Async** — downstream systems update with a small delay (milliseconds to seconds), not synchronously
- **No dual write** — your app touches one system only

> [!important] CDC gives you eventual consistency between your DB and downstream systems
> There is a brief window where Postgres has the new data but Elasticsearch hasn't been updated yet. For most use cases (search, cache, analytics) this is acceptable. For financial ledgers where you need immediate consistency, CDC alone is not enough.
