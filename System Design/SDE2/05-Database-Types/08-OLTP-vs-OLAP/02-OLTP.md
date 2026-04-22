# OLTP — Online Transaction Processing

> [!info] Plain-English definition
> OLTP is your production database — the one serving your live app. Every operation is small, fast, and touches very few rows. Thousands of these happen per second.

---

## What OLTP looks like

Every operation in an OLTP system is short and precise:

- Insert a new user → 1 row written
- Load someone's profile → fetch 1 row by primary key
- Mark a notification as read → update 1 column on 1 row
- Fetch the last 20 messages in a chat → scan a small range of rows

None of these operations touch millions of rows. They're in and out in milliseconds. The database is optimized for **low latency on individual rows**.

---

## How OLTP stores data — row-oriented

OLTP databases use **row-oriented storage** — all columns of a row are stored together on disk.

```
Row 1: [user_id=1, name="Alice", email="alice@gmail.com", country="IN", bio="..."]
Row 2: [user_id=2, name="Bob",   email="bob@gmail.com",   country="US", bio="..."]
Row 3: [user_id=3, name="Carol", email="carol@gmail.com", country="BR", bio="..."]
```

This is great for OLTP workloads. When you fetch a user's profile, you need all their columns — name, email, country, bio — and they're all sitting together on disk in one read.

But it's terrible for analytics. If you run:

```sql
SELECT country, COUNT(*) FROM users GROUP BY country;
```

You only need the `country` column. But because all columns are stored together, the database has to load every full row off disk — including `name`, `email`, `password_hash`, `bio`, `profile_pic_url` — just to get to `country`. At 500 million rows, you're reading gigabytes of data you don't need.

---

## OLTP examples

| Database | Type | Notes |
|---|---|---|
| PostgreSQL | Relational | Most popular open-source relational DB |
| MySQL | Relational | Widely used, especially in web stacks |
| Oracle DB | Relational | Enterprise relational, heavily used in banking/finance |
| DynamoDB | NoSQL (Key-Value) | AWS managed, fast single-item reads/writes |
| Cassandra | NoSQL (Wide-Column) | High-throughput writes, time-series, activity feeds |
| MongoDB | NoSQL (Document) | Flexible JSON documents, common in web apps |
| Redis | NoSQL (Key-Value) | In-memory, used for caching and session storage |
| CockroachDB | NewSQL | Distributed, ACID-compliant, Postgres-compatible |
| Google Spanner | NewSQL | Globally distributed, ACID with TrueTime |

> [!important] NoSQL ≠ OLAP
> Cassandra, MongoDB, DynamoDB are all OLTP — they're built for fast, low-latency operations on individual records. NoSQL just means "not relational." It says nothing about OLTP vs OLAP.

> [!important] NewSQL is still OLTP
> CockroachDB and Spanner give you distributed scale + ACID — but they're still serving live transactional traffic, not analytical batch queries. That makes them OLTP.

---

## What OLTP is NOT built for

- Full table scans
- Large aggregations (`COUNT`, `SUM`, `GROUP BY` across millions of rows)
- Historical trend analysis
- Queries that take minutes to run

These belong in OLAP.
