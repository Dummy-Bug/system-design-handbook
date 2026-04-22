> [!info] The core idea
> OLTP and OLAP are two fundamentally different types of database workloads. OLTP serves your live users — fast, small operations. OLAP serves your analysts — slow, massive scans. They cannot share the same database at scale.

## The scenario

You're running Instagram. Two things are happening constantly:

1. Users are posting photos, liking posts, following each other — thousands of operations per second hitting your production database.
2. The business team wants to know: "How many new users signed up this month? Which country has the highest engagement? What's the average session length?"

The obvious move is to run that analytics query directly against the production database:

```sql
SELECT country, COUNT(*) FROM users GROUP BY country;
```

Your users table has 500 million rows. That query does a **full table scan** — it reads every single row to count them by country. It takes minutes.

And while it's running, it doesn't politely step aside for live user traffic. It competes for the same resources.

---

## What "competing for resources" actually means

Think of your database server as a single kitchen in a restaurant. It has one set of burners, one oven — fixed resources.

Two types of orders come in at the same time:

1. A customer orders a quick espresso — done in 30 seconds. *(live user loading their feed)*
2. A catering order comes in — cook 500 meals for a wedding. *(analytics query scanning 500M rows)*

The wedding order doesn't wait. It takes over all the burners right now. The espresso customer has to wait — even though their order is tiny.

In database terms:

- **Disk I/O** — the hard drive can only read so much data per second. The analytics query consumes that bandwidth reading 500M rows off disk. Live user queries queue behind it.
- **CPU** — the database uses CPU to process rows, sort results, aggregate counts. The analytics query uses it flat out. Everything else slows down.

Resources are shared. A heavy query consumes what it needs, and everything else suffers.

---

## The result

Your production database grinds to a halt. Real users experience slow feed loads, timeouts, failed requests — all because an analyst ran a COUNT query.

> [!danger] Never run analytics queries against your production OLTP database at scale
> Full table scans compete with live traffic → latency spikes → user impact. At scale, this is unacceptable.

---

## The fix

Separate the workloads entirely. Use two different databases built for two different jobs:

- **OLTP** — serves live users, optimized for small fast operations
- **OLAP** — serves analysts, optimized for massive scans

The analyst's 10-minute query runs on the OLAP warehouse. No live user is affected because it's a completely separate system.
