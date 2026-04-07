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

| Database | Notes |
|---|---|
| PostgreSQL | Most popular open-source relational OLTP DB |
| MySQL | Widely used, especially in web stacks |
| DynamoDB | Managed NoSQL, still OLTP — optimized for fast single-item reads/writes |

> [!important] DynamoDB is OLTP, not OLAP
> Even though DynamoDB is NoSQL and scales horizontally, it's still an OLTP system — it's built for fast, low-latency operations on individual items, not analytical scans.

---

## What OLTP is NOT built for

- Full table scans
- Large aggregations (`COUNT`, `SUM`, `GROUP BY` across millions of rows)
- Historical trend analysis
- Queries that take minutes to run

These belong in OLAP.
