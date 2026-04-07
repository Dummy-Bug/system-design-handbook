# CDC — Interview Cheatsheet

---

## The trigger in your head

```
Two systems need to stay in sync with your DB?  →  CDC
"publish to Kafka after a DB write"?            →  Outbox Pattern
Interviewer asks "what if the Kafka publish fails"?  →  Outbox Pattern
```

---

## The three moments to mention CDC

### 1. Search index sync

> "You have Postgres as your primary DB and Elasticsearch for search. How do you keep them in sync?"

**Wrong answer:** write to both on every update — dual write problem.

**Right answer:**
> "I'd use CDC. Debezium reads the Postgres WAL and streams every change to a Kafka topic. An Elasticsearch consumer subscribes to that topic and updates the index. The app only writes to Postgres — Elasticsearch catches up asynchronously."

---

### 2. Cache invalidation

> "Data changes in the DB. How does Redis know to invalidate?"

**Wrong answer:** app deletes the Redis key after every DB write — dual write, can fail silently.

**Right answer:**
> "CDC detects the change in the WAL, publishes to Kafka, and a cache invalidation consumer deletes or refreshes the Redis key. Decoupled and guaranteed."

---

### 3. Any time you say "and then we publish to Kafka"

The moment those words leave your mouth, the interviewer will ask:

> "What if the DB write succeeds but the Kafka publish fails?"

**Right answer:**
> "I'd use the Outbox Pattern. Instead of publishing to Kafka directly, the app writes the event into an outbox table in the same DB transaction as the actual data. Either both are written or neither is — atomicity guaranteed. CDC picks up the outbox row and publishes to Kafka asynchronously. The app never touches two systems."

---

## One-line definitions

> [!info] CDC (Change Data Capture)
> A tool that reads a database's internal write-ahead log and streams every committed change as a structured event to downstream systems.

> [!info] WAL (Write-Ahead Log)
> The database's internal durability log. Written before and after every transaction. Already exists — CDC reads it as a side effect with near-zero overhead.

> [!info] Outbox Pattern
> Write the event to an outbox table in the same DB transaction as your data. CDC picks it up and publishes to Kafka. Solves dual write between DB and Kafka.

> [!info] Dual Write
> When application code writes the same data to two separate systems in sequence. Dangerous because if the second write fails, the systems are permanently out of sync with no way to detect it.

---

## What CDC guarantees

| Property | Detail |
|---|---|
| Ordered | Changes streamed in commit order |
| Complete | Every committed change is captured |
| Async | Small delay (ms to seconds) between DB write and downstream update |
| No dual write | App touches one system only |

> [!important] CDC gives eventual consistency — not immediate
> Downstream systems (Elasticsearch, Redis, warehouse) will be briefly stale after a DB write. For search, cache, and analytics this is acceptable. For financial systems needing immediate consistency, CDC alone is not sufficient.

---

## The tool to name

**Debezium** — the standard CDC tool. Connects to Postgres/MySQL, reads WAL/binlog, publishes JSON events to Kafka. One line in an interview is enough: "I'd use Debezium for CDC."
