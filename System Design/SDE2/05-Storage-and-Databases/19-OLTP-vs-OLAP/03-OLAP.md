# OLAP — Online Analytical Processing

> [!info] Plain-English definition
> OLAP is a separate database, purpose-built for heavy analytical queries. It serves analysts and dashboards — not live users. It's optimized for scanning billions of rows and computing aggregations.

---

## What OLAP looks like

OLAP is built for questions like:

- How many new users signed up this month, broken down by country?
- What's the average session length per platform over the last 90 days?
- Which product categories drove the most revenue in Q3?

These queries scan millions or billions of rows, compute aggregations (`COUNT`, `SUM`, `AVG`, `GROUP BY`), and can take seconds to minutes to run. That's fine — because no live user is waiting on them.

---

## Why OLAP is fast at scans — column-oriented storage

OLAP databases use **column-oriented storage** — all values of a column are stored together on disk, not all columns of a row.

```
Row-oriented (OLTP):

Row 1: [user_id=1, name="Alice", email="alice@...", country="IN"]

Row 2: [user_id=2, name="Bob",   email="bob@...",   country="US"]

Column-oriented (OLAP):

user_id column: [1, 2, 3, 4, 5, ...]
name column:    [Alice, Bob, Carol, ...]
country column: [IN, US, BR, IN, US, ...]
```

Now when you run:

```sql
SELECT country, COUNT(*) FROM users GROUP BY country;
```

The OLAP database reads **only the country column** off disk. It doesn't touch `name`, `email`, `password_hash`, or any other column. At 500 million rows, instead of reading gigabytes of irrelevant data, it reads only the country values — a fraction of the size.

That's why BigQuery can scan a billion rows in seconds while PostgreSQL would take minutes on the same query.

> [!important] Column-oriented = read only what you need
> OLAP queries typically touch 2-3 columns out of 20+. Column storage means you physically skip the columns you don't need. The I/O savings at billion-row scale are enormous.

---

## OLAP examples

| Database | Who uses it |
|---|---|
| BigQuery | Google — fully managed, serverless columnar warehouse |
| Redshift | Amazon — columnar warehouse, tight AWS integration |
| Snowflake | Cloud-agnostic, very popular in data teams |
| ClickHouse | Open-source, extremely fast columnar DB for real-time analytics |
| Apache Druid | Real-time analytics on event streams (used at Twitter, Airbnb) |
| Apache Hive | SQL on top of Hadoop — batch analytics on massive data lakes |
| Presto / Trino | Distributed SQL query engine — runs analytical queries across multiple data sources |

---

## What OLAP is NOT built for

OLAP databases are not designed to serve live user traffic. They don't have the low-latency guarantees of OLTP. You wouldn't point your Instagram app at BigQuery to load a user's feed — the query overhead is too high for single-row lookups.

OLAP is a **read-heavy, batch-oriented, offline** system. Analysts and dashboards query it. Your app never does.

---

## The warehouse mental model

Think of OLAP as a **warehouse** — not a live kitchen, but a giant storage facility where you batch-process everything offline, away from your live users. Data flows in from production, sits in the warehouse, and analysts query it at their leisure without impacting anyone.
